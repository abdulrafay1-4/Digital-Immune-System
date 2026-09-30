"""Experiment runner: the evaluation, reproducible from one command."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import platform
import subprocess
import sys
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from m8_eval_harness import stats
from m8_eval_harness.params import FROZEN, SystemParams

HELD_OUT_SEEDS: tuple[int, ...] = tuple(range(20000, 20100))


def recorded_rows(out: Path) -> list[dict[str, Any]]:
    """A suite's rows: `rows.jsonl` if it was run here, else the recorded `rows.jsonl.gz`."""
    path = out / "rows.jsonl"
    if path.exists():
        text = path.read_text()
    else:
        with gzip.open(out / "rows.jsonl.gz", "rt") as fh:
            text = fh.read()
    return [json.loads(line) for line in text.splitlines() if line]


PROPOSAL_ARMS = (
    "full",
    "static_trust",
    "no_sharing",
    "no_memory",
    "binary_response",
    "no_recovery",
    "binary_zt",
)
RESEARCH_ARMS = ("binary_zt", "trust_only", "trust_ti", "no_memory", "full")
ABLATION_ARMS = (
    "full",
    "static_trust",
    "no_sharing",
    "equal_weighting",
    "no_memory",
    "binary_response",
    "no_quorum",
    "no_weighting_no_quorum",
    "no_recovery",
)
CONTRIBUTION_ARMS = (
    "full",
    "static_trust",
    "no_sharing",
    "no_memory",
    "binary_response",
    "no_recovery",
    "static_no_sharing",
)
ADAPTIVE_ARMS = ("full", "static_trust", "no_sharing", "no_memory")

KEY_METRICS = (
    "device_tpr",
    "device_fpr",
    "device_f1",
    "tick_f1",
    "response_coverage",
    "latency_flag_mean",
    "latency_response_mean",
    "latency_restrict_mean",
    "containment_mean",
    "mttr_mean",
    "trust_restoration_mean",
    "benign_mttr_mean",
    "false_restriction_rate",
    "availability_cost",
    "disruptive_actions",
    "isolations",
    "operator_requests",
    "label_accuracy_primary",
    "tick_ms_p95",
)


@dataclass(frozen=True)
class Cell:
    scenario_id: str
    baseline_id: str
    seed: int
    operator: str = "absent"
    adjudication: str = "oracle"
    noise: str | None = None
    params_label: str = "frozen"
    binding: str = "provisioned"

    def variant(self) -> str:
        base = f"op={self.operator}|adj={self.adjudication}|noise={self.noise or 'gaussian'}"
        return base if self.binding == "provisioned" else f"{base}|binding={self.binding}"


