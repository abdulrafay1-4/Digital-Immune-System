"""Graduated response levels: the memoryless half of M4."""

from __future__ import annotations

import math
from enum import IntEnum

_LEVEL_STEPS = 5

_BOUNDARY_EPS = 1e-9


class ResponseLevel(IntEnum):
    """The five graduated levels."""

    NONE = 0
    MONITOR = 1
    REAUTH = 2
    RESTRICT = 3
    ISOLATE = 4

    @property
    def requires_approval(self) -> bool:
        """L4 is never self-service."""
        return self is ResponseLevel.ISOLATE

    @property
    def description(self) -> str:
        return LEVEL_DESCRIPTION[self]


LEVEL_DESCRIPTION: dict[ResponseLevel, str] = {
    ResponseLevel.NONE: "no action",
    ResponseLevel.MONITOR: "enhanced monitoring (raised sample rate, no user-visible effect)",
    ResponseLevel.REAUTH: "re-authentication challenge",
    ResponseLevel.RESTRICT: "restrict: logical micro-segmentation (policy gate, not SDN)",
    ResponseLevel.ISOLATE: "isolate: requires human approval",
}

MIN_LEVEL = ResponseLevel.NONE
MAX_LEVEL = ResponseLevel.ISOLATE


def level_for_gt(gt: float) -> ResponseLevel:
    """`clamp(floor(5·(1 − GT)), 0, 4)`."""
    if not 0.0 <= gt <= 1.0:
        raise ValueError(f"gt must be in [0, 1], got {gt!r}")

    steps = math.floor(_LEVEL_STEPS * (1.0 - gt) + _BOUNDARY_EPS)
    return ResponseLevel(max(int(MIN_LEVEL), min(steps, int(MAX_LEVEL))))
