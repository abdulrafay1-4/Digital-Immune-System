"""M2 orchestrator: turns a stream of edge telemetry into deterministic batches."""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from m1_monitoring.agent import TRUST_TOPIC
from shared.bus import Bus
from shared.clock import Clock
from shared.schemas import AuditRecord, MessageBase, TrustUpdate

ORCHESTRATOR_TOPIC = "orchestrator.batch"

ACTOR_ID = "orchestrator"


class TickBatch(MessageBase):
    """Every node's report for a single simulation tick."""

    model_config = ConfigDict(extra="forbid")

    updates: list[TrustUpdate]
    over_budget_agents: list[str] = []

    @property
    def node_ids(self) -> list[str]:
        return [u.node_id for u in self.updates]

    @property
    def min_node_trust(self) -> float:
        return min(u.node_trust for u in self.updates)

    @property
    def mean_node_trust(self) -> float:
        return sum(u.node_trust for u in self.updates) / len(self.updates)


class Pipeline(Protocol):
    """
    What the orchestrator hands a sealed batch to: `NullPipeline`, the LangGraph graph, or the
    closed-loop pipeline, all behind this same call.
    """

    def run(self, batch: TickBatch) -> None: ...


class NullPipeline:
    """Records what it was given and does nothing else."""

    def __init__(self) -> None:
        self.seen: list[TickBatch] = []

    def run(self, batch: TickBatch) -> None:
        self.seen.append(batch)


