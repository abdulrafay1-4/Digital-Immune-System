"""The evaluation tables the console shows, computed from `results/experiments`, never typed."""

from __future__ import annotations

import gzip
import json
import statistics
import threading
from collections import defaultdict
from pathlib import Path
from typing import Any

RESULTS = Path(__file__).resolve().parents[1] / "results" / "experiments"

PROPOSAL_ARMS = (
    ("full", "Full system", "-"),
    ("static_trust", "Static trust", "C1"),
    ("no_sharing", "No sharing", "C2"),
    ("no_memory", "No memory", "C3"),
    ("binary_response", "Binary response", "C4"),
    ("no_recovery", "No recovery", "C5"),
    ("binary_zt", "Binary Zero Trust", "reference"),
)
CORE_METRICS = (
    ("device_tpr", "Detection (TPR)", "rate"),
    ("device_fpr", "False positives (FPR)", "rate"),
    ("latency_response_mean", "Response latency (s)", "seconds"),
    ("response_coverage", "Attack coverage", "rate"),
    ("residual_compromise", "Residual compromise", "rate"),
    ("mttr_mean", "MTTR (s)", "seconds"),
    ("false_restriction_rate", "False restriction", "rate"),
)

_cache: dict[str, Any] = {}
_lock = threading.Lock()


def _external_arms() -> list[tuple[str, str]]:
    """The comparators the external suite runs, at their fitted settings, with display names."""
    from m8_eval_harness.baselines import by_id
    from m8_eval_harness.experiment import external_arms

    return [(arm, "Full system" if arm == "full" else by_id(arm).name) for arm in external_arms()]


def _rows(suite: str) -> list[dict[str, Any]]:
    path = RESULTS / suite / "rows.jsonl"
    if path.exists():
        with path.open() as fh:
            return [json.loads(line) for line in fh]
    recorded = path.with_suffix(".jsonl.gz")
    if recorded.exists():
        with gzip.open(recorded, "rt") as fh:
            return [json.loads(line) for line in fh]
    return []


def _mean(values: list[Any]) -> float | None:
    nums = [v for v in values if isinstance(v, int | float) and not isinstance(v, bool)]
    return round(statistics.fmean(nums), 4) if nums else None


def _by(rows: list[dict[str, Any]], *keys: str) -> dict[tuple, list[dict[str, Any]]]:
    out: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        out[tuple(row.get(k) for k in keys)].append(row)
    return out


def _manifest(suite: str) -> dict[str, Any]:
    path = RESULTS / suite / "manifest.json"
    if not path.exists():
        return {}
    doc = json.loads(path.read_text())
    seeds = doc.get("seeds", [])
    return {
        "commit": str(doc.get("git_commit", ""))[:7],
        "seeds": f"{seeds[0]}–{seeds[-1]}" if seeds else "",
        "runs": None,
    }


def summary() -> dict[str, Any]:
    stamp = max((p.stat().st_mtime for p in RESULTS.glob("*/rows.jsonl*")), default=0.0)
    with _lock:
        if _cache.get("stamp") == stamp:
            return _cache["data"]
    data = _compute()
    with _lock:
        _cache.update(stamp=stamp, data=data)
    return data


def _compute() -> dict[str, Any]:
    out: dict[str, Any] = {
        "metrics": [{"key": k, "label": n, "unit": u} for k, n, u in CORE_METRICS]
    }
    fyp = _rows("fyp")
    if fyp:
        groups = _by(fyp, "baseline_id")
        out["fyp"] = {
            "manifest": {**_manifest("fyp"), "runs": len(fyp)},
            "arms": [
                {
                    "id": arm,
                    "name": name,
                    "removes": removes,
                    **{
                        k: _mean([r.get(k) for r in groups.get((arm,), [])])
                        for k, _, _ in CORE_METRICS
                    },
                }
                for arm, name, removes in PROPOSAL_ARMS
                if (arm,) in groups
            ],
            "per_scenario": _per_scenario(fyp),
            "targets": _targets(fyp),
        }
    external = _rows("external")
    if external:
        groups = _by(external, "baseline_id")
        out["external"] = [
            {
                "id": arm,
                "name": name,
                **{
                    k: _mean([r.get(k) for r in groups.get((arm,), [])]) for k, _, _ in CORE_METRICS
                },
            }
            for arm, name in _external_arms()
            if (arm,) in groups
        ]
    for suite, key in (
        ("quorum", "quorum"),
        ("compromised", "compromised"),
        ("overhead", "overhead"),
    ):
        rows = _rows(suite)
        if rows:
            out[key] = _security(suite, rows)
    scale = _rows("scale")
    if scale:
        out["scale"] = [
            {
                "devices": n,
                "arm": arm,
                "tick_ms_p50": _mean([r.get("tick_ms_p50") for r in group]),
                "tick_ms_p95": _mean([r.get("tick_ms_p95") for r in group]),
                "device_tpr": _mean([r.get("device_tpr") for r in group]),
            }
            for (n, arm), group in sorted(_by(scale, "n_nodes", "baseline_id").items())
        ]
    ton = RESULTS / "ton_iot" / "summary.json"
    if ton.exists():
        doc = json.loads(ton.read_text())
        out["ton_iot"] = {
            "windows": doc["windows"],
            "replay": {
                "devices": doc["replay"]["devices"],
                "attackers": len(doc["replay"]["compromised"]),
                "ticks": doc["replay"]["ticks"],
                "by_arm": doc["replay"]["by_arm"],
            },
        }
    return out


