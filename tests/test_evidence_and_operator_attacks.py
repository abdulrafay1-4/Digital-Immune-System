"""Regression tests: attacks on the evidence path, the operator, and the evaluation itself."""

from __future__ import annotations

from collections import Counter
from unittest.mock import patch

from agents.approval import ApprovalGate, ScriptedApproval
from agents.correlation import CorrelationAgent
from agents.orchestrator import ORCHESTRATOR_TOPIC, TRUST_TOPIC, Orchestrator
from m1_monitoring.agent import MonitoringAgent
from m7_self_healing.engine import Phase
from m8_eval_harness.baselines import BINARY_RESPONSE, FULL
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios.base import Anomaly, Scenario
from m8_eval_harness.scenarios.catalogue import S3_RECURRING_ATTACKER, S6_WEAPONISED_HEALING
from shared.bus import InProcBus
from shared.schemas import ContextVector, Provenance, TrustUpdate


def _scenario(scenario_id: str, *, n_nodes: int = 30, ticks: int = 40, seed: int, **kw) -> Scenario:
    return Scenario(
        scenario_id=scenario_id,
        name=scenario_id,
        demonstrates="",
        n_nodes=n_nodes,
        ticks=ticks,
        seed=seed,
        **kw,
    )


def test_a_forged_observation_cannot_hold_a_compromised_device_at_l0() -> None:
    """A monitor claiming a perfect observation beside a degraded context is capped."""
    original = MonitoringAgent.tick

    def lying(self):
        if self.node_id != "node-0":
            return original(self)
        now = self.clock.now()
        context, provenance = self.sensor.read(now, self.node_id)
        update = TrustUpdate(
            sim_time=now,
            run_id=self.run_id,
            seed=self.seed,
            config_hash=self.config_hash,
            node_id=self.node_id,
            node_trust=self.state.step(1.0, now),
            observation=1.0,
            context=context,
            provenance=provenance,
            agent_id=self.agent_id,
        )
        self.bus.publish(TRUST_TOPIC, update)
        return update

    scenario = _scenario(
        "t-obs",
        ticks=60,
        seed=7401,
        anomalies=(Anomaly("node-0", 5.0, 55.0, 0.6),),
        ground_truth={"node-0": 5.0},
    )
    with patch.object(MonitoringAgent, "tick", lying):
        result = run_scenario(scenario, FULL)
    assert "node-0" in result.detected


def test_an_honest_fleet_is_never_capped() -> None:
    """A first report has no history to step from, so it is never capped."""
    result = run_scenario(_scenario("t-honest", n_nodes=20, ticks=30, seed=7402), FULL)
    assert result.pipeline.fusion.trust_rise_capped == 0


def test_fusion_never_trusts_a_device_more_than_its_own_monitor_did() -> None:
    """Healing is a ceiling: it never lifts a still-compromised device's trust."""
    scenario = _scenario(
        "t-heal",
        ticks=90,
        seed=7403,
        anomalies=(Anomaly("node-0", 5.0, 70.0, 0.6),),
        ground_truth={"node-0": 5.0},
    )
    result = run_scenario(scenario, FULL)
    reported = {
        b.sim_time: {u.node_id: u.node_trust for u in b.updates}
        for b in result.orchestrator.batches
    }
    assert any(o.healing for o in result.pipeline.outcomes), "healing actually ran"
    for outcome in result.pipeline.outcomes[1:]:
        previous = reported[outcome.sim_time - 1]
        for gt in outcome.gt_updates:
            assert gt.ts <= previous[gt.node_id] + 1e-9, (outcome.sim_time, gt.node_id)


