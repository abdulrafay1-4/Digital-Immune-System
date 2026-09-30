"""Persona-drift detector: a z-score on fixed invariants (not an LLM)."""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

from m10_persona_drift.baseline import PersonaBaseline
from m10_persona_drift.nhi import AgentIdentity, verify_binding


@dataclass
class DriftParams:
    rate_window: int = 20
    z_threshold: float = 3.0
    min_samples: int = 5


@dataclass
class DriftObservation:
    """One tick of agent behaviour for invariant checks."""

    agent_id: str
    sim_time: float
    messages_this_tick: int = 1
    capability_requested: str | None = None
    output_keys: frozenset[str] = field(default_factory=frozenset)
    identity: AgentIdentity | None = None
    claimed_agent_id: str | None = None


@dataclass
class DriftResult:
    agent_id: str
    drift_flag: float
    reasons: list[str] = field(default_factory=list)


class PersonaDriftDetector:
    def __init__(
        self,
        baseline: PersonaBaseline,
        params: DriftParams | None = None,
        *,
        bound_identity: AgentIdentity | None = None,
    ) -> None:
        self.baseline = baseline
        self.params = params or DriftParams()
        self.bound_identity = bound_identity
        self._rates: deque[float] = deque(maxlen=self.params.rate_window)
        self._cap_counts: dict[str, int] = {c: 0 for c in baseline.allowed_capabilities}
        self._cap_total: int = 0

    def observe(self, obs: DriftObservation) -> DriftResult:
        reasons: list[str] = []
        scores: list[float] = []

        if self.bound_identity is not None:
            claimed = obs.claimed_agent_id or obs.agent_id
            if obs.identity is None:
                reasons.append("missing_identity")
                scores.append(1.0)
            elif not verify_binding(obs.identity, claimed):
                reasons.append("identity_mismatch")
                scores.append(1.0)
            elif obs.identity.public_id != self.bound_identity.public_id:
                reasons.append("forged_identity")
                scores.append(1.0)

        rate = float(obs.messages_this_tick)
        self._rates.append(rate)
        if len(self._rates) >= self.params.min_samples:
            mean = sum(self._rates) / len(self._rates)
            var = sum((x - mean) ** 2 for x in self._rates) / len(self._rates)
            std = math.sqrt(var) if var > 0 else 0.0
            expected = self.baseline.message_rate
            if std > 1e-9:
                z = abs(rate - expected) / std
            else:
                z = abs(rate - expected) / max(expected, 1e-9)
            if z >= self.params.z_threshold:
                reasons.append("message_rate_drift")
                scores.append(min(1.0, z / (2 * self.params.z_threshold)))

        if obs.capability_requested is not None:
            cap = obs.capability_requested
            if cap not in self.baseline.allowed_capabilities:
                reasons.append("disallowed_capability")
                scores.append(1.0)
            else:
                self._cap_counts[cap] = self._cap_counts.get(cap, 0) + 1
                self._cap_total += 1
                if self._cap_total >= self.params.min_samples:
                    actual = self._cap_counts[cap] / self._cap_total
                    expected_mix = self.baseline.capability_mix.get(cap, 0.0)
                    if abs(actual - expected_mix) > 0.4:
                        reasons.append("capability_mix_drift")
                        scores.append(min(1.0, abs(actual - expected_mix)))

        if obs.output_keys:
            missing = self.baseline.required_schema_keys - obs.output_keys
            if missing:
                reasons.append("schema_nonconformance")
                scores.append(1.0)

        drift_flag = max(scores) if scores else 0.0
        return DriftResult(
            agent_id=obs.agent_id,
            drift_flag=min(1.0, drift_flag),
            reasons=reasons,
        )
