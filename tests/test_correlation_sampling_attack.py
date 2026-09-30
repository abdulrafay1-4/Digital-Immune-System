"""Regression tests: a correlation agent that knows when it is checked."""

from __future__ import annotations

from dataclasses import dataclass

from m8_eval_harness.baselines import FULL
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios.adversaries import LyingCorrelation
from m8_eval_harness.scenarios.base import Anomaly, Scenario

DEGRADED = [f"node-{i}" for i in range(15)]


@dataclass
class ScheduleAwareLiar(LyingCorrelation):
    """
    Lies only on ticks the verifier's sampling will not recompute, and inflates each device's own
    threat indicator, which nothing compared.
    """

    name: str = "schedule-aware-liar"

    def before_tick(self, run: object, sim_time: float) -> None:
        if self.installed:
            return
        correlator = run.pipeline.correlator  # type: ignore[attr-defined]
        honest = correlator.correlate
        outer = self

        def lying(batch, **kwargs):  # type: ignore[no-untyped-def]
            result = honest(batch, **kwargs)
            if batch.sim_time < outer.start_sim or (int(batch.sim_time) + 1) % 5 == 0:
                return result
            outer.lies += 1
            return result.model_copy(
                update={
                    "implicated_node_ids": sorted(result.node_ids),
                    "cti": 0.9,
                    "campaign_corroboration": 0.30,
                    "node_ti": {n: 1.0 for n in result.node_ids},
                }
            )

        correlator.correlate = lying
        self.installed = True


def _scenario(severity: float, adversary: object | None = None) -> Scenario:
    return Scenario(
        scenario_id="t-liar",
        name="schedule-aware liar",
        demonstrates="",
        n_nodes=60,
        ticks=60,
        anomalies=tuple(Anomaly(n, 5.0, 55.0, severity) for n in DEGRADED),
        seed=7711,
        adversary=adversary,
    )


def _levels(result) -> list[tuple[float, str, int]]:
    return [
        (o.sim_time, p.node_id, int(ex.level) if ex.executed and ex.level is not None else 0)
        for o in result.pipeline.outcomes
        for p, ex in zip(o.plans, o.executions, strict=True)
    ]


def test_a_liar_that_knows_the_schedule_raises_no_device_above_the_honest_level() -> None:
    """A liar that lies only on unsampled ticks raises no device above the honest level."""
    for severity in (0.08, 0.12):
        honest = run_scenario(_scenario(severity), FULL)
        lied = run_scenario(_scenario(severity, ScheduleAwareLiar(start_sim=10.0)), FULL)
        assert lied.adversary.lies > 0
        assert _levels(lied) == _levels(honest)
        assert lied.pipeline.correlation_overstated > 0


def test_bounding_leaves_an_honest_correlation_untouched() -> None:
    result = run_scenario(_scenario(0.3), FULL)
    assert result.pipeline.correlation_overstated == 0
