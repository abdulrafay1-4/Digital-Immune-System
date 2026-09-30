"""RedisBus: the wire carries signed telemetry intact and drops anything else."""

from __future__ import annotations

import json
from collections import defaultdict
from fnmatch import fnmatch

from m1_monitoring.agent import TRUST_TOPIC
from m1_monitoring.core.context_vector import make_context
from m10_persona_drift.nhi import issue_identity
from shared.provenance import tag_synthetic
from shared.redis_bus import MAX_FRAME_BYTES, PER_STREAM, RedisBus, stream_key
from shared.schemas import TrustUpdate
from shared.secure_bus import SignedBus, _Envelope


class _Broker:
    """Redis streams, enough of them: append with a cap, read after an id, list keys."""

    def __init__(self) -> None:
        self.streams: dict[str, list[tuple[bytes, dict]]] = defaultdict(list)
        self.seq = 0


class _Client:
    def __init__(self, broker: _Broker) -> None:
        self.broker = broker

    def xadd(self, name, fields, maxlen=None, approximate=True):
        self.broker.seq += 1
        entry_id = f"{self.broker.seq}-0".encode()
        stream = self.broker.streams[name]
        stream.append((entry_id, {k.encode(): v for k, v in fields.items()}))
        if maxlen is not None:
            del stream[:-maxlen]
        return entry_id

    def xread(self, streams, count=None, block=None):
        out = []
        for key, after in streams.items():
            after_seq = int(str(after).split("-")[0])
            rows = [e for e in self.broker.streams[key] if int(e[0].split(b"-")[0]) > after_seq]
            if rows:
                out.append([key.encode(), rows[:count]])
        return out

    def scan_iter(self, match, count=None):
        return [k.encode() for k in list(self.broker.streams) if fnmatch(k, match)]


AGENT = "mon-node-0"
KEY = issue_identity(AGENT, seed=b"k" * 32)


def _update(trust: float = 0.9) -> TrustUpdate:
    return TrustUpdate(
        sim_time=3.0,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id="node-0",
        node_trust=trust,
        observation=trust,
        context=make_context(trust, trust, trust, trust),
        provenance=tag_synthetic(),
        agent_id=AGENT,
    )


def _pair():
    broker = _Broker()
    publisher = RedisBus(_Client(broker), publisher=AGENT)
    subscriber = RedisBus(_Client(broker), publisher="control")
    verified = SignedBus(
        inner=subscriber, identity=KEY, registry={AGENT: KEY}, topics=frozenset({TRUST_TOPIC})
    )
    received: list = []
    verified.subscribe(TRUST_TOPIC, received.append)
    return publisher, subscriber, verified, received


def test_signed_telemetry_crosses_the_wire_and_verifies() -> None:
    publisher, subscriber, verified, received = _pair()
    SignedBus(inner=publisher, identity=KEY, topics=frozenset({TRUST_TOPIC})).publish(
        TRUST_TOPIC, _update()
    )
    assert subscriber.pump() == 1
    assert received == [_update()]
    assert verified.rejected_count == 0


def test_everything_an_insider_without_the_key_can_send_is_refused() -> None:
    publisher, subscriber, verified, received = _pair()
    rogue = issue_identity(AGENT, seed=b"x" * 32)
    SignedBus(inner=publisher, identity=rogue, topics=frozenset({TRUST_TOPIC})).publish(
        TRUST_TOPIC, _update(0.05)
    )
    publisher.publish(TRUST_TOPIC, _update(0.05))
    genuine = _Envelope(TRUST_TOPIC, _update(), AGENT, KEY.sign(b"not this message"))
    publisher.publish(TRUST_TOPIC, genuine)
    subscriber.pump()
    assert received == []
    assert sorted(r for _, r in verified.rejected) == [
        "bad_signature",
        "bad_signature",
        "not_signed",
    ]