def resolve_scenario(scenario_id: str):
    from m8_eval_harness.scenarios import by_id
    from m8_eval_harness.scenarios.base import Anomaly, Scenario

    if scenario_id.startswith("loss:"):
        _, share, base = scenario_id.split(":")
        return replace(by_id(base), scenario_id=scenario_id, message_loss=float(share))
    if scenario_id.startswith("drop:"):
        base = by_id(scenario_id.split(":")[1])
        healthy = next(
            f"node-{i}"
            for i in range(base.n_nodes - 1, -1, -1)
            if f"node-{i}" not in base.anomaly_map and f"node-{i}" not in base.outages
        )
        return replace(base, scenario_id=scenario_id, dropped={healthy: (20.0, 40.0)})
    if not scenario_id.startswith("sweep:"):
        return by_id(scenario_id)
    kind, *args = scenario_id.split(":")[1:]
    if kind == "lowslow":
        severity = float(args[0])
        return Scenario(
            scenario_id=scenario_id,
            name=f"Low-and-slow at {severity}",
            demonstrates="severity sweep",
            n_nodes=50,
            ticks=60,
            anomalies=(Anomaly("node-0", 10.0, 55.0, severity, ("behavioral", "network")),),
            ground_truth={"node-0": 10.0},
        )
    if kind == "campaign":
        severity = float(args[0])
        return Scenario(
            scenario_id=scenario_id,
            name=f"Campaign at {severity}",
            demonstrates="severity sweep",
            n_nodes=50,
            ticks=40,
            anomalies=tuple(Anomaly(f"node-{i}", 12.0 + i, 36.0, severity) for i in range(4)),
            ground_truth={f"node-{i}": 12.0 + i for i in range(4)},
        )
    if kind == "duty":
        on, period, severity = int(args[0]), int(args[1]), float(args[2])
        return Scenario(
            scenario_id=scenario_id,
            name=f"On-off {on}/{period} at {severity}",
            demonstrates="duty sweep",
            n_nodes=50,
            ticks=100,
            anomalies=(Anomaly("node-0", 5.0, 95.0, severity, pulse_on=on, pulse_period=period),),
            ground_truth={"node-0": 5.0},
        )
    if kind == "scale":
        n = int(args[0])
        return Scenario(
            scenario_id=scenario_id,
            name=f"Recurring attack at {n} devices",
            demonstrates="scale",
            n_nodes=n,
            ticks=40,
            anomalies=(
                Anomaly("node-0", 8.0, 24.0, 0.8, ("device", "network")),
                Anomaly("node-1", 9.0, 24.0, 0.8, ("device", "network")),
            ),
            ground_truth={"node-0": 8.0, "node-1": 9.0},
        )
    raise KeyError(f"unknown sweep: {scenario_id}")


SENSITIVITY_LABELS = (
    "weights=0.50,0.30,0.20",
    "weights=0.30,0.40,0.30",
    "weights=0.40,0.25,0.35",
    "k=1",
    "k=3",
    "threshold=0.3",
    "threshold=0.5",
    "hysteresis=1",
    "hysteresis=5",
    "lambda=0.6",
    "lambda=0.8",
    "lambda_up=0.85",
    "cohort=none",
    "rep_up=0.95",
    "brake=none",
    "brake=0.25",
    "cap=none",
)

_SENSITIVITY_FIELDS = {
    "k": "cti_k",
    "threshold": "campaign_ti_threshold",
    "hysteresis": "hysteresis_n",
    "lambda": "trust_lambda",
    "lambda_up": "trust_lambda_up",
    "cohort": "cohort_margin",
    "rep_up": "rep_lam_up",
    "brake": "max_auto_restrict_fraction",
    "cap": "cohort_baseline_cap",
    "zeta": "drift_coeff",
}


def sensitivity_params(label: str) -> SystemParams:
    """`frozen`, or `FROZEN` with one coefficient moved: `k=3`, `weights=a,b,g`, ..."""
    if label == "frozen":
        return FROZEN
    name, _, value = label.partition("=")
    if name == "weights":
        alpha, beta, gamma = (float(x) for x in value.split(","))
        return replace(FROZEN, alpha=alpha, beta=beta, gamma=gamma)
    key = _SENSITIVITY_FIELDS[name]
    parsed: Any = (
        None if value == "none" else (int(value) if key == "hysteresis_n" else float(value))
    )
    return replace(FROZEN, **{key: parsed})


def _fitted(family: str) -> str:
    """The comparator setting the calibration fit chose (`baseline_fit`)."""
    from m8_eval_harness.baseline_fit import fitted

    return fitted(family)


def _unique(*arms: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(arms))


def external_arms() -> tuple[str, ...]:
    """
    Every comparator at the setting the calibration set chose, plus the proposal's own binary zero
    trust at 0.5.
    """
    return _unique(
        "full",
        "binary_zt",
        _fitted("binary_zt"),
        _fitted("beta_reputation"),
        _fitted("cusum"),
        _fitted("page_cusum"),
        "tolerance",
        "tolerance_no_recovery",
        _fitted("tolerance_periodic"),
        _fitted("dirichlet_reliability"),
        "stopping_response",
        "stopping_response_release",
        _fitted("penalty_healing"),
        _fitted("isolation_forest"),
        _fitted("isolation_forest_persistent"),
        _fitted("ddca"),
    )


