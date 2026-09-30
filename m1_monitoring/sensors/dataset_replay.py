"""Recorded network traffic replayed into the network dimension (TON_IoT)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from m1_monitoring.sensors.synthetic import NoiseModel, SyntheticTelemetry
from shared.schemas import ContextVector, Provenance


class DatasetReplayTelemetry:
    def __init__(self, seed: int, trace: Mapping[str, Sequence[float]]) -> None:
        model = NoiseModel(
            kind="replay", trace=tuple((node, tuple(series)) for node, series in trace.items())
        )
        self._inner = SyntheticTelemetry(seed, noise_model=model)

    def read(self, sim_time: float, node_id: str) -> tuple[ContextVector, Provenance]:
        return self._inner.read(sim_time, node_id)
