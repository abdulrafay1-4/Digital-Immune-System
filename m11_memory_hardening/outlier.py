"""M11 outlier detection: the other half of memory hardening."""

from __future__ import annotations

import statistics
from collections.abc import Mapping
from dataclasses import dataclass

_MAD_TO_SIGMA = 0.6745


@dataclass(frozen=True)
class OutlierParams:
    z_threshold: float = 3.0
    quarantine_below: float = 0.35
    min_population: int = 5
    never_quarantine_above: float = 0.60
    uniform_tolerance: float = 0.05

    def __post_init__(self) -> None:
        if self.z_threshold <= 0:
            raise ValueError(f"z_threshold must be positive, got {self.z_threshold}")
        if not 0.0 <= self.quarantine_below <= 1.0:
            raise ValueError(f"quarantine_below must be in [0, 1], got {self.quarantine_below}")
        if self.never_quarantine_above < self.quarantine_below:
            raise ValueError(
                "never_quarantine_above must be at least quarantine_below, or the "
                "absolute floor and the absolute ceiling contradict each other"
            )
        if self.min_population < 1:
            raise ValueError(f"min_population must be at least 1, got {self.min_population}")
        if not 0.0 < self.uniform_tolerance <= 1.0:
            raise ValueError(f"uniform_tolerance must be in (0, 1], got {self.uniform_tolerance}")


@dataclass(frozen=True)
class AgentVerdict:
    agent_id: str
    reliability: float
    robust_z: float
    quarantined: bool
    reason: str | None = None


@dataclass(frozen=True)
class OutlierReport:
    verdicts: tuple[AgentVerdict, ...]
    median: float
    mad: float
    population: int
    statistics_applied: bool

    @property
    def quarantined(self) -> frozenset[str]:
        """Feed this straight into `QuorumGate.quarantined`."""
        return frozenset(v.agent_id for v in self.verdicts if v.quarantined)

    def verdict_for(self, agent_id: str) -> AgentVerdict | None:
        return next((v for v in self.verdicts if v.agent_id == agent_id), None)


def median_absolute_deviation(values: list[float], med: float) -> float:
    return statistics.median([abs(v - med) for v in values])


def robust_z(value: float, med: float, mad: float) -> float:
    """Signed robust z."""
    if mad <= 0.0:
        return 0.0
    return _MAD_TO_SIGMA * (value - med) / mad


def assess(
    reliabilities: Mapping[str, float],
    params: OutlierParams | None = None,
) -> OutlierReport:
    """Assess a population of agent reliabilities in one pass."""
    p = params or OutlierParams()
    if not reliabilities:
        return OutlierReport((), median=0.0, mad=0.0, population=0, statistics_applied=False)

    values = list(reliabilities.values())
    med = statistics.median(values)
    mad = median_absolute_deviation(values, med)

    big_enough = len(values) >= p.min_population
    apply_stats = big_enough and mad > 0.0
    apply_uniform = big_enough and mad == 0.0

    verdicts = []
    for agent_id in sorted(reliabilities):
        value = reliabilities[agent_id]
        z = robust_z(value, med, mad) if apply_stats else 0.0

        objectively_fine = value >= p.never_quarantine_above
        if value < p.quarantine_below:
            quarantined, reason = True, "below_floor"
        elif objectively_fine:
            quarantined, reason = False, None
        elif apply_stats and z <= -p.z_threshold:
            quarantined, reason = True, "low_outlier"
        elif apply_uniform and value < med - p.uniform_tolerance:
            quarantined, reason = True, "below_unanimous_median"
        else:
            quarantined, reason = False, None

        verdicts.append(
            AgentVerdict(
                agent_id=agent_id,
                reliability=value,
                robust_z=z,
                quarantined=quarantined,
                reason=reason,
            )
        )

    return OutlierReport(
        verdicts=tuple(verdicts),
        median=med,
        mad=mad,
        population=len(values),
        statistics_applied=apply_stats or apply_uniform,
    )
