"""Attesters in their own processes: the broker protocol, on a fake broker."""

from __future__ import annotations

from dataclasses import dataclass, field

from deploy.remote_attesters import (
    AttesterService,
    RemoteAttesters,
    SealedPublisher,
    attester_user,
)
from m11_memory_hardening.quorum import Attestation, MemoryCandidate
from shared.redis_bus import RedisBus
from tests.test_redis_bus import _Broker, _Client

NAMES = ("verifier", "correlation", "fusion", "orchestrator", "monitoring")


@dataclass
class _Attester:
    """Signs a candidate once it has seen a batch at or after the candidate's window."""

    name: str
    sign: bool = True
    seen: list[float] = field(default_factory=list)

    def observe(self, batch) -> None:
        self.seen.append(batch.sim_time)

    def review(self, candidate: MemoryCandidate, *, sim_time: float) -> Attestation | None:
        if not self.sign or not any(t >= candidate.window_end_sim for t in self.seen):
            return None
        return Attestation(
            record_hash="a" * 64, attester_id=self.name, signature="b" * 128, sim_time=sim_time
        )


@dataclass
class _Batch:
    sim_time: float
    run_id: str = "r"
    seed: int = 1
    config_hash: str = "h"
    updates: tuple = ()
    over_budget_agents: tuple = ()


def _candidate(end: float = 5.0) -> MemoryCandidate:
    return MemoryCandidate(
        record_id="rec-1",
        pattern_text="campaign",
        threat_type="device_compromise",
        node_ids=("node-1",),
        window_start_sim=0.0,
        window_end_sim=end,
        run_id="r",
        seed=1,
        config_hash="h",
        proposer_id="memory-curator",
    )


def _wire(*, declining: tuple[str, ...] = ()):
    broker = _Broker()
    control = RedisBus(_Client(broker), publisher="control")
    services = [
        AttesterService(
            _Attester(n, sign=n not in declining),
            RedisBus(_Client(broker), publisher=attester_user(n)),
        )
        for n in NAMES
    ]

    def poll() -> None:
        for service in services:
            service.step(timeout=0)
        control.pump()

    return control, services, RemoteAttesters(control, NAMES, poll=poll, max_polls=5)


def test_every_attester_that_saw_the_evidence_signs_on_its_own_stream() -> None:
    control, services, remote = _wire()
    SealedPublisher(control).observe(_Batch(sim_time=5.0))
    signed = remote.collect(_candidate(), sim_time=6.0)
    assert sorted(a.attester_id for a in signed) == sorted(NAMES)
    assert all(s.signed == 1 for s in services) and remote.timed_out == 0


def test_a_candidate_that_outruns_its_batch_waits_instead_of_being_refused() -> None:
    control, services, remote = _wire()
    publisher = SealedPublisher(control)
    polls = iter(range(10))

    def poll() -> None:
        if next(polls) == 1:
            publisher.observe(_Batch(sim_time=5.0))
        for service in services:
            service.step(timeout=0)
        control.pump()

    remote.poll = poll
    signed = remote.collect(_candidate(), sim_time=6.0)
    assert len(signed) == len(NAMES)
    assert all(s.declined == 0 for s in services)


def test_an_attester_that_declines_is_simply_missing_and_the_wait_is_bounded() -> None:
    control, _, remote = _wire(declining=("fusion", "monitoring"))
    SealedPublisher(control).observe(_Batch(sim_time=5.0))
    signed = remote.collect(_candidate(), sim_time=6.0)
    assert sorted(a.attester_id for a in signed) == sorted(set(NAMES) - {"fusion", "monitoring"})
    assert remote.timed_out == 1


def test_signatures_for_another_request_are_not_counted() -> None:
    control, _, remote = _wire()
    SealedPublisher(control).observe(_Batch(sim_time=5.0))
    first = remote.collect(_candidate(), sim_time=6.0)
    second = remote.collect(_candidate(end=5.0), sim_time=7.0)
    assert len(first) == len(second) == len(NAMES)
    assert all(a.sim_time == 7.0 for a in second), "each request gathers only its own replies"


def test_a_fifty_device_batch_crosses_the_frame_limit_in_parts_and_arrives_whole() -> None:
    """
    A whole 50-device batch is about 20 KB, over the broker's 16,000-byte frame limit: sent as one
    frame, every attester silently dropped it.
    """
    from shared.schemas import ContextVector, Provenance, TrustUpdate

    updates = tuple(
        TrustUpdate(
            sim_time=5.0,
            run_id="r",
            seed=1,
            config_hash="h",
            node_id=f"node-{i}",
            node_trust=0.9123456789012345,
            observation=0.8123456789012345,
            context=ContextVector(
                identity=0.9876543210987654,
                behavioral=0.8765432109876543,
                device=0.7654321098765432,
                network=0.6543210987654321,
            ),
            provenance=Provenance.HIGH,
            agent_id=f"mon-node-{i}",
        )
        for i in range(50)
    )
    seen: list = []
    broker = _Broker()
    control = RedisBus(_Client(broker), publisher="control")
    attester = _Attester("verifier")
    attester.observe = seen.append  # type: ignore[method-assign]
    service = AttesterService(attester, RedisBus(_Client(broker), publisher=attester_user("v")))
    SealedPublisher(control).observe(_Batch(sim_time=5.0, updates=updates))
    for _ in range(5):
        service.step(timeout=0)
    assert not service.bus.dropped
    assert [u.node_id for u in seen[0].updates] == [u.node_id for u in updates]
    assert service.observed_until == 5.0
