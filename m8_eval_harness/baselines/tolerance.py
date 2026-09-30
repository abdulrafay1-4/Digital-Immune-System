"""
TOLERANCE (Hammar & Stadler, DSN 2024; arXiv 2404.01741v5): its node controller as a whole-system
comparator, and the two recovery baselines of its evaluation.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from m6_trust_fusion.fusion import TrustFusionEngine

OBSERVATIONS = 10
H, C = 0, 1
CONFIG = Path(__file__).resolve().parents[2] / "configs" / "tolerance.json"


def observation(o: float) -> int:
    """Named choice 1: a report's observation in [0, 1] on the paper's ten values."""
    return min(OBSERVATIONS - 1, int(math.floor(OBSERVATIONS * (1.0 - o))))


@dataclass(frozen=True)
class NodeModel:
    """Problem 1's model for one node: transitions (2), observations (3), cost (5)."""

    p_a: float
    p_c1: float
    p_c2: float
    p_u: float
    z_h: tuple[float, ...]
    z_c: tuple[float, ...]
    eta: float = 2.0

    def prior(self, b: Any, recover: Any) -> tuple[Any, Any]:
        """P[next state is H], P[next state is C] from belief b and the action, by (2)."""
        pa, pc1, pc2, pu = self.p_a, self.p_c1, self.p_c2, self.p_u
        from_h_to_h, from_h_to_c = (1 - pa) * (1 - pc1), (1 - pc1) * pa
        from_c_to_h = np.where(recover, (1 - pa) * (1 - pc2), (1 - pc2) * pu)
        from_c_to_c = np.where(recover, (1 - pc2) * pa, (1 - pc2) * (1 - pu))
        to_h = (1 - b) * from_h_to_h + b * from_c_to_h
        to_c = (1 - b) * from_h_to_c + b * from_c_to_c
        return to_h, to_c

    def belief(self, b: float, recover: bool, o: int) -> float:
        """Appendix A (e): the belief after the last action and the new observation."""
        to_h, to_c = self.prior(b, recover)
        numerator = self.z_c[o] * to_c
        return float(numerator / (self.z_h[o] * to_h + numerator))

    def average_cost(
        self, alpha: float, rng: np.random.Generator, episodes: int = 50, horizon: int = 500
    ) -> float:
        """J (5) for the threshold strategy b >= alpha, by simulating Problem 1."""
        pa, pc1, pc2, pu = self.p_a, self.p_c1, self.p_c2, self.p_u
        z_h, z_c = np.asarray(self.z_h), np.asarray(self.z_c)
        cdf_h, cdf_c = np.cumsum(z_h), np.cumsum(z_c)
        state = (rng.random(episodes) < pa).astype(int)
        b = np.full(episodes, pa)
        live = np.ones(episodes, dtype=bool)
        cost = np.zeros(episodes)
        steps = np.zeros(episodes)
        for _ in range(horizon):
            act = b >= alpha
            cost += np.where(live, self.eta * state - act * self.eta * state + act, 0.0)
            steps += live
            u = rng.random(episodes)
            crash = np.where(state == C, pc2, pc1)
            to_c = np.where(
                state == H,
                (1 - pc1) * pa,
                np.where(act, (1 - pc2) * pa, (1 - pc2) * (1 - pu)),
            )
            crashed = u < crash
            state = np.where(crashed, state, np.where(u < crash + to_c, C, H))
            live &= ~crashed
            draw = rng.random(episodes)
            obs = np.minimum(
                OBSERVATIONS - 1,
                np.where(
                    state == C,
                    np.searchsorted(cdf_c, draw, side="right"),
                    np.searchsorted(cdf_h, draw, side="right"),
                ),
            )
            to_h_p, to_c_p = self.prior(b, act)  # type: ignore[arg-type]
            num = z_c[obs] * to_c_p
            b = num / (z_h[obs] * to_h_p + num)
        return float(np.sum(cost) / max(1.0, np.sum(steps)))


