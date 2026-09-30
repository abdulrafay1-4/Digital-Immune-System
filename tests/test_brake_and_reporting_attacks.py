"""Regression tests: attacks that turn the defence into the outage, or target its statistics."""

from __future__ import annotations

from dataclasses import replace

from m8_eval_harness.baselines import BINARY_ZT, FULL
from m8_eval_harness.params import FROZEN
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios import by_id
from m8_eval_harness.scenarios.base import Anomaly, Scenario

INDUCED = Scenario(
    scenario_id="t-induced",
    name="induced benign congestion",
    demonstrates="",
    n_nodes=100,
    ticks=50,
    anomalies=tuple(
        Anomaly(f"node-{i}", 20.0, 25.0, 0.9, ("network", "device")) for i in range(30)
    ),
    seed=7501,
)


def _executed_restrictions_per_tick(result) -> list[int]:
    return [
        sum(
            1
            for execution in outcome.executions
            if execution.executed and execution.level is not None and execution.level >= 3
        )
        for outcome in result.pipeline.outcomes
    ]


def test_induced_congestion_cannot_restrict_a_third_of_the_fleet_automatically() -> None:
    """Induced congestion on 30% of a fleet is not restricted wholesale with no one asked."""
    result = run_scenario(INDUCED, FULL)
    assert max(_executed_restrictions_per_tick(result)) <= 10
    assert result.pipeline.restrictions_withheld > 0
    assert all(result.worst_level(f"node-{i}") >= 2 for i in range(30))


def test_an_operator_can_confirm_a_mass_restriction_once() -> None:
    result = run_scenario(INDUCED, FULL, operator="approve")
    assert max(_executed_restrictions_per_tick(result)) > 10
    mass_questions = [d for d in result.approval_gate.escalations if d.node_id == "fleet"]
    assert len(mass_questions) == 1, "one question per episode, not per tick"


def test_the_brake_spends_its_budget_on_the_strongest_evidence_first() -> None:
    scenario = replace(
        INDUCED,
        scenario_id="t-induced-mixed",
        anomalies=INDUCED.anomalies + (Anomaly("node-99", 18.0, 40.0, 1.0),),
        ground_truth={"node-99": 18.0},
    )
    result = run_scenario(scenario, FULL)
    restricted = {
        plan.node_id
        for outcome in result.pipeline.outcomes
        for plan, execution in zip(outcome.plans, outcome.executions, strict=True)
        if execution.executed and execution.level is not None and execution.level >= 3
    }
    assert "node-99" in restricted


def test_dark_devices_do_not_spend_the_budget() -> None:
    """r2: crashed devices do not spend the budget a real campaign needs."""
    scenario = by_id("r2")
    result = run_scenario(scenario, FULL)
    down, back = next(iter(scenario.outages.values()))
    withheld_at: dict[float, set[str]] = {}
    for outcome in result.pipeline.outcomes:
        withheld = {
            plan.node_id
            for plan, execution in zip(outcome.plans, outcome.executions, strict=True)
            if plan.proposed_level >= 3
            and execution.executed
            and execution.level is not None
            and int(execution.level) == 2
        }
        if withheld:
            withheld_at[outcome.sim_time] = withheld

    assert all(t >= back for t in withheld_at), "nothing withheld while devices are dark"
    assert not set().union(*withheld_at.values()) & scenario.compromised
    assert result.detected == scenario.compromised


def test_external_baselines_are_not_given_the_brake() -> None:
    pipe = BINARY_ZT.pipeline(bus=None, run_id="t", seed=1, config_hash="h")
    assert pipe.max_auto_restrict_fraction is None


def test_the_frozen_configuration_carries_the_brake_and_the_cap() -> None:
    assert FROZEN.max_auto_restrict_fraction == 0.10 and FROZEN.min_auto_restrict == 5
    assert FROZEN.cohort_baseline_cap == 0.11


