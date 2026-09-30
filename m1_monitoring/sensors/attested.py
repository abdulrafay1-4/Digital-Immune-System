"""A telemetry source whose measurements the device signs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from m1_monitoring.sensors.base import TelemetrySource
from shared.attestation import attestation_payload
from shared.schemas import ContextVector, Provenance


class AttestedTelemetry:
    def __init__(self, inner: TelemetrySource, device_keys: Mapping[str, Any]) -> None:
        self._inner = inner
        self._keys = dict(device_keys)
        self._signed: dict[tuple[str, float], str] = {}

    def read(self, sim_time: float, node_id: str) -> tuple[ContextVector, Provenance]:
        context, provenance = self._inner.read(sim_time, node_id)
        key = self._keys.get(node_id)
        if key is not None:
            self._signed = {k: v for k, v in self._signed.items() if k[0] != node_id}
            self._signed[(node_id, sim_time)] = key.sign(
                attestation_payload(node_id, sim_time, context)
            )
        return context, provenance

    def attestation(self, sim_time: float, node_id: str) -> str | None:
        """The device's signature over what it measured at `sim_time`, if anything."""
        return self._signed.get((node_id, sim_time))

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)
