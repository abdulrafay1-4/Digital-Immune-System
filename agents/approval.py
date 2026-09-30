"""The Level 4 human-in-the-loop gate, as a swappable policy."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from shared.schemas import AuditRecord, FreeText, Identifier, MessageBase, ResponsePlan

MAX_REASON_CHARS = 4096

_INTERRUPT: Any
try:  # pragma: no cover
    from langgraph.types import interrupt as _INTERRUPT

    LANGGRAPH_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover
    _INTERRUPT = None
    LANGGRAPH_AVAILABLE = False


APPROVAL_REQUIRED_LEVEL = 4

MIN_LEVEL = 0
MAX_LEVEL = 4


class ApprovalError(RuntimeError):
    """Misconfiguration or an unusable operator response."""


class DeciderKind(StrEnum):
    """Who produced a decision."""

    HUMAN = "human"
    SCRIPTED = "scripted"
    AUTOMATIC = "automatic"


def requires_approval(level: int) -> bool:
    """Whether `level` needs human sign-off."""
    _check_level(level)
    return level >= APPROVAL_REQUIRED_LEVEL


def _check_level(level: int) -> None:
    if not isinstance(level, int) or isinstance(level, bool):
        raise ApprovalError(f"level must be an int, got {type(level).__name__}")
    if not MIN_LEVEL <= level <= MAX_LEVEL:
        raise ApprovalError(f"level must be in [{MIN_LEVEL}, {MAX_LEVEL}], got {level}")


class ApprovalRequest(MessageBase):
    """An escalation put to the operator."""

    node_id: Identifier
    level: int = Field(ge=MIN_LEVEL, le=MAX_LEVEL)
    rationale: FreeText = ""
    campaign_id: Identifier | None = None

    @classmethod
    def from_plan(cls, plan: ResponsePlan, *, campaign_id: str | None = None) -> ApprovalRequest:
        """Lift a planner output into an escalation, preserving run identity."""
        return cls(
            sim_time=plan.sim_time,
            run_id=plan.run_id,
            seed=plan.seed,
            config_hash=plan.config_hash,
            node_id=plan.node_id,
            level=plan.proposed_level,
            rationale=plan.rationale,
            campaign_id=campaign_id,
        )


class ApprovalDecision(MessageBase):
    """The answer, and everything the audit trail needs about it."""

    node_id: Identifier
    level: int = Field(ge=MIN_LEVEL, le=MAX_LEVEL)
    approved: bool
    reason: FreeText = ""
    decided_by: Identifier
    decider: DeciderKind
    delay_sim: float = Field(ge=0.0, default=0.0)
    required: bool = True
    signature: str = ""

    @property
    def decided_at_sim(self) -> float:
        """When the action may actually be executed."""
        return self.sim_time + self.delay_sim

    @property
    def denied(self) -> bool:
        return not self.approved

    def as_audit_record(self) -> AuditRecord:
        """Flatten into the project's common audit shape."""
        return AuditRecord(
            sim_time=self.sim_time,
            run_id=self.run_id,
            seed=self.seed,
            config_hash=self.config_hash,
            event_type="approval.decision",
            actor_id=self.decided_by,
            payload={
                "node_id": self.node_id,
                "level": self.level,
                "approved": self.approved,
                "reason": self.reason,
                "decider": str(self.decider),
                "delay_sim": self.delay_sim,
                "decided_at_sim": self.decided_at_sim,
                "required": self.required,
            },
        )


class ApprovalPolicy(Protocol):
    """What M4 calls instead of `interrupt()`."""

    def decide(self, request: ApprovalRequest) -> ApprovalDecision: ...


class ScriptedStep(BaseModel):
    """One pre-programmed operator answer."""

    model_config = ConfigDict(extra="forbid")

    approved: bool
    delay_sim: float = Field(ge=0.0, default=0.0)
    reason: FreeText = ""


