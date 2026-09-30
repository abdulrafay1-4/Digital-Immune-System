"""Crashes, benign anomalies, and the attacks found probing them."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import patch

import pytest

from agents.correlation import CorrelationAgent
from agents.orchestrator import TRUST_TOPIC, Orchestrator
from agents.verifier import VerifierAgent
from m1_monitoring.agent import MonitoringAgent
from m1_monitoring.core.trust import TrustState
from m5_immune_memory import MemoryQuery
from m6_trust_fusion import TrustFusionEngine
from m8_eval_harness.baselines import FULL, NO_MEMORY
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios import RESILIENCE, by_id
from m8_eval_harness.scenarios.adversaries import _update
from m8_eval_harness.scenarios.base import Anomaly, Scenario
from m8_eval_harness.scenarios.catalogue import S3_RECURRING_ATTACKER
from m8_eval_harness.simulator import run_trust_sim
from shared.bus import InProcBus


def _last_level(result, node_id: str) -> int:
    return next(
        p.proposed_level for p in result.pipeline.outcomes[-1].plans if p.node_id == node_id
    )


def test_a_crashing_subscriber_does_not_stop_the_immune_system(tmp_path) -> None:
    """
    A crashing subscriber (a closed dashboard socket) must not unwind into a monitoring agent's
    tick.
    """
    from m8_eval_harness.simulator import DEFAULT_CONFIG
    from shared.run_manifest import config_hash, load_yaml_config

    real_hash = config_hash(load_yaml_config(DEFAULT_CONFIG))
    bus = InProcBus()
    pipe = FULL.pipeline(bus=bus, run_id="s", seed=1, config_hash=real_hash)
    Orchestrator(bus=bus, run_id="s", seed=1, config_hash=real_hash, pipeline=pipe).attach()

    def dashboard(model) -> None:
        if getattr(model, "sim_time", None) == 10.0:
            raise ConnectionResetError("socket closed")

    bus.subscribe(TRUST_TOPIC, dashboard)
    run_trust_sim(
        seed=1, n_nodes=10, ticks=20, run_id="s", anomalies={}, results_dir=tmp_path, bus=bus
    )

    assert len(pipe.outcomes) == 19, "every sealed tick ran"
    assert bus.handler_errors == 10, "one per device at t=10, counted"


def _flaky(cls, name, when):
    original = getattr(cls, name)

    def wrapper(self, *args, **kwargs):
        if 10 <= when(args, kwargs) < 14:
            raise RuntimeError(f"{name} crashed")
        return original(self, *args, **kwargs)

    return patch.object(cls, name, wrapper)


@pytest.mark.parametrize(
    ("cls", "name", "when"),
    [
        (CorrelationAgent, "correlate", lambda a, k: a[0].sim_time),
        (TrustFusionEngine, "fuse_batch", lambda a, k: a[0][0].sim_time),
        (VerifierAgent, "audit", lambda a, k: k["plans"][0].sim_time),
    ],
    ids=["correlation", "fusion", "verifier"],
)
def test_a_crashing_critical_stage_costs_ticks_not_the_loop(cls, name, when) -> None:
    """A crashing stage costs only the ticks it crashed on."""
    with _flaky(cls, name, when):
        result = run_scenario(S3_RECURRING_ATTACKER, FULL)

    assert result.orchestrator.pipeline_failures == 4
    assert result.ticks == S3_RECURRING_ATTACKER.ticks - 4
    assert result.detected == S3_RECURRING_ATTACKER.compromised, "detection resumed"
    assert result.audit_intact


def test_broken_immune_memory_degrades_to_memoryless() -> None:
    """Memory is an enrichment."""

    def broken(self, pattern_text):
        raise OSError("index unreadable")

    with patch.object(MemoryQuery, "recognise", broken):
        result = run_scenario(S3_RECURRING_ATTACKER, FULL)

    assert result.orchestrator.pipeline_failures == 0
    assert result.ticks == S3_RECURRING_ATTACKER.ticks
    assert result.pipeline.degraded["recall"] > 0
    assert result.detected == S3_RECURRING_ATTACKER.compromised


@dataclass
class _Futurist:
    """One bound agent, reporting only for its own device, half a tick early."""

    name: str = "futurist"
    sent: int = 0

    def before_tick(self, run, sim_time: float) -> None:
        if sim_time != int(sim_time):
            return
        run.as_agent("mon-node-0").publish(
            TRUST_TOPIC,
            _update(
                node_id="node-0", agent_id="mon-node-0", level=0.9, sim_time=sim_time + 0.5, run=run
            ),
        )
        self.sent += 1

    def after_tick(self, run, sim_time, outcome) -> None:
        return None


def test_a_future_dated_report_cannot_seal_the_fleet_out() -> None:
    """A future-dated report cannot seal the honest fleet's reports out as late."""
    scenario = Scenario(
        scenario_id="t-future",
        name="watermark poisoning",
        demonstrates="",
        n_nodes=30,
        ticks=30,
        adversary=_Futurist(),
        seed=7101,
    )
    result = run_scenario(scenario, FULL)

    assert result.orchestrator.future_updates == result.adversary.sent > 0
    assert result.orchestrator.late_updates == 0
    assert all(len(b.updates) == scenario.n_nodes for b in result.orchestrator.batches)
    assert result.false_positives == frozenset()


