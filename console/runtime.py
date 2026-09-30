"""The live fleet: the whole DIS running continuously behind the operator console."""

from __future__ import annotations

import copy
import itertools
import threading
import traceback
from collections import Counter, deque
from concurrent.futures import Future
from dataclasses import dataclass, field
from typing import Any

N_NODES = 40
SEED = 7
RUN_ID = "console-live"
HISTORY = 300

_KINDS = (
    ("Extruder controller", "Line A"),
    ("Conveyor PLC", "Line A"),
    ("Vision camera", "Quality"),
    ("Robot arm", "Line B"),
    ("Pump controller", "Utilities"),
    ("HVAC sensor", "Facility"),
    ("Badge reader", "Access"),
    ("Edge gateway", "Network"),
)
LEVEL_NAMES = ("Normal", "Monitor", "Re-authenticate", "Restrict", "Isolate")


def fleet_catalogue(n: int) -> dict[str, dict[str, str]]:
    out = {}
    for i in range(n):
        kind, zone = _KINDS[i % len(_KINDS)]
        out[f"node-{i}"] = {
            "name": f"{kind} {i // len(_KINDS) + 1:02d}",
            "kind": kind,
            "zone": zone,
        }
    return out


class ConsoleApproval:
    """An `ApprovalPolicy` answered by a person on the console."""

    def __init__(self) -> None:
        self.pending: dict[str, dict[str, Any]] = {}
        self.answers: dict[str, tuple[bool, str, str]] = {}
        self.history: deque[dict[str, Any]] = deque(maxlen=200)

    def decide(self, request):  # type: ignore[no-untyped-def]
        from agents.approval import ApprovalDecision, DeciderKind

        answer = self.answers.pop(request.node_id, None)
        if answer is None:
            self.pending.setdefault(
                request.node_id,
                {
                    "node_id": request.node_id,
                    "level": request.level,
                    "rationale": request.rationale,
                    "asked_at": request.sim_time,
                },
            )
            approved, reason, by = False, "awaiting an operator: isolation withheld", "console"
        else:
            approved, reason, by = answer
            self.pending.pop(request.node_id, None)
            self.history.appendleft(
                {
                    "node_id": request.node_id,
                    "approved": approved,
                    "reason": reason,
                    "decided_by": by,
                    "sim_time": request.sim_time,
                }
            )
        return ApprovalDecision(
            sim_time=request.sim_time,
            run_id=request.run_id,
            seed=request.seed,
            config_hash=request.config_hash,
            node_id=request.node_id,
            level=request.level,
            approved=approved,
            reason=reason,
            decided_by=by,
            decider=DeciderKind.HUMAN,
            delay_sim=0.0,
        )


@dataclass
class ConsoleAdjudicator:
    """Every remembered incident waits for an operator to say what it meant."""

    actor_id: str = "console"
    delay_sim: float = 0.0

    def adjudicate(self, record: Any) -> str | None:
        return None


DIMENSIONS = ("identity", "behavioral", "device", "network")

