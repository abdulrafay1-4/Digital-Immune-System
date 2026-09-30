"""The trusted components, compromised one at a time."""

from __future__ import annotations

import pytest

from m8_eval_harness.baselines import by_id
from m8_eval_harness.evaluation import evaluate
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios import by_id as scenario


def _run(arm: str, sid: str = "s1", **kw):
    result = run_scenario(scenario(sid), by_id(arm), **kw)
    return result, evaluate(result)


def test_honest_fusion_is_never_recomputed() -> None:
    result, _ = _run("full", "s3")
    assert result.pipeline.engine.gt_inconsistent == 0


def test_a_fusion_signing_gt_its_inputs_do_not_produce_hides_nothing() -> None:
    result, ev = _run("core_fusion_suppress_naive")
    assert ev["device_tpr"] == 1.0
    assert result.pipeline.engine.gt_inconsistent > 0
    _, unchecked = _run("core_fusion_suppress_naive_unchecked")
    assert unchecked["device_tpr"] == 0.0, "without the check the same lie hides the attack"


def test_a_fusion_framing_with_an_inconsistent_gt_restricts_no_one() -> None:
    _, ev = _run("core_fusion_frame_naive")
    assert ev["false_restriction_rate"] == 0.0


def test_a_fusion_that_forges_its_inputs_too_is_the_stated_limit() -> None:
    """
    The engine alone cannot tell a consistent lie from the truth; replicated fusion
    (`m6_trust_fusion.replicated`) is the remedy.
    """
    result, ev = _run("core_fusion_suppress")
    assert ev["device_tpr"] == 0.0 and result.pipeline.engine.gt_inconsistent == 0


def test_an_orchestrator_replaying_old_reports_is_caught_when_devices_sign() -> None:
    _, hidden = _run("core_orchestrator_hide")
    assert hidden["device_tpr"] == 0.0, "without device signatures the replay hides it"
    result, caught = _run("core_orchestrator_hide", attested_telemetry=True)
    assert caught["device_tpr"] == 1.0
    assert result.pipeline.reports_unattested_in_core > 0


def test_an_orchestrator_forging_reports_frames_no_one_when_devices_sign() -> None:
    _, framed = _run("core_orchestrator_frame")
    assert framed["false_restriction_rate"] > 0.0
    result, ev = _run("core_orchestrator_frame", attested_telemetry=True)
    assert ev["false_restriction_rate"] == 0.0
    assert result.pipeline.reports_unattested_in_core > 0


def test_the_core_keeps_every_honest_attested_report() -> None:
    result, ev = _run("full", "s3", attested_telemetry=True)
    assert result.pipeline.reports_unattested_in_core == 0
    assert ev["device_tpr"] == 1.0


@pytest.mark.parametrize("sid", ["r5", "s2"])
def test_a_rogue_operator_cannot_isolate_a_device_the_engine_did_not_escalate(sid) -> None:
    """
    Approving everything isolates only what reached L4: under congestion and in a campaign, no
    healthy device does.
    """
    _, ev = _run("full", sid, operator="approve", adjudication="auto_confirm")
    assert ev["false_isolation_rate"] == 0.0