def cross_entropy_threshold(
    model: NodeModel,
    seed: int = 0,
    population: int = 100,
    keep: float = 0.15,
    samples: int = 50,
    iterations: int = 30,
) -> tuple[float, float]:
    """Algorithm 1 with the cross-entropy method (Table 8: K = 100, keep 0.15, M = 50)."""
    rng = np.random.default_rng(seed)
    mean, std = 0.5, 0.25
    best = (0.5, float("inf"))
    elite_n = max(1, int(round(keep * population)))
    for _ in range(iterations):
        alphas = np.clip(rng.normal(mean, std, population), 0.0, 1.0)
        costs = [
            model.average_cost(a, np.random.default_rng(rng.integers(2**32)), samples)
            for a in alphas
        ]
        order = np.argsort(costs)
        elite = alphas[order[:elite_n]]
        if costs[order[0]] < best[1]:
            best = (float(alphas[order[0]]), float(costs[order[0]]))
        mean, std = float(np.mean(elite)), max(float(np.std(elite)), 1e-3)
    alpha = mean
    return alpha, model.average_cost(alpha, np.random.default_rng(seed + 1), samples * 10)


def paper_model(p_u: float) -> NodeModel:
    """Table 8's model for Figs."""
    from scipy.stats import betabinom

    support = np.arange(OBSERVATIONS)
    z_h = betabinom(10, 0.7, 3).pmf(support)
    z_c = betabinom(10, 1, 0.7).pmf(support)
    return NodeModel(
        p_a=0.1,
        p_c1=1e-5,
        p_c2=1e-3,
        p_u=p_u,
        z_h=tuple(z_h / z_h.sum()),
        z_c=tuple(z_c / z_c.sum()),
    )


@dataclass
class _ToleranceFusion(TrustFusionEngine):
    """TOLERANCE's node controller per device, as the whole decision."""

    model: Any = None
    alpha: float = 1.0
    periodic: int | None = None
    never: bool = False
    evict_silent: bool = True
    _belief: dict[str, float] = field(default_factory=dict, repr=False)
    _recovered: dict[str, bool] = field(default_factory=dict, repr=False)
    _roster: set[str] = field(default_factory=set, repr=False)

    def fuse_batch(self, updates, correlation=None):  # type: ignore[override]
        from m8_eval_harness.baselines.base import _observation, _signed_gt

        if correlation is not None:
            self.observe_correlation(correlation)
        out = []
        present = {u.node_id for u in updates}
        for u in updates:
            recover = self._decide(u.node_id, u.sim_time, observation(_observation(u, self)))
            out.append(
                _signed_gt(
                    self,
                    u.node_id,
                    u.sim_time,
                    gt=0.0 if recover else 1.0,
                    ts=_observation(u, self),
                )
            )
        self._roster |= present
        sim_time = updates[0].sim_time if updates else getattr(correlation, "sim_time", None)
        if self.evict_silent and sim_time is not None:
            for node_id in sorted(self._roster - present):
                self._belief.pop(node_id, None)
                self._recovered.pop(node_id, None)
                out.append(_signed_gt(self, node_id, sim_time, gt=0.0, ts=0.0))
        return out

    def _decide(self, node_id: str, sim_time: float, o: int) -> bool:
        if self.never:
            return False
        if self.periodic is not None:
            return int(sim_time) > 0 and int(sim_time) % self.periodic == 0
        model = self.model
        previous = self._belief.get(node_id)
        if previous is None:
            previous = model.p_a
            self._recovered[node_id] = previous >= self.alpha
        b = model.belief(previous, self._recovered[node_id], o)
        recover = b >= self.alpha
        self._belief[node_id], self._recovered[node_id] = b, recover
        return recover

    def observe_silence(self, node_id, *, sim_time, beta=0.01):  # type: ignore[override]
        return None


def site_config(site: str) -> Path:
    """Where the model measured on one real dataset's calibration half is kept."""
    return CONFIG.with_name(f"tolerance_{site}.json")


def fitted_model(path: Path = CONFIG) -> tuple[NodeModel, float]:
    """The model measured on calibration, and alpha from Algorithm 1 (`tolerance_fit`)."""
    doc = json.loads(path.read_text())
    m = doc["model"]
    model = NodeModel(
        p_a=m["p_a"],
        p_c1=m["p_c1"],
        p_c2=m["p_c2"],
        p_u=m["p_u"],
        z_h=tuple(m["z_h"]),
        z_c=tuple(m["z_c"]),
        eta=m["eta"],
    )
    return model, float(doc["alpha"])
