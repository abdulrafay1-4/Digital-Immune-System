"""The trust-layer acceptance check: four conditions on one 50-node run."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from m8_eval_harness.metrics import (
    DetectionParams,
    GroundTruth,
    MetricsTable,
    RunMetrics,
    compute_metrics,
    load_events,
)
from m8_eval_harness.simulator import run_trust_sim

TIME_BUDGET_SECONDS = 60.0


class ExitCriteria(BaseModel):
    """The four acceptance conditions, each independently reported."""

    model_config = ConfigDict(extra="forbid")

    victim_detected: bool
    peers_stable: bool
    under_time_budget: bool
    byte_identical_replay: bool

    @property
    def passed(self) -> bool:
        return (
            self.victim_detected
            and self.peers_stable
            and self.under_time_budget
            and self.byte_identical_replay
        )

    def failures(self) -> list[str]:
        return [name for name, ok in self.model_dump().items() if not ok]


class ExitReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    criteria: ExitCriteria
    metrics: RunMetrics
    results_dir: str

    @property
    def passed(self) -> bool:
        return self.criteria.passed

    def render(self) -> str:
        m = self.metrics
        elapsed = "?" if m.wall_seconds is None else f"{m.wall_seconds:.2f}s"
        lines = [
            f"Acceptance check: {'PASS' if self.passed else 'FAIL'}",
            f"  results: {self.results_dir}",
            "",
            f"  victim detected ......... {self.criteria.victim_detected}",
            f"  peers stable (fp == 0) .. {self.criteria.peers_stable}",
            f"  under {TIME_BUDGET_SECONDS:.0f}s ............. "
            f"{self.criteria.under_time_budget} ({elapsed})",
            f"  byte-identical replay ... {self.criteria.byte_identical_replay}",
            "",
            f"  detection latency ....... {m.detection_latency} sim-s",
            f"  recovery time ........... {m.recovery_time} sim-s",
            f"  accuracy / fpr .......... {m.accuracy:.4f} / {m.fpr:.4f}",
            f"  trust separation ........ {m.trust_separation}",
        ]
        if not self.passed:
            lines += ["", f"  FAILED: {', '.join(self.criteria.failures())}"]
        return "\n".join(lines)


def run_phase1_exit(
    *,
    seed: int = 42,
    n_nodes: int = 50,
    ticks: int = 40,
    tick_seconds: float = 1.0,
    run_id: str = "phase1-exit",
    anomaly_node: str = "node-0",
    anomaly_window: tuple[float, float, float] = (10.0, 25.0, 0.6),
    config: dict[str, Any] | None = None,
    results_dir: Path | None = None,
    detection: DetectionParams | None = None,
) -> ExitReport:
    """Run the acceptance scenario and report against all four criteria."""
    out_dir = results_dir or (Path("results") / run_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    sim_kwargs: dict[str, Any] = dict(
        seed=seed,
        n_nodes=n_nodes,
        ticks=ticks,
        tick_seconds=tick_seconds,
        run_id=run_id,
        anomaly_node=anomaly_node,
        anomaly_window=anomaly_window,
        config=config,
    )

    started = time.perf_counter()
    _, _, log_a = run_trust_sim(**sim_kwargs, results_dir=out_dir)
    wall_seconds = time.perf_counter() - started

    _, _, log_b = run_trust_sim(**sim_kwargs, results_dir=out_dir / "_replay")

    events = load_events(out_dir / "events.jsonl")
    start, end, _severity = anomaly_window
    truth = GroundTruth(
        all_nodes=[f"node-{i}" for i in range(n_nodes)],
        anomalous={anomaly_node: (start, end)},
    )

    metrics = compute_metrics(
        events,
        truth,
        scenario="phase1-exit",
        baseline="dis",
        params=detection,
        wall_seconds=wall_seconds,
    )

    table = MetricsTable([metrics])
    table.to_csv(out_dir / "metrics.csv")
    table.to_markdown(out_dir / "metrics.md")

    criteria = ExitCriteria(
        victim_detected=metrics.tp >= 1,
        peers_stable=metrics.fp == 0,
        under_time_budget=wall_seconds < TIME_BUDGET_SECONDS,
        byte_identical_replay=log_a == log_b,
    )
    return ExitReport(criteria=criteria, metrics=metrics, results_dir=str(out_dir))


def main() -> int:
    report = run_phase1_exit()
    print(report.render())
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
