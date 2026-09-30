"""A person's verdict on a remembered incident, in the container deployment."""

from __future__ import annotations

import pytest

from agents.context_broker import CORRELATION_CLIENT, CURATOR_CLIENT, InProcBroker
from agents.mcp_broker import CORE_CLIENT, MCP_AVAILABLE, McpBroker, OperatorVerdicts
from console.stream import DECISION_TOPIC, StreamFleet
from deploy.operator import BrokerAdjudicator
from m5_immune_memory import IncidentSummary
from m8_eval_harness.baselines.base import _memory
from m10_persona_drift.nhi import issue_signing_identity
from shared.attestation import verdict_payload
from shared.redis_bus import RedisBus
from shared.schemas import AdjudicationVerdict, Provenance
from tests.test_redis_bus import _Broker, _Client

pytestmark = pytest.mark.skipif(not MCP_AVAILABLE, reason="the mcp extra is not installed")

KEY = issue_signing_identity("console", seed=b"c" * 32)
STORE_KEY = b"k" * 32
BASE = {"run_id": "wire", "seed": 7, "config_hash": "h"}
CAMPAIGN = "three controllers sliding together on device and network dimensions"
CLIENTS = (CORRELATION_CLIENT, CURATOR_CLIENT, CORE_CLIENT)


def _memory_service(verdicts: bool = True):
    """Memory with one admitted, pending record, behind its MCP server."""
    query, writer, attesters = _memory("wire")
    query.adjudication_key = STORE_KEY
    result = writer.propose_and_submit(
        IncidentSummary(
            record_id="rec-1",
            node_ids=("node-1",),
            peak_level=3,
            threat_type="device_compromise",
            pattern_text=CAMPAIGN,
            window_start_sim=1.0,
            window_end_sim=5.0,
            **BASE,
        ),
        {n: a.identity for n, a in attesters.items()},
        now_sim=5.0,
    )
    assert result.admitted and result.record.status == "pending"
    broker = InProcBroker(query=query, write_path=writer, **BASE)
    client = McpBroker(
        inner=broker,
        identities={c: issue_signing_identity(c) for c in CLIENTS},
        verdicts=OperatorVerdicts(console=KEY.public(), key=STORE_KEY) if verdicts else None,
    ).at(6.0, Provenance.HIGH, fleet_size=4)
    return client, broker, result.record


def _verdict(status="confirmed", *, key=KEY, record="rec-1", signed_for="rec-1", asked=5.0):
    by = "operator:ana"
    return AdjudicationVerdict(
        **BASE,
        sim_time=asked,
        record_id=record,
        status=status,
        decided_by=by,
        signature=key.sign(verdict_payload("wire", signed_for, asked, status, by)),
    )


def test_a_verdict_the_console_signed_is_recorded_and_the_incident_recalled() -> None:
    client, broker, _ = _memory_service()
    assert not client.recognise(CAMPAIGN).recognised, "a pending record is never recalled"
    assert client.adjudicate(_verdict(), sim_time=6.0) == {"allowed": True, "reason": None}
    record = broker.store.get("rec-1")
    assert (record.status, record.adjudicated_by) == ("confirmed", "operator:ana")
    assert client.recognise(CAMPAIGN).recognised


@pytest.mark.parametrize(
    ("verdict", "reason"),
    [
        (_verdict(key=issue_signing_identity("console", seed=b"m" * 32)), "bad_verdict"),
        (_verdict(signed_for="rec-9"), "bad_verdict"),
        (_verdict(record="rec-9", signed_for="rec-9"), "unknown_record"),
    ],
)
def test_memory_records_no_verdict_the_console_did_not_sign_for_that_record(
    verdict: AdjudicationVerdict, reason: str
) -> None:
    client, broker, _ = _memory_service()
    assert client.adjudicate(verdict, sim_time=6.0) == {"allowed": False, "reason": reason}
    assert broker.store.get("rec-1").status == "pending"
    assert broker.denied[reason] == 1, "refusals are audited"


def test_a_decided_incident_cannot_be_flipped_by_a_later_verdict() -> None:
    client, broker, _ = _memory_service()
    client.adjudicate(_verdict("confirmed"), sim_time=6.0)
    later = client.adjudicate(_verdict("benign"), sim_time=6.0)
    assert later == {"allowed": False, "reason": "already_adjudicated"}
    assert broker.store.get("rec-1").status == "confirmed"


