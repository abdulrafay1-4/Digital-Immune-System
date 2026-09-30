"""Fit the C4 comparator (optimal multiple stopping) on the calibration set only."""

from __future__ import annotations

import argparse
import itertools
import json
import os
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from m8_eval_harness.calibrate import CALIBRATION_IDS, score

BINS = 20

THRESHOLD_GRID = (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 0.999)

REPLICATES = 3


def labelled_gt(workers: int = 3) -> tuple[list[float], list[float], float]:
    """(healthy GT values, intruded GT values, per-tick intrusion rate)."""
    jobs = [(s, r) for s in CALIBRATION_IDS for r in range(REPLICATES)]
    collected = _map(_gt_of, jobs, workers)

    healthy: list[float] = []
    intruded: list[float] = []
    onsets = 0
    healthy_ticks = 0
    for run_healthy, run_intruded, run_onsets, run_healthy_ticks in collected:
        healthy += run_healthy
        intruded += run_intruded
        onsets += run_onsets
        healthy_ticks += run_healthy_ticks
    return healthy, intruded, onsets / max(1, healthy_ticks)


def _gt_of(job: tuple[str, int]) -> tuple[list[float], list[float], int, int]:
    import tempfile

    from m8_eval_harness.baselines import FULL
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios import by_id

    scenario_id, replicate = job
    scenario = by_id(scenario_id)
    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(scenario, FULL, seed=scenario.seed + replicate, results_dir=Path(tmp))
    attacked = {f"node-{i}": scenario.attack_ticks(f"node-{i}") for i in range(scenario.n_nodes)}
    healthy: list[float] = []
    intruded: list[float] = []
    onsets = 0
    healthy_ticks = 0
    previous: dict[str, bool] = {}
    for outcome in result.pipeline.outcomes:
        tick = int(outcome.sim_time)
        for update in outcome.gt_updates:
            now = tick in attacked.get(update.node_id, frozenset())
            (intruded if now else healthy).append(update.ts)
            if now and not previous.get(update.node_id, False):
                onsets += 1
            if not now:
                healthy_ticks += 1
            previous[update.node_id] = now
    return healthy, intruded, onsets, healthy_ticks


def _map(fn: Any, jobs: list[Any], workers: int) -> list[Any]:
    """
    Workers recycled every few runs, as the harness does: a long-lived worker otherwise grows
    without bound across a long fit.
    """
    if workers <= 1:
        return [fn(job) for job in jobs]
    from m8_eval_harness.experiment import MAX_CELLS_PER_WORKER, process_map

    return process_map(fn, jobs, workers=workers, per_process=MAX_CELLS_PER_WORKER)


def histogram(values: Sequence[float]) -> tuple[float, ...]:
    """Laplace-smoothed density over `BINS` bins of [0, 1]."""
    counts = [1.0] * BINS
    for value in values:
        counts[min(BINS - 1, max(0, int(min(1.0, max(0.0, value)) * BINS)))] += 1.0
    total = sum(counts)
    return tuple(c / total for c in counts)


def nested_grids() -> list[tuple[float, ...]]:
    """Every threshold triple the policy structure allows."""
    return [
        triple
        for triple in itertools.product(THRESHOLD_GRID, repeat=3)
        if triple[0] >= triple[1] >= triple[2]
    ]


def run_one(job: tuple[dict[str, Any], str, int]) -> dict[str, Any]:
    import tempfile

    from m8_eval_harness.baselines.base import StoppingPolicy, stopping_response
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios import by_id

    policy_dict, scenario_id, replicate = job
    policy = StoppingPolicy(
        thresholds=tuple(policy_dict["thresholds"]),
        f_healthy=tuple(policy_dict["f_healthy"]),
        f_intruded=tuple(policy_dict["f_intruded"]),
        intrusion_rate=policy_dict["intrusion_rate"],
        release=policy_dict["release"],
    )
    scenario = by_id(scenario_id)
    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(
            scenario,
            stopping_response(policy),
            seed=scenario.seed + replicate,
            results_dir=Path(tmp),
        )
    row = evaluate(result)
    row.update({"thresholds": json.dumps(list(policy.thresholds)), "replicate": replicate})
    return row


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    parser.add_argument("--out", type=Path, default=Path("results") / "calibration")
    parser.add_argument("--config", type=Path, default=Path("configs") / "stopping_response.json")
    parser.add_argument(
        "--release",
        action="store_true",
        help="fit the variant that gives a level back when the belief falls",
    )
    args = parser.parse_args(argv)

    suffix = "_release" if args.release else ""
    healthy, intruded, rate = labelled_gt(args.workers)
    observation_model = {
        "f_healthy": list(histogram(healthy)),
        "f_intruded": list(histogram(intruded)),
        "intrusion_rate": round(rate, 6),
    }
    print(
        f"observation model: {len(healthy)} healthy and {len(intruded)} intruded "
        f"device-ticks of own trust, intrusion rate {rate:.5f}"
    )

    candidates = [
        {"thresholds": list(triple), "release": args.release, **observation_model}
        for triple in nested_grids()
    ]
    jobs = [
        (candidate, scenario_id, replicate)
        for candidate in candidates
        for scenario_id in CALIBRATION_IDS
        for replicate in range(REPLICATES)
    ]
    print(f"{len(candidates)} threshold candidates, {len(jobs)} runs")

    rows = _map(run_one, jobs, args.workers)

    by_thresholds: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_thresholds[row["thresholds"]].append(row)
    ranking = []
    for key, group in by_thresholds.items():
        ranking.append({"thresholds": json.loads(key), **score(group)})
    ranking.sort(key=lambda r: (not r["feasible"], -r["objective"], -sum(r["thresholds"])))

    chosen = ranking[0]
    fitted = {**observation_model, "thresholds": chosen["thresholds"]}
    config = (
        args.config.with_name("stopping_response_release.json") if args.release else args.config
    )
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(json.dumps(fitted, indent=2) + "\n")

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / f"stopping_response{suffix}_ranking.json").write_text(json.dumps(ranking, indent=2))
    lines = [
        "# C4 comparator: optimal multiple stopping"
        + (" with release" if args.release else "")
        + ", fitted on the calibration set",
        "",
        f"{len(rows)} runs over {len(CALIBRATION_IDS)} calibration scenarios, "
        f"{REPLICATES} replicates, {len(candidates)} threshold candidates.",
        "",
        f"Observation model: {len(healthy)} healthy and {len(intruded)} intruded "
        f"device-ticks of own trust, {BINS} bins, intrusion rate {rate:.5f}.",
        "",
        "| thresholds (1, 2, 3 stops remaining) | feasible | objective | detection | "
        "latency in target | benign burden |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in ranking[:10]:
        lines.append(
            f"| {row['thresholds']} | {'yes' if row['feasible'] else 'no'} | "
            f"{row['objective']} | {row['detection']} | {row['latency_within_target']} | "
            f"{row['benign_burden']} |"
        )
    lines += ["", f"Chosen: {chosen['thresholds']} → `{config}`.", ""]
    (args.out / f"stopping_response{suffix}.md").write_text("\n".join(lines))
    print(f"chosen thresholds {chosen['thresholds']} (objective {chosen['objective']})")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
