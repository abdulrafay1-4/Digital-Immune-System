"""Regression tests that pin wiring, not only helpers."""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from agents.orchestrator import TRUST_TOPIC, Orchestrator
from shared.bus import InProcBus
from shared.schemas import ContextVector, Provenance, TrustUpdate


def _u(node_id: str = "n-0", *, run_id: str = "r", sim_time: float = 1.0, level: float = 0.9):
    return TrustUpdate(
        sim_time=sim_time,
        run_id=run_id,
        seed=1,
        config_hash="h",
        node_id=node_id,
        node_trust=level,
        observation=level,
        provenance=Provenance.HIGH,
        context=ContextVector(identity=level, behavioral=level, device=level, network=level),
        agent_id=f"mon-{node_id}",
    )


def test_a_report_from_another_run_is_refused_and_counted() -> None:
    """A report stamped with another run's identity must not enter this one."""

    class Sink:
        def __init__(self) -> None:
            self.batches: list = []

        def run(self, batch):
            self.batches.append(batch)

    bus, sink = InProcBus(), Sink()
    orch = Orchestrator(bus=bus, run_id="r", seed=1, config_hash="h", pipeline=sink)
    orch.attach()
    bus.publish(TRUST_TOPIC, _u(run_id="another-run"))
    bus.publish(TRUST_TOPIC, _u("n-1"))
    orch.flush()
    assert orch.foreign_updates == 1
    delivered = [u.node_id for b in sink.batches for u in b.updates]
    assert delivered == ["n-1"]


@pytest.mark.parametrize("bad_time", [math.nan, math.inf, -1.0])
def test_a_report_with_a_non_finite_or_negative_time_is_refused(bad_time: float) -> None:
    with pytest.raises(ValidationError):
        _u(sim_time=bad_time)


@pytest.mark.parametrize(
    "bad_id", ["", " n-0", "n 0", "n-0\n", "../etc", "x" * 129, "n-0;DROP", "-leading"]
)
def test_an_identifier_outside_the_alphabet_or_too_long_is_refused(bad_id: str) -> None:
    with pytest.raises(ValidationError):
        _u(node_id=bad_id)


def test_a_non_finite_context_dimension_is_refused() -> None:
    with pytest.raises(ValidationError):
        ContextVector(identity=math.nan, behavioral=0.9, device=0.9, network=0.9)


def test_the_engine_refuses_a_replayed_token_from_its_own_gate() -> None:
    """A gate that hands the same token twice must not act twice."""
    from unittest.mock import patch

    import m4_response_engine.engine as engine_module
    from tests.test_m9_gate import _armed, _Passes, _plan

    eng, level = _armed(0.30)
    plan = _plan(level)
    real_gate = engine_module.gate_response_plan
    first = {}

    def repeating_gate(p, **kw):
        if "decision" not in first:
            first["decision"] = real_gate(p, **kw)
        return first["decision"]

    with patch.object(engine_module, "gate_response_plan", repeating_gate):
        once = eng.execute(plan, verification=_Passes(), input_provenance=Provenance.HIGH)
        again = eng.execute(plan, verification=_Passes(), input_provenance=Provenance.HIGH)
    assert once.executed is True
    assert again.executed is False
    assert again.audit.payload["deny_reason"] == "token_replayed"


def test_no_component_but_an_attester_can_sign_as_it() -> None:
    """The gate and the read path hold public keys, which verify and cannot sign."""
    from m8_eval_harness.baselines import FULL

    pipe = FULL.pipeline(bus=InProcBus(), run_id="r", seed=1, config_hash="h")
    gate_keys = pipe.curator.gate.registry
    assert set(gate_keys) == set(pipe.attesters)
    for name, verifying in gate_keys.items():
        with pytest.raises(PermissionError):
            verifying.sign(b"forged attestation")
        signature = pipe.attesters[name].identity.sign(b"payload")
        assert verifying.verify(b"payload", signature)


def test_a_curator_cannot_collect_signatures_for_what_the_batches_never_showed() -> None:
    """A compromised curator proposes a record; independent attesters refuse it."""
    from m5_immune_memory.write_path import IncidentSummary
    from m8_eval_harness.baselines import FULL
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios import by_id

    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(by_id("s3"), FULL, seed=20000, results_dir=Path(tmp))
    pipe = result.pipeline
    honest_records = len(pipe.curator.store)
    assert honest_records > 0, "honest incidents are still admitted"

    forged = pipe.curator.propose_and_submit(
        IncidentSummary(
            record_id="forged-1",
            node_ids=("node-0",),
            peak_level=4,
            threat_type="benign",
            pattern_text="identity:none behavioral:none device:none network:heavy"
            " breadth wide severity high",
            window_start_sim=60.0,
            window_end_sim=70.0,
            run_id=result.orchestrator.run_id,
            seed=result.seed,
            config_hash=result.orchestrator.config_hash,
        ),
        pipe.attesters,
        now_sim=70.0,
    )
    assert forged.admitted is False and forged.reason == "attesters_disagree"
    assert len(pipe.curator.store) == honest_records
    assert all(a.refused >= 1 for a in pipe.attesters.values())


