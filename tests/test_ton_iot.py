"""TON_IoT calibration and replay, on a tiny capture written by the test."""

from __future__ import annotations

import csv
import json

import numpy as np
import pytest

from m1_monitoring.sensors.dataset_replay import DatasetReplayTelemetry
from m1_monitoring.sensors.synthetic import NoiseModel, SyntheticTelemetry
from m8_eval_harness import ton_iot
from shared.schemas import Provenance

COLUMNS = ["ts", "src_ip", "dst_ip", "dst_port", "conn_state", "src_bytes", "label", "type"]


def _capture(path) -> None:
    rows = []
    for window in range(40):
        ts = 1_000_000 * 300 + window * 300
        for host in ("10.0.0.1", "10.0.0.2"):
            for k in range(2 + window % 2):
                rows.append([ts, host, "10.0.0.9", 443 + k, "SF", 500, 0, "normal"])
        if window == 5 or 25 <= window < 30:
            for port in range(60):
                rows.append([ts, "10.0.0.66", f"10.0.1.{port}", port, "S0", 0, 1, "scanning"])
        elif window % 3 == 0:
            rows.append([ts, "10.0.0.66", "10.0.0.9", 80, "SF", 400, 0, "normal"])
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        writer.writerows(rows)


def test_calibration_scores_attacks_above_benign_and_replays_ground_truth(tmp_path) -> None:
    data, frozen = tmp_path / "net.csv", tmp_path / "cal.json"
    _capture(data)
    doc = ton_iot.calibrate(data, out=frozen)
    assert doc["sha256"] == ton_iot.sha256(data)
    assert doc["benign_quantiles"][50] == 0.0
    calibration, _ = ton_iot.Calibration.load(frozen)

    _, held_out, _ = ton_iot.split(ton_iot.load_windows(data))
    scan = [w for w in held_out if w.attack]
    quiet = [w for w in held_out if not w.attack]
    assert len(scan) == 5
    assert min(calibration.disturbance(w) for w in scan) > max(
        calibration.disturbance(w) for w in quiet
    )
    assert ton_iot.auc([calibration.raw(w) for w in held_out], [w.attack for w in held_out]) == 1.0

    scenario, devices = ton_iot.replay_scenario(held_out, calibration)
    attacker = next(n for n, d in devices.items() if d["host"] == "10.0.0.66")
    assert scenario.compromised == {attacker}
    assert scenario.attack_ticks(attacker) == frozenset(range(5, 10))
    trace = dict(scenario.noise.trace)
    assert all(trace[attacker][t] > 0.5 for t in range(5, 10))


def test_noise_models_leave_gaussian_untouched_and_validate() -> None:
    plain = SyntheticTelemetry(3).read(4.0, "node-0")[0]
    replay = NoiseModel(kind="replay", trace=(("node-0", (0.0,) * 4 + (0.3,)),))
    replayed = SyntheticTelemetry(3, noise_model=replay).read(4.0, "node-0")[0]
    assert replayed.network == pytest.approx(plain.network - 0.3)
    sensor = DatasetReplayTelemetry(3, {"node-0": (0.0,) * 4 + (0.3,)})
    assert sensor.read(4.0, "node-0") == (replayed, Provenance.MEDIUM)
    assert replayed.identity == plain.identity
    assert (
        SyntheticTelemetry(3, noise_model=replay).read(9.0, "node-0")[0]
        == SyntheticTelemetry(3).read(9.0, "node-0")[0]
    )
    with pytest.raises(ValueError):
        NoiseModel(kind="ton_iot")
    with pytest.raises(ValueError):
        NoiseModel(kind="replay", trace=(("node-0", (1.5,)),))


def test_committed_calibration_is_the_ton_iot_noise_model() -> None:
    doc = json.loads(ton_iot.CALIBRATION_FILE.read_text())
    model = ton_iot.noise_model()
    assert model.quantiles == tuple(doc["benign_quantiles"])
    assert doc["held_out_windows"]["attack"] > doc["calibration_windows"]["attack"] > 0


def test_host_replay_subtracts_real_disturbance_from_behaviour_and_device_only():
    trace = (("node-0", ((0.3, 0.2), (0.0, 0.0))),)
    replayed = SyntheticTelemetry(7, noise_model=NoiseModel(kind="host_replay", host_trace=trace))
    plain = SyntheticTelemetry(7)
    ctx, provenance = replayed.read(0.0, "node-0")
    base, _ = plain.read(0.0, "node-0")
    assert ctx.behavioral == pytest.approx(base.behavioral - 0.3)
    assert ctx.device == pytest.approx(base.device - 0.2)
    assert (ctx.identity, ctx.network) == (base.identity, base.network)
    assert provenance == Provenance.MEDIUM
    assert replayed.read(0.0, "node-1")[0] == plain.read(0.0, "node-1")[0]
    assert replayed.read(5.0, "node-0")[0] == plain.read(5.0, "node-0")[0]


def test_host_replay_with_network_counters_lowers_the_network_dimension_too():
    trace = (("node-0", ((0.3, 0.2, 0.25),)),)
    replayed = SyntheticTelemetry(7, noise_model=NoiseModel(kind="host_replay", host_trace=trace))
    base, _ = SyntheticTelemetry(7).read(0.0, "node-0")
    ctx, _ = replayed.read(0.0, "node-0")
    assert ctx.network == pytest.approx(base.network - 0.25)
    assert ctx.identity == base.identity, "no public dataset carries identity"


def test_top_k_aggregates_the_most_disturbed_counters_without_diluting_them():
    from m8_eval_harness.ton_iot_windows import Scale

    x = np.array([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]])
    flat = dict(keep=tuple(range(10)), median=(0.0,) * 10, spread=(1.0,) * 10)
    assert Scale(**flat, aggregate="mean").raw(x)[0] == pytest.approx(0.2)
    assert Scale(**flat, aggregate="top3").raw(x)[0] == pytest.approx(2 / 3)
    assert Scale(**flat, aggregate="top10pct").raw(x)[0] == pytest.approx(1.0)
