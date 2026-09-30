"""M8 metrics and the acceptance-check harness."""

from __future__ import annotations

from pathlib import Path

import pytest

from m8_eval_harness.metrics import (
    COLUMNS,
    DetectionParams,
    GroundTruth,
    MetricsTable,
    compute_metrics,
    evaluation_window,
    load_events,
    series_by_node,
)
from m8_eval_harness.runner import run_phase1_exit
from shared.schemas import ContextVector, Provenance, TrustUpdate

RESULTS = Path(__file__).resolve().parents[1] / "results" / "_test_metrics"


def make_event(node_id: str, sim_time: float, trust: float) -> TrustUpdate:
    """A TrustUpdate with everything but node_id/sim_time/trust held constant."""
    return TrustUpdate(
        sim_time=sim_time,
        run_id="test",
        seed=7,
        config_hash="deadbeefdeadbeef",
        node_id=node_id,
        node_trust=trust,
        observation=trust,
        context=ContextVector(identity=trust, behavioral=trust, device=trust, network=trust),
        provenance=Provenance.MEDIUM,
        agent_id=f"mon-{node_id}",
    )


def log_from(curves: dict[str, list[float]]) -> list[TrustUpdate]:
    """{node_id: [trust at t=0, t=1, ...]} -> a flat event log."""
    return [
        make_event(node_id, float(t), value)
        for node_id, values in curves.items()
        for t, value in enumerate(values)
    ]


def test_confusion_matrix_is_exact() -> None:
    events = log_from(
        {
            "victim": [0.9, 0.5, 0.4],
            "peer-1": [0.9, 0.9, 0.9],
            "peer-2": [0.9, 0.88, 0.9],
            "peer-3": [0.9, 0.55, 0.9],
        }
    )
    truth = GroundTruth(
        all_nodes=["victim", "peer-1", "peer-2", "peer-3"],
        anomalous={"victim": (1.0, 3.0)},
    )
    m = compute_metrics(events, truth, scenario="unit")

    assert (m.tp, m.fp, m.tn, m.fn) == (1, 1, 2, 0)
    assert m.accuracy == pytest.approx(3 / 4)
    assert m.precision == pytest.approx(1 / 2)
    assert m.recall == pytest.approx(1.0)
    assert m.fpr == pytest.approx(1 / 3)


def test_missed_anomaly_is_a_false_negative() -> None:
    events = log_from({"victim": [0.9, 0.85, 0.8], "peer": [0.9, 0.9, 0.9]})
    truth = GroundTruth(all_nodes=["victim", "peer"], anomalous={"victim": (1.0, 3.0)})
    m = compute_metrics(events, truth, scenario="unit")

    assert (m.tp, m.fn) == (0, 1)
    assert m.recall == pytest.approx(0.0)
    assert m.detection_latency is None


def test_silent_node_counts_as_missed_not_healthy() -> None:
    """A node that never reports is not evidence of health."""
    events = log_from({"peer": [0.9, 0.9]})
    truth = GroundTruth(all_nodes=["victim", "peer"], anomalous={"victim": (0.0, 2.0)})
    m = compute_metrics(events, truth, scenario="unit")

    assert m.fn == 1
    assert m.tn == 1


def test_detection_latency_is_measured_from_anomaly_start() -> None:
    events = log_from({"victim": [0.95, 0.94, 0.9, 0.7, 0.55, 0.4]})
    truth = GroundTruth(all_nodes=["victim"], anomalous={"victim": (2.0, 6.0)})
    m = compute_metrics(events, truth, scenario="unit")

    assert m.detection_latency == pytest.approx(2.0)


def test_recovery_time_is_measured_from_anomaly_end() -> None:
    events = log_from({"victim": [0.9, 0.3, 0.3, 0.5, 0.7, 0.88, 0.9]})
    truth = GroundTruth(all_nodes=["victim"], anomalous={"victim": (1.0, 3.0)})
    m = compute_metrics(events, truth, scenario="unit")

    assert m.recovery_time == pytest.approx(2.0)


def test_recovery_is_none_when_run_ends_mid_climb() -> None:
    """Never report a recovery the log does not actually contain."""
    events = log_from({"victim": [0.9, 0.3, 0.3, 0.5, 0.7]})
    truth = GroundTruth(all_nodes=["victim"], anomalous={"victim": (1.0, 3.0)})
    m = compute_metrics(events, truth, scenario="unit")

    assert m.recovery_time is None


