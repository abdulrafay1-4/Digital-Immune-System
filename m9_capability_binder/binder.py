"""M9 binder facade: prefers the Rust `dis_m9` extension, with a Python mirror."""

from __future__ import annotations

import hashlib
import hmac
import itertools
import math
from enum import Enum
from typing import Any

from shared.keys import derive

_SECRET = derive("capability")

try:
    import dis_m9 as _native
except ImportError:  # pragma: no cover
    _native = None


class Capability(str, Enum):
    MONITOR_ENHANCE = "monitor_enhance"
    REAUTH = "reauth"
    RESTRICT = "restrict"
    ISOLATE = "isolate"
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"


_REQUIRED = {
    Capability.MONITOR_ENHANCE: "LOW",
    Capability.REAUTH: "MEDIUM",
    Capability.RESTRICT: "MEDIUM",
    Capability.ISOLATE: "HIGH",
    Capability.MEMORY_READ: "LOW",
    Capability.MEMORY_WRITE: "MEDIUM",
}

_RANK = {"UNTRUSTED": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}

_NONCE = itertools.count(1)

_SPENT: dict[str, float] = {}


def _sign(
    token_id: str,
    capability: str,
    subject_id: str,
    expires_at_sim: float,
    ceiling: str,
) -> str:
    payload = f"{token_id}|{capability}|{subject_id}|{expires_at_sim:.6f}|{ceiling}".encode()
    return hmac.new(_SECRET, payload, hashlib.sha256).hexdigest()


def _resolve_python(
    capability: str,
    subject_id: str,
    input_provenance: str,
    sim_time: float,
    ttl: float = 60.0,
) -> dict[str, Any]:
    if not (math.isfinite(sim_time) and math.isfinite(ttl)):
        return {"ok": False, "deny_reason": "invalid_time"}
    try:
        cap = Capability(capability)
    except ValueError:
        return {"ok": False, "deny_reason": "unknown_capability"}
    if input_provenance not in _RANK:
        return {"ok": False, "deny_reason": "unknown_capability"}
    required = _REQUIRED[cap]
    if _RANK[input_provenance] < _RANK[required]:
        return {"ok": False, "deny_reason": "provenance_too_low"}
    if ttl <= 0:
        return {"ok": False, "deny_reason": "non_positive_ttl"}
    expires = sim_time + ttl
    token_id = f"{subject_id}:{cap.value}:{sim_time}:{next(_NONCE)}"
    sig = _sign(token_id, cap.value, subject_id, expires, required)
    return {
        "ok": True,
        "token_id": token_id,
        "capability": cap.value,
        "subject_id": subject_id,
        "signature": sig,
        "expires_at_sim": expires,
        "provenance_ceiling": required,
    }


def resolve_capability(
    capability: str,
    subject_id: str,
    input_provenance: str,
    sim_time: float,
    ttl: float = 60.0,
    *,
    prefer_native: bool = True,
) -> dict[str, Any]:
    """Resolve a capability request."""
    if prefer_native and _native is not None:
        return dict(
            _native.resolve_capability(
                capability, subject_id, input_provenance, sim_time, ttl, secret=_SECRET
            )
        )
    return _resolve_python(capability, subject_id, input_provenance, sim_time, ttl)


def native_available() -> bool:
    return _native is not None


def implementation() -> str:
    """Which binder is live."""
    return "rust" if _native is not None else "python"


def redeem(token: dict[str, Any], *, now_sim: float) -> tuple[bool, str | None]:
    """Spend a token exactly once, before its expiry."""
    token_id = token.get("token_id")
    if not token.get("ok") or not isinstance(token_id, str):
        return False, "malformed_token"
    fields = [token.get(k) for k in ("capability", "subject_id", "signature", "provenance_ceiling")]
    if not all(isinstance(f, str) for f in fields):
        return False, "malformed_token"
    capability, subject_id, signature, ceiling = fields

    expires = token.get("expires_at_sim")
    if not isinstance(expires, int | float) or not math.isfinite(expires):
        return False, "malformed_token"
    if not math.isfinite(now_sim):
        return False, "malformed_token"

    if _native is not None:
        reason = _native.redeem_token(
            token_id,
            capability,
            subject_id,
            signature,
            float(expires),
            ceiling,
            float(now_sim),
            secret=_SECRET,
        )
        return reason is None, reason

    if now_sim > expires:
        return False, "token_expired"
    expected = _sign(token_id, capability, subject_id, float(expires), ceiling)
    if not hmac.compare_digest(expected, signature):
        return False, "bad_signature"

    _maybe_evict(now_sim)
    if token_id in _SPENT:
        return False, "token_replayed"
    _SPENT[token_id] = float(expires)
    return True, None


_EVICT_AT = 4096
_EVICT_FLOOR = 4096


def _maybe_evict(now_sim: float) -> None:
    """Forget tokens the expiry check would refuse anyway, in amortised sweeps."""
    global _EVICT_AT
    if len(_SPENT) < _EVICT_AT:
        return
    for tid in [tid for tid, expires in _SPENT.items() if now_sim > expires]:
        del _SPENT[tid]
    _EVICT_AT = max(_EVICT_FLOOR, len(_SPENT) * 2)


def reset_spent_tokens() -> None:
    """Clear the spend set."""
    global _EVICT_AT
    _SPENT.clear()
    _EVICT_AT = _EVICT_FLOOR
    if _native is not None:
        _native.reset_spent_tokens()


def spent_token_count() -> int:
    """How many unexpired tokens are being remembered."""
    return _native.spent_token_count() if _native is not None else len(_SPENT)
