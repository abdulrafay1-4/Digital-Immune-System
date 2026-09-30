"""Provenance helpers. Enum lives in schemas; tagging policy lives here."""

from __future__ import annotations

from shared.schemas import Provenance

_RANK = {
    Provenance.UNTRUSTED: 0,
    Provenance.LOW: 1,
    Provenance.MEDIUM: 2,
    Provenance.HIGH: 3,
}


def rank(p: Provenance) -> int:
    return _RANK[p]


def meets_ceiling(actual: Provenance, ceiling: Provenance) -> bool:
    """True if `actual` is at least as trusted as required `ceiling`."""
    return rank(actual) >= rank(ceiling)


def tag_synthetic() -> Provenance:
    """Seeded synthetic generator is under our control → HIGH."""
    return Provenance.HIGH


def tag_dataset_replay() -> Provenance:
    """External dataset: MEDIUM until calibrated."""
    return Provenance.MEDIUM


def tag_host() -> Provenance:
    """Live host telemetry: MEDIUM (not under simulation control)."""
    return Provenance.MEDIUM


def tag_external_tool() -> Provenance:
    """Untrusted tool / inter-agent ingest default."""
    return Provenance.UNTRUSTED
