"""The two comparison figures, redrawn from the recorded results."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from statistics import mean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "experiments"
OUT = ROOT / "results" / "figures"
BLUE, ORANGE = "#1f77b4", "#ff7f0e"
plt.rcParams.update({"font.size": 8, "pdf.fonttype": 42, "ps.fonttype": 42})


def rows(suite: str) -> list[dict]:
    """A suite's rows, from `rows.jsonl` if it was re-run, else the recorded `.gz`."""
    path = RESULTS / suite / "rows.jsonl"
    if path.exists():
        text = path.read_text()
    else:
        with gzip.open(path.with_suffix(".jsonl.gz"), "rt") as fh:
            text = fh.read()
    return [json.loads(line) for line in text.splitlines() if line]


def grouped(ax, groups: list[str], series: list[tuple[str, list[float], str]]) -> None:
    width = 0.36
    for i, (name, values, colour) in enumerate(series):
        xs = [g + (i - 0.5) * width for g in range(len(groups))]
        bars = ax.bar(xs, values, width, label=name, color=colour)
        for bar, v in zip(bars, values, strict=True):
            text = f"{v:.1f}" if 0 < v < 1 else f"{v:.0f}"
            ax.text(bar.get_x() + bar.get_width() / 2, v + 2, text, ha="center", fontsize=7)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)
    ax.set_ylim(0, 138)
    ax.set_yticks(range(0, 101, 20))
    ax.legend(loc="upper left", fontsize=7, frameon=False)


def save(fig, name: str) -> None:
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / f"{name}.pdf")
    plt.close(fig)
    print("wrote", OUT / f"{name}.pdf")


def message_loss() -> None:
    robustness = rows("robustness")

    def restricted(arm: str, rate: str) -> float:
        wanted = {f"loss:{rate}:{s}" for s in ("s2", "a12", "r3")}
        chosen = [r for r in robustness if r["baseline_id"] == arm and r["scenario_id"] in wanted]
        return 100 * mean(r["false_restriction_rate"] for r in chosen)

    rates = ("0.01", "0.05", "0.1")
    fig, ax = plt.subplots(figsize=(3.5, 2.3))
    grouped(
        ax,
        ["1%", "5%", "10%"],
        [
            ("DIS", [restricted("full", r) for r in rates], BLUE),
            ("TOLERANCE", [restricted("tolerance", r) for r in rates], ORANGE),
        ],
    )
    ax.set_xlabel("Random report loss")
    ax.set_ylabel("Healthy devices restricted (%)")
    save(fig, "message_loss")


def windows7() -> None:
    summary = json.loads((RESULTS / "ton_iot_windows" / "summary.json").read_text())
    kinds = summary["loop"]["windows7"]
    methods = (
        ("DIS", "full"),
        ("DIS + CUSUM", "cusum@0.15:6.4"),
        ("CUSUM", "page_cusum@0.05:1.6"),
        ("TOLERANCE", "tolerance@windows7-first"),
    )

    def score(arm: str, metric: str) -> float:
        return 100 * mean(v[arm][metric] for v in kinds.values() if arm in v)

    fig, ax = plt.subplots(figsize=(3.5, 2.3))
    grouped(
        ax,
        [name for name, _ in methods],
        [
            ("Attacked devices detected", [score(a, "device_tpr") for _, a in methods], BLUE),
            (
                "Healthy devices restricted",
                [score(a, "false_restriction_rate") for _, a in methods],
                ORANGE,
            ),
        ],
    )
    ax.set_ylabel("Devices (%)")
    save(fig, "windows7")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    message_loss()
    windows7()
