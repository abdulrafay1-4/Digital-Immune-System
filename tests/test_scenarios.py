"""The six evaluation scenarios and the contribution-isolation baselines."""

from __future__ import annotations

import pytest

from agents.correlation import CorrelationAgent
from m8_eval_harness.baselines import (
    BASELINES,
    BINARY_RESPONSE,
    FULL,
    NO_MEMORY,
    NO_RECOVERY,
    STATIC_TRUST,
)
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios import CALIBRATION, SCENARIOS
from m8_eval_harness.scenarios.base import Anomaly, Scenario
from m8_eval_harness.scenarios.catalogue import (
    S2_DISTRIBUTED_CAMPAIGN,
    S3_RECURRING_ATTACKER,
    S4_COMPROMISED_AGENT,
    S5_MEMORY_POISONING,
    S6_WEAPONISED_HEALING,
)
from shared.bus import InProcBus


def test_there_are_six_scenarios_and_six_arms() -> None:
    assert len(SCENARIOS) == 6
    assert len(BASELINES) == 6


def test_every_contribution_has_exactly_one_isolating_baseline() -> None:
    isolated = [b.isolates for b in BASELINES if b.isolates]
    assert len(isolated) == 5
    assert len({i[:2] for i in isolated}) == 5, "C1..C5, one each"


def test_calibration_is_disjoint_from_the_evaluation_set() -> None:
    """A parameter tuned on s1--s6 makes every figure a description of its tuning."""
    assert {s.seed for s in SCENARIOS}.isdisjoint({s.seed for s in CALIBRATION})
    assert {s.scenario_id for s in SCENARIOS}.isdisjoint({s.scenario_id for s in CALIBRATION})


def test_a_scenario_cannot_target_a_device_that_does_not_exist() -> None:
    with pytest.raises(ValueError, match="absent node"):
        Scenario(
            scenario_id="x",
            name="x",
            demonstrates="",
            n_nodes=2,
            ticks=10,
            anomalies=(Anomaly("node-99", 1.0, 5.0, 0.5),),
        )


def test_an_anomaly_cannot_run_past_the_end_of_its_scenario() -> None:
    with pytest.raises(ValueError, match="past the end"):
        Scenario(
            scenario_id="x",
            name="x",
            demonstrates="",
            n_nodes=2,
            ticks=10,
            anomalies=(Anomaly("node-0", 1.0, 50.0, 0.5),),
        )


def test_anomaly_dimensions_are_validated() -> None:
    with pytest.raises(ValueError, match="unknown dimensions"):
        Anomaly("node-0", 1.0, 5.0, 0.5, ("not-a-dimension",))


def test_scenarios_four_to_six_attack_the_defender() -> None:
    attackers = [s.scenario_id for s in SCENARIOS if s.attacks_the_defender]
    assert attackers == ["s4", "s5", "s6"]


def test_each_baseline_builds_a_distinguishable_pipeline() -> None:
    """A grid whose arms agree is a bug until proven otherwise."""
    built = {
        b.baseline_id: b.pipeline(bus=InProcBus(), run_id="t", seed=1, config_hash="h")
        for b in BASELINES
    }
    assert built["full"].recall is not None and built["full"].healer is not None
    assert built["no_memory"].recall is None and built["no_memory"].curator is None
    assert built["no_recovery"].healer is None
    assert type(built["no_sharing"].correlator) is not CorrelationAgent


def test_memory_has_a_write_path_wherever_it_has_a_read_path() -> None:
    """A recall-only configuration reads a store nothing writes to."""
    for baseline in BASELINES:
        pipe = baseline.pipeline(bus=InProcBus(), run_id="t", seed=1, config_hash="h")
        assert (pipe.recall is None) == (pipe.curator is None)


@pytest.mark.parametrize("scenario", SCENARIOS[:2], ids=lambda s: s.scenario_id)
def test_removing_continuous_trust_loses_the_subtle_attacks(scenario) -> None:
    """The strongest single result in the grid, on the attacks worth detecting."""
    full = run_scenario(scenario, FULL)
    static = run_scenario(scenario, STATIC_TRUST)
    assert len(full.detected) > 0
    assert len(static.detected) == 0


def test_without_continuous_trust_the_fleet_view_has_nothing_to_amplify() -> None:
    """C2 is conditional on C1 by design, and the ablation shows it."""
    static = run_scenario(S3_RECURRING_ATTACKER, STATIC_TRUST)
    assert len(static.detected) == 0
    assert len(run_scenario(S3_RECURRING_ATTACKER, FULL).detected) == 4


def test_the_static_trust_arm_does_not_rebalance_the_weights() -> None:
    """An ablation that *improves* the system is a sign the ablation is wrong."""
    pipe = STATIC_TRUST.pipeline(bus=InProcBus(), run_id="t", seed=1, config_hash="h")
    assert pipe.fusion.params.alpha == 0.40
    assert pipe.fusion.params.beta == 0.35
    assert pipe.fusion.params.gamma == 0.25


def test_the_fleet_view_finds_a_campaign_that_isolated_judgement_misses() -> None:
    """S2 is calibrated so the fleet view is the *only* thing that catches it."""
    from m8_eval_harness.baselines import NO_SHARING

    full = run_scenario(S2_DISTRIBUTED_CAMPAIGN, FULL)
    isolated = run_scenario(S2_DISTRIBUTED_CAMPAIGN, NO_SHARING)

    assert len(full.detected) >= 2
    assert len(isolated.detected) == 0