def test_separation_uses_anomaly_window_not_end_of_run() -> None:
    """Regression: a victim that dips hard and fully recovers must still show strong separation."""
    events = log_from(
        {
            "victim": [0.9, 0.3, 0.3, 0.3, 0.9, 0.9],
            "peer": [0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
        }
    )
    truth = GroundTruth(all_nodes=["victim", "peer"], anomalous={"victim": (1.0, 4.0)})
    m = compute_metrics(events, truth, scenario="unit")

    assert m.mean_trust_anomalous == pytest.approx(0.3)
    assert m.mean_trust_healthy == pytest.approx(0.9)
    assert m.trust_separation == pytest.approx(0.6)
    assert m.min_trust_anomalous == pytest.approx(0.3)

    final = {n: s[-1][1] for n, s in series_by_node(events).items()}
    assert final["victim"] == pytest.approx(final["peer"])


def test_evaluation_window_spans_all_anomalies() -> None:
    events = log_from({"a": [0.9] * 10, "b": [0.9] * 10})
    truth = GroundTruth(all_nodes=["a", "b"], anomalous={"a": (2.0, 5.0), "b": (4.0, 9.0)})
    assert evaluation_window(truth, events) == (2.0, 9.0)


def test_evaluation_window_falls_back_to_whole_run() -> None:
    events = log_from({"a": [0.9, 0.9, 0.9]})
    truth = GroundTruth(all_nodes=["a"])
    start, end = evaluation_window(truth, events)
    assert start == 0.0
    assert end > 2.0


def test_metrics_are_deterministic_for_a_given_log() -> None:
    events = log_from({"victim": [0.9, 0.4, 0.4], "peer": [0.9, 0.9, 0.9]})
    truth = GroundTruth(all_nodes=["victim", "peer"], anomalous={"victim": (1.0, 3.0)})

    a = compute_metrics(events, truth, scenario="unit", wall_seconds=0.1)
    b = compute_metrics(events, truth, scenario="unit", wall_seconds=99.9)

    assert MetricsTable([a]).comparable() == MetricsTable([b]).comparable()


def test_table_csv_has_stable_column_order(tmp_path: Path) -> None:
    events = log_from({"victim": [0.9, 0.4], "peer": [0.9, 0.9]})
    truth = GroundTruth(all_nodes=["victim", "peer"], anomalous={"victim": (1.0, 2.0)})
    table = MetricsTable([compute_metrics(events, truth, scenario="unit")])

    csv_path = table.to_csv(tmp_path / "metrics.csv")
    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert header.split(",") == list(COLUMNS)

    markdown = table.to_markdown()
    assert markdown.startswith("| " + " | ".join(COLUMNS) + " |")


def test_detection_threshold_is_configurable() -> None:
    events = log_from({"victim": [0.9, 0.7], "peer": [0.9, 0.9]})
    truth = GroundTruth(all_nodes=["victim", "peer"], anomalous={"victim": (1.0, 2.0)})

    lenient = compute_metrics(events, truth, scenario="unit")
    strict = compute_metrics(events, truth, scenario="unit", params=DetectionParams(flag_below=0.8))

    assert lenient.tp == 0
    assert strict.tp == 1


def test_empty_log_is_rejected() -> None:
    with pytest.raises(ValueError, match="empty event log"):
        compute_metrics([], GroundTruth(all_nodes=["a"]), scenario="unit")


def test_phase1_exit_passes_all_four_criteria() -> None:
    report = run_phase1_exit(run_id="test-exit", results_dir=RESULTS / "exit")

    assert report.criteria.victim_detected
    assert report.criteria.peers_stable
    assert report.criteria.under_time_budget
    assert report.criteria.byte_identical_replay
    assert report.passed, report.render()

    m = report.metrics
    assert m.n_nodes == 50
    assert m.fp == 0
    assert m.detection_latency is not None
    assert m.recovery_time is not None, "run too short to observe recovery"
    assert m.trust_separation is not None and m.trust_separation > 0.3


def test_phase1_exit_writes_metrics_table() -> None:
    report = run_phase1_exit(run_id="test-exit-table", results_dir=RESULTS / "table")
    out = Path(report.results_dir)

    assert (out / "events.jsonl").exists()
    assert (out / "manifest.json").exists()
    assert (out / "metrics.csv").exists()
    assert (out / "metrics.md").exists()
    assert len(load_events(out / "events.jsonl")) == 50 * 40