class ScriptedApproval:
    """Deterministic, non-blocking operator for headless evaluation."""

    def __init__(
        self,
        steps: Sequence[ScriptedStep],
        *,
        label: str = "scripted",
        strict: bool = False,
    ) -> None:
        if not steps:
            raise ApprovalError("ScriptedApproval needs at least one step")
        self._steps = list(steps)
        self.label = label
        self.strict = strict
        self.requests: list[ApprovalRequest] = []
        self.decisions: list[ApprovalDecision] = []

    @classmethod
    def always_approve(cls, *, delay_sim: float = 0.0, reason: str = "") -> ScriptedApproval:
        return cls(
            [ScriptedStep(approved=True, delay_sim=delay_sim, reason=reason)],
            label="scripted:always_approve",
        )

    @classmethod
    def always_deny(cls, *, delay_sim: float = 0.0, reason: str = "") -> ScriptedApproval:
        return cls(
            [ScriptedStep(approved=False, delay_sim=delay_sim, reason=reason)],
            label="scripted:always_deny",
        )

    @classmethod
    def approve_after(cls, delay_sim: float, *, reason: str = "") -> ScriptedApproval:
        """Approve, but only after `delay_sim` sim-seconds of operator latency."""
        return cls(
            [ScriptedStep(approved=True, delay_sim=delay_sim, reason=reason)],
            label="scripted:approve_after",
        )

    @classmethod
    def deny_after(cls, delay_sim: float, *, reason: str = "") -> ScriptedApproval:
        return cls(
            [ScriptedStep(approved=False, delay_sim=delay_sim, reason=reason)],
            label="scripted:deny_after",
        )

    @classmethod
    def sequence(
        cls,
        steps: Sequence[ScriptedStep | bool],
        *,
        strict: bool = False,
    ) -> ScriptedApproval:
        """A per-escalation script."""
        coerced = [ScriptedStep(approved=s) if isinstance(s, bool) else s for s in steps]
        return cls(coerced, label="scripted:sequence", strict=strict)

    def decide(self, request: ApprovalRequest) -> ApprovalDecision:
        index = len(self.requests)
        self.requests.append(request)

        if index >= len(self._steps):
            if self.strict:
                raise ApprovalError(
                    f"{self.label} script exhausted: {len(self._steps)} step(s) "
                    f"but escalation #{index + 1} was requested"
                )
            step = self._steps[-1]
        else:
            step = self._steps[index]

        decision = ApprovalDecision(
            sim_time=request.sim_time,
            run_id=request.run_id,
            seed=request.seed,
            config_hash=request.config_hash,
            node_id=request.node_id,
            level=request.level,
            approved=step.approved,
            reason=step.reason or ("scripted approve" if step.approved else "scripted deny"),
            decided_by=self.label,
            decider=DeciderKind.SCRIPTED,
            delay_sim=step.delay_sim,
        )
        self.decisions.append(decision)
        return decision


class HumanApproval:
    """Real human-in-the-loop via LangGraph's `interrupt()`."""

    def __init__(
        self,
        *,
        operator_id: str = "human-operator",
        default_delay_sim: float = 0.0,
        interrupt_fn: Any | None = None,
    ) -> None:
        """
        `interrupt_fn` overrides the LangGraph import: used by tests, and by a front-end that
        prompts an operator without a graph.
        """
        if default_delay_sim < 0:
            raise ApprovalError("default_delay_sim must be >= 0")

        if interrupt_fn is None:
            if not LANGGRAPH_AVAILABLE or _INTERRUPT is None:
                raise ApprovalError(
                    "HumanApproval needs LangGraph, which is an optional extra. "
                    'Install it with: pip install -e ".[agents]", or use '
                    "ScriptedApproval for headless evaluation runs."
                )
            interrupt_fn = _INTERRUPT

        self._interrupt: Any = interrupt_fn
        self.operator_id = operator_id
        self.default_delay_sim = float(default_delay_sim)
        self.requests: list[ApprovalRequest] = []
        self.decisions: list[ApprovalDecision] = []

    def decide(self, request: ApprovalRequest) -> ApprovalDecision:
        self.requests.append(request)

        raw = self._interrupt(
            {
                "kind": "approval_request",
                "node_id": request.node_id,
                "level": request.level,
                "rationale": request.rationale,
                "campaign_id": request.campaign_id,
                "sim_time": request.sim_time,
                "run_id": request.run_id,
            }
        )

        approved, reason, delay = self._parse(raw)
        decision = ApprovalDecision(
            sim_time=request.sim_time,
            run_id=request.run_id,
            seed=request.seed,
            config_hash=request.config_hash,
            node_id=request.node_id,
            level=request.level,
            approved=approved,
            reason=reason,
            decided_by=self.operator_id,
            decider=DeciderKind.HUMAN,
            delay_sim=delay,
        )
        self.decisions.append(decision)
        return decision

    def _parse(self, raw: object) -> tuple[bool, str, float]:
        """Turn a resumed `interrupt()` value into a decision."""
        if isinstance(raw, bool):
            return raw, "operator response", self.default_delay_sim
        if isinstance(raw, Mapping):
            approved = raw.get("approved")
            if not isinstance(approved, bool):
                raise ApprovalError(
                    f"operator response needs a boolean 'approved', got {approved!r}"
                )
            reason = str(raw.get("reason", "operator response"))
            if len(reason) > MAX_REASON_CHARS:
                raise ApprovalError(f"'reason' is limited to {MAX_REASON_CHARS} characters")
            delay_raw = raw.get("delay_sim", self.default_delay_sim)
            if (
                not isinstance(delay_raw, (int, float))
                or isinstance(delay_raw, bool)
                or not math.isfinite(delay_raw)
            ):
                raise ApprovalError(f"'delay_sim' must be a finite number, got {delay_raw!r}")
            if delay_raw < 0:
                raise ApprovalError("'delay_sim' must be >= 0")
            return approved, reason, float(delay_raw)
        raise ApprovalError(
            f"unusable operator response {raw!r}: expected a bool or a mapping "
            "with an 'approved' key"
        )


