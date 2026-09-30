"""GT signing and the hash-chained audit log: the two remaining integrity gaps."""

from __future__ import annotations

import pytest

from agents.orchestrator import TickBatch
from agents.pipeline import ClosedLoopPipeline
from m4_response_engine.engine import ResponseEngine
from m6_trust_fusion import TrustFusionEngine
from m6_trust_fusion.fusion import gt_payload
from shared.audit import GENESIS, AuditLog, load_chain, verify_chain
from shared.bus import InProcBus
from shared.integrity import canonical, sign, verify
from shared.schemas import (
    AuditRecord,
    ContextVector,
    GlobalTrustUpdate,
    Provenance,
    TrustUpdate,
)


def _update(node_id: str, sim_time: float, level: float) -> TrustUpdate:
    return TrustUpdate(
        sim_time=sim_time,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id=node_id,
        node_trust=level,
        observation=level,
        context=ContextVector(identity=level, behavioral=level, device=level, network=level),
        provenance=Provenance.HIGH,
        agent_id=f"mon-{node_id}",
    )


def _batch(sim_time: float = 1.0, n_bad: int = 2, n_total: int = 6) -> TickBatch:
    return TickBatch(
        sim_time=sim_time,
        run_id="r",
        seed=1,
        config_hash="h",
        updates=[_update(f"n-{i}", sim_time, 0.10 if i < n_bad else 0.95) for i in range(n_total)],
    )


def _fusion() -> TrustFusionEngine:
    return TrustFusionEngine(bus=InProcBus(), run_id="r", seed=1, config_hash="h")


def _record(event: str = "response.executed", **payload) -> AuditRecord:
    return AuditRecord(
        sim_time=1.0,
        run_id="r",
        seed=1,
        config_hash="h",
        event_type=event,
        actor_id="response-engine",
        payload=payload,
    )


def test_sign_and_verify_round_trip() -> None:
    payload = canonical("r", 1, "h", 1.0, "n-0", 0.42)
    assert verify(payload, sign(payload)) is True


def test_an_empty_signature_is_never_valid() -> None:
    assert verify(b"anything", "") is False


def test_a_different_key_does_not_verify() -> None:
    payload = canonical("x")
    assert verify(payload, sign(payload, b"other-key")) is False


def test_float_precision_is_preserved_in_the_payload() -> None:
    """Formatting would make two distinct values share a signature."""
    assert canonical(0.1 + 0.2) != canonical(0.3)


def test_fusion_signs_every_global_trust_update() -> None:
    updates = _fusion().fuse_batch(list(_batch().updates))
    assert all(u.signature for u in updates)
    assert all(ResponseEngine().gt_is_authentic(u) for u in updates)


def test_a_tampered_gt_does_not_verify() -> None:
    update = _fusion().fuse_batch(list(_batch().updates))[0]
    forged = update.model_copy(update={"gt": 0.02})
    assert ResponseEngine().gt_is_authentic(forged) is False


def test_a_signature_does_not_transfer_between_ticks() -> None:
    """Replaying an old high GT over a since-compromised device is the attack."""
    update = _fusion().fuse_batch(list(_batch(sim_time=1.0).updates))[0]
    replayed = update.model_copy(update={"sim_time": 99.0})
    assert ResponseEngine().gt_is_authentic(replayed) is False


def test_a_signature_does_not_transfer_between_nodes() -> None:
    update = _fusion().fuse_batch(list(_batch().updates))[0]
    moved = update.model_copy(update={"node_id": "n-5"})
    assert ResponseEngine().gt_is_authentic(moved) is False


def test_an_engine_requiring_signatures_refuses_to_derive_from_an_unsigned_gt() -> None:
    """No action at all, rather than an action from a number it cannot vouch for."""
    unsigned = GlobalTrustUpdate(
        sim_time=1.0,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id="n-0",
        gt=0.10,
        ts=0.10,
        cti_i=0.0,
        cti_trust=1.0,
        rep=1.0,
        master_score=0.1,
    )
    with pytest.raises(ValueError, match="unsigned or altered"):
        ResponseEngine(require_signature=True).decide(unsigned)


def test_the_closed_loop_requires_signatures_by_default() -> None:
    pipe = ClosedLoopPipeline(fusion=_fusion())
    assert pipe.engine.require_signature is True
    out = pipe.run(_batch())
    assert all(u.signature for u in out.gt_updates)


def test_gt_payload_covers_run_identity() -> None:
    a = gt_payload(
        run_id="r",
        seed=1,
        config_hash="h",
        sim_time=1.0,
        node_id="n",
        gt=0.5,
        ts=0.5,
        cti_i=0.0,
        rep=1.0,
        drift_flag=0.0,
    )
    b = gt_payload(
        run_id="r",
        seed=2,
        config_hash="h",
        sim_time=1.0,
        node_id="n",
        gt=0.5,
        ts=0.5,
        cti_i=0.0,
        rep=1.0,
        drift_flag=0.0,
    )
    assert a != b


