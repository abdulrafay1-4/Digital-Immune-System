"""Hand-computed EWMA / decay checks for M1 core."""

from __future__ import annotations

import math

from m1_monitoring.core.context_vector import make_context
from m1_monitoring.core.observation import observation_from_context
from m1_monitoring.core.trust import TrustParams, TrustState, apply_time_decay, ewma_update
from m8_eval_harness.simulator import run_trust_sim


def test_ewma_hand_computed() -> None:
    assert ewma_update(1.0, 0.0, 0.7, ts_min=0.05) == 0.7
    assert abs(ewma_update(0.7, 0.0, 0.7, ts_min=0.05) - 0.49) < 1e-12


def test_ts_floor() -> None:
    assert ewma_update(0.05, 0.0, 0.0, ts_min=0.05) == 0.05
    assert apply_time_decay(0.05, dt=1000.0, beta=0.01, ts_min=0.05) == 0.05


def test_time_decay_hand_computed() -> None:
    expected = 1.0 * math.exp(-0.1)
    got = apply_time_decay(1.0, dt=10.0, beta=0.01, ts_min=0.05)
    assert abs(got - expected) < 1e-12


def test_trust_state_step_sequence() -> None:
    params = TrustParams(lam=0.7, beta=0.0, ts_min=0.05, ts_init=1.0)
    st = TrustState.initial(params, sim_time=0.0)
    assert st.step(0.0, sim_time=1.0) == 0.7
    assert abs(st.step(0.0, sim_time=2.0) - 0.49) < 1e-12


def test_observation_equal_weights() -> None:
    ctx = make_context(1.0, 0.0, 1.0, 0.0)
    assert observation_from_context(ctx) == 0.5


def test_anomaly_drops_only_target_node() -> None:
    _, series, raw = run_trust_sim(
        seed=7,
        n_nodes=10,
        ticks=40,
        run_id="trust-unit",
        anomaly_node="node-0",
        anomaly_window=(5.0, 40.0, 0.75),
        results_dir=None,
    )
    assert len(raw) > 0
    victim_final = series["node-0"][-1]
    victim_min = min(series["node-0"])
    others_final = [series[f"node-{i}"][-1] for i in range(1, 10)]
    assert victim_min < 0.7
    assert victim_final < min(others_final)
    assert all(ts > 0.7 for ts in others_final)


import pytest  # noqa: E402
from hypothesis import given  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

_unit = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
_floor = st.floats(min_value=0.0, max_value=0.5, allow_nan=False)


@given(ts=_unit, obs=_unit, lam=_unit, ts_min=_floor, lam_up=st.none() | _unit)
def test_ewma_stays_in_the_band_for_every_finite_input(ts, obs, lam, ts_min, lam_up) -> None:
    out = ewma_update(ts, obs, lam, ts_min=ts_min, lam_up=lam_up)
    assert ts_min <= out <= 1.0


@given(
    ts=_unit,
    dt=st.floats(min_value=0.0, max_value=1e6, allow_nan=False),
    beta=st.floats(min_value=0.0, max_value=10.0, allow_nan=False),
    ts_min=_floor,
)
def test_decay_never_raises_trust_and_never_crosses_the_floor(ts, dt, beta, ts_min) -> None:
    out = apply_time_decay(ts, dt, beta, ts_min)
    assert ts_min <= out <= max(ts, ts_min)


@pytest.mark.parametrize(
    "call",
    [
        lambda: ewma_update(0.2, math.nan, 0.7, ts_min=0.05),
        lambda: ewma_update(math.nan, 0.5, 0.7, ts_min=0.05),
        lambda: ewma_update(0.2, math.inf, 0.7, ts_min=0.05),
        lambda: apply_time_decay(0.5, math.nan, 0.01, 0.05),
        lambda: apply_time_decay(0.5, 1.0, math.nan, 0.05),
    ],
)
def test_non_finite_input_raises_rather_than_granting_full_trust(call) -> None:
    """`min(1.0, nan)` is 1.0, so a NaN must not come out as *full* trust."""
    with pytest.raises(ValueError):
        call()


def test_trust_rises_slower_than_it_falls_with_lambda_up() -> None:
    """The asymmetric branch: lam_up applies only while the observation is above TS."""
    rising = ewma_update(0.5, 1.0, 0.7, ts_min=0.05, lam_up=0.9)
    assert rising == pytest.approx(0.9 * 0.5 + 0.1 * 1.0)
    falling = ewma_update(0.5, 0.0, 0.7, ts_min=0.05, lam_up=0.9)
    assert falling == pytest.approx(0.7 * 0.5)
