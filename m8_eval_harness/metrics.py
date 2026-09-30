"""Metrics table: the single results artifact every run writes rows into."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable, Sequence
from pathlib import Path
from statistics import fmean, pstdev

from pydantic import BaseModel, ConfigDict, Field

from shared.schemas import TrustUpdate


class DetectionParams(BaseModel):
    """Thresholds that turn a trust series into a detection decision."""

    model_config = ConfigDict(extra="forbid")

    flag_below: float = Field(default=0.60, ge=0.0, le=1.0)
    recovered_at_or_above: float = Field(default=0.85, ge=0.0, le=1.0)


class GroundTruth(BaseModel):
    """What the scenario knows and the system under test does not."""

    model_config = ConfigDict(extra="forbid")

    all_nodes: list[str]
    anomalous: dict[str, tuple[float, float]] = Field(default_factory=dict)

    def is_anomalous(self, node_id: str) -> bool:
        return node_id in self.anomalous


class RunMetrics(BaseModel):
    """One row of the results table."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    seed: int
    config_hash: str
    scenario: str
    baseline: str = "dis"

    n_nodes: int
    n_events: int
    ticks: int

    tp: int
    fp: int
    tn: int
    fn: int

    accuracy: float
    precision: float | None
    recall: float | None
    fpr: float

    detection_latency: float | None = None
    containment_time: float | None = None
    recovery_time: float | None = None
    mttr: float | None = None

    mean_trust_healthy: float
    mean_trust_anomalous: float | None
    trust_separation: float | None
    min_trust_anomalous: float | None
    healthy_trust_stability: float

    memory_poisoning_blocked: bool | None = None

    wall_seconds: float | None = None


def load_events(path: Path) -> list[TrustUpdate]:
    """Read a `TrustUpdate` JSONL log back into models."""
    events: list[TrustUpdate] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            events.append(TrustUpdate.model_validate(json.loads(line)))
    return events


def series_by_node(events: Iterable[TrustUpdate]) -> dict[str, list[tuple[float, float]]]:
    """node_id -> [(sim_time, node_trust), ...] sorted by sim_time."""
    out: dict[str, list[tuple[float, float]]] = {}
    for ev in events:
        out.setdefault(ev.node_id, []).append((ev.sim_time, ev.node_trust))
    for node_id in out:
        out[node_id].sort(key=lambda pair: pair[0])
    return out


def first_time_below(series: Sequence[tuple[float, float]], threshold: float) -> float | None:
    for sim_time, value in series:
        if value < threshold:
            return sim_time
    return None


def first_time_at_or_above_after(
    series: Sequence[tuple[float, float]], threshold: float, after: float
) -> float | None:
    for sim_time, value in series:
        if sim_time >= after and value >= threshold:
            return sim_time
    return None


def _safe_div(num: float, den: float) -> float | None:
    return None if den == 0 else num / den


def values_in_window(
    series: Sequence[tuple[float, float]], start: float, end: float
) -> list[float]:
    """Trust values with `start <= sim_time < end`."""
    return [value for sim_time, value in series if start <= sim_time < end]


def evaluation_window(truth: GroundTruth, events: Sequence[TrustUpdate]) -> tuple[float, float]:
    """The interval trust behaviour is judged over."""
    if truth.anomalous:
        starts = [start for start, _ in truth.anomalous.values()]
        ends = [end for _, end in truth.anomalous.values()]
        return min(starts), max(ends)
    times = [ev.sim_time for ev in events]
    return min(times), max(times) + 1.0


