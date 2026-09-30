"""Immune response engine: it derives the level itself, then gates the action."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from m4_response_engine.gate import GateDecision, gate_response_plan
from m4_response_engine.hysteresis import LevelHysteresis
from m4_response_engine.levels import ResponseLevel, level_for_gt
from m9_capability_binder.binder import redeem
from shared.audit import AuditLog
from shared.integrity import DEV_KEY, approval_payload, verify
from shared.keys import derive
from shared.provenance import meets_ceiling
from shared.schemas import AuditRecord, GlobalTrustUpdate, Provenance, ResponsePlan


@runtime_checkable
class Verification(Protocol):
    """What the engine needs from a verifier report."""

    def blocks(self, node_id: str) -> bool: ...


@dataclass
class ExecutionResult:
    executed: bool
    decision: GateDecision | None
    audit: AuditRecord | None = None
    level: ResponseLevel | None = None


@dataclass
class ResponseEngine:
    """Owns level selection, hysteresis, and the capability gate."""

    actor_id: str = "response-engine"
    hysteresis: LevelHysteresis = field(default_factory=LevelHysteresis)
    verify_key: bytes = DEV_KEY
    require_signature: bool = False
    audit: AuditLog = field(default_factory=AuditLog)
    _last_gt: dict[str, GlobalTrustUpdate] = field(default_factory=dict, repr=False)
    fusion_params: Any | None = None
    gt_inconsistent: int = 0
    approval_key: bytes = field(default_factory=lambda: derive("approval"), repr=False)
    _l4_since: dict[str, float] = field(default_factory=dict, repr=False)
    denials: dict[str, int] = field(default_factory=dict)

    def decide(self, gt_update: GlobalTrustUpdate) -> ResponseLevel:
        """Authoritative level for one node this tick."""
        if self.require_signature and not self.gt_is_authentic(gt_update):
            raise ValueError(f"unsigned or altered GlobalTrustUpdate for {gt_update.node_id}")
        gt = gt_update.gt
        if self.fusion_params is not None:
            from m6_trust_fusion.fusion import fuse_gt

            recomputed, _ = fuse_gt(
                ts=gt_update.ts,
                cti_i=gt_update.cti_i,
                rep=gt_update.rep,
                params=self.fusion_params,
                drift_flag=gt_update.drift_flag,
            )
            if abs(recomputed - gt) > 1e-9:
                self.gt_inconsistent += 1
                gt = recomputed
        raw = level_for_gt(gt)
        self._last_gt[gt_update.node_id] = gt_update
        return self.hysteresis.apply(gt_update.node_id, raw)

    def gt_is_authentic(self, gt_update: GlobalTrustUpdate) -> bool:
        """Did M6 produce this exact GT, for this node, on this tick, in this run?"""
        from m6_trust_fusion.fusion import gt_payload

        return verify(
            gt_payload(
                run_id=gt_update.run_id,
                seed=gt_update.seed,
                config_hash=gt_update.config_hash,
                sim_time=gt_update.sim_time,
                node_id=gt_update.node_id,
                gt=gt_update.gt,
                ts=gt_update.ts,
                cti_i=gt_update.cti_i,
                rep=gt_update.rep,
                drift_flag=gt_update.drift_flag,
            ),
            gt_update.signature,
            self.verify_key,
        )

    def effective_level(self, node_id: str) -> ResponseLevel:
        """This node's current enforced level, without advancing anything."""
        return self.hysteresis.state(node_id).effective

    def execute(
        self,
        plan: ResponsePlan,
        *,
        verification: Verification,
        input_provenance: Provenance = Provenance.HIGH,
        approval: Any | None = None,
        restrict_allowed: bool = True,
    ) -> ExecutionResult:
        derived = self.effective_level(plan.node_id)
        if derived >= ResponseLevel.ISOLATE:
            self._l4_since.setdefault(plan.node_id, plan.sim_time)
        else:
            self._l4_since.pop(plan.node_id, None)
        inputs = self._decision_inputs(plan, verification, approval, input_provenance)
        if plan.proposed_level != int(derived):
            return self._deny(
                plan,
                decision=None,
                reason="level_not_derived",
                level=derived,
                extra={
                    "plan_level": plan.proposed_level,
                    "derived_level": int(derived),
                    **inputs,
                },
            )

        if verification.blocks(plan.node_id):
            return self._deny(
                plan, decision=None, reason="verifier_failed", level=derived, extra=inputs
            )

        isolation_approved = (
            derived >= ResponseLevel.ISOLATE
            and meets_ceiling(input_provenance, Provenance.HIGH)
            and _isolation_approved(
                plan, approval, self.approval_key, self._l4_since.get(plan.node_id)
            )
        )
        withheld = derived >= ResponseLevel.ISOLATE and not isolation_approved
        restriction_withheld = (
            derived >= ResponseLevel.RESTRICT and not isolation_approved and not restrict_allowed
        )
        if restriction_withheld:
            enforced_level = ResponseLevel.REAUTH
        elif withheld:
            enforced_level = ResponseLevel.RESTRICT
        else:
            enforced_level = derived
        enforced = (
            plan
            if enforced_level == derived
            else plan.model_copy(update={"proposed_level": int(enforced_level)})
        )

        decision = gate_response_plan(enforced, input_provenance=input_provenance)
        if not decision.allowed or decision.token is None:
            return self._deny(
                plan, decision=decision, reason=decision.deny_reason, level=derived, extra=inputs
            )

        spent, reason = redeem(decision.raw or {}, now_sim=plan.sim_time)
        if not spent:
            return self._deny(plan, decision=decision, reason=reason, level=derived, extra=inputs)

        audit = self._audit(
            plan,
            "response.executed",
            capability=decision.capability,
            token_id=decision.token.token_id,
            isolation_withheld=withheld,
            restriction_withheld=restriction_withheld,
            **inputs,
        )
        return ExecutionResult(
            executed=True,
            decision=decision,
            audit=audit,
            level=enforced_level,
        )

    def _decision_inputs(
        self,
        plan: ResponsePlan,
        verification: Verification,
        approval: Any | None,
        input_provenance: Provenance | str,
    ) -> dict[str, object]:
        """Everything the decision was made from, so the audit trail alone explains it."""
        gt = self._last_gt.get(plan.node_id)
        findings_for = getattr(verification, "findings_for", None)
        relevant = (
            findings_for(plan.node_id)
            if findings_for is not None
            else [
                f
                for f in (getattr(verification, "findings", None) or [])
                if getattr(f, "node_id", None) in (None, plan.node_id)
            ]
        )
        findings = [f"{f.code}:{f.severity}" for f in relevant]
        return {
            "rule": "level=clamp(floor(5*(1-GT)),0,4); hysteresis holds de-escalation; "
            "L4 needs a decided approval, else L3",
            "gt": None if gt is None else gt.gt,
            "ts": None if gt is None else gt.ts,
            "cti_i": None if gt is None else gt.cti_i,
            "rep": None if gt is None else gt.rep,
            "drift_flag": None if gt is None else gt.drift_flag,
            "raw_level": None if gt is None else int(level_for_gt(gt.gt)),
            "effective_level": int(self.effective_level(plan.node_id)),
            "input_provenance": getattr(input_provenance, "value", str(input_provenance)),
            "verifier_findings": findings,
            "approval": None
            if approval is None
            else {
                "approved": bool(getattr(approval, "approved", False)),
                "decided_by": getattr(approval, "decided_by", None),
                "decided_at_sim": getattr(approval, "decided_at_sim", None),
            },
        }

    def _deny(
        self,
        plan: ResponsePlan,
        *,
        decision: GateDecision | None,
        reason: str | None,
        level: ResponseLevel | None = None,
        extra: dict[str, object] | None = None,
    ) -> ExecutionResult:
        self.denials[reason or "unknown"] = self.denials.get(reason or "unknown", 0) + 1
        audit = self._audit(
            plan,
            "response.denied",
            capability=decision.capability if decision else None,
            deny_reason=reason,
            **(extra or {}),
        )
        return ExecutionResult(executed=False, decision=decision, audit=audit, level=level)

    def _audit(self, plan: ResponsePlan, event_type: str, **payload: object) -> AuditRecord:
        record = AuditRecord(
            sim_time=plan.sim_time,
            run_id=plan.run_id,
            seed=plan.seed,
            config_hash=plan.config_hash,
            event_type=event_type,
            actor_id=self.actor_id,
            payload={
                "node_id": plan.node_id,
                "proposed_level": plan.proposed_level,
                **payload,
            },
        )
        self.audit.append(record)
        return record

    @property
    def audit_log(self) -> list[AuditRecord]:
        return self.audit.records


def _isolation_approved(
    plan: ResponsePlan, approval: Any | None, key: bytes, episode_start: float | None
) -> bool:
    """An approval for *this* device, in *this* episode, decided, and signed by the gate."""
    return (
        approval is not None
        and episode_start is not None
        and getattr(approval, "node_id", None) == plan.node_id
        and bool(getattr(approval, "approved", False))
        and float(getattr(approval, "sim_time", -1.0)) >= episode_start
        and float(getattr(approval, "decided_at_sim", float("inf"))) <= plan.sim_time
        and verify(approval_payload(approval), str(getattr(approval, "signature", "") or ""), key)
    )
