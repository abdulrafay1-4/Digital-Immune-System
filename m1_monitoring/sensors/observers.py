"""
Observers the device does not control (network gateway, identity provider, TPM), each signing its
own reading of one context dimension.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.attestation import observation_payload

OBSERVABLE = {
    "network": "the gateway on its network path",
    "identity": "the identity provider that authenticates it",
    "device": "its TPM, quoting measured boot (remote attestation)",
}


@dataclass
class IndependentObserver:
    dimension: str
    identity: Any
    source: Any = None

    def __post_init__(self) -> None:
        if self.dimension not in OBSERVABLE:
            raise ValueError(f"no one outside the device observes {self.dimension!r}")

    def observe(self, node_id: str, sim_time: float) -> tuple[float, str] | None:
        """This observer's signed reading of `node_id`'s dimension at `sim_time`."""
        if self.source is None:
            return None
        context, _ = self.source.read(sim_time, node_id)
        value = float(getattr(context, self.dimension))
        return value, self.identity.sign(
            observation_payload(self.dimension, node_id, sim_time, value)
        )
