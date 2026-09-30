"""M4 graduated response: level formula boundaries and hysteresis behaviour."""

from __future__ import annotations

import math

import pytest

from m4_response_engine.hysteresis import (
    HysteresisParams,
    LevelHysteresis,
    NodeHysteresisState,
)
from m4_response_engine.levels import (
    LEVEL_DESCRIPTION,
    MAX_LEVEL,
    MIN_LEVEL,
    ResponseLevel,
    level_for_gt,
)


def test_five_distinct_levels() -> None:
    """The contribution is stated as five levels: L0 and L1 must not collapse."""
    assert [int(lv) for lv in ResponseLevel] == [0, 1, 2, 3, 4]
    assert len(set(LEVEL_DESCRIPTION.values())) == 5
    assert MIN_LEVEL is ResponseLevel.NONE
    assert MAX_LEVEL is ResponseLevel.ISOLATE


def test_only_isolation_requires_approval() -> None:
    approving = [lv for lv in ResponseLevel if lv.requires_approval]
    assert approving == [ResponseLevel.ISOLATE]


@pytest.mark.parametrize(
    ("gt", "expected"),
    [
        (1.0, ResponseLevel.NONE),
        (0.95, ResponseLevel.NONE),
        (0.81, ResponseLevel.NONE),
        (0.8, ResponseLevel.MONITOR),
        (0.7, ResponseLevel.MONITOR),
        (0.61, ResponseLevel.MONITOR),
        (0.6, ResponseLevel.REAUTH),
        (0.5, ResponseLevel.REAUTH),
        (0.41, ResponseLevel.REAUTH),
        (0.4, ResponseLevel.RESTRICT),
        (0.3, ResponseLevel.RESTRICT),
        (0.21, ResponseLevel.RESTRICT),
        (0.2, ResponseLevel.ISOLATE),
        (0.1, ResponseLevel.ISOLATE),
        (0.0, ResponseLevel.ISOLATE),
    ],
)
def test_level_boundaries(gt: float, expected: ResponseLevel) -> None:
    assert level_for_gt(gt) is expected


def test_boundary_is_inclusive_from_below() -> None:
    """Each boundary GT belongs to the *higher* level; just above it does not."""
    for boundary, level in [
        (0.8, ResponseLevel.MONITOR),
        (0.6, ResponseLevel.REAUTH),
        (0.4, ResponseLevel.RESTRICT),
        (0.2, ResponseLevel.ISOLATE),
    ]:
        assert level_for_gt(boundary) is level
        assert level_for_gt(boundary + 1e-6) is ResponseLevel(int(level) - 1)


def test_gt_zero_clamps_to_isolate() -> None:
    """The raw formula yields 5 at GT = 0: outside the stated 0..4 range."""
    assert math.floor(5 * (1 - 0.0)) == 5
    assert level_for_gt(0.0) is ResponseLevel.ISOLATE


def test_gt_one_is_no_action() -> None:
    assert level_for_gt(1.0) is ResponseLevel.NONE


@pytest.mark.parametrize("gt", [-0.001, -1.0, 1.001, 2.0, float("nan"), float("inf")])
def test_out_of_range_gt_raises(gt: float) -> None:
    """Out-of-range GT means fusion is broken; clamping it would hide that."""
    with pytest.raises(ValueError):
        level_for_gt(gt)


def test_level_is_monotone_non_increasing_in_gt() -> None:
    levels = [level_for_gt(i / 1000.0) for i in range(1001)]
    assert all(a >= b for a, b in zip(levels, levels[1:], strict=False))
    assert set(levels) == set(ResponseLevel)


def test_defaults_match_config() -> None:
    """configs/default.yaml: response.hysteresis_n: 3."""
    assert HysteresisParams().n == 3


def test_params_reject_unknown_and_invalid() -> None:
    with pytest.raises(ValueError):
        HysteresisParams(hysteresis_n=3)  # type: ignore[call-arg]
    with pytest.raises(ValueError):
        HysteresisParams(n=0)


