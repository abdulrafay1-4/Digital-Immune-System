"""Security hardening: each attack below is stopped, and the fix is pinned."""

from __future__ import annotations

from agents.orchestrator import TRUST_TOPIC, Orchestrator, TickBatch
from agents.pipeline import ClosedLoopPipeline
from m6_trust_fusion import TrustFusionEngine
from shared.audit import AuditLog
from shared.bus import InProcBus
from shared.schemas import AuditRecord, ContextVector, Provenance, TrustUpdate


def _u(node_id: str, sim_time: float, level: float = 0.05, prov=Provenance.HIGH):
    return TrustUpdate(
        sim_time=sim_time,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id=node_id,
        node_trust=level,
        observation=level,
        context=ContextVector(identity=level, behavioral=level, device=level, network=level),
        provenance=prov,
        agent_id=f"mon-{node_id}",
    )


def _pipe(**over) -> ClosedLoopPipeline:
    kw = dict(fusion=TrustFusionEngine(bus=InProcBus(), run_id="r", seed=1, config_hash="h"))
    kw.update(over)
    return ClosedLoopPipeline(**kw)


def _batch(updates, sim_time=1.0) -> TickBatch:
    return TickBatch(sim_time=sim_time, run_id="r", seed=1, config_hash="h", updates=updates)


def _orch(bus, pipeline):
    o = Orchestrator(bus=bus, run_id="r", seed=1, config_hash="h", pipeline=pipeline)
    o.attach()
    return o


def test_a_device_reporting_untrusted_telemetry_cannot_be_restricted() -> None:
    """M9 maps capabilities to provenance, so it must be fed each report's provenance."""
    updates = [_u("n-0", 1.0, prov=Provenance.UNTRUSTED)]
    updates += [_u(f"n-{i}", 1.0) for i in range(1, 6)]
    out = _pipe().run(_batch(updates))

    by_node = {p.node_id: e for p, e in zip(out.plans, out.executions, strict=True)}
    assert by_node["n-0"].executed is False
    assert by_node["n-0"].audit.payload["deny_reason"] == "provenance_too_low"
    assert by_node["n-1"].executed is True, "its peers are unaffected"


def test_the_run_ceiling_still_applies_on_top_of_per_device_provenance() -> None:
    out = _pipe(input_provenance=Provenance.UNTRUSTED).run(
        _batch([_u(f"n-{i}", 1.0) for i in range(6)])
    )
    assert all(e.executed is False for e in out.executions)


def test_a_healthy_high_provenance_fleet_is_unaffected() -> None:
    out = _pipe().run(_batch([_u(f"n-{i}", 1.0, level=0.95) for i in range(6)]))
    assert all(e.executed for e in out.executions)


def test_a_node_reporting_twice_is_counted_once() -> None:
    """Otherwise it gets double weight in CTI, two plans, and two REP charges."""
    bus = InProcBus()
    pipe = _pipe()
    orch = _orch(bus, pipe)

    bus.publish(TRUST_TOPIC, _u("n-0", 1.0, level=0.9))
    bus.publish(TRUST_TOPIC, _u("n-0", 1.0, level=0.1))
    bus.publish(TRUST_TOPIC, _u("n-1", 2.0))
    orch.flush()

    first = pipe.outcomes[0]
    assert [p.node_id for p in first.plans] == ["n-0"]
    assert orch.duplicate_updates == 1


def test_the_duplicate_kept_is_the_most_pessimistic() -> None:
    """Publishing twice must never be a way to raise a device's trust."""
    bus = InProcBus()
    pipe = _pipe()
    orch = _orch(bus, pipe)

    bus.publish(TRUST_TOPIC, _u("n-0", 1.0, level=0.1))
    bus.publish(TRUST_TOPIC, _u("n-0", 1.0, level=0.99))
    orch.flush()

    assert pipe.outcomes[0].gt_updates[0].ts == 0.1


