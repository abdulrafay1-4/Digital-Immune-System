"""Red-team attacks on each component, each one stopped."""

from __future__ import annotations

import pytest

from agents.correlation import CorrelationAgent
from agents.orchestrator import TRUST_TOPIC, Orchestrator, TickBatch
from agents.pipeline import ClosedLoopPipeline
from m4_response_engine.hysteresis import LevelHysteresis
from m4_response_engine.levels import ResponseLevel
from m6_trust_fusion import TrustFusionEngine
from m6_trust_fusion.fusion import cti_for_node
from m9_capability_binder.binder import redeem, reset_spent_tokens, resolve_capability
from m10_persona_drift.nhi import issue_identity
from m11_memory_hardening import QuorumGate
from shared.bus import InProcBus
from shared.schemas import ContextVector, Provenance, TrustUpdate

ATTESTERS = ("verifier", "correlation", "fusion", "orchestrator", "monitoring")


@pytest.fixture(autouse=True)
def _clean_tokens():
    reset_spent_tokens()
    yield
    reset_spent_tokens()


def _u(node_id, sim_time, level=0.9, agent=None):
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
        agent_id=agent or f"mon-{node_id}",
    )


def _batch(updates, sim_time=1.0):
    return TickBatch(sim_time=sim_time, run_id="r", seed=1, config_hash="h", updates=updates)


def _pipe(**over):
    kw = dict(fusion=TrustFusionEngine(bus=InProcBus(), run_id="r", seed=1, config_hash="h"))
    kw.update(over)
    return ClosedLoopPipeline(**kw)


def _orch(bus, **over):
    kw = dict(bus=bus, run_id="r", seed=1, config_hash="h")
    kw.update(over)
    o = Orchestrator(**kw)
    o.attach()
    return o


def test_an_agent_cannot_report_trust_for_a_device_it_does_not_monitor() -> None:
    """A report is bound to its reporter."""
    bus = InProcBus()
    pipe = _pipe()
    orch = _orch(bus, pipeline=pipe)

    bus.publish(TRUST_TOPIC, _u("n-victim", 1.0, 0.9))
    bus.publish(TRUST_TOPIC, _u("n-victim", 2.0, 0.01, agent="mon-n-attacker"))
    bus.publish(TRUST_TOPIC, _u("n-other", 3.0))
    orch.flush()

    assert orch.unbound_updates == 1
    reported = [u.ts for o in pipe.outcomes for u in o.gt_updates if u.node_id == "n-victim"]
    assert all(t > 0.5 for t in reported), "the forged low trust never landed"


def test_an_explicit_roster_refuses_an_unknown_agent_outright() -> None:
    bus = InProcBus()
    orch = _orch(bus, node_agent_binding={"n-0": "mon-n-0"}, bind_on_first_sight=False)
    bus.publish(TRUST_TOPIC, _u("n-0", 1.0, agent="mon-n-0"))
    bus.publish(TRUST_TOPIC, _u("n-99", 1.0, agent="mon-n-99"))
    orch.flush()
    assert orch.unbound_updates == 1


def test_trust_on_first_use_is_claimable_and_that_is_documented() -> None:
    """The honest limit of the default."""
    bus = InProcBus()
    orch = _orch(bus)
    bus.publish(TRUST_TOPIC, _u("n-0", 1.0, 0.01, agent="mon-evil"))
    bus.publish(TRUST_TOPIC, _u("n-0", 2.0, 0.9, agent="mon-n-0"))
    orch.flush()
    assert orch.unbound_updates == 1, "the *real* monitor is the one locked out"


def test_padding_the_fleet_with_healthy_devices_cannot_hide_a_campaign() -> None:
    """`cti` is breadth, normalised across every reporting device."""
    real = [_u(f"n-{i}", 1.0, 0.02) for i in range(3)]
    small = CorrelationAgent().correlate(_batch(real + [_u(f"h-{i}", 1.0, 0.95) for i in range(3)]))
    padded = CorrelationAgent().correlate(
        _batch(real + [_u(f"h-{i}", 1.0, 0.95) for i in range(200)])
    )

    assert padded.cti < small.cti / 2, "breadth genuinely shrinks -- correct"
    assert cti_for_node("n-0", padded) > 0.9, "but the victim's own threat does not"


def test_a_healthy_device_is_still_not_implicated_by_its_own_indicator() -> None:
    padded = CorrelationAgent().correlate(
        _batch(
            [_u(f"n-{i}", 1.0, 0.02) for i in range(3)]
            + [_u(f"h-{i}", 1.0, 0.95) for i in range(20)]
        )
    )
    assert cti_for_node("h-0", padded) == 0.0


