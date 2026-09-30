"""The Level 4 approval gate."""

from __future__ import annotations

from typing import Any

import pytest

from agents import approval as approval_module
from agents.approval import (
    APPROVAL_REQUIRED_LEVEL,
    ApprovalDecision,
    ApprovalError,
    ApprovalGate,
    ApprovalRequest,
    DeciderKind,
    HumanApproval,
    ScriptedApproval,
    ScriptedStep,
    requires_approval,
)
from shared.schemas import ResponsePlan

RUN_ID = "run-approval"
SEED = 7
CONFIG_HASH = "cfg-abc"


def make_request(
    *, level: int = 4, sim_time: float = 100.0, node_id: str = "node-1"
) -> ApprovalRequest:
    return ApprovalRequest(
        sim_time=sim_time,
        run_id=RUN_ID,
        seed=SEED,
        config_hash=CONFIG_HASH,
        node_id=node_id,
        level=level,
        rationale="trust collapsed",
    )


def make_plan(*, level: int = 4, sim_time: float = 100.0) -> ResponsePlan:
    return ResponsePlan(
        sim_time=sim_time,
        run_id=RUN_ID,
        seed=SEED,
        config_hash=CONFIG_HASH,
        node_id="node-1",
        proposed_level=level,
        rationale="GT below isolation threshold",
    )


def test_always_approve() -> None:
    decision = ScriptedApproval.always_approve().decide(make_request())

    assert decision.approved is True
    assert decision.denied is False
    assert decision.decider is DeciderKind.SCRIPTED
    assert decision.delay_sim == 0.0


def test_always_deny() -> None:
    decision = ScriptedApproval.always_deny().decide(make_request())

    assert decision.approved is False
    assert decision.denied is True
    assert decision.decider is DeciderKind.SCRIPTED


def test_a_denial_is_a_normal_outcome_not_an_exception() -> None:
    """Scenario 6 measures denials; they must be data, not control flow."""
    policy = ScriptedApproval.always_deny()
    for _ in range(5):
        assert policy.decide(make_request()).approved is False
    assert len(policy.decisions) == 5


def test_decision_carries_run_identity_from_the_request() -> None:
    """Approval records are evidence: they must tie back to the run."""
    decision = ScriptedApproval.always_approve().decide(make_request())

    assert (decision.run_id, decision.seed, decision.config_hash) == (
        RUN_ID,
        SEED,
        CONFIG_HASH,
    )
    assert decision.node_id == "node-1"
    assert decision.level == 4


def test_approve_after_reports_the_delay_without_sleeping() -> None:
    decision = ScriptedApproval.approve_after(30.0).decide(make_request(sim_time=100.0))

    assert decision.approved is True
    assert decision.delay_sim == pytest.approx(30.0)
    assert decision.sim_time == pytest.approx(100.0)
    assert decision.decided_at_sim == pytest.approx(130.0)


def test_deny_after_reports_the_delay() -> None:
    decision = ScriptedApproval.deny_after(12.5).decide(make_request(sim_time=40.0))

    assert decision.approved is False
    assert decision.decided_at_sim == pytest.approx(52.5)


def test_zero_delay_decides_at_the_escalation_time() -> None:
    decision = ScriptedApproval.always_approve().decide(make_request(sim_time=9.0))
    assert decision.decided_at_sim == pytest.approx(9.0)


def test_a_scripted_run_completes_instantly() -> None:
    """
    Never-blocks, stated as an executable claim: a headless sweep issuing 2000 escalations must
    return, not hang like interrupt() would.
    """
    policy = ScriptedApproval.approve_after(3600.0)
    for i in range(2000):
        policy.decide(make_request(sim_time=float(i)))
    assert len(policy.decisions) == 2000


def test_negative_delay_is_rejected() -> None:
    """A decision landing before its escalation makes latency negative."""
    with pytest.raises(ValueError):
        ScriptedStep(approved=True, delay_sim=-1.0)

    with pytest.raises(ValueError):
        ScriptedApproval.deny_after(-5.0)


def test_sequence_is_consumed_in_order() -> None:
    policy = ScriptedApproval.sequence([True, False, True])
    got = [policy.decide(make_request()).approved for _ in range(3)]
    assert got == [True, False, True]


