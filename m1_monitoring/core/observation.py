"""Observation O(t) from a 4-D context vector (pure math)."""

from __future__ import annotations

from m1_monitoring.core.context_vector import clamp01
from shared.schemas import ContextVector


def observation_from_context(
    ctx: ContextVector,
    *,
    w_identity: float = 0.25,
    w_behavioral: float = 0.25,
    w_device: float = 0.25,
    w_network: float = 0.25,
) -> float:
    """Weighted mean of dimensions."""
    weights = (w_identity, w_behavioral, w_device, w_network)
    total = sum(weights)
    if total <= 0:
        raise ValueError("context weights must sum to a positive value")
    dims = (ctx.identity, ctx.behavioral, ctx.device, ctx.network)
    o = sum(w * d for w, d in zip(weights, dims, strict=True)) / total
    return clamp01(o)
