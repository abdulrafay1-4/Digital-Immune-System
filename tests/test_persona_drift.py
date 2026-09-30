"""M10 persona-drift and NHI tests."""

from __future__ import annotations

from m6_trust_fusion import TrustFusionEngine, fuse_gt
from m10_persona_drift import (
    DriftObservation,
    PersonaBaseline,
    PersonaDriftDetector,
    issue_identity,
)
from shared.bus import InProcBus
from shared.schemas import ContextVector, Provenance, TrustUpdate


def test_forged_identity_flags_drift() -> None:
    real = issue_identity("agent-a", seed=b"real-secret-aaaaaaaaaaaaaaaa")
    fake = issue_identity("agent-a", seed=b"forged-secret-bbbbbbbbbbbbbbb")
    det = PersonaDriftDetector(
        PersonaBaseline(agent_id="agent-a"),
        bound_identity=real,
    )
    result = det.observe(
        DriftObservation(
            agent_id="agent-a",
            sim_time=0.0,
            identity=fake,
            claimed_agent_id="agent-a",
        )
    )
    assert result.drift_flag == 1.0
    assert "forged_identity" in result.reasons


def test_message_rate_spike_flags_drift() -> None:
    det = PersonaDriftDetector(
        PersonaBaseline(agent_id="a", message_rate=1.0),
    )
    for t in range(10):
        det.observe(DriftObservation(agent_id="a", sim_time=float(t), messages_this_tick=1))
    spike = det.observe(DriftObservation(agent_id="a", sim_time=10.0, messages_this_tick=50))
    assert spike.drift_flag > 0.0
    assert "message_rate_drift" in spike.reasons


def test_disallowed_capability_flags() -> None:
    det = PersonaDriftDetector(PersonaBaseline(agent_id="a"))
    r = det.observe(
        DriftObservation(
            agent_id="a",
            sim_time=0.0,
            capability_requested="exfiltrate",
        )
    )
    assert r.drift_flag == 1.0
    assert "disallowed_capability" in r.reasons


def test_schema_nonconformance_flags() -> None:
    det = PersonaDriftDetector(PersonaBaseline(agent_id="a"))
    r = det.observe(
        DriftObservation(
            agent_id="a",
            sim_time=0.0,
            output_keys=frozenset({"sim_time"}),
        )
    )
    assert "schema_nonconformance" in r.reasons


def test_drift_lowers_gt_via_fusion() -> None:
    gt_clean, _ = fuse_gt(ts=1.0, cti_i=0.0, rep=1.0, drift_flag=0.0)
    gt_drift, _ = fuse_gt(ts=1.0, cti_i=0.0, rep=1.0, drift_flag=1.0)
    assert gt_drift < gt_clean

    bus = InProcBus()
    eng = TrustFusionEngine(bus=bus, run_id="r", seed=1, config_hash="h")
    eng.set_drift("n0", 1.0)
    upd = TrustUpdate(
        sim_time=0.0,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id="n0",
        node_trust=1.0,
        observation=1.0,
        context=ContextVector(identity=1, behavioral=1, device=1, network=1),
        provenance=Provenance.HIGH,
        agent_id="mon-n0",
    )
    msg = eng.observe_trust(upd)
    assert msg.drift_flag == 1.0
    assert msg.gt < 1.0
