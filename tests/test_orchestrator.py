"""M2 orchestrator batching + reasoning-plane graph shape."""

from __future__ import annotations

import pytest

from agents.graph import LANGGRAPH_AVAILABLE
from agents.orchestrator import (
    ORCHESTRATOR_TOPIC,
    NullPipeline,
    Orchestrator,
    TickBatch,
)
from m1_monitoring.agent import TRUST_TOPIC
from shared.bus import InProcBus
from shared.schemas import AuditRecord, ContextVector, Provenance, SkeletonEvent, TrustUpdate

RUN = dict(run_id="test", seed=7, config_hash="cafebabecafebabe")


def update(node_id: str, sim_time: float, trust: float = 0.9) -> TrustUpdate:
    return TrustUpdate(
        sim_time=sim_time,
        node_id=node_id,
        node_trust=trust,
        observation=trust,
        context=ContextVector(identity=trust, behavioral=trust, device=trust, network=trust),
        provenance=Provenance.MEDIUM,
        agent_id=f"mon-{node_id}",
        **RUN,
    )


def make_orchestrator(bus: InProcBus, **kwargs: object) -> Orchestrator:
    orch = Orchestrator(bus=bus, **RUN, **kwargs)  # type: ignore[arg-type]
    orch.attach()
    return orch


def test_groups_updates_by_sim_time() -> None:
    bus = InProcBus()
    orch = make_orchestrator(bus)

    for t in (0.0, 1.0, 2.0):
        for node in ("node-0", "node-1", "node-2"):
            bus.publish(TRUST_TOPIC, update(node, t))
    orch.flush()

    assert orch.batches_sealed == 3
    assert [b.sim_time for b in orch.batches] == [0.0, 1.0, 2.0]
    assert all(len(b.updates) == 3 for b in orch.batches)
    assert orch.updates_seen == 9


def test_batch_is_sorted_by_node_id_regardless_of_arrival_order() -> None:
    """Downstream agents must never see a batch whose order depends on the bus."""
    bus = InProcBus()
    orch = make_orchestrator(bus)

    for node in ("node-9", "node-2", "node-5", "node-1"):
        bus.publish(TRUST_TOPIC, update(node, 0.0))
    orch.flush()

    assert orch.batches[0].node_ids == ["node-1", "node-2", "node-5", "node-9"]


def test_a_tick_seals_only_once_a_later_tick_arrives() -> None:
    """Watermark semantics: t=0 stays open until something newer shows up."""
    bus = InProcBus()
    orch = make_orchestrator(bus)

    bus.publish(TRUST_TOPIC, update("node-0", 0.0))
    bus.publish(TRUST_TOPIC, update("node-1", 0.0))
    assert orch.batches_sealed == 0, "t=0 could still receive more updates"

    bus.publish(TRUST_TOPIC, update("node-0", 1.0))
    assert orch.batches_sealed == 1
    assert orch.batches[0].sim_time == 0.0
    assert len(orch.batches[0].updates) == 2


def test_late_update_still_lands_in_its_own_tick() -> None:
    """Out-of-order delivery must not silently drop or misfile an update."""
    bus = InProcBus()
    orch = make_orchestrator(bus)

    bus.publish(TRUST_TOPIC, update("node-0", 5.0))
    bus.publish(TRUST_TOPIC, update("node-1", 3.0))
    orch.flush()

    by_time = {b.sim_time: b.node_ids for b in orch.batches}
    assert by_time == {3.0: ["node-1"], 5.0: ["node-0"]}
    assert [b.sim_time for b in orch.batches] == [3.0, 5.0]


def test_flush_is_idempotent() -> None:
    bus = InProcBus()
    orch = make_orchestrator(bus)
    bus.publish(TRUST_TOPIC, update("node-0", 0.0))

    orch.flush()
    orch.flush()

    assert orch.batches_sealed == 1


def test_ignores_messages_that_are_not_telemetry() -> None:
    bus = InProcBus()
    orch = make_orchestrator(bus)

    bus.publish(TRUST_TOPIC, SkeletonEvent(sim_time=0.0, node_id="node-0", value=1.0, **RUN))
    orch.flush()

    assert orch.updates_seen == 0
    assert orch.batches_sealed == 0


def test_batch_exposes_trust_summary() -> None:
    bus = InProcBus()
    orch = make_orchestrator(bus)

    bus.publish(TRUST_TOPIC, update("node-0", 0.0, trust=0.30))
    bus.publish(TRUST_TOPIC, update("node-1", 0.0, trust=0.90))
    orch.flush()

    batch = orch.batches[0]
    assert batch.min_node_trust == pytest.approx(0.30)
    assert batch.mean_node_trust == pytest.approx(0.60)


def test_publishes_one_audit_record_per_sealed_batch() -> None:
    bus = InProcBus()
    seen: list[AuditRecord] = []
    bus.subscribe(ORCHESTRATOR_TOPIC, lambda m: seen.append(m))  # type: ignore[arg-type]
    orch = make_orchestrator(bus)

    bus.publish(TRUST_TOPIC, update("node-0", 0.0, trust=0.4))
    bus.publish(TRUST_TOPIC, update("node-1", 0.0, trust=0.8))
    orch.flush()

    assert len(seen) == 1
    record = seen[0]
    assert record.event_type == "orchestrator.batch_sealed"
    assert record.actor_id == "orchestrator"
    assert record.payload["n_updates"] == 2
    assert record.payload["min_node_trust"] == pytest.approx(0.4)
    assert record.sim_time == 0.0
    assert record.run_id == RUN["run_id"]


