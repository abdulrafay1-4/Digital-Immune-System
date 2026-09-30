"""The operator console reading the container deployment's streams, on a fake broker."""

from __future__ import annotations

import time

from fastapi.testclient import TestClient

from agents.planner import PLAN_TOPIC
from console.accounts import Accounts
from console.app import create_app
from console.stream import AUDIT_TOPIC, READ_ONLY, StreamFleet
from m6_trust_fusion.fusion import GT_TOPIC
from shared.redis_bus import RedisBus
from shared.schemas import AuditRecord, GlobalTrustUpdate, ResponsePlan
from tests.test_redis_bus import _Broker, _Client

NODES = ["node-0", "node-1"]
BASE = {"run_id": "wire", "seed": 7, "config_hash": "h"}


def _gt(node: str, t: float, gt: float) -> GlobalTrustUpdate:
    return GlobalTrustUpdate(
        **BASE, sim_time=t, node_id=node, gt=gt, ts=gt, cti_i=0.0, cti_trust=1.0, rep=1.0,
        master_score=gt,
    )  # fmt: skip


def _executed(node: str, t: float, level: int, **flags: bool) -> AuditRecord:
    return AuditRecord(
        **BASE,
        sim_time=t,
        event_type="response.executed",
        actor_id="m4",
        payload={"node_id": node, "proposed_level": level, **flags},
    )


def _deployment() -> tuple[RedisBus, StreamFleet]:
    broker = _Broker()
    control = RedisBus(_Client(broker), publisher="control")
    return control, StreamFleet(RedisBus(_Client(broker), publisher="console"), NODES)


def _tick(control: RedisBus, t: float, node: str, gt: float, level: int, **flags: bool) -> None:
    control.publish(GT_TOPIC, _gt(node, t, gt))
    plan = ResponsePlan(**BASE, sim_time=t, node_id=node, proposed_level=level)
    control.publish(PLAN_TOPIC, plan)
    control.publish(AUDIT_TOPIC, _executed(node, t, level, **flags))


def test_the_console_shows_what_the_control_plane_did_not_what_it_planned() -> None:
    control, fleet = _deployment()
    _tick(control, 1, "node-1", 0.1, 4, isolation_withheld=True)
    _tick(control, 2, "node-0", 0.9, 0)
    fleet.step(timeout=0)
    row = {d["id"]: d for d in fleet.snapshot()["devices"]}["node-1"]
    assert row["gt"] == 0.1 and row["planned"] == 4
    assert row["level"] == 3 and row["isolation_withheld"], "unapproved isolation is restriction"
    assert fleet.worst == {"node-0": 0, "node-1": 3}
    assert any("raised to L3" in e["text"] for e in fleet.snapshot()["events"])
    assert [t["t"] for t in fleet.tick_history()] == [1, 2]
    assert fleet.tick_history()[0]["levels"] == {"4": 1}
    assert fleet.device_detail("node-1")["history"][0]["level"] == 3


def test_the_brake_and_a_refusal_read_as_the_engine_carried_them_out() -> None:
    control, fleet = _deployment()
    _tick(control, 1, "node-0", 0.3, 3, restriction_withheld=True)
    control.publish(
        AUDIT_TOPIC,
        AuditRecord(
            **BASE,
            sim_time=1,
            event_type="response.denied",
            actor_id="m4",
            payload={"node_id": "node-1", "proposed_level": 3, "deny_reason": "stale_token"},
        ),
    )
    fleet.step(timeout=0)
    rows = {d["id"]: d for d in fleet.snapshot()["devices"]}
    assert rows["node-0"]["level"] == 2, "a braked restriction is re-authentication"
    assert rows["node-1"]["level"] == 0, "a refused action did nothing"
    assert any("refused: stale_token" in e["text"] for e in fleet.snapshot()["events"])


def test_only_the_control_planes_streams_are_read() -> None:
    broker = _Broker()
    fleet = StreamFleet(RedisBus(_Client(broker), publisher="console"), NODES)
    RedisBus(_Client(broker), publisher="mon-node-0").publish(GT_TOPIC, _gt("node-0", 1, 0.05))
    fleet.step(timeout=0)
    assert fleet.snapshot()["devices"][0]["gt"] is None


def test_every_command_is_refused_and_every_screen_still_reads(tmp_path) -> None:
    control, fleet = _deployment()
    _tick(control, 1, "node-1", 0.1, 4, isolation_withheld=True)
    _tick(control, 2, "node-1", 0.1, 4, isolation_withheld=True)
    fleet.step(timeout=0)
    accounts = Accounts(tmp_path / "accounts.db", now=time.time)
    accounts.create("op", "op-password-123", "operator")
    client = TestClient(create_app(accounts, fleet))
    client.post("/api/login", json={"username": "op", "password": "op-password-123"})
    state = client.get("/api/state").json()
    assert state["read_only"] and state["tick"] == 2
    assert client.get("/api/devices/node-1").json()["history"][0]["level"] == 3
    refused = client.post(
        "/api/approvals/node-1",
        json={"approved": True, "reason": "looks bad"},
        headers={"X-DIS-Console": "1"},
    )
    assert refused.status_code == 400 and READ_ONLY in refused.text


def test_the_broker_lets_the_console_read_the_control_plane_and_write_only_its_answers() -> None:
    from deploy.wire import acl_file, broker_users

    acl = acl_file({u: "pw" for u in broker_users()}).decode().splitlines()
    (line,) = [x for x in acl if x.startswith("user console ")]
    assert "%R~dis:*:control" in line and "+xread" in line
    assert [p for p in line.split() if p.startswith("~")] == ["~dis:operator.decision:console"]
    assert "+set" not in line and "+scan" not in line


def test_a_tick_is_shown_once_every_stage_has_arrived() -> None:
    from agents.correlation import CORRELATION_TOPIC
    from console.stream import CLASSIFICATION_TOPIC, VERIFIER_EVENT
    from shared.schemas import Classification, CorrelationResult

    control, fleet = _deployment()
    _tick(control, 1, "node-1", 0.3, 3)
    control.publish(
        CORRELATION_TOPIC,
        CorrelationResult(
            **BASE, sim_time=1, node_ids=NODES, cti=0.5, implicated_node_ids=["node-1"]
        ),
    )
    fleet.step(timeout=0)
    assert fleet.snapshot()["last_tick"] is None, "the screens read every stage together"
    control.publish(
        CLASSIFICATION_TOPIC,
        Classification(**BASE, sim_time=1, threat_type="device_compromise", severity=0.7),
    )
    for event, payload in (
        ("orchestrator.batch_sealed", {"n_updates": 2}),
        (VERIFIER_EVENT, {"verdict": "pass", "findings": []}),
    ):
        control.publish(
            AUDIT_TOPIC,
            AuditRecord(**BASE, sim_time=1, event_type=event, actor_id="x", payload=payload),
        )
    fleet.step(timeout=0)
    last = fleet.snapshot()["last_tick"]
    assert last["sealed"] and last["t"] == 1 and last["reports"] == 2
    assert last["correlation"]["implicated"] == ["node-1"]
    assert last["executed"] == {"node-1": 3} and last["verifier"]["verdict"] == "pass"