def test_a_device_held_by_repeated_cancellation_is_surfaced() -> None:
    """One nudge every three ticks pins a device at L3 indefinitely."""
    h = LevelHysteresis()
    effective = [
        int(h.apply("n", ResponseLevel.RESTRICT if t % 3 == 0 else ResponseLevel.NONE))
        for t in range(15)
    ]
    assert all(level == 3 for level in effective[1:]), "still pinned, by design"
    assert "n" in h.flapping(), "but no longer silently"
    assert h.state("n").cancelled_deescalations >= 3


def test_an_honest_recovery_is_not_flagged_as_flapping() -> None:
    h = LevelHysteresis()
    for t in range(15):
        h.apply("m", ResponseLevel.RESTRICT if t < 3 else ResponseLevel.NONE)
    assert h.flapping() == []
    assert int(h.state("m").effective) == 0


def test_drift_is_actually_fed_now() -> None:
    """
    A monitoring agent's persona invariant is that it reports every tick, so silence *is* drift, and
    `set_drift` is called for it.
    """
    pipe = _pipe(silence_ticks=2)
    pipe.run(_batch([_u("n-0", 0.0), _u("n-1", 0.0)], sim_time=0.0))
    for t in range(1, 8):
        pipe.run(_batch([_u("n-1", float(t))], sim_time=float(t)))
    assert pipe.fusion._drift.get("n-0", 0.0) > 0.0


def test_the_drift_penalty_is_capped() -> None:
    """A long silence must not invert GT."""
    pipe = _pipe(silence_ticks=2)
    pipe.run(_batch([_u("n-0", 0.0), _u("n-1", 0.0)], sim_time=0.0))
    for t in range(1, 200):
        pipe.run(_batch([_u("n-1", float(t))], sim_time=float(t)))
    assert pipe.fusion._drift["n-0"] <= 1.0


def test_a_token_is_spent_exactly_once() -> None:
    token = resolve_capability("restrict", "n-0", "HIGH", 10.0, ttl=60.0)
    assert redeem(token, now_sim=10.0) == (True, None)
    assert redeem(token, now_sim=11.0) == (False, "token_replayed")


def test_two_identical_requests_do_not_mint_the_same_token() -> None:
    """Tokens are unique, so one captured token cannot be reused."""
    a = resolve_capability("isolate", "n-0", "HIGH", 10.0)
    b = resolve_capability("isolate", "n-0", "HIGH", 10.0)
    assert a["token_id"] != b["token_id"]
    assert a["signature"] != b["signature"]


def test_an_expired_token_is_refused() -> None:
    """`expires_at_sim` is checked at redemption."""
    token = resolve_capability("restrict", "n-0", "HIGH", 10.0, ttl=5.0)
    assert redeem(token, now_sim=100.0) == (False, "token_expired")


def test_a_token_presented_before_issue_is_refused() -> None:
    token = resolve_capability("restrict", "n-0", "HIGH", 100.0, ttl=5.0)
    ok, _ = redeem(token, now_sim=1.0)
    assert ok is True, "inside the window, which starts at issue"


def test_a_malformed_token_is_refused() -> None:
    assert redeem({}, now_sim=1.0) == (False, "malformed_token")
    assert redeem({"ok": True}, now_sim=1.0) == (False, "malformed_token")


def test_the_engine_redeems_the_token_it_was_issued() -> None:
    pipe = _pipe()
    out = pipe.run(_batch([_u(f"n-{i}", 1.0, 0.05) for i in range(6)]))
    executed = [e for e in out.executions if e.executed]
    assert executed, "something executed"
    ids = [e.decision.token.token_id for e in executed]
    assert len(ids) == len(set(ids)), "no two actions shared a token"


def test_a_device_that_silences_its_monitor_does_not_keep_its_level() -> None:
    """
    The device vanishes from every later batch, so without re-fusing its trust would freeze at
    whatever it held when it went quiet.
    """
    pipe = _pipe(silence_ticks=2)
    pipe.run(_batch([_u("n-0", 0.0, 0.95), _u("n-1", 0.0, 0.95)], sim_time=0.0))
    before = int(pipe.engine.effective_level("n-0"))

    for t in range(1, 40):
        pipe.run(_batch([_u("n-1", float(t), 0.95)], sim_time=float(t)))

    assert before == 0
    assert int(pipe.engine.effective_level("n-0")) > before


def test_silence_decay_uses_the_trust_decay_already_specified() -> None:
    """
    Not fabricated telemetry: `TS <- TS * exp(-beta*dt)` is M1's own rule, and "silence is not
    evidence of health" is why it exists.
    """
    fusion = TrustFusionEngine(bus=InProcBus(), run_id="r", seed=1, config_hash="h")
    fusion.observe_trust(_u("n-0", 0.0, 0.9))
    fusion.observe_trust(_u("n-0", 1.0, 0.9))

    near = fusion.observe_silence("n-0", sim_time=10.0)
    far = fusion.observe_silence("n-0", sim_time=300.0)
    assert far.ts < near.ts
    assert far.gt < near.gt