def test_degraded_sybils_cannot_hide_a_sub_threshold_campaign() -> None:
    """150 fake devices at 0.5 cannot hide a 40-device sub-threshold campaign."""
    result = run_scenario(by_id("a11"), FULL, binding="tofu")
    assert len(result.detected) >= 36


def test_provisioned_binding_refuses_every_sybil() -> None:
    """Refused for want of a key, before binding is ever consulted."""
    result = run_scenario(by_id("a11"), FULL)
    refused = result.telemetry_rejected + result.orchestrator.unbound_updates
    assert refused >= result.adversary.published > 0
    assert len(result.detected) >= 36


def test_a_monitor_that_withholds_incriminating_ticks_is_caught() -> None:
    """
    A monitor that withholds only incriminating ticks is never silent three ticks in a row, and is
    still caught.
    """
    result = run_scenario(by_id("a12"), FULL)
    assert "node-0" in result.detected


def test_a_single_crash_and_reboot_is_not_intermittent_silence() -> None:
    """One long gap stays with silence escalation, and recovery is not delayed by it."""
    result = run_scenario(by_id("r1"), FULL)
    last = {p.node_id: p.proposed_level for p in result.pipeline.outcomes[-1].plans}
    assert all(last[n] == 0 for n in by_id("r1").outages)


def test_decoys_cannot_spend_the_budget_a_real_attack_needs() -> None:
    """Twenty induced low-GT decoys cannot take the budget from three real attacks."""
    real = {f"node-{i}" for i in range(90, 93)}
    scenario = Scenario(
        scenario_id="t-decoys",
        name="decoys",
        demonstrates="",
        n_nodes=100,
        ticks=50,
        anomalies=tuple(Anomaly(n, 20.0, 40.0, 0.6) for n in sorted(real))
        + tuple(
            Anomaly(f"node-{i}", 18.0, 40.0, 0.95, ("network", "device", "behavioral"))
            for i in range(20)
        ),
        ground_truth={n: 20.0 for n in real},
        seed=7601,
    )
    result = run_scenario(scenario, FULL)
    for outcome in result.pipeline.outcomes:
        for plan, execution in zip(outcome.plans, outcome.executions, strict=True):
            if plan.node_id in real and plan.proposed_level >= 3 and execution.executed:
                assert int(execution.level) >= 3, (outcome.sim_time, plan.node_id)
    assert result.pipeline.restrictions_withheld > 0, "the decoys were still braked"


def test_random_link_loss_does_not_escalate_a_healthy_fleet() -> None:
    """At 30% random loss no healthy device is escalated as erratic."""
    import hashlib

    from m8_eval_harness import scenario_runner as runner
    from shared.bus import InProcBus
    from shared.schemas import TrustUpdate

    class Lossy(InProcBus):
        def publish(self, topic, model):
            if isinstance(model, TrustUpdate):
                digest = hashlib.sha256(f"{model.node_id}:{model.sim_time}".encode()).hexdigest()
                if int(digest[:8], 16) / 0xFFFFFFFF < 0.3:
                    return
            super().publish(topic, model)

    scenario = Scenario(
        scenario_id="t-loss", name="loss", demonstrates="", n_nodes=100, ticks=60, seed=7602
    )
    runner.InProcBus = Lossy
    try:
        result = run_scenario(scenario, FULL)
    finally:
        runner.InProcBus = InProcBus
    assert sum(result.worst_level(f"node-{i}") >= 2 for i in range(100)) <= 2


def test_selective_reporting_is_caught_across_withholding_patterns() -> None:
    """Withholding 1 tick in 4, or 3 in 4, is caught as well."""
    base = by_id("a12")
    for on, period in ((2, 3), (1, 4), (2, 5), (3, 4)):
        scenario = replace(
            base,
            scenario_id=f"t-sel-{on}-{period}",
            anomalies=(Anomaly("node-0", 5.0, 75.0, 0.9, pulse_on=on, pulse_period=period),),
        )
        assert "node-0" in run_scenario(scenario, FULL).detected, (on, period)