def compute_metrics(
    events: Sequence[TrustUpdate],
    truth: GroundTruth,
    *,
    scenario: str,
    baseline: str = "dis",
    params: DetectionParams | None = None,
    wall_seconds: float | None = None,
) -> RunMetrics:
    """Reduce an event log + ground truth into one results row."""
    if not events:
        raise ValueError("empty event log: nothing to measure")

    par = params or DetectionParams()
    series = series_by_node(events)
    win_start, win_end = evaluation_window(truth, events)

    tp = fp = tn = fn = 0
    detection_latency: float | None = None
    recovery_time: float | None = None
    healthy_window: list[float] = []
    anomalous_window: list[float] = []
    healthy_stdevs: list[float] = []

    for node_id in truth.all_nodes:
        node_series = series.get(node_id, [])
        if not node_series:
            if truth.is_anomalous(node_id):
                fn += 1
            continue

        flagged = first_time_below(node_series, par.flag_below) is not None
        window_values = values_in_window(node_series, win_start, win_end)

        if truth.is_anomalous(node_id):
            anomalous_window.extend(window_values)
            if flagged:
                tp += 1
            else:
                fn += 1

            start, end = truth.anomalous[node_id]
            detected_at = first_time_below(node_series, par.flag_below)
            if detected_at is not None:
                latency = max(0.0, detected_at - start)
                detection_latency = (
                    latency if detection_latency is None else min(detection_latency, latency)
                )
            recovered_at = first_time_at_or_above_after(node_series, par.recovered_at_or_above, end)
            if recovered_at is not None:
                rec = max(0.0, recovered_at - end)
                recovery_time = rec if recovery_time is None else max(recovery_time, rec)
        else:
            healthy_window.extend(window_values)
            if len(window_values) > 1:
                healthy_stdevs.append(pstdev(window_values))
            if flagged:
                fp += 1
            else:
                tn += 1

    total = tp + fp + tn + fn
    mean_healthy = fmean(healthy_window) if healthy_window else 0.0
    mean_anomalous = fmean(anomalous_window) if anomalous_window else None

    return RunMetrics(
        run_id=events[0].run_id,
        seed=events[0].seed,
        config_hash=events[0].config_hash,
        scenario=scenario,
        baseline=baseline,
        n_nodes=len(truth.all_nodes),
        n_events=len(events),
        ticks=max(len(s) for s in series.values()),
        tp=tp,
        fp=fp,
        tn=tn,
        fn=fn,
        accuracy=(tp + tn) / total if total else 0.0,
        precision=_safe_div(tp, tp + fp),
        recall=_safe_div(tp, tp + fn),
        fpr=_safe_div(fp, fp + tn) or 0.0,
        detection_latency=detection_latency,
        recovery_time=recovery_time,
        mean_trust_healthy=mean_healthy,
        mean_trust_anomalous=mean_anomalous,
        trust_separation=(mean_healthy - mean_anomalous) if mean_anomalous is not None else None,
        min_trust_anomalous=min(anomalous_window) if anomalous_window else None,
        healthy_trust_stability=fmean(healthy_stdevs) if healthy_stdevs else 0.0,
        wall_seconds=wall_seconds,
    )


COLUMNS: tuple[str, ...] = (
    "scenario",
    "baseline",
    "run_id",
    "seed",
    "config_hash",
    "n_nodes",
    "ticks",
    "n_events",
    "tp",
    "fp",
    "tn",
    "fn",
    "accuracy",
    "precision",
    "recall",
    "fpr",
    "detection_latency",
    "containment_time",
    "recovery_time",
    "mttr",
    "mean_trust_healthy",
    "mean_trust_anomalous",
    "trust_separation",
    "min_trust_anomalous",
    "healthy_trust_stability",
    "memory_poisoning_blocked",
    "wall_seconds",
)

NONDETERMINISTIC_COLUMNS: frozenset[str] = frozenset({"wall_seconds"})


def _render(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


class MetricsTable:
    """Accumulates `RunMetrics` rows and renders them to CSV and Markdown."""

    def __init__(self, rows: Iterable[RunMetrics] | None = None) -> None:
        self.rows: list[RunMetrics] = list(rows or [])

    def add(self, row: RunMetrics) -> None:
        self.rows.append(row)

    def to_csv(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(COLUMNS))
            writer.writeheader()
            for row in self.rows:
                data = row.model_dump()
                writer.writerow({col: data[col] for col in COLUMNS})
        return path

    def to_markdown(self, path: Path | None = None) -> str:
        header = "| " + " | ".join(COLUMNS) + " |"
        divider = "| " + " | ".join("---" for _ in COLUMNS) + " |"
        lines = [header, divider]
        for row in self.rows:
            data = row.model_dump()
            lines.append("| " + " | ".join(_render(data[col]) for col in COLUMNS) + " |")
        text = "\n".join(lines) + "\n"
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return text

    def comparable(self) -> list[dict[str, object]]:
        """Rows with machine-dependent fields stripped, for determinism checks."""
        return [
            {k: v for k, v in row.model_dump().items() if k not in NONDETERMINISTIC_COLUMNS}
            for row in self.rows
        ]
