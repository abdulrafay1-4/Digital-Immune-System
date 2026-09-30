"""Regression tests: who may speak for a device."""

from __future__ import annotations

from dataclasses import dataclass

from agents.orchestrator import TRUST_TOPIC
from m8_eval_harness.baselines import FULL
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios.base import Anomaly, Scenario
from shared.schemas import ContextVector, Provenance, TrustUpdate


@dataclass
class _Impersonator:
    """Not a compromised agent: something else that can reach the broker."""

    name: str = "impersonator"
    victim: str = "node-7"
    start_sim: float = 5.0
    published: int = 0

    def before_tick(self, run: object, sim_time: float) -> None:
        if sim_time < self.start_sim:
            return
        run.bus.publish(  # type: ignore[attr-defined]
            TRUST_TOPIC,
            TrustUpdate(
                sim_time=sim_time,
                run_id=run.run_id,  # type: ignore[attr-defined]
                seed=run.seed,  # type: ignore[attr-defined]
                config_hash=run.config_hash,  # type: ignore[attr-defined]
                node_id=self.victim,
                node_trust=0.02,
                observation=0.02,
                context=ContextVector(identity=0.02, behavioral=0.02, device=0.02, network=0.02),
                provenance=Provenance.HIGH,
                agent_id=f"mon-{self.victim}",
            ),
        )
        self.published += 1

    def after_tick(self, run: object, sim_time: float, outcome: object) -> None:
        return None


def _scenario(adversary: object | None = None, binding: str = "provisioned") -> Scenario:
    return Scenario(
        scenario_id="t-impersonation",
        name="speaking for a device you do not monitor",
        demonstrates="",
        n_nodes=20,
        ticks=40,
        anomalies=(Anomaly("node-1", 5.0, 35.0, 0.7),),
        ground_truth={"node-1": 5.0},
        adversary=adversary,
        seed=7910,
    )


def test_impersonating_a_monitor_no_longer_frames_its_device() -> None:
    """Forged reports under a victim's monitor id are refused, and the device is left alone."""
    result = run_scenario(_scenario(_Impersonator()), FULL)

    assert result.adversary.published > 0
    assert result.telemetry_rejected >= result.adversary.published
    assert result.worst_level("node-7") == 0, "the victim was never acted on"
    assert result.false_positives == frozenset()
    assert result.worst_level("node-1") >= 3, "and the real attack is still caught"


def test_a_signed_fleet_still_detects_and_refuses_nothing_honest() -> None:
    result = run_scenario(_scenario(), FULL)
    assert result.telemetry_rejected == 0, "every honest report is attributable"
    assert result.worst_level("node-1") >= 3
    assert result.orchestrator.updates_seen == 20 * 40


def test_trust_on_first_use_is_the_posture_that_still_admits_a_stranger() -> None:
    """The weak enrolment posture, kept so the registration suite can price it."""
    result = run_scenario(_scenario(_Impersonator()), FULL, binding="tofu")
    assert result.telemetry_rejected > 0
    assert result.worst_level("node-7") > 0, "and the victim pays for it"
