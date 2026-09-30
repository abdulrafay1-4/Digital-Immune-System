"""TON_IoT Windows host counters: real evidence for the behaviour, device and network dimensions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MACHINES = {
    "windows7": ROOT / "data" / "ton_iot" / "Train_Test_Windows_7.csv.gz",
    "windows10": ROOT / "data" / "ton_iot" / "Train_Test_Windows_10.csv.gz",
}
GROUPS = ("behavioral", "device", "network")
AGGREGATES = ("mean", "max", "top3", "top5", "top10pct")


@dataclass(frozen=True)
class Mapping:
    """Which counter groups drive which dimensions, and how counters may combine."""

    name: str
    groups: tuple[str, ...]
    aggregates: tuple[str, ...]
    calibration_file: Path
    results: str


MAPPINGS = {
    "first": Mapping(
        "first",
        ("behavioral", "device"),
        ("mean", "max"),
        ROOT / "configs" / "ton_iot_windows_calibration.json",
        "ton_iot_windows",
    ),
    "revised": Mapping(
        "revised",
        GROUPS,
        AGGREGATES,
        ROOT / "configs" / "ton_iot_windows_calibration_revised.json",
        "ton_iot_windows_revised",
    ),
}
PRIMARY = MAPPINGS["first"]
CALIBRATION_FILE = PRIMARY.calibration_file
SPLIT_SEED = 0
MIN_RECORDS = 20
N_NODES, TICKS, ATTACKED, ONSET, END = 50, 60, 10, 15, 45


def group_of(column: str) -> str | None:
    """Behaviour: per-process activity."""
    if column.startswith("Process") and not column.startswith("Processor"):
        return "behavioral"
    if column.startswith(("Processor", "Memory")) or "Disk" in column:
        return "device"
    if column.startswith("Network_I"):
        return "network"
    return None


@dataclass(frozen=True)
class Records:
    columns: dict[str, list[str]]
    x: dict[str, np.ndarray]
    kind: np.ndarray

    def take(self, index: np.ndarray) -> Records:
        return Records(self.columns, {g: v[index] for g, v in self.x.items()}, self.kind[index])


def load(path: Path) -> Records:
    from m8_eval_harness.ton_iot import open_csv

    with open_csv(path) as fh:
        reader = csv.reader(fh)
        header = next(reader)
        rows = list(reader)
    kind = np.array([r[header.index("type")] for r in rows])

    def number(value: str) -> float:
        try:
            return float(value)
        except ValueError:
            return float("nan")

    columns: dict[str, list[str]] = {g: [] for g in GROUPS}
    x: dict[str, np.ndarray] = {}
    for group in GROUPS:
        index = [i for i, c in enumerate(header) if group_of(c) == group]
        columns[group] = [header[i] for i in index]
        x[group] = np.array([[number(r[i]) for i in index] for r in rows], dtype=float)
    return Records(columns, x, kind)


def split(records: Records) -> tuple[Records, Records]:
    """Half of every class calibrates; the other half is held out."""
    rng = np.random.default_rng(SPLIT_SEED)
    calibration: list[int] = []
    for label in sorted(set(records.kind)):
        index = np.flatnonzero(records.kind == label)
        rng.shuffle(index)
        calibration.extend(index[: len(index) // 2])
    mask = np.zeros(len(records.kind), dtype=bool)
    mask[calibration] = True
    return records.take(np.flatnonzero(mask)), records.take(np.flatnonzero(~mask))


def auc(scores: Sequence[float], labels: Sequence[bool]) -> float:
    from m8_eval_harness.ton_iot import auc as ranked_auc

    return ranked_auc(scores, labels)


@dataclass(frozen=True)
class Scale:
    """One dimension's frozen scoring: per-counter median and deviation scale."""

    keep: tuple[int, ...]
    median: tuple[float, ...]
    spread: tuple[float, ...]
    aggregate: str
    offset: float = 0.0

    def raw(self, x: np.ndarray) -> np.ndarray:
        values = x[:, list(self.keep)]
        values = np.where(np.isnan(values), np.array(self.median), values)
        scores = np.clip(np.abs(values - np.array(self.median)) / np.array(self.spread), 0, 1)
        if self.aggregate == "max":
            return scores.max(axis=1)
        if self.aggregate.startswith("top"):
            k = (
                max(1, scores.shape[1] // 10)
                if self.aggregate == "top10pct"
                else int(self.aggregate[3:])
            )
            return np.sort(scores, axis=1)[:, ::-1][:, :k].mean(axis=1)
        return scores.mean(axis=1)

    def disturbance(self, x: np.ndarray) -> np.ndarray:
        return np.clip((self.raw(x) - self.offset) / (1.0 - self.offset), 0.0, 1.0)


def fit_scale(
    x: np.ndarray,
    normal: np.ndarray,
    attack: np.ndarray,
    aggregates: Sequence[str] = PRIMARY.aggregates,
) -> tuple[Scale, dict]:
    base = x[normal]
    median = np.nanmedian(base, axis=0)
    spread = np.nanquantile(np.abs(base - median), 0.99, axis=0)
    keep = tuple(int(i) for i in np.flatnonzero(np.isfinite(spread) & (spread > 0)))
    choices, saturated = {}, {}
    for aggregate in aggregates:
        candidate = Scale(keep, tuple(median[list(keep)]), tuple(spread[list(keep)]), aggregate)
        scores = candidate.raw(x)
        choices[aggregate] = auc(list(scores), list(attack))
        saturated[aggregate] = bool(np.quantile(candidate.raw(base), 0.95) >= 1.0)
    usable = [a for a in choices if not saturated[a]] or ["mean"]
    chosen = max(usable, key=lambda k: choices[k])
    unzeroed = Scale(keep, tuple(median[list(keep)]), tuple(spread[list(keep)]), chosen)
    offset = float(np.median(unzeroed.raw(base)))
    scale = Scale(unzeroed.keep, unzeroed.median, unzeroed.spread, chosen, offset)
    return scale, {"aggregate_auc": choices, "saturated": saturated, "counters_kept": len(keep)}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def calibrate(mapping: Mapping = PRIMARY, out: Path | None = None) -> dict[str, Any]:
    doc: dict[str, Any] = {"split_seed": SPLIT_SEED, "machines": {}}
    from m8_eval_harness.ton_iot import sha256 as csv_sha256

    for machine, path in MACHINES.items():
        calibration, held_out = split(load(path))
        normal = calibration.kind == "normal"
        entry: dict[str, Any] = {
            "file": path.name.removesuffix(".gz"),
            "sha256": csv_sha256(path),
            "calibration": dict(Counter(calibration.kind)),
            "held_out": dict(Counter(held_out.kind)),
            "groups": {},
        }
        for group in mapping.groups:
            scale, fit = fit_scale(calibration.x[group], normal, ~normal, mapping.aggregates)
            benign = scale.disturbance(calibration.x[group][normal])
            entry["groups"][group] = {
                "counters": calibration.columns[group],
                "keep": list(scale.keep),
                "median": list(scale.median),
                "spread": list(scale.spread),
                "aggregate": scale.aggregate,
                "offset": scale.offset,
                "benign_q95": float(np.quantile(benign, 0.95)),
                **fit,
            }
        doc["machines"][machine] = entry
    (out or mapping.calibration_file).write_text(json.dumps(doc, indent=2) + "\n")
    return doc


def load_scales(machine: str, doc: dict[str, Any]) -> dict[str, Scale]:
    """Every group the calibration file carries: the mapping is in the file."""
    groups = doc["machines"][machine]["groups"]
    return {
        g: Scale(
            tuple(groups[g]["keep"]),
            tuple(groups[g]["median"]),
            tuple(groups[g]["spread"]),
            groups[g]["aggregate"],
            groups[g]["offset"],
        )
        for g in GROUPS
        if g in groups
    }


def record_table(held_out: Records, calibration: Records, scales: dict[str, Scale]) -> dict:
    """Record-level separation, and an Isolation Forest on the same counters."""
    from sklearn.ensemble import IsolationForest

    groups = tuple(scales)
    attack = held_out.kind != "normal"
    disturbance = {g: scales[g].disturbance(held_out.x[g]) for g in groups}
    combined = sum(disturbance[g] for g in groups) / len(groups)
    raw = {g: scales[g].raw(held_out.x[g]) for g in groups}
    normal = calibration.kind == "normal"
    benign_combined = sum(scales[g].disturbance(calibration.x[g][normal]) for g in groups) / len(
        groups
    )
    threshold = float(np.quantile(benign_combined, 0.95))

    def features(records: Records) -> np.ndarray:
        parts = [np.nan_to_num(records.x[g][:, list(scales[g].keep)], nan=0.0) for g in groups]
        return np.hstack(parts)

    forest = IsolationForest(random_state=0).fit(
        features(calibration)[calibration.kind == "normal"]
    )
    table: dict[str, Any] = {
        "records": int(len(attack)),
        "attack_records": int(attack.sum()),
        **{f"auc_{g}": auc(list(raw[g]), list(attack)) for g in groups},
        "auc_combined": auc(list(sum(raw[g] for g in groups)), list(attack)),
        "auc_isolation_forest": auc(list(-forest.score_samples(features(held_out))), list(attack)),
        "benign_q95_combined": threshold,
        "fpr_at_q95": float(np.mean(combined[~attack] >= threshold)),
        "benign_disturbed_share": float(np.mean(combined[~attack] > 0)),
        "per_type": {},
    }
    for kind in sorted(set(held_out.kind) - {"normal"}):
        mine = held_out.kind == kind
        table["per_type"][kind] = {
            "records": int(mine.sum()),
            "median_disturbance": float(np.median(combined[mine])),
            "tpr_at_q95": float(np.mean(combined[mine] >= threshold)),
        }
    return table


def scenario_for(
    machine: str, kind: str, held_out: Records, scales: dict[str, Scale], seed: int
) -> Any:
    """50 devices, 60 ticks; ten run `kind` from tick 15 to 45, every other record is normal."""
    from m1_monitoring.sensors.synthetic import NoiseModel
    from m8_eval_harness.scenarios.base import Anomaly, Scenario

    groups = tuple(scales)
    pairs = np.stack([scales[g].disturbance(held_out.x[g]) for g in groups], axis=1)
    normal = np.flatnonzero(held_out.kind == "normal")
    attack = np.flatnonzero(held_out.kind == kind)
    rng = np.random.default_rng([seed, sum(map(ord, machine)), sum(map(ord, kind))])
    trace = []
    for n in range(N_NODES):
        compromised = n < ATTACKED
        picks = [
            rng.choice(attack) if compromised and ONSET <= t < END else rng.choice(normal)
            for t in range(TICKS)
        ]
        rows = tuple(tuple(round(float(v), 6) for v in row) for row in pairs[picks])
        trace.append((f"node-{n}", rows))
    victims = [f"node-{n}" for n in range(ATTACKED)]
    return Scenario(
        scenario_id=f"windows:{machine}:{kind}",
        name=f"{machine} host counters, {kind}",
        demonstrates=f"real host evidence for the {', '.join(groups)} dimensions",
        n_nodes=N_NODES,
        ticks=TICKS,
        anomalies=tuple(Anomaly(v, ONSET, END, 0.0, groups) for v in victims),
        ground_truth=dict.fromkeys(victims, ONSET),
        noise=NoiseModel(kind="host_replay", host_trace=tuple(trace)),
        seed=seed,
        notes=f"{', '.join(groups)} dimensions from TON_IoT Windows records",
    )


SITE_TOLERANCE = "tolerance@site"


def site_arm(arm: str, site: str) -> str:
    """`tolerance@site` resolved to the dataset being evaluated; any other arm unchanged."""
    return f"tolerance@{site}" if arm == SITE_TOLERANCE else arm


def arms() -> tuple[str, ...]:
    from m8_eval_harness.baseline_fit import fitted

    return (
        "full",
        fitted("binary_zt"),
        fitted("cusum"),
        fitted("page_cusum"),
        "tolerance",
        SITE_TOLERANCE,
        "stopping_response",
        fitted("isolation_forest"),
    )


def _cell(job: tuple[str, str, str, int, Any]) -> dict[str, Any]:
    import tempfile

    from m8_eval_harness import baselines
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario

    machine, kind, arm, seed, scenario = job
    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(scenario, baselines.by_id(arm), seed=seed, results_dir=Path(tmp))
    row = evaluate(result)
    row.update({"machine": machine, "attack_type": kind, "arm": arm})
    return row


def evaluate_held_out(
    out: Path,
    seeds: Sequence[int],
    workers: int,
    mapping: Mapping = PRIMARY,
    only: Sequence[str] | None = None,
) -> dict[str, Any]:
    from m8_eval_harness.experiment import MAX_CELLS_PER_WORKER, manifest, process_map

    doc = json.loads(mapping.calibration_file.read_text())
    meta = manifest(mapping.results, list(seeds), workers)
    meta["mapping"] = mapping.name
    report: dict[str, Any] = {"records": {}, "loop": {}}
    jobs = []
    from m8_eval_harness.ton_iot import sha256 as csv_sha256

    for machine, path in MACHINES.items():
        if csv_sha256(path) != doc["machines"][machine]["sha256"]:
            raise SystemExit(f"{path.name} does not match the calibration's SHA-256")
        calibration, held_out = split(load(path))
        scales = load_scales(machine, doc)
        report["records"][machine] = record_table(held_out, calibration, scales)
        kinds = [k for k, n in Counter(held_out.kind).items() if k != "normal" and n >= MIN_RECORDS]
        for kind in sorted(kinds):
            for seed in seeds:
                scenario = scenario_for(machine, kind, held_out, scales, seed)
                jobs += [
                    (machine, kind, site_arm(arm, f"{machine}-{mapping.name}"), seed, scenario)
                    for arm in (only or arms())
                ]
    rows = process_map(_cell, jobs, workers=workers, per_process=MAX_CELLS_PER_WORKER)
    rows = merged(
        out,
        rows,
        only and [site_arm(a, f"{m}-{mapping.name}") for a in only for m in MACHINES],
    )
    out.mkdir(parents=True, exist_ok=True)
    with (out / "rows.jsonl").open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row, default=str) + "\n")
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["machine"], row["attack_type"], row["arm"])].append(row)
    for (machine, kind, arm), mine in sorted(grouped.items()):
        report["loop"].setdefault(machine, {}).setdefault(kind, {})[arm] = {
            metric: _mean(mine, metric)
            for metric in (
                "device_tpr",
                "response_coverage",
                "latency_response_mean",
                "false_restriction_rate",
                "benign_worst_level",
            )
        }
    report["manifest"] = meta
    (out / "summary.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
    (out / "manifest.json").write_text(json.dumps(meta, indent=2, default=str) + "\n")
    return report


def merged(
    out: Path, rows: list[dict[str, Any]], only: Sequence[str] | None
) -> list[dict[str, Any]]:
    """`rows` for the arms just run, beside every other arm's rows as they were run."""
    if not only:
        return rows
    from m8_eval_harness.experiment import recorded_rows

    return [r for r in recorded_rows(out) if r["arm"] not in only] + rows


def _mean(rows: Sequence[dict[str, Any]], metric: str) -> float | None:
    values = [r[metric] for r in rows if isinstance(r.get(metric), int | float)]
    return round(float(np.mean(values)), 4) if values else None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=("calibrate", "evaluate"))
    parser.add_argument("--mapping", choices=sorted(MAPPINGS), default=PRIMARY.name)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument(
        "--arms", nargs="+", default=None, help="run only these arms, merged into the rows on disk"
    )
    args = parser.parse_args(argv)
    mapping = MAPPINGS[args.mapping]
    if args.command == "calibrate":
        doc = calibrate(mapping)
        for machine, entry in doc["machines"].items():
            print(machine, {g: v["aggregate_auc"] for g, v in entry["groups"].items()})
        return 0
    from m8_eval_harness.experiment import HELD_OUT_SEEDS

    out = args.out or Path("results") / "experiments" / mapping.results
    report = evaluate_held_out(
        out, HELD_OUT_SEEDS[: args.seeds], args.workers, mapping, only=args.arms
    )
    print(json.dumps(report["records"], indent=1, default=str)[:3000])
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
