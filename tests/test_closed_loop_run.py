"""The full system on a simulated fleet: every module, one seeded run."""

from __future__ import annotations

from agents.pipeline import ClosedLoopPipeline
from m5_immune_memory import HashingEmbedder, MemoryQuery, MemoryStore
from m6_trust_fusion import TrustFusionEngine
from m7_self_healing import SelfHealingEngine
from m8_eval_harness.closed_loop import run_closed_loop
from m10_persona_drift.nhi import issue_identity
from shared.bus import InProcBus


def _run(**over):
    kw = dict(n_nodes=20, ticks=30, run_id="test-loop")
    kw.update(over)
    return run_closed_loop(**kw)


def _pipeline(**over) -> ClosedLoopPipeline:
    kw = dict(
        fusion=TrustFusionEngine(
            bus=InProcBus(), run_id="test-loop", seed=42, config_hash="pending"
        )
    )
    kw.update(over)
    return ClosedLoopPipeline(**kw)


def test_every_tick_is_sealed_and_processed() -> None:
    run = _run()
    assert run.ticks == 30
    assert all(len(o.plans) == 20 for o in run.outcomes)


def test_the_anomalous_device_escalates_and_its_peers_do_not() -> None:
    """The acceptance condition, through the whole loop rather than M1 alone."""
    run = _run()
    assert run.worst_level("node-0") >= 2
    assert all(run.worst_level(f"node-{i}") == 0 for i in range(1, 20))


def test_detection_happens_inside_the_anomaly_window() -> None:
    run = _run(anomaly_window=(5.0, 18.0, 0.6))
    at = run.first_tick_at_or_above("node-0", 2)
    assert at is not None
    assert 5.0 <= at <= 18.0


def test_every_stage_produced_output() -> None:
    out = _run().outcomes[-1]
    assert out.correlation is not None
    assert out.classification.rules_threat_type is not None, "dual classification ran"
    assert out.gt_updates and out.plans and out.executions
    assert out.reputations


def test_global_trust_is_signed_throughout_the_run() -> None:
    run = _run()
    assert all(u.signature for o in run.outcomes for u in o.gt_updates)


def test_the_audit_chain_holds_across_a_whole_run() -> None:
    run = _run()
    assert run.audit_intact is True
    assert len(run.pipeline.engine.audit) == 30 * 20


def test_the_run_is_reproducible() -> None:
    a, b = _run(), _run()
    assert a.events_jsonl == b.events_jsonl
    assert [o.correlation.cti for o in a.outcomes] == [o.correlation.cti for o in b.outcomes]
    assert [p.proposed_level for o in a.outcomes for p in o.plans] == [
        p.proposed_level for o in b.outcomes for p in o.plans
    ]


def test_a_different_seed_gives_a_different_run() -> None:
    assert _run(seed=1).events_jsonl != _run(seed=2).events_jsonl


def test_healing_engages_when_a_pipeline_carries_one() -> None:
    run = _run(pipeline=_pipeline(healer=SelfHealingEngine()))
    assert isinstance(run.healing_phases("node-0"), list)


def test_a_memory_equipped_pipeline_still_runs_clean() -> None:
    names = ("verifier", "correlation", "fusion", "orchestrator", "monitoring")
    reg = {n: issue_identity(n, seed=n.encode().ljust(32, b"\0")) for n in names}
    emb = HashingEmbedder()
    query = MemoryQuery(store=MemoryStore(dim=emb.dim), registry=reg, embedder=emb)

    run = _run(pipeline=_pipeline(recall=query))
    assert run.ticks == 30
    assert all(o.correlation.recall_boost == 0.0 for o in run.outcomes), "empty store"


def test_it_scales_to_five_hundred_nodes_in_process() -> None:
    """The scalability claim is 50 to 5000; this is the cheap end of the sweep."""
    run = _run(n_nodes=500, ticks=10, run_id="scale-test")
    assert run.ticks == 10
    assert all(len(o.plans) == 500 for o in run.outcomes)
    assert run.audit_intact is True


def test_worst_level_is_zero_for_a_device_that_never_appeared() -> None:
    assert _run().worst_level("node-does-not-exist") == 0
    assert _run().first_tick_at_or_above("node-0", 4) is None
