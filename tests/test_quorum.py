"""M11 quorum gate: the security properties, not just the happy path."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from m10_persona_drift.nhi import issue_identity
from m11_memory_hardening.quorum import (
    Attestation,
    MemoryCandidate,
    QuorumGate,
    QuorumParams,
    RejectReason,
    attest,
    verify_certificate,
)

ATTESTERS = ("verifier", "correlation", "fusion", "orchestrator", "monitoring")
PROPOSER = "memory-curator"
NOW = 10.0


def _registry(names: tuple[str, ...] = ATTESTERS) -> dict:
    return {n: issue_identity(n, seed=n.encode().ljust(32, b"\0")) for n in names}


def _candidate(**over) -> MemoryCandidate:
    base = dict(
        record_id="rec-1",
        pattern_text="three controllers sliding together on device+network",
        threat_type="device_compromise",
        node_ids=("n-0312", "n-0455", "n-0781"),
        window_start_sim=45.0,
        window_end_sim=51.0,
        run_id="r",
        seed=1,
        config_hash="h",
        proposer_id=PROPOSER,
    )
    base.update(over)
    return MemoryCandidate(**base)


def _gate(**over) -> QuorumGate:
    kw = dict(registry=_registry(), params=QuorumParams())
    kw.update(over)
    return QuorumGate(**kw)


def _sign(names, candidate, registry, *, sim_time=NOW):
    return [attest(candidate, registry[n], sim_time=sim_time) for n in names]


def test_three_of_five_admits_and_issues_a_certificate() -> None:
    reg = _registry()
    cand = _candidate()
    gate = _gate(registry=reg)
    d = gate.admit(cand, _sign(ATTESTERS[:3], cand, reg), now_sim=NOW)
    assert d.admitted is True
    assert d.accepted == tuple(sorted(ATTESTERS[:3]))
    assert d.certificate is not None
    assert d.k == 3 and d.n == 5
    assert verify_certificate(d.certificate, cand, reg) is True


def test_two_of_five_is_refused() -> None:
    reg = _registry()
    cand = _candidate()
    d = _gate(registry=reg).admit(cand, _sign(ATTESTERS[:2], cand, reg), now_sim=NOW)
    assert d.admitted is False
    assert d.certificate is None
    assert d.shortfall == 1


def test_no_attestations_at_all_is_refused() -> None:
    d = _gate().admit(_candidate(), [], now_sim=NOW)
    assert d.admitted is False


def test_certificate_is_deterministic() -> None:
    reg = _registry()
    cand = _candidate()
    gate = _gate(registry=reg)
    a = gate.admit(cand, _sign(ATTESTERS[:3], cand, reg), now_sim=NOW)
    b = gate.admit(cand, _sign(tuple(reversed(ATTESTERS[:3])), cand, reg), now_sim=NOW)
    assert a.certificate == b.certificate, "attestation order must not change the certificate"


def test_node_id_order_does_not_change_the_record_hash() -> None:
    a = _candidate(node_ids=("n-0312", "n-0455", "n-0781"))
    b = _candidate(node_ids=("n-0781", "n-0312", "n-0455"))
    assert a.record_hash() == b.record_hash()


def test_rule1_signatures_over_a_different_record_do_not_count() -> None:
    """Collecting signatures on five slightly different records must not assemble."""
    reg = _registry()
    cand = _candidate()
    other = _candidate(record_id="rec-2", pattern_text="something else")
    mixed = _sign(ATTESTERS[:1], cand, reg) + _sign(ATTESTERS[1:3], other, reg)

    d = _gate(registry=reg).admit(cand, mixed, now_sim=NOW)
    assert d.admitted is False
    assert [r for _, r in d.rejected] == [RejectReason.WRONG_RECORD] * 2


def test_rule2_the_same_attester_three_times_is_one_vote() -> None:
    reg = _registry()
    cand = _candidate()
    one = _sign(("verifier",), cand, reg)
    d = _gate(registry=reg).admit(cand, one * 3, now_sim=NOW)
    assert d.admitted is False
    assert d.accepted == ("verifier",)
    assert [r for _, r in d.rejected] == [RejectReason.DUPLICATE] * 2


def test_rule3_the_proposer_cannot_vouch_for_itself() -> None:
    names = (*ATTESTERS, PROPOSER)
    reg = _registry(names)
    cand = _candidate()
    d = QuorumGate(registry=reg).admit(
        cand, _sign(("verifier", "correlation", PROPOSER), cand, reg), now_sim=NOW
    )
    assert d.admitted is False
    assert (PROPOSER, RejectReason.PROPOSER) in d.rejected


def test_rule4_quarantine_removes_a_vote_but_never_lowers_k() -> None:
    """Disabling attesters must make writing impossible, never easier."""
    reg = _registry()
    cand = _candidate()
    gate = _gate(registry=reg, quarantined=frozenset({"fusion", "orchestrator"}))

    d = gate.admit(cand, _sign(ATTESTERS[:4], cand, reg), now_sim=NOW)
    assert d.k == 3, "threshold must not track the healthy set"
    assert d.n == 5, "n is the registered set, not who is currently healthy"
    assert d.accepted == ("correlation", "verifier")
    assert d.admitted is False


def test_rule5_attestations_expire() -> None:
    reg = _registry()
    cand = _candidate()
    stale = _sign(ATTESTERS[:3], cand, reg, sim_time=NOW - 99.0)
    d = _gate(registry=reg).admit(cand, stale, now_sim=NOW)
    assert d.admitted is False
    assert [r for _, r in d.rejected] == [RejectReason.EXPIRED] * 3


def test_an_attestation_from_the_future_is_refused() -> None:
    reg = _registry()
    cand = _candidate()
    d = _gate(registry=reg).admit(
        cand, _sign(ATTESTERS[:3], cand, reg, sim_time=NOW + 5.0), now_sim=NOW
    )
    assert d.admitted is False


def test_an_unregistered_attester_never_counts() -> None:
    reg = _registry()
    rogue = issue_identity("rogue", seed=b"rogue".ljust(32, b"\0"))
    cand = _candidate()
    atts = _sign(ATTESTERS[:2], cand, reg) + [attest(cand, rogue, sim_time=NOW)]
    d = _gate(registry=reg).admit(cand, atts, now_sim=NOW)
    assert d.admitted is False
    assert ("rogue", RejectReason.UNKNOWN_ATTESTER) in d.rejected


def test_a_forged_signature_is_refused() -> None:
    reg = _registry()
    cand = _candidate()
    good = _sign(ATTESTERS[:2], cand, reg)
    forged = Attestation(
        record_hash=cand.record_hash(),
        attester_id="fusion",
        signature="0" * 64,
        sim_time=NOW,
    )
    d = _gate(registry=reg).admit(cand, [*good, forged], now_sim=NOW)
    assert d.admitted is False
    assert ("fusion", RejectReason.BAD_SIGNATURE) in d.rejected


def test_certificate_for_a_different_record_does_not_verify() -> None:
    reg = _registry()
    cand = _candidate()
    d = _gate(registry=reg).admit(cand, _sign(ATTESTERS[:3], cand, reg), now_sim=NOW)
    assert verify_certificate(d.certificate, _candidate(record_id="rec-2"), reg) is False


def test_certificate_below_k_does_not_verify() -> None:
    """Defence in depth: a hand-built certificate with too few signers is refused."""
    reg = _registry()
    cand = _candidate()
    h = cand.record_hash()
    thin = f"{h}|verifier:{reg['verifier'].sign(h.encode())}"
    assert verify_certificate(thin, cand, reg) is False


def test_params_reject_a_threshold_below_one() -> None:
    with pytest.raises(ValueError):
        QuorumParams(k=0)


_names = st.sampled_from(ATTESTERS)


@given(subset=st.lists(_names, max_size=2, unique=True))
def test_property_no_subset_smaller_than_k_ever_admits(subset: list[str]) -> None:
    reg = _registry()
    cand = _candidate()
    d = QuorumGate(registry=reg).admit(cand, _sign(tuple(subset), cand, reg), now_sim=NOW)
    assert d.admitted is False
    assert d.certificate is None


@given(name=_names, copies=st.integers(min_value=1, max_value=12))
def test_property_duplicating_one_attester_never_admits(name: str, copies: int) -> None:
    reg = _registry()
    cand = _candidate()
    one = _sign((name,), cand, reg)
    d = QuorumGate(registry=reg).admit(cand, one * copies, now_sim=NOW)
    assert d.admitted is False
    assert len(d.accepted) == 1


@given(
    left=st.lists(_names, min_size=1, max_size=5, unique=True),
    right=st.lists(_names, min_size=1, max_size=5, unique=True),
)
def test_property_signatures_spanning_two_hashes_never_admit(
    left: list[str], right: list[str]
) -> None:
    """Even with every attester signing, two different records cannot combine."""
    reg = _registry()
    cand = _candidate()
    other = _candidate(record_id="rec-other")
    atts = _sign(tuple(left), cand, reg) + _sign(tuple(right), other, reg)

    d = QuorumGate(registry=reg).admit(cand, atts, now_sim=NOW)
    if d.admitted:
        assert len(set(left)) >= QuorumParams().k
