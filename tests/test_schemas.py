"""Schema invariants: node_trust vs agent_reliability, required stamps."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from shared.schemas import AgentReliability, ContextVector, Provenance, TrustUpdate


def test_trust_update_requires_run_stamps() -> None:
    with pytest.raises(ValidationError):
        TrustUpdate(  # type: ignore[call-arg]
            node_id="n0",
            node_trust=0.9,
            observation=0.9,
            context=ContextVector(identity=1, behavioral=1, device=1, network=1),
            provenance=Provenance.HIGH,
            agent_id="a0",
        )


def test_node_trust_and_agent_reliability_are_separate_models() -> None:
    tu = TrustUpdate(
        sim_time=0.0,
        run_id="r",
        seed=1,
        config_hash="abcd",
        node_id="n0",
        node_trust=0.4,
        observation=0.4,
        context=ContextVector(identity=0.4, behavioral=0.4, device=0.4, network=0.4),
        provenance=Provenance.HIGH,
        agent_id="mon-n0",
    )
    ar = AgentReliability(
        sim_time=0.0,
        run_id="r",
        seed=1,
        config_hash="abcd",
        agent_id="mon-n0",
        agent_reliability=0.95,
    )
    assert tu.node_trust == 0.4
    assert ar.agent_reliability == 0.95
    assert not hasattr(tu, "agent_reliability")
    assert not hasattr(ar, "node_trust")


def test_provenance_is_closed_enum() -> None:
    assert {p.value for p in Provenance} == {"HIGH", "MEDIUM", "LOW", "UNTRUSTED"}