ATTACKS: dict[str, dict[str, Any]] = {
    "compromise": {
        "title": "Device compromise",
        "family": "Fleet",
        "summary": "One device's telemetry degrades on the chosen dimensions.",
        "defends": "C1 continuous trust, C4 graduated response, M9 capability gate",
        "targets": 1,
        "defaults": {"severity": 0.6, "duration": 25, "dimensions": list(DIMENSIONS)},
    },
    "low_and_slow": {
        "title": "Low-and-slow",
        "family": "Fleet",
        "summary": "A mild, long degradation that never crosses a single-report threshold.",
        "defends": "C1 EWMA trust and fleet correlation; binary Zero Trust misses it",
        "targets": 1,
        "defaults": {"severity": 0.35, "duration": 60, "dimensions": ["behavioral", "network"]},
    },
    "campaign": {
        "title": "Distributed campaign",
        "family": "Fleet",
        "summary": "Several devices degrade together, each only moderately.",
        "defends": "C2 collaborative threat intelligence (fleet correlation)",
        "targets": 5,
        "defaults": {"severity": 0.3, "duration": 25, "dimensions": list(DIMENSIONS)},
    },
    "on_off": {
        "title": "On-off attacker",
        "family": "Fleet",
        "summary": "Active a few ticks, quiet a few ticks, to stay under the radar.",
        "defends": "Hysteresis and reputation; below a 2-in-5 duty cycle it evades (reported)",
        "targets": 1,
        "defaults": {"severity": 0.6, "duration": 40, "on": 2, "period": 5},
    },
    "crash": {
        "title": "Mass device crash",
        "family": "Resilience",
        "summary": "Devices go dark and come back rebooted, monitors restarted.",
        "defends": "Correlated-outage grouping, silence handling, fail-static response",
        "targets": 5,
        "defaults": {"duration": 8},
    },
    "congestion": {
        "title": "Benign fleet congestion",
        "family": "Resilience",
        "summary": "The whole fleet's network dimension dips. Not an attack.",
        "defends": "Cohort baseline and the mass-restriction brake (false-positive control)",
        "targets": 0,
        "defaults": {"severity": 0.35, "duration": 10},
    },
    "compromised_monitor": {
        "title": "Compromised monitor (ballot-stuffing)",
        "family": "Defender",
        "summary": "A monitor claims perfect health while its device degrades.",
        "defends": "Report step check, M11 outlier quarantine",
        "targets": 1,
        "defaults": {"severity": 0.7, "duration": 25},
    },
    "whitewash": {
        "title": "Whitewashing",
        "family": "Defender",
        "summary": "A compromised monitor restarts itself to reset its device's trust.",
        "defends": "Fusion keeps history; a restarted monitor cannot launder trust (V3)",
        "targets": 1,
        "defaults": {"severity": 0.6, "duration": 30, "every": 3},
    },
    "selective": {
        "title": "Selective reporting",
        "family": "Defender",
        "summary": "A compromised monitor stays silent on every incriminating tick.",
        "defends": "Intermittent-silence detection (M10 persona invariant)",
        "targets": 1,
        "defaults": {"severity": 0.6, "duration": 30},
    },
    "impersonation": {
        "title": "Impersonation",
        "family": "Defender",
        "summary": "Someone without the monitor's key reports a healthy device as failing.",
        "defends": "Signed telemetry under per-agent NHI",
        "targets": 1,
        "defaults": {"duration": 15},
    },
    "cross_report": {
        "title": "Compromised agent speaks for others",
        "family": "Defender",
        "summary": "A real, signed monitor reports other devices as failing.",
        "defends": "Provisioned device-to-monitor binding (M10)",
        "targets": 3,
        "defaults": {"duration": 15},
    },
    "sybil": {
        "title": "Sybil flood",
        "family": "Defender",
        "summary": "Two hundred fake devices join and report perfect health.",
        "defends": "Signed telemetry: unattributable reports never reach the orchestrator",
        "targets": 0,
        "defaults": {"duration": 10, "count": 200},
    },
    "future_dating": {
        "title": "Watermark poisoning",
        "family": "Defender",
        "summary": "A monitor stamps its reports in the future to steer tick sealing.",
        "defends": "The orchestrator's own clock (V2)",
        "targets": 1,
        "defaults": {"duration": 15},
    },
    "memory_poison": {
        "title": "Immune-memory poisoning",
        "family": "Defender",
        "summary": "Unattested, forged, sub-quorum and mislabelled memory writes.",
        "defends": "M11 k-of-n quorum, recomputed labels, operator adjudication",
        "targets": 0,
        "defaults": {"duration": 20},
    },
    "healing_abuse": {
        "title": "Weaponised self-healing",
        "family": "Defender",
        "summary": "Drive a healthy device down, let it heal, repeat: an outage from the cure.",
        "defends": "Human-approved isolation, heal budget, ceiling-only reintegration",
        "targets": 1,
        "defaults": {"duration": 32},
    },
    "lying_correlation": {
        "title": "Lying correlation agent",
        "family": "Defender",
        "summary": "The correlation agent implicates the entire fleet.",
        "defends": "Correlation recomputed from the batch every tick, own-evidence gate",
        "targets": 0,
        "defaults": {"duration": 15},
    },
}


@dataclass
class Attack:
    attack_id: str
    kind: str
    targets: list[str]
    params: dict[str, Any]
    start: int
    end: int
    launched_by: str
    adversary: Any | None = None
    counters_at_start: dict[str, int] = field(default_factory=dict)
    first_seen: dict[str, dict[int, int]] = field(default_factory=dict)
    peak: dict[str, int] = field(default_factory=dict)
    executed: Counter[str] = field(default_factory=Counter)
    refused: Counter[str] = field(default_factory=Counter)
    timeline: list[dict[str, Any]] = field(default_factory=list)
    defences: dict[str, int] = field(default_factory=dict)

    @property
    def title(self) -> str:
        return ATTACKS[self.kind]["title"]


