"""The scenario lab: any evaluated scenario, run by the real engine, beside baselines."""

from __future__ import annotations

import tempfile
import threading
from collections import Counter
from pathlib import Path
from typing import Any

LAB_ARMS = ("full", "binary_zt", "no_sharing", "no_memory", "static_trust", "beta_reputation")
METRICS = (
    "device_tpr",
    "device_fpr",
    "latency_flag_mean",
    "latency_response_mean",
    "latency_restrict_mean",
    "response_coverage",
    "residual_compromise",
    "false_restriction_rate",
    "mttr_mean",
    "disruptive_actions",
    "isolations",
    "operator_requests",
    "poison_attempts",
    "poison_accepted",
    "unattributable_deliveries",
    "unbound_updates",
    "agents_quarantined",
    "trust_rise_capped",
    "recall_boosts",
)
MAX_FOCUS = 10
_MILESTONES = (
    (1, "flagged (L1)"),
    (2, "responded to (L2)"),
    (3, "restricted (L3)"),
    (4, "isolation requested (L4)"),
)

_cache: dict[tuple[str, tuple[str, ...], int], dict[str, Any]] = {}
_lock = threading.Lock()
_pool: Any = None
_pool_runs = 0
RUNS_PER_WORKER = 12


def _executor() -> Any:
    global _pool, _pool_runs
    if _pool is not None and _pool_runs >= RUNS_PER_WORKER:
        _pool.shutdown(wait=False)
        _pool = None
    if _pool is None:
        from concurrent.futures import ProcessPoolExecutor

        _pool, _pool_runs = ProcessPoolExecutor(max_workers=1), 0
    _pool_runs += 1
    return _pool


def shutdown() -> None:
    if _pool is not None:
        _pool.shutdown(cancel_futures=True)


def catalogue() -> list[dict[str, Any]]:
    from m8_eval_harness.scenarios import ADAPTIVE, RESILIENCE, SCENARIOS

    out = []
    for family, group in (("Core", SCENARIOS), ("Adaptive", ADAPTIVE), ("Resilience", RESILIENCE)):
        for s in group:
            out.append(
                {
                    "id": s.scenario_id,
                    "name": s.name,
                    "family": family,
                    "demonstrates": s.demonstrates,
                    "devices": s.n_nodes,
                    "ticks": s.ticks,
                    "compromised": len(s.compromised),
                    "notes": s.notes,
                }
            )
    return out


def run(scenario_id: str, arms: list[str], seed: int) -> dict[str, Any]:
    arms = [a for a in dict.fromkeys(arms) if a in LAB_ARMS] or ["full", "binary_zt"]
    if "full" not in arms:
        arms.insert(0, "full")
    arms = arms[:4]
    if scenario_id not in {s["id"] for s in catalogue()}:
        raise ValueError("unknown scenario")
    if not 0 <= int(seed) < 1_000_000:
        raise ValueError("seed must be between 0 and 999999")
    key = (scenario_id, tuple(arms), int(seed))
    with _lock:
        if key in _cache:
            return _cache[key]
    with _lock:
        pool = _executor()
    payload = pool.submit(compute, scenario_id, tuple(arms), int(seed)).result(timeout=120)
    with _lock:
        if len(_cache) > 64:
            _cache.clear()
        _cache[key] = payload
    return payload


def compute(scenario_id: str, arms: tuple[str, ...], seed: int) -> dict[str, Any]:
    from m8_eval_harness.experiment import resolve_scenario

    scenario = resolve_scenario(scenario_id)
    results = {arm: _run_arm(scenario, arm, seed) for arm in arms}
    focus = _focus(scenario, results)
    payload = {
        "scenario": {
            "id": scenario.scenario_id,
            "name": scenario.name,
            "demonstrates": scenario.demonstrates,
            "devices": scenario.n_nodes,
            "ticks": scenario.ticks,
            "compromised": sorted(scenario.compromised),
            "attack_windows": {
                a.node_id: [a.start_sim, a.end_sim, a.severity, list(a.dimensions)]
                for a in scenario.anomalies
            },
            "outages": {k: list(v) for k, v in scenario.outages.items()},
            "adversary": getattr(scenario.adversary, "name", None),
            "notes": scenario.notes,
        },
        "seed": seed,
        "focus": focus,
        "arms": {arm: _arm_view(r, focus, scenario) for arm, r in results.items()},
    }
    return payload


