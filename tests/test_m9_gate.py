"""Hard-gate integration: no verifier pass and no token means no execution."""

from __future__ import annotations

from agents.verifier import VerifierAgent
from m4_response_engine import ResponseEngine
from shared.schemas import GlobalTrustUpdate, Provenance, ResponsePlan


class _Passes:
    """Verification stub that blocks nothing."""

    def blocks(self, node_id: str) -> bool:
        return False


class _BlocksAll:
    """Verification stub standing in for a tick-wide FAIL."""

    def blocks(self, node_id: str) -> bool:
        return True


def _gt(node_id: str, gt: float) -> GlobalTrustUpdate:
    return GlobalTrustUpdate(
        sim_time=10.0,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id=node_id,
        gt=gt,
        ts=gt,
        cti_i=0.0,
        cti_trust=1.0,
        rep=1.0,
        master_score=gt,
    )


def _armed(gt: float, node_id: str = "node-0") -> tuple[ResponseEngine, int]:
    """An engine that has derived a level for this node, as the pipeline does."""
    eng = ResponseEngine()
    level = eng.decide(_gt(node_id, gt))
    return eng, int(level)


def _plan(level: int, node_id: str = "node-0") -> ResponsePlan:
    return ResponsePlan(
        sim_time=10.0,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id=node_id,
        proposed_level=level,
        rationale="test",
    )


def test_high_provenance_restrict_executes_with_token() -> None:
    eng, level = _armed(0.30)
    result = eng.execute(_plan(level), verification=_Passes(), input_provenance=Provenance.HIGH)
    assert result.executed is True
    assert result.decision.allowed is True
    assert result.decision.token is not None
    assert result.audit is not None
    assert result.audit.event_type == "response.executed"


def test_low_provenance_cannot_execute_isolate() -> None:
    eng, level = _armed(0.05)
    result = eng.execute(_plan(level), verification=_Passes(), input_provenance=Provenance.LOW)
    assert result.executed is False
    assert result.decision.allowed is False
    assert result.decision.token is None
    assert result.decision.deny_reason == "provenance_too_low"
    assert result.audit is not None
    assert result.audit.event_type == "response.denied"


def test_plan_without_token_never_side_effects() -> None:
    """Fall-through-to-allow must not happen: deny leaves executed=False."""
    eng, level = _armed(0.05)
    denied = eng.execute(
        _plan(level), verification=_Passes(), input_provenance=Provenance.UNTRUSTED
    )
    assert denied.executed is False
    assert all(a.event_type == "response.denied" for a in eng.audit_log)


def test_verifier_fail_blocks_execution_before_m9_is_consulted() -> None:
    """A blocked plan must not reach the capability registry at all."""
    eng, level = _armed(0.30)
    result = eng.execute(_plan(level), verification=_BlocksAll(), input_provenance=Provenance.HIGH)
    assert result.executed is False
    assert result.decision is None, "M9 should not be consulted for a plan the verifier failed"
    assert result.audit is not None
    assert result.audit.event_type == "response.denied"
    assert result.audit.payload["deny_reason"] == "verifier_failed"


def test_under_response_plan_is_refused_end_to_end() -> None:
    """The real defect: GT warrants L3, a tampered plan says L0, and it executed anyway."""
    gt_update = _gt("node-0", 0.30)
    tampered = _plan(0)

    report = VerifierAgent().audit(plans=[tampered], gt_updates=[gt_update])
    assert "under_response" in report.codes()
    assert report.failed is True
    assert report.blocks("node-0") is True

    eng = ResponseEngine()
    eng.decide(gt_update)
    result = eng.execute(tampered, verification=report, input_provenance=Provenance.HIGH)
    assert result.executed is False
    assert result.audit.payload["deny_reason"] == "level_not_derived"


def test_verifier_fail_on_one_node_does_not_block_another() -> None:
    """A per-node FAIL is per-node."""
    bad = _plan(0, node_id="node-0")
    good = _plan(3, node_id="node-1")
    report = VerifierAgent().audit(
        plans=[bad, good],
        gt_updates=[_gt("node-0", 0.30), _gt("node-1", 0.30)],
    )
    assert report.blocks("node-0") is True
    assert report.blocks("node-1") is False

    eng = ResponseEngine()
    eng.decide(_gt("node-0", 0.30))
    eng.decide(_gt("node-1", 0.30))
    assert eng.execute(bad, verification=report, input_provenance=Provenance.HIGH).executed is False
    assert eng.execute(good, verification=report, input_provenance=Provenance.HIGH).executed is True


def test_passing_report_still_requires_a_token() -> None:
    """The two gates are independent: a clean verdict does not grant a capability."""
    eng, level = _armed(0.30)
    plan = _plan(level)
    report = VerifierAgent().audit(plans=[plan], gt_updates=[_gt("node-0", 0.30)])
    assert report.blocks("node-0") is False

    result = eng.execute(plan, verification=report, input_provenance=Provenance.LOW)
    assert result.executed is False
    assert result.decision.deny_reason == "provenance_too_low", "restrict needs MEDIUM"


