"""M7 self-healing: pure recovery mathematics. No clock, no I/O, no state."""

from __future__ import annotations

from dataclasses import dataclass


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


@dataclass(frozen=True)
class HealingParams:
    tau_h: float = 0.35
    eta: float = 0.6
    target_ts: float = 0.70
    converge_rate: float = 0.25
    reintegrate_ticks: int = 8
    rs_healed: float = 0.65
    relapse_drop: float = 0.10
    max_auto_attempts: int = 2

    def __post_init__(self) -> None:
        if not 0.0 < self.tau_h < 1.0:
            raise ValueError(f"tau_h must be in (0, 1), got {self.tau_h}")
        if not 0.0 <= self.eta <= 1.0:
            raise ValueError(f"eta must be in [0, 1], got {self.eta}")
        if not 0.0 < self.converge_rate <= 1.0:
            raise ValueError(f"converge_rate must be in (0, 1], got {self.converge_rate}")
        if self.reintegrate_ticks < 1:
            raise ValueError(f"reintegrate_ticks must be at least 1, got {self.reintegrate_ticks}")
        if self.max_auto_attempts < 0:
            raise ValueError(f"max_auto_attempts must be >= 0, got {self.max_auto_attempts}")


def recovery_score(gt: float, health: float, *, eta: float = 0.6) -> float:
    """`RS = eta*GT + (1 - eta)*health`."""
    return clamp01(eta * clamp01(gt) + (1.0 - eta) * clamp01(health))


def should_heal(gt: float, *, tau_h: float = 0.35) -> bool:
    """`Heal = 1 if GT < tau_h else 0`."""
    return clamp01(gt) < tau_h


def converge(current_ts: float, target_ts: float, *, rate: float = 0.25) -> float:
    """One step of TS toward the recalibration target."""
    cur, tgt = clamp01(current_ts), clamp01(target_ts)
    return clamp01(cur + rate * (tgt - cur))


def ticks_to_reach(
    current_ts: float,
    target_ts: float,
    *,
    rate: float = 0.25,
    tolerance: float = 0.01,
) -> int:
    """How many convergence steps until TS is within `tolerance` of the target."""
    if rate <= 0.0:
        raise ValueError("rate must be positive")
    cur, tgt = clamp01(current_ts), clamp01(target_ts)
    steps = 0
    while abs(tgt - cur) > tolerance:
        cur = converge(cur, tgt, rate=rate)
        steps += 1
        if steps > 1000:
            break
    return steps