def test_a_tick_is_never_sealed_twice() -> None:
    """A late arrival must not create a second batch at the same sim_time."""
    bus = InProcBus()
    pipe = _pipe()
    orch = _orch(bus, pipe)

    bus.publish(TRUST_TOPIC, _u("n-0", 1.0))
    bus.publish(TRUST_TOPIC, _u("n-0", 2.0))
    bus.publish(TRUST_TOPIC, _u("n-1", 1.0))
    orch.flush()

    sealed = [o.sim_time for o in pipe.outcomes]
    assert sealed == sorted(set(sealed)), "no sim_time appears twice"
    assert orch.late_updates == 1


def test_an_out_of_order_update_for_a_still_open_tick_is_kept() -> None:
    """Only *sealed* ticks are closed."""
    bus = InProcBus()
    pipe = _pipe()
    orch = _orch(bus, pipe)

    bus.publish(TRUST_TOPIC, _u("n-0", 5.0))
    bus.publish(TRUST_TOPIC, _u("n-1", 3.0))
    orch.flush()

    assert [o.sim_time for o in pipe.outcomes] == [3.0, 5.0]
    assert orch.late_updates == 0


def test_the_orchestrator_batch_window_is_bounded() -> None:
    """A 5000-node, 5000-tick run would otherwise hold 25 million updates."""
    bus = InProcBus()
    orch = Orchestrator(bus=bus, run_id="r", seed=1, config_hash="h", max_retained_batches=10)
    orch.attach()
    for t in range(50):
        bus.publish(TRUST_TOPIC, _u("n-0", float(t)))
    orch.flush()
    assert len(orch.batches) == 10
    assert orch.updates_seen == 50, "everything was still processed"


def test_pipeline_outcome_retention_is_bounded() -> None:
    pipe = _pipe(max_retained_outcomes=5)
    for t in range(30):
        pipe.run(_batch([_u("n-0", float(t), level=0.9)], sim_time=float(t)))
    assert len(pipe.outcomes) == 5
    assert pipe.outcomes[-1].sim_time == 29.0


def test_pipeline_retention_is_bounded_in_decisions_not_only_ticks() -> None:
    """A tick cap alone does not bound a large fleet; decisions are bounded too."""
    pipe = _pipe(max_retained_decisions=10)
    for t in range(30):
        updates = [_u(f"n-{i}", float(t), level=0.9) for i in range(4)]
        pipe.run(_batch(updates, sim_time=float(t)))
    assert sum(len(o.plans) for o in pipe.outcomes) <= 10
    assert pipe.outcomes[-1].sim_time == 29.0


def test_the_bus_log_is_a_bounded_window() -> None:
    """The in-process bus keeps a bounded window, not every message ever published."""
    bus = InProcBus(max_log=100)
    for t in range(1000):
        bus.publish(TRUST_TOPIC, _u("n-0", float(t)))
    assert len(bus.log) == 100
    assert bus.log[-1][1].sim_time == 999.0


def test_late_reports_stay_refused_after_old_ticks_collapse_into_a_floor() -> None:
    bus = InProcBus(max_log=10)
    orch = Orchestrator(bus=bus, run_id="r", seed=1, config_hash="h", max_retained_batches=0)
    orch.attach()
    for t in range(5000):
        bus.publish(TRUST_TOPIC, _u("n-0", float(t)))
    orch.flush()
    assert len(orch._sealed_times) <= 4096
    before = orch.late_updates
    bus.publish(TRUST_TOPIC, _u("n-0", 10.0))
    bus.publish(TRUST_TOPIC, _u("n-0", 4990.0))
    assert orch.late_updates == before + 2


