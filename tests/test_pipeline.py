"""The closed loop: every module driven in order, for one tick and across ticks."""

from __future__ import annotations

import pytest

from agents.approval import ApprovalGate, ScriptedApproval
from agents.orchestrator import TickBatch
from agents.pipeline import ClosedLoopPipeline, TickOutcome
from m5_immune_memory import HashingEmbedder, MemoryQuery, MemoryStore
from m6_trust_fusion import TrustFusionEngine
from m7_self_healing import Phase, SelfHealingEngine
from m10_persona_drift.nhi import issue_identity
from shared.bus import InProcBus
from shared.schemas import ContextVector, Provenance, TrustUpdate

HEALTHY = 0.95


def _update(node_id: str, sim_time: float, *, level: float) -> TrustUpdate:
    """A self-consistent report: observation is the mean of the context dims."""
    ctx = ContextVector(identity=level, behavioral=level, device=level, network=level)
    return TrustUpdate(
        sim_time=sim_time,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id=node_id,
        node_trust=level,
        observation=level,
        context=ctx,
        provenance=Provenance.HIGH,
        agent_id=f"mon-{node_id}",
    )


def _batch(sim_time: float, *, n_bad: int = 2, n_total: int = 6, bad: float = 0.10):
    return TickBatch(
        sim_time=sim_time,
        run_id="r",
        seed=1,
        config_hash="h",
        updates=[
            _update(f"n-{i}", sim_time, level=bad if i < n_bad else HEALTHY) for i in range(n_total)
        ],
    )


def _pipeline(**over) -> ClosedLoopPipeline:
    kw = dict(fusion=TrustFusionEngine(bus=InProcBus(), run_id="r", seed=1, config_hash="h"))
    kw.update(over)
    return ClosedLoopPipeline(**kw)


def _memory():
    names = ("verifier", "correlation", "fusion", "orchestrator", "monitoring")
    reg = {n: issue_identity(n, seed=n.encode().ljust(32, b"\0")) for n in names}
    emb = HashingEmbedder()
    store = MemoryStore(dim=emb.dim)
    return MemoryQuery(store=store, registry=reg, embedder=emb), store, reg


def test_one_tick_produces_every_stage() -> None:
    out = _pipeline().run(_batch(1.0))
    assert isinstance(out, TickOutcome)
    assert out.correlation is not None
    assert out.classification is not None
    assert len(out.gt_updates) == 6
    assert len(out.plans) == 6
    assert out.report is not None
    assert len(out.executions) == 6


def test_plans_and_executions_stay_aligned() -> None:
    """`TickOutcome.executed` zips them, so a length mismatch would be silent."""
    out = _pipeline().run(_batch(1.0))
    assert len(out.plans) == len(out.executions)
    assert all(p.node_id for p in out.executed)


def test_a_quiet_fleet_plans_no_action() -> None:
    out = _pipeline().run(_batch(1.0, n_bad=0))
    assert {p.proposed_level for p in out.plans} == {0}
    assert out.correlation.implicated_node_ids == []


def test_an_attacked_device_is_planned_above_a_healthy_one() -> None:
    out = _pipeline().run(_batch(1.0))
    by_node = {p.node_id: p.proposed_level for p in out.plans}
    assert by_node["n-0"] > by_node["n-5"]


def test_rep_is_recorded_after_the_responses_it_describes() -> None:
    """Fusion at t must not see the interactions from t."""
    pipe = _pipeline()
    first = pipe.run(_batch(1.0))
    assert all(u.rep == 1.0 for u in first.gt_updates), "nothing recorded yet at t=1"
    assert first.reputations["n-0"] < 1.0, "but it is recorded by the end of the tick"

    second = pipe.run(_batch(2.0))
    rep_n0 = next(u.rep for u in second.gt_updates if u.node_id == "n-0")
    assert rep_n0 < 1.0, "and visible to fusion at t=2"


def test_a_failed_verification_stops_execution() -> None:
    """Verification runs before the gate, so a bad plan never reaches M9."""
    pipe = _pipeline()
    out = pipe.run(_batch(1.0))

    tampered = out.plans[0].model_copy(update={"proposed_level": 0})
    report = pipe.verifier.audit(plans=[tampered], gt_updates=out.gt_updates)
    assert report.blocks(tampered.node_id) is True

    result = pipe.engine.execute(tampered, verification=report)
    assert result.executed is False
    assert result.decision is None


def test_healing_reacts_to_this_tick_on_the_next_one() -> None:
    """One anomalous tick should not start a recovery."""
    healer = SelfHealingEngine()
    pipe = _pipeline(healer=healer)
    pipe.run(_batch(1.0, n_bad=0))
    assert healer.state("n-0").phase is Phase.IDLE


def test_without_an_approval_gate_l4_is_never_granted() -> None:
    """A missing operator must not mean automatic isolation."""
    pipe = _pipeline()
    out = pipe.run(_batch(1.0, bad=0.0))
    for plan, result in zip(out.plans, out.executions, strict=True):
        if plan.proposed_level == 4:
            assert result.executed is False