def test_a_patient_liar_walks_a_restricted_device_back_to_l0_under_attack() -> None:
    """The patient liar: the step check bounds the rate of a forged rise, not its destination."""
    from m8_eval_harness.baselines import FULL
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios.base import Anomaly, Scenario

    scenario = Scenario(
        scenario_id="patient-liar-walkback",
        name="patient liar, late",
        demonstrates="walk back",
        n_nodes=30,
        ticks=45,
        seed=7900,
        anomalies=(Anomaly("node-0", 10, 44, 0.7),),
        ground_truth={"node-0": 10},
        forged_context={"node-0": 20.0},
    )
    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(scenario, FULL, seed=7900, results_dir=Path(tmp))
    levels = {
        int(o.sim_time): p.proposed_level
        for o in result.pipeline.outcomes
        for p in o.plans
        if p.node_id == "node-0"
    }
    assert max(v for t, v in levels.items() if t < 20) >= 2, "caught while honest"
    assert levels[max(levels)] == 0, "and walked back to L0, still under attack"
    assert evaluate(result)["trust_rise_capped"] == 0


@pytest.mark.parametrize(
    "requested",
    ["binary_zt+brake", "binary_zt@0.6+brake", "binary_zt@0.8", "isolation_forest@0.002"],
)
def test_a_baseline_id_round_trips(requested: str) -> None:
    from m8_eval_harness.baselines import by_id

    assert by_id(requested).baseline_id == requested


@pytest.mark.parametrize(
    "requested", ["binary_zt+brake@0.6", "isolation_forest@0.05+brake", "binary_zt+brakeX"]
)
def test_a_baseline_id_that_cannot_be_built_exactly_is_refused(requested: str) -> None:
    """An arm label parses exactly, or not at all, so `+brake` always means the brake."""
    from m8_eval_harness.baselines import by_id

    with pytest.raises(KeyError):
        by_id(requested)


def test_the_braked_baseline_really_carries_the_brake() -> None:
    from m8_eval_harness.baselines import by_id

    kw = dict(bus=InProcBus(), run_id="r", seed=1, config_hash="h")
    assert by_id("binary_zt+brake").pipeline(**kw).max_auto_restrict_fraction == 0.10
    assert by_id("binary_zt").pipeline(**kw).max_auto_restrict_fraction is None


def test_the_manifest_is_taken_before_any_cell_runs(monkeypatch) -> None:
    """The manifest is taken before the runs, not after commits made during them."""
    import m8_eval_harness.experiment as experiment

    order: list[str] = []
    monkeypatch.setattr(experiment, "manifest", lambda *a, **k: order.append("manifest") or {})
    monkeypatch.setattr(experiment, "run_cells", lambda *a, **k: order.append("run") or [])
    monkeypatch.setattr(experiment, "write_outputs", lambda *a, **k: None)
    experiment.main(["--suite", "fairness", "--seeds", "1", "--workers", "1", "--out", "/tmp/x"])
    assert order == ["manifest", "run"]


def test_reanalysis_rebuilds_the_comparisons_and_keeps_the_provenance(tmp_path) -> None:
    import csv
    import json

    import m8_eval_harness.experiment as experiment

    rows = [
        {
            "scenario_id": "s1",
            "variant": "v",
            "baseline_id": arm,
            "seed": seed,
            "device_tpr": 1.0 if arm == "full" else 0.5 + 0.01 * seed,
        }
        for arm in ("full", "other")
        for seed in range(10)
    ]
    (tmp_path / "rows.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    (tmp_path / "manifest.json").write_text(
        json.dumps({"suite": "fairness", "git_commit": "abc123"})
    )
    experiment.main(["--suite", "fairness", "--reanalyse", "--out", str(tmp_path)])

    meta = json.loads((tmp_path / "manifest.json").read_text())
    assert meta["git_commit"] == "abc123" and meta["reanalysed"] is True
    written = list(csv.DictReader((tmp_path / "comparisons.csv").open()))
    expected = experiment.compare_rows(rows)
    assert [(r["metric"], float(r["p_adjusted"])) for r in written] == [
        (c.metric, pytest.approx(c.p_adjusted)) for c in expected
    ]


