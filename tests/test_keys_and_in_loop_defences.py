"""Regression tests: the key posture, the operator's input, and M10/M11 running in the loop."""

from __future__ import annotations

import pytest

from agents.approval import ApprovalError, ApprovalGate, ApprovalRequest, HumanApproval
from agents.orchestrator import TRUST_TOPIC, Orchestrator
from agents.pipeline import ClosedLoopPipeline
from m6_trust_fusion import TrustFusionEngine
from m8_eval_harness.baselines import FULL
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios.base import Anomaly, Scenario
from shared import keys
from shared.bus import InProcBus
from shared.schemas import ContextVector, Provenance, TrustUpdate


def test_setting_the_master_key_after_first_use_cannot_split_the_keys(monkeypatch) -> None:
    """Keys derived at import and later come from the same master."""
    keys.master_key.cache_clear()
    try:
        first = keys.derive("gt-signing")
        monkeypatch.setenv(keys.ENV_VAR, "ab" * 32)
        assert keys.derive("gt-signing") == first
        assert keys.derive("approval") == keys.derive("approval", keys.master_key())
        assert keys.using_development_key() is True, "the posture reports the key in use"
    finally:
        monkeypatch.delenv(keys.ENV_VAR, raising=False)
        keys.master_key.cache_clear()


def test_a_real_master_key_is_reported_as_such(monkeypatch) -> None:
    keys.master_key.cache_clear()
    try:
        monkeypatch.setenv(keys.ENV_VAR, "cd" * 32)
        assert keys.using_development_key() is False
    finally:
        monkeypatch.delenv(keys.ENV_VAR, raising=False)
        keys.master_key.cache_clear()


def _request() -> ApprovalRequest:
    return ApprovalRequest(
        sim_time=1.0, run_id="r", seed=1, config_hash="h", node_id="node-0", level=4
    )


@pytest.mark.parametrize("delay", [float("nan"), float("inf")])
def test_a_non_finite_operator_delay_is_refused(delay: float) -> None:
    policy = HumanApproval(interrupt_fn=lambda payload: {"approved": True, "delay_sim": delay})
    with pytest.raises(ApprovalError, match="finite"):
        policy.decide(_request())


def test_an_unbounded_operator_reason_is_refused() -> None:
    policy = HumanApproval(interrupt_fn=lambda payload: {"approved": False, "reason": "x" * 5000})
    with pytest.raises(ApprovalError, match="limited"):
        policy.decide(_request())


class _BrokenOperator:
    """An operator interface that returns something unusable every time."""

    def decide(self, request: ApprovalRequest):  # type: ignore[no-untyped-def]
        raise ApprovalError("unusable operator response")


SEVERE = Scenario(
    scenario_id="t-broken-operator",
    name="severe campaign with a broken operator interface",
    demonstrates="",
    n_nodes=20,
    ticks=40,
    anomalies=tuple(Anomaly(f"node-{i}", 5.0, 35.0, 0.95) for i in range(3)),
    seed=7801,
)


def test_a_broken_operator_costs_no_ticks_and_isolates_nothing() -> None:
    result = run_scenario(SEVERE, FULL, approval=ApprovalGate(_BrokenOperator()))
    assert result.orchestrator.pipeline_failures == 0, "the tick was lost every time"
    assert result.pipeline.degraded.get("approval", 0) > 0, "L4 was reached and asked"
    assert result.isolations == 0
    assert all(result.worst_level(f"node-{i}") >= 3 for i in range(3)), "still restricted"


def _forging(forged: dict[str, float]) -> Scenario:
    return Scenario(
        scenario_id="t-forged",
        name="monitors forging their observation",
        demonstrates="",
        n_nodes=20,
        ticks=30,
        anomalies=tuple(Anomaly(n, 5.0, 25.0, 0.6) for n in ("node-3", "node-4")),
        forged_observation=forged,
        seed=7802,
    )


def test_reporters_that_fail_integrity_are_quarantined_during_the_run() -> None:
    """Quarantine is reassessed every tick during a run."""
    result = run_scenario(_forging({"node-3": 5.0, "node-4": 5.0}), FULL)
    assert result.pipeline.agents_quarantined == {"mon-node-3", "mon-node-4"}


def test_an_honest_fleet_quarantines_nobody() -> None:
    result = run_scenario(_forging({}), FULL)
    assert result.pipeline.agents_quarantined == set()


def _u(node_id: str, sim_time: float) -> TrustUpdate:
    return TrustUpdate(
        sim_time=sim_time,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id=node_id,
        node_trust=0.9,
        observation=0.9,
        context=ContextVector(identity=0.9, behavioral=0.9, device=0.9, network=0.9),
        provenance=Provenance.HIGH,
        agent_id=f"mon-{node_id}",
    )


def test_a_flooding_monitor_puts_its_own_device_under_drift_and_no_other() -> None:
    bus = InProcBus()
    pipe = ClosedLoopPipeline(
        fusion=TrustFusionEngine(bus=bus, run_id="r", seed=1, config_hash="h")
    )
    orch = Orchestrator(
        bus=bus,
        run_id="r",
        seed=1,
        config_hash="h",
        pipeline=pipe,
        max_updates_per_agent_per_tick=2,
    )
    orch.attach()
    for t in range(3):
        for _ in range(4 if t == 2 else 1):
            bus.publish(TRUST_TOPIC, _u("node-0", float(t)))
        bus.publish(TRUST_TOPIC, _u("node-1", float(t)))
    orch.flush()

    last = {u.node_id: u for u in pipe.outcomes[-1].gt_updates}
    assert last["node-0"].drift_flag == 1.0
    assert last["node-1"].drift_flag == 0.0
    assert pipe.persona_violations == 1


def test_recall_hastens_restriction_instead_of_blocking_it(tmp_path) -> None:
    """Recalled records are attested, so a decision they touched sits at MEDIUM."""
    from agents.pipeline import RECALL_PROVENANCE
    from m8_eval_harness import baselines
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios import by_id
    from shared.schemas import Provenance

    assert RECALL_PROVENANCE is Provenance.MEDIUM
    rows = {
        arm: evaluate(
            run_scenario(by_id("s3"), baselines.by_id(arm), seed=20000, results_dir=tmp_path / arm)
        )
        for arm in ("full", "no_memory")
    }
    assert rows["full"]["recall_boosts"] > 0
    assert rows["full"]["actions_refused_low_provenance"] == 0
    assert rows["full"]["residual_compromise"] <= rows["no_memory"]["residual_compromise"]