def test_an_unapproved_isolation_is_carried_out_as_a_restriction() -> None:
    """The human gate is enforced where the action happens."""
    eng, level = _armed(0.05)
    plan = _plan(level)
    report = VerifierAgent().audit(plans=[plan], gt_updates=[_gt("node-0", 0.05)])
    assert "l4_without_approval" in report.codes()
    assert not report.blocks(plan.node_id)

    result = eng.execute(plan, verification=report, input_provenance=Provenance.HIGH)
    assert result.executed is True
    assert int(result.level) == 3
    assert result.decision.capability == "restrict"
    assert result.audit.payload["isolation_withheld"] is True


def test_isolation_needs_an_approval_for_this_device_already_decided() -> None:
    """Denied, for another device, or not yet decided: restrict."""
    from types import SimpleNamespace

    def approval(**overrides):
        fields = {"node_id": "node-0", "approved": True, "decided_at_sim": 0.0}
        return SimpleNamespace(**{**fields, **overrides})

    for refused in (
        approval(approved=False),
        approval(node_id="node-9"),
        approval(decided_at_sim=1e9),
    ):
        eng, level = _armed(0.05)
        plan = _plan(level)
        result = eng.execute(
            plan, verification=_Passes(), input_provenance=Provenance.HIGH, approval=refused
        )
        assert result.executed is True and int(result.level) == 3

    from agents.approval import ApprovalGate, ScriptedApproval

    eng, level = _armed(0.05)
    plan = _plan(level)
    granted = ApprovalGate(ScriptedApproval.always_approve()).review_plan(plan)
    result = eng.execute(
        plan, verification=_Passes(), input_provenance=Provenance.HIGH, approval=granted
    )
    assert result.executed is True and int(result.level) == 4
    assert result.decision.capability == "isolate"


def test_a_level_the_engine_did_not_derive_is_refused() -> None:
    """The planner is a narrator."""
    eng, derived = _armed(0.30)
    for fabricated in (0, 1, 2, 4):
        result = eng.execute(
            _plan(fabricated), verification=_Passes(), input_provenance=Provenance.HIGH
        )
        assert result.executed is False
        assert result.audit.payload["deny_reason"] == "level_not_derived"
        assert result.audit.payload["derived_level"] == derived


def test_the_derivation_gate_runs_before_the_verifier() -> None:
    """A fabricated level is refused even by a verifier that passes everything."""
    eng, _ = _armed(0.30)
    result = eng.execute(_plan(0), verification=_Passes(), input_provenance=Provenance.HIGH)
    assert result.executed is False
    assert result.decision is None, "M9 is never consulted"


def test_hysteresis_lives_in_the_engine_and_holds_a_de_escalation() -> None:
    """Escalation applies at once; de-escalation waits for stable ticks."""
    eng = ResponseEngine()
    assert int(eng.decide(_gt("node-0", 0.30))) == 3
    assert int(eng.decide(_gt("node-0", 0.95))) == 3, "held by hysteresis"
    assert int(eng.decide(_gt("node-0", 0.95))) == 3
    assert int(eng.decide(_gt("node-0", 0.95))) == 0, "third stable tick releases it"


def test_effective_level_does_not_advance_hysteresis() -> None:
    eng = ResponseEngine()
    eng.decide(_gt("node-0", 0.30))
    for _ in range(5):
        assert int(eng.effective_level("node-0")) == 3


def test_a_forged_approval_does_not_isolate() -> None:
    """An object with approved=True but no gate signature does not authorise an isolation."""
    from types import SimpleNamespace

    eng, level = _armed(0.05)
    plan = _plan(level)
    forged = SimpleNamespace(
        run_id=plan.run_id,
        seed=plan.seed,
        config_hash=plan.config_hash,
        sim_time=plan.sim_time,
        node_id=plan.node_id,
        level=4,
        approved=True,
        decided_by="operator:mallory",
        delay_sim=0.0,
        decided_at_sim=plan.sim_time,
        signature="0" * 64,
    )
    result = eng.execute(
        plan, verification=_Passes(), input_provenance=Provenance.HIGH, approval=forged
    )
    assert result.executed is True and int(result.level) == 3
    assert result.audit.payload["isolation_withheld"] is True


def test_an_approval_does_not_raise_the_evidence_behind_an_isolation() -> None:
    """Approving on MEDIUM evidence still restricts."""
    from agents.approval import ApprovalGate, ScriptedApproval

    for provenance in (Provenance.MEDIUM, Provenance.LOW):
        eng, level = _armed(0.05)
        plan = _plan(level)
        granted = ApprovalGate(ScriptedApproval.always_approve()).review_plan(plan)
        result = eng.execute(
            plan, verification=_Passes(), input_provenance=provenance, approval=granted
        )
        if provenance is Provenance.MEDIUM:
            assert result.executed is True, "restricted, not left alone"
            assert int(result.level) == 3
            assert result.audit.payload["isolation_withheld"] is True
        else:
            assert not (result.executed and int(result.level) == 4)