def test_an_approved_isolation_executes() -> None:
    """What L4 actually costs, as arithmetic."""
    pipe = _pipeline(approval=ApprovalGate(ScriptedApproval.always_approve()))
    for _ in range(8):
        for node in ("n-0", "n-1", "n-2", "n-3"):
            pipe.fusion.observe_response(node, 3)

    out = pipe.run(_batch(1.0, n_bad=4, bad=0.0))
    assert any(p.proposed_level == 4 for p in out.plans), "a fleet-wide campaign"
    assert out.approvals, "every plan is reviewed; the gate decides what escalates"

    isolated = [
        result
        for plan, result in zip(out.plans, out.executions, strict=True)
        if plan.proposed_level == 4
    ]
    assert all(r.executed for r in isolated), "approved, so it executes"


def test_no_recall_is_the_memoryless_baseline() -> None:
    out = _pipeline().run(_batch(1.0))
    assert out.correlation.recall_boost == 0.0
    assert out.correlation.recalled_record_id is None


def test_no_healer_removes_c5_and_nothing_else() -> None:
    without = _pipeline().run(_batch(1.0))
    with_healer = _pipeline(healer=SelfHealingEngine()).run(_batch(1.0))
    assert without.healing == []
    assert [p.proposed_level for p in without.plans] == [
        p.proposed_level for p in with_healer.plans
    ]


def test_a_sustained_attack_escalates_and_a_quiet_fleet_does_not() -> None:
    attacked = _pipeline()
    quiet = _pipeline()
    worst_attacked, worst_quiet = 0, 0
    for t in range(6):
        worst_attacked = max(
            worst_attacked,
            max(p.proposed_level for p in attacked.run(_batch(float(t))).plans),
        )
        worst_quiet = max(
            worst_quiet,
            max(p.proposed_level for p in quiet.run(_batch(float(t), n_bad=0)).plans),
        )
    assert worst_attacked >= 3
    assert worst_quiet == 0


def test_healing_runs_its_phases_when_trust_collapses() -> None:
    healer = SelfHealingEngine()
    pipe = _pipeline(healer=healer)
    seen = []
    for t in range(6):
        seen += [e.phase for e in pipe.run(_batch(float(t), bad=0.0)).healing]
    assert "revoke" in seen
    assert "recalibrate" in seen


def test_the_loop_is_reproducible() -> None:
    """Same inputs, same outputs: the property every evaluation run depends on."""

    def trace():
        pipe = _pipeline(healer=SelfHealingEngine())
        out = []
        for t in range(5):
            o = pipe.run(_batch(float(t)))
            out.append(
                (
                    round(o.correlation.cti, 9),
                    tuple(p.proposed_level for p in o.plans),
                    tuple(round(v, 9) for v in o.reputations.values()),
                    tuple(e.phase for e in o.healing),
                )
            )
        return out

    assert trace() == trace()


def test_recall_is_consulted_when_memory_is_attached() -> None:
    query, store, reg = _memory()
    pipe = _pipeline(recall=query)
    out = pipe.run(_batch(1.0))
    assert out.correlation.pattern_text != "", "a campaign produces a signature"
    assert out.correlation.recall_boost == 0.0, "nothing stored yet"


def test_outcomes_accumulate_in_order() -> None:
    pipe = _pipeline()
    for t in range(4):
        pipe.run(_batch(float(t)))
    assert [o.sim_time for o in pipe.outcomes] == [0.0, 1.0, 2.0, 3.0]


def test_quarantined_reporters_are_passed_through_to_correlation() -> None:
    pipe = _pipeline(quarantined_agent_ids=("mon-n-0",))
    out = pipe.run(_batch(1.0))
    assert out.correlation is not None


def test_low_provenance_telemetry_cannot_execute_a_restriction() -> None:
    """The capability gate still applies to everything the loop plans."""
    pipe = _pipeline(input_provenance=Provenance.UNTRUSTED)
    out = pipe.run(_batch(1.0))
    for plan, result in zip(out.plans, out.executions, strict=True):
        if plan.proposed_level >= 2:
            assert result.executed is False
            assert result.decision.deny_reason == "provenance_too_low"


def test_audit_records_exist_for_every_execution_attempt() -> None:
    out = _pipeline().run(_batch(1.0))
    assert len(out.audit) == len(out.executions)
    assert {r.event_type for r in out.audit} <= {"response.executed", "response.denied"}


def test_master_score_is_produced_for_every_node() -> None:
    out = _pipeline().run(_batch(1.0))
    assert all(0.0 <= u.master_score <= 1.0 for u in out.gt_updates)


def test_reputation_falls_only_for_devices_that_needed_a_response() -> None:
    out = _pipeline().run(_batch(1.0))
    levels = {p.node_id: p.proposed_level for p in out.plans}
    for node_id, rep in out.reputations.items():
        if levels[node_id] == 0:
            assert rep == pytest.approx(1.0)
        else:
            assert rep < 1.0