def test_the_verifier_index_agrees_with_a_plain_scan() -> None:
    """The per-device index replaced a quadratic scan; it must decide identically."""
    import random

    from agents.verifier import Finding, Verdict, VerifierReport

    rng = random.Random(3)
    nodes = [f"n-{i}" for i in range(30)] + [None]
    for trial in range(200):
        findings = [
            Finding(
                code=f"c{i}",
                severity=rng.choice(list(Verdict)),
                node_id=rng.choice(nodes) if trial % 5 else rng.choice(nodes[:-1]),
                detail="x",
            )
            for i in range(rng.randint(0, 40))
        ]
        report = VerifierReport(
            sim_time=1.0, run_id="r", seed=1, config_hash="h", verdict=Verdict.PASS
        )
        report.findings.extend(findings)
        for node in nodes[:-1]:
            scan = [f for f in findings if f.node_id in (None, node)]
            assert report.findings_for(node) == scan
            assert report.blocks(node) == any(f.severity is Verdict.FAIL for f in scan)
        late = Finding(code="late", severity=Verdict.FAIL, node_id=None, detail="x")
        report.findings.append(late)
        assert report.blocks("n-0"), "an appended finding is seen"


def test_the_orchestrator_window_is_bounded_in_reports(monkeypatch) -> None:
    monkeypatch.setattr(Orchestrator, "MAX_RETAINED_UPDATES", 12)
    bus = InProcBus()
    orch = Orchestrator(bus=bus, run_id="r", seed=1, config_hash="h")
    orch.attach()
    for t in range(20):
        for i in range(5):
            bus.publish(TRUST_TOPIC, _u(f"n-{i}", float(t)))
    orch.flush()
    assert sum(len(b.updates) for b in orch.batches) <= 12
    assert orch.updates_seen == 100


def test_the_audit_window_is_bounded_but_the_file_is_not(tmp_path) -> None:
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path=path, max_in_memory=10)
    for i in range(40):
        log.append(
            AuditRecord(
                sim_time=float(i),
                run_id="r",
                seed=1,
                config_hash="h",
                event_type="x",
                actor_id="a",
                payload={"i": i},
            )
        )
    assert len(log) == 10
    assert len(path.read_text(encoding="utf-8").splitlines()) == 40


def test_a_trimmed_chain_still_verifies_over_its_window(tmp_path) -> None:
    log = AuditLog(max_in_memory=5)
    for i in range(20):
        log.append(
            AuditRecord(
                sim_time=float(i),
                run_id="r",
                seed=1,
                config_hash="h",
                event_type="x",
                actor_id="a",
                payload={"i": i},
            )
        )
    assert log.verify() is None, "the window is internally consistent"


def test_divergence_history_is_a_rolling_window() -> None:
    """A lifetime average dilutes exactly the signal a rising rate should raise."""
    pipe = _pipe()
    pipe.classifier.window = 8
    for t in range(40):
        pipe.run(_batch([_u("n-0", float(t), level=0.9)], sim_time=float(t)))
    assert len(pipe.classifier.observations) == 8


def test_a_node_that_stops_reporting_is_detected() -> None:
    """A silenced monitor is a plausible precursor to compromising its device."""
    bus = InProcBus()
    pipe = _pipe()
    orch = Orchestrator(
        bus=bus, run_id="r", seed=1, config_hash="h", pipeline=pipe, silence_ticks=3
    )
    orch.attach()

    for t in range(2):
        for n in ("n-0", "n-1"):
            bus.publish(TRUST_TOPIC, _u(n, float(t), level=0.9))
    for t in range(2, 8):
        bus.publish(TRUST_TOPIC, _u("n-0", float(t), level=0.9))
    orch.flush()

    assert "n-1" in orch.silent_nodes
    assert "n-0" not in orch.silent_nodes


def test_silence_clears_when_a_node_reports_again() -> None:
    bus = InProcBus()
    orch = Orchestrator(bus=bus, run_id="r", seed=1, config_hash="h", silence_ticks=2)
    orch.attach()
    for n in ("n-0", "n-1"):
        bus.publish(TRUST_TOPIC, _u(n, 0.0, level=0.9))
    for t in range(1, 5):
        bus.publish(TRUST_TOPIC, _u("n-0", float(t), level=0.9))
    bus.publish(TRUST_TOPIC, _u("n-1", 5.0, level=0.9))
    bus.publish(TRUST_TOPIC, _u("n-0", 6.0, level=0.9))
    orch.flush()
    assert orch.silent_nodes == ()


