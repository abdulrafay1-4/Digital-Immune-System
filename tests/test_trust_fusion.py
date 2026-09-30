"""M6 Global Trust Fusion: hand-computed and per-node CTI tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from m4_response_engine.levels import ResponseLevel, level_for_gt
from m6_trust_fusion import (
    FusionParams,
    MasterScoreWeights,
    ReputationTracker,
    TrustFusionEngine,
    cti_for_node,
    fuse_gt,
    interaction_success,
    master_score,
)
from m6_trust_fusion.reputation import RepMode, ReputationParams
from shared.bus import InProcBus
from shared.schemas import (
    ContextVector,
    CorrelationResult,
    Provenance,
    ResponsePlan,
    TrustUpdate,
)


def _corr(
    *,
    cti: float,
    implicated: list[str],
    node_ids: list[str] | None = None,
) -> CorrelationResult:
    return CorrelationResult(
        sim_time=1.0,
        run_id="r",
        seed=1,
        config_hash="h",
        node_ids=node_ids or implicated,
        cti=cti,
        implicated_node_ids=implicated,
    )


def _tu(node_id: str, ts: float, sim_time: float = 0.0) -> TrustUpdate:
    return TrustUpdate(
        sim_time=sim_time,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id=node_id,
        node_trust=ts,
        observation=ts,
        context=ContextVector(identity=ts, behavioral=ts, device=ts, network=ts),
        provenance=Provenance.HIGH,
        agent_id=f"mon-{node_id}",
    )


def _engine() -> TrustFusionEngine:
    return TrustFusionEngine(bus=InProcBus(), run_id="r", seed=1, config_hash="h")


def test_fusion_weights_must_sum_to_one() -> None:
    with pytest.raises(ValueError):
        FusionParams(alpha=0.5, beta=0.5, gamma=0.5)


def test_fuse_gt_hand_computed() -> None:
    gt, cti_trust = fuse_gt(ts=1.0, cti_i=0.0, rep=1.0)
    assert cti_trust == 1.0
    assert abs(gt - 1.0) < 1e-12

    gt2, ct2 = fuse_gt(ts=1.0, cti_i=1.0, rep=1.0)
    assert ct2 == 0.0
    assert abs(gt2 - 0.65) < 1e-12


def test_cti_for_node_implicated_vs_clean() -> None:
    corr = _corr(cti=0.8, implicated=["node-0"], node_ids=["node-0", "node-1"])
    assert cti_for_node("node-0", corr) == 0.8
    assert cti_for_node("node-1", corr) == 0.0


def test_implicated_node_gets_lower_gt_than_clean_peer() -> None:
    bus = InProcBus()
    eng = TrustFusionEngine(bus=bus, run_id="r", seed=1, config_hash="h")
    corr = _corr(cti=0.9, implicated=["victim"], node_ids=["victim", "peer"])
    eng.observe_correlation(corr)

    eng.observe_trust(_tu("victim", 0.7, sim_time=0.0))
    eng.observe_trust(_tu("peer", 0.7, sim_time=0.0))

    v = eng.observe_trust(_tu("victim", 0.7, sim_time=1.0))
    p = eng.observe_trust(_tu("peer", 0.7, sim_time=1.0))
    assert v.cti_i == 0.9
    assert p.cti_i == 0.0
    assert v.gt < p.gt
    assert v.threat_confirmed is False, (
        "implicated by correlation, but its own trust is still high -- one source "
        "is not confirmation"
    )
    assert p.threat_confirmed is False


def test_same_tick_cti_change_does_not_affect_current_gt() -> None:
    bus = InProcBus()
    eng = TrustFusionEngine(bus=bus, run_id="r", seed=1, config_hash="h")
    eng.observe_correlation(_corr(cti=0.0, implicated=[], node_ids=["n0"]))
    first = eng.observe_trust(_tu("n0", 0.7, sim_time=0.0))
    assert first.cti_i == 0.0

    eng.observe_correlation(_corr(cti=1.0, implicated=["n0"], node_ids=["n0"]))
    second = eng.observe_trust(_tu("n0", 0.7, sim_time=1.0))
    assert second.cti_i == 0.0
    assert abs(second.gt - first.gt) < 1e-12

    third = eng.observe_trust(_tu("n0", 0.7, sim_time=2.0))
    assert third.cti_i == 1.0
    assert third.gt < second.gt


def test_reputation_floor_and_ratio() -> None:
    tr = ReputationTracker(ReputationParams(mode=RepMode.RATIO))
    assert tr.get("n") == 1.0
    tr.record("n", success=True)
    tr.record("n", success=False)
    assert abs(tr.get("n") - 0.5) < 1e-12


def test_master_score_weights() -> None:
    with pytest.raises(ValueError):
        MasterScoreWeights(w_ts=1.0, w_cti=1.0, w_gt=0, w_resp=0, w_health=0)
    s = master_score(ts=1.0, cti_i=0.0, gt=1.0)
    assert abs(s - 1.0) < 1e-12


def test_publishes_on_trust_global_topic() -> None:
    bus = InProcBus()
    eng = TrustFusionEngine(bus=bus, run_id="r", seed=1, config_hash="h")
    eng.observe_trust(_tu("n0", 1.0))
    topics = [t for t, _ in bus.log]
    assert "trust.global" in topics


def test_interaction_rule_l0_succeeds_and_everything_else_does_not() -> None:
    assert interaction_success(0) is True
    assert [interaction_success(n) for n in (1, 2, 3, 4)] == [False] * 4
    with pytest.raises(ValueError):
        interaction_success(5)


def test_rep_stays_at_init_until_something_records() -> None:
    """REP stays at its initial value until a response is recorded."""
    tr = ReputationTracker()
    assert tr.get("n-1") == 1.0
    assert tr.snapshot() == {}


def test_observe_response_drives_rep_down_for_a_node_under_response() -> None:
    eng = _engine()
    assert eng.reputation.get("n-1") == 1.0
    eng.observe_response("n-1", 3)
    assert eng.reputation.get("n-1") == pytest.approx(0.6), "one bad response, lam_down"
    for _ in range(5):
        eng.observe_response("n-1", 3)
    assert eng.reputation.get("n-1") == pytest.approx(0.05), "floored after ~6"


def test_observe_responses_records_a_whole_tick_in_node_order() -> None:
    eng = _engine()
    plans = [
        ResponsePlan(
            sim_time=1.0,
            run_id="r",
            seed=1,
            config_hash="h",
            node_id=nid,
            proposed_level=lvl,
            rationale="",
        )
        for nid, lvl in (("n-2", 0), ("n-1", 3))
    ]
    out = eng.observe_responses(plans)
    assert list(out) == ["n-1", "n-2"], "stable node order, not arrival order"
    assert out["n-1"] < 1.0, "a restricted device loses reputation"
    assert out["n-2"] == 1.0, "a clean one keeps it"


def test_l4_is_unreachable_while_rep_is_pinned_at_its_maximum() -> None:
    """Why the missing producer mattered, stated as arithmetic."""
    best_case_gt, _ = fuse_gt(ts=0.05, cti_i=1.0, rep=1.0)
    assert best_case_gt > 0.20
    assert level_for_gt(best_case_gt) == ResponseLevel.RESTRICT


def test_l4_becomes_reachable_once_rep_can_fall() -> None:
    eng = _engine()
    for _ in range(8):
        eng.observe_response("n-1", 3)
    rep = eng.reputation.get("n-1")

    gt, _ = fuse_gt(ts=0.05, cti_i=1.0, rep=rep)
    assert gt <= 0.20
    assert level_for_gt(gt) == ResponseLevel.ISOLATE


def test_fusion_reads_rep_live_so_a_response_lands_on_the_next_tick() -> None:
    """ "Fusion at t reads REP through t-1": one tick behind, not two."""
    eng = _engine()
    u1 = _tu("n-1", 0.9, sim_time=1.0)
    first = eng.observe_trust(u1)
    assert first.rep == 1.0

    eng.observe_response("n-1", 3)

    second = eng.observe_trust(_tu("n-1", 0.9, sim_time=2.0))
    assert second.rep < 1.0, "the tick-1 response must be visible at tick 2"


def _corr_omitting(node_id: str) -> CorrelationResult:
    """A compromised correlation agent: real campaign, one device left off."""
    return _corr(cti=0.80, implicated=["other"], node_ids=[node_id, "other"])


def test_omitting_a_node_from_the_implicated_list_no_longer_pays() -> None:
    """The cheapest attack on correlation is silence, not fabrication."""
    corr = _corr_omitting("victim")
    assert cti_for_node("victim", corr) == 0.0, "the list alone says nothing"
    assert cti_for_node("victim", corr, node_ts=0.10) == pytest.approx(0.80)


def test_the_fail_safe_does_not_implicate_a_healthy_node() -> None:
    corr = _corr_omitting("victim")
    assert cti_for_node("bystander", corr, node_ts=0.95) == 0.0


def test_an_explicitly_implicated_node_is_unaffected() -> None:
    corr = _corr(cti=0.60, implicated=["n0"], node_ids=["n0"])
    assert cti_for_node("n0", corr, node_ts=0.70) == pytest.approx(0.60)


def test_correlation_cannot_originate_a_threat() -> None:
    """A device whose own trust is in the L0 band gets nothing from the fleet view."""
    corr = _corr(cti=0.95, implicated=["n0"], node_ids=["n0"])
    assert cti_for_node("n0", corr, node_ts=0.99) == 0.0
    assert cti_for_node("n0", corr, node_ts=0.81) == 0.0
    assert cti_for_node("n0", corr, node_ts=0.80) > 0.0, "0.80 is already L1"
    assert cti_for_node("n0", corr) == pytest.approx(0.95), "no own trust given: list only"


def test_omitting_node_ts_keeps_the_old_behaviour_for_the_no_sharing_baseline() -> None:
    corr = _corr_omitting("victim")
    assert cti_for_node("victim", corr) == 0.0


def test_fusion_applies_the_fail_safe_end_to_end() -> None:
    eng = _engine()
    eng.observe_correlation(_corr_omitting("victim"))
    eng.observe_trust(_tu("victim", 0.10, sim_time=0.0))
    second = eng.observe_trust(_tu("victim", 0.10, sim_time=1.0))
    assert second.cti_i > 0.0, "the omitted node still carries the campaign score"


def test_the_implication_threshold_is_validated() -> None:
    with pytest.raises(ValueError):
        FusionParams(implicate_below_ts=1.5)


def test_reputation_falls_fast_and_is_earned_back_slowly() -> None:
    """The same asymmetry as hysteresis and as self-healing."""
    tr = ReputationTracker()
    for _ in range(6):
        tr.record("n", success=False)
    assert tr.get("n") == pytest.approx(0.05, abs=0.01), "floored in about six"

    for _ in range(20):
        tr.record("n", success=True)
    partly = tr.get("n")
    assert 0.5 < partly < 0.8, "twenty clean responses buys back most of it"

    for _ in range(40):
        tr.record("n", success=True)
    assert tr.get("n") > partly


def test_reputation_forgets_so_healing_is_not_cancelled() -> None:
    """The plain ratio never forgets."""
    ratio = ReputationTracker(ReputationParams(mode=RepMode.RATIO))
    ewma = ReputationTracker()
    for tracker in (ratio, ewma):
        for _ in range(50):
            tracker.record("n", success=False)
        for _ in range(50):
            tracker.record("n", success=True)

    assert ratio.get("n") == pytest.approx(0.5)
    assert ewma.get("n") > 0.9


def test_reputation_must_not_be_earned_back_faster_than_it_is_lost() -> None:
    with pytest.raises(ValueError, match="earned back more"):
        ReputationParams(lam_down=0.95, lam_up=0.6)


def test_interaction_count_is_tracked_in_both_modes() -> None:
    tr = ReputationTracker()
    for _ in range(3):
        tr.record("n", success=True)
    assert tr.interactions("n") == 3


def test_confirmation_needs_two_independent_sources() -> None:
    """Correlation's output cannot corroborate correlation's output."""
    eng = _engine()
    eng.observe_correlation(_corr(cti=0.9, implicated=["victim"], node_ids=["victim"]))

    eng.observe_trust(_tu("victim", 0.70, sim_time=0.0))
    high_trust = eng.observe_trust(_tu("victim", 0.70, sim_time=1.0))
    assert high_trust.cti_i > 0.0, "the fleet implicated it"
    assert high_trust.threat_confirmed is False, "but its own history disagrees"

    eng.observe_trust(_tu("victim", 0.10, sim_time=2.0))
    both = eng.observe_trust(_tu("victim", 0.10, sim_time=3.0))
    assert both.threat_confirmed is True, "now both sources agree"


def test_low_trust_alone_is_not_confirmation_either() -> None:
    eng = _engine()
    eng.observe_trust(_tu("lonely", 0.10, sim_time=0.0))
    second = eng.observe_trust(_tu("lonely", 0.10, sim_time=1.0))
    assert second.cti_i == 0.0
    assert second.threat_confirmed is False


def test_a_silent_device_decays_once_per_tick_and_never_below_the_floor() -> None:
    """Silence decay is applied once per tick and respects TS_min."""
    import math

    from m6_trust_fusion.fusion import TrustFusionEngine
    from shared.bus import InProcBus
    from shared.schemas import ContextVector, Provenance, TrustUpdate

    def seen(level: float) -> TrustFusionEngine:
        f = TrustFusionEngine(bus=InProcBus(), run_id="r", seed=1, config_hash="h")
        f.fuse_batch(
            [
                TrustUpdate(
                    sim_time=0.0,
                    run_id="r",
                    seed=1,
                    config_hash="h",
                    node_id="n",
                    node_trust=level,
                    observation=level,
                    provenance=Provenance.HIGH,
                    context=ContextVector(
                        identity=level, behavioral=level, device=level, network=level
                    ),
                    agent_id="mon-n",
                )
            ]
        )
        return f

    f = seen(0.9)
    for t in range(1, 41):
        ts = f.observe_silence("n", sim_time=float(t)).ts
        assert ts == pytest.approx(0.9 * math.exp(-0.01 * t), abs=1e-9)

    f = seen(0.9)
    for t in range(1, 400):
        ts = f.observe_silence("n", sim_time=float(t)).ts
    assert ts == pytest.approx(f.params.ts_min), "floored, not driven to zero"


def test_fusions_trust_floor_mirrors_the_monitoring_agents() -> None:
    from m6_trust_fusion.fusion import FusionParams
    from shared.run_manifest import load_yaml_config

    cfg = load_yaml_config(Path("configs/default.yaml"))
    assert FusionParams().ts_min == cfg["trust"]["ts_min"]
