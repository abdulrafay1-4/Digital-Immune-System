"""Memory attesters in their own processes, over the broker."""

from __future__ import annotations

import secrets
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

from shared.schemas import AttestationRequest, SealedBatch, SignedAttestation

SEALED, CANDIDATES, ATTEST = "sealed", "candidates", "attest"
CONTROL = "control"
REPORTS_PER_FRAME = 20


def attester_user(name: str) -> str:
    return f"attester-{name}"


@dataclass
class SealedPublisher:
    """An orchestrator observer that sends each sealed batch to the attesters."""

    bus: Any
    published: int = 0

    def observe(self, batch: Any) -> None:
        updates = list(batch.updates)
        slices = [
            updates[i : i + REPORTS_PER_FRAME] for i in range(0, len(updates), REPORTS_PER_FRAME)
        ] or [[]]
        for part, chunk in enumerate(slices):
            self.bus.publish(
                SEALED,
                SealedBatch(
                    sim_time=batch.sim_time,
                    run_id=batch.run_id,
                    seed=batch.seed,
                    config_hash=batch.config_hash,
                    updates=chunk,
                    over_budget_agents=list(batch.over_budget_agents),
                    part=part,
                    parts=len(slices),
                ),
            )
        self.published += 1


@dataclass
class RemoteAttesters:
    """The control plane's side: put a candidate to every attester, gather signatures."""

    bus: Any
    names: tuple[str, ...]
    poll: Callable[[], Any] | None = None
    max_polls: int = 40
    replies: dict[str, list[Any]] = field(default_factory=dict)
    timed_out: int = 0

    def __post_init__(self) -> None:
        self.bus.discover = False
        self.bus.subscribe(ATTEST, self._reply)
        for name in self.names:
            self.bus.follow(ATTEST, attester_user(name))

    def _reply(self, message: Any) -> None:
        if isinstance(message, SignedAttestation) and message.request_id in self.replies:
            self.replies[message.request_id].append(message)

    def collect(self, candidate: Any, *, sim_time: float) -> list[Any]:
        from m11_memory_hardening.quorum import Attestation

        request_id = f"{candidate.record_id}:{secrets.token_hex(4)}"
        self.replies[request_id] = []
        self.bus.publish(
            CANDIDATES,
            AttestationRequest(
                sim_time=sim_time,
                run_id=candidate.run_id,
                seed=candidate.seed,
                config_hash=candidate.config_hash,
                request_id=request_id,
                record_id=candidate.record_id,
                pattern_text=candidate.pattern_text,
                threat_type=candidate.threat_type,
                node_ids=list(candidate.node_ids),
                window_start_sim=candidate.window_start_sim,
                window_end_sim=candidate.window_end_sim,
                proposer_id=candidate.proposer_id,
            ),
        )
        for _ in range(self.max_polls):
            if {r.attester_id for r in self.replies[request_id]} >= set(self.names):
                break
            (self.poll or (lambda: self.bus.pump(timeout=0.05)))()
        else:
            self.timed_out += 1
        signed = self.replies.pop(request_id)
        return [
            Attestation(
                record_hash=r.record_hash,
                attester_id=r.attester_id,
                signature=r.signature,
                sim_time=r.sim_time,
            )
            for r in signed
        ]

    def items(self) -> Iterable[tuple[str, Any]]:
        """No attester lives here: nothing to observe in-process."""
        return ()


@dataclass
class AttesterService:
    """One attester's process: observe sealed batches, answer candidates."""

    attester: Any
    bus: Any
    observed_until: float = -1.0
    signed: int = 0
    declined: int = 0
    _pending: list[AttestationRequest] = field(default_factory=list)
    _parts: dict[float, dict[int, SealedBatch]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.bus.discover = False
        self.bus.subscribe(SEALED, self._sealed)
        self.bus.subscribe(CANDIDATES, self._candidate)
        self.bus.follow(SEALED, CONTROL)
        self.bus.follow(CANDIDATES, CONTROL)

    def _sealed(self, message: Any) -> None:
        from agents.orchestrator import TickBatch

        if not isinstance(message, SealedBatch):
            return
        parts = self._parts.setdefault(message.sim_time, {})
        parts[message.part] = message
        if len(parts) < message.parts:
            return
        del self._parts[message.sim_time]
        whole = message.model_dump(exclude={"part", "parts"})
        whole["updates"] = [u for i in sorted(parts) for u in parts[i].model_dump()["updates"]]
        self.attester.observe(TickBatch(**whole))
        self.observed_until = max(self.observed_until, message.sim_time)

    def _candidate(self, message: Any) -> None:
        if isinstance(message, AttestationRequest):
            self._pending.append(message)

    def step(self, timeout: float = 0.05) -> None:
        """Read what arrived, then answer every candidate its evidence has caught up to."""
        self.bus.pump(timeout=timeout)
        ready = [r for r in self._pending if r.window_end_sim <= self.observed_until]
        self._pending = [r for r in self._pending if r not in ready]
        for request in ready:
            self._answer(request)

    def _answer(self, request: AttestationRequest) -> None:
        from m11_memory_hardening.quorum import MemoryCandidate

        candidate = MemoryCandidate(
            record_id=request.record_id,
            pattern_text=request.pattern_text,
            threat_type=request.threat_type,
            node_ids=tuple(request.node_ids),
            window_start_sim=request.window_start_sim,
            window_end_sim=request.window_end_sim,
            run_id=request.run_id,
            seed=request.seed,
            config_hash=request.config_hash,
            proposer_id=request.proposer_id,
        )
        attestation = self.attester.review(candidate, sim_time=request.sim_time)
        if attestation is None:
            self.declined += 1
            return
        self.signed += 1
        self.bus.publish(
            ATTEST,
            SignedAttestation(
                sim_time=request.sim_time,
                run_id=request.run_id,
                seed=request.seed,
                config_hash=request.config_hash,
                request_id=request.request_id,
                record_hash=attestation.record_hash,
                attester_id=attestation.attester_id,
                signature=attestation.signature,
            ),
        )