def test_silence_is_reported_in_the_audit_record() -> None:
    bus = InProcBus()
    seen: list = []
    from agents.orchestrator import ORCHESTRATOR_TOPIC

    bus.subscribe(ORCHESTRATOR_TOPIC, lambda r: seen.append(r))
    orch = Orchestrator(bus=bus, run_id="r", seed=1, config_hash="h", silence_ticks=1)
    orch.attach()
    for n in ("n-0", "n-1"):
        bus.publish(TRUST_TOPIC, _u(n, 0.0, level=0.9))
    for t in range(1, 4):
        bus.publish(TRUST_TOPIC, _u("n-0", float(t), level=0.9))
    orch.flush()
    assert any("n-1" in r.payload.get("silent_nodes", []) for r in seen)


def test_a_flooding_agent_is_rate_limited() -> None:
    """Deduplication removes the benefit within a tick; this caps the cost."""
    bus = InProcBus()
    pipe = _pipe()
    orch = Orchestrator(
        bus=bus,
        run_id="r",
        seed=1,
        config_hash="h",
        pipeline=pipe,
        max_updates_per_agent_per_tick=3,
    )
    orch.attach()
    for _ in range(50):
        bus.publish(TRUST_TOPIC, _u("n-0", 1.0, level=0.9))
    orch.flush()

    assert orch.rate_limited_updates == 47
    assert len(pipe.outcomes[0].plans) == 1


def test_the_rate_limit_tolerates_an_ordinary_retry() -> None:
    """Above one, because a duplicated delivery is normal, not an attack."""
    bus = InProcBus()
    orch = Orchestrator(bus=bus, run_id="r", seed=1, config_hash="h")
    orch.attach()
    bus.publish(TRUST_TOPIC, _u("n-0", 1.0, level=0.9))
    bus.publish(TRUST_TOPIC, _u("n-0", 1.0, level=0.9))
    orch.flush()
    assert orch.rate_limited_updates == 0


def test_the_budget_is_per_agent_not_global() -> None:
    bus = InProcBus()
    orch = Orchestrator(
        bus=bus, run_id="r", seed=1, config_hash="h", max_updates_per_agent_per_tick=2
    )
    orch.attach()
    for n in range(10):
        bus.publish(TRUST_TOPIC, _u(f"n-{n}", 1.0, level=0.9))
    orch.flush()
    assert orch.rate_limited_updates == 0


def test_an_inflated_cti_is_caught_by_recomputation() -> None:
    """Omission is defeated by the fail-safe; inflation is detected."""
    from agents.correlation import CorrelationAgent
    from agents.verifier import VerifierAgent

    pipe = _pipe()
    batch = _batch([_u(f"n-{i}", 1.0, level=0.9) for i in range(6)])
    out = pipe.run(batch)

    inflated = out.correlation.model_copy(update={"cti": 0.99})
    from agents.verifier import VerifierParams

    report = VerifierAgent(VerifierParams(sample_every=1), correlator=CorrelationAgent()).audit(
        plans=out.plans, gt_updates=out.gt_updates, correlation=inflated, batch=batch
    )
    assert "cti_inflated" in report.codes()
    assert report.failed is False


def test_an_honest_correlation_passes_recomputation() -> None:
    """A restriction-planning tick is always rechecked, never sampled past."""
    pipe = _pipe()
    batch = _batch([_u(f"n-{i}", 1.0, level=0.05) for i in range(6)])
    out = pipe.run(batch)
    assert max(p.proposed_level for p in out.plans) >= 3, "a consequential tick"
    assert "cti_inflated" not in out.report.codes()
    assert "implication_fabricated" not in out.report.codes()


def test_fabricated_implication_is_surfaced() -> None:
    from agents.correlation import CorrelationAgent
    from agents.verifier import VerifierAgent

    pipe = _pipe()
    batch = _batch([_u(f"n-{i}", 1.0, level=0.95) for i in range(6)])
    out = pipe.run(batch)

    framed = out.correlation.model_copy(update={"implicated_node_ids": ["n-3"]})
    from agents.verifier import VerifierParams

    report = VerifierAgent(VerifierParams(sample_every=1), correlator=CorrelationAgent()).audit(
        plans=out.plans, gt_updates=out.gt_updates, correlation=framed, batch=batch
    )
    assert "implication_fabricated" in report.codes()


