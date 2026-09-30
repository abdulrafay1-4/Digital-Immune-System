"""A device's sensor in another process: its measurements arrive over the broker."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from shared.schemas import ContextVector, DeviceMeasurement, Provenance

MEASUREMENT_TOPIC = "device.measurement"


def sensor_user(node_id: str) -> str:
    return f"sensor-{node_id}"


class MissingMeasurement(LookupError):
    """The device published nothing for this tick: to the monitor, it was silent."""


@dataclass
class RemoteSensor:
    bus: Any
    node_id: str
    poll: Callable[[], Any] | None = None
    max_polls: int = 10
    _latest: dict[float, DeviceMeasurement] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.bus.discover = False
        self.bus.subscribe(MEASUREMENT_TOPIC, self._measured)
        self.bus.follow(MEASUREMENT_TOPIC, sensor_user(self.node_id))

    def _measured(self, message: Any) -> None:
        if isinstance(message, DeviceMeasurement) and message.node_id == self.node_id:
            self._latest = {t: m for t, m in self._latest.items() if t >= message.sim_time - 4}
            self._latest[message.sim_time] = message

    def read(self, sim_time: float, node_id: str) -> tuple[ContextVector, Provenance]:
        for _ in range(self.max_polls):
            if sim_time in self._latest:
                break
            (self.poll or (lambda: self.bus.pump(timeout=0.05)))()
        measurement = self._latest.get(sim_time)
        if measurement is None or node_id != self.node_id:
            raise MissingMeasurement(f"{node_id} published nothing for tick {sim_time}")
        return measurement.context, measurement.provenance

    def attestation(self, sim_time: float, node_id: str) -> str | None:
        measurement = self._latest.get(sim_time)
        return measurement.attestation if measurement is not None else None


@dataclass
class SensorService:
    """The device's side: measure, sign with the device's own key, publish."""

    sensor: Any
    bus: Any
    node_id: str
    run_id: str
    seed: int
    config_hash: str
    published: int = 0

    def measure(self, sim_time: float) -> None:
        context, provenance = self.sensor.read(sim_time, self.node_id)
        signature = self.sensor.attestation(sim_time, self.node_id)
        self.bus.publish(
            MEASUREMENT_TOPIC,
            DeviceMeasurement(
                sim_time=sim_time,
                run_id=self.run_id,
                seed=self.seed,
                config_hash=self.config_hash,
                node_id=self.node_id,
                context=context,
                provenance=provenance,
                attestation=signature,
            ),
        )
        self.published += 1