class Orchestrator:
    """Subscribes to edge telemetry, seals per-tick batches, drives a pipeline."""

    MAX_RETAINED_UPDATES = 50_000

    def __init__(
        self,
        *,
        bus: Bus,
        run_id: str,
        seed: int,
        config_hash: str,
        pipeline: Pipeline | None = None,
        topic: str = TRUST_TOPIC,
        emit_audit: bool = True,
        max_retained_batches: int = 256,
        max_updates_per_agent_per_tick: int = 4,
        silence_ticks: int = 3,
        node_agent_binding: dict[str, str] | None = None,
        bind_on_first_sight: bool = True,
        max_nodes: int = 100_000,
        clock: Clock | None = None,
        max_clock_skew: float = 0.0,
        outage_min_nodes: int = 3,
        enforce_run_identity: bool = True,
        observers: Sequence[Any] = (),
        device_keys: Mapping[str, Any] | None = None,
        seal_on_report: bool = True,
    ) -> None:
        self.bus = bus
        self.run_id = run_id
        self.seed = seed
        self.config_hash = config_hash
        self.pipeline = pipeline or NullPipeline()
        self.observers = tuple(observers)
        self.observer_failures = 0
        self.device_keys = dict(device_keys) if device_keys is not None else None
        self.unattested_updates = 0
        self.topic = topic
        self.emit_audit = emit_audit
        self.max_retained_batches = max_retained_batches
        self.max_updates_per_agent_per_tick = max_updates_per_agent_per_tick
        self.silence_ticks = silence_ticks
        self._binding: dict[str, str] = dict(node_agent_binding or {})
        self.bind_on_first_sight = bind_on_first_sight
        self.unbound_updates = 0
        self.max_nodes = max_nodes
        self.over_capacity_updates = 0
        self.clock = clock
        self.max_clock_skew = max_clock_skew
        self.seal_on_report = seal_on_report
        self.future_updates = 0
        self.enforce_run_identity = enforce_run_identity
        self.foreign_updates = 0
        self.pipeline_failures = 0
        self.last_pipeline_failure: str | None = None
        self.outage_min_nodes = outage_min_nodes
        self.outages: list[tuple[float, tuple[str, ...]]] = []

        self._pending: dict[float, list[TrustUpdate]] = {}
        self._sealed: list[TickBatch] = []
        self.updates_seen = 0
        self._sealed_times: set[float] = set()
        self._sealed_floor = float("-inf")
        self.late_updates = 0
        self.duplicate_updates = 0
        self.rate_limited_updates = 0
        self._roster: set[str] = set()
        self._silent_for: dict[str, int] = {}
        self.silent_nodes: tuple[str, ...] = ()
        self._per_tick_counts: dict[float, dict[str, int]] = {}

    def attach(self) -> None:
        """Subscribe to the telemetry topic."""
        handler: Callable[[BaseModel], None] = self._on_message
        self.bus.subscribe(self.topic, handler)

    def _on_message(self, model: BaseModel) -> None:
        if not isinstance(model, TrustUpdate):
            return

        self.updates_seen += 1

        if self.enforce_run_identity and (
            model.run_id != self.run_id
            or model.seed != self.seed
            or model.config_hash != self.config_hash
        ):
            self.foreign_updates += 1
            return

        if self.clock is not None and model.sim_time > self.clock.now() + self.max_clock_skew:
            self.future_updates += 1
            return

        if model.sim_time in self._sealed_times or model.sim_time <= self._sealed_floor:
            self.late_updates += 1
            return

        if model.node_id not in self._binding and len(self._binding) >= self.max_nodes:
            self.over_capacity_updates += 1
            return

        if not self._binding_ok(model):
            self.unbound_updates += 1
            return

        if self.device_keys is not None and not self._attested(model):
            self.unattested_updates += 1
            return

        counts = self._per_tick_counts.setdefault(model.sim_time, {})
        counts[model.agent_id] = counts.get(model.agent_id, 0) + 1
        if counts[model.agent_id] > self.max_updates_per_agent_per_tick:
            self.rate_limited_updates += 1
            return

        self._pending.setdefault(model.sim_time, []).append(model)
        if self.seal_on_report:
            self._seal_below(model.sim_time if self.clock is None else self.clock.now())

    def seal_due(self) -> None:
        """Seal every tick the clock has passed."""
        if self.clock is not None:
            self._seal_below(self.clock.now())

    def _seal_below(self, watermark: float) -> None:
        """Seal every tick strictly older than `watermark`; those cannot grow."""
        for sim_time in sorted(t for t in self._pending if t < watermark):
            self._seal(sim_time)

    def flush(self) -> None:
        """Seal whatever is still open."""
        for sim_time in sorted(self._pending):
            self._seal(sim_time)

    def _seal(self, sim_time: float) -> None:
        updates = self._deduplicate(self._pending.pop(sim_time))
        counts = self._per_tick_counts.pop(sim_time, {})
        self._sealed_times.add(sim_time)
        if len(self._sealed_times) > 4096:
            ordered = sorted(self._sealed_times)
            self._sealed_floor = ordered[len(ordered) // 2]
            self._sealed_times = set(ordered[len(ordered) // 2 + 1 :])
        self._update_silence({u.node_id for u in updates}, sim_time)
        batch = TickBatch(
            sim_time=sim_time,
            run_id=self.run_id,
            seed=self.seed,
            config_hash=self.config_hash,
            updates=sorted(updates, key=lambda u: u.node_id),
            over_budget_agents=sorted(
                agent for agent, n in counts.items() if n > self.max_updates_per_agent_per_tick
            ),
        )
        if self.max_retained_batches != 0:
            self._sealed.append(batch)
            if len(self._sealed) > self.max_retained_batches:
                del self._sealed[0]
            retained = sum(len(b.updates) for b in self._sealed)
            while len(self._sealed) > 1 and retained > self.MAX_RETAINED_UPDATES:
                retained -= len(self._sealed.pop(0).updates)

        if self.emit_audit:
            self.bus.publish(ORCHESTRATOR_TOPIC, self._audit(batch))

        for observer in self.observers:
            try:
                observer.observe(batch)
            except Exception:  # noqa: BLE001
                self.observer_failures += 1
        try:
            self.pipeline.run(batch)
        except Exception as exc:  # noqa: BLE001
            self._pipeline_failed(batch, exc)

    def _pipeline_failed(self, batch: TickBatch, exc: Exception) -> None:
        """A tick whose pipeline raised is lost; the loop carries on."""
        self.pipeline_failures += 1
        self.last_pipeline_failure = f"{type(exc).__name__}: {exc}"
        with contextlib.suppress(Exception):
            self.bus.publish(
                ORCHESTRATOR_TOPIC,
                AuditRecord(
                    sim_time=batch.sim_time,
                    run_id=self.run_id,
                    seed=self.seed,
                    config_hash=self.config_hash,
                    event_type="orchestrator.pipeline_failed",
                    actor_id=ACTOR_ID,
                    payload={
                        "error": self.last_pipeline_failure,
                        "n_updates": len(batch.updates),
                        "pipeline_failures": self.pipeline_failures,
                    },
                ),
            )

    def rebind(self, node_id: str, agent_id: str, *, by: str) -> None:
        """Hand a device to a new monitoring agent."""
        previous = self._binding.get(node_id)
        self._binding[node_id] = agent_id
        sim_time = (
            self.clock.now() if self.clock is not None else max(self._sealed_times, default=0.0)
        )
        with contextlib.suppress(Exception):
            self.bus.publish(
                ORCHESTRATOR_TOPIC,
                AuditRecord(
                    sim_time=sim_time,
                    run_id=self.run_id,
                    seed=self.seed,
                    config_hash=self.config_hash,
                    event_type="orchestrator.rebind",
                    actor_id=by,
                    payload={
                        "node_id": node_id,
                        "previous_agent_id": previous,
                        "agent_id": agent_id,
                    },
                ),
            )

    def _attested(self, model: TrustUpdate) -> bool:
        """Did this device sign exactly this context, at exactly this tick?"""
        from shared.attestation import attestation_payload

        key = self.device_keys.get(model.node_id) if self.device_keys is not None else None
        if key is None or model.attestation is None:
            return False
        payload = attestation_payload(model.node_id, model.sim_time, model.context)
        return bool(key.verify(payload, model.attestation))

    def _binding_ok(self, update: TrustUpdate) -> bool:
        """Is this agent the monitor for the node it is reporting on?"""
        owner = self._binding.get(update.node_id)
        if owner is None:
            if not self.bind_on_first_sight:
                return False
            self._binding[update.node_id] = update.agent_id
            return True
        return owner == update.agent_id

    def _update_silence(self, reported: set[str], sim_time: float) -> None:
        """Count consecutive misses per known node."""
        self._roster |= reported
        for node_id in self._roster:
            if node_id in reported:
                self._silent_for[node_id] = 0
            else:
                self._silent_for[node_id] = self._silent_for.get(node_id, 0) + 1
        self.silent_nodes = tuple(
            sorted(n for n, missed in self._silent_for.items() if missed >= self.silence_ticks)
        )
        newly_silent = tuple(
            sorted(n for n, missed in self._silent_for.items() if missed == self.silence_ticks)
        )
        if len(newly_silent) >= self.outage_min_nodes:
            self.outages.append((sim_time, newly_silent))

    def _deduplicate(self, updates: list[TrustUpdate]) -> list[TrustUpdate]:
        """One report per node per tick, keeping the most pessimistic."""
        best: dict[str, TrustUpdate] = {}
        for update in updates:
            seen = best.get(update.node_id)
            if seen is None:
                best[update.node_id] = update
                continue
            self.duplicate_updates += 1
            if update.node_trust < seen.node_trust:
                best[update.node_id] = update
        return list(best.values())

    def _audit(self, batch: TickBatch) -> AuditRecord:
        return AuditRecord(
            sim_time=batch.sim_time,
            run_id=self.run_id,
            seed=self.seed,
            config_hash=self.config_hash,
            event_type="orchestrator.batch_sealed",
            actor_id=ACTOR_ID,
            payload={
                "n_updates": len(batch.updates),
                "min_node_trust": batch.min_node_trust,
                "mean_node_trust": batch.mean_node_trust,
                "late_updates": self.late_updates,
                "duplicate_updates": self.duplicate_updates,
                "rate_limited_updates": self.rate_limited_updates,
                "unbound_updates": self.unbound_updates,
                "over_capacity_updates": self.over_capacity_updates,
                "future_updates": self.future_updates,
                "foreign_updates": self.foreign_updates,
                "unattested_updates": self.unattested_updates,
                "silent_nodes": list(self.silent_nodes),
                "correlated_outage": (
                    list(self.outages[-1][1])
                    if self.outages and self.outages[-1][0] == batch.sim_time
                    else []
                ),
            },
        )

    @property
    def batches(self) -> list[TickBatch]:
        """Sealed batches, oldest first."""
        return list(self._sealed)

    @property
    def batches_sealed(self) -> int:
        return len(self._sealed)