def test_a_lying_correlation_agent_cannot_touch_healthy_devices_or_stop_enforcement() -> None:
    """An inflating correlation agent restricts no healthy device and blocks nothing."""
    original = CorrelationAgent.correlate

    def fabricating(self, batch, **kwargs):
        result = original(self, batch, **kwargs)
        if "recall" not in kwargs:
            return result
        return result.model_copy(
            update={
                "implicated_node_ids": sorted(result.node_ids),
                "cti": 0.9,
                "campaign_corroboration": 0.30,
            }
        )

    scenario = _scenario(
        "t-fabricate",
        n_nodes=50,
        seed=7404,
        anomalies=(Anomaly("node-0", 10.0, 38.0, 0.9),),
        ground_truth={"node-0": 10.0},
    )
    with patch.object(CorrelationAgent, "correlate", fabricating):
        result = run_scenario(scenario, FULL)

    assert result.false_positives == frozenset()
    assert all(result.worst_level(n) < 2 for n in scenario.healthy)
    assert "node-0" in result.detected
    assert result.disruptive_actions > 0, "the real attack was still enforced"
    assert any("cti_inflated" in o.report.codes() for o in result.pipeline.outcomes)


_CAMPAIGN = dict(
    anomalies=tuple(Anomaly(f"node-{i}", 10.0, 40.0, 0.9) for i in range(5)),
    ground_truth={f"node-{i}": 10.0 for i in range(5)},
)


def _l4_episodes(result, node_id: str) -> int:
    levels = [
        p.proposed_level for o in result.pipeline.outcomes for p in o.plans if p.node_id == node_id
    ]
    return sum(1 for a, b in zip([0, *levels], levels, strict=False) if a < 4 <= b)


def test_a_denied_isolation_is_never_carried_out() -> None:
    """A denied isolation is never executed."""
    gate = ApprovalGate(ScriptedApproval.always_deny())
    result = run_scenario(
        _scenario("t-deny", ticks=45, seed=7405, **_CAMPAIGN), FULL, approval=gate
    )

    assert gate.escalations, "isolation was asked for"
    assert result.isolations == 0
    assert result.disruptive_actions > 0, "restricted instead"


def test_an_approved_isolation_is_carried_out() -> None:
    gate = ApprovalGate(ScriptedApproval.always_approve())
    result = run_scenario(
        _scenario("t-approve", ticks=45, seed=7405, **_CAMPAIGN), FULL, approval=gate
    )
    assert result.isolations > 0


def test_with_no_operator_an_l4_device_is_restricted_not_ignored() -> None:
    """Without an operator, an L4 device is restricted rather than left alone."""
    result = run_scenario(_scenario("t-no-operator", ticks=45, seed=7405, **_CAMPAIGN), FULL)
    at_l4 = [n for n in result.scenario.compromised if result.worst_level(n) == 4]
    assert at_l4, "the scenario reaches isolation"
    restricted = {
        p.node_id
        for o in result.pipeline.outcomes
        for p, ex in zip(o.plans, o.executions, strict=True)
        if ex.executed and ex.level is not None and ex.level == 3
    }
    assert set(at_l4) <= restricted
    assert result.isolations == 0


def test_the_operator_is_asked_once_per_isolation_episode() -> None:
    """One question per device per isolation episode, not one per tick."""
    gate = ApprovalGate(ScriptedApproval.always_approve())
    result = run_scenario(
        _scenario("t-fatigue", ticks=45, seed=7405, **_CAMPAIGN), FULL, approval=gate
    )

    asked = Counter(d.node_id for d in gate.escalations)
    assert gate.standing_reuses > 0
    for node_id in result.scenario.compromised:
        assert asked[node_id] == _l4_episodes(result, node_id)


def test_an_operator_can_release_a_device_parked_for_approval() -> None:
    """An operator's grant reaches the healing engine."""
    result = run_scenario(S6_WEAPONISED_HEALING, FULL)
    pipeline, target = result.pipeline, S6_WEAPONISED_HEALING.adversary.target
    assert pipeline.healer.state(target).phase is Phase.NEEDS_APPROVAL

    pipeline.grant_heal(target)
    last = result.orchestrator.batches[-1]
    now = last.sim_time + 1.0
    pipeline.run(
        last.model_copy(
            update={
                "sim_time": now,
                "updates": [u.model_copy(update={"sim_time": now}) for u in last.updates],
            }
        )
    )
    assert pipeline.healer.state(target).phase is not Phase.NEEDS_APPROVAL