def test_audit_can_be_switched_off() -> None:
    bus = InProcBus()
    seen: list[AuditRecord] = []
    bus.subscribe(ORCHESTRATOR_TOPIC, lambda m: seen.append(m))  # type: ignore[arg-type]
    orch = make_orchestrator(bus, emit_audit=False)

    bus.publish(TRUST_TOPIC, update("node-0", 0.0))
    orch.flush()

    assert seen == []
    assert orch.batches_sealed == 1


def test_pipeline_receives_batches_in_simulation_order() -> None:
    bus = InProcBus()
    pipeline = NullPipeline()
    orch = make_orchestrator(bus, pipeline=pipeline)

    for t in (2.0, 0.0, 1.0):
        bus.publish(TRUST_TOPIC, update("node-0", t))
    orch.flush()

    assert [b.sim_time for b in pipeline.seen] == [0.0, 1.0, 2.0]


def test_batching_is_deterministic_across_identical_streams() -> None:
    def run_once() -> list[TickBatch]:
        bus = InProcBus()
        orch = make_orchestrator(bus)
        for t in (0.0, 1.0):
            for node in ("node-2", "node-0", "node-1"):
                bus.publish(TRUST_TOPIC, update(node, t, trust=0.5 + t / 10))
        orch.flush()
        return orch.batches

    a, b = run_once(), run_once()
    assert [x.model_dump() for x in a] == [x.model_dump() for x in b]


requires_langgraph = pytest.mark.skipif(
    not LANGGRAPH_AVAILABLE,
    reason="control-plane extra not installed: pip install -e '.[agents]'",
)


@requires_langgraph
def test_graph_runs_all_four_stages_in_order() -> None:
    from agents.graph import NODE_ORDER, GraphPipeline

    bus = InProcBus()
    pipeline = GraphPipeline()
    orch = make_orchestrator(bus, pipeline=pipeline)

    bus.publish(TRUST_TOPIC, update("node-0", 0.0, trust=0.42))
    orch.flush()

    assert len(pipeline.results) == 1
    state = pipeline.results[0]
    assert state.trail == list(NODE_ORDER)
    assert state.node_trusts == {"node-0": pytest.approx(0.42)}
    assert state.sim_time == 0.0


@requires_langgraph
def test_remaining_stubs_do_not_invent_scores() -> None:
    """Without a fusion engine, plan and verify must leave their fields None."""
    from agents.graph import GraphPipeline

    bus = InProcBus()
    pipeline = GraphPipeline()
    orch = make_orchestrator(bus, pipeline=pipeline)

    bus.publish(TRUST_TOPIC, update("node-0", 0.0))
    orch.flush()

    state = pipeline.results[0]
    assert state.proposed_level is None
    assert state.guard_verdict is None

    assert state.cti is not None
    assert state.correlation is not None
    assert state.classification is not None
    assert state.classification.used_llm is False


@requires_langgraph
def test_graph_is_reusable_across_batches() -> None:
    from agents.graph import GraphPipeline

    bus = InProcBus()
    pipeline = GraphPipeline()
    orch = make_orchestrator(bus, pipeline=pipeline)

    for t in (0.0, 1.0, 2.0):
        bus.publish(TRUST_TOPIC, update("node-0", t))
    orch.flush()

    assert [s.sim_time for s in pipeline.results] == [0.0, 1.0, 2.0]
    assert all(len(s.trail) == 4 for s in pipeline.results)


@requires_langgraph
def test_orchestrator_consumes_a_real_50_node_run(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """End-to-end: the edge layer feeds the reasoning plane."""
    from agents.graph import GraphPipeline
    from m8_eval_harness.simulator import DEFAULT_CONFIG, run_trust_sim
    from shared.run_manifest import config_hash, load_yaml_config

    bus = InProcBus()
    pipeline = GraphPipeline()
    orch = Orchestrator(
        bus=bus,
        run_id="orch-integration",
        seed=42,
        config_hash=config_hash(load_yaml_config(DEFAULT_CONFIG)),
        pipeline=pipeline,
    )
    orch.attach()

    run_trust_sim(
        seed=42,
        n_nodes=50,
        ticks=40,
        run_id="orch-integration",
        results_dir=tmp_path / "run",
        bus=bus,
    )
    orch.flush()

    assert orch.updates_seen == 50 * 40
    assert orch.batches_sealed == 40
    assert [b.sim_time for b in orch.batches] == [float(t) for t in range(40)]
    assert all(len(b.updates) == 50 for b in orch.batches)
    assert len(pipeline.results) == 40

    trough = min(b.min_node_trust for b in orch.batches)
    assert trough < 0.4, f"expected the anomaly to reach the orchestrator, got {trough}"


def test_a_backlog_read_stream_by_stream_is_sealed_whole_when_sealing_waits_for_the_loop() -> None:
    """
    A backlog read one publisher's stream at a time is sealed whole when sealing waits for the loop.
    """
    from shared.clock import ManualClock

    def backlog(seal_on_report: bool) -> Orchestrator:
        bus = InProcBus()
        orch = make_orchestrator(
            bus, clock=ManualClock(39.0), max_clock_skew=1.0, seal_on_report=seal_on_report
        )
        for node in ("node-0", "node-1"):
            for t in (37.0, 38.0):
                bus.publish(TRUST_TOPIC, update(node, t))
        orch.seal_due()
        return orch

    assert backlog(True).late_updates == 2
    orch = backlog(False)
    assert orch.late_updates == 0
    assert [len(b.updates) for b in orch.batches] == [2, 2]
