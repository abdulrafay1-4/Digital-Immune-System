"""Metrics: every number the evaluation reports, defined once."""

from __future__ import annotations

import statistics
from collections import defaultdict
from typing import Any

FLAG_LEVEL = 1
RESPONSE_LEVEL = 2
RESTRICT_LEVEL = 3
ISOLATE_LEVEL = 4
TRUST_RESTORED = 0.8
COVERAGE_GRACE = 2
LATENCY_TARGET_TICKS = 5
MTTR_TARGET_TICKS = 10


def _ratio(numerator: float, denominator: float) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round(q * (len(ordered) - 1))))]


def _series(result: Any):
    levels: dict[str, dict[int, int]] = defaultdict(dict)
    executed: dict[str, dict[int, int]] = defaultdict(dict)
    trust: dict[str, dict[int, float]] = defaultdict(dict)
    for outcome in result.pipeline.outcomes:
        tick = int(round(outcome.sim_time))
        for plan, execution in zip(outcome.plans, outcome.executions, strict=True):
            levels[plan.node_id][tick] = plan.proposed_level
            if execution.executed and execution.level is not None:
                executed[plan.node_id][tick] = int(execution.level)
        for update in outcome.gt_updates:
            trust[update.node_id][tick] = update.ts
    return levels, executed, trust


def _first_at_or_above(series: dict[int, int], level: int, start: int) -> int | None:
    for tick in sorted(series):
        if tick >= start and series[tick] >= level:
            return tick
    return None


def _settles(series: dict[Any, Any], start: int, end: int, ok: Any) -> int | None:
    """First tick >= start after which every recorded value up to `end` satisfies `ok`."""
    ticks = [t for t in range(start, end) if t in series]
    for i, tick in enumerate(ticks):
        if all(ok(series[t]) for t in ticks[i:]):
            return tick
    return None