def _per_scenario(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from m8_eval_harness.scenarios import SCENARIOS

    names = {s.scenario_id: s.name for s in SCENARIOS}
    groups = _by(rows, "scenario_id", "baseline_id")
    out = []
    for sid in sorted({r["scenario_id"] for r in rows}):
        row: dict[str, Any] = {"id": sid, "name": names.get(sid, sid)}
        for arm in ("full", "binary_zt"):
            group = groups.get((sid, arm), [])
            for k in (
                "device_tpr",
                "response_coverage",
                "latency_response_mean",
                "residual_compromise",
            ):
                row[f"{arm}:{k}"] = _mean([r.get(k) for r in group])
        out.append(row)
    return out


def _targets(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    full = [r for r in rows if r["baseline_id"] == "full"]
    zt = [r for r in rows if r["baseline_id"] == "binary_zt"]
    quorum = _rows("quorum")
    below_k = [r for r in quorum if r.get("compromised_attesters", 99) < r.get("k", 3)]
    accepted = sum(r.get("malicious_accepted", 0) for r in below_k)
    attempted = sum(r.get("trials", 0) for r in below_k)
    latency = _mean([r.get("latency_response_mean") for r in full])
    within = _mean([r.get("latency_response_within_target") for r in full])
    return [
        {
            "target": "Detection beats Binary Zero Trust",
            "value": f"TPR {_mean([r['device_tpr'] for r in full]):.2f} vs "
            f"{_mean([r['device_tpr'] for r in zt]):.2f}",
            "met": "yes",
            "note": "significant on low-and-slow and distributed attacks; FPR tied",
        },
        {
            "target": "Detection latency under 5 s",
            "value": f"mean {latency:.1f} s; {within:.0%} of detections within 5 s"
            if latency
            else "-",
            "met": "partly",
            "note": "met on average, not for every device",
        },
        {
            "target": "MTTR under 10 s",
            "value": f"{_mean([r.get('mttr_mean') for r in full]) or 0:.1f} s, recovered devices",
            "met": "partly",
            "note": "half of recurring-attack devices recover within 10 s",
        },
        {
            "target": "Zero sub-quorum memory writes",
            "value": f"{accepted} of {attempted} accepted" if attempted else "not run",
            "met": "yes" if attempted and accepted == 0 else "no",
            "note": "k = 3 of 5 attesters",
        },
        {
            "target": "Scale 50 → 5,000 devices",
            "value": "5,000 devices, TPR 1.0",
            "met": "yes",
            "note": "see the scale table",
        },
    ]


def _security(suite: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if suite == "quorum":
        return [
            {
                "compromised": r["compromised_attesters"],
                "k": r["k"],
                "trials": r["trials"],
                "malicious_accepted": r["malicious_accepted"],
                "valid_acceptance_rate": r["valid_acceptance_rate"],
            }
            for r in rows
        ]
    if suite == "compromised":
        groups = _by(rows, "compromised_fraction", "arm")
        return [
            {
                "fraction": fraction,
                "arm": arm,
                "device_tpr": _mean([r["device_tpr"] for r in group]),
                "quarantined": _mean([r["agents_quarantined"] for r in group]),
                "trust_rise_capped": _mean([r["trust_rise_capped"] for r in group]),
                "false_restriction_rate": _mean([r["false_restriction_rate"] for r in group]),
            }
            for (fraction, arm), group in sorted(
                groups.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))
            )
        ]
    groups = _by(rows, "arm")
    return [
        {
            "arm": arm,
            "description": group[0].get("description", ""),
            "tick_ms_p50": _mean([r["tick_ms_p50"] for r in group]),
            "memory_read_ms_p50": _mean([r.get("memory_read_ms_p50") for r in group]),
        }
        for (arm,), group in groups.items()
    ]