def test_sequence_accepts_steps_with_per_escalation_delays() -> None:
    policy = ScriptedApproval.sequence(
        [
            ScriptedStep(approved=False, delay_sim=5.0, reason="looks like a false positive"),
            ScriptedStep(approved=True, delay_sim=1.0, reason="confirmed"),
        ]
    )
    first = policy.decide(make_request(sim_time=10.0))
    second = policy.decide(make_request(sim_time=20.0))

    assert (first.approved, first.decided_at_sim) == (False, 15.0)
    assert (second.approved, second.decided_at_sim) == (True, 21.0)
    assert first.reason == "looks like a false positive"


def test_exhausted_sequence_repeats_the_last_step() -> None:
    """A scenario cannot predict how many escalations it will produce."""
    policy = ScriptedApproval.sequence([True, False])
    got = [policy.decide(make_request()).approved for _ in range(5)]
    assert got == [True, False, False, False, False]


def test_strict_sequence_raises_when_exhausted() -> None:
    policy = ScriptedApproval.sequence([True], strict=True)
    policy.decide(make_request())
    with pytest.raises(ApprovalError, match="script exhausted"):
        policy.decide(make_request())


def test_empty_script_is_rejected_at_construction() -> None:
    with pytest.raises(ApprovalError, match="at least one step"):
        ScriptedApproval([])

    with pytest.raises(ApprovalError, match="at least one step"):
        ScriptedApproval.sequence([])


def test_two_identical_scripted_runs_produce_identical_decisions() -> None:
    def run() -> list[str]:
        policy = ScriptedApproval.sequence(
            [
                ScriptedStep(approved=True, delay_sim=2.0),
                ScriptedStep(approved=False, delay_sim=7.5, reason="denied"),
            ]
        )
        return [
            policy.decide(make_request(sim_time=float(i), node_id=f"n{i}")).model_dump_json()
            for i in range(6)
        ]

    assert run() == run()


def test_the_gate_is_deterministic_across_repeats() -> None:
    def run() -> list[str]:
        gate = ApprovalGate(ScriptedApproval.deny_after(4.0))
        return [
            gate.review_plan(make_plan(level=lvl, sim_time=float(lvl))).model_dump_json()
            for lvl in (0, 1, 2, 3, 4, 4)
        ]

    assert run() == run()


def test_policy_records_the_full_escalation_trail() -> None:
    policy = ScriptedApproval.always_deny()
    policy.decide(make_request(node_id="a"))
    policy.decide(make_request(node_id="b"))

    assert [r.node_id for r in policy.requests] == ["a", "b"]
    assert [d.node_id for d in policy.decisions] == ["a", "b"]


def test_requires_approval_is_true_only_at_level_4() -> None:
    assert [requires_approval(lvl) for lvl in range(5)] == [False, False, False, False, True]
    assert APPROVAL_REQUIRED_LEVEL == 4


@pytest.mark.parametrize("level", [-1, 5, 99])
def test_requires_approval_rejects_out_of_range_levels(level: int) -> None:
    with pytest.raises(ApprovalError, match=r"level must be in \[0, 4\]"):
        requires_approval(level)


@pytest.mark.parametrize("level", ["4", 4.0, None, True])
def test_requires_approval_rejects_non_int_levels(level: object) -> None:
    with pytest.raises(ApprovalError, match="must be an int"):
        requires_approval(level)  # type: ignore[arg-type]


@pytest.mark.parametrize("level", [-1, 5])
def test_request_rejects_out_of_range_levels(level: int) -> None:
    with pytest.raises(ValueError):
        make_request(level=level)


@pytest.mark.parametrize("level", [0, 1, 2, 3])
def test_sub_l4_levels_never_reach_the_policy(level: int) -> None:
    policy = ScriptedApproval.always_deny()
    gate = ApprovalGate(policy)

    decision = gate.review(make_request(level=level))

    assert decision.approved is True, "a deny-everything operator must not block L0-L3"
    assert decision.required is False
    assert decision.decider is DeciderKind.AUTOMATIC
    assert policy.requests == [], "the policy must not have been consulted"


