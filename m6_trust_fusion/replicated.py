"""
N-version trust fusion: 2f+1 independent instances, and an update acts only when a majority returned
it exactly.
"""

from __future__ import annotations

import statistics
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any


class NoMajority(RuntimeError):
    """No update was returned by a majority of fusion instances."""


class _Discard:
    """A bus for the replicas: only the chosen update is published, once."""

    def publish(self, topic: str, message: Any) -> None:
        return None

    def subscribe(self, topic: str, handler: Any) -> None:
        return None


@dataclass
class ReplicatedFusion:
    """Looks like one `TrustFusionEngine`; is 2f+1, and acts on what a majority returns."""

    replicas: list[Any]
    bus: Any
    disagreements: int = 0
    _publish_topic: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        if len(self.replicas) < 3 or len(self.replicas) % 2 == 0:
            raise ValueError("a majority that outvotes f liars needs 2f+1 instances, f >= 1")
        from m6_trust_fusion.fusion import GT_TOPIC

        self._publish_topic = GT_TOPIC
        for replica in self.replicas:
            replica.bus = _Discard()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.replicas[0], name)

    def set_drift(self, node_id: str, drift_flag: float) -> None:
        for replica in self.replicas:
            replica.set_drift(node_id, drift_flag)

    def apply_recalibration(self, node_id: str, next_ts: float) -> None:
        for replica in self.replicas:
            replica.apply_recalibration(node_id, next_ts)

    def observe_responses(self, plans: Iterable[Any]) -> dict[str, float]:
        plans = list(plans)
        answers = [replica.observe_responses(plans) for replica in self.replicas]
        nodes = dict.fromkeys(n for a in answers for n in a)
        return {n: statistics.median(a[n] for a in answers if n in a) for n in nodes}

    def fuse_batch(self, updates: Iterable[Any], correlation: Any) -> list[Any]:
        updates = list(updates)
        outputs = [replica.fuse_batch(updates, correlation) for replica in self.replicas]
        by_node = [{u.node_id: u for u in out} for out in outputs]
        nodes = dict.fromkeys(u.node_id for out in outputs for u in out)
        chosen = [self._choose([m.get(n) for m in by_node]) for n in nodes]
        chosen = [u for u in chosen if u is not None]
        for update in chosen:
            self.bus.publish(self._publish_topic, update)
        return chosen

    def observe_silence(self, node_id: str, **kw: Any) -> Any:
        outputs = [replica.observe_silence(node_id, **kw) for replica in self.replicas]
        update = self._choose(outputs)
        if update is not None:
            self.bus.publish(self._publish_topic, update)
        return update

    def current_ts(self, node_id: str) -> float | None:
        values = [v for r in self.replicas if (v := r.current_ts(node_id)) is not None]
        return statistics.median(values) if values else None

    def implicates_on_own_trust(self, node_id: str) -> bool:
        votes = [bool(r.implicates_on_own_trust(node_id)) for r in self.replicas]
        return sum(votes) * 2 > len(votes)

    def _choose(self, updates: list[Any]) -> Any:
        """The update a majority of instances returned, field for field."""
        keys = [_trust_fields(u) for u in updates]
        if len(set(keys)) > 1:
            self.disagreements += 1
        for key in set(keys):
            if keys.count(key) * 2 > len(self.replicas):
                return updates[keys.index(key)]
        raise NoMajority(f"no fusion update has a majority of {len(self.replicas)}")


def _trust_fields(update: Any) -> tuple[Any, ...] | None:
    if update is None:
        return None
    return (
        update.node_id,
        update.gt,
        update.ts,
        update.cti_i,
        update.cti_trust,
        update.rep,
        update.master_score,
        update.drift_flag,
        update.threat_confirmed,
    )
