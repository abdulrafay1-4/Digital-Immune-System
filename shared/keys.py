"""Key derivation: one master secret, a separate key for every purpose."""

from __future__ import annotations

import functools
import hashlib
import hmac
import os

ENV_VAR = "DIS_MASTER_KEY"

_DEVELOPMENT_MASTER = b"dis-development-master-key--never-deploy-this--"

PURPOSES = frozenset(
    {
        "gt-signing",
        "audit-chain",
        "capability",
        "adjudication",
        "approval",
    }
)


@functools.cache
def master_key() -> bytes:
    """Resolved once, at first use, and fixed for the life of the process."""
    raw = os.environ.get(ENV_VAR)
    if not raw:
        return _DEVELOPMENT_MASTER
    try:
        key = bytes.fromhex(raw)
    except ValueError as exc:
        raise ValueError(f"{ENV_VAR} must be hex") from exc
    if len(key) < 32:
        raise ValueError(f"{ENV_VAR} must be at least 32 bytes")
    return key


def using_development_key() -> bool:
    """Whether the key this process actually signs with is the development one."""
    return master_key() == _DEVELOPMENT_MASTER


def derive(purpose: str, master: bytes | None = None) -> bytes:
    """The key for one purpose."""
    if purpose not in PURPOSES:
        raise ValueError(f"unknown key purpose: {purpose}")
    return hmac.new(
        master if master is not None else master_key(),
        b"dis-key:" + purpose.encode(),
        hashlib.sha256,
    ).digest()


def fingerprint(key: bytes) -> str:
    """Safe to log: identifies a key without revealing it."""
    return hashlib.sha256(b"fingerprint:" + key).hexdigest()[:16]
