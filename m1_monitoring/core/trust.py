"""EWMA trust score and exponential time decay (pure math, no I/O)."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class TrustParams:
    lam: float = 0.7
    beta: float = 0.01
    ts_min: float = 0.05
    ts_init: float = 1.0
    lam_up: float | None = None


def clamp_ts(ts: float, ts_min: float) -> float:
    if not math.isfinite(ts):
        raise ValueError(f"trust must be finite, got {ts!r}")
    return max(float(ts_min), min(1.0, float(ts)))


def ewma_update(
    ts: float,
    observation: float,
    lam: float,
    ts_min: float,
    lam_up: float | None = None,
) -> float:
    """TS(t+1) = λ·TS(t) + (1-λ)·O(t), clamped to [TS_min, 1]."""
    if not 0.0 <= lam <= 1.0:
        raise ValueError("lambda must be in [0, 1]")
    if lam_up is not None and not 0.0 <= lam_up <= 1.0:
        raise ValueError("lambda_up must be in [0, 1]")
    weight = lam_up if (lam_up is not None and observation > ts) else lam
    nxt = weight * ts + (1.0 - weight) * observation
    return clamp_ts(nxt, ts_min)


def apply_time_decay(ts: float, dt: float, beta: float, ts_min: float) -> float:
    """TS ← TS · e^(-β·dt), then floor."""
    if dt < 0:
        raise ValueError("dt must be >= 0")
    if beta < 0:
        raise ValueError("beta must be >= 0")
    if dt == 0 or beta == 0:
        return clamp_ts(ts, ts_min)
    return clamp_ts(ts * math.exp(-beta * dt), ts_min)


@dataclass
class TrustState:
    """Mutable per-node trust state for the monitoring agent."""

    ts: float
    params: TrustParams
    last_update_sim: float = 0.0

    @classmethod
    def initial(cls, params: TrustParams | None = None, *, sim_time: float = 0.0) -> TrustState:
        p = params or TrustParams()
        return cls(ts=clamp_ts(p.ts_init, p.ts_min), params=p, last_update_sim=sim_time)

    def step(self, observation: float, sim_time: float) -> float:
        """Apply decay for elapsed sim time, then EWMA update."""
        dt = sim_time - self.last_update_sim
        if dt < 0:
            raise ValueError("sim_time went backwards")
        decayed = apply_time_decay(self.ts, dt, self.params.beta, self.params.ts_min)
        self.ts = ewma_update(
            decayed, observation, self.params.lam, self.params.ts_min, self.params.lam_up
        )
        self.last_update_sim = sim_time
        return self.ts
