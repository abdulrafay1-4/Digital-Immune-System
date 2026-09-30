"""Level hysteresis: the stateful half of M4."""

from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field

from m4_response_engine.levels import ResponseLevel, level_for_gt


class HysteresisParams(BaseModel):
    """Calibrate `n` on the calibration set only, then freeze."""

    model_config = ConfigDict(extra="forbid")

    n: int = Field(default=3, ge=1)


@dataclass(frozen=True)
class NodeHysteresisState:
    """Immutable view of one node's state, for tests and audit records."""

    effective: ResponseLevel = ResponseLevel.NONE
    pending: ResponseLevel | None = None
    stable_ticks: int = 0
    cancelled_deescalations: int = 0


@dataclass
class LevelHysteresis:
    """Turns raw per-tick levels into effective levels, per node."""

    params: HysteresisParams = field(default_factory=HysteresisParams)
    _state: dict[str, NodeHysteresisState] = field(default_factory=dict, repr=False)

    def apply(self, node_id: str, raw_level: ResponseLevel | int) -> ResponseLevel:
        """Record `raw_level` for `node_id` and return the level to actually enforce."""
        raw = ResponseLevel(raw_level)
        state = self._state.get(node_id, NodeHysteresisState())

        if raw > state.effective:
            new = NodeHysteresisState(
                effective=raw,
                cancelled_deescalations=(
                    state.cancelled_deescalations + (1 if state.pending is not None else 0)
                ),
            )
        elif raw == state.effective:
            new = NodeHysteresisState(
                effective=state.effective,
                cancelled_deescalations=(
                    state.cancelled_deescalations + (1 if state.pending is not None else 0)
                ),
            )
        else:
            ticks = state.stable_ticks + 1 if state.pending == raw else 1
            new = (
                NodeHysteresisState(
                    effective=raw, cancelled_deescalations=state.cancelled_deescalations
                )
                if ticks >= self.params.n
                else NodeHysteresisState(
                    effective=state.effective,
                    pending=raw,
                    stable_ticks=ticks,
                    cancelled_deescalations=state.cancelled_deescalations,
                )
            )

        self._state[node_id] = new
        return new.effective

    def apply_gt(self, node_id: str, gt: float) -> ResponseLevel:
        """Convenience for the per-tick path: GT → raw level → effective level."""
        return self.apply(node_id, level_for_gt(gt))

    def flapping(self, threshold: int = 3) -> list[str]:
        """Nodes held at a level by repeated cancellation, sorted."""
        return sorted(
            node_id for node_id, s in self._state.items() if s.cancelled_deescalations >= threshold
        )

    def state(self, node_id: str) -> NodeHysteresisState:
        """Current state for `node_id`; the L0 default for an unseen node."""
        return self._state.get(node_id, NodeHysteresisState())

    def snapshot(self) -> dict[str, NodeHysteresisState]:
        """All tracked nodes, as a copy so callers cannot mutate internal state."""
        return dict(self._state)

    def reset(self, node_id: str | None = None) -> None:
        """Forget one node (e.g. after M7 reintegration) or all of them."""
        if node_id is None:
            self._state.clear()
        else:
            self._state.pop(node_id, None)
