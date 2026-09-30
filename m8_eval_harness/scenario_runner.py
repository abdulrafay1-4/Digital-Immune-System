"""Run one scenario against one baseline, and the whole grid."""

from __future__ import annotations

import copy
import gc
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any

import simpy

from agents.orchestrator import Orchestrator
from agents.pipeline import ClosedLoopPipeline
from m8_eval_harness.baselines.base import FULL, Baseline
from m8_eval_harness.params import FROZEN, SystemParams
from m8_eval_harness.scenarios.base import Scenario
from m8_eval_harness.simulator import DEFAULT_CONFIG, run_trust_sim
from shared.bus import InProcBus
from shared.clock import SimPyClock
from shared.run_manifest import config_hash, load_yaml_config


@dataclass
class RunContext:
    """What an adversary is handed."""

    bus: InProcBus
    run_id: str
    seed: int
    config_hash: str
    pipeline: ClosedLoopPipeline
    identities: dict[str, Any] = field(default_factory=dict)

    def as_agent(self, agent_id: str) -> Any:
        """Publish as `agent_id`."""
        if agent_id not in self.identities:
            return self.bus
        from agents.orchestrator import TRUST_TOPIC
        from shared.secure_bus import SignedBus

        return SignedBus(
            inner=self.bus,
            identity=self.identities[agent_id],
            topics=frozenset({TRUST_TOPIC}),
        )


@dataclass
class ScenarioResult:
    scenario: Scenario
    baseline: Baseline
    seed: int
    pipeline: ClosedLoopPipeline = field(repr=False)
    orchestrator: Orchestrator = field(repr=False)
    adversary: Any | None = None
    params: SystemParams = FROZEN
    operator: str = "absent"
    adjudication: str = "oracle"
    binding: str = "provisioned"
    approval_gate: Any | None = field(default=None, repr=False)
    tick_seconds: list[float] = field(default_factory=list, repr=False)
    memory_read_seconds: list[float] = field(default_factory=list, repr=False)
    memory_write_seconds: list[float] = field(default_factory=list, repr=False)
    wall_seconds: float = 0.0
    cpu_seconds: float = 0.0
    rss_mb: float | None = None
    rss_mb_delta: float | None = None
    telemetry_rejected: int = 0
    audit_checkpoint: dict[str, Any] | None = None
    config_hash: str = ""

    @property
    def ticks(self) -> int:
        return len(self.pipeline.outcomes)

    def worst_level(self, node_id: str) -> int:
        return max(
            (
                p.proposed_level
                for o in self.pipeline.outcomes
                for p in o.plans
                if p.node_id == node_id
            ),
            default=0,
        )

    def first_at_or_above(self, node_id: str, level: int) -> float | None:
        for outcome in self.pipeline.outcomes:
            for plan in outcome.plans:
                if plan.node_id == node_id and plan.proposed_level >= level:
                    return outcome.sim_time
        return None

    def detection_latency(self, level: int = 2) -> float | None:
        """Mean sim-seconds from compromise to reaching `level`, over detections."""
        latencies = [
            found - began
            for node_id, began in self.scenario.ground_truth.items()
            if (found := self.first_at_or_above(node_id, level)) is not None
        ]
        return sum(latencies) / len(latencies) if latencies else None

    @property
    def detected(self) -> frozenset[str]:
        return frozenset(n for n in self.scenario.ground_truth if self.worst_level(n) >= 2)

    @property
    def missed(self) -> frozenset[str]:
        return self.scenario.compromised - self.detected

    @property
    def false_positives(self) -> frozenset[str]:
        """Healthy devices that were restricted or worse."""
        return frozenset(n for n in self.scenario.healthy if self.worst_level(n) >= 3)

    @property
    def detection_rate(self) -> float | None:
        if not self.scenario.ground_truth:
            return None
        return len(self.detected) / len(self.scenario.ground_truth)

    @property
    def false_positive_rate(self) -> float | None:
        healthy = self.scenario.healthy
        return len(self.false_positives) / len(healthy) if healthy else None

    @property
    def isolations(self) -> int:
        """Isolations actually carried out: only ever with an operator's approval."""
        return self._executed_at_or_above(4)

    @property
    def disruptive_actions(self) -> int:
        """Restrictions and isolations actually carried out: the cost of response."""
        return self._executed_at_or_above(3)

    def _executed_at_or_above(self, level: int) -> int:
        return sum(
            1
            for o in self.pipeline.outcomes
            for ex in o.executions
            if ex.executed and ex.level is not None and ex.level >= level
        )

    @property
    def heal_events(self) -> int:
        """Recovery actions taken."""
        return sum(len(o.healing) for o in self.pipeline.outcomes)

    @property
    def recall_boosts(self) -> int:
        """Ticks where immune memory recognised the pattern."""
        return sum(1 for o in self.pipeline.outcomes if o.correlation.recall_boost > 0.0)

    @property
    def audit_intact(self) -> bool:
        return self.pipeline.engine.audit.verify() is None

    def summary(self) -> dict[str, Any]:
        return {
            "scenario": self.scenario.scenario_id,
            "baseline": self.baseline.baseline_id,
            "seed": self.seed,
            "ticks": self.ticks,
            "detected": len(self.detected),
            "missed": len(self.missed),
            "detection_rate": self.detection_rate,
            "false_positives": len(self.false_positives),
            "false_positive_rate": self.false_positive_rate,
            "detection_latency": self.detection_latency(),
            "isolations": self.isolations,
            "disruptive_actions": self.disruptive_actions,
            "heal_events": self.heal_events,
            "recall_boosts": self.recall_boosts,
            "unbound_updates": self.orchestrator.unbound_updates,
            "audit_intact": self.audit_intact,
        }


