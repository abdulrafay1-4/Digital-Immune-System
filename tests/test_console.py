"""The operator console: accounts, roles, and the live loop answering an operator."""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

from console.accounts import Accounts, AuthError
from console.app import create_app
from console.runtime import LiveFleet

HEADERS = {"X-DIS-Console": "1"}


@pytest.fixture(scope="module")
def console(tmp_path_factory):
    accounts = Accounts(tmp_path_factory.mktemp("console") / "accounts.db", now=time.time)
    for name, role in (("admin", "admin"), ("op", "operator"), ("aud", "auditor")):
        accounts.create(name, f"{name}-password-123", role)
    fleet = LiveFleet(n_nodes=20, tick_seconds=0.02)
    fleet.start()
    app = create_app(accounts, fleet)
    yield app, accounts, fleet
    fleet.stop()


def _client(app, user: str) -> TestClient:
    client = TestClient(app)
    response = client.post(
        "/api/login", json={"username": user, "password": f"{user}-password-123"}
    )
    assert response.status_code == 200, response.text
    return client


def _wait(client: TestClient, predicate, timeout: float = 30.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        state = client.get("/api/state").json()
        if state.get("ready") and predicate(state):
            return state
        time.sleep(0.05)
    raise AssertionError("condition not reached")


def test_passwords_and_sessions(tmp_path) -> None:
    clock = [1000.0]
    accounts = Accounts(tmp_path / "a.db", now=lambda: clock[0])
    accounts.create("alice", "correct-horse-1", "operator")
    with pytest.raises(AuthError):
        accounts.create("alice", "another-pass-1", "auditor")
    with pytest.raises(AuthError):
        accounts.create("bob", "short", "auditor")
    user, token = accounts.login("alice", "correct-horse-1")
    assert accounts.session(token) == user
    raw = accounts._db.execute("SELECT token_hash FROM sessions").fetchone()[0]
    assert token not in raw, "only a hash of the session token is stored"
    for _ in range(5):
        with pytest.raises(AuthError):
            accounts.login("alice", "wrong")
    with pytest.raises(AuthError, match="too many"):
        accounts.login("alice", "correct-horse-1")
    clock[0] += 9 * 3600
    assert accounts.session(token) is None, "sessions expire"
    with pytest.raises(AuthError, match="last active administrator"):
        accounts.create("root", "root-password-1", "admin")
        accounts.update("root", active=False)


def test_roles_and_the_console_header(console) -> None:
    app, _, _ = console
    anonymous = TestClient(app)
    assert anonymous.get("/api/state").status_code == 401
    auditor = _client(app, "aud")
    assert auditor.get("/api/state").status_code == 200
    assert (
        auditor.post("/api/attacks", json={"kind": "compromise"}, headers=HEADERS).status_code
        == 403
    )
    assert (
        auditor.post("/api/approvals/node-0", json={"approved": True}, headers=HEADERS).status_code
        == 403
    )
    operator = _client(app, "op")
    assert operator.get("/api/users").status_code == 403
    assert operator.post("/api/fleet", json={"action": "pause"}, headers=HEADERS).status_code == 403
    assert operator.post("/api/attacks", json={"kind": "compromise"}).status_code == 403
    admin = _client(app, "admin")
    created = admin.post(
        "/api/users",
        json={"username": "newbie", "password": "newbie-password-1", "role": "auditor"},
        headers=HEADERS,
    )
    assert created.status_code == 200
    assert (
        admin.patch("/api/users/admin", json={"active": False}, headers=HEADERS).status_code == 400
    )


def test_an_attack_is_answered_and_isolation_waits_for_a_person(console) -> None:
    app, _, _ = console
    operator = _client(app, "op")
    launched = operator.post(
        "/api/attacks",
        json={"kind": "compromise", "severity": 0.8, "duration": 60},
        headers=HEADERS,
    )
    assert launched.status_code == 200, launched.text
    target = launched.json()["targets"][0]
    state = _wait(
        operator, lambda s: any(p["node_id"] == target for p in s["approvals"]["pending"])
    )
    device = next(d for d in state["devices"] if d["id"] == target)
    assert device["level"] == 3, "isolation is carried out as restriction until someone decides"
    decided = operator.post(
        f"/api/approvals/{target}", json={"approved": True, "reason": "confirmed"}, headers=HEADERS
    )
    assert decided.status_code == 200
    state = _wait(
        operator, lambda s: any(d["id"] == target and d["level"] == 4 for d in s["devices"])
    )
    assert state["approvals"]["history"][0]["decided_by"] == "operator:op"
    assert any(e["source"] == "operator" for e in state["events"])
    assert (
        operator.post(
            "/api/approvals/node-19", json={"approved": True}, headers=HEADERS
        ).status_code
        == 400
    )


def test_a_question_whose_episode_ended_is_withdrawn_not_left_to_answer(console) -> None:
    app, _, fleet = console
    operator = _client(app, "op")
    launched = operator.post(
        "/api/attacks",
        json={"kind": "compromise", "severity": 0.8, "duration": 12},
        headers=HEADERS,
    )
    assert launched.status_code == 200, launched.text
    target = launched.json()["targets"][0]
    _wait(operator, lambda s: any(p["node_id"] == target for p in s["approvals"]["pending"]))
    state = _wait(
        operator,
        lambda s: all(p["node_id"] != target for p in s["approvals"]["pending"]),
        timeout=60.0,
    )
    assert not any(h["node_id"] == target for h in state["approvals"]["history"])
    assert any("withdrawn" in e["text"] and e.get("node") == target for e in state["events"])
    assert target not in fleet.policy.answers
    stale = operator.post(
        f"/api/approvals/{target}", json={"approved": True, "reason": "late"}, headers=HEADERS
    )
    assert stale.status_code == 400


def test_the_gate_says_when_a_question_has_closed() -> None:
    from agents.approval import ApprovalGate, ApprovalRequest
    from console.runtime import ConsoleApproval

    policy = ConsoleApproval()
    gate = ApprovalGate(policy)

    def ask(level: int, t: float):
        return gate.review(
            ApprovalRequest(
                sim_time=t, run_id="r", seed=1, config_hash="h", node_id="n1", level=level
            )
        )

    assert ask(4, 1.0).approved is False
    assert gate.is_open("n1") and "n1" in policy.pending
    ask(2, 2.0)
    assert not gate.is_open("n1")
    assert not gate.is_open("fleet")


def test_defender_attacks_are_refused_where_they_should_be(console) -> None:
    app, _, _ = console
    operator = _client(app, "op")
    for kind in ("impersonation", "memory_poison"):
        assert (
            operator.post(
                "/api/attacks", json={"kind": kind, "duration": 8}, headers=HEADERS
            ).status_code
            == 200
        )
    state = _wait(
        operator,
        lambda s: (
            s["counters"].get("telemetry_refused", 0) > 0
            and s["counters"].get("poison_attempts", 0) > 1
        ),
    )
    assert state["counters"]["poison_accepted"] == 0
    victim = next(a for a in state["attacks"] if a["kind"] == "impersonation")["targets"][0]["id"]
    assert next(d for d in state["devices"] if d["id"] == victim)["level"] == 0
    assert (
        operator.post("/api/attacks", json={"kind": "nonsense"}, headers=HEADERS).status_code == 400
    )


def test_evaluation_tables_come_from_the_results(console) -> None:
    app, _, _ = console
    tables = _client(app, "aud").get("/api/evaluation").json()
    assert "metrics" in tables
    if "fyp" in tables:
        assert {a["id"] for a in tables["fyp"]["arms"]} >= {"full", "binary_zt"}


def test_kiosk_is_off_unless_asked_and_only_for_this_machine(console, tmp_path) -> None:
    app, accounts, fleet = console
    assert TestClient(app).post("/api/kiosk", headers=HEADERS).status_code == 404
    kiosk_app = create_app(accounts, fleet, kiosk_user="aud")
    remote = TestClient(kiosk_app)
    assert remote.get("/api/kiosk").json() == {"enabled": False, "username": None}
    assert remote.post("/api/kiosk", headers=HEADERS).status_code == 404