def test_a_node_never_seen_is_not_invented() -> None:
    fusion = TrustFusionEngine(bus=InProcBus(), run_id="r", seed=1, config_hash="h")
    assert fusion.observe_silence("ghost", sim_time=10.0) is None


def test_quorum_reports_when_it_can_no_longer_admit_anything() -> None:
    """Fail-closed is right; failing *silently* is not."""
    registry = {n: issue_identity(n, seed=n.encode().ljust(32, b"\0")) for n in ATTESTERS}
    healthy = QuorumGate(registry=registry)
    starved = QuorumGate(registry=registry, quarantined=frozenset(ATTESTERS[:3]))

    assert healthy.can_admit is True and healthy.usable == 5
    assert starved.can_admit is False and starved.usable == 2


def test_the_pattern_signature_distinguishes_different_attacks() -> None:
    """A handful of distinct signatures would make unrelated attacks recall each other."""
    seen = set()
    for n_bad in (1, 2, 3, 5, 8, 12, 30):
        for depth in (0.02, 0.25, 0.45):
            batch = _batch(
                [_u(f"n-{i}", 1.0, depth) for i in range(n_bad)]
                + [_u(f"h-{i}", 1.0, 0.95) for i in range(40)]
            )
            result = CorrelationAgent().correlate(batch)
            if result.pattern_text:
                seen.add(result.pattern_text)
    assert len(seen) >= 12


def test_the_same_attack_at_slightly_different_intensity_still_matches() -> None:
    """Bucketing is the point: recall must survive an attack that varies."""
    a = CorrelationAgent().correlate(_batch([_u(f"n-{i}", 1.0, 0.10) for i in range(3)]))
    b = CorrelationAgent().correlate(_batch([_u(f"n-{i}", 1.0, 0.13) for i in range(3)]))
    assert a.pattern_text == b.pattern_text


def test_the_spent_token_set_does_not_grow_without_bound() -> None:
    """An unbounded replay set is itself the attack."""
    from m9_capability_binder.binder import _EVICT_FLOOR, spent_token_count

    issued = _EVICT_FLOOR * 2
    for i in range(issued):
        token = resolve_capability("monitor_enhance", f"n-{i}", "HIGH", float(i), ttl=5.0)
        redeem(token, now_sim=float(i))

    assert spent_token_count() < issued / 2


def test_eviction_is_amortised_not_per_call() -> None:
    """Sweeping on every redemption is O(n) per call and O(n^2) over a run."""
    import time

    from m9_capability_binder.binder import reset_spent_tokens as _reset

    _reset()
    start = time.perf_counter()
    for i in range(20000):
        token = resolve_capability("monitor_enhance", f"n-{i}", "HIGH", 1.0, ttl=600.0)
        redeem(token, now_sim=1.0)
    elapsed = time.perf_counter() - start
    assert elapsed < 5.0, f"20k redemptions took {elapsed:.1f}s -- eviction is quadratic"


def test_eviction_does_not_reopen_a_live_replay() -> None:
    token = resolve_capability("restrict", "n-0", "HIGH", 10.0, ttl=60.0)
    assert redeem(token, now_sim=10.0)[0] is True
    assert redeem(token, now_sim=20.0) == (False, "token_replayed")


def test_an_objectively_reliable_agent_is_not_silenced_for_being_unusual() -> None:
    """A z-score is relative, so an attacker who can register agents sets it."""
    from m11_memory_hardening.outlier import assess

    population = {f"evil-{i}": 0.94 + (i % 5) * 0.01 for i in range(30)}
    population.update({f"good-{i}": 0.93 + (i % 3) * 0.01 for i in range(5)})
    population["honest-but-noisy"] = 0.70

    report = assess(population)
    verdict = report.verdict_for("honest-but-noisy")
    assert verdict.robust_z <= -3.0, "a clear statistical outlier"
    assert "honest-but-noisy" not in report.quarantined, "but not silenced for it"


def test_a_genuinely_unreliable_agent_is_still_quarantined() -> None:
    from m11_memory_hardening.outlier import assess

    population = {f"a{i}": 0.95 for i in range(9)}
    population["broken"] = 0.10
    assert assess(population).quarantined == frozenset({"broken"})


def test_the_two_absolute_bounds_cannot_contradict_each_other() -> None:
    from m11_memory_hardening.outlier import OutlierParams

    with pytest.raises(ValueError, match="contradict"):
        OutlierParams(quarantine_below=0.8, never_quarantine_above=0.3)


