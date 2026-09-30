"""M7 self-healing: recovery maths, the state machine, and the healing attacks."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from m1_monitoring.core.trust import TrustParams, TrustState
from m7_self_healing import (
    HealingParams,
    NodeHealingState,
    Phase,
    SelfHealingEngine,
    converge,
    recovery_score,
    should_heal,
    ticks_to_reach,
)

SICK = dict(gt=0.20, health=0.30)
REPAIRED = dict(gt=0.72, health=0.90)


def _engine(**over) -> SelfHealingEngine:
    return SelfHealingEngine(params=HealingParams(**over))


def _drive(engine, node_id, steps, *, approval_at=None):
    """Run `steps` of (gt, health) and collect the phases that were entered."""
    phases = []
    for t, obs in enumerate(steps):
        ev = engine.observe(
            node_id,
            sim_time=float(t),
            approval_granted=(approval_at is not None and t >= approval_at),
            **obs,
        )
        if ev is not None:
            phases.append(ev.phase)
    return phases


def test_the_heal_trigger_is_the_configured_threshold() -> None:
    assert should_heal(0.34) is True
    assert should_heal(0.35) is False, "strictly below tau_h"
    assert should_heal(0.90) is False


def test_recovery_score_weights_trust_and_health() -> None:
    assert recovery_score(1.0, 1.0) == pytest.approx(1.0)
    assert recovery_score(0.0, 0.0) == pytest.approx(0.0)
    assert recovery_score(0.5, 1.0, eta=0.6) == pytest.approx(0.7)


def test_a_repaired_but_untrusted_device_scores_between() -> None:
    """The interesting disagreement: health back, trust not yet earned."""
    assert 0.3 < recovery_score(gt=0.2, health=0.95) < 0.6


def test_convergence_approaches_without_overshooting() -> None:
    ts = 0.05
    for _ in range(40):
        ts = converge(ts, 0.70, rate=0.25)
        assert ts <= 0.70 + 1e-9, "must never exceed the target"
    assert ts == pytest.approx(0.70, abs=0.01)


def test_convergence_can_move_downward() -> None:
    """A node above the target is brought to it, not left more trusted."""
    assert converge(0.95, 0.70, rate=0.25) < 0.95


def test_healing_never_reaches_full_trust() -> None:
    """The snap-back the design rejects."""
    ts = 0.05
    for _ in range(200):
        ts = converge(ts, HealingParams().target_ts, rate=0.25)
    assert ts < 1.0
    assert ts == pytest.approx(HealingParams().target_ts, abs=1e-6)


@given(
    start=st.floats(min_value=0.0, max_value=1.0),
    target=st.floats(min_value=0.0, max_value=1.0),
    rate=st.floats(min_value=0.01, max_value=1.0),
)
def test_property_convergence_never_leaves_the_interval(
    start: float, target: float, rate: float
) -> None:
    nxt = converge(start, target, rate=rate)
    assert 0.0 <= nxt <= 1.0
    lo, hi = sorted((start, target))
    assert lo - 1e-9 <= nxt <= hi + 1e-9, "a step never moves past the target"


def test_params_validate() -> None:
    for kwargs in (
        {"tau_h": 0.0},
        {"eta": 1.5},
        {"converge_rate": 0.0},
        {"reintegrate_ticks": 0},
        {"max_auto_attempts": -1},
    ):
        with pytest.raises(ValueError):
            HealingParams(**kwargs)


def test_a_healthy_device_is_never_healed() -> None:
    eng = _engine()
    assert _drive(eng, "n-1", [dict(gt=0.9, health=0.95)] * 5) == []
    assert eng.state("n-1").phase is Phase.IDLE


def test_the_full_path_runs_revoke_recalibrate_reintegrate_healed() -> None:
    eng = _engine()
    phases = _drive(eng, "n-1", [SICK, SICK, SICK, REPAIRED, REPAIRED, REPAIRED])
    assert phases[:4] == ["revoke", "recalibrate", "reintegrate", "healed"]
    assert eng.state("n-1").attempts == 1


def test_the_target_only_exists_while_healing() -> None:
    """M7 publishes a target; it never assigns a trust score."""
    eng = _engine()
    assert eng.target_for("n-1") is None

    eng.observe("n-1", sim_time=0.0, **SICK)
    eng.observe("n-1", sim_time=1.0, **SICK)
    assert eng.target_for("n-1") == pytest.approx(0.70)

    for t in range(2, 8):
        eng.observe("n-1", sim_time=float(t), **REPAIRED)
    assert eng.state("n-1").phase in (Phase.HEALED, Phase.IDLE)
    assert eng.target_for("n-1") is None, "the target is withdrawn once healing ends"


def test_next_ts_is_a_suggestion_the_caller_applies() -> None:
    """The owner of TS keeps owning it: M7 returns a value, never writes one."""
    eng = _engine()
    eng.observe("n-1", sim_time=0.0, **SICK)
    eng.observe("n-1", sim_time=1.0, **SICK)

    trust = TrustState.initial(TrustParams(), sim_time=0.0)
    trust.ts = 0.05
    stepped = eng.next_ts("n-1", trust.ts)
    assert stepped > trust.ts
    assert trust.ts == 0.05, "M7 did not touch it"


def test_next_ts_is_a_no_op_for_a_node_that_is_not_healing() -> None:
    assert _engine().next_ts("n-1", 0.42) == 0.42


def test_a_relapse_during_reintegration_rolls_back_immediately() -> None:
    eng = _engine()
    _drive(eng, "n-1", [SICK, SICK, SICK])
    assert eng.state("n-1").phase is Phase.REINTEGRATE

    ev = eng.observe("n-1", sim_time=9.0, gt=0.05, health=0.10)
    assert ev.phase == "rollback"
    assert ev.success is False
    assert eng.target_for("n-1") is None, "TS must stop converging upward at once"


def test_reintegration_that_never_recovers_times_out() -> None:
    """A device that is not actually getting better does not heal by waiting."""
    eng = _engine(reintegrate_ticks=4)
    phases = _drive(eng, "n-1", [SICK] * 12)
    assert "rollback" in phases
    assert "healed" not in phases


def test_rollback_settles_back_to_idle_once_trust_recovers() -> None:
    eng = _engine()
    _drive(eng, "n-1", [SICK, SICK, SICK])
    eng.observe("n-1", sim_time=9.0, gt=0.05, health=0.10)
    ev = eng.observe("n-1", sim_time=10.0, gt=0.90, health=0.95)
    assert ev.phase == "idle"


def test_repeated_healing_stops_being_automatic() -> None:
    """An attacker driving a device through the recovery path runs out of budget."""
    eng = _engine(max_auto_attempts=2, reintegrate_ticks=2)
    for _ in range(3):
        _drive(eng, "n-1", [SICK] * 6)

    assert eng.state("n-1").attempts >= 2
    assert eng.state("n-1").phase is Phase.NEEDS_APPROVAL
    assert eng.target_for("n-1") is None, "no target while waiting on a person"


def test_a_parked_node_stays_parked_until_a_human_approves() -> None:
    eng = _engine(max_auto_attempts=0)
    ev = eng.observe("n-1", sim_time=0.0, **SICK)
    assert ev.phase == "needs_approval"

    for t in range(1, 20):
        assert eng.observe("n-1", sim_time=float(t), **SICK) is None
    assert eng.state("n-1").phase is Phase.NEEDS_APPROVAL

    released = eng.observe("n-1", sim_time=20.0, approval_granted=True, **SICK)
    assert released.phase == "revoke"


def test_healing_cannot_be_used_to_restore_trust_faster_than_evidence() -> None:
    """The upward attack: gaming a compromised device through recovery."""
    eng = _engine()
    _drive(eng, "n-1", [SICK, SICK, SICK])
    ts = 0.05
    for _ in range(eng.params.reintegrate_ticks):
        ts = eng.next_ts("n-1", ts)
    assert ts < eng.params.target_ts < 1.0


def test_an_event_is_emitted_only_on_a_phase_change() -> None:
    eng = _engine()
    assert eng.observe("n-1", sim_time=0.0, **SICK).phase == "revoke"
    assert eng.observe("n-1", sim_time=1.0, **SICK).phase == "recalibrate"
    assert eng.observe("n-1", sim_time=2.0, **SICK).phase == "reintegrate"
    assert eng.observe("n-1", sim_time=3.0, **SICK) is None, "still reintegrating"


def test_events_carry_run_identity() -> None:
    eng = SelfHealingEngine(run_id="run-7", seed=42, config_hash="abc")
    ev = eng.observe("n-1", sim_time=5.0, **SICK)
    assert (ev.run_id, ev.seed, ev.config_hash, ev.sim_time) == ("run-7", 42, "abc", 5.0)


def test_healing_is_per_node() -> None:
    eng = _engine()
    eng.observe("sick", sim_time=0.0, **SICK)
    eng.observe("well", sim_time=0.0, gt=0.95, health=0.95)
    assert eng.state("sick").phase is Phase.REVOKE
    assert eng.state("well").phase is Phase.IDLE


def test_the_same_observations_always_produce_the_same_events() -> None:
    steps = [SICK, SICK, SICK, REPAIRED, dict(gt=0.10, health=0.10), REPAIRED]
    assert _drive(_engine(), "n-1", steps) == _drive(_engine(), "n-1", steps)


def test_default_state_is_idle_with_no_history() -> None:
    assert _engine().state("never-seen") == NodeHealingState()


def test_convergence_diagnostic_reports_full_arrival_time() -> None:
    """Reintegration succeeds on RS long before TS finishes converging."""
    assert ticks_to_reach(0.05, 0.70, rate=0.25) > HealingParams().reintegrate_ticks
