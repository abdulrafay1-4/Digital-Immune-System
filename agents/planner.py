"""Response planner: turns a global trust score into a proposed action level."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from m4_response_engine.hysteresis import HysteresisParams, LevelHysteresis
from m4_response_engine.levels import LEVEL_DESCRIPTION, ResponseLevel, level_for_gt
from shared.schemas import Classification, GlobalTrustUpdate, ResponsePlan

ACTOR_ID = "response_planner"
PLAN_TOPIC = "response.plan"


class RationaleWriter(Protocol):
    """Optional narrator."""

    def write(
        self,
        *,
        node_id: str,
        level: ResponseLevel,
        gt: float,
        classification: Classification | None,
    ) -> str: ...


class PlannerParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hysteresis: HysteresisParams = HysteresisParams()


class ResponsePlanner:
    """Deterministic level selection with per-node hysteresis."""

    def __init__(
        self,
        params: PlannerParams | None = None,
        *,
        hysteresis: LevelHysteresis | None = None,
        rationale_writer: RationaleWriter | None = None,
    ) -> None:
        self.params = params or PlannerParams()
        self.hysteresis = hysteresis or LevelHysteresis(params=self.params.hysteresis)
        self.rationale_writer = rationale_writer
        self.plans_made = 0

    def plan(
        self,
        gt_update: GlobalTrustUpdate,
        *,
        classification: Classification | None = None,
        level: ResponseLevel | int | None = None,
    ) -> ResponsePlan:
        """Narrate the response for one node at one tick."""
        if level is None:
            raw = level_for_gt(gt_update.gt)
            effective = self.hysteresis.apply(gt_update.node_id, raw)
        else:
            raw = level_for_gt(gt_update.gt)
            effective = ResponseLevel(level)

        rationale = self._rationale(gt_update, raw, effective, classification)
        self.plans_made += 1

        return ResponsePlan(
            sim_time=gt_update.sim_time,
            run_id=gt_update.run_id,
            seed=gt_update.seed,
            config_hash=gt_update.config_hash,
            node_id=gt_update.node_id,
            proposed_level=int(effective),
            rationale=rationale,
        )

    def plan_batch(
        self,
        gt_updates: list[GlobalTrustUpdate],
        *,
        classification: Classification | None = None,
        levels: Mapping[str, ResponseLevel | int] | None = None,
    ) -> list[ResponsePlan]:
        """Narrate every node in a tick, in a stable node order."""
        ordered = sorted(gt_updates, key=lambda u: u.node_id)
        return [
            self.plan(
                u,
                classification=classification,
                level=None if levels is None else levels.get(u.node_id),
            )
            for u in ordered
        ]

    def _rationale(
        self,
        gt_update: GlobalTrustUpdate,
        raw: ResponseLevel,
        effective: ResponseLevel,
        classification: Classification | None,
    ) -> str:
        base = (
            f"GT {gt_update.gt:.3f} -> L{int(raw)}; "
            f"effective L{int(effective)} ({LEVEL_DESCRIPTION[effective]})"
        )
        if effective != raw:
            base += " [held by hysteresis]"
        base += f"; TS {gt_update.ts:.3f}, CTI_i {gt_update.cti_i:.3f}, REP {gt_update.rep:.3f}"
        if classification is not None:
            base += f"; classified {classification.threat_type} (sev {classification.severity:.2f})"

        if self.rationale_writer is None:
            return base

        try:
            note = self.rationale_writer.write(
                node_id=gt_update.node_id,
                level=effective,
                gt=gt_update.gt,
                classification=classification,
            )
        except Exception as exc:  # noqa: BLE001
            return f"{base}; [narration failed: {type(exc).__name__}]"
        return f"{base}; {note}".strip()
