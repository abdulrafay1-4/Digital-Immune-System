"""An independent memory attester: its own key, its own view of the evidence, its own check."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from agents.correlation import CorrelationAgent
from m10_persona_drift.nhi import SigningIdentity, VerifyingIdentity
from m11_memory_hardening.outlier import OutlierParams, assess
from m11_memory_hardening.quorum import Attestation, MemoryCandidate, attest

EVIDENCE_HORIZON_SIM = 60.0


@dataclass
class IndependentAttester:
    identity: SigningIdentity
    correlator: CorrelationAgent
    outlier_params: OutlierParams | None = None
    horizon_sim: float = EVIDENCE_HORIZON_SIM
    _evidence: deque[tuple[float, str, frozenset[str]]] = field(default_factory=deque, repr=False)
    _quarantined: frozenset[str] = field(default_factory=frozenset, repr=False)
    refused: int = 0

    @property
    def agent_id(self) -> str:
        return self.identity.agent_id

    def public(self) -> VerifyingIdentity:
        return self.identity.public()

    def observe(self, batch: Any) -> None:
        """Called by the orchestrator with every sealed batch, before the pipeline."""
        result = self.correlator.correlate(batch, quarantined_agent_ids=sorted(self._quarantined))
        if result.pattern_text:
            self._evidence.append(
                (batch.sim_time, result.pattern_text, frozenset(result.implicated_node_ids))
            )
        horizon = batch.sim_time - self.horizon_sim
        while self._evidence and self._evidence[0][0] < horizon:
            self._evidence.popleft()
        report = assess(self.correlator.tracker.snapshot(), self.outlier_params)
        self._quarantined = report.quarantined

    def shows(self, candidate: MemoryCandidate) -> bool:
        """Did the batches this attester saw show this pattern, on these devices?"""
        window = [
            (pattern, implicated)
            for sim_time, pattern, implicated in self._evidence
            if candidate.window_start_sim <= sim_time <= candidate.window_end_sim
        ]
        if not any(pattern == candidate.pattern_text for pattern, _ in window):
            return False
        seen: set[str] = set()
        for _, implicated in window:
            seen |= implicated
        return set(candidate.node_ids) <= seen

    def review(self, candidate: MemoryCandidate, *, sim_time: float) -> Attestation | None:
        if not self.shows(candidate):
            self.refused += 1
            return None
        return attest(candidate, self.identity, sim_time=sim_time)
