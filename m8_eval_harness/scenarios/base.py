"""What a scenario is, and what an adversary may do inside one."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

DIMENSIONS = ("identity", "behavioral", "device", "network")


@dataclass(frozen=True)
class Anomaly:
    """One device degrading over a window, on named dimensions."""

    node_id: str
    start_sim: float
    end_sim: float
    severity: float
    dimensions: tuple[str, ...] = DIMENSIONS
    pulse_on: int = 0
    pulse_period: int = 0

    def __post_init__(self) -> None:
        if (self.pulse_on == 0) != (self.pulse_period == 0) or not (
            0 <= self.pulse_on < max(self.pulse_period, 1) or self.pulse_period == 0
        ):
            raise ValueError("a pulse needs 0 < pulse_on < pulse_period")
        if not 0.0 <= self.severity <= 1.0:
            raise ValueError(f"severity must be in [0, 1], got {self.severity}")
        if self.end_sim <= self.start_sim:
            raise ValueError("anomaly window must have positive duration")
        unknown = set(self.dimensions) - set(DIMENSIONS)
        if unknown:
            raise ValueError(f"unknown dimensions: {sorted(unknown)}")

    def active(self, tick: float) -> bool:
        if not self.start_sim <= tick < self.end_sim:
            return False
        if self.pulse_period == 0:
            return True
        return int(tick - self.start_sim) % self.pulse_period < self.pulse_on

    @property
    def spec(self) -> tuple[float, ...]:
        base = (self.start_sim, self.end_sim, self.severity)
        return base + (self.pulse_on, self.pulse_period) if self.pulse_period else base


@runtime_checkable
class Adversary(Protocol):
    """An attacker acting on the defensive pipeline, once per tick."""

    name: str

    def before_tick(self, run: object, sim_time: float) -> None: ...

    def after_tick(self, run: object, sim_time: float, outcome: object) -> None: ...


@dataclass(frozen=True)
class Scenario:
    """One attack, fully specified and reproducible from its seed."""

    scenario_id: str
    name: str
    demonstrates: str
    n_nodes: int
    ticks: int
    anomalies: tuple[Anomaly, ...] = ()
    ground_truth: Mapping[str, float] = field(default_factory=dict)
    outages: Mapping[str, tuple[float, float]] = field(default_factory=dict)
    restarts: Mapping[str, tuple[float, int]] = field(default_factory=dict)
    forged_observation: Mapping[str, float] = field(default_factory=dict)
    forged_context: Mapping[str, float] = field(default_factory=dict)
    selective_reporting: Mapping[str, float] = field(default_factory=dict)
    message_loss: float = 0.0
    dropped: Mapping[str, tuple[float, float]] = field(default_factory=dict)
    noise: Any | None = None
    adversary: Adversary | None = None
    seed: int = 42
    notes: str = ""

    def __post_init__(self) -> None:
        if self.n_nodes < 1:
            raise ValueError("a scenario needs at least one node")
        if self.ticks < 1:
            raise ValueError("a scenario needs at least one tick")
        known = {f"node-{i}" for i in range(self.n_nodes)}
        for anomaly in self.anomalies:
            if anomaly.node_id not in known:
                raise ValueError(f"anomaly targets an absent node: {anomaly.node_id}")
            if anomaly.end_sim > self.ticks:
                raise ValueError(f"anomaly on {anomaly.node_id} runs past the end of the scenario")
        for node_id in self.ground_truth:
            if node_id not in known:
                raise ValueError(f"ground truth names an absent node: {node_id}")
        for mapping, label in (
            (self.restarts, "restart"),
            (self.forged_observation, "forgery"),
            (self.forged_context, "patient forgery"),
            (self.selective_reporting, "selective reporting"),
        ):
            for node_id in mapping:
                if node_id not in known:
                    raise ValueError(f"{label} targets an absent node: {node_id}")
        if not 0.0 <= self.message_loss < 1.0:
            raise ValueError("message_loss must lie in [0, 1)")
        for node_id, (start, end) in self.dropped.items():
            if node_id not in known or not 0.0 <= start < end <= self.ticks:
                raise ValueError(f"dropped window for {node_id} must lie inside the scenario")
        for node_id, (down, back) in self.outages.items():
            if node_id not in known:
                raise ValueError(f"outage targets an absent node: {node_id}")
            if not 0.0 <= down < back <= self.ticks:
                raise ValueError(f"outage window for {node_id} must lie inside the scenario")

    @property
    def anomaly_map(self) -> dict[str, tuple[float, ...]]:
        return {a.node_id: a.spec for a in self.anomalies}

    @property
    def dimension_masks(self) -> dict[str, tuple[str, ...]]:
        return {a.node_id: a.dimensions for a in self.anomalies}

    def attack_ticks(self, node_id: str) -> frozenset[int]:
        """Ticks on which `node_id` is genuinely compromised."""
        anomalies = [a for a in self.anomalies if a.node_id == node_id]
        if not anomalies:
            onset = self.ground_truth.get(node_id)
            return frozenset() if onset is None else frozenset(range(int(onset), self.ticks))
        return frozenset(t for a in anomalies for t in range(self.ticks) if a.active(t))

    def attack_end(self, node_id: str) -> float | None:
        """When the attack on `node_id` last stops, for recovery metrics."""
        ends = [a.end_sim for a in self.anomalies if a.node_id == node_id]
        return max(ends) if ends else None

    def threat_families(self, node_id: str) -> frozenset[str]:
        """Rules-classifier labels that correctly name this device's compromise."""
        from agents.rules_classifier import DIMENSION_THREAT

        dims = {d for a in self.anomalies if a.node_id == node_id for d in a.dimensions}
        return frozenset(DIMENSION_THREAT[d].value for d in dims)

    @property
    def compromised(self) -> frozenset[str]:
        return frozenset(self.ground_truth)

    @property
    def healthy(self) -> frozenset[str]:
        return frozenset(f"node-{i}" for i in range(self.n_nodes)) - self.compromised

    @property
    def attacks_the_defender(self) -> bool:
        """True for scenarios s4 to s6: the target is the immune system itself."""
        return self.adversary is not None
