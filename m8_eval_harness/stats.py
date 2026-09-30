"""Statistics for the evaluation: paired, non-parametric, corrected, with effect sizes."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Interval:
    estimate: float
    low: float
    high: float

    def __str__(self) -> str:
        return f"{self.estimate:+.3f} [{self.low:+.3f}, {self.high:+.3f}]"


def _clean(values: Sequence[float | None]) -> np.ndarray:
    return np.asarray([v for v in values if v is not None and np.isfinite(v)], dtype=float)


def bootstrap_mean(
    values: Sequence[float | None], *, n_boot: int = 10_000, alpha: float = 0.05, seed: int = 0
) -> Interval | None:
    """Percentile bootstrap interval for a mean."""
    data = _clean(values)
    if data.size == 0:
        return None
    rng = np.random.default_rng(seed)
    means = rng.choice(data, size=(n_boot, data.size), replace=True).mean(axis=1)
    return Interval(
        float(data.mean()),
        float(np.percentile(means, 100 * alpha / 2)),
        float(np.percentile(means, 100 * (1 - alpha / 2))),
    )


def paired_differences(a: Sequence[float | None], b: Sequence[float | None]) -> np.ndarray:
    """`a - b` over the pairs where both are present."""
    if len(a) != len(b):
        raise ValueError("paired samples must be the same length")
    return np.asarray(
        [x - y for x, y in zip(a, b, strict=True) if x is not None and y is not None], dtype=float
    )


def paired_bootstrap(
    a: Sequence[float | None], b: Sequence[float | None], **kwargs: float
) -> Interval | None:
    """Interval for the mean paired difference `a - b`."""
    return bootstrap_mean(list(paired_differences(a, b)), **kwargs)  # type: ignore[arg-type]


def wilcoxon_p(a: Sequence[float | None], b: Sequence[float | None]) -> float:
    """Two-sided Wilcoxon signed-rank p-value on the paired differences."""
    from scipy.stats import wilcoxon

    diffs = paired_differences(a, b)
    if diffs.size == 0 or np.allclose(diffs, 0.0):
        return 1.0
    return float(wilcoxon(diffs, zero_method="zsplit", alternative="two-sided").pvalue)


def rank_biserial(a: Sequence[float | None], b: Sequence[float | None]) -> float:
    """Matched-pairs rank-biserial correlation in [-1, 1]."""
    from scipy.stats import rankdata

    diffs = paired_differences(a, b)
    diffs = diffs[diffs != 0]
    if diffs.size == 0:
        return 0.0
    ranks = rankdata(np.abs(diffs))
    positive = ranks[diffs > 0].sum()
    negative = ranks[diffs < 0].sum()
    return float((positive - negative) / ranks.sum())


def vargha_delaney_a(a: Sequence[float | None], b: Sequence[float | None]) -> float | None:
    """Vargha and Delaney's A: P(a random run of `a` beats one of `b`), ties counted half."""
    ca, cb = _clean(a), _clean(b)
    if not ca.size or not cb.size:
        return None
    greater = (ca[:, None] > cb[None, :]).sum()
    ties = (ca[:, None] == cb[None, :]).sum()
    return float((greater + 0.5 * ties) / (ca.size * cb.size))


def holm(p_values: Mapping[str, float]) -> dict[str, float]:
    """Holm-Bonferroni adjusted p-values, monotone and capped at 1."""
    ordered = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(ordered)
    adjusted: dict[str, float] = {}
    running = 0.0
    for i, (key, p) in enumerate(ordered):
        running = max(running, min(1.0, (m - i) * p))
        adjusted[key] = running
    return adjusted


@dataclass(frozen=True)
class Comparison:
    """One claim: arm `a` against arm `b` on one metric, over paired seeds."""

    metric: str
    a: str
    b: str
    n: int
    mean_a: float | None
    mean_b: float | None
    difference: Interval | None
    p_value: float
    effect_size: float
    p_adjusted: float | None = None
    a12: float | None = None


def compare(
    metric: str,
    a_name: str,
    a: Sequence[float | None],
    b_name: str,
    b: Sequence[float | None],
    *,
    seed: int = 0,
) -> Comparison:
    ca, cb = _clean(a), _clean(b)
    return Comparison(
        metric=metric,
        a=a_name,
        b=b_name,
        n=int(paired_differences(a, b).size),
        mean_a=float(ca.mean()) if ca.size else None,
        mean_b=float(cb.mean()) if cb.size else None,
        difference=paired_bootstrap(a, b, seed=seed),
        p_value=wilcoxon_p(a, b),
        effect_size=rank_biserial(a, b),
        a12=vargha_delaney_a(a, b),
    )


def adjust(comparisons: Sequence[Comparison]) -> list[Comparison]:
    """Holm-correct a family of comparisons together."""
    adjusted = holm({str(i): c.p_value for i, c in enumerate(comparisons)})
    return [
        Comparison(**{**c.__dict__, "p_adjusted": adjusted[str(i)]})
        for i, c in enumerate(comparisons)
    ]