def run_scenario(
    scenario: Scenario,
    baseline: Baseline = FULL,
    *,
    seed: int | None = None,
    results_dir: Any | None = None,
    adjudication: str = "oracle",
    operator: str = "absent",
    params: SystemParams | None = None,
    binding: str = "provisioned",
    attested_telemetry: bool = False,
    compromised_device: str | None = None,
    observers: tuple[str, ...] = (),
    **pipeline_kwargs: Any,
) -> ScenarioResult:
    """One cell of the grid."""
    from m9_capability_binder import binder

    params = params or FROZEN
    seed = scenario.seed if seed is None else seed
    run_id = f"{scenario.scenario_id}-{baseline.baseline_id}-{seed}"
    cfg = params.apply_to_config(load_yaml_config(DEFAULT_CONFIG))
    cfg_hash = config_hash(cfg)
    bus = InProcBus()
    binder.reset_spent_tokens()
    identities = _fleet_identities(scenario.n_nodes, run_id)

    gate = pipeline_kwargs.pop("approval", None) or _operator(operator)
    pipeline = baseline.pipeline(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=cfg_hash,
        params=params,
        approval=gate,
        **pipeline_kwargs,
    )
    pipeline.max_retained_outcomes = 0
    pipeline.max_retained_decisions = 0
    read_seconds: list[float] = []
    write_seconds: list[float] = []
    _time_memory(pipeline, read_seconds, write_seconds)
    timed = _TimedPipeline(pipeline)
    if binding not in ("provisioned", "tofu"):
        raise ValueError(f"unknown binding mode: {binding}")
    provisioned = {f"node-{i}": f"mon-node-{i}" for i in range(scenario.n_nodes)}
    verified = _verifying_view(bus, identities, strict=binding != "tofu")
    device_keys = _device_keys(scenario.n_nodes, run_id) if attested_telemetry else {}
    orchestrator = Orchestrator(
        bus=verified,
        run_id=run_id,
        seed=seed,
        config_hash=cfg_hash,
        pipeline=timed,
        node_agent_binding=provisioned if binding == "provisioned" else None,
        bind_on_first_sight=binding == "tofu",
        observers=tuple((getattr(pipeline, "attesters", None) or {}).values()),
        device_keys={n: k.public() for n, k in device_keys.items()} if device_keys else None,
    )
    if device_keys:
        pipeline.device_keys = {n: k.public() for n, k in device_keys.items()}
    watching: tuple[Any, ...] = ()
    if observers:
        from m1_monitoring.sensors.observers import IndependentObserver
        from m10_persona_drift.nhi import issue_signing_identity

        watching = tuple(
            IndependentObserver(
                d,
                issue_signing_identity(
                    f"observer-{d}", seed=hashlib.sha256(f"{run_id}:observer:{d}".encode()).digest()
                ),
            )
            for d in observers
        )
        pipeline.observers = watching
        pipeline.observer_keys = {o.dimension: o.identity.public() for o in watching}
    env = simpy.Environment()
    orchestrator.clock = SimPyClock(env)
    pipeline.adjudicator = _adjudicator(adjudication, scenario)
    orchestrator.attach()

    adversary = copy.deepcopy(scenario.adversary)
    if adversary is not None and getattr(adversary, "write_path", "n/a") is None:
        if getattr(pipeline, "curator", None) is not None and pipeline.attesters:
            adversary.write_path = pipeline.curator
            adversary.registry = {n: a.identity for n, a in pipeline.attesters.items()}
        else:
            registry, write_path = _memory_under_attack()
            adversary.write_path = write_path
            adversary.registry = registry

    if adversary is not None:
        context = RunContext(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=cfg_hash,
            pipeline=pipeline,
            identities=identities,
        )
        _attach_adversary(bus, adversary, context)

    wall_start, cpu_start, rss_start = time.perf_counter(), time.process_time(), _rss_mb()
    run_trust_sim(
        seed=seed,
        n_nodes=scenario.n_nodes,
        ticks=scenario.ticks,
        run_id=run_id,
        anomalies=scenario.anomaly_map,
        dimension_masks=scenario.dimension_masks,
        results_dir=results_dir,
        bus=bus,
        config=cfg,
        outages=dict(scenario.outages),
        env=env,
        noise_model=scenario.noise,
        restarts=dict(scenario.restarts),
        forged_observation=dict(scenario.forged_observation),
        forged_context=dict(scenario.forged_context),
        selective_reporting=dict(scenario.selective_reporting),
        message_loss=scenario.message_loss,
        dropped=dict(scenario.dropped),
        identities=identities,
        device_keys=device_keys or None,
        compromised_device=(
            dict.fromkeys(scenario.anomaly_map, compromised_device) if compromised_device else None
        ),
        observers=watching,
    )
    orchestrator.flush()
    gc.unfreeze()

    return ScenarioResult(
        scenario=scenario,
        baseline=baseline,
        seed=seed,
        pipeline=pipeline,
        orchestrator=orchestrator,
        adversary=adversary,
        params=params,
        operator=operator,
        adjudication=adjudication,
        binding=binding,
        approval_gate=gate,
        tick_seconds=timed.seconds,
        memory_read_seconds=read_seconds,
        memory_write_seconds=write_seconds,
        wall_seconds=time.perf_counter() - wall_start,
        cpu_seconds=time.process_time() - cpu_start,
        rss_mb=(rss_end := _rss_mb()),
        rss_mb_delta=(
            None if rss_end is None or rss_start is None else max(0.0, rss_end - rss_start)
        ),
        telemetry_rejected=getattr(verified, "rejected_count", 0),
        audit_checkpoint=pipeline.engine.audit.checkpoint().as_dict(),
        config_hash=cfg_hash,
    )