def test_a_suppressing_correlation_agent_hides_nothing() -> None:
    """A suppressing correlation agent changes no decision."""
    from m8_eval_harness.baselines import FULL
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios import by_id

    def decisions(scenario_id: str):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_scenario(by_id(scenario_id), FULL, seed=20000, results_dir=Path(tmp))
        levels = [
            (o.sim_time, p.node_id, p.proposed_level)
            for o in result.pipeline.outcomes
            for p in o.plans
            if p.node_id in {"node-0", "node-1", "node-2", "node-3"}
        ]
        return levels, result.pipeline

    honest, _ = decisions("s2")
    suppressed, pipe = decisions("a13")
    assert suppressed == honest, "the lie changes nothing that acts"
    assert pipe.correlation_understated > 0 and pipe.correlation_overstated == 0


def _liar(kind: str) -> object:
    from m8_eval_harness.scenarios.base import Anomaly, Scenario

    forgery = {"patient": "forged_context", "loud": "forged_observation"}.get(kind)
    return Scenario(
        scenario_id=f"att-{kind}",
        name=kind,
        demonstrates="attested telemetry",
        n_nodes=30,
        ticks=45,
        seed=7900,
        anomalies=(Anomaly("node-0", 10, 44, 0.7), Anomaly("node-1", 10, 44, 0.7)),
        ground_truth={"node-0": 10, "node-1": 10},
        **({forgery: {"node-0": 8.0}} if forgery else {}),
    )


def _run(kind: str, attested: bool):
    from m8_eval_harness.baselines import FULL
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario

    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(
            _liar(kind), FULL, seed=7900, results_dir=Path(tmp), attested_telemetry=attested
        )
    levels = [
        (o.sim_time, p.node_id, p.proposed_level) for o in result.pipeline.outcomes for p in o.plans
    ]
    return evaluate(result), levels


def test_attesting_devices_change_nothing_for_an_honest_fleet() -> None:
    plain, plain_levels = _run("honest", attested=False)
    attested, attested_levels = _run("honest", attested=True)
    assert attested["unattested_updates"] == 0, "no honest report refused"
    assert attested_levels == plain_levels


def test_a_patient_liar_cannot_forge_what_its_device_signs() -> None:
    """The patient liar, defeated for the compromised-monitor case."""
    open_metrics, open_levels = _run("patient", attested=False)
    closed_metrics, closed_levels = _run("patient", attested=True)
    worst = lambda levels: max(lv for _, n, lv in levels if n == "node-0")  # noqa: E731
    assert worst(open_levels) == 0, "the stated limitation"
    assert closed_metrics["unattested_updates"] > 0
    assert worst(closed_levels) >= 2, "caught once the monitor can no longer author evidence"
    assert closed_metrics["residual_compromise"] < open_metrics["residual_compromise"]


def test_a_device_signs_only_what_it_measured_and_a_replay_fails() -> None:
    """The monitor cannot obtain a signature over a context it made up, or reuse one."""
    from agents.orchestrator import Orchestrator
    from m1_monitoring.sensors.attested import AttestedTelemetry
    from m1_monitoring.sensors.synthetic import SyntheticTelemetry
    from m10_persona_drift.nhi import issue_signing_identity

    key = issue_signing_identity("n-0", seed=b"device")
    sensor = AttestedTelemetry(SyntheticTelemetry(1), {"n-0": key})
    measured, _ = sensor.read(1.0, "n-0")
    signature = sensor.attestation(1.0, "n-0")
    assert sensor.attestation(2.0, "n-0") is None, "no signature for a tick not measured"

    orch = Orchestrator(
        bus=InProcBus(), run_id="r", seed=1, config_hash="h", device_keys={"n-0": key.public()}
    )

    def report(sim_time: float, context, attestation):
        return TrustUpdate(
            sim_time=sim_time,
            run_id="r",
            seed=1,
            config_hash="h",
            node_id="n-0",
            node_trust=0.9,
            observation=0.9,
            context=context,
            provenance=Provenance.HIGH,
            agent_id="mon-n-0",
            attestation=attestation,
        )

    perfect = ContextVector(identity=1.0, behavioral=1.0, device=1.0, network=1.0)
    assert orch._attested(report(1.0, measured, signature)) is True
    assert orch._attested(report(1.0, perfect, signature)) is False, "forged context"
    assert orch._attested(report(5.0, measured, signature)) is False, "replayed at a new tick"
    assert orch._attested(report(1.0, measured, None)) is False, "no attestation at all"
