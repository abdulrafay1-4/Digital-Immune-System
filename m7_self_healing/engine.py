"""M7 self-healing state machine: revoke, recalibrate, reintegrate, rollback."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from m7_self_healing.recovery import (
    HealingParams,
    converge,
    recovery_score,
    should_heal,
)
from shared.schemas import HealingEvent

ACTOR_ID = "self-healing"
HEAL_TOPIC = "healing.event"


class Phase(StrEnum):
    """`HealingEvent.phase` carries these verbatim."""

    IDLE = "idle"
    REVOKE = "revoke"
    RECALIBRATE = "recalibrate"
    REINTEGRATE = "reintegrate"
    HEALED = "healed"
    ROLLBACK = "rollback"
    NEEDS_APPROVAL = "needs_approval"


@dataclass(frozen=True)
class NodeHealingState:
    phase: Phase = Phase.IDLE
    attempts: int = 0
    ticks_in_phase: int = 0
    target_ts: float | None = None
    gt_at_reintegrate: float | None = None
    last_rs: float = 0.0


@dataclass
class SelfHealingEngine:
    """One instance for a whole run: healing state is per node and long-lived."""

    params: HealingParams = field(default_factory=HealingParams)
    run_id: str = "r"
    seed: int = 1
    config_hash: str = "h"
    _state: dict[str, NodeHealingState] = field(default_factory=dict, repr=False)

    def state(self, node_id: str) -> NodeHealingState:
        return self._state.get(node_id, NodeHealingState())

    def target_for(self, node_id: str) -> float | None:
        """The recalibration target TS should converge toward, or `None`."""
        return self.state(node_id).target_ts

    def next_ts(self, node_id: str, current_ts: float) -> float:
        """Convenience for the owner of TS: one convergence step, or no change."""
        target = self.target_for(node_id)
        if target is None:
            return current_ts
        return converge(current_ts, target, rate=self.params.converge_rate)

    def observe(
        self,
        node_id: str,
        *,
        gt: float,
        health: float,
        sim_time: float,
        approval_granted: bool = False,
    ) -> HealingEvent | None:
        """Advance one node by one tick."""
        before = self.state(node_id)
        after = self._advance(before, gt=gt, health=health, approval=approval_granted)
        self._state[node_id] = after

        if after.phase is before.phase:
            return None
        return HealingEvent(
            sim_time=sim_time,
            run_id=self.run_id,
            seed=self.seed,
            config_hash=self.config_hash,
            node_id=node_id,
            phase=after.phase.value,
            target_ts=after.target_ts,
            success=after.phase in (Phase.HEALED, Phase.REINTEGRATE),
        )

    def _advance(
        self,
        s: NodeHealingState,
        *,
        gt: float,
        health: float,
        approval: bool,
    ) -> NodeHealingState:
        p = self.params
        rs = recovery_score(gt, health, eta=p.eta)

        if s.phase is Phase.NEEDS_APPROVAL:
            if not approval:
                return _tick(s, rs)
            return NodeHealingState(phase=Phase.REVOKE, attempts=s.attempts, last_rs=rs)

        if s.phase in (Phase.IDLE, Phase.HEALED, Phase.ROLLBACK):
            if not should_heal(gt, tau_h=p.tau_h):
                if s.phase is Phase.IDLE:
                    return _tick(s, rs)
                return NodeHealingState(phase=Phase.IDLE, attempts=s.attempts, last_rs=rs)
            if s.attempts >= p.max_auto_attempts:
                return NodeHealingState(phase=Phase.NEEDS_APPROVAL, attempts=s.attempts, last_rs=rs)
            return NodeHealingState(phase=Phase.REVOKE, attempts=s.attempts, last_rs=rs)

        if s.phase is Phase.REVOKE:
            return NodeHealingState(
                phase=Phase.RECALIBRATE,
                attempts=s.attempts,
                target_ts=p.target_ts,
                last_rs=rs,
            )

        if s.phase is Phase.RECALIBRATE:
            return NodeHealingState(
                phase=Phase.REINTEGRATE,
                attempts=s.attempts,
                target_ts=p.target_ts,
                gt_at_reintegrate=gt,
                last_rs=rs,
            )

        if s.phase is Phase.REINTEGRATE:
            entry = s.gt_at_reintegrate if s.gt_at_reintegrate is not None else gt
            relapsed = gt < entry - p.relapse_drop
            expired = s.ticks_in_phase + 1 >= p.reintegrate_ticks

            if relapsed:
                return _failed(s, rs)
            if rs >= p.rs_healed:
                return NodeHealingState(phase=Phase.HEALED, attempts=s.attempts + 1, last_rs=rs)
            if expired:
                return _failed(s, rs)
            return NodeHealingState(
                phase=Phase.REINTEGRATE,
                attempts=s.attempts,
                ticks_in_phase=s.ticks_in_phase + 1,
                target_ts=s.target_ts,
                gt_at_reintegrate=s.gt_at_reintegrate,
                last_rs=rs,
            )

        raise AssertionError(f"unhandled phase: {s.phase}")


def _tick(s: NodeHealingState, rs: float) -> NodeHealingState:
    return NodeHealingState(
        phase=s.phase,
        attempts=s.attempts,
        ticks_in_phase=s.ticks_in_phase + 1,
        target_ts=s.target_ts,
        gt_at_reintegrate=s.gt_at_reintegrate,
        last_rs=rs,
    )


def _failed(s: NodeHealingState, rs: float) -> NodeHealingState:
    """Rollback drops the target, so TS stops converging upward immediately."""
    return NodeHealingState(
        phase=Phase.ROLLBACK,
        attempts=s.attempts + 1,
        target_ts=None,
        last_rs=rs,
    )