def _time_memory(pipeline: Any, read_seconds: list[float], write_seconds: list[float]) -> None:
    """Time memory recall and memory writes from outside the components."""
    source = pipeline.broker if pipeline.broker is not None else pipeline.recall
    if source is not None and hasattr(source, "recognise"):
        inner_recognise = source.recognise

        def timed_recognise(pattern_text: str) -> Any:
            start = time.perf_counter()
            try:
                return inner_recognise(pattern_text)
            finally:
                read_seconds.append(time.perf_counter() - start)

        source.recognise = timed_recognise  # type: ignore[method-assign]

    curator = pipeline.curator
    if curator is not None and hasattr(curator, "propose_and_submit"):
        inner_submit = curator.propose_and_submit

        def timed_submit(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                return inner_submit(*args, **kwargs)
            finally:
                write_seconds.append(time.perf_counter() - start)

        curator.propose_and_submit = timed_submit  # type: ignore[method-assign]


class _TimedPipeline:
    """Measures how long the pipeline takes per tick."""

    def __init__(self, inner: ClosedLoopPipeline) -> None:
        self.inner = inner
        self.seconds: list[float] = []

    def run(self, batch: Any) -> Any:
        start = time.perf_counter()
        try:
            return self.inner.run(batch)
        finally:
            self.seconds.append(time.perf_counter() - start)
            gc.freeze()


def _operator(mode: str) -> Any | None:
    """The approval model for isolation."""
    from agents.approval import ApprovalGate, ScriptedApproval

    if mode == "absent":
        return None
    if mode == "approve":
        return ApprovalGate(ScriptedApproval.always_approve())
    if mode == "deny":
        return ApprovalGate(ScriptedApproval.always_deny())
    if mode.startswith("approve_after:"):
        return ApprovalGate(ScriptedApproval.approve_after(float(mode.split(":", 1)[1])))
    raise ValueError(f"unknown operator model: {mode}")


def _rss_mb() -> float | None:
    try:
        import psutil
    except ImportError:  # pragma: no cover
        return None
    return psutil.Process().memory_info().rss / 1e6


def _adjudicator(mode: str, scenario: Scenario) -> Any | None:
    """The operator model that decides what a remembered incident *meant*."""
    from agents.adjudication import AutoConfirmAdjudicator, OracleAdjudicator

    if mode == "oracle":
        return OracleAdjudicator(compromised=scenario.compromised)
    if mode == "auto_confirm":
        return AutoConfirmAdjudicator()
    if mode == "none":
        return None
    raise ValueError(f"unknown adjudication mode: {mode}")


def _device_keys(n_nodes: int, run_id: str) -> dict[str, Any]:
    """Each device's attestation key, held by its sensor and by nothing else."""
    import hashlib

    from m10_persona_drift.nhi import issue_signing_identity

    return {
        f"node-{i}": issue_signing_identity(
            f"node-{i}", seed=hashlib.sha256(f"{run_id}:device:node-{i}".encode()).digest()
        )
        for i in range(n_nodes)
    }


def _fleet_identities(n_nodes: int, run_id: str) -> dict[str, Any]:
    """One software-bound identity per monitoring agent (M10 NHI)."""
    import hashlib

    from m10_persona_drift.nhi import issue_identity

    return {
        f"mon-node-{i}": issue_identity(
            f"mon-node-{i}", seed=hashlib.sha256(f"{run_id}:mon-node-{i}".encode()).digest()
        )
        for i in range(n_nodes)
    }


def _verifying_view(bus: InProcBus, identities: dict[str, Any], *, strict: bool = True) -> Any:
    """Subscriber-side verification of telemetry."""
    from agents.orchestrator import TRUST_TOPIC
    from shared.secure_bus import SignedBus

    any_identity = next(iter(identities.values()))
    return SignedBus(
        inner=bus,
        identity=any_identity,
        registry=identities,
        topics=frozenset({TRUST_TOPIC}),
        strict=strict,
    )


def _memory_under_attack() -> tuple[dict, Any]:
    """A stand-in write path, for arms that carry no immune memory of their own."""
    from m5_immune_memory import HashingEmbedder, MemoryStore, WritePath
    from m10_persona_drift.nhi import issue_identity
    from m11_memory_hardening import QuorumGate

    names = ("verifier", "correlation", "fusion", "orchestrator", "monitoring")
    registry = {n: issue_identity(n, seed=n.encode().ljust(32, b"\0")) for n in names}
    embedder = HashingEmbedder()
    return registry, WritePath(
        store=MemoryStore(dim=embedder.dim),
        gate=QuorumGate(registry=registry),
        embedder=embedder,
    )


def _attach_adversary(bus: Any, adversary: Any, context: RunContext) -> None:
    """Let the adversary act once per simulated moment."""
    seen: set[float] = set()

    def on_message(model: Any) -> None:
        from shared.secure_bus import inner_model

        model = inner_model(model)
        sim_time = getattr(model, "sim_time", None)
        if sim_time is None or sim_time in seen:
            return
        seen.add(sim_time)
        adversary.before_tick(context, sim_time)

    from agents.orchestrator import TRUST_TOPIC

    bus.subscribe(TRUST_TOPIC, on_message)


def run_grid(
    scenarios: tuple[Scenario, ...],
    baselines: tuple[Baseline, ...],
    *,
    seeds: tuple[int, ...] = (42,),
    **kwargs: Any,
) -> list[ScenarioResult]:
    """Every scenario against every baseline, for every seed."""
    return [
        run_scenario(scenario, baseline, seed=seed, **kwargs)
        for scenario in scenarios
        for baseline in baselines
        for seed in seeds
    ]