def test_an_attester_refuses_a_candidate_the_sealed_batches_never_showed() -> None:
    """An attester checks its own evidence."""
    from types import SimpleNamespace

    from agents.attester import IndependentAttester
    from agents.correlation import CorrelationAgent
    from m10_persona_drift.nhi import issue_signing_identity

    attester = IndependentAttester(
        identity=issue_signing_identity("verifier", seed=b"t"), correlator=CorrelationAgent()
    )
    for t in range(1, 12):
        attacked = [_u(f"n-{i}", float(t), level=0.3) for i in range(3)]
        healthy = [_u(f"n-{i}", float(t), level=0.95) for i in range(3, 12)]
        attester.observe(_batch(attacked + healthy, sim_time=float(t)))
    sealed = attester._evidence[-1][1]

    def candidate(pattern: str, nodes: tuple[str, ...], start: float = 0.0, end: float = 20.0):
        return SimpleNamespace(
            pattern_text=pattern, node_ids=nodes, window_start_sim=start, window_end_sim=end
        )

    assert attester.shows(candidate(sealed, ("n-0",))) is True
    assert attester.shows(candidate("a pattern nobody saw", ("n-0",))) is False
    assert attester.shows(candidate(sealed, ("n-0", "n-9"))) is False, "device never implicated"
    assert attester.shows(candidate(sealed, ("n-0",), 100.0, 120.0)) is False, "wrong window"


def test_a_publisher_view_carries_its_own_key_and_no_other() -> None:
    """A publisher must not hold the registry: it would hold every agent's forging key."""
    from m8_eval_harness.scenario_runner import RunContext
    from m10_persona_drift.nhi import issue_identity

    identities = {
        f"mon-n-{i}": issue_identity(f"mon-n-{i}", seed=bytes([i]) * 32) for i in range(3)
    }
    context = RunContext(
        bus=InProcBus(),
        run_id="r",
        seed=1,
        config_hash="h",
        pipeline=_pipe(),
        identities=identities,
    )
    view = context.as_agent("mon-n-0")
    assert view.identity.agent_id == "mon-n-0"
    assert not view.registry, "a publisher-only view must not hold anyone else's key"