def suite_cells(name: str, seeds: Sequence[int]) -> list[Cell]:
    from m8_eval_harness.scenarios import ADAPTIVE, RESILIENCE, SCENARIOS

    six = [s.scenario_id for s in SCENARIOS]
    adaptive = [s.scenario_id for s in ADAPTIVE]
    resilience = [s.scenario_id for s in RESILIENCE]

    def grid(scenarios: Iterable[str], arms: Iterable[str], **kw: Any) -> list[Cell]:
        return [Cell(s, a, seed, **kw) for s in scenarios for a in arms for seed in seeds]

    if name == "fyp":
        return grid(six, _unique(*PROPOSAL_ARMS, _fitted("binary_zt")))
    if name == "research":
        return grid(six, RESEARCH_ARMS)
    if name == "ablations":
        return grid(six, ABLATION_ARMS)
    if name == "contributions":
        return grid(six, CONTRIBUTION_ARMS)
    if name == "external":
        return grid(six + adaptive, external_arms())
    if name == "adaptive":
        return grid(adaptive, ADAPTIVE_ARMS)
    if name == "resilience":
        return grid(resilience, external_arms())
    if name == "operators":
        return [
            c
            for op in ("absent", "approve", "deny", "approve_after:5")
            for c in grid(("s3", "a6", "a10"), ("full",), operator=op)
        ]
    if name == "adjudication":
        return [
            c
            for adj in ("oracle", "auto_confirm", "none")
            for c in grid(("r5", "r6", "s3"), ("full",), adjudication=adj)
        ]
    if name == "noise":
        return [
            c
            for kind in ("gaussian", "heavy_tail", "diurnal", "correlated", "ton_iot")
            for c in grid(
                ("s1", "s2", "s3", "r3", "r5"),
                _unique(
                    "full",
                    "binary_zt",
                    _fitted("binary_zt"),
                    "stopping_response",
                    _fitted("cusum"),
                    _fitted("page_cusum"),
                    "tolerance",
                ),
                noise=kind,
            )
        ]
    if name == "fairness":
        cells = grid(("r5", "r6", "s1", "s2"), ("full", "binary_zt", "binary_zt+brake"))
        cells += grid(
            ("s1", "s3", "r5"),
            [f"isolation_forest@{c:g}" for c in (0.002, 0.005, 0.02, 0.05)]
            + ["isolation_forest", "full"],
        )
        braked = _fitted("binary_zt") + "+brake"
        cells += grid(resilience, (braked,))
        cells += [
            c
            for kind in ("gaussian", "heavy_tail", "diurnal", "correlated", "ton_iot")
            for c in grid(("s1", "s2", "s3", "r3", "r5"), (braked,), noise=kind)
        ]
        return cells
    if name == "sweeps":
        cells = grid(
            [f"sweep:lowslow:{v:.2f}" for v in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)],
            ("full", "binary_zt"),
        )
        cells += grid(
            [f"sweep:campaign:{v:.2f}" for v in (0.2, 0.25, 0.3, 0.35, 0.4, 0.5)],
            ("full", "no_sharing"),
        )
        cells += grid(
            [
                f"sweep:duty:{on}:{p}:0.60"
                for on, p in ((1, 10), (1, 5), (1, 3), (2, 5), (1, 2), (3, 5))
            ],
            ("full", "beta_reputation"),
        )
        cells += grid(
            ("s1", "s2", "s3", "r5"),
            [f"binary_zt@{t:g}" for t in (0.3, 0.4, 0.6, 0.7, 0.8)] + ["binary_zt", "full"],
        )
        return cells
    if name == "scale":
        return grid(
            [f"sweep:scale:{n}" for n in (50, 100, 500, 1000, 2500, 5000)], ("full",)
        ) + grid([f"sweep:scale:{n}" for n in (50, 5000)], ("binary_zt",))
    if name == "llm":
        return grid((*six, "r3"), ("full", "full_llm"))
    if name == "registration":
        return [
            c
            for binding in ("provisioned", "tofu")
            for c in grid(("a8", "a11"), ("full",), binding=binding)
        ]
    if name == "sensitivity":
        return [
            c
            for label in ("frozen", *SENSITIVITY_LABELS)
            for c in grid(("s1", "s2", "s3", "a1", "r5"), ("full",), params_label=label)
        ]
    if name == "robustness":
        strong = (
            "full",
            _fitted("binary_zt"),
            _fitted("cusum"),
            _fitted("page_cusum"),
            "tolerance",
            "stopping_response",
        )
        cells = grid(
            [f"loss:{p:g}:{s}" for p in (0.01, 0.05, 0.1) for s in ("r3", "a12", "s2")], strong
        )
        cells += grid(("drop:r3",), strong)
        cells += grid(("a12", "s1", "s2", "s3", "r1"), ("full",), params_label="zeta=0")
        cells += grid(
            ("s3", "r3", "r4", "r5", "r6"),
            [f"penalty_healing@{p}" for p in (3, 5, 20, 40)],
        )
        cells += [
            c
            for label in ("lambda_up=0.85", "threshold=0.3")
            for c in grid(("r1", "r2", "r3", "r4", "r5", "r6"), ("full",), params_label=label)
        ]
        return cells
    if name == "quick":
        return [Cell("s3", "full", seeds[0]), Cell("s3", "binary_zt", seeds[0])]
    raise KeyError(f"unknown suite: {name}")