def test_a_replaced_monitor_can_be_rebound_by_an_administrator() -> None:
    """A device whose monitor was replaced can be rebound by an administrator."""
    bus = InProcBus()
    orchestrator = Orchestrator(bus=bus, run_id="r", seed=1, config_hash="h")
    orchestrator.attach()

    def report(agent_id: str, t: float) -> None:
        bus.publish(
            TRUST_TOPIC,
            TrustUpdate(
                sim_time=t,
                run_id="r",
                seed=1,
                config_hash="h",
                node_id="node-0",
                node_trust=0.9,
                observation=0.9,
                context=ContextVector(identity=0.9, behavioral=0.9, device=0.9, network=0.9),
                provenance=Provenance.HIGH,
                agent_id=agent_id,
            ),
        )

    report("mon-old", 1.0)
    report("mon-new", 2.0)
    assert orchestrator.unbound_updates == 1

    orchestrator.rebind("node-0", "mon-new", by="admin:alice")
    report("mon-new", 3.0)
    report("mon-old", 4.0)
    assert orchestrator.unbound_updates == 2, "the new monitor is accepted, the old one is not"
    audit = [
        m
        for topic, m in bus.log
        if topic == ORCHESTRATOR_TOPIC and m.event_type == "orchestrator.rebind"
    ]
    assert len(audit) == 1 and audit[0].actor_id == "admin:alice"


def test_the_binary_baseline_actually_enforces_something() -> None:
    """The binary-response arm's plans match the level the engine derived."""
    result = run_scenario(S3_RECURRING_ATTACKER, BINARY_RESPONSE)
    refused = [
        r
        for r in result.pipeline.engine.audit.records
        if r.payload.get("deny_reason") == "level_not_derived"
    ]
    assert refused == []
    assert result.disruptive_actions > 0


def test_an_approval_from_an_earlier_episode_does_not_isolate_again() -> None:
    """A signed approval replayed after recovery and relapse does not isolate again."""
    from agents.approval import ApprovalGate, ScriptedApproval
    from m4_response_engine.engine import ResponseEngine
    from m4_response_engine.hysteresis import HysteresisParams, LevelHysteresis
    from m6_trust_fusion.fusion import gt_payload
    from shared.integrity import DEV_KEY, sign
    from shared.schemas import GlobalTrustUpdate, ResponsePlan

    engine = ResponseEngine(
        require_signature=True, hysteresis=LevelHysteresis(params=HysteresisParams(n=1))
    )

    def gt(value: float, t: float) -> GlobalTrustUpdate:
        payload = gt_payload(
            run_id="r",
            seed=1,
            config_hash="h",
            sim_time=t,
            node_id="node-0",
            gt=value,
            ts=value,
            cti_i=0.0,
            rep=1.0,
            drift_flag=0.0,
        )
        return GlobalTrustUpdate(
            signature=sign(payload, DEV_KEY),
            sim_time=t,
            run_id="r",
            seed=1,
            config_hash="h",
            node_id="node-0",
            gt=value,
            ts=value,
            cti_i=0.0,
            cti_trust=1.0,
            rep=1.0,
            master_score=value,
        )

    class Passes:
        findings: list = []

        def blocks(self, node_id: str) -> bool:
            return False

    def plan(level: int, t: float) -> ResponsePlan:
        return ResponsePlan(
            sim_time=t, run_id="r", seed=1, config_hash="h", node_id="node-0", proposed_level=level
        )

    gate = ApprovalGate(ScriptedApproval.always_approve())
    engine.decide(gt(0.05, 10.0))
    first = gate.review_plan(plan(4, 10.0))
    assert int(engine.execute(plan(4, 10.0), verification=Passes(), approval=first).level) == 4

    engine.decide(gt(0.95, 11.0))
    engine.execute(plan(0, 11.0), verification=Passes())
    engine.decide(gt(0.05, 40.0))
    replayed = engine.execute(plan(4, 40.0), verification=Passes(), approval=first)
    assert int(replayed.level) == 3, "restricted, not isolated, until someone approves again"
