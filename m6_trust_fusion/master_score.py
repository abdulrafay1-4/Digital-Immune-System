"""Master DIS score: a composite for the operator console and reporting."""

from __future__ import annotations

from dataclasses import dataclass


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


@dataclass(frozen=True)
class MasterScoreWeights:
    w_ts: float = 0.25
    w_cti: float = 0.20
    w_gt: float = 0.25
    w_resp: float = 0.15
    w_health: float = 0.15

    def __post_init__(self) -> None:
        total = self.w_ts + self.w_cti + self.w_gt + self.w_resp + self.w_health
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"master score weights must sum to 1, got {total}")


def master_score(
    *,
    ts: float,
    cti_i: float,
    gt: float,
    response_level: float = 0.0,
    health: float = 1.0,
    weights: MasterScoreWeights | None = None,
) -> float:
    """DIS = w1·TS + w2·(1−CTI) + w3·GT + w4·RespTrust + w5·Health."""
    w = weights or MasterScoreWeights()
    resp_trust = 1.0 - (float(response_level) / 4.0)
    return clamp01(
        w.w_ts * ts
        + w.w_cti * (1.0 - cti_i)
        + w.w_gt * gt
        + w.w_resp * resp_trust
        + w.w_health * health
    )