def evaluate(result: Any) -> dict[str, Any]:
    scenario = result.scenario
    levels, executed, trust = _series(result)
    devices = [f"node-{i}" for i in range(scenario.n_nodes)]
    compromised = set(scenario.compromised)
    healthy = [d for d in devices if d not in compromised]
    benign = sorted({a.node_id for a in scenario.anomalies} - compromised)
    attack_ticks = {n: scenario.attack_ticks(n) for n in compromised}
    last_tick = scenario.ticks

    def worst(node: str) -> int:
        return max(levels[node].values(), default=0)

    responded = {d for d in devices if worst(d) >= RESPONSE_LEVEL}
    tp = len(responded & compromised)
    fp = sum(1 for d in healthy if d in responded)
    fn = len(compromised) - tp
    tn = len(healthy) - fp
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    f1 = (
        None
        if precision is None or recall is None or precision + recall == 0
        else 2 * precision * recall / (precision + recall)
    )

    ttp = tfp = tfn = ttn = 0
    attacked = covered = residual = 0
    for device in devices:
        attack = attack_ticks.get(device, frozenset())
        series = levels[device]
        for tick in range(last_tick):
            positive = tick in attack
            predicted = series.get(tick, 0) >= RESPONSE_LEVEL
            if positive and predicted:
                ttp += 1
            elif positive:
                tfn += 1
            elif predicted:
                tfp += 1
            else:
                ttn += 1
        for tick in attack:
            attacked += 1
            if any(
                series.get(u, 0) >= RESPONSE_LEVEL for u in range(tick, tick + COVERAGE_GRACE + 1)
            ):
                covered += 1
            if executed[device].get(tick, 0) < RESPONSE_LEVEL:
                residual += 1
    tick_precision = _ratio(ttp, ttp + tfp)
    tick_recall = _ratio(ttp, ttp + tfn)
    tick_f1 = (
        None
        if tick_precision is None or tick_recall is None or tick_precision + tick_recall == 0
        else 2 * tick_precision * tick_recall / (tick_precision + tick_recall)
    )

    flag, response, restrict, containment, mttr, restoration = [], [], [], [], [], []
    unrecovered = 0
    for device in sorted(compromised):
        onset = int(scenario.ground_truth[device])
        series = levels[device]
        first_flag = _first_at_or_above(series, FLAG_LEVEL, onset)
        first_response = _first_at_or_above(series, RESPONSE_LEVEL, onset)
        first_restrict = _first_at_or_above(series, RESTRICT_LEVEL, onset)
        if first_flag is not None:
            flag.append(first_flag - onset)
        if first_response is not None:
            response.append(first_response - onset)
        if first_restrict is not None:
            restrict.append(first_restrict - onset)
        first_executed_restriction = _first_at_or_above(executed[device], RESTRICT_LEVEL, onset)
        if first_response is not None and first_executed_restriction is not None:
            containment.append(first_executed_restriction - first_response)
        end = scenario.attack_end(device)
        if end is not None and end < last_tick - 1 and first_response is not None:
            settled = _settles(series, int(end), last_tick, lambda v: v == 0)
            if settled is None:
                unrecovered += 1
            else:
                mttr.append(settled - end)
            restored = _settles(trust[device], int(end), last_tick, lambda v: v >= TRUST_RESTORED)
            if restored is not None:
                restoration.append(restored - end)

    benign_mttr, benign_unrecovered = [], 0
    for device in benign:
        end = max(a.end_sim for a in scenario.anomalies if a.node_id == device)
        if end >= last_tick - 1:
            continue
        settled = _settles(levels[device], int(end), last_tick, lambda v: v == 0)
        if settled is None:
            benign_unrecovered += 1
        else:
            benign_mttr.append(settled - end)

    falsely_restricted = [
        d for d in healthy if any(v >= RESTRICT_LEVEL for v in executed[d].values())
    ]
    falsely_isolated = [d for d in healthy if any(v >= ISOLATE_LEVEL for v in executed[d].values())]
    availability_cost = sum(1 for d in healthy for v in executed[d].values() if v >= RESTRICT_LEVEL)
    benign_response_ticks = sum(
        1 for d in benign for v in levels[d].values() if v >= RESPONSE_LEVEL
    )

    labelled = correct_primary = correct_rules = attacked_ticks = 0
    for outcome in result.pipeline.outcomes:
        tick = int(round(outcome.sim_time))
        under_attack = [n for n in compromised if tick in attack_ticks[n]]
        if not under_attack:
            continue
        attacked_ticks += 1
        families = set().union(*(scenario.threat_families(n) for n in under_attack))
        label = outcome.classification.threat_type
        rules = outcome.classification.rules_threat_type or label
        if label == "none" and rules == "none":
            continue
        labelled += 1
        correct_primary += label in families
        correct_rules += rules in families

    contained = sum(
        1 for d in compromised if any(v >= RESTRICT_LEVEL for v in executed[d].values())
    )
    healthy_device_ticks = len(healthy) * last_tick

    gate = result.approval_gate
    store = getattr(getattr(result.pipeline, "curator", None), "store", None)
    records = store.all_records() if store is not None else []
    adversary = result.adversary
    orchestrator = result.orchestrator
    tick_ms = [s * 1000 for s in result.tick_seconds]
    read_ms = [s * 1000 for s in getattr(result, "memory_read_seconds", [])]
    write_ms = [s * 1000 for s in getattr(result, "memory_write_seconds", [])]
    bus = getattr(orchestrator, "bus", None)
    engine_denials = dict(getattr(result.pipeline.engine, "denials", {}))
    broker = getattr(result.pipeline, "broker", None)
    broker_inner = getattr(broker, "inner", broker)

    def adversary_count(name: str) -> int | None:
        value = getattr(adversary, name, None)
        return (
            int(value) if isinstance(value, int | float) and not isinstance(value, bool) else None
        )

    return {
        "scenario_id": scenario.scenario_id,
        "baseline_id": result.baseline.baseline_id,
        "seed": result.seed,
        "operator": result.operator,
        "adjudication": result.adjudication,
        "binding": result.binding,
        "n_nodes": scenario.n_nodes,
        "ticks": result.ticks,
        "config_hash": result.config_hash,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "device_tpr": recall,
        "device_fpr": _ratio(fp, fp + tn),
        "device_precision": precision,
        "device_f1": f1,
        "device_accuracy": _ratio(tp + tn, len(devices)),
        "tick_precision": tick_precision,
        "tick_recall": tick_recall,
        "tick_f1": tick_f1,
        "tick_fpr": _ratio(tfp, tfp + ttn),
        "response_coverage": _ratio(covered, attacked),
        "latency_flag_mean": _mean(flag),
        "latency_response_mean": _mean(response),
        "latency_response_median": statistics.median(response) if response else None,
        "latency_restrict_mean": _mean(restrict),
        "latency_response_within_target": _ratio(
            sum(1 for v in response if v <= LATENCY_TARGET_TICKS), len(response)
        ),
        "detected_devices": len(response),
        "reached_restrict_devices": len(restrict),
        "containment_mean": _mean(containment),
        "mttr_mean": _mean(mttr),
        "mttr_within_target": _ratio(
            sum(1 for v in mttr if v <= MTTR_TARGET_TICKS), len(mttr) + unrecovered
        ),
        "unrecovered_devices": unrecovered,
        "trust_restoration_mean": _mean(restoration),
        "benign_devices": len(benign),
        "benign_worst_level": max((worst(d) for d in benign), default=None),
        "benign_mttr_mean": _mean(benign_mttr),
        "benign_unrecovered": benign_unrecovered,
        "benign_response_ticks": benign_response_ticks,
        "false_restriction_rate": _ratio(len(falsely_restricted), len(healthy)),
        "false_isolation_rate": _ratio(len(falsely_isolated), len(healthy)),
        "availability_cost": availability_cost,
        "healthy_worst_level": max((worst(d) for d in healthy if d not in benign), default=0),
        "disruptive_actions": result.disruptive_actions,
        "isolations": result.isolations,
        "restrictions_withheld": getattr(result.pipeline, "restrictions_withheld", 0),
        "label_coverage": _ratio(labelled, attacked_ticks),
        "label_accuracy_primary": _ratio(correct_primary, labelled),
        "label_accuracy_rules": _ratio(correct_rules, labelled),
        "operator_requests": len(gate.escalations) if gate is not None else 0,
        "operator_standing_reuses": gate.standing_reuses if gate is not None else 0,
        "memory_records": len(records),
        "memory_confirmed": sum(1 for r in records if r.status == "confirmed"),
        "memory_benign": sum(1 for r in records if r.status == "benign"),
        "recall_boosts": result.recall_boosts,
        "heal_events": result.heal_events,
        "poison_attempts": adversary_count("attempts"),
        "poison_accepted": adversary_count("accepted"),
        "forged_for_others": adversary_count("forged_for_others"),
        "correlation_lies": adversary_count("lies"),
        "sybil_reports": adversary_count("published"),
        "future_dated_sent": adversary_count("sent"),
        "unbound_updates": orchestrator.unbound_updates,
        "unattributable_deliveries": getattr(result, "telemetry_rejected", 0),
        "future_updates": orchestrator.future_updates,
        "foreign_updates": orchestrator.foreign_updates,
        "unattested_updates": orchestrator.unattested_updates,
        "late_updates": orchestrator.late_updates,
        "rate_limited_updates": orchestrator.rate_limited_updates,
        "pipeline_failures": orchestrator.pipeline_failures,
        "agents_quarantined": len(getattr(result.pipeline, "agents_quarantined", ())),
        "device_fnr": _ratio(fn, fn + tp),
        "containment_rate": _ratio(contained, len(compromised)),
        "residual_compromise": _ratio(residual, attacked),
        "service_availability": (
            None if healthy_device_ticks == 0 else 1.0 - availability_cost / healthy_device_ticks
        ),
        "mttd_mean": _mean(response),
        "mttrsp_mean": _mean(containment),
        "memory_read_ms_p50": _percentile(read_ms, 0.5),
        "memory_write_ms_p50": _percentile(write_ms, 0.5),
        "messages_published": None if bus is None else bus.published,
        "messages_per_device_tick": (
            None
            if bus is None or scenario.n_nodes * last_tick == 0
            else bus.published / (scenario.n_nodes * last_tick)
        ),
        "events_per_second": (
            None if not result.wall_seconds else orchestrator.updates_seen / result.wall_seconds
        ),
        "broker_requests": getattr(broker_inner, "requests", 0),
        "broker_denied": getattr(broker_inner, "denied_total", 0),
        "broker_unauthorised_rejected": (
            getattr(broker_inner, "denied", {}).get("unknown_caller", 0)
            + getattr(broker_inner, "denied", {}).get("capability_not_granted", 0)
        ),
        "broker_transport": (
            "none" if broker is None else ("mcp" if hasattr(broker, "calls") else "in-process")
        ),
        "mcp_calls": getattr(broker, "calls", 0) if broker is not None else 0,
        "memory_writes_denied": getattr(result.pipeline, "memory_writes_denied", 0),
        "actions_refused": sum(engine_denials.values()),
        "actions_refused_low_provenance": engine_denials.get("provenance_too_low", 0),
        "actions_refused_unknown_capability": engine_denials.get("unknown_capability", 0),
        "replay_attempts": engine_denials.get("token_replayed", 0),
        "expired_token_attempts": engine_denials.get("token_expired", 0),
        "correlation_overstated": getattr(result.pipeline, "correlation_overstated", 0),
        "persona_violations": getattr(result.pipeline, "persona_violations", 0),
        "degraded_stages": sum(result.pipeline.degraded.values()),
        "trust_rise_capped": getattr(result.pipeline.fusion, "trust_rise_capped", 0),
        "audit_intact": result.audit_intact,
        "audit_records": (result.audit_checkpoint or {}).get("count"),
        "tick_ms_p50": _percentile(tick_ms, 0.5),
        "tick_ms_p95": _percentile(tick_ms, 0.95),
        "wall_seconds": result.wall_seconds,
        "cpu_seconds": result.cpu_seconds,
        "rss_mb": result.rss_mb,
        "rss_mb_delta": result.rss_mb_delta,
    }