def test_an_empty_log_starts_at_genesis() -> None:
    log = AuditLog()
    assert log.head == GENESIS
    assert log.verify() is None


def test_records_chain_to_one_another() -> None:
    log = AuditLog()
    first = log.append(_record())
    second = log.append(_record("response.denied"))
    assert first.previous_hash == GENESIS
    assert second.previous_hash == first.hash
    assert log.verify() is None


def test_editing_a_record_breaks_the_chain() -> None:
    log = AuditLog()
    log.append(_record(node_id="n-0"))
    log.append(_record(node_id="n-1"))
    log.append(_record(node_id="n-2"))

    entries = list(log)
    tampered = entries[1].record.model_copy(update={"event_type": "response.denied"})
    entries[1] = type(entries[1])(
        record=tampered,
        previous_hash=entries[1].previous_hash,
        hash=entries[1].hash,
    )
    assert verify_chain(entries) == 1


def test_deleting_a_record_is_not_silent() -> None:
    """The property an audit trail actually needs: removal is detectable."""
    log = AuditLog()
    for i in range(4):
        log.append(_record(node_id=f"n-{i}"))

    entries = list(log)
    del entries[2]
    assert verify_chain(entries) == 2


def test_reordering_records_breaks_the_chain() -> None:
    log = AuditLog()
    for i in range(3):
        log.append(_record(node_id=f"n-{i}"))
    entries = list(log)
    entries[0], entries[1] = entries[1], entries[0]
    assert verify_chain(entries) is not None


def test_the_log_persists_as_it_goes_and_verifies_offline(tmp_path) -> None:
    """A log that only survives a clean shutdown is not much of an audit trail."""
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path=path)
    for i in range(5):
        log.append(_record(node_id=f"n-{i}"))

    reloaded = load_chain(path)
    assert len(reloaded) == 5
    assert verify_chain(reloaded) is None
    assert reloaded[0].record.payload["node_id"] == "n-0"


def test_a_truncated_file_is_detected_when_reloaded(tmp_path) -> None:
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path=path)
    for i in range(4):
        log.append(_record(node_id=f"n-{i}"))

    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(lines[:1] + lines[2:]) + "\n", encoding="utf-8")
    assert verify_chain(load_chain(path)) == 1


def test_the_engine_writes_into_the_chain() -> None:
    pipe = ClosedLoopPipeline(fusion=_fusion())
    pipe.run(_batch())
    assert len(pipe.engine.audit) == 6
    assert pipe.engine.audit.verify() is None


def test_the_gt_signature_covers_every_input_it_was_fused_from() -> None:
    """Signing `gt` alone let the explanation beside a level be rewritten."""
    base = dict(
        run_id="r",
        seed=1,
        config_hash="h",
        sim_time=1.0,
        node_id="n",
        gt=0.5,
        ts=0.5,
        cti_i=0.2,
        rep=0.9,
        drift_flag=0.0,
    )
    reference = gt_payload(**base)
    for field_name, altered in (("ts", 0.9), ("cti_i", 0.0), ("rep", 1.0), ("drift_flag", 0.3)):
        assert gt_payload(**{**base, field_name: altered}) != reference, field_name


def test_a_truncated_log_is_caught_by_its_checkpoint(tmp_path) -> None:
    """Dropping the last records leaves a chain that verifies on its own."""
    from shared.audit import AuditLog, load_chain, verify_chain

    log = AuditLog(path=tmp_path / "audit.jsonl")
    for i in range(5):
        log.append(_record(i=i))
    checkpoint = log.checkpoint()
    entries = load_chain(tmp_path / "audit.jsonl")

    assert verify_chain(entries, checkpoint=checkpoint) is None
    assert verify_chain(entries[:3]) is None, "the chain alone cannot see it"
    assert verify_chain(entries[:3], checkpoint=checkpoint) == 3


def test_a_chain_rebuilt_without_the_key_does_not_verify() -> None:
    """An unkeyed chain could be rewritten wholesale and still verified."""
    import hashlib

    from shared.audit import GENESIS, AuditLog, ChainedRecord, record_payload, verify_chain

    log = AuditLog()
    for i in range(4):
        log.append(_record(i=i))
    forged, previous = [], GENESIS
    for entry in log:
        record = entry.record.model_copy(update={"event_type": "response.denied"})
        digest = hashlib.sha256(previous.encode() + b"\x1f" + record_payload(record)).hexdigest()
        forged.append(ChainedRecord(record=record, previous_hash=previous, hash=digest))
        previous = digest
    assert verify_chain(forged) == 0