def test_l4_reaches_the_policy_and_can_be_denied() -> None:
    policy = ScriptedApproval.always_deny()
    gate = ApprovalGate(policy)

    decision = gate.review(make_request(level=4))

    assert decision.approved is False
    assert decision.required is True
    assert decision.decider is DeciderKind.SCRIPTED
    assert len(policy.requests) == 1


def test_gate_decides_every_level_but_retains_only_escalations() -> None:
    """No silent holes: L0-L3 still produce a decision."""
    gate = ApprovalGate(ScriptedApproval.always_approve())
    decided = [gate.review(make_request(level=lvl)) for lvl in (0, 2, 4, 3, 4)]

    assert [d.level for d in decided] == [0, 2, 4, 3, 4]
    assert [d.level for d in gate.decisions] == [4, 4]
    assert [d.level for d in gate.escalations] == [4, 4]


def test_review_plan_lifts_a_response_plan() -> None:
    gate = ApprovalGate(ScriptedApproval.always_deny())
    decision = gate.review_plan(make_plan(level=4, sim_time=55.0))

    assert decision.approved is False
    assert decision.node_id == "node-1"
    assert decision.level == 4
    assert decision.sim_time == pytest.approx(55.0)
    assert decision.run_id == RUN_ID


def test_request_from_plan_preserves_identity_and_rationale() -> None:
    request = ApprovalRequest.from_plan(make_plan(level=3), campaign_id="camp-1")

    assert request.level == 3
    assert request.rationale == "GT below isolation threshold"
    assert request.campaign_id == "camp-1"
    assert (request.run_id, request.seed, request.config_hash) == (RUN_ID, SEED, CONFIG_HASH)


def test_models_forbid_extra_fields() -> None:
    with pytest.raises(ValueError):
        ApprovalRequest(
            sim_time=0.0,
            run_id=RUN_ID,
            seed=SEED,
            config_hash=CONFIG_HASH,
            node_id="n",
            level=4,
            typo_field=1,  # type: ignore[call-arg]
        )


def test_decision_rejects_a_negative_delay() -> None:
    with pytest.raises(ValueError):
        ApprovalDecision(
            sim_time=0.0,
            run_id=RUN_ID,
            seed=SEED,
            config_hash=CONFIG_HASH,
            node_id="n",
            level=4,
            approved=True,
            decided_by="x",
            decider=DeciderKind.SCRIPTED,
            delay_sim=-0.1,
        )


def test_decision_flattens_into_an_audit_record() -> None:
    decision = ScriptedApproval.deny_after(6.0).decide(make_request(sim_time=20.0))
    record = decision.as_audit_record()

    assert record.event_type == "approval.decision"
    assert record.actor_id == "scripted:deny_after"
    assert record.sim_time == pytest.approx(20.0)
    assert record.payload["approved"] is False
    assert record.payload["decided_at_sim"] == pytest.approx(26.0)
    assert record.payload["level"] == 4


def test_module_exposes_the_availability_flag() -> None:
    assert isinstance(approval_module.LANGGRAPH_AVAILABLE, bool)


def test_scripted_path_works_regardless_of_langgraph(monkeypatch: pytest.MonkeyPatch) -> None:
    """The deterministic path must not touch the optional dependency at all."""
    monkeypatch.setattr(approval_module, "LANGGRAPH_AVAILABLE", False)
    monkeypatch.setattr(approval_module, "_INTERRUPT", None)

    decision = ScriptedApproval.always_approve().decide(make_request())
    assert decision.approved is True
    assert ApprovalGate(ScriptedApproval.always_deny()).review(make_request()).denied


def _import_without_langgraph() -> Any:
    """
    Execute agents/approval.py a second time with every `langgraph` import failing, as it would on a
    machine that skipped the optional extra.
    """
    import builtins
    import importlib.util
    import sys

    real_import = builtins.__import__
    name = "agents._approval_no_langgraph"

    def blocked(name: str, *args: Any, **kwargs: Any) -> Any:
        if name.split(".")[0] == "langgraph":
            raise ModuleNotFoundError(f"No module named {name!r}")
        return real_import(name, *args, **kwargs)

    spec = importlib.util.spec_from_file_location(name, approval_module.__file__)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)

    builtins.__import__ = blocked
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        builtins.__import__ = real_import
        sys.modules.pop(name, None)
    return module


