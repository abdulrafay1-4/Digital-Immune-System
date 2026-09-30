"""Seeded synthetic telemetry, the primary data source."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

import numpy as np

from m1_monitoring.core.context_vector import make_context
from shared.provenance import tag_dataset_replay, tag_synthetic
from shared.schemas import ContextVector, Provenance

DIMENSIONS = ("identity", "behavioral", "device", "network")


def _node_seed(base_seed: int, node_id: str) -> int:
    h = hashlib.sha256(f"{base_seed}:{node_id}".encode()).hexdigest()
    return int(h[:8], 16)


@dataclass(frozen=True)
class NoiseModel:
    """How healthy telemetry varies: the external-validity knob."""

    kind: str = "gaussian"
    sigma: float = 0.02
    amplitude: float = 0.05
    period: float = 60.0
    rho: float = 0.5
    quantiles: tuple[float, ...] = ()
    trace: tuple[tuple[str, tuple[float, ...]], ...] = ()
    trace_dimension: str = "network"
    host_trace: tuple[tuple[str, tuple[tuple[float, ...], ...]], ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in (
            "gaussian",
            "heavy_tail",
            "diurnal",
            "correlated",
            "ton_iot",
            "replay",
            "host_replay",
        ):
            raise ValueError(f"unknown noise model: {self.kind}")
        if self.sigma < 0 or not 0.0 <= self.rho <= 1.0 or self.period <= 0:
            raise ValueError("invalid noise parameters")
        if self.trace_dimension not in DIMENSIONS:
            raise ValueError(f"unknown dimension: {self.trace_dimension}")
        if self.kind == "ton_iot" and len(self.quantiles) < 2:
            raise ValueError("ton_iot noise needs calibrated quantiles")
        values = [
            *self.quantiles,
            *(v for _, series in self.trace for v in series),
            *(v for _, series in self.host_trace for pair in series for v in pair),
        ]
        if any(not 0.0 <= v <= 1.0 for v in values):
            raise ValueError("disturbance must lie in [0, 1]")

    def network_disturbance(self, rng: np.random.Generator, node_id: str, sim_time: float) -> float:
        if self.kind == "ton_iot":
            position = float(rng.random()) * (len(self.quantiles) - 1)
            low = int(position)
            high = min(low + 1, len(self.quantiles) - 1)
            return self.quantiles[low] + (position - low) * (
                self.quantiles[high] - self.quantiles[low]
            )
        if self.kind == "replay":
            series = self._traces().get(node_id, ())
            tick = int(sim_time)
            return series[tick] if 0 <= tick < len(series) else 0.0
        return 0.0

    def host_disturbance(self, node_id: str, sim_time: float) -> tuple[float, ...]:
        """(behavioural, device[, network]) disturbance for `node_id` at `sim_time`."""
        if self.kind != "host_replay":
            return (0.0, 0.0)
        cached = self.__dict__.get("_host_map")
        if cached is None:
            cached = dict(self.host_trace)
            object.__setattr__(self, "_host_map", cached)
        series = cached.get(node_id, ())
        tick = int(sim_time)
        return series[tick] if 0 <= tick < len(series) else (0.0, 0.0)

    def _traces(self) -> dict[str, tuple[float, ...]]:
        cached = self.__dict__.get("_trace_map")
        if cached is None:
            cached = dict(self.trace)
            object.__setattr__(self, "_trace_map", cached)
        return cached


class SyntheticTelemetry:
    """Healthy baseline with optional scheduled anomaly windows per node."""

    def __init__(
        self,
        seed: int,
        *,
        noise: float = 0.02,
        anomalies: dict[str, tuple[float, ...]] | None = None,
        dimension_masks: dict[str, tuple[str, ...]] | None = None,
        noise_model: NoiseModel | None = None,
    ) -> None:
        """
        anomalies: node_id -> (start_sim, end_sim, severity[, on_ticks, period_ticks]) severity in
        [0,1] subtracts from the affected dimensions in the window.
        """
        self._seed = seed
        self._noise = noise
        self._anomalies = anomalies or {}
        self._masks = dimension_masks or {}
        self._model = noise_model or NoiseModel(sigma=noise)

    def anomaly_active(self, sim_time: float, node_id: str) -> bool:
        """Is `node_id`'s scheduled anomaly active at `sim_time`?"""
        spec = self._anomalies.get(node_id)
        if spec is None:
            return False
        start, end = spec[0], spec[1]
        on, period = (int(spec[3]), int(spec[4])) if len(spec) >= 5 else (0, 0)
        if not start <= sim_time < end:
            return False
        return on <= 0 or period <= 0 or int(sim_time - start) % period < on

    def read(self, sim_time: float, node_id: str) -> tuple[ContextVector, Provenance]:
        rng = np.random.default_rng(_node_seed(self._seed, node_id) ^ int(sim_time * 1000))
        model = self._model
        if model.kind == "heavy_tail":

            def draw() -> float:
                return float(rng.standard_t(3)) * model.sigma / math.sqrt(3.0)
        else:

            def draw() -> float:
                return float(rng.normal(0.0, model.sigma))

        base = 0.92 + draw()
        if model.kind == "diurnal":
            base += model.amplitude * math.sin(2.0 * math.pi * sim_time / model.period)
        elif model.kind == "correlated":
            fleet_seed = _node_seed(self._seed, "__fleet__") ^ int(sim_time * 1000)
            fleet = np.random.default_rng(fleet_seed)
            shared = float(fleet.normal(0.0, model.sigma))
            base = 0.92 + math.sqrt(model.rho) * shared + math.sqrt(1.0 - model.rho) * (base - 0.92)
        dims = [base + draw() for _ in range(4)]
        if model.kind in ("ton_iot", "replay"):
            replayed_dim = DIMENSIONS.index(model.trace_dimension) if model.kind == "replay" else 3
            dims[replayed_dim] -= model.network_disturbance(rng, node_id, sim_time)
        if model.kind == "host_replay":
            for dim, value in enumerate(model.host_disturbance(node_id, sim_time), start=1):
                dims[dim] -= value

        if node_id in self._anomalies:
            spec = self._anomalies[node_id]
            start, end, severity = spec[0], spec[1], spec[2]
            on, period = (int(spec[3]), int(spec[4])) if len(spec) >= 5 else (0, 0)
            pulsing = on > 0 and period > 0
            active = start <= sim_time < end and (
                not pulsing or int(sim_time - start) % period < on
            )
            if active:
                affected = self._masks.get(node_id, DIMENSIONS)
                dims = [
                    d - severity if name in affected else d
                    for name, d in zip(DIMENSIONS, dims, strict=True)
                ]

        ctx = make_context(*dims)
        replayed = model.kind in ("replay", "host_replay")
        return ctx, tag_dataset_replay() if replayed else tag_synthetic()
