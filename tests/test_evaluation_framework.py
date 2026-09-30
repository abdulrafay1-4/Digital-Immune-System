"""The evaluation framework: seeds, parameters, arms, metrics, statistics, scenarios."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from m8_eval_harness import stats
from m8_eval_harness.baselines import (
    ALL_BASELINES,
    BETA_REPUTATION,
    BINARY_RESPONSE,
    BINARY_ZT,
    FULL,
    ISOLATION_FOREST,
    NO_MEMORY,
    NO_RECOVERY,
    NO_SHARING,
    STATIC_NO_SHARING,
    STATIC_TRUST,
    by_id,
)
from m8_eval_harness.calibrate import CALIBRATION_IDS, candidates
from m8_eval_harness.evaluation import evaluate
from m8_eval_harness.experiment import (
    HELD_OUT_SEEDS,
    Cell,
    resolve_scenario,
    run_cells,
    suite_cells,
)
from m8_eval_harness.params import FROZEN, SystemParams
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios import (
    ADAPTIVE,
    CALIBRATION,
    RESILIENCE,
    SCENARIOS,
)
from m8_eval_harness.scenarios import (
    by_id as scenario,
)
from m8_eval_harness.scenarios.base import Anomaly, Scenario
from m8_eval_harness.simulator import DEFAULT_CONFIG
from shared.run_manifest import config_hash, load_yaml_config

SHORT = Scenario(
    scenario_id="t-short",
    name="short",
    demonstrates="",
    n_nodes=20,
    ticks=30,
    anomalies=(Anomaly("node-0", 5.0, 20.0, 0.8), Anomaly("node-1", 6.0, 20.0, 0.8)),
    ground_truth={"node-0": 5.0, "node-1": 6.0},
    seed=7301,
)


def test_every_seed_set_is_disjoint() -> None:
    """Calibration, evaluation, resilience, adaptive and held-out seeds never meet."""
    sets = {
        "evaluation": {s.seed for s in SCENARIOS},
        "calibration": {s.seed + r for s in CALIBRATION for r in range(3)},
        "resilience": {s.seed for s in RESILIENCE},
        "adaptive": {s.seed for s in ADAPTIVE},
        "held_out": set(HELD_OUT_SEEDS),
    }
    names = list(sets)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            assert sets[a].isdisjoint(sets[b]), (a, b)


def test_calibration_uses_only_calibration_scenarios() -> None:
    assert set(CALIBRATION_IDS) <= {s.scenario_id for s in CALIBRATION}
    assert len(candidates()) == 96


def test_coefficients_reach_the_config_hash() -> None:
    base = load_yaml_config(DEFAULT_CONFIG)
    a = config_hash(FROZEN.apply_to_config(base))
    b = config_hash(replace(FROZEN, trust_lambda_up=0.85).apply_to_config(base))
    assert a != b


def test_every_arm_takes_the_same_coefficients() -> None:
    params = SystemParams(
        trust_lambda=0.6, trust_lambda_up=0.85, cohort_margin=0.15, rep_lam_up=0.9
    )
    for baseline in (
        FULL,
        STATIC_TRUST,
        NO_SHARING,
        NO_MEMORY,
        BINARY_RESPONSE,
        NO_RECOVERY,
        BETA_REPUTATION,
    ):
        pipe = baseline.pipeline(bus=_bus(), run_id="t", seed=1, config_hash="h", params=params)
        assert pipe.fusion.params.trust_lambda == 0.6, baseline.baseline_id
        assert pipe.fusion.reputation.params.lam_up == 0.9, baseline.baseline_id
        assert pipe.verifier.correlator.params.cohort_margin == 0.15, baseline.baseline_id


def _bus():
    from shared.bus import InProcBus

    return InProcBus()


def test_static_trust_never_moves_fused_trust() -> None:
    result = run_scenario(SHORT, STATIC_TRUST)
    assert {u.ts for o in result.pipeline.outcomes for u in o.gt_updates} == {1.0}


def test_no_sharing_has_no_fleet_view_at_all() -> None:
    result = run_scenario(SHORT, NO_SHARING)
    for outcome in result.pipeline.outcomes:
        assert outcome.correlation.cti == 0.0
        assert outcome.correlation.implicated_node_ids == []
        assert outcome.correlation.campaign_corroboration == 0.0


def test_no_memory_never_stores_or_recalls() -> None:
    result = run_scenario(scenario("s3"), NO_MEMORY)
    assert result.pipeline.curator is None and result.recall_boosts == 0


def test_no_recovery_never_heals() -> None:
    assert run_scenario(scenario("s6"), NO_RECOVERY).heal_events == 0


def test_binary_arms_only_ever_allow_or_block() -> None:
    for baseline in (BINARY_RESPONSE, BINARY_ZT, ISOLATION_FOREST):
        result = run_scenario(SHORT, baseline)
        levels = {p.proposed_level for o in result.pipeline.outcomes for p in o.plans}
        assert levels <= {0, 4}, baseline.baseline_id
        assert result.disruptive_actions > 0, baseline.baseline_id


def test_binary_zero_trust_keeps_nothing_between_reports() -> None:
    result = run_scenario(SHORT, BINARY_ZT)
    assert result.pipeline.recall is None and result.pipeline.healer is None
    assert all(o.correlation.implicated_node_ids == [] for o in result.pipeline.outcomes)


def test_binary_zero_trust_gives_no_response_to_low_and_slow() -> None:
    """The proposal's acceptance criterion describes the baseline this way."""
    result = run_scenario(scenario("s1"), BINARY_ZT)
    assert result.detected == frozenset()


