"""The operator console, reading the container deployment."""

from __future__ import annotations

import threading
from collections import Counter, defaultdict, deque
from collections.abc import Callable
from concurrent.futures import Future
from typing import Any, Literal

from console.runtime import HISTORY, LEVEL_NAMES
from shared.schemas import (
    AdjudicationQuestion,
    AuditRecord,
    Classification,
    CorrelationResult,
    GlobalTrustUpdate,
    HealingEvent,
    OperatorQuestion,
    ResponsePlan,
)

PUBLISHER = "control"
AUDIT_TOPIC = "response.audit"
CLASSIFICATION_TOPIC = "classification.result"
VERIFIER_EVENT = "verifier.report"
QUESTION_TOPIC = "operator.question"
DECISION_TOPIC = "operator.decision"
READ_ONLY = (
    "this console follows the container deployment: it answers isolation questions and "
    "says what remembered incidents meant, and the control plane decides everything else"
)


def enforced_level(record: AuditRecord) -> int | None:
    """What the engine did, from its audit record: `None` when it did nothing."""
    if record.event_type != "response.executed":
        return None
    if record.payload.get("restriction_withheld"):
        return 2
    if record.payload.get("isolation_withheld"):
        return 3
    return int(record.payload.get("proposed_level", 0))


class StreamFleet:
    """`LiveFleet`'s read interface, fed by the broker instead of a pipeline."""

    def __init__(
        self, bus: Any, nodes: list[str], *, run_id: str = "", signer: Any | None = None
    ) -> None:
        from agents.correlation import CORRELATION_TOPIC
        from agents.orchestrator import ORCHESTRATOR_TOPIC
        from agents.planner import PLAN_TOPIC
        from m6_trust_fusion.fusion import GT_TOPIC
        from m7_self_healing import HEAL_TOPIC

        self.bus, self.run_id = bus, run_id
        bus.discover = False
        topics = (GT_TOPIC, PLAN_TOPIC, AUDIT_TOPIC, HEAL_TOPIC, ORCHESTRATOR_TOPIC)
        for topic in (*topics, CORRELATION_TOPIC, CLASSIFICATION_TOPIC, QUESTION_TOPIC):
            bus.subscribe(topic, self._on)
            bus.follow(topic, PUBLISHER)
        self.signer = signer
        self.pending: dict[str, Any] = {}
        self.answered: deque[dict[str, Any]] = deque(maxlen=50)
        self.reviews: dict[str, AdjudicationQuestion] = {}
        self.rows = {n: _blank(n) for n in nodes}
        self.history: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
        self.ticks: dict[int, dict[str, Any]] = {}
        self.events: deque[dict[str, Any]] = deque(maxlen=200)
        self.audit: deque[dict[str, Any]] = deque(maxlen=60)
        self.received: Counter[str] = Counter()
        self.worst = dict.fromkeys(nodes, 0)
        self.tick = -1
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._snapshot: dict[str, Any] = {"ready": False}

    def start(self) -> None:
        self._thread = threading.Thread(target=self._main, name="dis-stream-fleet", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return self._snapshot

    def submit(self, command: str, **payload: Any) -> Future:
        future: Future = Future()
        commands: dict[str, Callable[..., dict[str, Any]]] = {
            "approve": self._answer,
            "adjudicate": self._adjudicate,
        }
        try:
            if command not in commands or self.signer is None:
                raise ValueError(READ_ONLY)
            future.set_result(commands[command](**payload))
        except (ValueError, KeyError) as exc:
            future.set_exception(exc)
        return future

    def _answer(self, node_id: str, approved: bool, reason: str, user: str) -> dict[str, Any]:
        from agents.approval import MAX_REASON_CHARS
        from shared.attestation import decision_payload
        from shared.schemas import OperatorDecision

        with self._lock:
            question = self.pending.get(node_id)
        if question is None:
            raise ValueError("no isolation request is waiting for that device")
        reason = (reason or ("approved" if approved else "denied")).strip()[:MAX_REASON_CHARS]
        by = f"operator:{user}"
        signature = self.signer.sign(
            decision_payload(question.run_id, node_id, question.sim_time, approved, reason, by)
        )
        self.bus.publish(
            DECISION_TOPIC,
            OperatorDecision(
                sim_time=question.sim_time,
                run_id=question.run_id,
                seed=question.seed,
                config_hash=question.config_hash,
                node_id=node_id,
                approved=approved,
                reason=reason,
                decided_by=by,
                signature=signature,
            ),
        )
        with self._lock:
            self.answered.appendleft(
                {"node_id": node_id, "approved": approved, "reason": reason, "decided_by": by}
            )
        return {"ok": True}

    def _adjudicate(
        self, record_id: str, status: Literal["confirmed", "benign"], user: str
    ) -> dict[str, Any]:
        from shared.attestation import verdict_payload
        from shared.schemas import AdjudicationVerdict

        with self._lock:
            question = self.reviews.get(record_id)
        if question is None or not question.open:
            raise ValueError("no remembered incident is waiting for a verdict under that id")
        by = f"operator:{user}"
        assert self.signer is not None
        signature = self.signer.sign(
            verdict_payload(question.run_id, record_id, question.sim_time, status, by)
        )
        self.bus.publish(
            DECISION_TOPIC,
            AdjudicationVerdict(
                sim_time=question.sim_time,
                run_id=question.run_id,
                seed=question.seed,
                config_hash=question.config_hash,
                record_id=record_id,
                status=status,
                decided_by=by,
                signature=signature,
            ),
        )
        return {"ok": True}

    def device_detail(self, node_id: str) -> dict[str, Any]:
        with self._lock:
            entries = self.history.get(node_id, {})
            return {"history": [dict(entries[t]) for t in sorted(entries)]}

    def tick_history(self, count: int = 60) -> list[dict[str, Any]]:
        with self._lock:
            return [_view(self.ticks[t]) for t in sorted(self.ticks)[-count:]]

    def _main(self) -> None:
        while not self._stop.is_set():
            self.step()

    def step(self, timeout: float = 0.2) -> None:
        self.bus.pump(timeout=timeout)
        self._publish()

    def _on(self, message: Any) -> None:
        with self._lock:
            self._apply(message)

    def _apply(self, message: Any) -> None:
        self.received[type(message).__name__] += 1
        t = int(message.sim_time)
        self.tick = max(self.tick, t)
        row = self.rows.get(getattr(message, "node_id", None) or "")
        if isinstance(message, GlobalTrustUpdate) and row is not None:
            row.update(
                ts=round(message.ts, 4),
                gt=round(message.gt, 4),
                cti=round(message.cti_i, 4),
                rep=round(message.rep, 4),
                drift=bool(message.drift_flag),
                reporting=True,
            )
            self._entry(row, t).update(ts=row["ts"], gt=row["gt"])
        elif isinstance(message, ResponsePlan) and row is not None:
            row["planned"] = row["derived"] = message.proposed_level
            self._entry(row, t)["planned"] = message.proposed_level
            levels = self._trace(t)["levels"]
            levels[str(message.proposed_level)] = levels.get(str(message.proposed_level), 0) + 1
        elif isinstance(message, HealingEvent) and row is not None:
            if message.phase != row["healing"]:
                text = f"{row['name']}: self-healing {message.phase}"
                self._event("healing", text, row, "info", t)
            row["healing"] = message.phase
            self._trace(t)["healing"].append({"node_id": message.node_id, "phase": message.phase})
        elif isinstance(message, CorrelationResult):
            self._trace(t)["correlation"] = {
                "cti": round(message.cti, 4),
                "implicated": list(message.implicated_node_ids),
                "recall_boost": round(message.recall_boost, 4),
                "corroboration": round(message.campaign_corroboration, 4),
            }
        elif isinstance(message, Classification):
            self._trace(t)["classification"] = {
                "label": message.threat_type,
                "severity": round(message.severity, 3),
                "rules_label": message.rules_threat_type,
                "agree": message.classifiers_agree,
                "used_llm": message.used_llm,
            }
        elif isinstance(message, AuditRecord):
            self._on_audit(message, t)
        elif isinstance(message, OperatorQuestion):
            if message.open:
                self.pending[message.node_id] = message
            else:
                self.pending.pop(message.node_id, None)
        elif isinstance(message, AdjudicationQuestion):
            self.reviews[message.record_id] = message

    def _entry(self, row: dict[str, Any], t: int) -> dict[str, Any]:
        entries = self.history[row["id"]]
        if t not in entries:
            entries[t] = {"t": t} | {k: row[k] for k in ("ts", "gt", "level", "planned")}
            if len(entries) > HISTORY:
                del entries[min(entries)]
        return entries[t]

    def _trace(self, t: int) -> dict[str, Any]:
        if t not in self.ticks:
            self.ticks[t] = {
                "t": t,
                "levels": {},
                "executed": {},
                "refused": {},
                "approvals": [],
                "healing": [],
            }
            if len(self.ticks) > HISTORY:
                del self.ticks[min(self.ticks)]
        return self.ticks[t]

    def _on_audit(self, record: AuditRecord, t: int) -> None:
        payload = record.payload
        if record.event_type == "orchestrator.batch_sealed":
            self._trace(t)["reports"] = payload.get("n_updates", 0)
            return
        if record.event_type == VERIFIER_EVENT:
            self._trace(t)["verifier"] = {
                "verdict": payload.get("verdict", ""),
                "findings": list(payload.get("findings", []))[:12],
            }
            return
        row = self.rows.get(payload.get("node_id") or "")
        self.audit.appendleft(
            {
                "t": record.sim_time,
                "event": record.event_type,
                "actor": record.actor_id,
                "node": payload.get("node_id"),
                "level": payload.get("proposed_level"),
                "capability": payload.get("capability"),
                "reason": payload.get("deny_reason") or payload.get("reason"),
                "withheld": bool(payload.get("isolation_withheld")),
                "hash": "",
            }
        )
        level = enforced_level(record)
        if row is None:
            return
        if level is None:
            if record.event_type == "response.denied":
                reason = payload.get("deny_reason") or "refused"
                self._trace(t)["refused"][row["id"]] = reason
                self._event("gate", f"Action on {row['name']} refused: {reason}", row, "warn", t)
            return
        if level != row["level"]:
            direction = "raised" if level > row["level"] else "lowered"
            tone = "bad" if level >= 3 else "warn" if level >= 1 else "ok"
            text = f"{row['name']} {direction} to L{level} ({LEVEL_NAMES[level]})"
            self._event("response", text, row, tone, t)
        row["level"] = level
        self._entry(row, t)["level"] = level
        if level > 0:
            self._trace(t)["executed"][row["id"]] = level
        row["isolation_withheld"] = bool(payload.get("isolation_withheld"))
        self.worst[row["id"]] = max(self.worst[row["id"]], level)

    def _event(self, source: str, text: str, row: dict[str, Any], tone: str, t: int) -> None:
        self.events.appendleft(
            {"t": t, "source": source, "text": text, "tone": tone, "node": row["id"]}
        )

    def _publish(self) -> None:
        with self._lock:
            devices = [dict(r) for r in self.rows.values()]
            pending, answered = list(self.pending.values()), list(self.answered)
            reviews = list(self.reviews.values())
            done = [t for t in sorted(self.ticks) if _view(self.ticks[t])["sealed"]]
            last = _view(self.ticks[done[-1]]) if done else None
        snapshot = {
            "ready": self.tick >= 0,
            "read_only": True,
            "tick": max(self.tick, 0),
            "paused": False,
            "speed": 1.0,
            "run_id": self.run_id,
            "devices": devices,
            "counts": dict(Counter(d["level"] for d in devices)),
            "events": list(self.events)[:120],
            "incidents": [],
            "approvals": {
                "pending": [
                    {
                        "node_id": q.node_id,
                        "level": q.level,
                        "rationale": q.rationale,
                        "asked_at": q.sim_time,
                    }
                    for q in pending
                ],
                "history": answered,
            },
            "memory": [
                {
                    "id": q.record_id,
                    "threat_type": q.threat_type,
                    "nodes": list(q.node_ids),
                    "window": [q.window_start_sim, q.window_end_sim],
                    "status": q.status,
                    "certified": True,
                    "pattern": q.pattern_text[:160],
                    "adjudicated_by": q.decided_by,
                }
                for q in reviews
            ],
            "attacks": [],
            "last_tick": last,
            "counters": dict(self.received),
            "audit": list(self.audit),
            "health": {
                "binder": "in the control plane",
                "development_key": False,
                "audit_records": sum(1 for a in self.audit if a["event"].startswith("response.")),
                "audit_head": "",
                "audit_intact": None,
                "bus_messages": self.bus.delivered,
                "errors": [],
                "quarantined": [],
            },
        }
        with self._lock:
            self._snapshot = snapshot


def _view(trace: dict[str, Any]) -> dict[str, Any]:
    """
    A tick is shown as sealed once every stage's output has arrived: they travel on separate
    streams, and the screens read them all together.
    """
    stages = ("reports", "correlation", "classification", "verifier")
    return {**trace, "sealed": all(k in trace for k in stages)}


def _blank(node: str) -> dict[str, Any]:
    return {
        "id": node,
        "name": node,
        "kind": "Container",
        "zone": "Compose",
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
