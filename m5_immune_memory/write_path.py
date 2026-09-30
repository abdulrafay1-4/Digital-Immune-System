"""M5 write path: the curator proposes, the quorum gate decides."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from m5_immune_memory.embeddings import Embedder, default_embedder
from m5_immune_memory.store import MemoryStore
from m11_memory_hardening.quorum import (
    Attestation,
    MemoryCandidate,
    QuorumDecision,
    QuorumGate,
)
from shared.schemas import MemoryRecord

CURATOR_ID = "memory-curator"

MATERIAL_LEVEL = 2

LIVENESS_WINDOW_SIM = 5.0


def is_material(peak_level: int) -> bool:
    """Deterministically checkable, so attesters verify it rather than trusting it."""
    if not 0 <= peak_level <= 4:
        raise ValueError(f"peak_level must be 0..4, got {peak_level}")
    return peak_level >= MATERIAL_LEVEL


@dataclass(frozen=True)
class IncidentSummary:
    """A resolved incident, as the reasoning plane saw it."""

    record_id: str
    node_ids: tuple[str, ...]
    peak_level: int
    threat_type: str
    pattern_text: str
    window_start_sim: float
    window_end_sim: float
    run_id: str
    seed: int
    config_hash: str


@dataclass(frozen=True)
class WriteResult:
    admitted: bool
    decision: QuorumDecision | None
    record: MemoryRecord | None = None
    reason: str | None = None


class MemoryCurator:
    """Turns a resolved incident into a candidate."""

    def __init__(self, curator_id: str = CURATOR_ID) -> None:
        self.curator_id = curator_id

    def propose(self, incident: IncidentSummary) -> MemoryCandidate | None:
        """`None` when the incident is immaterial, which is not a failure."""
        if not is_material(incident.peak_level):
            return None
        return MemoryCandidate(
            record_id=incident.record_id,
            pattern_text=incident.pattern_text,
            threat_type=incident.threat_type,
            node_ids=tuple(sorted(incident.node_ids)),
            window_start_sim=incident.window_start_sim,
            window_end_sim=incident.window_end_sim,
            run_id=incident.run_id,
            seed=incident.seed,
            config_hash=incident.config_hash,
            proposer_id=self.curator_id,
        )


@dataclass
class LivenessMonitor:
    """Makes a curator's silence as visible as a lie."""

    window_sim: float = LIVENESS_WINDOW_SIM
    _pending: dict[str, float] = field(default_factory=dict)

    def incident_resolved(self, record_id: str, peak_level: int, *, sim_time: float) -> None:
        if is_material(peak_level):
            self._pending[record_id] = sim_time

    def candidate_proposed(self, record_id: str) -> None:
        self._pending.pop(record_id, None)

    def overdue(self, now_sim: float) -> list[str]:
        """Material incidents with no candidate after the window."""
        return sorted(rid for rid, at in self._pending.items() if now_sim - at > self.window_sim)


@dataclass
class WritePath:
    """The only thing that may add to the store."""

    store: MemoryStore
    gate: QuorumGate
    embedder: Embedder = field(default_factory=default_embedder)
    curator: MemoryCurator = field(default_factory=MemoryCurator)
    liveness: LivenessMonitor = field(default_factory=LivenessMonitor)
    initial_status: str = "pending"
    coalesced: int = 0

    def submit(
        self,
        candidate: MemoryCandidate,
        attestations: Iterable[Attestation],
        *,
        now_sim: float,
    ) -> WriteResult:
        """Run the gate, then store only if it admits."""
        self.liveness.candidate_proposed(candidate.record_id)
        decision = self.gate.admit(candidate, attestations, now_sim=now_sim)
        if not decision.admitted or decision.certificate is None:
            return WriteResult(
                admitted=False,
                decision=decision,
                reason=f"quorum_not_met: {len(decision.accepted)}/{decision.k}",
            )
        existing = self.store.find_pattern(candidate.pattern_text, candidate.threat_type)
        if existing is not None:
            self.coalesced += 1
            return WriteResult(
                admitted=False,
                decision=decision,
                record=existing,
                reason=f"duplicate_of: {existing.record_id}",
            )

        record = MemoryRecord(
            sim_time=now_sim,
            run_id=candidate.run_id,
            seed=candidate.seed,
            config_hash=candidate.config_hash,
            record_id=candidate.record_id,
            pattern_text=candidate.pattern_text,
            threat_type=candidate.threat_type,
            node_ids=list(candidate.node_ids),
            window_start_sim=candidate.window_start_sim,
            window_end_sim=candidate.window_end_sim,
            proposer_id=candidate.proposer_id,
            embedding_dim=self.embedder.dim,
            quorum_certificate=decision.certificate,
        )
        self.store.add(record, self.embedder.embed(candidate.pattern_text))
        if self.initial_status == "confirmed":
            record = self.store.adjudicate(
                record.record_id, "confirmed", actor="auto-confirm", sim_time=now_sim
            )
        return WriteResult(admitted=True, decision=decision, record=record)

    def propose_and_submit(
        self,
        incident: IncidentSummary,
        attesters: Mapping[str, Any],
        *,
        now_sim: float,
    ) -> WriteResult:
        """The full path: propose, ask each attester, submit what they sign to the gate."""
        from m11_memory_hardening.quorum import attest

        candidate = self.curator.propose(incident)
        if candidate is None:
            return WriteResult(admitted=False, decision=None, reason="immaterial")
        atts = []
        for _, attester in sorted(attesters.items()):
            if hasattr(attester, "review"):
                signed = attester.review(candidate, sim_time=now_sim)
                if signed is not None:
                    atts.append(signed)
            else:
                atts.append(attest(candidate, attester, sim_time=now_sim))
        if not atts:
            return WriteResult(admitted=False, decision=None, reason="attesters_disagree")
        return self.submit(candidate, atts, now_sim=now_sim)