def test_module_imports_with_langgraph_absent() -> None:
    isolated = _import_without_langgraph()

    assert isolated.LANGGRAPH_AVAILABLE is False
    assert isolated.ScriptedApproval.always_approve().decide(make_request()).approved
    assert (
        isolated.ApprovalGate(isolated.ScriptedApproval.always_deny())
        .review(make_request(level=4))
        .approved
        is False
    )


def test_human_approval_in_a_langgraph_free_install_raises_actionably() -> None:
    isolated = _import_without_langgraph()

    with pytest.raises(isolated.ApprovalError, match=r"pip install -e \"\.\[agents\]\""):
        isolated.HumanApproval()


def test_human_approval_without_langgraph_raises_an_actionable_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(approval_module, "LANGGRAPH_AVAILABLE", False)
    monkeypatch.setattr(approval_module, "_INTERRUPT", None)

    with pytest.raises(ApprovalError) as exc:
        approval_module.HumanApproval()

    message = str(exc.value)
    assert "LangGraph" in message
    assert 'pip install -e ".[agents]"' in message
    assert "ScriptedApproval" in message, "the error should name the headless alternative"


def test_human_approval_accepts_a_bare_bool_response() -> None:
    policy = HumanApproval(interrupt_fn=lambda payload: True, operator_id="alice")
    decision = policy.decide(make_request())

    assert decision.approved is True
    assert decision.decided_by == "alice"
    assert decision.decider is DeciderKind.HUMAN


def test_human_approval_accepts_a_mapping_response() -> None:
    policy = HumanApproval(
        interrupt_fn=lambda payload: {
            "approved": False,
            "reason": "false positive, node is fine",
            "delay_sim": 45.0,
        }
    )
    decision = policy.decide(make_request(sim_time=10.0))

    assert decision.approved is False
    assert decision.reason == "false positive, node is fine"
    assert decision.decided_at_sim == pytest.approx(55.0)


def test_human_approval_charges_a_default_think_time() -> None:
    policy = HumanApproval(interrupt_fn=lambda payload: True, default_delay_sim=20.0)
    assert policy.decide(make_request(sim_time=1.0)).decided_at_sim == pytest.approx(21.0)


def test_human_approval_sees_the_escalation_payload() -> None:
    seen: list[dict[str, Any]] = []

    def capture(payload: dict[str, Any]) -> bool:
        seen.append(payload)
        return True

    HumanApproval(interrupt_fn=capture).decide(make_request(sim_time=8.0))

    assert seen[0]["node_id"] == "node-1"
    assert seen[0]["level"] == 4
    assert seen[0]["sim_time"] == 8.0
    assert seen[0]["run_id"] == RUN_ID


@pytest.mark.parametrize("raw", [None, "yes", 1, [], {"reason": "no approved key"}])
def test_malformed_operator_response_raises_rather_than_guessing(raw: object) -> None:
    """
    Defaulting to approve would isolate a node nobody signed off on; defaulting to deny would
    silently discard a real approval.
    """
    policy = HumanApproval(interrupt_fn=lambda payload: raw)
    with pytest.raises(ApprovalError):
        policy.decide(make_request())


def test_operator_response_with_a_negative_delay_is_rejected() -> None:
    policy = HumanApproval(interrupt_fn=lambda payload: {"approved": True, "delay_sim": -2.0})
    with pytest.raises(ApprovalError, match=">= 0"):
        policy.decide(make_request())


def test_human_approval_rejects_a_negative_default_delay() -> None:
    with pytest.raises(ApprovalError, match="must be >= 0"):
        HumanApproval(interrupt_fn=lambda payload: True, default_delay_sim=-1.0)


def test_gate_works_with_a_human_policy_too() -> None:
    """The gate is policy-agnostic: same L4 rule, either operator."""
    gate = ApprovalGate(HumanApproval(interrupt_fn=lambda payload: False))

    assert gate.review(make_request(level=3)).approved is True
    assert gate.review(make_request(level=4)).approved is False
