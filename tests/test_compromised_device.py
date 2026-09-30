"""A compromised device, and observers it does not control."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from agents.orchestrator import TickBatch
from agents.pipeline import ClosedLoopPipeline
from m1_monitoring.sensors.observers import IndependentObserver
from m8_eval_harness.baselines import by_id
from m8_eval_harness.evaluation import evaluate
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios import by_id as scenario
from m10_persona_drift.nhi import issue_signing_identity
from shared.schemas import Provenance
from tests.test_redis_bus import _update

EVERYONE = ("network", "identity", "device")


def _run(sid: str = "s1", **kw):
    result = run_scenario(scenario(sid), by_id("full"), attested_telemetry=True, **kw)
    return result, evaluate(result)


def _decisions(result) -> list:
    return [
        (o.sim_time, [(p.node_id, p.proposed_level) for p in o.plans], [u.gt for u in o.gt_updates])
        for o in result.pipeline.outcomes
    ]


def test_a_compromised_device_signs_its_own_lie_and_nothing_downstream_can_tell() -> None:
    result, ev = _run(compromised_device="all")
    assert ev["device_tpr"] == 0.0
    assert result.pipeline.reports_unattested_in_core == 0, (
        "every forged report carried a valid signature"
    )


def test_a_gateway_catches_a_device_lying_about_its_own_traffic() -> None:
    result, ev = _run(compromised_device="all", observers=("network",))
    assert ev["device_tpr"] == 1.0 and ev["false_restriction_rate"] == 0.0
    assert result.pipeline.observed_contradictions > 0


def test_honest_devices_under_every_observer_decide_exactly_as_without() -> None:
    plain, _ = _run("s3")
    observed, _ = _run("s3", observers=EVERYONE)
    assert _decisions(observed) == _decisions(plain)
    assert observed.pipeline.observed_contradictions == observed.pipeline.observed_unverified == 0


@pytest.mark.parametrize("sid", ["s2", "s3"])
def test_identity_provider_and_tpm_expose_a_device_that_leaves_only_its_traffic_true(sid) -> None:
    _, gateway_only = _run(sid, compromised_device="unobservable", observers=("network",))
    assert gateway_only["device_tpr"] == 0.0
    result, ev = _run(sid, compromised_device="unobservable", observers=EVERYONE)
    assert ev["device_tpr"] == 1.0 and result.pipeline.observed_contradictions == 0


def test_a_device_whose_attack_shows_in_behaviour_is_the_stated_limit() -> None:
    """s1 moves behaviour and network."""
    result, ev = _run("s1", compromised_device="unobservable", observers=EVERYONE)
    assert ev["device_tpr"] == 0.0 and result.pipeline.observed_contradictions == 0


def test_behaviour_has_no_observer() -> None:
    with pytest.raises(ValueError):
        IndependentObserver("behavioral", issue_signing_identity("x", seed=b"x" * 32))


class _Outside:
    """What someone outside the device sees: its traffic and its logins are bad."""

    def read(self, sim_time, node_id):
        return SimpleNamespace(network=0.2, identity=0.3), Provenance.HIGH


def _core(signer: str = "observer"):
    observers = tuple(
        IndependentObserver(
            d, issue_signing_identity(d, seed=d[0].encode() * 32), source=_Outside()
        )
        for d in ("network", "identity")
    )
    keys = {
        o.dimension: issue_signing_identity(
            o.dimension, seed=(o.dimension[0] if signer == "observer" else "z").encode() * 32
        ).public()
        for o in observers
    }
    return SimpleNamespace(
        observers=observers,
        observer_keys=keys,
        observer_tolerance=0.15,
        observed_contradictions=0,
        observed_unverified=0,
    )


def test_the_core_fuses_each_observers_reading_and_flags_the_contradiction() -> None:
    core = _core()
    batch = TickBatch(sim_time=3.0, run_id="r", seed=1, config_hash="h", updates=[_update(0.9)])
    observed, contradicted = ClosedLoopPipeline._observed(core, batch)  # type: ignore[arg-type]
    context = observed.updates[0].context
    assert (context.network, context.identity, context.behavioral) == (0.2, 0.3, 0.9)
    assert contradicted == {"node-0"}


def test_an_observer_reading_that_fails_its_signature_is_no_evidence() -> None:
    core = _core(signer="someone-else")
    batch = TickBatch(sim_time=3.0, run_id="r", seed=1, config_hash="h", updates=[_update(0.9)])
    observed, contradicted = ClosedLoopPipeline._observed(core, batch)  # type: ignore[arg-type]
    assert observed is batch and not contradicted and core.observed_unverified == 2