def run_cell(cell: Cell) -> dict[str, Any]:
    import tempfile

    from m1_monitoring.sensors.synthetic import NoiseModel
    from m8_eval_harness import baselines
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario

    scenario = resolve_scenario(cell.scenario_id)
    if cell.noise == "ton_iot":
        from m8_eval_harness.ton_iot import noise_model

        scenario = replace(scenario, noise=noise_model())
    elif cell.noise is not None and cell.noise != "gaussian":
        scenario = replace(scenario, noise=NoiseModel(kind=cell.noise))
    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(
            scenario,
            baselines.by_id(cell.baseline_id),
            seed=cell.seed,
            results_dir=Path(tmp),
            adjudication=cell.adjudication,
            operator=cell.operator,
            params=sensitivity_params(cell.params_label),
            binding=cell.binding,
        )
    row = evaluate(result)
    row.update({"noise": cell.noise or "gaussian", "variant": cell.variant()})
    if cell.params_label != "frozen":
        row["baseline_id"] = f"{cell.baseline_id}[{cell.params_label}]"
    row["params_label"] = cell.params_label
    row["binding"] = cell.binding
    return row


MAX_CELLS_PER_WORKER = 24


def process_map(fn: Any, items: Sequence[Any], *, workers: int, per_process: int) -> list[Any]:
    """`fn` over `items` in worker processes, none of which runs more than `per_process`."""
    from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

    workers = max(1, workers)
    if per_process == 1:

        def alone(item: Any) -> Any:
            with ProcessPoolExecutor(max_workers=1) as pool:
                return pool.submit(fn, item).result()

        with ThreadPoolExecutor(max_workers=workers) as threads:
            return list(threads.map(alone, items))
    out: list[Any] = []
    for start in range(0, len(items), per_process):
        batch = items[start : start + per_process]
        n = min(workers, len(batch))
        with ProcessPoolExecutor(max_workers=n) as pool:
            out.extend(pool.map(fn, batch, chunksize=-(-len(batch) // n)))
    return out


def run_cells(
    cells: Sequence[Cell], *, workers: int = 1, fresh_process: bool = False
) -> list[dict[str, Any]]:
    """Run every cell."""
    if workers <= 1 and not fresh_process and len(cells) <= MAX_CELLS_PER_WORKER:
        return [run_cell(c) for c in cells]
    per_process = 1 if fresh_process else MAX_CELLS_PER_WORKER
    return process_map(run_cell, list(cells), workers=workers, per_process=per_process)


def compare_rows(rows: Sequence[dict[str, Any]], reference: str = "full") -> list[stats.Comparison]:
    """Every arm against `reference`, per scenario and variant, paired on seed."""
    grouped: dict[tuple[str, str], dict[str, dict[int, dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for row in rows:
        grouped[(row["scenario_id"], row["variant"])][row["baseline_id"]][row["seed"]] = row
    comparisons: list[stats.Comparison] = []
    for (scenario_id, variant), arms in sorted(grouped.items()):
        if reference not in arms:
            continue
        seeds = sorted(arms[reference])
        for arm, by_seed in sorted(arms.items()):
            if arm == reference:
                continue
            paired = [s for s in seeds if s in by_seed]
            for metric in KEY_METRICS:
                ref = [arms[reference][s].get(metric) for s in paired]
                other = [by_seed[s].get(metric) for s in paired]
                if all(v is None for v in ref) and all(v is None for v in other):
                    continue
                comparison = stats.compare(
                    f"{scenario_id}|{variant}|{metric}", arm, other, reference, ref
                )
                comparisons.append(comparison)
    families: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, comparison in enumerate(comparisons):
        families[(comparison.a, comparison.metric.rsplit("|", 1)[-1])].append(index)
    corrected = list(comparisons)
    for indices in families.values():
        family = stats.adjust([comparisons[i] for i in indices])
        for index, adjusted in zip(indices, family, strict=True):
            corrected[index] = adjusted
    return corrected


def summarise(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["scenario_id"], row["variant"], row["baseline_id"])].append(row)
    out = []
    for (scenario_id, variant, arm), group in sorted(grouped.items()):
        entry: dict[str, Any] = {
            "scenario_id": scenario_id,
            "variant": variant,
            "baseline_id": arm,
            "runs": len(group),
        }
        for metric in KEY_METRICS:
            interval = stats.bootstrap_mean([r.get(metric) for r in group], n_boot=2000)
            entry[metric] = None if interval is None else round(interval.estimate, 4)
            entry[f"{metric}_ci"] = (
                None if interval is None else f"[{interval.low:.3f}, {interval.high:.3f}]"
            )
        out.append(entry)
    return out


def manifest(suite: str, seeds: Sequence[int], workers: int) -> dict[str, Any]:
    from importlib.metadata import PackageNotFoundError, version

    from m8_eval_harness.simulator import DEFAULT_CONFIG
    from m9_capability_binder import binder
    from shared.keys import derive, fingerprint, using_development_key
    from shared.run_manifest import config_hash, load_yaml_config

    def git(*args: str) -> str | None:
        try:
            return subprocess.run(
                ["git", *args], capture_output=True, text=True, check=True
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    packages = {}
    for name in ("numpy", "scipy", "scikit-learn", "simpy", "pydantic", "faiss-cpu", "matplotlib"):
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = None
    return {
        "suite": suite,
        "seeds": list(seeds),
        "workers": workers,
        "git_commit": git("rev-parse", "HEAD"),
        "git_dirty": bool(git("status", "--porcelain")),
        "code_dirty": bool(
            git("status", "--porcelain", "--", "*.py", "*.rs", "*.toml", "configs", ":!Docs")
        ),
        "frozen_params": FROZEN.as_dict(),
        "config_hash": config_hash(FROZEN.apply_to_config(load_yaml_config(DEFAULT_CONFIG))),
        "capability_binder": binder.implementation(),
        "development_key": using_development_key(),
        "gt_key_fingerprint": fingerprint(derive("gt-signing")),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "packages": packages,
    }


def write_outputs(
    out_dir: Path, rows: list[dict[str, Any]], suite: str, meta: dict[str, Any]
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "rows.jsonl").open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row, default=str) + "\n")
    summary = summarise(rows)
    _write_csv(out_dir / "summary.csv", summary)
    comparisons = compare_rows(rows)
    _write_csv(
        out_dir / "comparisons.csv",
        [
            {
                **{k: v for k, v in asdict(c).items() if k != "difference"},
                "difference": None if c.difference is None else round(c.difference.estimate, 4),
                "difference_ci": None
                if c.difference is None
                else f"[{c.difference.low:.3f}, {c.difference.high:.3f}]",
            }
            for c in comparisons
        ],
    )
    (out_dir / "manifest.json").write_text(json.dumps(meta, indent=2, default=str))
    _figures(out_dir / "figures", rows, suite)
    _report(out_dir / "report.md", summary, comparisons, meta)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _figures(directory: Path, rows: list[dict[str, Any]], suite: str) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:  # pragma: no cover
        return
    directory.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[
            row["scenario_id"].split(":")[1]
            if row["scenario_id"].startswith("sweep:")
            else row["scenario_id"]
        ][row["baseline_id"]].append(row)

    for metric in ("device_f1", "latency_response_mean", "response_coverage", "availability_cost"):
        scenarios = sorted(
            s for s in grouped if not s.startswith(("lowslow", "campaign", "duty", "scale"))
        )
        if not scenarios:
            continue
        arms = sorted({a for s in scenarios for a in grouped[s]})
        fig, ax = plt.subplots(figsize=(max(6, len(scenarios) * 1.1), 3.2))
        width = 0.8 / max(1, len(arms))
        for i, arm in enumerate(arms):
            means, lows, highs = [], [], []
            for s in scenarios:
                interval = stats.bootstrap_mean(
                    [r.get(metric) for r in grouped[s].get(arm, [])], n_boot=2000
                )
                if interval is None:
                    means.append(float("nan"))
                    lows.append(0.0)
                    highs.append(0.0)
                else:
                    means.append(interval.estimate)
                    lows.append(interval.estimate - interval.low)
                    highs.append(interval.high - interval.estimate)
            ax.bar(
                [x + i * width for x in range(len(scenarios))],
                means,
                width,
                yerr=[lows, highs],
                label=arm,
                capsize=2,
            )
        ax.set_xticks([x + width * (len(arms) - 1) / 2 for x in range(len(scenarios))], scenarios)
        ax.set_ylabel(metric)
        ax.legend(fontsize=7, ncols=min(4, len(arms)))
        fig.tight_layout()
        fig.savefig(directory / f"{suite}_{metric}.png", dpi=160)
        plt.close(fig)

    sweeps = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row["scenario_id"].startswith("sweep:"):
            parts = row["scenario_id"].split(":")
            sweeps[parts[1]][row["baseline_id"]].append(
                (parts[-1] if parts[1] != "duty" else f"{parts[2]}/{parts[3]}", row)
            )
    for kind, arms in sweeps.items():
        fig, ax = plt.subplots(figsize=(5, 3.2))
        metric = (
            "response_coverage"
            if kind == "duty"
            else ("tick_ms_p95" if kind == "scale" else "device_tpr")
        )
        for arm, points in sorted(arms.items()):
            by_x: dict[str, list[float]] = defaultdict(list)
            for x, row in points:
                if row.get(metric) is not None:
                    by_x[x].append(row[metric])
            xs = sorted(
                by_x,
                key=lambda v: (
                    float(v.split("/")[0]) / float(v.split("/")[1]) if "/" in v else float(v)
                ),
            )
            ax.plot(xs, [sum(by_x[x]) / len(by_x[x]) for x in xs], marker="o", label=arm)
        ax.set_xlabel(kind)
        ax.set_ylabel(metric)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(directory / f"sweep_{kind}.png", dpi=160)
        plt.close(fig)


def _report(
    path: Path,
    summary: list[dict[str, Any]],
    comparisons: list[stats.Comparison],
    meta: dict[str, Any],
) -> None:
    lines = [
        f"# Experiment report: `{meta['suite']}`",
        "",
        "Generated from `rows.jsonl`; regenerate, never edit.",
        "",
    ]
    lines += ["## Manifest", "", "```json", json.dumps(meta, indent=2, default=str), "```", ""]
    lines += ["## Means with bootstrap 95% CI", ""]
    headline = (
        "device_tpr",
        "device_fpr",
        "device_f1",
        "latency_response_mean",
        "response_coverage",
        "mttr_mean",
        "false_restriction_rate",
        "disruptive_actions",
    )
    lines.append("| scenario | variant | arm | runs | " + " | ".join(headline) + " |")
    lines.append("|" + "---|" * (4 + len(headline)))
    for entry in summary:
        cells = [
            f"{entry[m]} {entry[m + '_ci'] or ''}".strip() if entry[m] is not None else "-"
            for m in headline
        ]
        lines.append(
            f"| {entry['scenario_id']} | {entry['variant']} | "
            f"{entry['baseline_id']} | {entry['runs']} | " + " | ".join(cells) + " |"
        )
    lines += ["", "## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)", ""]
    lines.append(
        "| comparison | arm | n | mean arm | mean full | difference [95% CI] "
        "| p (Holm) | rank-biserial |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for c in comparisons:
        if c.p_adjusted is None or c.p_adjusted >= 0.05:
            continue
        lines.append(
            f"| {c.metric} | {c.a} | {c.n} | "
            f"{c.mean_a if c.mean_a is None else round(c.mean_a, 3)} | "
            f"{c.mean_b if c.mean_b is None else round(c.mean_b, 3)} | {c.difference} | "
            f"{c.p_adjusted:.2g} | {c.effect_size:+.2f} |"
        )
    lines += [
        "",
        f"Only comparisons significant after Holm correction are listed; "
        f"all {len(comparisons)} are in `comparisons.csv`.",
    ]
    path.write_text("\n".join(lines) + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--suite", required=True)
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--arms",
        nargs="+",
        default=None,
        help="run only these arms' cells and merge their rows into the suite's rows on disk "
        "(replacing any earlier rows of the same arms); every other arm's rows are kept as run",
    )
    parser.add_argument(
        "--reanalyse",
        action="store_true",
        help="rebuild summary, comparisons, figures and report from rows already on disk",
    )
    args = parser.parse_args(argv)
    if args.reanalyse:
        out = args.out or Path("results") / "experiments" / args.suite
        rows = recorded_rows(out)
        meta = json.loads((out / "manifest.json").read_text())
        meta["reanalysed"] = True
        write_outputs(out, rows, args.suite, meta)
        print(f"{len(rows)} rows re-analysed -> {out}")
        return 0
    seeds = HELD_OUT_SEEDS[: args.seeds]
    cells = suite_cells(args.suite, seeds)
    if args.arms:
        cells = [c for c in cells if c.baseline_id in args.arms]
        if not cells:
            raise SystemExit(f"no cell of {args.suite} runs {args.arms}")
    meta = manifest(args.suite, seeds, args.workers)
    rows = run_cells(cells, workers=args.workers, fresh_process=args.suite == "scale")
    out = args.out or Path("results") / "experiments" / args.suite
    if args.arms:
        kept = [r for r in recorded_rows(out) if r["baseline_id"] not in args.arms]
        meta["merged_arms"] = sorted(args.arms)
        meta["merged_into_rows"] = len(kept)
        rows = kept + rows
    write_outputs(out, rows, args.suite, meta)
    print(f"{len(rows)} runs -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