class ApprovalGate:
    """Applies the L4 rule, then delegates to the installed policy."""

    def __init__(self, policy: ApprovalPolicy) -> None:
        self.policy = policy
        self.decisions: list[ApprovalDecision] = []
        self._standing: dict[str, ApprovalDecision] = {}
        self.standing_reuses = 0
        self._standing_mass: ApprovalDecision | None = None

    @staticmethod
    def _signed(decision: ApprovalDecision) -> ApprovalDecision:
        from shared.integrity import approval_payload, sign
        from shared.keys import derive

        return decision.model_copy(
            update={"signature": sign(approval_payload(decision), derive("approval"))}
        )

    def review_mass_restriction(
        self, *, count: int, budget: int, sim_time: float, run_id: str, seed: int, config_hash: str
    ) -> ApprovalDecision:
        """One question when automatic restriction would exceed the fleet budget."""
        if self._standing_mass is not None:
            self.standing_reuses += 1
            return self._standing_mass
        request = ApprovalRequest(
            sim_time=sim_time,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            node_id="fleet",
            level=MAX_LEVEL,
            rationale=f"automatic restriction of {count} devices exceeds the budget of {budget}",
        )
        decision = self._signed(self.policy.decide(request))
        self._standing_mass = decision
        self.decisions.append(decision)
        return decision

    def clear_mass_restriction(self) -> None:
        self._standing_mass = None

    def reconsider(self, node_id: str) -> None:
        """Drop a device's standing decision so the operator is asked again."""
        self._standing.pop(node_id, None)

    def is_open(self, node_id: str) -> bool:
        """Whether the question for a device (or ``"fleet"``) belongs to a live episode."""
        if node_id == "fleet":
            return self._standing_mass is not None
        return node_id in self._standing

    def review(self, request: ApprovalRequest) -> ApprovalDecision:
        if requires_approval(request.level):
            standing = self._standing.get(request.node_id)
            if standing is not None:
                self.standing_reuses += 1
                return standing
            decision = self._signed(self.policy.decide(request))
            self._standing[request.node_id] = decision
            self.decisions.append(decision)
            return decision
        self._standing.pop(request.node_id, None)
        return ApprovalDecision(
            sim_time=request.sim_time,
            run_id=request.run_id,
            seed=request.seed,
            config_hash=request.config_hash,
            node_id=request.node_id,
            level=request.level,
            approved=True,
            reason=f"level {request.level} does not require approval",
            decided_by="approval-gate",
            decider=DeciderKind.AUTOMATIC,
            delay_sim=0.0,
            required=False,
        )

    def review_plan(
        self, plan: ResponsePlan, *, campaign_id: str | None = None
    ) -> ApprovalDecision:
        return self.review(ApprovalRequest.from_plan(plan, campaign_id=campaign_id))

    @property
    def escalations(self) -> list[ApprovalDecision]:
        """Decisions that actually went to the policy."""
        return [d for d in self.decisions if d.required]
