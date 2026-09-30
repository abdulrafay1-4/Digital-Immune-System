"""TON_IoT: the network dimension, calibrated on real traffic and tested on more of it."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_FILE = ROOT / "configs" / "ton_iot_calibration.json"
DATASET = ROOT / "data" / "ton_iot" / "Train_Test_Network.csv.gz"
WINDOW_SECONDS = 300
FEATURES = ("flows", "failed_share", "dst_ports", "dst_hosts", "mean_src_bytes")
FAILED_STATES = frozenset({"S0", "REJ", "RSTO", "RSTOS0", "RSTR", "RSTRH", "SH", "SHR"})
MIN_ACTIVE_WINDOWS = 20
MAX_DEVICES = 60
REPLAY_ARMS = (
    "full",
    "static_trust",
    "no_sharing",
    "no_memory",
    "binary_response",
    "no_recovery",
    "binary_zt",
    "beta_reputation",
    "isolation_forest",
)


@dataclass
class Window:
    host: str
    index: int
    flows: int = 0
    failed: int = 0
    ports: set[str] = field(default_factory=set)
    hosts: set[str] = field(default_factory=set)
    src_bytes: int = 0
    attacks: Counter[str] = field(default_factory=Counter)

    @property
    def attack(self) -> bool:
        return bool(self.attacks)

    @property
    def attack_type(self) -> str:
        return self.attacks.most_common(1)[0][0] if self.attacks else "normal"

    def features(self) -> np.ndarray:
        return np.array(
            [
                np.log1p(self.flows),
                self.failed / self.flows,
                np.log1p(len(self.ports)),
                np.log1p(len(self.hosts)),
                np.log1p(self.src_bytes / self.flows),
            ]
        )


def open_csv(path: Path) -> Any:
    """A dataset CSV, read as text whether or not it is gzipped."""
    if path.suffix == ".gz":
        return gzip.open(path, "rt", newline="", encoding="utf-8-sig")
    return path.open(newline="", encoding="utf-8-sig")


def sha256(path: Path) -> str:
    """SHA-256 of a dataset CSV's content, so a gzipped copy matches the original."""
    digest = hashlib.sha256()
    with gzip.open(path, "rb") if path.suffix == ".gz" else path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_windows(path: Path) -> list[Window]:
    windows: dict[tuple[str, int], Window] = {}
    with open_csv(path) as fh:
        for row in csv.DictReader(fh):
            key = (row["src_ip"], int(row["ts"]) // WINDOW_SECONDS)
            window = windows.get(key)
            if window is None:
                window = windows[key] = Window(*key)
            window.flows += 1
            window.failed += row["conn_state"] in FAILED_STATES
            window.ports.add(row["dst_port"])
            window.hosts.add(row["dst_ip"])
            window.src_bytes += int(row["src_bytes"] or 0)
            if row["label"] == "1":
                window.attacks[row["type"]] += 1
    return list(windows.values())


def split(windows: Sequence[Window]) -> tuple[list[Window], list[Window], int]:
    """Earlier half of the active time windows calibrates; the later half is held out."""
    active = sorted({w.index for w in windows})
    boundary = active[len(active) // 2]
    return (
        [w for w in windows if w.index < boundary],
        [w for w in windows if w.index >= boundary],
        boundary,
    )


def auc(scores: Sequence[float], labels: Sequence[bool]) -> float:
    """Probability a random attack window outscores a random normal one (ties half)."""
    order = np.argsort(scores, kind="mergesort")
    ranked = np.asarray(scores)[order]
    ranks = np.empty(len(scores))
    i = 0
    while i < len(ranked):
        j = i
        while j + 1 < len(ranked) and ranked[j + 1] == ranked[i]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2 + 1
        i = j + 1
    positive = np.asarray(labels, dtype=bool)
    n_pos, n_neg = int(positive.sum()), int((~positive).sum())
    if not n_pos or not n_neg:
        return float("nan")
    return float((ranks[positive].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


@dataclass(frozen=True)
class Calibration:
    median: tuple[float, ...]
    q99: tuple[float, ...]
    aggregate: str
    offset: float = 0.0

    def feature_scores(self, x: np.ndarray) -> np.ndarray:
        median, q99 = np.array(self.median), np.array(self.q99)
        span = q99 - median
        scaled = np.where(span > 0, (x - median) / np.where(span > 0, span, 1), (x > q99) * 1.0)
        return np.clip(scaled, 0.0, 1.0)

    def raw(self, window: Window) -> float:
        scores = self.feature_scores(window.features())
        return float(scores.max() if self.aggregate == "max" else scores.mean())

    def disturbance(self, window: Window) -> float:
        return float(np.clip((self.raw(window) - self.offset) / (1.0 - self.offset), 0.0, 1.0))

    @classmethod
    def load(cls, path: Path = CALIBRATION_FILE) -> tuple[Calibration, dict[str, Any]]:
        doc = json.loads(path.read_text())
        return cls(tuple(doc["median"]), tuple(doc["q99"]), doc["aggregate"], doc["offset"]), doc


def calibrate(csv_path: Path, out: Path = CALIBRATION_FILE) -> dict[str, Any]:
    windows = load_windows(csv_path)
    calibration_set, held_out, boundary = split(windows)
    normal = np.array([w.features() for w in calibration_set if not w.attack])
    median = tuple(float(v) for v in np.median(normal, axis=0))
    q99 = tuple(float(v) for v in np.quantile(normal, 0.99, axis=0))
    labels = [w.attack for w in calibration_set]
    choices = {}
    for aggregate in ("mean", "max"):
        candidate = Calibration(median, q99, aggregate)
        choices[aggregate] = auc([candidate.raw(w) for w in calibration_set], labels)
    chosen = max(choices, key=lambda k: choices[k])
    unzeroed = Calibration(median, q99, chosen)
    offset = float(np.median([unzeroed.raw(w) for w in calibration_set if not w.attack]))
    frozen = Calibration(median, q99, chosen, offset)
    benign = [frozen.disturbance(w) for w in calibration_set if not w.attack]
    by_type: dict[str, list[float]] = defaultdict(list)
    for w in calibration_set:
        if w.attack:
            by_type[w.attack_type].append(frozen.disturbance(w))
    doc = {
        "dataset": csv_path.name,
        "sha256": sha256(csv_path),
        "window_seconds": WINDOW_SECONDS,
        "split_window_index": boundary,
        "calibration_windows": {"normal": len(benign), "attack": sum(labels)},
        "held_out_windows": {
            "normal": sum(not w.attack for w in held_out),
            "attack": sum(w.attack for w in held_out),
        },
        "features": list(FEATURES),
        "failed_states": sorted(FAILED_STATES),
        "median": median,
        "q99": q99,
        "aggregate": chosen,
        "offset": offset,
        "calibration_auc": choices,
        "thresholds": {
            "q95": float(np.quantile(benign, 0.95)),
            "q99": float(np.quantile(benign, 0.99)),
        },
        "benign_quantiles": [float(v) for v in np.quantile(benign, np.linspace(0, 1, 101))],
        "benign_share_disturbed": float(np.mean(np.array(benign) > 0)),
        "attack_disturbance_median": {k: float(np.median(v)) for k, v in sorted(by_type.items())},
    }
    out.write_text(json.dumps(doc, indent=2) + "\n")
    return doc


def noise_model() -> Any:
    """The `ton_iot` noise model: benign network disturbance from the calibration half."""
    from m1_monitoring.sensors.synthetic import NoiseModel

    _, doc = Calibration.load()
    return NoiseModel(kind="ton_iot", quantiles=tuple(doc["benign_quantiles"]))


def window_table(held_out: Sequence[Window], calibration: Calibration, doc: dict) -> dict:
    scores = [calibration.disturbance(w) for w in held_out]
    labels = [w.attack for w in held_out]
    result: dict[str, Any] = {"windows": len(held_out), "attack_windows": sum(labels)}
    result["auc_disturbance"] = auc([calibration.raw(w) for w in held_out], labels)
    for name, threshold in doc["thresholds"].items():
        flagged = [s >= threshold and s > 0 for s in scores]
        normal = [f for f, a in zip(flagged, labels, strict=True) if not a]
        attack = [f for f, a in zip(flagged, labels, strict=True) if a]
        result[f"tpr_at_{name}"] = float(np.mean(attack)) if attack else float("nan")
        result[f"fpr_at_{name}"] = float(np.mean(normal)) if normal else float("nan")
    per_type: dict[str, dict[str, float]] = {}
    threshold = doc["thresholds"]["q95"]
    for kind in sorted({w.attack_type for w in held_out if w.attack}):
        mine = [s for s, w in zip(scores, held_out, strict=True) if w.attack_type == kind]
        per_type[kind] = {
            "windows": len(mine),
            "median_disturbance": float(np.median(mine)),
            "tpr_at_q95": float(np.mean([s >= threshold and s > 0 for s in mine])),
        }
    result["per_type"] = per_type
    return result


def isolation_forest_auc(
    calibration_set: Sequence[Window], held_out: Sequence[Window], seed: int = 0
) -> float:
    """A standard unsupervised detector on the same features, trained on normal windows."""
    from sklearn.ensemble import IsolationForest

    normal = np.array([w.features() for w in calibration_set if not w.attack])
    model = IsolationForest(random_state=seed).fit(normal)
    scores = -model.score_samples(np.array([w.features() for w in held_out]))
    return auc(list(scores), [w.attack for w in held_out])


def replay_scenario(held_out: Sequence[Window], calibration: Calibration) -> tuple[Any, dict]:
    from m1_monitoring.sensors.synthetic import NoiseModel
    from m8_eval_harness.scenarios.base import Anomaly, Scenario

    ticks_of = {index: tick for tick, index in enumerate(sorted({w.index for w in held_out}))}
    by_host: dict[str, list[Window]] = defaultdict(list)
    for w in held_out:
        by_host[w.host].append(w)
    eligible = [
        h for h, ws in by_host.items() if len(ws) >= MIN_ACTIVE_WINDOWS or any(w.attack for w in ws)
    ]
    eligible.sort(key=lambda h: (not any(w.attack for w in by_host[h]), -len(by_host[h]), h))
    hosts = sorted(eligible[:MAX_DEVICES])
    node_of = {h: f"node-{i}" for i, h in enumerate(hosts)}
    ticks = len(ticks_of)
    trace, anomalies, onset = [], [], {}
    for host in hosts:
        series = [0.0] * ticks
        for w in by_host[host]:
            tick = ticks_of[w.index]
            series[tick] = round(calibration.disturbance(w), 6)
            if w.attack:
                anomalies.append(Anomaly(node_of[host], tick, tick + 1, 0.0, ("network",)))
                onset[node_of[host]] = min(onset.get(node_of[host], tick), tick)
        trace.append((node_of[host], tuple(series)))
    scenario = Scenario(
        scenario_id="ton_iot_replay",
        name="TON_IoT held-out replay",
        demonstrates="real network traffic through the closed loop",
        n_nodes=len(hosts),
        ticks=ticks,
        anomalies=tuple(anomalies),
        ground_truth=onset,
        noise=NoiseModel(kind="replay", trace=tuple(trace)),
        notes="network dimension replayed from TON_IoT; other dimensions synthetic",
    )
    devices = {
        node_of[h]: {
            "host": h,
            "active_windows": len(by_host[h]),
            "attack_windows": sum(w.attack for w in by_host[h]),
            "attack_types": dict(sum((w.attacks for w in by_host[h]), Counter())),
        }
        for h in hosts
    }
    return scenario, devices


def _replay_cell(args: tuple[Any, str, int]) -> dict[str, Any]:
    import tempfile

    from m8_eval_harness import baselines
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario

    scenario, arm, seed = args
    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(scenario, baselines.by_id(arm), seed=seed, results_dir=Path(tmp))
    return evaluate(result)


def evaluate_held_out(csv_path: Path, out: Path, seeds: Sequence[int], workers: int) -> dict:
    from m8_eval_harness.experiment import MAX_CELLS_PER_WORKER, process_map

    calibration, doc = Calibration.load()
    if sha256(csv_path) != doc["sha256"]:
        raise SystemExit("dataset does not match the calibration's SHA-256")
    windows = load_windows(csv_path)
    calibration_set, held_out, _ = split(windows)
    table = window_table(held_out, calibration, doc)
    table["auc_isolation_forest"] = isolation_forest_auc(calibration_set, held_out)
    scenario, devices = replay_scenario(held_out, calibration)
    cells = [(scenario, arm, seed) for arm in REPLAY_ARMS for seed in seeds]
    rows = process_map(_replay_cell, cells, workers=workers, per_process=MAX_CELLS_PER_WORKER)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "rows.jsonl").open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row, default=str) + "\n")
    summary = _summarise(rows)
    report = {
        "calibration": {
            k: doc[k] for k in ("sha256", "aggregate", "calibration_auc", "thresholds")
        },
        "windows": table,
        "replay": {
            "devices": len(devices),
            "compromised": sorted(scenario.compromised),
            "ticks": scenario.ticks,
            "seeds": list(seeds),
            "by_arm": summary,
        },
        "device_map": devices,
    }
    (out / "summary.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
    (out / "report.md").write_text(_markdown(report))
    return report


REPORTED = (
    "device_tpr",
    "device_fpr",
    "tick_precision",
    "tick_recall",
    "response_coverage",
    "latency_response_mean",
    "false_restriction_rate",
    "availability_cost",
    "containment_rate",
)


def _summarise(rows: Sequence[dict[str, Any]]) -> dict[str, dict[str, float | None]]:
    by_arm: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_arm[row["baseline_id"]].append(row)
    out: dict[str, dict[str, float | None]] = {}
    for arm in REPLAY_ARMS:
        stats: dict[str, float | None] = {}
        for metric in REPORTED:
            values = [r[metric] for r in by_arm[arm] if isinstance(r.get(metric), int | float)]
            stats[metric] = round(statistics.fmean(values), 4) if values else None
        out[arm] = stats
    return out


def _markdown(report: dict[str, Any]) -> str:
    w, r = report["windows"], report["replay"]
    lines = [
        "# TON_IoT held-out results",
        "",
        f"Calibration: aggregate `{report['calibration']['aggregate']}`, "
        f"calibration AUC {report['calibration']['calibration_auc']}, "
        f"dataset SHA-256 `{report['calibration']['sha256'][:16]}...`.",
        "",
        "## Window level (held-out half)",
        "",
        f"{w['windows']} windows, {w['attack_windows']} with attack traffic. "
        f"AUC of network disturbance **{w['auc_disturbance']:.3f}**; "
        f"Isolation Forest on the same features {w['auc_isolation_forest']:.3f}.",
        "",
        "| Threshold (benign calibration quantile) | Detection | False alarm |",
        "|---|---:|---:|",
    ]
    for q in ("q95", "q99"):
        lines.append(f"| {q} | {w[f'tpr_at_{q}']:.3f} | {w[f'fpr_at_{q}']:.3f} |")
    lines += [
        "",
        "| Attack type | Windows | Median disturbance | Detection at q95 |",
        "|---|---:|---:|---:|",
    ]
    for kind, v in w["per_type"].items():
        lines.append(
            f"| {kind} | {v['windows']} | {v['median_disturbance']:.3f} | {v['tpr_at_q95']:.3f} |"
        )
    lines += [
        "",
        "## Devices replayed through the closed loop",
        "",
        f"{r['devices']} hosts, {len(r['compromised'])} of them attackers, {r['ticks']} ticks "
        f"(one per active 5-minute window), seeds {r['seeds'][0]}--{r['seeds'][-1]}. "
        "Network dimension from the capture; identity, behaviour and device synthetic and healthy.",
        "",
        "| Arm | " + " | ".join(REPORTED) + " |",
        "|---|" + "---:|" * len(REPORTED),
    ]
    for arm, stats in r["by_arm"].items():
        cells = ["-" if stats[m] is None else f"{stats[m]:.3f}" for m in REPORTED]
        lines.append(f"| {arm} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


PROFILE_WEIGHTS = (0.25, 0.4, 0.55, 0.7, 0.85, 1.0)
PROFILE_SEEDS = (7000, 7001, 7002)
PROFILE_MAX_FPR = 0.05


def profile_params(w_network: float) -> Any:
    from dataclasses import replace

    from m8_eval_harness.params import FROZEN

    rest = (1.0 - w_network) / 3
    return replace(FROZEN, obs_weights=(rest, rest, rest, w_network))


def _profile_cell(args: tuple[Any, float, int]) -> dict[str, Any]:
    import tempfile

    from m8_eval_harness import baselines
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario

    scenario, w_network, seed = args
    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(
            scenario,
            baselines.by_id("full"),
            seed=seed,
            results_dir=Path(tmp),
            params=profile_params(w_network),
        )
    row = evaluate(result)
    return {"w_network": w_network, "seed": seed, **{m: row.get(m) for m in REPORTED}}


def _run_profiles(scenario: Any, weights: Sequence[float], seeds: Sequence[int], workers: int):
    from m8_eval_harness.experiment import process_map

    cells = [(scenario, w, seed) for w in weights for seed in seeds]
    return process_map(_profile_cell, cells, workers=workers, per_process=4)


def _mean_of(rows: Sequence[dict[str, Any]], metric: str) -> float:
    values = [r[metric] for r in rows if isinstance(r.get(metric), int | float)]
    return statistics.fmean(values) if values else 0.0


def network_profile(csv_path: Path, out: Path, held_out_seeds: Sequence[int], workers: int) -> dict:
    """Choose a network-weighted observation profile on the calibration half; test it."""
    calibration, doc = Calibration.load()
    if sha256(csv_path) != doc["sha256"]:
        raise SystemExit("dataset does not match the calibration's SHA-256")
    calibration_set, held_out, _ = split(load_windows(csv_path))
    choose_on, _ = replay_scenario(calibration_set, calibration)
    rows = _run_profiles(choose_on, PROFILE_WEIGHTS, PROFILE_SEEDS, workers)
    scores = {}
    for w in PROFILE_WEIGHTS:
        mine = [r for r in rows if r["w_network"] == w]
        tpr, fpr = _mean_of(mine, "device_tpr"), _mean_of(mine, "device_fpr")
        scores[w] = {"tpr": tpr, "fpr": fpr, "score": tpr - fpr, "feasible": fpr <= PROFILE_MAX_FPR}
    feasible = [w for w in PROFILE_WEIGHTS if scores[w]["feasible"]] or [PROFILE_WEIGHTS[0]]
    chosen = max(feasible, key=lambda w: (round(scores[w]["score"], 9), -w))
    test_on, _ = replay_scenario(held_out, calibration)
    tested = _run_profiles(test_on, sorted({0.25, chosen}), held_out_seeds, workers)
    report = {
        "chosen_w_network": chosen,
        "calibration": {
            "devices": choose_on.n_nodes,
            "attackers": len(choose_on.compromised),
            "seeds": list(PROFILE_SEEDS),
            "scores": {str(w): v for w, v in scores.items()},
        },
        "held_out": {
            "devices": test_on.n_nodes,
            "attackers": len(test_on.compromised),
            "seeds": list(held_out_seeds),
            "by_weight": {
                str(w): {
                    m: round(_mean_of([r for r in tested if r["w_network"] == w], m), 4)
                    for m in REPORTED
                }
                for w in sorted({0.25, chosen})
            },
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "network_profile.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=("calibrate", "evaluate", "profile"))
    parser.add_argument("--csv", type=Path, default=DATASET)
    parser.add_argument("--out", type=Path, default=Path("results/experiments/ton_iot"))
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args(argv)
    if args.command == "calibrate":
        doc = calibrate(args.csv)
        print(json.dumps({k: doc[k] for k in ("aggregate", "calibration_auc", "thresholds")}))
        return 0
    from m8_eval_harness.experiment import HELD_OUT_SEEDS

    if args.command == "profile":
        result = network_profile(args.csv, args.out, HELD_OUT_SEEDS[: args.seeds], args.workers)
        print(json.dumps(result, indent=2))
        return 0
    report = evaluate_held_out(args.csv, args.out, HELD_OUT_SEEDS[: args.seeds], args.workers)
    print(json.dumps(report["windows"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