def _run_arm(scenario: Any, arm: str, seed: int) -> dict[str, Any]:
    from m8_eval_harness import baselines
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario

    with tempfile.TemporaryDirectory() as tmp:
        result = run_scenario(scenario, baselines.by_id(arm), seed=seed, results_dir=Path(tmp))
    return {"result": result, "row": evaluate(result)}


def _focus(scenario: Any, results: dict[str, dict[str, Any]]) -> list[str]:
    """The devices worth drawing: the attacked, then anything any arm acted on."""
    chosen = list(
        dict.fromkeys([*sorted(scenario.compromised), *(a.node_id for a in scenario.anomalies)])
    )
    touched: Counter[str] = Counter()
    for r in results.values():
        for outcome in r["result"].pipeline.outcomes:
            for plan in outcome.plans:
                if plan.proposed_level >= 2:
                    touched[plan.node_id] += 1
    chosen += [n for n, _ in touched.most_common() if n not in chosen]
    if len(chosen) < 3:
        chosen += [f"node-{i}" for i in range(scenario.n_nodes) if f"node-{i}" not in chosen][
            : 3 - len(chosen)
        ]
    return chosen[:MAX_FOCUS]


def _arm_view(r: dict[str, Any], focus: list[str], scenario: Any) -> dict[str, Any]:
    result, row = r["result"], r["row"]
    timeline = []
    events: list[dict[str, Any]] = []
    first: dict[tuple[str, int], int] = {}
    for outcome in result.pipeline.outcomes:
        t = int(outcome.sim_time)
        gt = {u.node_id: round(u.gt, 3) for u in outcome.gt_updates if u.node_id in focus}
        ts = {u.node_id: round(u.ts, 3) for u in outcome.gt_updates if u.node_id in focus}
        planned = {p.node_id: int(p.proposed_level) for p in outcome.plans}
        executed, refused = {}, {}
        for plan, res in zip(outcome.plans, outcome.executions, strict=True):
            if res.executed and plan.proposed_level > 0:
                executed[plan.node_id] = int(res.level or plan.proposed_level)
            elif not res.executed and res.decision is not None and plan.node_id in focus:
                refused[plan.node_id] = res.decision.deny_reason or "refused"
        counts = Counter(planned.values())
        timeline.append(
            {
                "t": t,
                "counts": [counts.get(level, 0) for level in range(5)],
                "gt": gt,
                "ts": ts,
                "planned": {n: planned.get(n, 0) for n in focus},
                "executed": {n: v for n, v in executed.items() if n in focus},
                "refused": refused,
                "cti": round(outcome.correlation.cti, 3),
                "implicated": [n for n in outcome.correlation.implicated_node_ids if n in focus],
                "recall": round(outcome.correlation.recall_boost, 3),
                "label": outcome.classification.threat_type,
                "healing": [
                    {"node": e.node_id, "phase": e.phase}
                    for e in outcome.healing
                    if e.node_id in focus
                ],
                "approvals": [
                    {"node": d.node_id, "approved": d.approved}
                    for d in outcome.approvals
                    if d.required and d.node_id in focus
                ],
                "restricted": sum(1 for v in executed.values() if v >= 3),
            }
        )
        for node in focus:
            level = planned.get(node, 0)
            for threshold, text in (
                (1, "flagged (L1)"),
                (2, "responded to (L2)"),
                (3, "restricted (L3)"),
                (4, "isolation requested (L4)"),
            ):
                if level >= threshold and (node, threshold) not in first:
                    first[(node, threshold)] = t
                    events.append({"t": t, "node": node, "text": f"{node} {text}"})
        if outcome.correlation.recall_boost > 0 and ("recall", 0) not in first:
            first[("recall", 0)] = t
            events.append({"t": t, "node": None, "text": "immune memory recognised the pattern"})
        for e in outcome.healing:
            if e.node_id in focus:
                events.append(
                    {"t": t, "node": e.node_id, "text": f"{e.node_id} self-healing: {e.phase}"}
                )
        for node, reason in refused.items():
            events.append({"t": t, "node": node, "text": f"{node}: action refused ({reason})"})
    adversary = result.adversary
    return {
        "name": result.baseline.name,
        "mechanism": result.baseline.mechanism,
        "metrics": {m: row.get(m) for m in METRICS},
        "timeline": timeline,
        "events": events[:300],
        "adversary": {
            k: getattr(adversary, k)
            for k in (
                "attempts",
                "accepted",
                "by_strategy",
                "forged_for_others",
                "lies_about_own",
                "cycles",
                "pushes",
                "published",
                "sent",
                "lies",
            )
            if adversary is not None and hasattr(adversary, k)
        },
    }
