"""Mediated access to immune memory: the boundary, the transport, and the mediated arms."""

from __future__ import annotations

import pytest

from agents.context_broker import (
    CORRELATION_CLIENT,
    CURATOR_CLIENT,
    InProcBroker,
)
from agents.mcp_broker import MCP_AVAILABLE, McpBroker
from m5_immune_memory import IncidentSummary
from m8_eval_harness.baselines import by_id
from m8_eval_harness.baselines.base import _memory
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios import by_id as scenario
from shared.schemas import Provenance

CAMPAIGN = "three controllers sliding together on device and network dimensions"


@pytest.fixture
def broker() -> InProcBroker:
    query, writer, attesters = _memory("broker-test")
    signers = {n: a.identity for n, a in attesters.items()}
    writer.initial_status = "confirmed"
    writer.propose_and_submit(
        IncidentSummary(
            record_id="rec-1",
            node_ids=("n-1",),
            peak_level=3,
            threat_type="device_compromise",
            pattern_text=CAMPAIGN,
            window_start_sim=1.0,
            window_end_sim=5.0,
            run_id="broker-test",
            seed=1,
            config_hash="h",
        ),
        signers,
        now_sim=5.0,
    )
    return InProcBroker(
        query=query, write_path=writer, run_id="broker-test", seed=1, config_hash="h"
    )


def test_a_registered_reader_gets_the_record(broker: InProcBroker) -> None:
    decision = broker.request_recall(
        caller_id=CORRELATION_CLIENT, pattern_text=CAMPAIGN, sim_time=6.0
    )
    assert decision.allowed and decision.result.recognised
    assert decision.result.best.record_id == "rec-1"
    assert decision.token_id, "the read resolved and spent an M9 capability"


def test_an_unregistered_caller_is_refused_before_memory_is_touched(broker: InProcBroker) -> None:
    """The classifier is deliberately not a client of the state plane."""
    decision = broker.request_recall(caller_id="classifier", pattern_text=CAMPAIGN, sim_time=6.0)
    assert not decision.allowed
    assert decision.reason == "unknown_caller"


def test_a_reader_cannot_propose_a_write(broker: InProcBroker) -> None:
    decision = broker.request_write(
        caller_id=CORRELATION_CLIENT, candidate=None, attestations=(), sim_time=6.0
    )
    assert not decision.allowed
    assert decision.reason == "capability_not_granted"


def test_an_untrusted_caller_cannot_even_read(broker: InProcBroker) -> None:
    """Reading is gated too: `memory_read` needs LOW, and UNTRUSTED is below it."""
    decision = broker.request_recall(
        caller_id=CORRELATION_CLIENT,
        pattern_text=CAMPAIGN,
        sim_time=6.0,
        provenance=Provenance.UNTRUSTED,
    )
    assert not decision.allowed
    assert decision.reason == "provenance_too_low"


def test_the_run_ceiling_bounds_what_a_caller_may_claim(broker: InProcBroker) -> None:
    broker.ceiling = Provenance.UNTRUSTED
    decision = broker.request_recall(
        caller_id=CORRELATION_CLIENT,
        pattern_text=CAMPAIGN,
        sim_time=6.0,
        provenance=Provenance.HIGH,
    )
    assert not decision.allowed, "a caller cannot claim more than the run's ceiling"


def test_every_request_is_audited_allowed_or_refused(broker: InProcBroker) -> None:
    broker.request_recall(caller_id=CORRELATION_CLIENT, pattern_text=CAMPAIGN, sim_time=6.0)
    broker.request_recall(caller_id="classifier", pattern_text=CAMPAIGN, sim_time=6.0)
    events = [(r.event_type, r.payload["deny_reason"]) for r in broker.audit.records]
    assert ("broker.served", None) in events
    assert ("broker.denied", "unknown_caller") in events
    assert broker.audit.verify() is None, "the broker's own trail is hash-chained"


@pytest.mark.skipif(not MCP_AVAILABLE, reason="the mcp extra is not installed")
def test_mcp_enforces_the_same_policy_and_returns_no_stored_prose(broker: InProcBroker) -> None:
    client = McpBroker(inner=broker).at(6.0)
    recognition = client.recognise(CAMPAIGN)
    assert recognition.recognised and recognition.best.record_id == "rec-1"
    assert not hasattr(recognition.best, "pattern_text")

    refused = McpBroker(inner=broker, caller_id="classifier").at(6.0).recognise(CAMPAIGN)
    assert refused is None, "an unregistered caller is refused server-side"

    assert client.authorise_write(caller_id=CURATOR_CLIENT, sim_time=6.0).allowed
    assert not client.authorise_write(caller_id=CORRELATION_CLIENT, sim_time=6.0).allowed


@pytest.mark.skipif(not MCP_AVAILABLE, reason="the mcp extra is not installed")
def test_mediation_does_not_change_what_the_system_decides() -> None:
    """Both mediated postures must reproduce the unmediated run exactly."""
    sc = scenario("s3")
    runs = {arm: run_scenario(sc, by_id(arm)) for arm in ("full", "full_mediated", "full_mcp")}
    levels = {
        arm: [
            (o.sim_time, p.node_id, p.proposed_level) for o in r.pipeline.outcomes for p in o.plans
        ]
        for arm, r in runs.items()
    }
    assert levels["full_mediated"] == levels["full"]
    assert levels["full_mcp"] == levels["full"]
    assert runs["full_mediated"].recall_boosts == runs["full"].recall_boosts > 0
    assert runs["full_mcp"].pipeline.broker.calls > 0, "the MCP path actually carried the traffic"
    assert runs["full_mediated"].pipeline.memory_writes_denied == 0


def test_the_no_quorum_arm_admits_what_the_quorum_refuses() -> None:
    """Ablation F: without the quorum, the arm admits what the quorum refuses."""
    full = run_scenario(scenario("s5"), by_id("full"))
    none = run_scenario(scenario("s5"), by_id("no_quorum"))
    assert full.adversary.accepted == 0
    assert none.adversary.accepted > 0
    assert none.adversary.attempts == full.adversary.attempts


def test_the_staged_research_baselines_carry_what_they_say() -> None:
    """Baselines B and C: trust alone, then trust plus the fleet view."""
    trust_only = run_scenario(scenario("s3"), by_id("trust_only"))
    trust_ti = run_scenario(scenario("s3"), by_id("trust_ti"))
    for run in (trust_only, trust_ti):
        assert run.recall_boosts == 0, "no immune memory in either"
        assert run.heal_events == 0, "no healing in either"
    assert trust_only.pipeline.correlator.__class__.__name__ == "_IsolatedCorrelation"
    assert trust_ti.pipeline.correlator.__class__.__name__ == "CorrelationAgent"


def test_the_equal_weighting_arm_really_stops_weighting() -> None:
    """Ablation C: `k = 0` makes every reporter's intel count the same."""
    run = run_scenario(scenario("a4"), by_id("equal_weighting"))
    assert run.pipeline.correlator.params.k == 0.0
    assert run.pipeline.verifier.correlator.params.k == 0.0, "the checker matches the arm"
