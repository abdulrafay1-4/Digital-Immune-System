"""Mediated access to immune memory: the state plane behind a policy boundary."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from m9_capability_binder.binder import redeem, resolve_capability
from shared.audit import AuditLog
from shared.provenance import rank
from shared.schemas import AuditRecord, Provenance

READ_CAPABILITY = "memory_read"
WRITE_CAPABILITY = "memory_write"

CORRELATION_CLIENT = "correlation-agent"
CURATOR_CLIENT = "memory-curator"
DEFAULT_CLIENTS: Mapping[str, tuple[str, ...]] = {
    CORRELATION_CLIENT: (READ_CAPABILITY,),
    CURATOR_CLIENT: (READ_CAPABILITY, WRITE_CAPABILITY),
}


@dataclass(frozen=True)
class BrokerDecision:
    """What happened, in a form the audit trail and the metrics both read."""

    allowed: bool
    capability: str
    caller_id: str
    reason: str | None = None
    result: Any = None
    token_id: str | None = None


@runtime_checkable
class ContextBroker(Protocol):
    """What the reasoning plane is given instead of the memory objects."""

    def request_recall(
        self, *, caller_id: str, pattern_text: str, sim_time: float, provenance: Provenance
    ) -> BrokerDecision: ...

    def request_write(
        self,
        *,
        caller_id: str,
        candidate: Any,
        attestations: Iterable[Any],
        sim_time: float,
        provenance: Provenance,
    ) -> BrokerDecision: ...


@dataclass
class InProcBroker:
    """The broker every evaluation run uses."""

    query: Any
    write_path: Any | None = None
    clients: Mapping[str, tuple[str, ...]] = field(default_factory=lambda: dict(DEFAULT_CLIENTS))
    ceiling: Provenance = Provenance.HIGH
    tick_ceiling: Provenance = Provenance.HIGH
    fleet_size: int = 1
    audit: AuditLog = field(default_factory=AuditLog)
    actor_id: str = "context-broker"
    run_id: str = "broker"
    seed: int = 0
    config_hash: str = "broker"
    default_caller: str = CORRELATION_CLIENT
    default_provenance: Provenance = Provenance.HIGH

    requests: int = 0
    allowed: int = 0
    denied: dict[str, int] = field(default_factory=dict)

    def request_recall(
        self,
        *,
        caller_id: str,
        pattern_text: str,
        sim_time: float,
        provenance: Provenance = Provenance.HIGH,
    ) -> BrokerDecision:
        decision = self._authorise(
            caller_id=caller_id,
            capability=READ_CAPABILITY,
            sim_time=sim_time,
            provenance=provenance,
        )
        if not decision.allowed:
            return decision
        recognition = self.query.recognise(pattern_text)
        return self._allow(decision, self._filtered(recognition), sim_time)

    def request_write(
        self,
        *,
        caller_id: str,
        candidate: Any,
        attestations: Iterable[Any],
        sim_time: float,
        provenance: Provenance = Provenance.HIGH,
    ) -> BrokerDecision:
        decision = self._authorise(
            caller_id=caller_id,
            capability=WRITE_CAPABILITY,
            sim_time=sim_time,
            provenance=provenance,
        )
        if not decision.allowed:
            return decision
        if self.write_path is None:
            return self._deny(caller_id, WRITE_CAPABILITY, "no_write_path", sim_time)
        result = self.write_path.submit(candidate, list(attestations), now_sim=sim_time)
        return self._allow(decision, result, sim_time)

    def authorise_write(
        self,
        *,
        caller_id: str,
        sim_time: float,
        provenance: Provenance = Provenance.HIGH,
    ) -> BrokerDecision:
        """Steps 1-3 and the audit, without executing a write."""
        decision = self._authorise(
            caller_id=caller_id,
            capability=WRITE_CAPABILITY,
            sim_time=sim_time,
            provenance=provenance,
        )
        if decision.allowed:
            self.allowed += 1
            self._audit(caller_id, WRITE_CAPABILITY, sim_time, None, decision.token_id)
        return decision

    def recognise(self, pattern_text: str) -> Any:
        """`Recall`-shaped, so `ClosedLoopPipeline(recall=broker)` works unchanged."""
        decision = self.request_recall(
            caller_id=self.default_caller,
            pattern_text=pattern_text,
            sim_time=self._now,
            provenance=self.default_provenance,
        )
        return decision.result if decision.allowed else None

    def submit(self, candidate: Any, attestations: Iterable[Any], *, now_sim: float) -> Any:
        """`WritePath`-shaped, so a curator can be handed the broker instead."""
        decision = self.request_write(
            caller_id=CURATOR_CLIENT,
            candidate=candidate,
            attestations=attestations,
            sim_time=now_sim,
            provenance=self.default_provenance,
        )
        if decision.allowed:
            return decision.result
        from m5_immune_memory.write_path import WriteResult

        return WriteResult(admitted=False, decision=None, reason=f"broker: {decision.reason}")

    _now: float = 0.0

    def at(
        self, sim_time: float, ceiling: Provenance | None = None, fleet_size: int | None = None
    ) -> InProcBroker:
        self._now = sim_time
        if ceiling is not None:
            self.tick_ceiling = ceiling
        if fleet_size is not None:
            self.fleet_size = max(1, fleet_size)
        return self

    @property
    def now(self) -> float:
        return self._now

    def refuse(
        self, caller_id: str, capability: str, reason: str, sim_time: float
    ) -> BrokerDecision:
        """An audited refusal decided in front of the broker (the MCP call gate)."""
        self.requests += 1
        return self._deny(caller_id, capability, reason, sim_time)

    def served(self, caller_id: str, capability: str, sim_time: float) -> None:
        """An audited call served in front of the broker (the MCP call gate)."""
        self.requests += 1
        self.allowed += 1
        self._audit(caller_id, capability, sim_time, None, None)

    @property
    def store(self) -> Any:
        """The curator seam: `pipeline._remember` reaches `curator.store`."""
        return getattr(self.write_path, "store", None)

    def _authorise(
        self, *, caller_id: str, capability: str, sim_time: float, provenance: Provenance
    ) -> BrokerDecision:
        self.requests += 1
        permitted = self.clients.get(caller_id)
        if permitted is None:
            return self._deny(caller_id, capability, "unknown_caller", sim_time)
        if capability not in permitted:
            return self._deny(caller_id, capability, "capability_not_granted", sim_time)

        effective = min(provenance, self.ceiling, self.tick_ceiling, key=rank)
        token = resolve_capability(capability, caller_id, effective.value, sim_time)
        if not token.get("ok"):
            return self._deny(
                caller_id, capability, str(token.get("deny_reason", "denied")), sim_time
            )
        spent, reason = redeem(token, now_sim=sim_time)
        if not spent:
            return self._deny(caller_id, capability, reason or "not_redeemed", sim_time)
        return BrokerDecision(
            allowed=True, capability=capability, caller_id=caller_id, token_id=token["token_id"]
        )

    def _filtered(self, recognition: Any) -> Any:
        """Reads carry identifiers and numbers."""
        return recognition

    def _allow(self, decision: BrokerDecision, result: Any, sim_time: float) -> BrokerDecision:
        self.allowed += 1
        self._audit(decision.caller_id, decision.capability, sim_time, None, decision.token_id)
        return BrokerDecision(
            allowed=True,
            capability=decision.capability,
            caller_id=decision.caller_id,
            result=result,
            token_id=decision.token_id,
        )

    def _deny(
        self, caller_id: str, capability: str, reason: str, sim_time: float
    ) -> BrokerDecision:
        self.denied[reason] = self.denied.get(reason, 0) + 1
        self._audit(caller_id, capability, sim_time, reason, None)
        return BrokerDecision(
            allowed=False, capability=capability, caller_id=caller_id, reason=reason
        )

    def _audit(
        self,
        caller_id: str,
        capability: str,
        sim_time: float,
        reason: str | None,
        token_id: str | None,
    ) -> None:
        self.audit.append(
            AuditRecord(
                sim_time=max(0.0, float(sim_time)),
                run_id=self.run_id,
                seed=self.seed,
                config_hash=self.config_hash,
                event_type="broker.denied" if reason else "broker.served",
                actor_id=self.actor_id,
                payload={
                    "caller_id": caller_id,
                    "capability": capability,
                    "deny_reason": reason,
                    "token_id": token_id,
                },
            )
        )

    @property
    def denied_total(self) -> int:
        return sum(self.denied.values())