def test_the_step_cap_bounds_the_rate_of_a_forged_rise_and_not_its_destination():
    """The patient liar: a monitor that forges its context too is never capped."""
    import tempfile
    from pathlib import Path

    from m8_eval_harness.baselines import by_id
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios.base import Anomaly, Scenario

    def run(**forgery):
        scenario = Scenario(
            scenario_id="patient-liar",
            name="patient liar",
            demonstrates="the step cap bounds a rate, not a destination",
            n_nodes=30,
            ticks=40,
            anomalies=(Anomaly("node-0", 10, 34, 0.7), Anomaly("node-1", 10, 34, 0.7)),
            ground_truth={"node-0": 10, "node-1": 10},
            seed=7900,
            **forgery,
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = run_scenario(scenario, by_id("full"), seed=7900, results_dir=Path(tmp))
        planned = {}
        for outcome in result.pipeline.outcomes:
            for plan in outcome.plans:
                planned.setdefault(plan.node_id, []).append(plan.proposed_level)
        return evaluate(result), planned

    loud, loud_levels = run(forged_observation={"node-0": 8.0})
    patient, patient_levels = run(forged_context={"node-0": 8.0})

    assert loud["trust_rise_capped"] > 0 and loud["agents_quarantined"] >= 1
    assert max(loud_levels["node-0"]) >= 2

    assert patient["trust_rise_capped"] == 0, "a legal step is never capped"
    assert patient["agents_quarantined"] == 0, "its reliability is untouched"
    assert max(patient_levels["node-0"]) == 0, "the lie holds for the whole attack"
    assert max(patient_levels["node-1"]) >= 2
    assert patient["residual_compromise"] > loud["residual_compromise"]


def test_a_correlation_agent_cannot_publish_a_recall_boost_memory_did_not_give() -> None:
    """The recall boost is not taken on trust from the correlation agent."""
    from agents.correlation import CorrelationAgent

    class InflatesRecall(CorrelationAgent):
        def correlate(self, batch, **kw):
            honest = super().correlate(batch, **kw)
            return honest.model_copy(update={"recall_boost": 1.0})

    def worst_levels(correlator) -> tuple[int, int]:
        pipe = _pipe(correlator=correlator)
        worst = 0
        for t in range(1, 30):
            degraded = [_u(f"n-{i}", float(t), level=0.74) for i in range(4)]
            healthy = [_u(f"n-{i}", float(t), level=0.95) for i in range(4, 20)]
            out = pipe.run(_batch(degraded + healthy, sim_time=float(t)))
            assert out.correlation.recall_boost == 0.0, "no memory, so no recall"
            worst = max([worst] + [p.proposed_level for p in out.plans])
        return worst, pipe.correlation_overstated

    honest_worst, _ = worst_levels(CorrelationAgent())
    lying_worst, flagged = worst_levels(InflatesRecall())
    assert lying_worst == honest_worst, "the inflated boost changes nothing that acts"
    assert flagged > 0, "and the overstatement is counted"


def test_the_bound_takes_its_coefficients_from_the_assembler_not_the_correlator() -> None:
    """The independent recomputation takes its coefficients at assembly."""
    from agents.correlation import CorrelationAgent, CorrelationParams

    correlator = CorrelationAgent()
    pipe = _pipe(correlator=correlator, bound_correlator=CorrelationAgent(CorrelationParams()))
    correlator.params = correlator.params.model_copy(update={"campaign_ti_threshold": 0.0})
    out = pipe.run(_batch([_u(f"n-{i}", 1.0, level=0.95) for i in range(10)]))
    assert out.correlation.implicated_node_ids == []
    assert pipe.correlation_overstated == 1


def test_recall_provenance_covers_the_tick_on_which_recall_reaches_fused_trust() -> None:
    """Fusion reads t-1, so recall lands a tick late, and the provenance floor follows it."""
    from types import SimpleNamespace

    from agents.correlation import CorrelationAgent

    recall_now = {"on": False}

    class OneTickMemory:
        def recognise(self, pattern_text):
            best = SimpleNamespace(record_id="rec-1", similarity=1.0)
            return SimpleNamespace(recognised=recall_now["on"], best=best, cti_boost=0.25)

    class ForgetsDeviceZero(CorrelationAgent):
        """Omit n-0 from the list, so only fusion's fail-safe implicates it."""

        def correlate(self, batch, **kw):
            out = super().correlate(batch, **kw)
            kept = [n for n in out.implicated_node_ids if n != "n-0"]
            return out.model_copy(update={"implicated_node_ids": kept})

    pipe = _pipe(recall=OneTickMemory(), correlator=ForgetsDeviceZero())
    provenance_by_tick: dict[int, str] = {}
    for t in range(1, 8):
        recall_now["on"] = t == 5
        attacked = [_u(f"n-{i}", float(t), level=0.1) for i in range(4)]
        healthy = [_u(f"n-{i}", float(t), level=0.95) for i in range(4, 12)]
        out = pipe.run(_batch(attacked + healthy, sim_time=float(t)))
        for plan, ex in zip(out.plans, out.executions, strict=True):
            if plan.node_id == "n-0" and ex.audit is not None:
                provenance_by_tick[t] = ex.audit.payload["input_provenance"]

    assert provenance_by_tick[5] == "MEDIUM", "recall touched n-0 this tick"
    assert provenance_by_tick[6] == "MEDIUM", "and its boost is in n-0's GT this tick"
    assert provenance_by_tick[7] == "HIGH", "and after that it is gone"