def test_the_full_system_keeps_every_mechanism_acting() -> None:
    assert run_scenario(scenario("s3"), FULL).recall_boosts > 0
    assert run_scenario(scenario("s6"), FULL).heal_events > 0
    assert run_scenario(SHORT, FULL).disruptive_actions > 0


def test_beta_reputation_replaces_the_trust_model_only() -> None:
    pipe = BETA_REPUTATION.pipeline(bus=_bus(), run_id="t", seed=1, config_hash="h")
    assert pipe.fusion.params.step_check is False
    assert pipe.recall is not None and pipe.healer is not None
    assert "node-0" in run_scenario(SHORT, BETA_REPUTATION).detected


def test_the_factorial_cell_removes_both() -> None:
    result = run_scenario(SHORT, STATIC_NO_SHARING)
    assert {u.ts for o in result.pipeline.outcomes for u in o.gt_updates} == {1.0}
    assert all(o.correlation.implicated_node_ids == [] for o in result.pipeline.outcomes)


def test_parameterised_arms_resolve_by_id() -> None:
    assert by_id("binary_zt@0.7").baseline_id == "binary_zt@0.7"
    assert by_id("isolation_forest@0.05").baseline_id == "isolation_forest@0.05"
    assert len({b.baseline_id for b in ALL_BASELINES}) == len(ALL_BASELINES)


def test_metrics_on_a_clean_detection() -> None:
    row = evaluate(run_scenario(SHORT, FULL))
    assert row["device_tpr"] == 1.0 and row["device_fpr"] == 0.0
    assert row["latency_response_mean"] is not None and row["latency_response_mean"] >= 0
    assert 0.0 < row["response_coverage"] <= 1.0
    assert row["audit_intact"] is True
    assert row["tick_ms_p50"] is not None


def test_misses_are_excluded_from_latency_and_counted() -> None:
    row = evaluate(run_scenario(scenario("s1"), STATIC_TRUST))
    assert row["device_tpr"] == 0.0
    assert row["latency_response_mean"] is None
    assert row["detected_devices"] == 0


def test_recovery_is_measured_after_the_attack_ends() -> None:
    row = evaluate(run_scenario(scenario("cal-11"), FULL))
    assert row["mttr_mean"] is not None and row["mttr_mean"] >= 0
    assert row["unrecovered_devices"] == 0


def test_benign_devices_are_measured_separately() -> None:
    row = evaluate(run_scenario(scenario("r4"), FULL))
    assert row["benign_devices"] == 1 and row["tp"] == 0
    assert row["benign_unrecovered"] == 0


def test_pulse_attack_ticks_are_counted_exactly() -> None:
    pulsed = Anomaly("node-0", 5.0, 20.0, 0.6, pulse_on=1, pulse_period=3)
    s = Scenario(
        scenario_id="t-p",
        name="p",
        demonstrates="",
        n_nodes=5,
        ticks=25,
        anomalies=(pulsed,),
        ground_truth={"node-0": 5.0},
        seed=7302,
    )
    assert s.attack_ticks("node-0") == frozenset({5, 8, 11, 14, 17})


def test_holm_is_monotone_and_capped() -> None:
    adjusted = stats.holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.5})
    assert adjusted["a"] == pytest.approx(0.04)
    assert adjusted["c"] >= adjusted["a"] and adjusted["b"] >= adjusted["c"]
    assert max(adjusted.values()) <= 1.0


def test_identical_samples_carry_no_evidence() -> None:
    assert stats.wilcoxon_p([1, 2, 3], [1, 2, 3]) == 1.0
    assert stats.rank_biserial([1, 2, 3], [1, 2, 3]) == 0.0


def test_a_consistent_improvement_is_detected_with_the_right_sign() -> None:
    rng = np.random.default_rng(0)
    b = rng.normal(0, 1, 30)
    a = b + 1.0
    comparison = stats.compare("x", "a", list(a), "b", list(b))
    assert comparison.p_value < 0.001
    assert comparison.effect_size == pytest.approx(1.0)
    assert comparison.difference.low > 0.9


