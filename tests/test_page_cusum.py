"""
Page's CUSUM on its own: the one-sided scheme, action at h, restart at zero, and nothing else of the
DIS (a silent device is not inspected).
"""

from m8_eval_harness.baselines.base import (
    _fusion,
    _healthy_observation_mean,
    _PageCusumFusion,
    by_id,
)
from m8_eval_harness.params import FROZEN
from shared.bus import InProcBus
from shared.schemas import ContextVector, Provenance, TrustUpdate


def _report(t: float, level: float) -> TrustUpdate:
    return TrustUpdate(
        sim_time=t,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id="n-0",
        node_trust=level,
        observation=level,
        context=ContextVector(identity=level, behavioral=level, device=level, network=level),
        provenance=Provenance.HIGH,
        agent_id="mon-n-0",
    )


def _chart() -> _PageCusumFusion:
    return _fusion(
        InProcBus(),
        "r",
        1,
        "h",
        FROZEN,
        cls=_PageCusumFusion,
        cusum_k=0.1,
        cusum_h=0.5,
        cusum_mu0=0.9,
    )


def test_action_at_h_then_the_chart_restarts_at_zero() -> None:
    chart = _chart()
    gts = [chart.observe_trust(_report(float(t), 0.6)).gt for t in range(6)]
    assert gts == [1.0, 1.0, 0.0, 1.0, 1.0, 0.0]


def test_a_healthy_device_is_never_acted_on_and_silence_is_not_inspected() -> None:
    chart = _chart()
    assert all(chart.observe_trust(_report(float(t), 0.85)).gt == 1.0 for t in range(50))
    assert chart.observe_silence("n-0", sim_time=50.0) is None


def test_the_in_control_mean_is_measured_and_the_arm_keeps_nothing_else() -> None:
    assert 0.85 < _healthy_observation_mean() < 0.95
    pipeline = by_id("page_cusum@0.15:6.4").pipeline(
        bus=InProcBus(), run_id="r", seed=1, config_hash="h"
    )
    assert pipeline.curator is None and pipeline.healer is None
