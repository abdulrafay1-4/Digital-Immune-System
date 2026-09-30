"""Host telemetry (psutil): a stub for a live host."""

from __future__ import annotations

from m1_monitoring.core.context_vector import make_context
from shared.provenance import tag_host
from shared.schemas import ContextVector, Provenance


class HostTelemetry:
    def read(self, sim_time: float, node_id: str) -> tuple[ContextVector, Provenance]:
        _ = (sim_time, node_id)
        return make_context(0.8, 0.8, 0.8, 0.8), tag_host()
