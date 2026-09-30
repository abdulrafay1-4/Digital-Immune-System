"""Fit TOLERANCE's node controller on the calibration set only (`baselines/tolerance.py`)."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Sequence
from typing import Any

import numpy as np

from m8_eval_harness.baselines.tolerance import (
    CONFIG,
    OBSERVATIONS,
    NodeModel,
    cross_entropy_threshold,
    observation,
)

P_C1, P_C2, P_U, ETA = 1e-5, 1e-3, 2e-2, 2.0

REPRODUCTION = {
    "paper": "Table 2, Delta_R infinite: J = 0.16 (CEM), 0.15 (BO)",
    "ours": {
        "Table 8 as printed (eta 2, BetaBin n 10 on O = 0..9, b1 = p_A)": "0.325-0.329",
        "the authors' code (BetaBin n = |O| - 1, starts healthy), eta 2": "0.277-0.295",
        "eta 1, as in the authors' public example": "0.199-0.237",
        "eta 1 and 1000 observation values, as in that example": "0.185-0.198",
    },
    "oracle_lower_bound": 0.100,
    "verdict": "not reproduced; the equations match the authors' code line by line",
}


SITE_SEEDS = (0, 1, 2)


def site_scenarios(site: str) -> list[Any]:
    """Scenarios from one real dataset's calibration half, built as its held-out ones are."""
    if site == "lanl":
        from m8_eval_harness import lanl_identity as lanl

        doc = json.loads(lanl.CALIBRATION_FILE.read_text())
        devices = lanl.Devices()
        calibration, _ = devices.split()
        return [
            lanl.scenario(devices, fleet, doc, k)
            for k, fleet in enumerate(lanl.fleets(devices, calibration))
        ]
    from m8_eval_harness import ton_iot_windows as windows

    machine, mapping_name = site.split("-")
    mapping = windows.MAPPINGS[mapping_name]
    doc = json.loads(mapping.calibration_file.read_text())
    calibration, _ = windows.split(windows.load(windows.MACHINES[machine]))
    scales = windows.load_scales(machine, doc)
    counts = Counter(calibration.kind)
    kinds = sorted(k for k, n in counts.items() if k != "normal" and n >= windows.MIN_RECORDS)
    return [
        windows.scenario_for(machine, kind, calibration, scales, seed)
        for kind in kinds
        for seed in SITE_SEEDS
    ]


def measure(scenarios: Sequence[Any] | None = None, replicates: int | None = None) -> dict:
    """Z(. | H), Z(. | C) and p_A on the calibration scenarios' telemetry."""
    from m1_monitoring.core.observation import observation_from_context
    from m1_monitoring.sensors.synthetic import SyntheticTelemetry
    from m8_eval_harness.calibrate import CALIBRATION_IDS, REPLICATES
    from m8_eval_harness.params import FROZEN
    from m8_eval_harness.scenarios.catalogue import by_id

    w_identity, w_behavioral, w_device, w_network = FROZEN.obs_weights
    counts = np.zeros((2, OBSERVATIONS))
    onsets = healthy_steps = 0
    chosen = scenarios if scenarios is not None else [by_id(s) for s in CALIBRATION_IDS]
    default_replicates = REPLICATES if scenarios is None else 1
    for scenario in chosen:
        for replicate in range(default_replicates if replicates is None else replicates):
            sensor = SyntheticTelemetry(
                scenario.seed + replicate,
                anomalies=scenario.anomaly_map,
                dimension_masks=scenario.dimension_masks,
                noise_model=scenario.noise,
            )
            for i in range(scenario.n_nodes):
                node = f"node-{i}"
                attacked = scenario.attack_ticks(node)
                for t in range(scenario.ticks):
                    context, _ = sensor.read(float(t), node)
                    o = observation(
                        observation_from_context(
                            context,
                            w_identity=w_identity,
                            w_behavioral=w_behavioral,
                            w_device=w_device,
                            w_network=w_network,
                        )
                    )
                    counts[1 if t in attacked else 0, o] += 1
                    if t not in attacked and t + 1 < scenario.ticks:
                        healthy_steps += 1
                        onsets += (t + 1) in attacked
    smoothed = counts + 1.0
    z_h, z_c = smoothed[0] / smoothed[0].sum(), smoothed[1] / smoothed[1].sum()
    return {
        "p_a": onsets / healthy_steps,
        "z_h": z_h.round(6).tolist(),
        "z_c": z_c.round(6).tolist(),
        "counts": counts.astype(int).tolist(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=None, help="windows7-first, windows10-revised, lanl, ...")
    args = parser.parse_args(argv)
    from m8_eval_harness.baselines.tolerance import site_config

    measured = measure(site_scenarios(args.site) if args.site else None)
    model = NodeModel(
        p_a=measured["p_a"],
        p_c1=P_C1,
        p_c2=P_C2,
        p_u=P_U,
        z_h=tuple(measured["z_h"]),
        z_c=tuple(measured["z_c"]),
        eta=ETA,
    )
    alpha, cost = cross_entropy_threshold(model, seed=0)
    doc = {
        "model": {
            **{k: measured[k] for k in ("p_a", "z_h", "z_c")},
            "p_c1": P_C1,
            "p_c2": P_C2,
            "p_u": P_U,
            "eta": ETA,
        },
        "counts": measured["counts"],
        "alpha": round(alpha, 4),
        "average_cost": round(cost, 4),
        "reproduction": REPRODUCTION,
    }
    if args.site:
        doc["site"] = args.site
    (site_config(args.site) if args.site else CONFIG).write_text(json.dumps(doc, indent=2) + "\n")
    print(json.dumps({k: doc[k] for k in ("alpha", "average_cost")}), "p_a", round(model.p_a, 5))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
