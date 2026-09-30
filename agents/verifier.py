"""Verifier / guard agent: deterministic rules and statistical checks, never an LLM."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from agents.approval import ApprovalDecision, requires_approval
from m4_response_engine.levels import level_for_gt
from shared.schemas import (
    Classification,
    CorrelationResult,
    GlobalTrustUpdate,
    MessageBase,
    ResponsePlan,
)

ACTOR_ID = "verifier"
VERIFIER_TOPIC = "verifier.report"


class Verdict(StrEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class Finding(BaseModel):
    """One rule that fired."""

    model_config = ConfigDict(extra="forbid")

    code: str
    severity: Verdict
    node_id: str | None = None
    detail: str


class VerifierReport(MessageBase):
    verdict: Verdict
    findings: list[Finding] = Field(default_factory=list)
    plans_checked: int = 0
    _index: Any = PrivateAttr(default=None)

    @property
    def failed(self) -> bool:
        return self.verdict is Verdict.FAIL

    def codes(self) -> list[str]:
        return [f.code for f in self.findings]

    @property
    def blocked_fraction(self) -> float:
        """Share of audited plans this report refuses."""
        if self.plans_checked <= 0:
            return 0.0
        blocked = {f.node_id for f in self.findings if f.severity is Verdict.FAIL and f.node_id}
        tick_wide = any(f.severity is Verdict.FAIL and f.node_id is None for f in self.findings)
        return 1.0 if tick_wide else len(blocked) / self.plans_checked

    def _indexed(self) -> tuple[dict[str | None, list[tuple[int, Finding]]], set[str | None]]:
        """Findings by device, rebuilt only when the list changes."""
        key = (id(self.findings), len(self.findings))
        if self._index is None or self._index[0] != key:
            by_node: dict[str | None, list[tuple[int, Finding]]] = {}
            failing: set[str | None] = set()
            for position, f in enumerate(self.findings):
                by_node.setdefault(f.node_id, []).append((position, f))
                if f.severity is Verdict.FAIL:
                    failing.add(f.node_id)
            self._index = (key, by_node, failing)
        return self._index[1], self._index[2]

    def findings_for(self, node_id: str) -> list[Finding]:
        """Findings about `node_id` and tick-wide ones, in report order."""
        by_node, _ = self._indexed()
        both = by_node.get(None, []) + by_node.get(node_id, [])
        return [f for _, f in sorted(both, key=lambda pair: pair[0])]

    def blocks(self, node_id: str) -> bool:
        """True if a FAIL finding forbids acting on `node_id`."""
        _, failing = self._indexed()
        return None in failing or node_id in failing


class VerifierParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    high_severity: float = Field(default=0.6, ge=0.0, le=1.0)
    cti_tolerance: float = Field(default=1e-6, ge=0.0)
    always_check_at_or_above: int = Field(default=3, ge=0, le=4)
    sample_every: int = Field(default=5, ge=0)


class VerifierAgent:
    """Audits one tick's reasoning-plane output."""

    def __init__(
        self,
        params: VerifierParams | None = None,
        *,
        correlator: Any | None = None,
    ) -> None:
        self.params = params or VerifierParams()
        self.correlator = correlator
        self._ticks_seen = 0

    def audit(
        self,
        *,
        plans: list[ResponsePlan],
        gt_updates: list[GlobalTrustUpdate],
        correlation: CorrelationResult | None = None,
        classification: Classification | None = None,
        approvals: dict[str, ApprovalDecision] | None = None,
        batch: Any | None = None,
    ) -> VerifierReport:
        if not plans:
            raise ValueError("cannot audit an empty plan set")
        self._ticks_seen += 1

        gt_by_node = {u.node_id: u for u in gt_updates}
        approvals = approvals or {}
        findings: list[Finding] = []

        anchor = plans[0]
        findings += self._check_run_identity(plans, gt_updates, correlation, classification)

        for plan in plans:
            findings += self._check_plan(plan, gt_by_node, approvals)

        if classification is not None and correlation is not None:
            findings += self._check_classification(classification, correlation)

        if batch is not None and correlation is not None:
            findings += self._check_correlation(batch, correlation, plans)

        if correlation is not None and correlation.outlier_agent_ids:
            findings.append(
                Finding(
                    code="reporter_integrity_failed",
                    severity=Verdict.WARN,
                    detail=(
                        f"{len(correlation.outlier_agent_ids)} reporter(s) failed the "
                        f"integrity check: {', '.join(correlation.outlier_agent_ids[:5])}"
                    ),
                )
            )

        return VerifierReport(
            sim_time=anchor.sim_time,
            run_id=anchor.run_id,
            seed=anchor.seed,
            config_hash=anchor.config_hash,
            verdict=_worst([f.severity for f in findings]),
            findings=findings,
            plans_checked=len(plans),
        )

    def _check_plan(
        self,
        plan: ResponsePlan,
        gt_by_node: dict[str, GlobalTrustUpdate],
        approvals: dict[str, ApprovalDecision],
    ) -> list[Finding]:
        out: list[Finding] = []
        gt_update = gt_by_node.get(plan.node_id)

        if gt_update is None:
            out.append(
                Finding(
                    code="unknown_target",
                    severity=Verdict.FAIL,
                    node_id=plan.node_id,
                    detail="plan targets a node with no Global Trust for this tick",
                )
            )
        else:
            raw = int(level_for_gt(gt_update.gt))
            if plan.proposed_level < raw:
                out.append(
                    Finding(
                        code="under_response",
                        severity=Verdict.FAIL,
                        node_id=plan.node_id,
                        detail=(
                            f"proposed L{plan.proposed_level} but GT {gt_update.gt:.3f} "
                            f"warrants L{raw}; hysteresis may hold a level higher, never lower"
                        ),
                    )
                )
            elif plan.proposed_level > raw:
                out.append(
                    Finding(
                        code="level_held_above_formula",
                        severity=Verdict.WARN,
                        node_id=plan.node_id,
                        detail=(
                            f"proposed L{plan.proposed_level} above formula L{raw} "
                            f"(GT {gt_update.gt:.3f}), expected while hysteresis damps"
                        ),
                    )
                )

        if requires_approval(plan.proposed_level):
            decision = approvals.get(plan.node_id)
            if decision is None:
                out.append(
                    Finding(
                        code="l4_without_approval",
                        severity=Verdict.WARN,
                        node_id=plan.node_id,
                        detail="isolation planned with no approval decision attached",
                    )
                )
            elif not decision.approved:
                out.append(
                    Finding(
                        code="l4_denied",
                        severity=Verdict.WARN,
                        node_id=plan.node_id,
                        detail=f"isolation denied by {decision.decided_by}: {decision.reason}",
                    )
                )
        return out

    def _should_recheck_correlation(self, plans: list[ResponsePlan]) -> bool:
        if self.correlator is None:
            return False
        worst = max((p.proposed_level for p in plans), default=0)
        if worst >= self.params.always_check_at_or_above:
            return True
        if self.params.sample_every <= 0:
            return False
        return self._ticks_seen % self.params.sample_every == 0

    def _check_correlation(
        self,
        batch: Any,
        correlation: CorrelationResult,
        plans: list[ResponsePlan],
    ) -> list[Finding]:
        """Recompute the campaign score and implication set from the batch."""
        if not self._should_recheck_correlation(plans):
            return []

        try:
            recomputed = self.correlator.correlate(batch)
        except Exception as exc:  # noqa: BLE001
            return [
                Finding(
                    code="correlation_recheck_failed",
                    severity=Verdict.WARN,
                    detail=f"could not recompute correlation: {type(exc).__name__}: {exc}",
                )
            ]

        out: list[Finding] = []
        expected = recomputed.cti
        if correlation.cti - expected > self.params.cti_tolerance:
            out.append(
                Finding(
                    code="cti_inflated",
                    severity=Verdict.WARN,
                    detail=(
                        f"published CTI {correlation.cti:.6f} exceeds the value "
                        f"recomputed from the batch ({expected:.6f}) by more than "
                        f"tolerance"
                    ),
                )
            )

        fabricated = sorted(
            set(correlation.implicated_node_ids) - set(recomputed.implicated_node_ids)
        )
        if fabricated:
            out.append(
                Finding(
                    code="implication_fabricated",
                    severity=Verdict.WARN,
                    detail=(
                        f"{len(fabricated)} node(s) implicated that the batch does "
                        f"not support: {', '.join(fabricated[:5])}"
                    ),
                )
            )
        return out

    def _check_classification(
        self, classification: Classification, correlation: CorrelationResult
    ) -> list[Finding]:
        out: list[Finding] = []
        implicated = len(correlation.implicated_node_ids)

        if classification.severity >= self.params.high_severity and implicated == 0:
            out.append(
                Finding(
                    code="severity_without_evidence",
                    severity=Verdict.WARN,
                    detail=(
                        f"severity {classification.severity:.2f} but correlation "
                        f"implicated no nodes (CTI {correlation.cti:.3f})"
                    ),
                )
            )
        if classification.threat_type == "none" and implicated > 0:
            out.append(
                Finding(
                    code="evidence_without_classification",
                    severity=Verdict.WARN,
                    detail=(
                        f"{implicated} node(s) implicated but classified 'none' "
                        f"(CTI {correlation.cti:.3f})"
                    ),
                )
            )
        return out

    def _check_run_identity(
        self,
        plans: list[ResponsePlan],
        gt_updates: list[GlobalTrustUpdate],
        correlation: CorrelationResult | None,
        classification: Classification | None,
    ) -> list[Finding]:
        anchor = plans[0]
        expected = (anchor.run_id, anchor.seed, anchor.config_hash)

        others: list[MessageBase] = [*plans[1:], *gt_updates]
        if correlation is not None:
            others.append(correlation)
        if classification is not None:
            others.append(classification)

        for msg in others:
            if (msg.run_id, msg.seed, msg.config_hash) != expected:
                return [
                    Finding(
                        code="run_identity_mismatch",
                        severity=Verdict.FAIL,
                        detail=(
                            f"{type(msg).__name__} carries "
                            f"({msg.run_id}, {msg.seed}, {msg.config_hash}) "
                            f"but plans carry {expected}"
                        ),
                    )
                ]
        return []


def _worst(severities: list[Verdict]) -> Verdict:
    if Verdict.FAIL in severities:
        return Verdict.FAIL
    if Verdict.WARN in severities:
        return Verdict.WARN
    return Verdict.PASS
