"""Bus security: message authentication, and the TLS configuration it sits under."""

from __future__ import annotations

import pytest

from m10_persona_drift.nhi import issue_identity
from shared.bus import InProcBus
from shared.schemas import ContextVector, Provenance, TrustUpdate
from shared.secure_bus import SignedBus, TLSConfig, message_payload

TOPIC = "trust.update"


def _ident(name: str):
    return issue_identity(name, seed=name.encode().ljust(32, b"\0"))


def _update(node_id: str = "n-0", level: float = 0.9, agent_id: str = "mon-a") -> TrustUpdate:
    return TrustUpdate(
        sim_time=1.0,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id=node_id,
        node_trust=level,
        observation=level,
        context=ContextVector(identity=level, behavioral=level, device=level, network=level),
        provenance=Provenance.HIGH,
        agent_id=agent_id,
    )


def _wired(sender: str = "mon-a", registry_names=("mon-a",)):
    inner = InProcBus()
    registry = {n: _ident(n) for n in registry_names}
    bus = SignedBus(inner=inner, identity=_ident(sender), registry=registry)
    got: list[TrustUpdate] = []
    bus.subscribe(TOPIC, lambda m: got.append(m))
    return bus, inner, got


def test_a_signed_message_is_delivered_unwrapped() -> None:
    bus, _, got = _wired()
    bus.publish(TOPIC, _update())
    assert len(got) == 1
    assert isinstance(got[0], TrustUpdate), "subscribers never see the envelope"
    assert bus.delivered == 1
    assert bus.rejected == []


def test_an_unsigned_message_injected_onto_the_bus_is_refused() -> None:
    """What an injected message looks like on a signed bus."""
    bus, inner, got = _wired()
    inner.publish(TOPIC, _update(level=0.01))
    assert got == []
    assert bus.rejected == [("<unsigned>", "not_signed")]


def test_an_altered_message_does_not_verify() -> None:
    """A proxy that terminates TLS sees plaintext; the signature still holds."""
    bus, inner, got = _wired()
    captured: list = []
    inner.subscribe(TOPIC, lambda e: captured.append(e))
    bus.publish(TOPIC, _update(level=0.9))

    from dataclasses import replace

    tampered = replace(captured[0], model=_update(level=0.01))
    bus2, inner2, got2 = _wired()
    inner2.publish(TOPIC, tampered)
    assert got2 == []
    assert bus2.rejected == [("mon-a", "bad_signature")]


def test_a_message_cannot_be_replayed_onto_another_topic() -> None:
    update = _update()
    assert message_payload("trust.update", update, "mon-a") != message_payload(
        "healing.event", update, "mon-a"
    )


def test_a_signature_cannot_be_re_attributed_to_another_sender() -> None:
    update = _update()
    assert message_payload(TOPIC, update, "mon-a") != message_payload(TOPIC, update, "mon-b")


def test_an_unknown_publisher_is_refused() -> None:
    """Deny by default: a sender not in the registry is not merely unverified."""
    bus, _, got = _wired(sender="stranger", registry_names=("mon-a",))
    bus.publish(TOPIC, _update())
    assert got == []
    assert bus.rejected == [("stranger", "unknown_sender")]


def test_one_agent_cannot_impersonate_another() -> None:
    """A compromised publisher still cannot speak as a different agent."""
    inner = InProcBus()
    registry = {"mon-a": _ident("mon-a"), "mon-b": _ident("mon-b")}
    attacker = SignedBus(inner=inner, identity=_ident("mon-a"), registry=registry)
    got: list = []
    SignedBus(inner=inner, identity=_ident("mon-b"), registry=registry).subscribe(
        TOPIC, lambda m: got.append(m)
    )

    attacker.identity = _ident("mon-a")
    forged = type("F", (), {"agent_id": "mon-b", "sign": _ident("mon-a").sign})()
    attacker.identity = forged  # type: ignore[assignment]
    attacker.publish(TOPIC, _update())
    assert got == []


def test_a_monitor_cannot_sign_a_report_that_names_another_monitor() -> None:
    """The signature proves the sender, not the claimed author."""
    inner = InProcBus()
    registry = {"mon-a": _ident("mon-a"), "mon-b": _ident("mon-b")}
    compromised = SignedBus(inner=inner, identity=_ident("mon-a"))
    orchestrator = SignedBus(inner=inner, identity=_ident("mon-b"), registry=registry)
    got: list = []
    orchestrator.subscribe(TOPIC, lambda m: got.append(m))

    compromised.publish(TOPIC, _update(node_id="n-b", level=0.01, agent_id="mon-b"))
    assert got == [], "a report naming another monitor is not delivered"
    assert orchestrator.rejected == [("mon-a", "agent_mismatch")]

    compromised.publish(TOPIC, _update(node_id="n-a", level=0.01, agent_id="mon-a"))
    assert [m.agent_id for m in got] == ["mon-a"]


def test_an_unattributable_sender_maps_to_untrusted_provenance() -> None:
    bus, _, _ = _wired()
    assert bus.provenance_for("mon-a") is Provenance.HIGH
    assert bus.provenance_for("stranger") is Provenance.UNTRUSTED


def test_non_strict_mode_passes_unsigned_through_but_still_counts_it() -> None:
    inner = InProcBus()
    bus = SignedBus(
        inner=inner,
        identity=_ident("mon-a"),
        registry={"mon-a": _ident("mon-a")},
        strict=False,
    )
    got: list = []
    bus.subscribe(TOPIC, lambda m: got.append(m))
    inner.publish(TOPIC, _update())
    assert len(got) == 1, "opt-in migration path"
    assert bus.rejected == [("<unsigned>", "not_signed")]


def test_plaintext_is_the_explicit_default() -> None:
    cfg = TLSConfig()
    cfg.validate()
    assert cfg.describe() == "plaintext"
    assert cfg.mutual is False


def test_tls_without_a_ca_is_refused() -> None:
    """Verifying an internal broker against the public trust store is not a check."""
    with pytest.raises(ValueError, match="CA certificate"):
        TLSConfig(enabled=True).validate()


def test_missing_certificate_material_fails_at_construction(tmp_path) -> None:
    with pytest.raises(ValueError, match="not found"):
        TLSConfig(enabled=True, ca_cert=tmp_path / "absent.pem").validate()


def test_mutual_tls_is_detected_and_described(tmp_path) -> None:
    ca = tmp_path / "ca.pem"
    ca.write_text("x")
    crt = tmp_path / "c.pem"
    crt.write_text("x")
    key = tmp_path / "c.key"
    key.write_text("x")
    cfg = TLSConfig(enabled=True, ca_cert=ca, client_cert=crt, client_key=key)
    cfg.validate()
    assert cfg.mutual is True
    assert cfg.describe() == "mTLS"


def test_a_half_configured_client_identity_is_refused(tmp_path) -> None:
    ca = tmp_path / "ca.pem"
    ca.write_text("x")
    crt = tmp_path / "c.pem"
    crt.write_text("x")
    with pytest.raises(ValueError, match="supplied together"):
        TLSConfig(enabled=True, ca_cert=ca, client_cert=crt).validate()


def test_server_only_tls_is_described_as_such(tmp_path) -> None:
    """Naming it matters: with server-only TLS anything reachable may publish."""
    ca = tmp_path / "ca.pem"
    ca.write_text("x")
    cfg = TLSConfig(enabled=True, ca_cert=ca)
    cfg.validate()
    assert cfg.describe() == "TLS (server-authenticated only)"
