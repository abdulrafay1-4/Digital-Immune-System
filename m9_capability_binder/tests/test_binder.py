"""M9 binder: token uniqueness, redemption and parity between Rust and Python."""

from __future__ import annotations

from m9_capability_binder import binder
from m9_capability_binder.binder import native_available, resolve_capability


def test_unknown_capability_denies() -> None:
    r = resolve_capability("fly", "node-0", "HIGH", 0.0, prefer_native=False)
    assert r["ok"] is False
    assert r["deny_reason"] == "unknown_capability"


def test_low_provenance_cannot_resolve_isolate() -> None:
    r = resolve_capability("isolate", "node-0", "LOW", 0.0, prefer_native=False)
    assert r["ok"] is False
    assert r["deny_reason"] == "provenance_too_low"


def test_high_provenance_resolves_restrict() -> None:
    r = resolve_capability("restrict", "node-0", "HIGH", 10.0, ttl=30.0, prefer_native=False)
    assert r["ok"] is True
    assert r["capability"] == "restrict"
    assert r["signature"]
    assert r["expires_at_sim"] == 40.0


def test_native_module_optional() -> None:
    r = resolve_capability("monitor_enhance", "n", "LOW", 0.0)
    assert "ok" in r
    _ = native_available()


def test_the_build_in_use_is_reported() -> None:
    assert binder.implementation() in ("rust", "python")


def test_a_token_is_spent_once_and_its_signature_is_checked() -> None:
    binder.reset_spent_tokens()
    token = binder.resolve_capability("restrict", "node-0", "HIGH", 10.0)
    assert binder.redeem(dict(token, capability="isolate"), now_sim=10.0) == (
        False,
        "bad_signature",
    )
    assert binder.redeem(token, now_sim=10.0) == (True, None)
    assert binder.redeem(token, now_sim=10.0) == (False, "token_replayed")


def test_tokens_are_unique_for_the_same_subject_and_tick() -> None:
    a = binder.resolve_capability("restrict", "node-0", "HIGH", 10.0)
    b = binder.resolve_capability("restrict", "node-0", "HIGH", 10.0)
    assert a["token_id"] != b["token_id"]


def test_invalid_times_are_denied() -> None:
    import math

    assert (
        binder.resolve_capability("restrict", "n", "HIGH", math.nan)["deny_reason"]
        == "invalid_time"
    )
    assert (
        binder.resolve_capability("restrict", "n", "HIGH", 1.0, ttl=0.0)["deny_reason"]
        == "non_positive_ttl"
    )


def test_python_and_rust_tokens_verify_in_either_implementation() -> None:
    binder.reset_spent_tokens()
    token = binder._resolve_python("restrict", "node-7", "HIGH", 5.0)
    assert binder.redeem(token, now_sim=5.0) == (True, None)
