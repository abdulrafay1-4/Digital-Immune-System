"""M1 core: pure trust math, no I/O."""

from m1_monitoring.core.context_vector import clamp01, make_context
from m1_monitoring.core.observation import observation_from_context
from m1_monitoring.core.trust import TrustParams, TrustState, apply_time_decay, ewma_update

__all__ = [
    "TrustParams",
    "TrustState",
    "apply_time_decay",
    "clamp01",
    "ewma_update",
    "make_context",
    "observation_from_context",
]
