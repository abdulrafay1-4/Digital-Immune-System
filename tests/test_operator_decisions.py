"""The operator at the console deciding an isolation in the container deployment."""

from __future__ import annotations

import pytest

from agents.approval import ApprovalGate, ApprovalRequest
from console.stream import DECISION_TOPIC, StreamFleet
from deploy.operator import BrokerApproval
from m10_persona_drift.nhi import issue_signing_identity
from shared.attestation import decision_payload
from shared.redis_bus import RedisBus
from shared.schemas import OperatorDecision
from tests.test_redis_bus import _Broker, _Client

KEY = issue_signing_identity("console", seed=b"c" * 32)
BASE = {"run_id": "wire", "seed": 7, "config_hash": "h"}


def _deployment(signer=KEY):
    broker = _Broker()
    policy = BrokerApproval(
        RedisBus(_Client(broker), publisher="control"), console_key=KEY.public()
    )
    gate = ApprovalGate(policy)
    policy.gate = gate
    console = StreamFleet(
        RedisBus(_Client(broker), publisher="console"), ["node-1"], run_id="wire", signer=signer
    )
    return broker, policy, gate, console


def _ask(gate, level: int = 4, t: float = 12.0):
    return gate.review(ApprovalRequest(**BASE, sim_time=t, node_id="node-1", level=level))


def test_a_signed_answer_from_the_console_decides_the_isolation() -> None:
    _, policy, gate, console = _deployment()
    assert not _ask(gate).approved, "withheld until someone answers"
    console.step(timeout=0)
    assert list(console.pending) == ["node-1"]
    console.submit(
        "approve", node_id="node-1", approved=True, reason="seen it", user="ana"
    ).result()
    policy.poll()
    decision = _ask(gate)
    assert decision.approved and decision.decided_by == "operator:ana" and decision.signature
    assert policy.accepted == 1 and policy.asked == 1
    console.step(timeout=0)
    assert console.pending == {}, "the answered question is withdrawn"


def _forged(policy, *, key=KEY, sim_time: float = 12.0, node: str = "node-1") -> None:
    payload = decision_payload("wire", node, sim_time, True, "x", "operator:mallory")
    RedisBus(policy.bus.client, publisher="console").publish(
        DECISION_TOPIC,
        OperatorDecision(
            **BASE,
            sim_time=sim_time,
            node_id=node,
            approved=True,
            reason="x",
            decided_by="operator:mallory",
            signature=key.sign(payload),
        ),
    )
    policy.poll()


@pytest.mark.parametrize(
    ("kw", "reason"),
    [
        ({"key": issue_signing_identity("console", seed=b"m" * 32)}, "bad_signature"),
        ({"sim_time": 5.0}, "another_episode"),
        ({"node": "node-2"}, "no_open_question"),
    ],
    ids=["another key", "an earlier episode", "no question asked"],
)
def test_an_answer_that_is_not_the_consoles_for_this_question_is_refused(kw, reason) -> None:
    _, policy, gate, _ = _deployment()
    _ask(gate)
    _forged(policy, **kw)
    assert policy.refused[reason] == 1 and policy.accepted == 0
    assert not _ask(gate).approved


def test_a_question_whose_episode_ended_is_withdrawn() -> None:
    _, policy, gate, console = _deployment()
    _ask(gate)
    console.step(timeout=0)
    assert "node-1" in console.pending
    _ask(gate, level=3, t=13.0)
    policy.poll()
    console.step(timeout=0)
    assert console.pending == {} and policy.pending == {}


def test_a_console_without_the_key_answers_nothing() -> None:
    _, _, gate, console = _deployment(signer=None)
    _ask(gate)
    console.step(timeout=0)
    with pytest.raises(ValueError, match="answers isolation questions"):
        console.submit("approve", node_id="node-1", approved=True, reason="", user="x").result()
