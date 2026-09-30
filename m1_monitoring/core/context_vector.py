"""Pure context-vector helpers: no I/O, no clock, no network."""

from __future__ import annotations

from shared.schemas import ContextVector


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def make_context(
    identity: float,
    behavioral: float,
    device: float,
    network: float,
) -> ContextVector:
    return ContextVector(
        identity=clamp01(identity),
        behavioral=clamp01(behavioral),
        device=clamp01(device),
        network=clamp01(network),
    )
