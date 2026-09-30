"""Message integrity: HMAC over a canonical payload."""

from __future__ import annotations

import hashlib
import hmac

from shared.keys import derive

DEV_KEY = derive("gt-signing")
AUDIT_KEY = derive("audit-chain")

_SEP = "\x1f"


def canonical(*parts: object) -> bytes:
    """Order-sensitive, separator-delimited encoding of the signed fields."""
    return _SEP.join(repr(p) if isinstance(p, float) else str(p) for p in parts).encode()


def sign(payload: bytes, key: bytes = DEV_KEY) -> str:
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def verify(payload: bytes, signature: str, key: bytes = DEV_KEY) -> bool:
    """Constant-time comparison."""
    if not signature:
        return False
    return hmac.compare_digest(sign(payload, key), signature)


def approval_payload(approval: object) -> bytes:
    """What an isolation approval's signature covers."""
    fields = (
        "run_id",
        "seed",
        "config_hash",
        "sim_time",
        "node_id",
        "level",
        "approved",
        "decided_by",
        "delay_sim",
    )
    return canonical("approval", *(getattr(approval, f, None) for f in fields))


def chain_hash(previous: str, payload: bytes, key: bytes | None = None) -> str:
    """Link one audit record to the one before it, under a key."""
    return hmac.new(
        key if key is not None else AUDIT_KEY,
        previous.encode() + _SEP.encode() + payload,
        hashlib.sha256,
    ).hexdigest()
