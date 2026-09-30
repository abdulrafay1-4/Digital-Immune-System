"""M11 outlier detection: down-weighting and quarantine of inconsistent agents."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from m10_persona_drift.nhi import issue_identity
from m11_memory_hardening import MemoryCandidate, QuorumGate, attest
from m11_memory_hardening.outlier import (
    OutlierParams,
    assess,
    robust_z,
)

HEALTHY = {f"agent-{i:02d}": 0.94 + (i % 3) * 0.01 for i in range(9)}


def test_a_healthy_population_quarantines_nobody() -> None:
    report = assess(HEALTHY)
    assert report.quarantined == frozenset()
    assert report.statistics_applied is True


def test_one_low_agent_in_a_healthy_fleet_is_quarantined() -> None:
    pop = {**HEALTHY, "agent-0448": 0.21}
    report = assess(pop)
    assert report.quarantined == frozenset({"agent-0448"})

    v = report.verdict_for("agent-0448")
    assert v.robust_z < -3.0
    assert v.reason == "below_floor"


def test_a_low_outlier_above_the_floor_is_caught_by_statistics() -> None:
    """The floor alone is not enough: this agent would pass it."""
    pop = {**HEALTHY, "drifting": 0.55}
    report = assess(pop)
    v = report.verdict_for("drifting")
    assert v.reliability > OutlierParams().quarantine_below
    assert v.reason == "low_outlier"
    assert v.quarantined is True


def test_an_unusually_high_agent_is_never_quarantined() -> None:
    """Two-sided detection would quarantine the best reporter in the fleet."""
    pop = {f"a{i}": 0.50 + i * 0.01 for i in range(9)}
    pop["star"] = 1.0
    report = assess(pop)
    assert report.mad > 0.0
    assert report.verdict_for("star").robust_z > 3.0, "unusual by any measure"
    assert report.quarantined == frozenset(), "but unusual upward is not a threat"


def test_a_uniformly_compromised_fleet_is_still_caught_by_the_floor() -> None:
    """Everyone equally bad looks perfectly consistent, so no z-score can fire."""
    pop = {f"a{i}": 0.10 for i in range(9)}
    report = assess(pop)
    assert report.mad == 0.0
    assert all(v.robust_z == 0.0 for v in report.verdicts)
    assert report.quarantined == frozenset(pop), "the floor still fires"
    assert all(v.reason == "below_floor" for v in report.verdicts)


def test_one_bad_agent_in_a_unanimous_fleet_is_still_caught() -> None:
    """The realistic case, and the one MAD alone misses."""
    pop = {f"a{i}": 0.95 for i in range(9)}
    pop["drifting"] = 0.55
    report = assess(pop)
    assert report.mad == 0.0
    assert report.quarantined == frozenset({"drifting"})
    assert report.verdict_for("drifting").reason == "below_unanimous_median"


def test_a_unanimous_fleet_tolerates_small_deviation() -> None:
    """Otherwise one agent a rounding error below the median gets quarantined."""
    pop = {f"a{i}": 0.95 for i in range(9)}
    pop["jitter"] = 0.93
    assert assess(pop).quarantined == frozenset()


def test_a_small_group_cannot_hide_by_dragging_the_average() -> None:
    """The reason for median rather than mean."""
    pop = {f"good-{i}": 0.95 - i * 0.005 for i in range(8)}
    pop.update({f"bad-{i}": 0.40 for i in range(2)})
    report = assess(pop)

    mean = sum(pop.values()) / len(pop)
    assert mean < 0.85, "the mean has been dragged"
    assert report.median > 0.92, "the median has barely moved"
    assert all(report.verdict_for(f"bad-{i}").quarantined for i in range(2))
    assert not any(report.verdict_for(f"good-{i}").quarantined for i in range(8))


def test_forty_percent_contamination_is_still_caught() -> None:
    """Median and MAD hold as long as the honest agents are a majority."""
    pop = {f"good-{i}": 0.95 - i * 0.005 for i in range(6)}
    pop.update({f"bad-{i}": 0.45 for i in range(4)})
    report = assess(pop)
    assert report.quarantined == frozenset(f"bad-{i}" for i in range(4))


def test_the_limit_is_half_the_population() -> None:
    """Honest limit, and it belongs in the threat model."""
    pop = {f"good-{i}": 0.95 for i in range(5)}
    pop.update({f"bad-{i}": 0.45 for i in range(5)})
    report = assess(pop)
    assert report.quarantined == frozenset(), "outlier detection cannot cover this"


def test_a_small_population_uses_the_floor_only() -> None:
    """Three agents give a MAD built from two points."""
    report = assess({"a": 0.95, "b": 0.94, "c": 0.60})
    assert report.statistics_applied is False
    assert report.quarantined == frozenset(), "0.60 is above the floor"


def test_empty_population_is_not_an_error() -> None:
    report = assess({})
    assert report.population == 0
    assert report.quarantined == frozenset()


def test_verdicts_are_sorted_and_order_independent() -> None:
    a = assess({"z": 0.9, "a": 0.9, "m": 0.9})
    b = assess({"a": 0.9, "m": 0.9, "z": 0.9})
    assert [v.agent_id for v in a.verdicts] == ["a", "m", "z"]
    assert a == b


def test_zero_dispersion_gives_zero_z_not_infinity() -> None:
    assert robust_z(0.5, med=0.9, mad=0.0) == 0.0


def test_quarantine_is_reversible() -> None:
    """It is a function of current reliabilities, with no sticky state."""
    assert assess({**HEALTHY, "recovering": 0.21}).quarantined == frozenset({"recovering"})
    assert assess({**HEALTHY, "recovering": 0.93}).quarantined == frozenset()


@pytest.mark.parametrize(
    "kwargs", [{"z_threshold": 0}, {"quarantine_below": 1.5}, {"min_population": 0}]
)
def test_params_validate(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        OutlierParams(**kwargs)


def test_a_quarantined_attester_loses_its_vote_in_the_quorum_gate() -> None:
    """The two halves of M11 meet here: assess() feeds QuorumGate.quarantined."""
    names = ("verifier", "correlation", "fusion", "orchestrator", "monitoring")
    registry = {n: issue_identity(n, seed=n.encode().ljust(32, b"\0")) for n in names}

    reliabilities = {n: 0.95 for n in names}
    reliabilities["fusion"] = 0.10
    report = assess(reliabilities, OutlierParams(min_population=5))
    assert report.quarantined == frozenset({"fusion"})

    candidate = MemoryCandidate(
        record_id="rec-1",
        pattern_text="p",
        threat_type="device_compromise",
        node_ids=("n-1",),
        window_start_sim=1.0,
        window_end_sim=2.0,
        run_id="r",
        seed=1,
        config_hash="h",
        proposer_id="memory-curator",
    )
    gate = QuorumGate(registry=registry, quarantined=report.quarantined)
    atts = [
        attest(candidate, registry[n], sim_time=10.0) for n in ("verifier", "correlation", "fusion")
    ]
    decision = gate.admit(candidate, atts, now_sim=10.0)

    assert decision.admitted is False, "three signatures, but one does not count"
    assert decision.n == 5, "quarantine must not shrink n"
    assert decision.k == 3, "nor lower k"


@given(
    values=st.lists(st.floats(min_value=0.6, max_value=1.0), min_size=5, max_size=30),
)
def test_property_a_population_with_no_low_agent_quarantines_nobody(
    values: list[float],
) -> None:
    """Everything comfortably above the floor, so only statistics could fire."""
    pop = {f"a{i}": v for i, v in enumerate(values)}
    report = assess(pop)
    assert not report.quarantined


@given(
    base=st.floats(min_value=0.80, max_value=0.99),
    n=st.integers(min_value=5, max_value=20),
)
def test_property_the_lowest_agent_is_never_less_suspicious_than_the_highest(
    base: float, n: int
) -> None:
    pop = {f"a{i}": base for i in range(n)}
    pop["low"] = 0.05
    pop["high"] = 1.0
    report = assess(pop)
    assert report.verdict_for("low").robust_z <= report.verdict_for("high").robust_z
    assert report.verdict_for("low").quarantined is True
    assert report.verdict_for("high").quarantined is False


@given(
    healthy=st.lists(st.floats(min_value=0.4, max_value=1.0), min_size=5, max_size=30),
    low=st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=0, max_size=5),
)
def test_property_quarantine_is_downward_closed(healthy: list[float], low: list[float]) -> None:
    """If an agent is quarantined, every agent less reliable than it is too."""
    pop = {f"h{i}": v for i, v in enumerate(healthy)} | {f"l{i}": v for i, v in enumerate(low)}
    report = assess(pop)
    for q in report.quarantined:
        for other, value in pop.items():
            if value < pop[q]:
                assert other in report.quarantined, (q, pop[q], other, value)
