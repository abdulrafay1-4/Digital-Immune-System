"""Re-run recorded runs with this code and check each one matches its recorded row exactly."""

from __future__ import annotations

import argparse
import gzip
import json
import math
import random
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RESULTS = ROOT / "results" / "experiments"

GRID = (
    "fyp",
    "contributions",
    "external",
    "adaptive",
    "resilience",
    "robustness",
    "noise",
    "operators",
    "adjudication",
    "sweeps",
    "sensitivity",
    "registration",
    "research",
    "ablations",
    "fairness",
    "scale",
    "llm",
)
REAL = ("ton_iot", "ton_iot_windows", "ton_iot_windows_revised", "lanl_identity")
SECURITY = (
    "quorum",
    "mcp",
    "trusted",
    "device",
    "compromised",
    "compromised_patient",
    "compromised_patient_attested",
    "overhead",
)
MEASURED = {
    "cpu_seconds",
    "wall_seconds",
    "rss_mb",
    "rss_mb_delta",
    "tick_ms_p50",
    "tick_ms_p95",
    "tick_ms_mean",
    "memory_read_ms_p50",
    "memory_write_ms_p50",
    "events_per_second",
    "seconds",
    "ms_per_tick",
}


def recorded(suite: str) -> list[dict[str, Any]]:
    with gzip.open(RESULTS / suite / "rows.jsonl.gz", "rt") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def measured(key: str) -> bool:
    return key in MEASURED or "_ms" in key or key.endswith(("_seconds", "_mb"))