class LiveFleet:
    def __init__(self, *, n_nodes: int = N_NODES, seed: int = SEED, tick_seconds: float = 1.0):
        self.n_nodes = n_nodes
        self.seed = seed
        self.tick_seconds = tick_seconds
        self.speed = 1.0
        self.catalogue = fleet_catalogue(n_nodes)
        self._commands: deque[tuple[str, dict[str, Any], Future]] = deque()
        self._lock = threading.Lock()
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._paused = False
        self._snapshot: dict[str, Any] = {"ready": False}
        self._thread: threading.Thread | None = None
        self.errors: deque[str] = deque(maxlen=20)

    def start(self) -> None:
        self._thread = threading.Thread(target=self._main, name="dis-live-fleet", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._wake.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return self._snapshot

    def submit(self, command: str, **payload: Any) -> Future:
        future: Future = Future()
        with self._lock:
            self._commands.append((command, payload, future))
        self._wake.set()
        return future

    def _main(self) -> None:
        try:
            self._build()
        except Exception:  # noqa: BLE001
            self.errors.appendleft(traceback.format_exc(limit=6))
            with self._lock:
                self._snapshot = {"ready": False, "errors": list(self.errors)}
            return
        self._publish()
        while not self._stop.is_set():
            self._apply_commands()
            if not self._paused:
                try:
                    self._tick()
                except Exception:  # noqa: BLE001
                    self.errors.appendleft(traceback.format_exc(limit=4))
                    self.t += 1
                self._publish()
            self._wake.clear()
            self._wake.wait(timeout=None if self._paused else self.tick_seconds / self.speed)

    def _build(self) -> None:
        from agents.approval import ApprovalGate
        from agents.orchestrator import Orchestrator
        from m1_monitoring.agent import MonitoringAgent
        from m1_monitoring.sensors.synthetic import SyntheticTelemetry
        from m8_eval_harness import baselines
        from m8_eval_harness.params import FROZEN
        from m8_eval_harness.scenario_runner import (
            RunContext,
            _fleet_identities,
            _verifying_view,
        )
        from m8_eval_harness.simulator import DEFAULT_CONFIG, _publisher_view, trust_settings
        from m9_capability_binder import binder
        from shared.bus import InProcBus
        from shared.clock import ManualClock
        from shared.run_manifest import config_hash, load_yaml_config

        binder.reset_spent_tokens()
        cfg = FROZEN.apply_to_config(load_yaml_config(DEFAULT_CONFIG))
        self.config_hash = config_hash(cfg)
        self.params, weights = trust_settings(cfg)
        self.bus = InProcBus()
        nodes = list(self.catalogue)
        self.identities = _fleet_identities(self.n_nodes, RUN_ID)
        self.policy = ConsoleApproval()
        self.gate = ApprovalGate(self.policy)
        self.pipeline = baselines.by_id("full_mediated").pipeline(
            bus=self.bus,
            run_id=RUN_ID,
            seed=self.seed,
            config_hash=self.config_hash,
            params=FROZEN,
            approval=self.gate,
        )
        self.pipeline.adjudicator = ConsoleAdjudicator()
        self.verified = _verifying_view(self.bus, self.identities)
        self.clock = ManualClock(0.0)
        self.orchestrator = Orchestrator(
            bus=self.verified,
            run_id=RUN_ID,
            seed=self.seed,
            config_hash=self.config_hash,
            pipeline=self.pipeline,
            node_agent_binding={n: f"mon-{n}" for n in nodes},
            bind_on_first_sight=False,
            clock=self.clock,
            observers=tuple((self.pipeline.attesters or {}).values()),
        )
        self.orchestrator.attach()
        self.sensor = SyntheticTelemetry(self.seed)
        self.anomalies: dict[str, tuple[float, ...]] = self.sensor._anomalies
        self.masks: dict[str, tuple[str, ...]] = self.sensor._masks
        self.agents = {
            n: MonitoringAgent(
                node_id=n,
                agent_id=f"mon-{n}",
                sensor=self.sensor,
                bus=_publisher_view(self.bus, self.identities, f"mon-{n}"),
                clock=self.clock,
                run_id=RUN_ID,
                seed=self.seed,
                config_hash=self.config_hash,
                trust_params=self.params,
                obs_weights=weights,
            )
            for n in nodes
        }
        self.context = RunContext(
            bus=self.bus,
            run_id=RUN_ID,
            seed=self.seed,
            config_hash=self.config_hash,
            pipeline=self.pipeline,
            identities=self.identities,
        )
        self.t = 0
        self.down: dict[str, tuple[int, int]] = {}
        self.forged: dict[str, tuple[int, int]] = {}
        self.restarts: dict[str, tuple[int, int, int]] = {}
        self.selective: dict[str, tuple[int, int]] = {}
        self.benign: dict[str, int] = {}
        self.attacks: dict[str, Attack] = {}
        self._attack_seq = 0
        self.history: dict[str, deque] = {n: deque(maxlen=HISTORY) for n in nodes}
        self.ticks: deque[dict[str, Any]] = deque(maxlen=HISTORY)
        self.events: deque[dict[str, Any]] = deque(maxlen=400)
        self.incidents: list[dict[str, Any]] = []
        self._open_incident: dict[str, dict[str, Any]] = {}
        self._last_level = dict.fromkeys(nodes, 0)
        self._enforced: dict[str, int] = {}
        self._last_phase = dict.fromkeys(nodes, "idle")
        self._last_counters: dict[str, int] = {}
        self._memory_seen: dict[str, str] = {}
        self._audit_ok: bool | None = True
        self._devices: list[dict[str, Any]] | None = None
        self._counters_now: dict[str, int] = {}
        self._event("system", f"Fleet of {self.n_nodes} devices started", level="info")

    def _tick(self) -> None:
        from m1_monitoring.core.trust import TrustState
        from m8_eval_harness.simulator import _forged_tick

        t = self.t
        self.clock.set(float(t))
        for attack in self._active():
            if attack.adversary is not None:
                attack.adversary.before_tick(self.context, float(t))
            self._attack_publish(attack, t)
        for node, agent in self.agents.items():
            window = self.down.get(node)
            if window and window[0] <= t < window[1]:
                agent.state = TrustState.initial(self.params, sim_time=float(t))
                continue
            sel = self.selective.get(node)
            if sel and sel[0] <= t < sel[1] and self.sensor.anomaly_active(float(t), node):
                continue
            spec = self.restarts.get(node)
            if spec and spec[0] <= t < spec[1] and (t - spec[0]) % spec[2] == 0:
                agent.state = TrustState.initial(self.params, sim_time=float(t))
            forged = self.forged.get(node)
            if forged and forged[0] <= t < forged[1]:
                _forged_tick(agent)
            else:
                agent.tick()
        self.clock.set(float(t + 1))
        self.orchestrator.seal_due()
        self._withdraw_ended_questions()
        outcome = self.pipeline.outcomes[-1] if self.pipeline.outcomes else None
        if outcome is not None and outcome.sim_time != float(t):
            outcome = None
        for attack in self._active():
            if attack.adversary is not None:
                attack.adversary.after_tick(self.context, float(t), outcome)
        self._record(t, outcome)
        self._expire(t)
        self.t += 1

    def _withdraw_ended_questions(self) -> None:
        """Drop questions whose episode ended before anyone answered them."""
        for node_id in [n for n in self.policy.pending if not self.gate.is_open(n)]:
            self.policy.pending.pop(node_id)
            unused = self.policy.answers.pop(node_id, None)
            what = "mass-restriction" if node_id == "fleet" else "isolation"
            note = " (the answer given was not applied)" if unused else ""
            self._event(
                "gate",
                f"{what} question for {self._name(node_id)} withdrawn: the episode ended{note}",
                **({} if node_id == "fleet" else {"node": node_id}),
            )

    def _active(self) -> list[Attack]:
        return [a for a in self.attacks.values() if a.start <= self.t < a.end]

    def _attack_publish(self, attack: Attack, t: int) -> None:
        """Attacks that are traffic rather than device behaviour."""
        from agents.orchestrator import TRUST_TOPIC
        from m8_eval_harness.scenarios.adversaries import _update
        from m10_persona_drift.nhi import issue_identity
        from shared.secure_bus import SignedBus

        if attack.kind == "impersonation":
            victim = attack.targets[0]
            forged = _update(
                node_id=victim,
                agent_id=f"mon-{victim}",
                level=0.03,
                sim_time=float(t),
                run=self.context,
            )
            self.bus.publish(TRUST_TOPIC, forged)
            rogue = SignedBus(
                inner=self.bus,
                identity=issue_identity(f"mon-{victim}", seed=b"rogue".ljust(32, b"\0")),
                topics=frozenset({TRUST_TOPIC}),
            )
            rogue.publish(TRUST_TOPIC, forged)

    def _counters(self) -> dict[str, int]:
        p, o = self.pipeline, self.orchestrator
        denials = getattr(p.engine, "denials", {})
        broker = getattr(p, "broker", None)
        broker = getattr(broker, "inner", broker)
        return {
            "telemetry_refused": self.verified.rejected_count,
            "unbound_reports": o.unbound_updates,
            "future_reports": o.future_updates,
            "late_reports": o.late_updates,
            "duplicate_reports": o.duplicate_updates,
            "rate_limited_reports": o.rate_limited_updates,
            "foreign_reports": o.foreign_updates,
            "trust_rise_capped": getattr(p.fusion, "trust_rise_capped", 0),
            "agents_quarantined": len(getattr(p, "agents_quarantined", ())),
            "persona_violations": getattr(p, "persona_violations", 0),
            "correlation_overstated": getattr(p, "correlation_overstated", 0),
            "restrictions_withheld": getattr(p, "restrictions_withheld", 0),
            "memory_writes_denied": getattr(p, "memory_writes_denied", 0),
            "actions_refused": sum(denials.values()),
            "broker_requests": getattr(broker, "requests", 0) if broker else 0,
            "broker_denied": int(getattr(broker, "denied_total", 0)) if broker else 0,
            "pipeline_failures": o.pipeline_failures,
            "handler_errors": self.bus.handler_errors,
            "degraded_stages": sum(p.degraded.values()),
            "poison_attempts": sum(
                getattr(a.adversary, "attempts", 0)
                for a in self.attacks.values()
                if a.kind == "memory_poison"
            ),
            "poison_accepted": sum(
                getattr(a.adversary, "accepted", 0)
                for a in self.attacks.values()
                if a.kind == "memory_poison"
            ),
        }

    def _record(self, t: int, outcome: Any) -> None:
        engine = self.pipeline.engine
        healer = getattr(self.pipeline, "healer", None)
        gt_by = {u.node_id: u for u in (outcome.gt_updates if outcome else [])}
        planned = {p.node_id: int(p.proposed_level) for p in (outcome.plans if outcome else [])}
        executed_now: dict[str, int] = {}
        refused_now: dict[str, str] = {}
        if outcome is not None:
            for plan, result in zip(outcome.plans, outcome.executions, strict=True):
                if result.executed and result.level is not None:
                    self._enforced[plan.node_id] = int(result.level)
                    if int(result.level) > 0:
                        executed_now[plan.node_id] = int(result.level)
                elif not result.executed and result.decision is not None:
                    refused_now[plan.node_id] = result.decision.deny_reason or "refused"
        devices = []
        for node, info in self.catalogue.items():
            gt = gt_by.get(node)
            derived = int(engine.effective_level(node))
            level = self._enforced.get(node, 0)
            phase = healer.state(node).phase.value if healer is not None else "idle"
            row = {
                "id": node,
                **info,
                "ts": round(gt.ts, 4) if gt else None,
                "gt": round(gt.gt, 4) if gt else None,
                "cti": round(gt.cti_i, 4) if gt else None,
                "rep": round(gt.rep, 4) if gt else None,
                "drift": bool(gt.drift_flag) if gt else False,
                "planned": planned.get(node, 0),
                "derived": derived,
                "level": level,
                "isolation_withheld": derived == 4 and level < 4,
                "healing": phase,
                "reporting": gt is not None,
                "under_attack": any(node in a.targets for a in self._active()),
            }
            devices.append(row)
            with self._lock:
                self.history[node].append(
                    {
                        "t": t,
                        "ts": row["ts"],
                        "gt": row["gt"],
                        "level": level,
                        "planned": row["planned"],
                    }
                )
            self._track_device(t, node, row, executed_now.get(node), refused_now.get(node))
        counters = self._counters()
        self._track_counters(t, counters)
        self._track_memory(t)
        if t % 10 == 0:
            self._audit_ok = engine.audit.verify() is None
        tick = self._stage_trace(t, outcome, executed_now, refused_now)
        with self._lock:
            self.ticks.append(tick)
        for attack in self.attacks.values():
            self._track_attack(attack, t, devices, counters, tick)
        self._devices = devices
        self._counters_now = counters

    def _stage_trace(self, t, outcome, executed_now, refused_now) -> dict[str, Any]:  # type: ignore[no-untyped-def]
        if outcome is None:
            return {"t": t, "sealed": False}
        c, k, r = outcome.correlation, outcome.classification, outcome.report
        levels = Counter(int(p.proposed_level) for p in outcome.plans)
        return {
            "t": t,
            "sealed": True,
            "reports": len(outcome.gt_updates),
            "correlation": {
                "cti": round(c.cti, 4),
                "implicated": list(c.implicated_node_ids),
                "recall_boost": round(c.recall_boost, 4),
                "corroboration": round(getattr(c, "campaign_corroboration", 0.0), 4),
            },
            "classification": {
                "label": k.threat_type,
                "severity": round(k.severity, 3),
                "rules_label": k.rules_threat_type,
                "agree": k.classifiers_agree,
                "used_llm": k.used_llm,
            },
            "levels": {str(level): n for level, n in sorted(levels.items())},
            "executed": executed_now,
            "refused": refused_now,
            "verifier": {"verdict": str(r.verdict.value), "findings": r.codes()[:12]},
            "approvals": [
                {"node_id": d.node_id, "approved": d.approved, "reason": d.reason}
                for d in outcome.approvals
                if d.required
            ],
            "healing": [{"node_id": e.node_id, "phase": e.phase} for e in outcome.healing],
        }

    def _track_device(self, t, node, row, executed, refused) -> None:  # type: ignore[no-untyped-def]
        level, before = row["level"], self._last_level[node]
        name = row["name"]
        if level != before:
            direction = "raised" if level > before else "lowered"
            tone = "bad" if level >= 3 else "warn" if level >= 1 else "ok"
            self._event(
                "response",
                f"{name} {direction} to L{level} ({LEVEL_NAMES[level]})",
                node=node,
                level=tone,
                detail=f"GT {row['gt']}, own trust {row['ts']}" if row["gt"] is not None else "",
            )
        if refused:
            self._event("gate", f"Action on {name} refused: {refused}", node=node, level="warn")
        if row["healing"] != self._last_phase[node]:
            self._event(
                "healing", f"{name}: self-healing {row['healing']}", node=node, level="info"
            )
        self._last_phase[node] = row["healing"]
        episode = self._open_incident.get(node)
        if episode is None and level >= 2:
            episode = {
                "id": f"inc-{len(self.incidents) + 1:04d}",
                "node_id": node,
                "name": name,
                "opened": t,
                "closed": None,
                "peak": level,
                "attack": next((a.attack_id for a in self._active() if node in a.targets), None),
                "actions": 0,
            }
            self.incidents.append(episode)
            self._open_incident[node] = episode
        if episode is not None:
            episode["peak"] = max(episode["peak"], level)
            if executed:
                episode["actions"] += 1
            if level == 0:
                episode["closed"] = t
                del self._open_incident[node]
        self._last_level[node] = level
        del self.incidents[:-200]

    _COUNTER_EVENTS = {
        "telemetry_refused": ("identity", "Unsigned or wrongly signed telemetry refused", "warn"),
        "unbound_reports": (
            "identity",
            "Report from a monitor not bound to that device refused",
            "warn",
        ),
        "future_reports": ("clock", "Report stamped in the future refused", "warn"),
        "late_reports": ("clock", "Report for an already sealed tick refused", "info"),
        "trust_rise_capped": (
            "fusion",
            "Trust rise capped by the step check (forged observation)",
            "warn",
        ),
        "agents_quarantined": ("M11", "Reporter quarantined as statistically inconsistent", "bad"),
        "persona_violations": ("M10", "Monitor exceeded its report budget", "warn"),
        "correlation_overstated": (
            "correlation",
            "Correlation claimed more than the batch supports; capped",
            "warn",
        ),
        "restrictions_withheld": ("brake", "Mass-restriction brake withheld restrictions", "warn"),
        "memory_writes_denied": ("M9", "Memory write denied by the capability gate", "warn"),
        "poison_attempts": ("M11", "Immune-memory write attempted by the attacker", "warn"),
        "poison_accepted": ("M11", "Poisoned memory write ACCEPTED", "bad"),
        "pipeline_failures": (
            "system",
            "Pipeline stage failed; responses held (fail-static)",
            "bad",
        ),
    }

    def _track_counters(self, t: int, counters: dict[str, int]) -> None:
        for key, (source, text, tone) in self._COUNTER_EVENTS.items():
            delta = counters.get(key, 0) - self._last_counters.get(key, 0)
            if delta > 0 and self._last_counters:
                self._event(source, f"{text} ×{delta}", level=tone)
        self._last_counters = counters

    def _track_memory(self, t: int) -> None:
        store = getattr(getattr(self.pipeline, "curator", None), "store", None)
        if store is None:
            return
        for record in store.all_records():
            status = self._memory_seen.get(record.record_id)
            if status != record.status:
                if status is None:
                    self._event(
                        "memory",
                        f"Incident stored in immune memory ({record.threat_type}), awaiting review",
                        level="info",
                    )
                self._memory_seen[record.record_id] = record.status

    def _track_attack(self, attack: Attack, t: int, devices, counters, tick) -> None:  # type: ignore[no-untyped-def]
        if t < attack.start or t > attack.end + 30:
            return
        by_id = {d["id"]: d for d in devices}
        notes = []
        for node in attack.targets:
            d = by_id.get(node)
            if d is None:
                continue
            seen = attack.first_seen.setdefault(node, {})
            for lvl in (1, 2, 3, 4):
                if d["level"] >= lvl and lvl not in seen:
                    seen[lvl] = t
                    notes.append(f"{d['name']} reached L{lvl} ({LEVEL_NAMES[lvl]}) at tick {t}")
            attack.peak[node] = max(attack.peak.get(node, 0), d["level"])
            if node in tick.get("executed", {}):
                attack.executed[LEVEL_NAMES[tick["executed"][node]]] += 1
            if node in tick.get("refused", {}):
                attack.refused[tick["refused"][node]] += 1
            if (
                node in tick.get("correlation", {}).get("implicated", [])
                and "implicated" not in seen
            ):
                seen["implicated"] = t  # type: ignore[index]
                notes.append(f"Correlation implicated {d['name']} at tick {t}")
        defences = {
            k: counters[k] - attack.counters_at_start.get(k, 0)
            for k in counters
            if counters[k] - attack.counters_at_start.get(k, 0) > 0
        }
        if notes or t == attack.end:
            attack.timeline.append({"t": t, "notes": notes or ["Attack window closed"]})
        attack.defences = defences

    def _expire(self, t: int) -> None:
        for attack in self.attacks.values():
            if attack.end == t + 1:
                self._event(
                    "attack", f"{attack.title} ended", level="info", attack=attack.attack_id
                )

    def _event(self, source: str, text: str, *, level: str = "info", **extra: Any) -> None:
        self.events.appendleft(
            {"t": getattr(self, "t", 0), "source": source, "text": text, "tone": level, **extra}
        )

    def _apply_commands(self) -> None:
        while True:
            with self._lock:
                if not self._commands:
                    return
                command, payload, future = self._commands.popleft()
            try:
                result = getattr(self, f"_cmd_{command}")(**payload)
                future.set_result(result)
            except Exception as exc:  # noqa: BLE001
                future.set_exception(exc)
            self._publish()

    def _cmd_approve(self, node_id: str, approved: bool, reason: str, user: str) -> dict:
        from agents.approval import MAX_REASON_CHARS

        reason = (reason or ("approved" if approved else "denied")).strip()[:MAX_REASON_CHARS]
        if node_id == "fleet":
            if "fleet" not in self.policy.pending:
                raise ValueError("no mass-restriction question is waiting")
            self.policy.answers["fleet"] = (approved, reason, f"operator:{user}")
            self.gate.clear_mass_restriction()
        else:
            if node_id not in self.policy.pending:
                raise ValueError("no isolation request is waiting for that device")
            self.policy.answers[node_id] = (approved, reason, f"operator:{user}")
            self.gate.reconsider(node_id)
        verdict = "approved" if approved else "denied"
        self._event(
            "operator",
            f"{user} {verdict} isolation of {self._name(node_id)}",
            node=node_id,
            level="bad" if approved else "info",
        )
        return {"ok": True}

    def _cmd_reconsider(self, node_id: str, user: str) -> dict:
        self.gate.reconsider(node_id)
        self._event(
            "operator", f"{user} asked for {self._name(node_id)} to be reconsidered", node=node_id
        )
        return {"ok": True}

    def _cmd_grant_heal(self, node_id: str, user: str) -> dict:
        self.pipeline.grant_heal(node_id)
        self._event("operator", f"{user} released {self._name(node_id)} for healing", node=node_id)
        return {"ok": True}

    def _cmd_adjudicate(self, record_id: str, status: str, user: str) -> dict:
        store = self.pipeline.curator.store
        record = store.adjudicate(
            record_id, status, actor=f"operator:{user}", sim_time=float(self.t)
        )
        self._memory_seen[record_id] = record.status
        self._event("memory", f"{user} marked an incident {status}", level="info")
        return {"ok": True}

    def _cmd_rebind(self, node_id: str, agent_id: str, user: str) -> dict:
        if node_id not in self.catalogue:
            raise ValueError("unknown device")
        self.orchestrator.rebind(node_id, agent_id, by=f"admin:{user}")
        self._event(
            "admin", f"{user} bound {self._name(node_id)} to {agent_id}", node=node_id, level="warn"
        )
        return {"ok": True}

    def _cmd_control(self, action: str, user: str, speed: float | None = None) -> dict:
        if action == "pause":
            self._paused = True
        elif action == "resume":
            self._paused = False
        elif action == "speed":
            if speed is None or not 0.25 <= speed <= 8:
                raise ValueError("speed must be between 0.25 and 8")
            self.speed = float(speed)
        elif action == "reset":
            self._build()
        else:
            raise ValueError("unknown control action")
        self._event("admin", f"{user}: fleet {action}", level="info")
        return {"ok": True}

    def _cmd_launch(
        self, kind: str, user: str, targets: list[str] | None = None, **params: Any
    ) -> dict:
        from m8_eval_harness.scenarios.adversaries import (
            CompromisedAgent,
            FutureDating,
            HealingWeaponiser,
            LyingCorrelation,
            MemoryPoisoner,
            SybilPadding,
        )

        spec = ATTACKS.get(kind)
        if spec is None:
            raise ValueError("unknown attack")
        merged = {**spec["defaults"], **{k: v for k, v in params.items() if v is not None}}
        duration = int(merged.get("duration", 20))
        if not 1 <= duration <= 200:
            raise ValueError("duration must be 1-200 ticks")
        severity = float(merged.get("severity", 0.5))
        if not 0.0 < severity <= 1.0:
            raise ValueError("severity must be in (0, 1]")
        dims = (
            tuple(d for d in merged.get("dimensions", DIMENSIONS) if d in DIMENSIONS) or DIMENSIONS
        )
        chosen = self._pick_targets(spec["targets"], targets)
        start, end = self.t, self.t + duration
        self._attack_seq += 1
        attack = Attack(
            attack_id=f"atk-{self._attack_seq:03d}",
            kind=kind,
            targets=chosen,
            params=merged,
            start=start,
            end=end,
            launched_by=user,
            counters_at_start=dict(self._counters_now or self._counters()),
        )
        if kind in (
            "compromise",
            "low_and_slow",
            "campaign",
            "compromised_monitor",
            "whitewash",
            "selective",
        ):
            for node in chosen:
                self.anomalies[node] = (float(start), float(end), severity)
                self.masks[node] = dims
        if kind == "on_off":
            on, period = int(merged["on"]), int(merged["period"])
            if not 0 < on < period:
                raise ValueError("a pulse needs 0 < on < period")
            for node in chosen:
                self.anomalies[node] = (float(start), float(end), severity, on, period)
                self.masks[node] = dims
        if kind == "congestion":
            for node in self.catalogue:
                if node not in self.anomalies or self.anomalies[node][1] <= start:
                    self.anomalies[node] = (float(start), float(end), severity)
                    self.masks[node] = ("network",)
                    self.benign[node] = end
        if kind == "crash":
            for node in chosen:
                self.down[node] = (start, end)
        if kind == "compromised_monitor":
            for node in chosen:
                self.forged[node] = (start, end)
        if kind == "whitewash":
            for node in chosen:
                self.restarts[node] = (start, end, max(2, int(merged.get("every", 3))))
        if kind == "selective":
            for node in chosen:
                self.selective[node] = (start, end)
        if kind == "cross_report":
            own = self._pick_targets(1, None, exclude=chosen)[0]
            attack.adversary = CompromisedAgent(
                victim_ids=tuple(chosen), own_node=own, start_sim=start
            )
            attack.params["compromised_monitor"] = own
        if kind == "sybil":
            attack.adversary = SybilPadding(count=int(merged.get("count", 200)), start_sim=start)
        if kind == "future_dating":
            attack.adversary = FutureDating(node_id=chosen[0])
        if kind == "memory_poison":
            curator = self.pipeline.curator
            attack.adversary = MemoryPoisoner(
                write_path=curator,
                registry={n: a.identity for n, a in self.pipeline.attesters.items()},
                start_sim=start,
                every=2.0,
            )
        if kind == "healing_abuse":
            attack.adversary = HealingWeaponiser(target=chosen[0], start_sim=start)
        if kind == "lying_correlation":
            attack.adversary = LyingCorrelation(start_sim=start)
        self.attacks[attack.attack_id] = attack
        names = ", ".join(self._name(n) for n in chosen) or "the fleet"
        self._event(
            "attack",
            f"{user} launched {attack.title} on {names}",
            level="bad",
            attack=attack.attack_id,
        )
        return {"attack_id": attack.attack_id, "targets": chosen}

    def _cmd_stop_attack(self, attack_id: str, user: str) -> dict:
        attack = self.attacks.get(attack_id)
        if attack is None:
            raise ValueError("unknown attack")
        if attack.end > self.t:
            attack.end = self.t
            for node in attack.targets:
                spec = self.anomalies.get(node)
                if spec and spec[1] > self.t:
                    self.anomalies[node] = (spec[0], float(self.t), *spec[2:])
                for table in (self.down, self.forged, self.selective):
                    if node in table:
                        table[node] = (table[node][0], self.t)
                if node in self.restarts:
                    s = self.restarts[node]
                    self.restarts[node] = (s[0], self.t, s[2])
            if attack.kind == "congestion":
                for node, spec in list(self.anomalies.items()):
                    if self.benign.get(node) and spec[1] > self.t:
                        self.anomalies[node] = (spec[0], float(self.t), *spec[2:])
            self._event("attack", f"{user} stopped {attack.title}", level="info", attack=attack_id)
        return {"ok": True}

    def _pick_targets(self, count: int, requested: list[str] | None, exclude=()) -> list[str]:  # type: ignore[no-untyped-def]
        if requested:
            unknown = [n for n in requested if n not in self.catalogue]
            if unknown:
                raise ValueError(f"unknown devices: {', '.join(unknown)}")
            chosen = list(dict.fromkeys(requested))[: max(count, 1)]
            if len(chosen) < count:
                chosen += self._pick_targets(count - len(chosen), None, exclude=[*exclude, *chosen])
            return chosen
        busy = {n for a in self._active() for n in a.targets}
        healthy = [
            n
            for n in self.catalogue
            if n not in busy and n not in exclude and self._last_level.get(n, 0) == 0
        ]
        rotation = self._attack_seq * 7
        ordered = (
            healthy[rotation % max(len(healthy), 1) :] + healthy[: rotation % max(len(healthy), 1)]
        )
        return ordered[:count]

    def _name(self, node_id: str) -> str:
        return self.catalogue.get(node_id, {}).get("name", node_id)

    def _publish(self) -> None:
        from m9_capability_binder.binder import implementation
        from shared.keys import using_development_key

        devices = self._devices
        if devices is None:
            devices = [
                {
                    "id": n,
                    **info,
                    "ts": None,
                    "gt": None,
                    "cti": None,
                    "rep": None,
                    "drift": False,
                    "planned": 0,
                    "derived": 0,
                    "level": 0,
                    "isolation_withheld": False,
                    "healing": "idle",
                    "reporting": False,
                    "under_attack": False,
                }
                for n, info in self.catalogue.items()
            ]
        store = getattr(getattr(self.pipeline, "curator", None), "store", None)
        memory = [
            {
                "id": r.record_id,
                "threat_type": r.threat_type,
                "nodes": list(r.node_ids),
                "window": [r.window_start_sim, r.window_end_sim],
                "status": r.status,
                "certified": bool(r.quorum_certificate),
                "pattern": r.pattern_text[:160],
                "adjudicated_by": getattr(r, "adjudicated_by", None),
            }
            for r in (store.all_records() if store is not None else [])
        ]
        audit = self.pipeline.engine.audit
        checkpoint = audit.checkpoint()
        tail = []
        for entry in itertools.islice(reversed(audit._chain), 60):
            record, payload = entry.record, entry.record.payload
            tail.append(
                {
                    "t": record.sim_time,
                    "event": record.event_type,
                    "actor": record.actor_id,
                    "node": payload.get("node_id"),
                    "level": payload.get("level"),
                    "capability": payload.get("capability"),
                    "reason": payload.get("deny_reason") or payload.get("reason"),
                    "withheld": bool(payload.get("isolation_withheld")),
                    "hash": entry.hash[:12],
                }
            )
        snapshot = {
            "ready": True,
            "tick": self.t,
            "paused": self._paused,
            "speed": self.speed,
            "run_id": RUN_ID,
            "devices": devices,
            "counts": dict(Counter(d["level"] for d in devices)),
            "events": list(self.events)[:120],
            "incidents": [dict(i) for i in reversed(self.incidents[-100:])],
            "approvals": {
                "pending": list(self.policy.pending.values()),
                "history": list(self.policy.history)[:50],
            },
            "memory": memory[-100:],
            "attacks": [self._attack_view(a) for a in reversed(list(self.attacks.values())[-30:])],
            "last_tick": self.ticks[-1] if self.ticks else None,
            "counters": self._counters_now,
            "audit": tail,
            "health": {
                "binder": implementation(),
                "development_key": using_development_key(),
                "audit_records": len(audit),
                "audit_head": checkpoint.head[:16],
                "audit_intact": self._audit_ok,
                "bus_messages": self.bus.published,
                "errors": list(self.errors)[:5],
                "quarantined": sorted(getattr(self.pipeline, "agents_quarantined", ())),
            },
        }
        with self._lock:
            self._snapshot = snapshot

    def _attack_view(self, a: Attack) -> dict[str, Any]:
        return {
            "id": a.attack_id,
            "kind": a.kind,
            "title": a.title,
            "family": ATTACKS[a.kind]["family"],
            "defends": ATTACKS[a.kind]["defends"],
            "targets": [{"id": n, "name": self._name(n)} for n in a.targets],
            "params": a.params,
            "start": a.start,
            "end": a.end,
            "active": a.start <= self.t < a.end,
            "launched_by": a.launched_by,
            "first_seen": {n: {str(k): v for k, v in s.items()} for n, s in a.first_seen.items()},
            "peak": a.peak,
            "executed": dict(a.executed),
            "refused": dict(a.refused),
            "defences": a.defences,
            "timeline": a.timeline[-40:],
            "adversary": _adversary_view(a.adversary),
        }

    def device_detail(self, node_id: str) -> dict[str, Any]:
        with self._lock:
            history = list(self.history.get(node_id, ()))
        return {"history": history}

    def tick_history(self, count: int = 60) -> list[dict[str, Any]]:
        with self._lock:
            return list(self.ticks)[-count:]


def _adversary_view(adversary: Any) -> dict[str, Any] | None:
    if adversary is None:
        return None
    keys = (
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
    return {k: copy.copy(getattr(adversary, k)) for k in keys if hasattr(adversary, k)}