def test_only_the_core_relays_and_a_relay_cannot_be_replayed() -> None:
    client, broker, _ = _memory_service()
    fields = {
        "record_id": "rec-1",
        "status": "confirmed",
        "decided_by": "operator:ana",
        "asked_at": 5.0,
        "verdict": _verdict().signature,
    }
    as_curator = client._call("memory_adjudicate", CURATOR_CLIENT, fields, sim_time=6.0)
    assert as_curator == {"allowed": False, "reason": "not_the_core"}
    from tests.test_mcp_security import _raw

    signed = client.signed("memory_adjudicate", CORE_CLIENT, fields, 6.0)
    first = _raw(client, "memory_adjudicate", signed)
    again = _raw(client, "memory_adjudicate", signed)
    assert first["allowed"] and again == {"allowed": False, "reason": "stale_call"}


def test_a_memory_service_without_the_console_key_records_nothing() -> None:
    client, broker, _ = _memory_service(verdicts=False)
    assert client.adjudicate(_verdict(), sim_time=6.0) == {
        "allowed": False,
        "reason": "no_operator",
    }
    assert broker.store.get("rec-1").status == "pending"


def _deployment():
    client, broker, record = _memory_service()
    bus = _Broker()
    adjudicator = BrokerAdjudicator(RedisBus(_Client(bus), publisher="control"), client)
    console = StreamFleet(
        RedisBus(_Client(bus), publisher="console"), ["node-1"], run_id="wire", signer=KEY
    )
    adjudicator.ask(record, sim_time=5.0)
    console.step(timeout=0)
    return adjudicator, console, broker


def test_the_console_decides_and_memory_records_it_through_the_control_plane() -> None:
    adjudicator, console, broker = _deployment()
    assert [m["status"] for m in console.snapshot()["memory"]] == ["pending"]
    console.submit("adjudicate", record_id="rec-1", status="confirmed", user="ana").result()
    adjudicator.poll(6.0)
    assert (adjudicator.asked, adjudicator.applied) == (1, 1)
    assert broker.store.get("rec-1").status == "confirmed"
    console.step(timeout=0)
    [row] = console.snapshot()["memory"]
    assert (row["status"], row["adjudicated_by"]) == ("confirmed", "operator:ana")
    with pytest.raises(ValueError):
        console.submit("adjudicate", record_id="rec-1", status="benign", user="ana").result()


def test_a_verdict_the_console_did_not_sign_is_refused_by_memory_not_the_relay() -> None:
    adjudicator, _, broker = _deployment()
    RedisBus(adjudicator.bus.client, publisher="console").publish(
        DECISION_TOPIC, _verdict(key=issue_signing_identity("console", seed=b"m" * 32))
    )
    adjudicator.poll(6.0)
    assert adjudicator.refused == {"bad_verdict": 1} and adjudicator.applied == 0
    assert broker.store.get("rec-1").status == "pending"


@pytest.mark.parametrize(
    ("verdict", "reason"),
    [
        (_verdict(record="rec-9", signed_for="rec-9"), "no_open_question"),
        (_verdict(asked=4.0), "another_question"),
    ],
)
def test_a_verdict_must_answer_an_open_question_exactly(verdict, reason) -> None:
    adjudicator, _, broker = _deployment()
    RedisBus(adjudicator.bus.client, publisher="console").publish(DECISION_TOPIC, verdict)
    adjudicator.poll(6.0)
    assert adjudicator.refused == {reason: 1}
    assert broker.store.get("rec-1").status == "pending"


def test_an_admitted_remote_write_comes_back_with_its_record() -> None:
    """
    Without it the pipeline would never queue a remote record for review, and in the deployment no
    incident would be adjudicated.
    """
    from m5_immune_memory.write_path import MemoryCurator
    from m11_memory_hardening import attest

    query, writer, attesters = _memory("wire")
    client = McpBroker(inner=InProcBroker(query=query, write_path=writer, **BASE)).at(
        5.0, Provenance.HIGH, fleet_size=4
    )
    candidate = MemoryCurator().propose(
        IncidentSummary(
            record_id="rec-2",
            node_ids=("node-2",),
            peak_level=3,
            threat_type="device_compromise",
            pattern_text=CAMPAIGN,
            window_start_sim=1.0,
            window_end_sim=5.0,
            **BASE,
        )
    )
    signed = [attest(candidate, a.identity, sim_time=5.0) for a in list(attesters.values())[:3]]
    result = client.submit(candidate, signed, now_sim=5.0)
    assert result.admitted and result.record.record_id == "rec-2"
    assert result.record.node_ids == ["node-2"]
