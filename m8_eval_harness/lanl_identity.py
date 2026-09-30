"""LANL authentication: real evidence for the identity dimension."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "lanl"
REDTEAM = DATA / "redteam.txt.gz"
FEATURES_FILE = DATA / "features.npz"
CALIBRATION_FILE = ROOT / "configs" / "lanl_identity_calibration.json"
RESULTS = ROOT / "results" / "experiments" / "lanl_identity"
DAYS = 30
HOURS = DAYS * 24
WARMUP_HOURS = 36
SAMPLE_BUCKETS = 16
MIN_ACTIVE_DAYS = 10
SPLIT_SEED = 0
FLEETS = 4
FEATURES = (
    "logons",
    "failed",
    "ntlm",
    "new_accounts",
    "new_sources",
    "new_pairs",
    "new_ntlm_pairs",
)
AGGREGATES = ("mean", "max", "top2", "top3")


def auth_path() -> Path:
    found = sorted(DATA.glob("auth*.txt.gz"))
    if len(found) != 1:
        raise SystemExit(f"expected one data/lanl/auth*.txt.gz, found {len(found)}")
    return found[0]


def sampled(name: bytes) -> bool:
    return hashlib.sha256(name).digest()[0] % SAMPLE_BUCKETS == 0


def red_team(path: Path = REDTEAM) -> tuple[dict[bytes, list[int]], set[bytes]]:
    """Destination -> the hours of its red-team logons; and the red team's sources."""
    raw = subprocess.run(["gzip", "-dc", str(path)], capture_output=True, check=True).stdout
    hours: dict[bytes, list[int]] = defaultdict(list)
    sources: set[bytes] = set()
    for line in raw.splitlines():
        t, _user, source, destination = line.split(b",")
        hours[destination].append(int(t) // 3600)
        sources.add(source)
    return {d: sorted(h) for d, h in hours.items()}, sources


def extract(
    auth: Path | None = None, out: Path = FEATURES_FILE, redteam: Path = REDTEAM
) -> dict[str, Any]:
    """Stream the first 30 days once; keep seven counts per device-hour."""
    auth = auth or auth_path()
    attacks, red_sources = red_team(redteam)
    member: dict[bytes, bool] = {}
    counts: dict[bytes, np.ndarray] = {}
    seen: dict[bytes, tuple[set, set, set]] = {}
    end = DAYS * 86400
    events = kept = 0
    gunzip = subprocess.Popen(["gzip", "-dc", str(auth)], stdout=subprocess.PIPE, bufsize=1 << 20)
    assert gunzip.stdout is not None
    try:
        for line in gunzip.stdout:
            fields = line.split(b",")
            t = int(fields[0])
            if t >= end:
                break
            events += 1
            if fields[7] != b"LogOn":
                continue
            destination = fields[4]
            chosen = member.get(destination)
            if chosen is None:
                chosen = destination in attacks or (
                    sampled(destination) and destination not in red_sources
                )
                member[destination] = chosen
            if not chosen:
                continue
            kept += 1
            row = counts.get(destination)
            if row is None:
                row = counts[destination] = np.zeros((HOURS, len(FEATURES)), dtype=np.float32)
                seen[destination] = (set(), set(), set())
            accounts, sources, pairs = seen[destination]
            hour = t // 3600
            account, source = fields[1], fields[3]
            ntlm = fields[5] == b"NTLM"
            new_pair = (account, source) not in pairs
            row[hour, 0] += 1
            row[hour, 1] += fields[8].startswith(b"Fail")
            row[hour, 2] += ntlm
            row[hour, 3] += account not in accounts
            row[hour, 4] += source not in sources
            row[hour, 5] += new_pair
            row[hour, 6] += ntlm and new_pair
            accounts.add(account)
            sources.add(source)
            pairs.add((account, source))
    finally:
        gunzip.kill()
        gunzip.wait()
    names = sorted(
        d
        for d, row in counts.items()
        if int(np.count_nonzero(row[:, 0].reshape(DAYS, 24).sum(axis=1))) >= MIN_ACTIVE_DAYS
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out,
        names=np.array([n.decode() for n in names]),
        counts=np.stack([counts[n] for n in names]),
        attack_hours=np.array([json.dumps(attacks.get(n, [])) for n in names]),
    )
    summary = {
        "events_read": events,
        "logons_kept": kept,
        "devices_seen": len(counts),
        "devices_active": len(names),
        "attacked_active": sum(n in attacks for n in names),
        "red_team_destinations": len(attacks),
    }
    (out.parent / "extract.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


class Devices:
    def __init__(self, path: Path = FEATURES_FILE) -> None:
        data = np.load(path)
        self.names: list[str] = list(data["names"])
        self.counts: np.ndarray = data["counts"]
        self.attack_hours: list[list[int]] = [json.loads(s) for s in data["attack_hours"]]
        self.attacked = np.array([bool(h) for h in self.attack_hours])

    def split(self) -> tuple[np.ndarray, np.ndarray]:
        """Half of each class calibrates; the other half is held out."""
        rng = np.random.default_rng(SPLIT_SEED)
        calibration: list[int] = []
        for label in (True, False):
            index = np.flatnonzero(self.attacked == label)
            rng.shuffle(index)
            calibration.extend(index[: len(index) // 2])
        mask = np.zeros(len(self.names), dtype=bool)
        mask[calibration] = True
        return np.flatnonzero(mask), np.flatnonzero(~mask)

    def rows(self, index: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Scored device-hours: features (log1p), healthy-device mask, attack-hour mask."""
        x, healthy, attack = [], [], []
        for i in index:
            hours = set(self.attack_hours[i])
            for hour in range(WARMUP_HOURS, HOURS):
                x.append(np.log1p(self.counts[i, hour].astype(float)))
                healthy.append(not self.attacked[i])
                attack.append(hour in hours)
        return np.array(x), np.array(healthy), np.array(attack)


def calibrate(out: Path = CALIBRATION_FILE) -> dict[str, Any]:
    from m8_eval_harness.ton_iot_windows import fit_scale
    from m8_eval_harness.ton_iot_windows import sha256 as file_sha256

    devices = Devices()
    calibration, held_out = devices.split()
    x, healthy, attack = devices.rows(calibration)
    fit = healthy | attack
    scale, detail = fit_scale(x[fit], healthy[fit], attack[fit], AGGREGATES)
    benign = scale.disturbance(x[healthy])
    doc = {
        "auth_sha256": file_sha256(auth_path()),
        "redteam_sha256": file_sha256(REDTEAM),
        "split_seed": SPLIT_SEED,
        "features": list(FEATURES),
        "calibration_devices": int(len(calibration)),
        "calibration_attacked": int(devices.attacked[calibration].sum()),
        "held_out_devices": int(len(held_out)),
        "held_out_attacked": int(devices.attacked[held_out].sum()),
        "keep": list(scale.keep),
        "median": list(scale.median),
        "spread": list(scale.spread),
        "aggregate": scale.aggregate,
        "offset": scale.offset,
        "benign_q95": float(np.quantile(benign, 0.95)),
        **detail,
    }
    out.write_text(json.dumps(doc, indent=2) + "\n")
    return doc


def load_scale(doc: dict[str, Any]) -> Any:
    from m8_eval_harness.ton_iot_windows import Scale

    return Scale(
        tuple(doc["keep"]),
        tuple(doc["median"]),
        tuple(doc["spread"]),
        doc["aggregate"],
        doc["offset"],
    )


def hour_table(devices: Devices, held_out: np.ndarray, calibration: np.ndarray, doc: dict) -> dict:
    """Device-hour separation on the held-out half, and an Isolation Forest beside it."""
    from sklearn.ensemble import IsolationForest

    from m8_eval_harness.ton_iot import auc

    scale = load_scale(doc)
    x, healthy, attack = devices.rows(held_out)
    rows = healthy | attack
    raw = scale.raw(x)
    xc, healthy_c, _ = devices.rows(calibration)
    forest = IsolationForest(random_state=0).fit(xc[healthy_c])
    disturbance = scale.disturbance(x)
    return {
        "device_hours": int(rows.sum()),
        "attack_hours": int(attack.sum()),
        "auc": auc(list(raw[rows]), list(attack[rows])),
        "auc_isolation_forest": auc(list(-forest.score_samples(x[rows])), list(attack[rows])),
        "tpr_at_benign_q95": float(np.mean(disturbance[attack] >= doc["benign_q95"])),
        "fpr_at_benign_q95": float(np.mean(disturbance[healthy] >= doc["benign_q95"])),
        "benign_disturbed_share": float(np.mean(disturbance[healthy] > 0)),
    }


def fleets(devices: Devices, held_out: np.ndarray) -> list[np.ndarray]:
    """The held-out devices in `FLEETS` fleets: shuffled once, attacked ones dealt round."""
    rng = np.random.default_rng(SPLIT_SEED + 1)
    out: list[list[int]] = [[] for _ in range(FLEETS)]
    for label in (True, False):
        index = held_out[devices.attacked[held_out] == label]
        rng.shuffle(index)
        for k, i in enumerate(index):
            out[k % FLEETS].append(int(i))
    return [np.array(sorted(f)) for f in out]


def scenario(devices: Devices, held_out: np.ndarray, doc: dict, fleet: int = 0) -> Any:
    """Every device given, one tick per hour after the warm-up."""
    from m1_monitoring.sensors.synthetic import NoiseModel
    from m8_eval_harness.scenarios.base import Anomaly, Scenario

    scale = load_scale(doc)
    ticks = HOURS - WARMUP_HOURS
    order = sorted(held_out, key=lambda i: (not devices.attacked[i], devices.names[i]))
    trace, anomalies, onset = [], [], {}
    for n, i in enumerate(order):
        node = f"node-{n}"
        x = np.log1p(devices.counts[i, WARMUP_HOURS:].astype(float))
        trace.append((node, tuple(round(float(v), 6) for v in scale.disturbance(x))))
        hours = [h - WARMUP_HOURS for h in devices.attack_hours[i] if h >= WARMUP_HOURS]
        for tick in sorted(set(hours)):
            anomalies.append(Anomaly(node, tick, tick + 1, 0.0, ("identity",)))
        if hours:
            onset[node] = min(hours)
    return Scenario(
        scenario_id=f"lanl_identity:fleet{fleet}",
        name="LANL authentication, held-out devices",
        demonstrates="real identity evidence through the closed loop",
        n_nodes=len(order),
        ticks=ticks,
        anomalies=tuple(anomalies),
        ground_truth=onset,
        noise=NoiseModel(kind="replay", trace=tuple(trace), trace_dimension="identity"),
        notes="identity dimension from LANL auth; behaviour, posture, network synthetic",
    )


def arms() -> tuple[str, ...]:
    from m8_eval_harness.ton_iot_windows import arms as host_arms

    return host_arms()


def _cell(job: tuple[str, int, Any]) -> dict[str, Any]:
    import tempfile

    from m8_eval_harness import baselines
    from m8_eval_harness.evaluation import RESPONSE_LEVEL, _series, evaluate
    from m8_eval_harness.scenario_runner import run_scenario

    arm, seed, fleet, scenario = job
    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(scenario, baselines.by_id(arm), seed=seed, results_dir=Path(tmp))
    row = evaluate(result)
    levels, _, _ = _series(result)
    onset = scenario.ground_truth
    after = [
        any(level >= RESPONSE_LEVEL for tick, level in levels[node].items() if tick >= at)
        for node, at in onset.items()
    ]
    healthy = scenario.n_nodes - len(onset)
    row.update(
        {
            "arm": arm,
            "fleet": fleet,
            "attacked_devices": len(onset),
            "detected_after_onset_count": int(sum(after)),
            "detected_after_onset": float(np.mean(after)) if after else None,
            "healthy_devices": healthy,
            "restricted_healthy_count": round((row.get("false_restriction_rate") or 0.0) * healthy),
        }
    )
    return row


METRICS = (
    "device_tpr",
    "detected_after_onset",
    "latency_response_mean",
    "false_restriction_rate",
    "device_fpr",
    "tick_precision",
)


def evaluate_held_out(
    out: Path, seeds: Sequence[int], workers: int, only: Sequence[str] | None = None
) -> dict[str, Any]:
    from m8_eval_harness.experiment import manifest, process_map
    from m8_eval_harness.ton_iot_windows import merged, site_arm
    from m8_eval_harness.ton_iot_windows import sha256 as file_sha256

    doc = json.loads(CALIBRATION_FILE.read_text())
    if file_sha256(REDTEAM) != doc["redteam_sha256"]:
        raise SystemExit("redteam.txt.gz does not match the calibration's SHA-256")
    devices = Devices()
    calibration, held_out = devices.split()
    meta = manifest("lanl_identity", list(seeds), workers)
    worlds = [scenario(devices, f, doc, k) for k, f in enumerate(fleets(devices, held_out))]
    chosen = [site_arm(a, "lanl") for a in (only or arms())]
    jobs = [(arm, seed, k, w) for arm in chosen for seed in seeds for k, w in enumerate(worlds)]
    rows = merged(out, process_map(_cell, jobs, workers=workers, per_process=1), only and chosen)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "rows.jsonl").open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row, default=str) + "\n")
    by_arm: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_arm[row["arm"]].append(row)
    report = {
        "calibration": {
            k: doc[k]
            for k in (
                "aggregate",
                "aggregate_auc",
                "benign_q95",
                "held_out_devices",
                "held_out_attacked",
            )
        },
        "hours": hour_table(devices, held_out, calibration, doc),
        "loop": {
            "devices": sum(w.n_nodes for w in worlds),
            "attacked": sum(len(w.ground_truth) for w in worlds),
            "fleets": [w.n_nodes for w in worlds],
            "ticks": worlds[0].ticks,
            "seeds": list(seeds),
            "by_arm": {arm: _pooled(mine) for arm, mine in by_arm.items()},
        },
        "manifest": meta,
    }
    (out / "summary.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
    (out / "manifest.json").write_text(json.dumps(meta, indent=2, default=str) + "\n")
    return report


def _pooled(rows: Sequence[dict[str, Any]]) -> dict[str, float | None]:
    """Rates over every device of every fleet and seed; latency and precision as means."""
    attacked = sum(r["attacked_devices"] for r in rows)
    healthy = sum(r["healthy_devices"] for r in rows)
    return {
        "detected_after_onset": round(
            sum(r["detected_after_onset_count"] for r in rows) / attacked, 4
        )
        if attacked
        else None,
        "false_restriction_rate": round(
            sum(r["restricted_healthy_count"] for r in rows) / healthy, 4
        )
        if healthy
        else None,
        **{
            m: _mean(rows, m)
            for m in ("device_tpr", "latency_response_mean", "device_fpr", "tick_precision")
        },
    }


def _mean(rows: Sequence[dict[str, Any]], metric: str) -> float | None:
    values = [r[metric] for r in rows if isinstance(r.get(metric), int | float)]
    return round(float(np.mean(values)), 4) if values else None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=("extract", "calibrate", "evaluate"))
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--out", type=Path, default=RESULTS)
    parser.add_argument(
        "--arms", nargs="+", default=None, help="run only these arms, merged into the rows on disk"
    )
    args = parser.parse_args(argv)
    if args.command == "extract":
        print(json.dumps(extract(), indent=1))
    elif args.command == "calibrate":
        doc = calibrate()
        print(
            json.dumps({k: doc[k] for k in ("aggregate", "aggregate_auc", "benign_q95")}, indent=1)
        )
    else:
        from m8_eval_harness.experiment import HELD_OUT_SEEDS

        report = evaluate_held_out(
            args.out, HELD_OUT_SEEDS[: args.seeds], args.workers, only=args.arms
        )
        print(json.dumps({k: report[k] for k in ("hours", "loop")}, indent=1, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