def test_unseen_node_starts_at_l0() -> None:
    hys = LevelHysteresis()
    assert hys.state("ghost") == NodeHysteresisState()
    assert hys.snapshot() == {}


def test_escalation_is_immediate() -> None:
    hys = LevelHysteresis()
    assert hys.apply("n0", ResponseLevel.RESTRICT) is ResponseLevel.RESTRICT
    assert hys.apply("n0", ResponseLevel.ISOLATE) is ResponseLevel.ISOLATE


def test_multi_step_escalation_does_not_step() -> None:
    """L0 → L4 in one tick lands on L4, not L1."""
    hys = LevelHysteresis()
    assert hys.apply("n0", ResponseLevel.ISOLATE) is ResponseLevel.ISOLATE


def test_de_escalation_waits_for_n_consecutive_ticks() -> None:
    hys = LevelHysteresis(params=HysteresisParams(n=3))
    hys.apply("n0", ResponseLevel.RESTRICT)

    assert hys.apply("n0", ResponseLevel.MONITOR) is ResponseLevel.RESTRICT
    assert hys.apply("n0", ResponseLevel.MONITOR) is ResponseLevel.RESTRICT
    assert hys.apply("n0", ResponseLevel.MONITOR) is ResponseLevel.MONITOR
    assert hys.state("n0") == NodeHysteresisState(effective=ResponseLevel.MONITOR)


def test_de_escalation_run_is_broken_by_a_return_to_the_enforced_level() -> None:
    hys = LevelHysteresis(params=HysteresisParams(n=3))
    hys.apply("n0", ResponseLevel.RESTRICT)
    hys.apply("n0", ResponseLevel.MONITOR)
    hys.apply("n0", ResponseLevel.MONITOR)

    assert hys.apply("n0", ResponseLevel.RESTRICT) is ResponseLevel.RESTRICT
    assert hys.state("n0").stable_ticks == 0

    assert hys.apply("n0", ResponseLevel.MONITOR) is ResponseLevel.RESTRICT
    assert hys.apply("n0", ResponseLevel.MONITOR) is ResponseLevel.RESTRICT
    assert hys.apply("n0", ResponseLevel.MONITOR) is ResponseLevel.MONITOR


def test_changing_the_lower_level_restarts_the_count() -> None:
    """A moving target is not evidence of a stable recovery."""
    hys = LevelHysteresis(params=HysteresisParams(n=3))
    hys.apply("n0", ResponseLevel.ISOLATE)
    hys.apply("n0", ResponseLevel.NONE)
    hys.apply("n0", ResponseLevel.NONE)

    assert hys.apply("n0", ResponseLevel.REAUTH) is ResponseLevel.ISOLATE
    assert hys.state("n0") == NodeHysteresisState(
        effective=ResponseLevel.ISOLATE, pending=ResponseLevel.REAUTH, stable_ticks=1
    )
    assert hys.apply("n0", ResponseLevel.REAUTH) is ResponseLevel.ISOLATE
    assert hys.apply("n0", ResponseLevel.REAUTH) is ResponseLevel.REAUTH


def test_escalation_cancels_a_pending_de_escalation() -> None:
    hys = LevelHysteresis(params=HysteresisParams(n=3))
    hys.apply("n0", ResponseLevel.REAUTH)
    hys.apply("n0", ResponseLevel.NONE)
    hys.apply("n0", ResponseLevel.NONE)

    assert hys.apply("n0", ResponseLevel.ISOLATE) is ResponseLevel.ISOLATE
    assert hys.state("n0").pending is None
    assert hys.state("n0").stable_ticks == 0


def test_oscillation_around_a_boundary_does_not_flap() -> None:
    """The point of the module: GT jittering across 0.6 must not toggle levels."""
    hys = LevelHysteresis(params=HysteresisParams(n=3))
    gts = [0.62, 0.58, 0.62, 0.58, 0.61, 0.59, 0.62, 0.58]

    raw = [level_for_gt(gt) for gt in gts]
    assert len(set(raw)) == 2

    effective = [hys.apply_gt("n0", gt) for gt in gts]
    assert effective == [ResponseLevel.MONITOR] + [ResponseLevel.REAUTH] * 7