def test_paired_samples_ignore_missing_pairs() -> None:
    assert list(stats.paired_differences([1.0, None, 3.0], [0.0, 1.0, None])) == [1.0]


def test_noise_models_are_deterministic_and_gaussian_is_unchanged() -> None:
    from m1_monitoring.sensors.synthetic import NoiseModel, SyntheticTelemetry

    default = SyntheticTelemetry(5).read(3.0, "node-1")[0]
    explicit = SyntheticTelemetry(5, noise_model=NoiseModel()).read(3.0, "node-1")[0]
    assert default == explicit
    for kind in ("heavy_tail", "diurnal", "correlated"):
        a = SyntheticTelemetry(5, noise_model=NoiseModel(kind=kind)).read(3.0, "node-1")[0]
        b = SyntheticTelemetry(5, noise_model=NoiseModel(kind=kind)).read(3.0, "node-1")[0]
        assert a == b


def test_each_run_gets_its_own_adversary() -> None:
    """A shared adversary installed itself once and did nothing afterwards."""
    first = run_scenario(scenario("a5"), FULL)
    second = run_scenario(scenario("a5"), FULL)
    assert first.adversary.lies > 0 and second.adversary.lies == first.adversary.lies
    assert scenario("a5").adversary.lies == 0


@pytest.mark.parametrize("scenario_id", [s.scenario_id for s in ADAPTIVE])
def test_every_adaptive_scenario_runs_with_an_intact_audit(scenario_id) -> None:
    result = run_scenario(scenario(scenario_id), FULL)
    assert result.ticks == scenario(scenario_id).ticks
    assert result.audit_intact
    assert result.orchestrator.pipeline_failures == 0


def test_the_quick_suite_produces_complete_rows() -> None:
    rows = run_cells(suite_cells("quick", HELD_OUT_SEEDS[:1]))
    assert {r["baseline_id"] for r in rows} == {"full", "binary_zt"}
    assert all("device_f1" in r and "variant" in r for r in rows)


def test_sweep_scenarios_resolve() -> None:
    assert resolve_scenario("sweep:duty:1:3:0.60").anomalies[0].pulse_period == 3
    assert resolve_scenario("sweep:scale:500").n_nodes == 500
    assert Cell("s1", "full", 1).variant() == "op=absent|adj=oracle|noise=gaussian"


def test_the_default_config_is_the_frozen_configuration() -> None:
    """The YAML the simulator reads and the coefficients the evaluation uses cannot drift."""
    cfg = load_yaml_config(DEFAULT_CONFIG)
    assert config_hash(FROZEN.apply_to_config(cfg)) == config_hash(cfg)


def test_the_frozen_configuration_is_the_calibrated_one() -> None:
    assert FROZEN.cohort_margin == 0.15
    assert FROZEN.rep_lam_up == 0.85
    assert FROZEN.trust_lambda == 0.7 and FROZEN.trust_lambda_up is None


def test_the_correction_family_is_one_arm_and_one_metric():
    """A wide family erases a comparator's win; the family is the table row."""
    from m8_eval_harness.experiment import compare_rows

    def rows(scenarios, arms, metrics):
        out = []
        for name in scenarios:
            for arm in arms:
                for seed in range(30):
                    row = {"scenario_id": name, "variant": "v", "baseline_id": arm, "seed": seed}
                    row.update({m: (0.2 if arm == "full" else 0.9) for m in metrics})
                    out.append(row)
        return out

    narrow = compare_rows(rows(["s1"], ["full", "other"], ["device_tpr"]))
    scenarios = [f"s{i}" for i in range(6)]
    metrics = ["device_tpr", "response_coverage"]
    wide = compare_rows(rows(scenarios, ["full", "a", "b", "c"], metrics))
    assert len(narrow) == 1 and len(wide) == 36
    assert narrow[0].p_adjusted == pytest.approx(narrow[0].p_value), "a family of one"
    for c in wide:
        assert c.p_adjusted == pytest.approx(min(1.0, 6 * c.p_value)), c.metric


def test_vargha_delaney_a_reads_as_a_probability() -> None:
    from m8_eval_harness.stats import vargha_delaney_a

    assert vargha_delaney_a([4, 5], [1, 2]) == 1.0, "every a beats every b"
    assert vargha_delaney_a([1, 2], [4, 5]) == 0.0
    assert vargha_delaney_a([1, 2, 3], [1, 2, 3]) == 0.5, "identical samples: no effect"
    assert vargha_delaney_a([1, None, 3], [2]) == 0.5, "missing values are dropped"
    assert vargha_delaney_a([], [1]) is None