def test_tampering_after_signing_is_refused() -> None:
    publisher, subscriber, verified, received = _pair()
    captured: list = []
    publisher.subscribe(TRUST_TOPIC, captured.append)
    SignedBus(inner=publisher, identity=KEY, topics=frozenset({TRUST_TOPIC})).publish(
        TRUST_TOPIC, _update()
    )
    publisher.pump()
    subscriber.pump()
    genuine = captured[0]
    altered = genuine.model.model_copy(update={"node_trust": 0.05})
    publisher.publish(
        TRUST_TOPIC, _Envelope(genuine.topic, altered, genuine.sender, genuine.signature)
    )
    subscriber.pump()
    assert received == [_update()]
    assert [r for _, r in verified.rejected] == ["bad_signature"]


def test_malformed_frames_are_dropped_before_any_subscriber() -> None:
    publisher, subscriber, verified, received = _pair()
    raw = publisher.client
    stream = stream_key(TRUST_TOPIC, AGENT)

    def send(frame: bytes) -> None:
        raw.xadd(stream, {"f": frame})

    send(b"\x00not json")
    send(b"[1, 2]")
    send(b'{"type": "Nope", "body": "{}"}')
    send(b'{"type": "TrustUpdate", "body": "{\\"node_id\\": 5}"}')
    send(b"x" * (MAX_FRAME_BYTES + 1))
    unsigned = {"type": "TrustUpdate", "body": _update().model_dump_json(), "sender": AGENT}
    send(json.dumps(unsigned).encode())
    assert subscriber.pump() == 6
    assert subscriber.delivered == 0
    assert received == [] and verified.rejected_count == 0
    assert dict(subscriber.dropped) == {
        "not_json": 1,
        "malformed": 2,
        "unknown_type": 1,
        "invalid": 1,
        "oversized": 1,
    }


def test_a_failing_subscriber_does_not_stop_delivery() -> None:
    broker = _Broker()
    publisher = RedisBus(_Client(broker), publisher="a")
    subscriber = RedisBus(_Client(broker), publisher="b")
    seen: list = []

    def broken(_):
        raise RuntimeError("disk full")

    subscriber.subscribe("x", broken)
    subscriber.subscribe("x", seen.append)
    publisher.publish("x", _update())
    subscriber.pump()
    assert seen == [_update()]
    assert subscriber.handler_errors == 1


def test_a_flooded_stream_cannot_starve_the_others() -> None:
    """One publisher's flood is read a slice at a time; everyone else still arrives."""
    broker = _Broker()
    honest = RedisBus(_Client(broker), publisher=AGENT)
    flooder = RedisBus(_Client(broker), publisher="mon-node-9")
    subscriber = RedisBus(_Client(broker), publisher="control")
    verified = SignedBus(
        inner=subscriber, identity=KEY, registry={AGENT: KEY}, topics=frozenset({TRUST_TOPIC})
    )
    received: list = []
    verified.subscribe(TRUST_TOPIC, received.append)
    for _ in range(1000):
        flooder.client.xadd(stream_key(TRUST_TOPIC, "mon-node-9"), {"f": b"junk"}, maxlen=128)
    SignedBus(inner=honest, identity=KEY, topics=frozenset({TRUST_TOPIC})).publish(
        TRUST_TOPIC, _update()
    )
    handled = subscriber.pump()
    assert received == [_update()]
    assert handled <= 1 + 8 * PER_STREAM
    assert len(broker.streams[stream_key(TRUST_TOPIC, "mon-node-9")]) == 128


def test_a_signature_naming_someone_other_than_the_stream_owner_is_dropped() -> None:
    publisher, subscriber, verified, received = _pair()
    intruder = RedisBus(publisher.client, publisher="mon-node-2")
    SignedBus(inner=intruder, identity=KEY, topics=frozenset({TRUST_TOPIC})).publish(
        TRUST_TOPIC, _update()
    )
    subscriber.pump()
    assert received == [] and verified.rejected_count == 0
    assert subscriber.dropped == {"sender_mismatch": 1}
