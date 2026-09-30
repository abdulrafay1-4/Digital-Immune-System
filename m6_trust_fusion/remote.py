"""Trust fusion in another process: one instance per container, reached over the broker."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from shared.integrity import DEV_KEY, sign
from shared.schemas import FusionCall, FusionReply, GlobalTrustUpdate

CALLS = frozenset(
    {
        "fuse_batch",
        "observe_silence",
        "observe_responses",
        "set_drift",
        "apply_recalibration",
        "current_trust",
    }
)
VOID = frozenset({"set_drift", "apply_recalibration"})
CHUNK = 3_000
CONTROL = "control"


def replica_user(name: str) -> str:
    return f"fusion-{name}"


def call_topic(name: str) -> str:
    return f"fusion.call-{name}"


def reply_topic(name: str) -> str:
    return f"fusion.reply-{name}"


def encode(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return {"$model": type(value).__name__, "data": value.model_dump(mode="json")}
    if isinstance(value, list | tuple):
        return [encode(v) for v in value]
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    return value


def decode(value: Any) -> Any:
    from shared.redis_bus import wire_models

    if isinstance(value, dict) and "$model" in value:
        return wire_models()[value["$model"]].model_validate(value["data"])
    if isinstance(value, list):
        return [decode(v) for v in value]
    if isinstance(value, dict):
        return {k: decode(v) for k, v in value.items()}
    return value


def _parts(text: str) -> list[str]:
    return [text[i : i + CHUNK] for i in range(0, len(text), CHUNK)] or [""]


class _Assembler:
    """Joins a message sent in parts; answers the whole once every part is in."""

    def __init__(self) -> None:
        self._partial: dict[int, dict[int, str]] = {}

    def add(self, message: Any) -> str | None:
        parts = self._partial.setdefault(message.seq, {})
        parts[message.part] = message.body
        if len(parts) < message.parts:
            return None
        del self._partial[message.seq]
        return "".join(parts[i] for i in range(message.parts))


_ABSENT = object()


@dataclass
class RemoteFusion:
    """The control plane's handle on one fusion instance in another container."""

    broker: Any
    name: str
    params: Any
    run_id: str
    seed: int
    config_hash: str
    signing_key: bytes = DEV_KEY
    poll: Callable[[], Any] | None = None
    max_polls: int = 40
    bus: Any = None
    down: bool = False
    unanswered: int = 0
    _seq: int = 0
    _now: float = 0.0
    _answers: dict[int, tuple[bool, str]] = field(default_factory=dict)
    _assembler: _Assembler = field(default_factory=_Assembler)
    _trust: dict[str, float] | None = None

    def __post_init__(self) -> None:
        self.broker.discover = False
        self.broker.subscribe(reply_topic(self.name), self._reply)
        self.broker.follow(reply_topic(self.name), replica_user(self.name))

    def fuse_batch(self, updates: Any, correlation: Any) -> list[GlobalTrustUpdate]:
        updates = list(updates)
        if updates:
            self._now = updates[0].sim_time
        self._trust = None
        out = self._call("fuse_batch", updates, correlation)
        if not isinstance(out, list):
            return []
        return [self._signed(u) for u in out if isinstance(u, GlobalTrustUpdate)]

    def observe_silence(self, node_id: str, **kw: Any) -> GlobalTrustUpdate | None:
        self._now = float(kw.get("sim_time", self._now))
        self._trust = None
        out = self._call("observe_silence", node_id, **kw)
        return self._signed(out) if isinstance(out, GlobalTrustUpdate) else None

    def observe_responses(self, plans: Any) -> dict[str, float]:
        out = self._call("observe_responses", list(plans))
        return out if isinstance(out, dict) else {}

    def set_drift(self, node_id: str, drift_flag: float) -> None:
        self._call("set_drift", node_id, drift_flag)

    def apply_recalibration(self, node_id: str, next_ts: float) -> None:
        self._trust = None
        self._call("apply_recalibration", node_id, next_ts)

    def current_ts(self, node_id: str) -> float | None:
        if self._trust is None:
            out = self._call("current_trust")
            self._trust = out if isinstance(out, dict) else {}
        value = self._trust.get(node_id)
        return float(value) if isinstance(value, int | float) else None

    def implicates_on_own_trust(self, node_id: str) -> bool:
        trust = self.current_ts(node_id)
        return trust is not None and trust < self.params.implicate_below_ts

    def _call(self, method: str, *args: Any, **kwargs: Any) -> Any:
        if self.down:
            return _ABSENT
        self._seq += 1
        seq = self._seq
        body = json.dumps(encode({"args": list(args), "kwargs": kwargs}))
        chunks = _parts(body)
        for i, chunk in enumerate(chunks):
            self.broker.publish(
                call_topic(self.name),
                FusionCall(
                    sim_time=self._now,
                    run_id=self.run_id,
                    seed=self.seed,
                    config_hash=self.config_hash,
                    seq=seq,
                    method=method,
                    part=i,
                    parts=len(chunks),
                    body=chunk,
                ),
            )
        if method in VOID:
            return None
        for _ in range(self.max_polls):
            if seq in self._answers:
                break
            (self.poll or (lambda: self.broker.pump(timeout=0.05)))()
        answer = self._answers.pop(seq, None)
        if answer is None:
            self.unanswered += 1
            self.down = True
            return _ABSENT
        ok, text = answer
        return decode(json.loads(text)) if ok else _ABSENT

    def _reply(self, message: Any) -> None:
        if isinstance(message, FusionReply) and (whole := self._assembler.add(message)) is not None:
            self._answers[message.seq] = (message.ok, whole)

    def _signed(self, update: GlobalTrustUpdate) -> GlobalTrustUpdate:
        from m6_trust_fusion.fusion import gt_payload

        payload = gt_payload(
            run_id=update.run_id,
            seed=update.seed,
            config_hash=update.config_hash,
            sim_time=update.sim_time,
            node_id=update.node_id,
            gt=update.gt,
            ts=update.ts,
            cti_i=update.cti_i,
            rep=update.rep,
            drift_flag=update.drift_flag,
        )
        return update.model_copy(update={"signature": sign(payload, self.signing_key)})


@dataclass
class FusionReplicaService:
    """One fusion instance's container: answer the control plane's calls, in order."""

    engine: Any
    broker: Any
    name: str
    served: int = 0
    refused: int = 0
    _assembler: _Assembler = field(default_factory=_Assembler)

    def __post_init__(self) -> None:
        self.broker.discover = False
        self.broker.subscribe(call_topic(self.name), self._call)
        self.broker.follow(call_topic(self.name), CONTROL)

    def step(self, timeout: float = 0.05) -> None:
        self.broker.pump(timeout=timeout)

    def _call(self, message: Any) -> None:
        if not isinstance(message, FusionCall):
            return
        body = self._assembler.add(message)
        if body is None:
            return
        ok, result = False, None
        if message.method in CALLS:
            try:
                call = decode(json.loads(body))
                result = getattr(self.engine, message.method)(*call["args"], **call["kwargs"])
                ok = True
            except Exception:  # noqa: BLE001
                pass
        self.served += ok
        self.refused += not ok
        if message.method in VOID:
            return
        chunks = _parts(json.dumps(encode(result)))
        for i, chunk in enumerate(chunks):
            self.broker.publish(
                reply_topic(self.name),
                FusionReply(
                    sim_time=message.sim_time,
                    run_id=message.run_id,
                    seed=message.seed,
                    config_hash=message.config_hash,
                    seq=message.seq,
                    ok=ok,
                    part=i,
                    parts=len(chunks),
                    body=chunk,
                ),
            )