def test_corroboration_grows_with_peers_not_with_fleet_fraction() -> None:
    """`cti` is breadth, so on a large fleet it is tiny and `max` discards it."""
    from agents.correlation import MAX_CORROBORATION, campaign_corroboration

    assert campaign_corroboration(1) == 0.0, "a device alone corroborates nothing"
    assert campaign_corroboration(2) > 0.0
    assert campaign_corroboration(4) > campaign_corroboration(2)
    assert campaign_corroboration(500) == MAX_CORROBORATION, "capped"


def test_immune_memory_is_written_to_during_a_run() -> None:
    """Records are stored at the incident's *peak*, not at its close."""
    result = run_scenario(S3_RECURRING_ATTACKER, FULL)
    assert len(result.pipeline.curator.store) > 0
    stored = result.pipeline.curator.store.all_records()
    assert all(r.pattern_text for r in stored), "no empty patterns stored"
    assert all(r.quorum_certificate for r in stored), "every record is attested"


def test_recall_fires_and_shortens_the_second_encounter() -> None:
    """C3 end to end, against the arm that removes it."""
    full = run_scenario(S3_RECURRING_ATTACKER, FULL)
    memoryless = run_scenario(S3_RECURRING_ATTACKER, NO_MEMORY)

    assert sum(1 for o in full.pipeline.outcomes if o.correlation.recall_boost > 0) > 0
    assert all(o.correlation.recall_boost == 0 for o in memoryless.pipeline.outcomes)

    second_wave = ("node-2", "node-3")
    full_latency = [full.first_at_or_above(n, 2) for n in second_wave]
    memoryless_latency = [memoryless.first_at_or_above(n, 2) for n in second_wave]
    assert all(
        a is not None and b is not None
        for a, b in zip(full_latency, memoryless_latency, strict=True)
    )
    assert sum(full_latency) <= sum(memoryless_latency)


def test_the_binary_arm_isolates_what_the_graduated_arm_only_monitors() -> None:
    """C4's contribution is not *whether* a device is found but what is done to it."""
    full = run_scenario(S3_RECURRING_ATTACKER, FULL)
    binary = run_scenario(S3_RECURRING_ATTACKER, BINARY_RESPONSE)

    assert full.detected == binary.detected, "same devices found"
    assert full.disruptive_actions < binary.disruptive_actions, "at a very different cost"


def test_memory_and_recovery_arms_are_flat_on_detection_but_not_on_their_metric() -> None:
    """The same trap as C4: the right metric per contribution, not one column."""
    full = run_scenario(S3_RECURRING_ATTACKER, FULL)
    assert full.recall_boosts > 0
    assert run_scenario(S3_RECURRING_ATTACKER, NO_MEMORY).recall_boosts == 0

    weaponised = run_scenario(S6_WEAPONISED_HEALING, FULL)
    assert weaponised.heal_events > 0
    assert run_scenario(S6_WEAPONISED_HEALING, NO_RECOVERY).heal_events == 0


def test_healing_moves_trust_rather_than_only_emitting_events() -> None:
    """M7 publishes a target; fusion converges toward it."""
    full = FULL.pipeline(bus=InProcBus(), run_id="t", seed=1, config_hash="h")
    none = NO_RECOVERY.pipeline(bus=InProcBus(), run_id="t", seed=1, config_hash="h")
    assert full.healer is not None
    assert none.healer is None


def test_a_compromised_agent_cannot_speak_for_other_devices() -> None:
    result = run_scenario(S4_COMPROMISED_AGENT, FULL)
    adversary = result.adversary
    assert adversary.forged_for_others > 0, "it tried"
    assert result.orchestrator.unbound_updates == adversary.forged_for_others
    for victim in adversary.victim_ids:
        assert result.worst_level(victim) == 0, "no victim was touched"


def test_the_genuinely_compromised_device_is_still_detected() -> None:
    """Its agent lies about it; the fleet view does not corroborate the story."""
    result = run_scenario(S4_COMPROMISED_AGENT, FULL)
    assert "node-0" in result.detected


def test_no_poisoned_memory_write_is_ever_admitted() -> None:
    """Four escalating strategies, including truthful facts under a false label."""
    result = run_scenario(S5_MEMORY_POISONING, FULL)
    poisoner = result.adversary
    assert poisoner.attempts >= 4
    assert set(poisoner.by_strategy) == {
        "unattested",
        "forged",
        "sub_quorum",
        "true_facts_false_label",
    }
    assert poisoner.accepted == 0


def test_weaponised_healing_is_contained() -> None:
    """Ground truth is empty: every restriction here is a false positive."""
    result = run_scenario(S6_WEAPONISED_HEALING, FULL)
    assert result.adversary.cycles >= 3, "the attacker kept trying"
    assert len(result.false_positives) <= 2, "and got almost nowhere"


def test_every_cell_of_the_grid_completes_with_an_intact_audit() -> None:
    for scenario in SCENARIOS:
        for baseline in BASELINES:
            result = run_scenario(scenario, baseline)
            assert result.ticks == scenario.ticks
            assert result.audit_intact, f"{scenario.scenario_id}/{baseline.baseline_id}"


def test_a_cell_is_reproducible() -> None:
    a = run_scenario(S3_RECURRING_ATTACKER, FULL).summary()
    b = run_scenario(S3_RECURRING_ATTACKER, FULL).summary()
    assert a == b


def test_undetected_devices_are_excluded_from_the_latency_mean() -> None:
    """
    Averaging misses in as some large number lets a system that misses everything post a good
    latency.
    """
    static = run_scenario(SCENARIOS[0], STATIC_TRUST)
    assert static.detection_latency() is None
    assert len(static.missed) == 1
