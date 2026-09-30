"""The C4 comparator: belief recursion, nested thresholds, one-way stops."""

from __future__ import annotations

import pytest

from m8_eval_harness.baselines.base import StoppingPolicy

HEALTHY = (0.0,) * 8 + (0.2, 0.8)
INTRUDED = (0.1, 0.3, 0.3, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0)


def policy(thresholds=(0.9, 0.8, 0.7)) -> StoppingPolicy:
    return StoppingPolicy(
        thresholds=thresholds,
        f_healthy=HEALTHY,
        f_intruded=INTRUDED,
        intrusion_rate=0.01,
    )


def test_thresholds_must_be_nested_in_stops_remaining():
    """Theorem 1.A: with more stops in hand, stop no later than with fewer."""
    with pytest.raises(ValueError, match="nested"):
        policy(thresholds=(0.7, 0.8, 0.9))


def test_a_degraded_observation_raises_the_belief_and_a_clean_one_lowers_it():
    p = policy()
    assert p.update(0.5, observation=0.25) > 0.5
    assert p.update(0.5, observation=0.95) < 0.5


def test_the_belief_is_monotone_in_the_observation():
    p = policy()
    beliefs = [p.update(0.5, observation=o) for o in (0.95, 0.85, 0.55, 0.25, 0.05)]
    assert beliefs == sorted(beliefs), beliefs


def test_no_stop_below_the_threshold_and_one_stop_per_tick():
    p = policy(thresholds=(0.9, 0.8, 0.7))
    assert p.stops_after(belief=0.69, stops_used=0) == 0
    assert p.stops_after(belief=0.99, stops_used=0) == 1
    assert p.stops_after(belief=0.99, stops_used=1) == 2


def test_later_stops_need_a_stronger_belief():
    p = policy(thresholds=(0.9, 0.8, 0.7))
    assert p.stops_after(belief=0.75, stops_used=0) == 1
    assert p.stops_after(belief=0.75, stops_used=1) == 1
    assert p.stops_after(belief=0.85, stops_used=1) == 2


def test_stops_are_irreversible_as_published_unless_release_is_asked_for():
    published = policy()
    assert published.stops_after(belief=0.0, stops_used=2) == 2
    releasing = StoppingPolicy(
        thresholds=(0.9, 0.8, 0.7),
        f_healthy=HEALTHY,
        f_intruded=INTRUDED,
        intrusion_rate=0.01,
        release=True,
    )
    assert releasing.stops_after(belief=0.0, stops_used=2) == 1


def test_stops_stop_at_three():
    p = policy()
    assert p.stops_after(belief=1.0, stops_used=3) == 3


def test_the_arm_swaps_only_the_response_rule(tmp_path):
    """C1, C2, C3 and C5 stay on: a difference is a difference in the rule."""
    from m8_eval_harness.baselines.base import _StoppingResponseEngine, stopping_response
    from shared.bus import InProcBus

    pipeline = stopping_response(policy()).pipeline(
        bus=InProcBus(), run_id="r", seed=1, config_hash="h"
    )
    assert isinstance(pipeline.engine, _StoppingResponseEngine)
    assert pipeline.curator is not None, "immune memory (C3) must still be on"
    assert pipeline.healer is not None, "self-healing (C5) must still be on"


def test_the_arm_detects_an_attacked_device_and_leaves_a_quiet_fleet_alone(tmp_path):
    from m8_eval_harness.baselines.base import stopping_response
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios import by_id

    fitted = StoppingPolicy.load()
    arm = stopping_response(fitted)

    attacked = evaluate(run_scenario(by_id("s1"), arm, seed=20000, results_dir=tmp_path / "s1"))
    assert attacked["device_tpr"] == 1.0

    quiet = evaluate(run_scenario(by_id("cal-1"), arm, seed=20000, results_dir=tmp_path / "q"))
    assert quiet["false_restriction_rate"] == 0.0

    glitch = evaluate(run_scenario(by_id("r3"), arm, seed=20000, results_dir=tmp_path / "g"))
    assert glitch["benign_worst_level"] >= 2
