"""Deterministic threat classifier, with no LLM."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from agents.orchestrator import TickBatch
from shared.schemas import Classification

ACTOR_ID = "rules_classifier"


class ThreatType(StrEnum):
    NONE = "none"
    CREDENTIAL_ABUSE = "credential_abuse"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    DEVICE_COMPROMISE = "device_compromise"
    NETWORK_ANOMALY = "network_anomaly"
    UNKNOWN = "unknown"


class Scope(StrEnum):
    NONE = "none"
    SINGLE_NODE = "single_node"
    COORDINATED = "coordinated"


DIMENSION_THREAT = {
    "identity": ThreatType.CREDENTIAL_ABUSE,
    "behavioral": ThreatType.ANOMALOUS_BEHAVIOR,
    "device": ThreatType.DEVICE_COMPROMISE,
    "network": ThreatType.NETWORK_ANOMALY,
}

DIMENSIONS = tuple(DIMENSION_THREAT)


class RulesParams(BaseModel):
    """Thresholds and weights."""

    model_config = ConfigDict(extra="forbid")

    affected_below: float = Field(default=0.60, ge=0.0, le=1.0)
    coordinated_min_nodes: int = Field(default=2, ge=2)
    depth_weight: float = Field(default=0.7, ge=0.0, le=1.0)


class RulesClassifier:
    """Classifies a sealed batch using thresholds and arithmetic only."""

    def __init__(self, params: RulesParams | None = None) -> None:
        self.params = params or RulesParams()

    def classify(self, batch: TickBatch) -> Classification:
        if not batch.updates:
            raise ValueError("cannot classify an empty batch")

        par = self.params
        affected = [u for u in batch.updates if u.node_trust < par.affected_below]

        if not affected:
            return self._result(
                batch,
                ThreatType.NONE,
                Scope.NONE,
                severity=0.0,
                rationale=(f"all {len(batch.updates)} nodes at or above {par.affected_below:.2f}"),
            )

        scope = (
            Scope.COORDINATED if len(affected) >= par.coordinated_min_nodes else Scope.SINGLE_NODE
        )

        means = {
            dim: sum(getattr(u.context, dim) for u in affected) / len(affected)
            for dim in DIMENSIONS
        }
        worst_dim = min(DIMENSIONS, key=lambda d: means[d])
        threat = DIMENSION_THREAT[worst_dim]

        depth = 1.0 - min(u.node_trust for u in affected)
        breadth = len(affected) / len(batch.updates)
        severity = _clamp(par.depth_weight * depth + (1.0 - par.depth_weight) * breadth)

        rationale = (
            f"{len(affected)}/{len(batch.updates)} node(s) below "
            f"{par.affected_below:.2f}; most degraded dimension '{worst_dim}' "
            f"(mean {means[worst_dim]:.3f}); depth {depth:.3f}, breadth {breadth:.3f}"
        )
        return self._result(batch, threat, scope, severity=severity, rationale=rationale)

    def _result(
        self,
        batch: TickBatch,
        threat: ThreatType,
        scope: Scope,
        *,
        severity: float,
        rationale: str,
    ) -> Classification:
        return Classification(
            sim_time=batch.sim_time,
            run_id=batch.run_id,
            seed=batch.seed,
            config_hash=batch.config_hash,
            threat_type=threat.value,
            severity=severity,
            rationale=f"[{scope.value}] {rationale}",
            used_llm=False,
            cache_hit=False,
        )


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))