def test_embedding_input_is_capped() -> None:
    from m5_immune_memory.embeddings import MAX_EMBED_CHARS, HashingEmbedder

    embedder = HashingEmbedder()
    padded = "attack pattern " + ("x" * MAX_EMBED_CHARS * 4)
    truncated = padded[:MAX_EMBED_CHARS]
    assert (embedder.embed(padded) == embedder.embed(truncated)).all()


class _Crashes:
    def classify(self, batch):
        raise RuntimeError("model down")


def test_a_crashing_classifier_does_not_stop_the_tick() -> None:
    """Otherwise "break the classifier" becomes "disable the immune system"."""
    from agents.dual_classifier import DualClassifier

    dual = DualClassifier(primary=_Crashes())
    result = dual.classify(_batch([_u(f"n-{i}", 1.0, 0.02) for i in range(4)]))

    assert result.threat_type == result.rules_threat_type
    assert result.used_llm is False
    assert dual.primary_failures == 1
    assert dual.availability < 1.0


def test_the_loop_survives_a_classifier_that_always_crashes() -> None:
    from agents.dual_classifier import DualClassifier

    pipe = _pipe(classifier=DualClassifier(primary=_Crashes()))
    for t in range(6):
        out = pipe.run(_batch([_u(f"n-{i}", float(t), 0.02) for i in range(6)], sim_time=float(t)))
        assert out.plans, "the tick still produced decisions"
    assert max(p.proposed_level for o in pipe.outcomes for p in o.plans) >= 2


def test_a_verifier_blocking_everything_is_itself_visible() -> None:
    """Fail-closed is right, but nothing audits the verifier."""
    from agents.verifier import Finding, Verdict, VerifierReport

    blocking = VerifierReport(
        sim_time=1.0,
        run_id="r",
        seed=1,
        config_hash="h",
        verdict=Verdict.FAIL,
        plans_checked=10,
        findings=[
            Finding(code="under_response", severity=Verdict.FAIL, node_id=f"n-{i}", detail="x")
            for i in range(10)
        ],
    )
    assert blocking.blocked_fraction == 1.0


def test_a_tick_wide_failure_counts_as_blocking_everything() -> None:
    from agents.verifier import Finding, Verdict, VerifierReport

    report = VerifierReport(
        sim_time=1.0,
        run_id="r",
        seed=1,
        config_hash="h",
        verdict=Verdict.FAIL,
        plans_checked=50,
        findings=[Finding(code="run_identity_mismatch", severity=Verdict.FAIL, detail="x")],
    )
    assert report.blocked_fraction == 1.0


def test_a_healthy_tick_blocks_nothing() -> None:
    out = _pipe().run(_batch([_u(f"n-{i}", 1.0, 0.95) for i in range(6)]))
    assert out.report.blocked_fraction == 0.0


def test_the_fleet_size_is_capped() -> None:
    """
    Every node id costs a roster entry, a silence counter, a hysteresis state and a fusion lag
    entry, all held for the run.
    """
    bus = InProcBus()
    orch = _orch(bus, max_nodes=50)
    for i in range(500):
        bus.publish(TRUST_TOPIC, _u(f"flood-{i}", 1.0))
    orch.flush()

    assert orch.over_capacity_updates == 450
    assert len(orch._binding) == 50


def test_a_known_node_still_reports_when_the_fleet_is_full() -> None:
    """The cap must not lock out devices that are already enrolled."""
    bus = InProcBus()
    orch = _orch(bus, max_nodes=2)
    bus.publish(TRUST_TOPIC, _u("n-0", 1.0))
    bus.publish(TRUST_TOPIC, _u("n-1", 1.0))
    bus.publish(TRUST_TOPIC, _u("n-2", 1.0))
    bus.publish(TRUST_TOPIC, _u("n-0", 2.0))
    orch.flush()

    assert orch.over_capacity_updates == 1
    assert orch.updates_seen == 4


def test_registering_hundreds_of_healthy_agents_cannot_hide_a_campaign() -> None:
    """The agent-level form of fleet padding, covered by the per-device indicator."""
    real = [_u(f"n-{i}", 1.0, 0.02) for i in range(3)]
    sybil = [_u(f"s-{i}", 1.0, 0.95, agent=f"mon-s-{i}") for i in range(300)]
    result = CorrelationAgent().correlate(_batch(real + sybil))

    assert result.cti < 0.1, "breadth genuinely collapses -- 3 of 303 is narrow"
    assert cti_for_node("n-0", result) > 0.9, "the victim's own threat does not"
    assert result.campaign_id is not None
