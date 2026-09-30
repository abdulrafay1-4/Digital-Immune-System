"""Memory adjudication: deciding what a remembered incident *meant*."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from shared.schemas import MemoryRecord


class Adjudicator(Protocol):
    actor_id: str
    delay_sim: float

    def adjudicate(self, record: MemoryRecord) -> str | None:
        """`confirmed`, `benign`, or `None` to leave the record pending."""
        ...


@dataclass(frozen=True)
class OracleAdjudicator:
    """An operator who reviews every incident and always gets it right."""

    compromised: frozenset[str]
    delay_sim: float = 0.0
    actor_id: str = "operator:oracle"

    def adjudicate(self, record: MemoryRecord) -> str | None:
        return "confirmed" if set(record.node_ids) & self.compromised else "benign"


@dataclass(frozen=True)
class AutoConfirmAdjudicator:
    """Remembers every incident as an attack: the lower bound, with no adjudication."""

    delay_sim: float = 0.0
    actor_id: str = "auto-confirm"

    def adjudicate(self, record: MemoryRecord) -> str | None:
        return "confirmed"


@dataclass(frozen=True)
class ErringAdjudicator:
    """An operator who gets a fixed, deterministic share of reviews wrong."""

    compromised: frozenset[str]
    error_rate: float
    delay_sim: float = 0.0
    actor_id: str = "operator:erring"

    def adjudicate(self, record: MemoryRecord) -> str | None:
        import hashlib

        truth = "confirmed" if set(record.node_ids) & self.compromised else "benign"
        roll = int(hashlib.sha256(record.record_id.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
        if roll >= self.error_rate:
            return truth
        return "benign" if truth == "confirmed" else "confirmed"