def differences(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    out = []
    for key, value in old.items():
        if measured(key):
            continue
        other = new.get(key)
        if isinstance(value, float) and isinstance(other, int | float):
            if not math.isclose(value, other, rel_tol=1e-9, abs_tol=1e-12):
                out.append(f"{key}: recorded {value!r}, now {other!r}")
        elif value != other:
            out.append(f"{key}: recorded {value!r}, now {other!r}")
    return out


def grid_rerun(row: dict[str, Any]) -> dict[str, Any]:
    from m8_eval_harness.experiment import Cell, run_cell

    label = row.get("params_label", "frozen")
    arm = row["baseline_id"].rsplit("[", 1)[0] if label != "frozen" else row["baseline_id"]
    cell = Cell(
        scenario_id=row["scenario_id"],
        baseline_id=arm,
        seed=row["seed"],
        operator=row["operator"],
        adjudication=row["adjudication"],
        noise=None if row["noise"] == "gaussian" else row["noise"],
        params_label=label,
        binding=row.get("binding", "provisioned"),
    )
    return run_cell(cell)


def windows_rerun(suite: str, row: dict[str, Any]) -> dict[str, Any]:
    from m8_eval_harness import ton_iot_windows as w

    mapping = w.MAPPINGS["revised" if suite.endswith("revised") else "first"]
    doc = json.loads(mapping.calibration_file.read_text())
    machine = row["machine"]
    _, held_out = w.split(w.load(w.MACHINES[machine]))
    scales = w.load_scales(machine, doc)
    scenario = w.scenario_for(machine, row["attack_type"], held_out, scales, row["seed"])
    return w._cell((machine, row["attack_type"], row["arm"], row["seed"], scenario))


def lanl_rerun(row: dict[str, Any]) -> dict[str, Any]:
    from m8_eval_harness import lanl_identity as lanl

    doc = json.loads(lanl.CALIBRATION_FILE.read_text())
    devices = lanl.Devices()
    _, held_out = devices.split()
    fleet = lanl.fleets(devices, held_out)[row["fleet"]]
    scenario = lanl.scenario(devices, fleet, doc, row["fleet"])
    return lanl._cell((row["arm"], row["seed"], row["fleet"], scenario))


def ton_iot_rerun(row: dict[str, Any]) -> dict[str, Any]:
    from m8_eval_harness import ton_iot

    calibration, _ = ton_iot.Calibration.load()
    _, held_out, _ = ton_iot.split(ton_iot.load_windows(ton_iot.DATASET))
    scenario, _ = ton_iot.replay_scenario(held_out, calibration)
    return ton_iot._replay_cell((scenario, row["baseline_id"], row["seed"]))


def sampled(suite: str, rows: list[dict[str, Any]], sample: int, rng: random.Random) -> int:
    checked = failed = 0
    for row in rng.sample(rows, min(sample, len(rows))):
        start = time.perf_counter()
        if suite in GRID:
            new = grid_rerun(row)
        elif suite == "ton_iot":
            new = ton_iot_rerun(row)
        elif suite == "lanl_identity":
            new = lanl_rerun(row)
        else:
            new = windows_rerun(suite, row)
        diff = differences(row, new)
        checked += 1
        failed += bool(diff)
        what = row.get("scenario_id"), row.get("baseline_id", row.get("arm")), row.get("seed")
        status = "MISMATCH" if diff else "match"
        print(f"  {status:8} {what}  ({time.perf_counter() - start:.1f} s)")
        for line in diff[:8]:
            print(f"           {line}")
    return failed


def container_twin() -> int:
    from m8_eval_harness.container_twin import SCENARIOS, outcome, run_simulator
    from m8_eval_harness.scenarios.catalogue import by_id

    failed = 0
    twin = ROOT / "results" / "container_twin"
    for scenario_id in SCENARIOS:
        old = json.loads((twin / f"{scenario_id}.json").read_text())
        scenario = by_id(scenario_id)
        sim = run_simulator(scenario)
        cells = sum(len(levels) for levels in sim["levels"].values())
        diff = differences(old["simulator"], outcome(scenario, sim["levels"]))
        diff += differences(old["adversary_simulator"] or {}, sim["adversary"] or {})
        if cells != old["proposed"]["device_ticks"]:
            diff.append(f"device-ticks: recorded {old['proposed']['device_ticks']}, now {cells}")
        failed += bool(diff)
        print(f"  {'MISMATCH' if diff else 'match':8} {scenario_id}: {cells} device-ticks")
        for line in diff:
            print(f"           {line}")
    return failed


def security(suite: str) -> int:
    from m8_eval_harness.security_experiments import EXPERIMENTS

    run = EXPERIMENTS[suite][0]
    start = time.perf_counter()
    new = {key(r): r for r in json.loads(json.dumps(run(), default=str))}
    old = recorded(suite)
    failed = 0
    for row in old:
        diff = differences(row, new[key(row)]) if key(row) in new else ["not produced by this run"]
        failed += bool(diff)
        for line in diff[:4]:
            print(f"  MISMATCH {key(row)}: {line}")
    status = "all recorded rows match" if not failed else f"{failed} recorded rows differ"
    print(f"  {status}: {len(old)} rows ({time.perf_counter() - start:.0f} s)")
    if extra := len(new) - len({key(r) for r in old}):
        print(f"  note: this run also produced {extra} rows that are not in the recorded file")
    return failed


IDENTITY = (
    "experiment",
    "compromised_attesters",
    "tool",
    "attack",
    "honest",
    "component",
    "arm",
    "scenario",
    "scenario_id",
    "observers",
    "device",
    "liar",
    "attested",
    "compromised_fraction",
    "seed",
)


def key(row: dict[str, Any]) -> tuple:
    return tuple(json.dumps(row.get(k)) for k in IDENTITY)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suites", nargs="*", default=list(GRID + REAL))
    parser.add_argument("--sample", type=int, default=3, help="recorded runs re-run per suite")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    failed = 0
    for suite in args.suites:
        print(suite)
        if suite == "container_twin":
            failed += container_twin()
        elif suite in SECURITY:
            failed += security(suite)
        else:
            failed += sampled(suite, recorded(suite), args.sample, rng)
    print("OK: every re-run matches its recorded row" if not failed else f"{failed} mismatches")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
