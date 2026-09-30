"""Calibration: choose the coefficients on the calibration set only, then freeze."""

from __future__ import annotations

import argparse
import itertools
import json
import os
import statistics
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

from m8_eval_harness.params import SystemParams

GRID: dict[str, tuple[Any, ...]] = {
    "trust_lambda": (0.6, 0.7),
    "trust_lambda_up": (None, 0.8, 0.85, 0.9),
    "cohort_margin": (None, 0.12, 0.15, 0.2),
    "rep_lam_up": (0.85, 0.9, 0.95),
}
REPLICATES = 3

QUIET = ("cal-1", "cal-13")
GLITCH = ("cal-8",)
BENIGN = ("cal-9", "cal-10")
ATTACKS = ("cal-2", "cal-3", "cal-4", "cal-5", "cal-6", "cal-7", "cal-11", "cal-12")
LOW_AND_SLOW = "cal-4"
RECOVERY = ("cal-11",)
CALIBRATION_IDS = QUIET + GLITCH + BENIGN + ATTACKS
STARTING = SystemParams()


def candidates() -> list[SystemParams]:
    keys = list(GRID)
    return [
        replace(STARTING, **dict(zip(keys, values, strict=True)))
        for values in itertools.product(*GRID.values())
    ]


def run_one(job: tuple[SystemParams, str, int]) -> dict[str, Any]:
    import tempfile

    from m8_eval_harness.baselines import FULL
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios import by_id

    params, scenario_id, replicate = job
    scenario = by_id(scenario_id)
    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(
            scenario, FULL, seed=scenario.seed + replicate, params=params, results_dir=Path(tmp)
        )
    row = evaluate(result)
    row.update({"params": json.dumps(params.as_dict(), sort_keys=True), "replicate": replicate})
    return row


def score(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    by_scenario: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_scenario[row["scenario_id"]].append(row)

    def values(ids: Sequence[str], metric: str) -> list[float]:
        return [r[metric] for s in ids for r in by_scenario[s] if r.get(metric) is not None]

    violations = []
    if any(v > 0 for v in values(QUIET, "fp")):
        violations.append("quiet fleet responded")
    if any((r.get("benign_worst_level") or 0) > 1 for s in GLITCH for r in by_scenario[s]):
        violations.append("glitch escalated past L1")
    if any((r.get("benign_unrecovered") or 0) > 0 for s in GLITCH + BENIGN for r in by_scenario[s]):
        violations.append("benign device not recovered")

    detection = statistics.fmean(values(ATTACKS, "device_tpr") or [0.0])
    latency = statistics.fmean(values(ATTACKS, "latency_response_within_target") or [0.0])
    recovery_share = values(RECOVERY, "mttr_within_target")
    benign_mttr = values(BENIGN, "benign_mttr_mean")
    mttr = statistics.fmean(
        recovery_share + [1.0 if v <= 10 else 0.0 for v in benign_mttr] or [0.0]
    )
    low_and_slow = statistics.fmean(
        [
            1.0 if (r["reached_restrict_devices"] or 0) > 0 else 0.0
            for r in by_scenario[LOW_AND_SLOW]
        ]
        or [0.0]
    )
    burden_ticks = values(BENIGN, "benign_response_ticks")
    benign_devices = values(BENIGN, "benign_devices")
    burden = sum(burden_ticks) / max(1.0, sum(benign_devices) * 20.0)
    objective = (
        0.35 * detection
        + 0.20 * latency
        + 0.15 * mttr
        + 0.10 * low_and_slow
        + 0.20 * (1 - min(1.0, burden))
    )
    return {
        "feasible": not violations,
        "violations": "; ".join(violations),
        "objective": round(objective, 4),
        "detection": round(detection, 4),
        "latency_within_target": round(latency, 4),
        "mttr_within_target": round(mttr, 4),
        "low_and_slow_restricted": round(low_and_slow, 4),
        "benign_burden": round(burden, 4),
    }


def distance(params: SystemParams) -> int:
    return sum(getattr(params, k) != getattr(STARTING, k) for k in GRID)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    parser.add_argument("--out", type=Path, default=Path("results") / "calibration")
    args = parser.parse_args(argv)

    jobs = [(p, s, r) for p in candidates() for s in CALIBRATION_IDS for r in range(REPLICATES)]
    if args.workers <= 1:
        rows = [run_one(j) for j in jobs]
    else:
        from m8_eval_harness.experiment import MAX_CELLS_PER_WORKER, process_map

        rows = process_map(run_one, jobs, workers=args.workers, per_process=MAX_CELLS_PER_WORKER)

    by_params: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_params[row["params"]].append(row)
    ranking = []
    for key, group in by_params.items():
        params = SystemParams(**json.loads(key))
        ranking.append(
            {**params.as_dict(), **score(group), "distance_from_start": distance(params)}
        )
    ranking.sort(key=lambda r: (not r["feasible"], -r["objective"], r["distance_from_start"]))

    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "rows.jsonl").open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row, default=str) + "\n")
    (args.out / "ranking.json").write_text(json.dumps(ranking, indent=2))
    chosen = ranking[0]
    (args.out / "chosen.json").write_text(json.dumps(chosen, indent=2))
    header = [
        "trust_lambda",
        "trust_lambda_up",
        "cohort_margin",
        "rep_lam_up",
        "feasible",
        "objective",
        "detection",
        "latency_within_target",
        "mttr_within_target",
        "low_and_slow_restricted",
        "benign_burden",
        "violations",
    ]
    lines = [
        "# Calibration ranking",
        "",
        f"{len(rows)} runs, {len(ranking)} candidates, {REPLICATES} replicates, "
        "calibration set only.",
        "",
        "| " + " | ".join(header) + " |",
        "|" + "---|" * len(header),
    ]
    lines += ["| " + " | ".join(str(r[h]) for h in header) + " |" for r in ranking[:25]]
    (args.out / "ranking.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(chosen, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
