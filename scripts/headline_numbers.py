"""Print the evaluation's headline numbers, each computed from the recorded rows it comes from."""

from __future__ import annotations

import gzip
import json
import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RESULTS = ROOT / "results" / "experiments"


def rows(suite: str) -> list[dict[str, Any]]:
    path = RESULTS / suite / "rows.jsonl"
    if path.exists():
        return [json.loads(line) for line in path.read_text().splitlines() if line]
    with gzip.open(path.with_suffix(".jsonl.gz"), "rt") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def avg(items: Iterable[dict[str, Any]], key: str) -> float | None:
    values = [r[key] for r in items if isinstance(r.get(key), int | float)]
    return mean(values) if values else None


def pct(x: float | None) -> str:
    return "n/a" if x is None else f"{100 * x:.1f}%"


def select(data: list[dict[str, Any]], **match: Any) -> list[dict[str, Any]]:
    return [r for r in data if all(r.get(k) == v for k, v in match.items())]


def section(title: str, lines: Iterable[str]) -> None:
    print(f"\n{title}")
    for line in lines:
        print(f"  {line}")


def scenarios() -> list[str]:
    from m8_eval_harness.scenarios import ADAPTIVE, RESILIENCE, SCENARIOS

    held = [*SCENARIOS, *ADAPTIVE, *RESILIENCE]
    sizes = sorted({s.n_nodes for s in held})
    return [f"{len(held)} held-out scenarios, fleets of {sizes[0]} to {sizes[-1]} devices"]


def container_twin() -> list[str]:
    twin = json.loads((ROOT / "results" / "container_twin" / "summary.json").read_text())
    same = sum(r["proposed"]["identical"] for r in twin)
    total = sum(r["proposed"]["device_ticks"] for r in twin)
    return [
        f"{len(twin)} scenarios, identical response levels on {same:,} of {total:,} device-ticks"
    ]


def message_loss() -> list[str]:
    rob = rows("robustness")
    out = []
    for rate in ("0.01", "0.05", "0.1"):
        detected = avg(
            select(rob, scenario_id=f"loss:{rate}:a12", baseline_id="full"), "device_tpr"
        )
        cells = [f"loss:{rate}:{s}" for s in ("s2", "a12", "r3")]

        def restricted(arm: str, cells: list[str] = cells) -> float | None:
            return avg(
                [r for r in rob if r["baseline_id"] == arm and r["scenario_id"] in cells],
                "false_restriction_rate",
            )

        out.append(
            f"{float(rate):.0%} loss: withholding monitor detected by the DIS {pct(detected)}; "
            f"healthy restricted, DIS {pct(restricted('full'))}, "
            f"TOLERANCE {pct(restricted('tolerance'))}"
        )
    return out


def external() -> list[str]:
    ext = rows("external")
    attacked = sorted({r["scenario_id"] for r in ext if r["tp"] + r["fn"] > 0})
    arms = {
        "DIS": "full",
        "DIS + CUSUM": "cusum@0.15:6.4",
        "CUSUM": "page_cusum@0.05:1.6",
        "TOLERANCE": "tolerance",
        "optimal stopping": "stopping_response",
        "binary zero trust": "binary_zt@0.8",
        "Isolation Forest": "isolation_forest@0.002",
    }
    out = [
        "on-off attacker (a1) detected: "
        + ", ".join(
            f"{name} {pct(avg(select(ext, scenario_id='a1', baseline_id=a), 'device_tpr'))}"
            for name, a in arms.items()
        )
    ]
    for name in ("DIS", "CUSUM"):
        hit = [r for r in ext if r["baseline_id"] == arms[name] and r["scenario_id"] in attacked]
        out.append(f"mean response latency, {name}: {avg(hit, 'latency_response_mean'):.2f} ticks")
    inflate = avg(select(ext, scenario_id="a5", baseline_id="full"), "false_restriction_rate")
    suppress = avg(select(ext, scenario_id="a13", baseline_id="full"), "device_tpr")
    out.append(f"inflating correlation agent (a5): healthy restricted by the DIS {pct(inflate)}")
    out.append(f"suppressing correlation agent (a13): campaign detected by the DIS {pct(suppress)}")
    full = select(ext, baseline_id="full", operator="absent")
    out.append(
        f"isolations without an operator's approval (DIS, every scenario): "
        f"{sum(r['isolations'] for r in full)}"
    )
    s6 = {
        name: avg(select(ext, scenario_id="s6", baseline_id=a), "availability_cost")
        for name, a in arms.items()
        if name != "Isolation Forest"
    }
    out.append(
        "weaponised healing (s6), victim ticks restricted of 50: "
        + ", ".join(f"{k} {v:.1f}" for k, v in s6.items() if v is not None)
    )
    out.append(
        f"weaponised healing (s6), isolations by the DIS: "
        f"{sum(r['isolations'] for r in select(ext, scenario_id='s6', baseline_id='full'))}"
    )
    return out


