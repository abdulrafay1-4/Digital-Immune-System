"""What a device attests: one measurement, bound to the device and the tick."""

from __future__ import annotations

from shared.schemas import ContextVector


def attestation_payload(node_id: str, sim_time: float, context: ContextVector) -> bytes:
    """Canonical bytes for one measurement."""
    parts = (
        "dis-attestation-v1",
        node_id,
        f"{sim_time:.6f}",
        f"{context.identity:.9f}",
        f"{context.behavioral:.9f}",
        f"{context.device:.9f}",
        f"{context.network:.9f}",
    )
    return "\x1f".join(parts).encode()


def observation_payload(dimension: str, node_id: str, sim_time: float, value: float) -> bytes:
    """Canonical bytes for an independent observer's reading of one device's dimension."""
    parts = ("dis-observer-v1", dimension, node_id, f"{sim_time:.6f}", f"{value:.9f}")
    return "\x1f".join(parts).encode()


def verdict_payload(
    run_id: str, record_id: str, asked_at: float, status: str, decided_by: str
) -> bytes:
    """Canonical bytes for an operator's verdict on one remembered incident."""
    parts = ("dis-adjudication-v1", run_id, record_id, f"{asked_at:.6f}", status, decided_by)
    return "\x1f".join(parts).encode()


def decision_payload(
    run_id: str, node_id: str, asked_at: float, approved: bool, reason: str, decided_by: str
) -> bytes:
    """Canonical bytes for an operator's answer to one isolation question."""
    parts = (
        "dis-operator-v1",
        run_id,
        node_id,
        f"{asked_at:.6f}",
        "approve" if approved else "deny",
        reason,
        decided_by,
    )
    return "\x1f".join(parts).encode()
