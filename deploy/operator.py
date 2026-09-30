"""
The operator at the console, over the broker: isolation and memory adjudication in the container
deployment.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from console.stream import DECISION_TOPIC, QUESTION_TOPIC
from shared.attestation import decision_payload
from shared.schemas import (
    AdjudicationQuestion,
    AdjudicationVerdict,
    OperatorDecision,
    OperatorQuestion,
)

CONSOLE = "console"


@dataclass
class BrokerApproval:
    """An `ApprovalPolicy` answered by a person at the console, across processes."""

    bus: Any
    console_key: Any
    gate: Any = None
    pending: dict[str, OperatorQuestion] = field(default_factory=dict)
    answers: dict[str, tuple[bool, str, str]] = field(default_factory=dict)
    asked: int = 0
    accepted: int = 0
    refused: Counter[str] = field(default_factory=Counter)

    def __post_init__(self) -> None:
        self.bus.discover = False
        self.bus.subscribe(DECISION_TOPIC, self._decision)
        self.bus.follow(DECISION_TOPIC, CONSOLE)

    def decide(self, request: Any) -> Any:
        from agents.approval import ApprovalDecision, DeciderKind

        answer = self.answers.pop(request.node_id, None)
        if answer is None:
            if request.node_id not in self.pending:
                question = OperatorQuestion(
                    sim_time=request.sim_time,
                    run_id=request.run_id,
                    seed=request.seed,
                    config_hash=request.config_hash,
                    node_id=request.node_id,
                    level=request.level,
                    rationale=request.rationale[:4096],
                )
                self.pending[request.node_id] = question
                self.bus.publish(QUESTION_TOPIC, question)
                self.asked += 1
            approved, reason, by = False, "awaiting an operator: isolation withheld", CONSOLE
        else:
            approved, reason, by = answer
        return ApprovalDecision(
            sim_time=request.sim_time,
            run_id=request.run_id,
            seed=request.seed,
            config_hash=request.config_hash,
            node_id=request.node_id,
            level=request.level,
            approved=approved,
            reason=reason,
            decided_by=by,
            decider=DeciderKind.HUMAN,
            delay_sim=0.0,
        )

    def poll(self) -> None:
        """Read the console's answers; withdraw questions whose episode has ended."""
        self.bus.pump(timeout=0)
        if self.gate is None:
            return
        for node_id in [n for n in self.pending if not self.gate.is_open(n)]:
            self._close(node_id)

    def _decision(self, message: Any) -> None:
        if not isinstance(message, OperatorDecision):
            return
        question = self.pending.get(message.node_id)
        if question is None:
            self.refused["no_open_question"] += 1
            return
        if message.sim_time != question.sim_time or message.run_id != question.run_id:
            self.refused["another_episode"] += 1
            return
        payload = decision_payload(
            message.run_id,
            message.node_id,
            message.sim_time,
            message.approved,
            message.reason,
            message.decided_by,
        )
        if not self.console_key.verify(payload, message.signature):
            self.refused["bad_signature"] += 1
            return
        self.accepted += 1
        self.answers[message.node_id] = (message.approved, message.reason, message.decided_by)
        self._close(message.node_id)
        if self.gate is not None:
            self.gate.reconsider(message.node_id)

    def _close(self, node_id: str) -> None:
        question = self.pending.pop(node_id)
        self.bus.publish(QUESTION_TOPIC, question.model_copy(update={"open": False}))


@dataclass
class BrokerAdjudicator:
    """
    The deployment's adjudicator: the memory service records a person's verdict only under the
    console's signature.
    """

    bus: Any
    memory: Any
    actor_id: str = CONSOLE
    delay_sim: float = 0.0
    pending: dict[str, AdjudicationQuestion] = field(default_factory=dict)
    asked: int = 0
    applied: int = 0
    refused: Counter[str] = field(default_factory=Counter)
    _now: float = 0.0

    def __post_init__(self) -> None:
        self.bus.discover = False
        self.bus.subscribe(DECISION_TOPIC, self._verdict)
        self.bus.follow(DECISION_TOPIC, CONSOLE)

    def ask(self, record: Any, *, sim_time: float) -> None:
        question = AdjudicationQuestion(
            sim_time=sim_time,
            run_id=record.run_id,
            seed=record.seed,
            config_hash=record.config_hash,
            record_id=record.record_id,
            threat_type=record.threat_type,
            node_ids=list(record.node_ids),
            window_start_sim=record.window_start_sim,
            window_end_sim=record.window_end_sim,
            pattern_text=record.pattern_text,
        )
        self.pending[record.record_id] = question
        self.bus.publish(QUESTION_TOPIC, question)
        self.asked += 1

    def adjudicate(self, record: Any) -> str | None:
        """Nothing to apply at the due time: verdicts are applied as they arrive."""
        return None

    def poll(self, now: float) -> None:
        """Read the console's verdicts and relay each to the memory service."""
        self._now = now
        self.bus.pump(timeout=0)

    def _verdict(self, message: Any) -> None:
        if not isinstance(message, AdjudicationVerdict):
            return
        question = self.pending.get(message.record_id)
        if question is None:
            self.refused["no_open_question"] += 1
            return
        if message.sim_time != question.sim_time or message.run_id != question.run_id:
            self.refused["another_question"] += 1
            return
        outcome = self.memory.adjudicate(message, sim_time=max(self._now, question.sim_time))
        if not outcome.get("allowed"):
            self.refused[str(outcome.get("reason"))] += 1
            return
        self.applied += 1
        del self.pending[message.record_id]
        self.bus.publish(
            QUESTION_TOPIC,
            question.model_copy(
                update={"open": False, "status": message.status, "decided_by": message.decided_by}
            ),
        )