def test_sustained_recovery_still_de_escalates() -> None:
    """Damping must not become a latch: a node that really recovers comes back."""
    hys = LevelHysteresis(params=HysteresisParams(n=3))
    hys.apply_gt("n0", 0.1)
    assert hys.state("n0").effective is ResponseLevel.ISOLATE

    seen = [hys.apply_gt("n0", 0.99) for _ in range(5)]
    assert seen[-1] is ResponseLevel.NONE
    assert seen.count(ResponseLevel.ISOLATE) == 2


def test_n_one_disables_damping() -> None:
    hys = LevelHysteresis(params=HysteresisParams(n=1))
    hys.apply("n0", ResponseLevel.RESTRICT)
    assert hys.apply("n0", ResponseLevel.NONE) is ResponseLevel.NONE


def test_per_node_state_is_independent() -> None:
    hys = LevelHysteresis(params=HysteresisParams(n=3))
    hys.apply("noisy", ResponseLevel.ISOLATE)
    for _ in range(2):
        hys.apply("noisy", ResponseLevel.NONE)

    hys.apply("quiet", ResponseLevel.RESTRICT)
    assert hys.apply("quiet", ResponseLevel.MONITOR) is ResponseLevel.RESTRICT
    assert hys.state("noisy").effective is ResponseLevel.ISOLATE
    assert hys.state("noisy").stable_ticks == 2
    assert set(hys.snapshot()) == {"noisy", "quiet"}


def test_snapshot_is_a_copy() -> None:
    hys = LevelHysteresis()
    hys.apply("n0", ResponseLevel.REAUTH)
    snap = hys.snapshot()
    snap.clear()
    assert hys.state("n0").effective is ResponseLevel.REAUTH


def test_reset_clears_one_node_or_all() -> None:
    hys = LevelHysteresis()
    hys.apply("a", ResponseLevel.ISOLATE)
    hys.apply("b", ResponseLevel.RESTRICT)

    hys.reset("a")
    assert hys.state("a") == NodeHysteresisState()
    assert hys.state("b").effective is ResponseLevel.RESTRICT

    hys.reset()
    assert hys.snapshot() == {}


def test_invalid_raw_level_raises() -> None:
    hys = LevelHysteresis()
    with pytest.raises(ValueError):
        hys.apply("n0", 5)
    with pytest.raises(ValueError):
        hys.apply("n0", -1)


def test_deterministic_across_instances() -> None:
    """Same input sequence, same output sequence: no hidden or global state."""
    gts = [0.95, 0.55, 0.15, 0.15, 0.62, 0.58, 0.9, 0.9, 0.9, 0.3, 0.3, 0.3, 0.3]

    def run() -> list[ResponseLevel]:
        hys = LevelHysteresis(params=HysteresisParams(n=3))
        return [hys.apply_gt("n0", gt) for gt in gts]

    first = run()
    assert first == run()
    assert first == run()


def test_interleaved_nodes_match_sequential_runs() -> None:
    """Node order within a tick cannot change any node's result."""
    gts_a = [0.1, 0.9, 0.9, 0.9, 0.9]
    gts_b = [0.9, 0.5, 0.5, 0.1, 0.9]

    solo_a = LevelHysteresis()
    solo_b = LevelHysteresis()
    expected_a = [solo_a.apply_gt("a", gt) for gt in gts_a]
    expected_b = [solo_b.apply_gt("b", gt) for gt in gts_b]

    shared = LevelHysteresis()
    got_a: list[ResponseLevel] = []
    got_b: list[ResponseLevel] = []
    for ga, gb in zip(gts_a, gts_b, strict=True):
        got_b.append(shared.apply_gt("b", gb))
        got_a.append(shared.apply_gt("a", ga))

    assert got_a == expected_a
    assert got_b == expected_b
