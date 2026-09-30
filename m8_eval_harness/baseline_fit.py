"""Fit every comparator's free parameters on the calibration set only."""

from __future__ import annotations

import argparse
import json
import tempfile
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from m8_eval_harness.calibrate import CALIBRATION_IDS, REPLICATES, score

FAMILIES: dict[str, tuple[str, ...]] = {
    "binary_zt": tuple(
        f"binary_zt{'' if t == 0.5 else f'@{t:g}'}{'+brake' if b else ''}"
        for t in (0.5, 0.6, 0.7, 0.8)
        for b in (False, True)
    ),
    "beta_reputation": tuple(
        "beta_reputation" if f == 0.9 else f"beta_reputation@{f:g}"
        for f in (0.9, 0.5, 0.6, 0.7, 0.8, 0.95)
    ),
    "cusum": tuple(
        f"cusum@{k:g}:{h:g}"
        for k in (0.05, 0.02, 0.1, 0.15, 0.2, 0.3)
        for h in (0.4, 0.1, 0.2, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6)
    ),
    "page_cusum": tuple(
        f"page_cusum@{k:g}:{h:g}"
        for k in (0.05, 0.02, 0.1, 0.15, 0.2, 0.3)
        for h in (0.4, 0.1, 0.2, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6)
    ),
    "tolerance_periodic": tuple(f"tolerance_periodic@{d}" for d in (5, 15, 25)),
    "dirichlet_reliability": tuple(
        "dirichlet_reliability" if lam == 0.9 else f"dirichlet_reliability@{lam:g}"
        for lam in (0.9, 0.5, 0.7, 0.8, 0.95, 0.99)
    ),
    "penalty_healing": tuple(f"penalty_healing@{p}" for p in (10, 3, 5, 20, 40)),
    "ddca": tuple(
        f"ddca@{theta:g}:{m:g}" for theta in (0.8, 0.6, 0.7, 0.85) for m in (2, 0.5, 1, 4)
    ),
    "isolation_forest": tuple(
        "isolation_forest" if c == 0.01 else f"isolation_forest@{c:g}"
        for c in (0.01, 0.001, 0.002, 0.005, 0.02, 0.05)
    ),
    "isolation_forest_persistent": tuple(
        f"isolation_forest_persistent@{c:g}" for c in (0.01, 0.001, 0.002, 0.005, 0.02)
    ),
}

CONFIG = Path("configs") / "fitted_baselines.json"


def fitted(family: str, default: str | None = None) -> str:
    """The arm id the calibration fit chose for `family`."""
    path = Path(__file__).resolve().parents[1] / CONFIG
    if path.exists():
        chosen = json.loads(path.read_text()).get(family)
        if chosen:
            return str(chosen)
    if default is None:
        raise KeyError(f"no fitted arm for {family}: run `python -m m8_eval_harness.baseline_fit`")
    return default


def run_one(job: tuple[str, str, int]) -> dict[str, Any]:
    from m8_eval_harness.baselines import by_id
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios import by_id as scenario_by_id

    arm, scenario_id, replicate = job
    scenario = scenario_by_id(scenario_id)
    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(
            scenario, by_id(arm), seed=scenario.seed + replicate, results_dir=Path(tmp)
        )
    row = evaluate(result)
    row.update({"arm": arm, "replicate": replicate})
    return row


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--families", nargs="*", default=list(FAMILIES))
    parser.add_argument("--out", type=Path, default=Path("results") / "calibration")
    args = parser.parse_args(argv)

    arms = [a for f in args.families for a in FAMILIES[f]]
    jobs = [(a, s, r) for a in arms for s in CALIBRATION_IDS for r in range(REPLICATES)]
    print(f"{len(arms)} candidates, {len(jobs)} runs")
    if args.workers <= 1:
        rows = [run_one(j) for j in jobs]
    else:
        from m8_eval_harness.experiment import MAX_CELLS_PER_WORKER, process_map

        rows = process_map(run_one, jobs, workers=args.workers, per_process=MAX_CELLS_PER_WORKER)

    by_arm: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_arm[row["arm"]].append(row)

    config = json.loads(CONFIG.read_text()) if CONFIG.exists() else {}
    args.out.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Comparators fitted on the calibration set",
        "",
        f"{REPLICATES} replicates of {len(CALIBRATION_IDS)} calibration scenarios per candidate, "
        "scored with `calibrate.score`: the objective and constraints our own coefficients "
        "were chosen with. Ties go to the published default, listed first.",
        "",
    ]
    for family in args.families:
        ranking = [{"arm": a, **score(by_arm[a])} for a in FAMILIES[family]]
        order = {a: i for i, a in enumerate(FAMILIES[family])}
        ranking.sort(key=lambda r: (not r["feasible"], -r["objective"], order[r["arm"]]))
        config[family] = ranking[0]["arm"]
        (args.out / f"fit_{family}.json").write_text(json.dumps(ranking, indent=2))
        lines += [
            f"## {family}: chosen `{ranking[0]['arm']}`",
            "",
            "| arm | feasible | violations | objective | detection | latency in target | "
            "benign burden |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
        for r in ranking:
            lines.append(
                f"| {r['arm']} | {'yes' if r['feasible'] else 'no'} | {r['violations'] or '-'} | "
                f"{r['objective']} | {r['detection']} | {r['latency_within_target']} | "
                f"{r['benign_burden']} |"
            )
        lines.append("")
    CONFIG.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    (args.out / "fitted_baselines.md").write_text("\n".join(lines))
    print("\n".join(f"{f}: {config[f]}" for f in args.families))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