def quorum() -> list[str]:
    out = []
    for r in rows("quorum"):
        out.append(
            f"{r['compromised_attesters']} of {r['n']} attesters compromised: "
            f"{r['malicious_accepted']} of {r['trials']} malicious writes admitted"
        )
    return out


def windows() -> list[str]:
    out = []
    arms = {"DIS": "full", "DIS + CUSUM": "cusum@0.15:6.4", "CUSUM": "page_cusum@0.05:1.6"}
    for mapping, suite in (("first", "ton_iot_windows"), ("revised", "ton_iot_windows_revised")):
        loop = json.loads((RESULTS / suite / "summary.json").read_text())["loop"]
        for machine, kinds in loop.items():
            own = {**arms, "TOLERANCE (own-data fit)": f"tolerance@{machine}-{mapping}"}
            cells = []
            for name, arm in own.items():
                vals = [v[arm] for v in kinds.values() if arm in v]
                if vals:
                    cells.append(
                        f"{name} {pct(mean(v['device_tpr'] for v in vals))} / "
                        f"{pct(mean(v['false_restriction_rate'] for v in vals))}"
                    )
            out.append(
                f"{machine}, {mapping} mapping (detected / healthy restricted): " + "; ".join(cells)
            )
    return out


def lanl() -> list[str]:
    by_arm = json.loads((RESULTS / "lanl_identity" / "summary.json").read_text())["loop"]["by_arm"]
    arms = {
        "DIS": "full",
        "CUSUM": "page_cusum@0.05:1.6",
        "TOLERANCE (own-data fit)": "tolerance@lanl",
        "binary zero trust": "binary_zt@0.8",
    }
    return [
        f"{name}: detected {pct(by_arm[a]['detected_after_onset'])}, "
        f"healthy restricted {pct(by_arm[a]['false_restriction_rate'])}"
        for name, a in arms.items()
        if a in by_arm
    ]


def trusted() -> list[str]:
    t = rows("trusted")

    def line(label: str, **match: Any) -> str:
        chosen = select(t, **match)
        return (
            f"{label}: detected {pct(avg(chosen, 'device_tpr'))}, healthy restricted "
            f"{pct(avg(chosen, 'false_restriction_rate'))}"
        )

    return [
        line("fusion lying (suppress), single instance", arm="core_fusion_suppress"),
        line("fusion lying (suppress), one liar of three", arm="core_fusion_suppress_replicated"),
        line("fusion lying (frame), one liar of three", arm="core_fusion_frame_replicated"),
        line(
            "orchestrator hiding attacks, devices sign", arm="core_orchestrator_hide", attested=True
        ),
        line(
            "orchestrator framing devices, devices sign",
            arm="core_orchestrator_frame",
            attested=True,
        ),
        f"operator approving everything: healthy isolated "
        f"{pct(avg(select(t, component='operator'), 'false_isolation_rate'))}",
    ]


def scale() -> list[str]:
    sc = rows("scale")

    def p95(n: int, arm: str) -> float | None:
        return avg(select(sc, scenario_id=f"sweep:scale:{n}", baseline_id=arm), "tick_ms_p95")

    full50, full5000, zt5000 = p95(50, "full"), p95(5000, "full"), p95(5000, "binary_zt")
    return [
        f"tick p95: {full50:.1f} ms at 50 devices, {full5000:.0f} ms at 5,000 "
        f"(binary zero trust {zt5000:.0f} ms, +{100 * (full5000 / zt5000 - 1):.0f}%); "
        "timings depend on the machine"
    ]


SECTIONS: tuple[tuple[str, Callable[[], list[str]]], ...] = (
    ("Scenarios", scenarios),
    ("Container deployment against the simulator", container_twin),
    ("Silence under random report loss (robustness)", message_loss),
    ("Synthetic attacks and comparators (external)", external),
    ("Memory poisoning (quorum)", quorum),
    ("Real Windows host counters (TON_IoT)", windows),
    ("Real authentication with a red team (LANL)", lanl),
    ("Trusted components compromised (trusted)", trusted),
    ("Scale", scale),
)

if __name__ == "__main__":
    for title, fn in SECTIONS:
        section(title, fn())
