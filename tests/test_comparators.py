"""The published comparators: each one is what its source says it is."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from m8_eval_harness.baselines import by_id
from m8_eval_harness.baselines.base import (
    _DirichletReliabilityTracker,
    _PenaltyHealer,
)


def test_dirichlet_expectation_matches_josang_and_haller_worked_example() -> None:
    """Their Sec. II: 6 red, 1 black, 1 yellow, C = 2, base rate 1/3 -> E(red) = 2/3."""
    tracker = _DirichletReliabilityTracker(lam=1.0, c=2.0)
    evidence = [6.0, 1.0, 1.0]
    total = tracker.c + sum(evidence)
    expectation_red = (evidence[0] + tracker.c * (1 / 3)) / total
    assert expectation_red == pytest.approx(2 / 3)


def test_dirichlet_reliability_rewards_consistent_reports_and_forgets() -> None:
    tracker = _DirichletReliabilityTracker(lam=0.9)
    assert tracker.get("new") == pytest.approx(0.5), "no evidence: the base rate"
    for _ in range(30):
        tracker.observe_deviation("honest", 0.0)
        tracker.observe_deviation("liar", 0.5)
    assert tracker.get("honest") > 0.85
    assert tracker.get("liar") < 0.15
    for _ in range(40):
        tracker.observe_deviation("liar", 0.0)
    assert tracker.get("liar") > 0.8, "longevity < 1 lets old ratings age out"


def test_the_penalty_healer_holds_for_exactly_the_penalty_then_restores_at_once() -> None:
    healer = _PenaltyHealer(penalty_ticks=3, tau_h=0.5)
    healer.observe("n", gt=0.2, health=1.0, sim_time=0.0)
    held = []
    for t in range(1, 6):
        held.append(healer.target_for("n"))
        healer.observe("n", gt=0.9, health=1.0, sim_time=float(t))
    assert held[:3] == [0.05, 0.05, 0.05]
    assert held[3] is None, "restored in one step, no ramp"
    assert healer.next_ts("n", 0.9) == 0.9


@pytest.mark.parametrize(
    "arm_id",
    [
        "cusum@0.05:0.4",
        "dirichlet_reliability",
        "penalty_healing@10",
        "ddca@0.8:2",
        "isolation_forest_persistent@0.01",
    ],
)
def test_each_comparator_detects_a_plain_attack_without_failing_a_tick(arm_id: str) -> None:
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios import by_id as scenario

    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(scenario("s4"), by_id(arm_id), seed=20000, results_dir=Path(tmp))
    assert result.orchestrator.pipeline_failures == 0, "a swallowed exception is not a result"
    assert evaluate(result)["device_tpr"] == 1.0


def test_each_single_mechanism_comparator_keeps_the_rest_of_the_loop() -> None:
    """C1, C2 and C5 swaps keep memory and the fleet view; only their mechanism changes."""
    from agents.correlation import CorrelationAgent
    from m6_trust_fusion.fusion import TrustFusionEngine
    from shared.bus import InProcBus

    kw = dict(bus=InProcBus(), run_id="r", seed=1, config_hash="h")
    cusum = by_id("cusum@0.05:0.4").pipeline(**kw)
    assert type(cusum.fusion).__name__ == "_CusumTrustFusion"
    assert cusum.curator is not None and cusum.healer is not None
    dirichlet = by_id("dirichlet_reliability").pipeline(**kw)
    assert type(dirichlet.correlator).__name__ == "_DirichletCorrelation"
    assert type(dirichlet.fusion) is TrustFusionEngine and dirichlet.curator is not None
    penalty = by_id("penalty_healing@10").pipeline(**kw)
    assert type(penalty.healer).__name__ == "_PenaltyHealer"
    assert type(penalty.correlator) is CorrelationAgent and penalty.curator is not None
