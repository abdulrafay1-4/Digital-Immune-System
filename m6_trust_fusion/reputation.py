"""
Per-node reputation: an asymmetric EWMA of response outcomes that falls fast and is earned back
slowly, with the plain success ratio kept for comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


def clamp(x: float, lo: float, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def interaction_success(level: int) -> bool:
    """One completed response is one interaction."""
    if not 0 <= level <= 4:
        raise ValueError(f"level must be 0..4, got {level}")
    return level == 0


class RepMode(StrEnum):
    EWMA = "ewma"
    RATIO = "ratio"


@dataclass
class ReputationParams:
    rep_init: float = 1.0
    rep_min: float = 0.05
    mode: RepMode = RepMode.EWMA
    lam_down: float = 0.6
    lam_up: float = 0.95

    def __post_init__(self) -> None:
        for name in ("lam_down", "lam_up"):
            value = getattr(self, name)
            if not 0.0 <= value < 1.0:
                raise ValueError(f"{name} must be in [0, 1), got {value}")
        if self.lam_up < self.lam_down:
            raise ValueError(
                "lam_up must be at least lam_down: reputation is earned back more "
                "slowly than it is lost, never the reverse"
            )
        if not 0.0 <= self.rep_min <= 1.0:
            raise ValueError(f"rep_min must be in [0, 1], got {self.rep_min}")


@dataclass
class ReputationTracker:
    """Per-node reputation, in whichever mode the params select."""

    params: ReputationParams = field(default_factory=ReputationParams)
    _success: dict[str, int] = field(default_factory=dict)
    _total: dict[str, int] = field(default_factory=dict)
    _ewma: dict[str, float] = field(default_factory=dict)

    def get(self, node_id: str) -> float:
        if self.params.mode is RepMode.EWMA:
            value = self._ewma.get(node_id, self.params.rep_init)
            return clamp(value, self.params.rep_min)

        total = self._total.get(node_id, 0)
        if total <= 0:
            return clamp(self.params.rep_init, self.params.rep_min)
        return clamp(self._success[node_id] / total, self.params.rep_min)

    def record(self, node_id: str, *, success: bool) -> float:
        self._total[node_id] = self._total.get(node_id, 0) + 1
        self._success[node_id] = self._success.get(node_id, 0) + (1 if success else 0)

        lam = self.params.lam_up if success else self.params.lam_down
        previous = self._ewma.get(node_id, self.params.rep_init)
        self._ewma[node_id] = lam * previous + (1.0 - lam) * (1.0 if success else 0.0)
        return self.get(node_id)

    def interactions(self, node_id: str) -> int:
        """How many completed responses this device has been through."""
        return self._total.get(node_id, 0)

    def snapshot(self) -> dict[str, float]:
        ids = set(self._total) | set(self._success) | set(self._ewma)
        if not ids:
            return {}
        return {nid: self.get(nid) for nid in ids}