def test_restarting_the_monitor_does_not_launder_trust() -> None:
    """A compromised device restarting its monitor every two ticks is still caught."""
    original = MonitoringAgent.tick

    def restarting(self):
        now = self.clock.now()
        if self.node_id == "node-0" and now >= 5 and int(now) % 2 == 0:
            self.state = TrustState.initial(self.params, sim_time=now)
        return original(self)

    scenario = Scenario(
        scenario_id="t-launder",
        name="trust laundering",
        demonstrates="",
        n_nodes=30,
        ticks=60,
        anomalies=(Anomaly("node-0", 5.0, 55.0, 0.6),),
        ground_truth={"node-0": 5.0},
        seed=7102,
    )
    with patch.object(MonitoringAgent, "tick", restarting):
        result = run_scenario(scenario, FULL)

    assert "node-0" in result.detected
    assert result.pipeline.fusion.trust_rise_capped > 0


def test_resilience_scenarios_are_disjoint_from_evaluation_and_calibration() -> None:
    from m8_eval_harness.scenarios import CALIBRATION, SCENARIOS

    seeds = {s.seed for s in (*SCENARIOS, *CALIBRATION)}
    assert seeds.isdisjoint({s.seed for s in RESILIENCE})


def test_a_mass_crash_is_one_outage_watched_never_isolated_and_fully_recovered() -> None:
    scenario = by_id("r1")
    crashed = set(scenario.outages)
    result = run_scenario(scenario, FULL)

    assert any(set(nodes) == crashed for _, nodes in result.orchestrator.outages), "one incident"
    for node_id in crashed:
        watched = result.first_at_or_above(node_id, 1)
        assert watched is not None and watched < 30.0, "escalated while dark"
        assert result.worst_level(node_id) < 4, "never isolated without a human"
        assert _last_level(result, node_id) == 0, "back to full trust"
    never_dark = scenario.healthy - crashed
    assert not any(result.worst_level(n) >= 2 for n in never_dark), (
        "the rest of the fleet untouched"
    )


def test_an_outage_neither_hides_a_campaign_nor_joins_it() -> None:
    scenario = by_id("r2")
    crashed = set(scenario.outages)
    result = run_scenario(scenario, FULL)

    assert result.detected == scenario.compromised
    implicated = {n for o in result.pipeline.outcomes for n in o.correlation.implicated_node_ids}
    assert not implicated & crashed
    bystanders = scenario.healthy - crashed
    assert not any(result.worst_level(n) >= 2 for n in bystanders)


@pytest.mark.parametrize("scenario_id", ["r3", "r4", "r5"])
def test_a_healthy_device_that_misbehaved_is_not_latched(scenario_id) -> None:
    """A two-tick glitch does not leave a device at L1 for the rest of the run."""
    scenario = by_id(scenario_id)
    result = run_scenario(scenario, FULL)
    touched = {a.node_id for a in scenario.anomalies}

    assert all(_last_level(result, n) == 0 for n in touched)
    assert all(result.worst_level(n) < 4 for n in touched)


def test_a_benign_fleet_event_is_remembered_as_benign_not_as_an_attack() -> None:
    """V7, closed by adjudication."""
    result = run_scenario(by_id("r5"), FULL)
    stored = result.pipeline.curator.store.all_records()
    assert stored, "the event is still remembered"
    assert {r.status for r in stored} == {"benign"}
    assert result.recall_boosts == 0


def test_a_remembered_benign_event_no_longer_amplifies_the_next_one() -> None:
    """The measured V7 attack: the same benign congestion twice (scenario r6)."""
    scenario = by_id("r6")
    second_wave = {f"node-{i}" for i in range(10, 20)}

    def burden(result) -> int:
        return sum(
            1
            for o in result.pipeline.outcomes
            for p in o.plans
            if p.node_id in second_wave and p.proposed_level >= 2
        )

    remembered_as_attack = run_scenario(scenario, FULL, adjudication="auto_confirm")
    adjudicated = run_scenario(scenario, FULL)
    memoryless = run_scenario(scenario, NO_MEMORY)

    assert remembered_as_attack.recall_boosts > 0
    assert adjudicated.recall_boosts == 0
    assert burden(remembered_as_attack) > burden(adjudicated)
    assert burden(adjudicated) == burden(memoryless)
