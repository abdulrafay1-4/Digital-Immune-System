"""TelemetrySource protocol: sensors feed the agent; the core stays pure."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from shared.schemas import ContextVector, Provenance


@runtime_checkable
class TelemetrySource(Protocol):
    def read(self, sim_time: float, node_id: str) -> tuple[ContextVector, Provenance]:
        """Return context + provenance at sim_time for node_id."""
        ...
