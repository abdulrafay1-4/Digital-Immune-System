"""A device's sensor in its own process, holding the only copy of the device's key."""

from __future__ import annotations

import pytest

from m1_monitoring.sensors.attested import AttestedTelemetry
from m1_monitoring.sensors.remote import MissingMeasurement, RemoteSensor, SensorService
from m1_monitoring.sensors.synthetic import SyntheticTelemetry
from m10_persona_drift.nhi import issue_signing_identity
from shared.attestation import attestation_payload
from shared.redis_bus import RedisBus
from tests.test_redis_bus import _Broker, _Client

DEVICE = issue_signing_identity("node-1", seed=b"d" * 32)


def _link():
    broker = _Broker()
    sensor = SensorService(
        AttestedTelemetry(SyntheticTelemetry(7), {"node-1": DEVICE}),
        RedisBus(_Client(broker), publisher="sensor-node-1"),
        "node-1",
        "wire",
        7,
        "h",
    )
    monitor = RemoteSensor(RedisBus(_Client(broker), publisher="mon-node-1"), "node-1", max_polls=2)
    return sensor, monitor


def test_the_monitor_relays_what_the_device_signed() -> None:
    sensor, monitor = _link()
    sensor.measure(3.0)
    context, _ = monitor.read(3.0, "node-1")
    signature = monitor.attestation(3.0, "node-1")
    assert DEVICE.public().verify(attestation_payload("node-1", 3.0, context), signature)


def test_a_monitor_without_the_key_cannot_sign_a_context_it_made_up() -> None:
    sensor, monitor = _link()
    sensor.measure(3.0)
    context, _ = monitor.read(3.0, "node-1")
    forged = context.model_copy(update={"device": 0.99, "network": 0.99})
    signature = monitor.attestation(3.0, "node-1")
    assert not DEVICE.public().verify(attestation_payload("node-1", 3.0, forged), signature)


def test_a_tick_the_device_did_not_measure_is_silence() -> None:
    sensor, monitor = _link()
    sensor.measure(3.0)
    with pytest.raises(MissingMeasurement):
        monitor.read(4.0, "node-1")


def test_the_broker_gives_the_sensor_its_stream_and_the_monitor_read_access_only() -> None:
    from deploy.wire import acl_file, broker_users

    acl = acl_file({u: "pw" for u in broker_users()}).decode().splitlines()
    (sensor,) = [x for x in acl if x.startswith("user sensor-node-1 ")]
    assert [p for p in sensor.split() if p.startswith("~")] == [
        "~dis:device.measurement:sensor-node-1"
    ]
    assert "+xread" not in sensor
    (monitor,) = [x for x in acl if x.startswith("user mon-node-1 ")]
    assert "%R~dis:device.measurement:sensor-node-1" in monitor
