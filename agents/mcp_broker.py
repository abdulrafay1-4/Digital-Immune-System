"""
Immune memory served over the Model Context Protocol: the context broker's policy enforced server-
side, with signed calls, freshness, budgets and bearer tokens.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import secrets
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from typing import Any

from agents.context_broker import (
    CORRELATION_CLIENT,
    CURATOR_CLIENT,
    READ_CAPABILITY,
    WRITE_CAPABILITY,
    BrokerDecision,
    InProcBroker,
)
from agents.rules_classifier import ThreatType
from m10_persona_drift.nhi import SigningIdentity, VerifyingIdentity, issue_signing_identity
from shared.schemas import MemoryRecord, Provenance

try:  # pragma: no cover
    from mcp.server.mcpserver import MCPServer

    MCP_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover
    MCPServer = None  # type: ignore[assignment]
    MCP_AVAILABLE = False

SERVER_NAME = "dis-immune-memory"
CORE_CLIENT = "control-core"
TICK_CAPABILITY = "memory_tick"
ADJUDICATE_CAPABILITY = "memory_adjudicate"
TOKEN_SCOPE = "memory"
ISSUER = "https://provision.dis.internal"

READ_BUDGET = 4

MANIFEST_DIGEST = "6d1e26eda0ce71cc01750c79b6f7df41559837e0f4c5d95a214687611d8655fe"

PROPOSE_ONLY: dict[str, Any] = {"provenance": "HIGH", "candidate": None, "attestations": None}

_THREAT_LABELS = frozenset(t.value for t in ThreatType)


@dataclass(frozen=True)
class OperatorVerdicts:
    """What lets the memory service record what a person decided an incident meant."""

    console: VerifyingIdentity
    key: bytes


class ToolManifestChanged(RuntimeError):
    """The server's tools are not the ones this client was built against."""


@dataclass(frozen=True)
class _Hit:
    """What a client gets back for one recalled record."""

    record_id: str
    similarity: float
    threat_type: str


@dataclass(frozen=True)
class _Recognition:
    """The client-side view of a recall answer, shaped like `m5.Recognition`."""

    recognised: bool
    cti_boost: float
    hits: tuple[_Hit, ...] = ()

    @property
    def best(self) -> _Hit | None:
        return self.hits[0] if self.hits else None


def call_payload(
    tool: str, caller_id: str, sim_time: float, nonce: str, fields: Mapping[str, Any]
) -> bytes:
    """The bytes a call's signature covers: the tool, who, when, and every argument."""
    return json.dumps(
        {
            "tool": tool,
            "caller_id": caller_id,
            "sim_time": float(sim_time),
            "nonce": nonce,
            **fields,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


def _as_payload(recognition: Any) -> dict[str, Any]:
    """Serialise a recall answer."""
    if recognition is None:
        return {"recognised": False, "cti_boost": 0.0, "hits": []}
    return {
        "recognised": bool(getattr(recognition, "recognised", False)),
        "cti_boost": float(getattr(recognition, "cti_boost", 0.0)),
        "hits": [
            {
                "record_id": h.record_id,
                "similarity": float(h.similarity),
                "threat_type": (
                    h.threat_type if h.threat_type in _THREAT_LABELS else "unrecognised"
                ),
            }
            for h in getattr(recognition, "hits", ())
        ],
    }


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def issue_token(client_id: str, key: bytes, *, audience: str, expires_at: int) -> str:
    """An access token for one client, bound to one server's address."""
    body = _b64(
        json.dumps(
            {"sub": client_id, "aud": audience, "exp": int(expires_at), "scope": TOKEN_SCOPE},
            sort_keys=True,
        ).encode()
    )
    mac = hmac.new(key, body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{mac}"


@dataclass
class ProvisionedTokens:
    """Verifies bearer tokens for the MCP SDK's resource-server middleware."""

    key: bytes
    now: Callable[[], float]
    refused: Counter[str] = field(default_factory=Counter)

    async def verify_token(self, token: str) -> Any:
        from mcp.server.auth.provider import AccessToken

        body, _, mac = token.partition(".")
        expected = hmac.new(self.key, body.encode(), hashlib.sha256).hexdigest()
        if not mac or not hmac.compare_digest(expected, mac):
            self.refused["bad_token"] += 1
            return None
        claims = json.loads(_unb64(body))
        if claims["exp"] < self.now():
            self.refused["expired_token"] += 1
            return None
        return AccessToken(
            token=token,
            client_id=claims["sub"],
            scopes=[claims["scope"]],
            expires_at=None,
            resource=claims["aud"],
        )


@dataclass
class _CallGate:
    """Steps before the broker's own six: signature, freshness, budget."""

    broker: InProcBroker
    verifiers: Mapping[str, VerifyingIdentity]
    read_budget: int = READ_BUDGET
    _tick: float | None = None
    _seen: set[tuple[str, str]] = field(default_factory=set)
    _count: Counter[tuple[str, str]] = field(default_factory=Counter)
    _tick_nonces: set[str] = field(default_factory=set)

    def check(
        self,
        tool: str,
        capability: str,
        caller_id: str,
        sim_time: float,
        nonce: str,
        signature: str,
        fields: Mapping[str, Any],
    ) -> BrokerDecision | None:
        """`None` when the call may proceed; otherwise the audited refusal."""
        now = self.broker.now
        if self._tick != now:
            self._tick, self._seen, self._count = now, set(), Counter()
        refused = self._signed(tool, capability, caller_id, sim_time, nonce, signature, fields)
        if refused is not None:
            return refused
        if float(sim_time) != now:
            return self.broker.refuse(caller_id, capability, "stale_call", now)
        if (caller_id, nonce) in self._seen:
            return self.broker.refuse(caller_id, capability, "replayed_call", now)
        budget = self.read_budget if capability == READ_CAPABILITY else self.broker.fleet_size
        if self._count[caller_id, capability] >= budget:
            return self.broker.refuse(caller_id, capability, "over_call_budget", now)
        self._seen.add((caller_id, nonce))
        self._count[caller_id, capability] += 1
        return None

    def check_tick(
        self,
        caller_id: str,
        sim_time: float,
        nonce: str,
        signature: str,
        fields: Mapping[str, Any],
        *,
        tool: str = "memory_tick",
        capability: str = TICK_CAPABILITY,
        stale: str = "stale_tick",
    ) -> BrokerDecision | None:
        """
        Only the core advances the tick (or relays a verdict); never backwards, never twice by one
        call.
        """
        now = self.broker.now
        if caller_id != CORE_CLIENT:
            return self.broker.refuse(caller_id, capability, "not_the_core", now)
        refused = self._signed(tool, capability, caller_id, sim_time, nonce, signature, fields)
        if refused is not None:
            return refused
        if float(sim_time) < now or nonce in self._tick_nonces:
            return self.broker.refuse(caller_id, capability, stale, now)
        self._tick_nonces.add(nonce)
        return None

    def _signed(
        self,
        tool: str,
        capability: str,
        caller_id: str,
        sim_time: float,
        nonce: str,
        signature: str,
        fields: Mapping[str, Any],
    ) -> BrokerDecision | None:
        now = self.broker.now
        verifier = self.verifiers.get(caller_id)
        if verifier is None:
            return self.broker.refuse(caller_id, capability, "unknown_caller", now)
        if not verifier.verify(call_payload(tool, caller_id, sim_time, nonce, fields), signature):
            return self.broker.refuse(caller_id, capability, "bad_signature", now)
        return None


def _candidate(data: Mapping[str, Any]) -> Any:
    from m11_memory_hardening.quorum import MemoryCandidate

    return MemoryCandidate(**{**data, "node_ids": tuple(data["node_ids"])})


def _attestation(data: Mapping[str, Any]) -> Any:
    from m11_memory_hardening.quorum import Attestation

    return Attestation(**data)


def build_server(
    broker: InProcBroker,
    verifiers: Mapping[str, VerifyingIdentity],
    *,
    read_budget: int = READ_BUDGET,
    tokens: ProvisionedTokens | None = None,
    resource_url: str | None = None,
    verdicts: OperatorVerdicts | None = None,
) -> Any:
    """
    An MCP server exposing recall, propose, tick and adjudicate, all behind the broker's policy.
    """
    if not MCP_AVAILABLE:  # pragma: no cover
        raise RuntimeError(
            'the MCP extra is not installed. Install it with: pip install "mcp>=2", '
            "or use InProcBroker, which every evaluation run uses."
        )

    gate = _CallGate(broker=broker, verifiers=dict(verifiers), read_budget=read_budget)
    auth: dict[str, Any] = {}
    if tokens is not None:
        from mcp.server.auth.settings import AuthSettings

        auth = {
            "token_verifier": tokens,
            "auth": AuthSettings(
                issuer_url=ISSUER,
                resource_server_url=resource_url,
                required_scopes=[TOKEN_SCOPE],
                validate_token_resource=True,
            ),
        }
    server = MCPServer(
        name=SERVER_NAME, instructions="Mediated access to DIS immune memory.", **auth
    )

    @server.tool(
        name="memory_recall",
        description="Ask immune memory whether this campaign shape has been seen before.",
    )
    async def memory_recall(
        caller_id: str,
        pattern_text: str,
        sim_time: float,
        nonce: str,
        signature: str,
        provenance: str = "HIGH",
    ) -> str:
        fields = {"pattern_text": pattern_text, "provenance": provenance}
        refused = gate.check(
            "memory_recall", READ_CAPABILITY, caller_id, sim_time, nonce, signature, fields
        )
        decision = refused or broker.request_recall(
            caller_id=caller_id,
            pattern_text=pattern_text,
            sim_time=sim_time,
            provenance=_provenance(provenance),
        )
        if not decision.allowed:
            return json.dumps({"allowed": False, "reason": decision.reason})
        return json.dumps({"allowed": True, "recognition": _as_payload(decision.result)})

    @server.tool(
        name="memory_propose",
        description=(
            "Propose an incident for immune memory, with the attesters' signatures."
            " The quorum gate still decides."
        ),
    )
    async def memory_propose(
        caller_id: str,
        sim_time: float,
        nonce: str,
        signature: str,
        provenance: str = "HIGH",
        candidate: dict[str, Any] | None = None,
        attestations: list[dict[str, Any]] | None = None,
    ) -> str:
        fields = {"provenance": provenance, "candidate": candidate, "attestations": attestations}
        refused = gate.check(
            "memory_propose", WRITE_CAPABILITY, caller_id, sim_time, nonce, signature, fields
        )
        if refused is not None:
            return json.dumps({"allowed": False, "reason": refused.reason})
        if candidate is None:
            decision = broker.authorise_write(
                caller_id=caller_id, sim_time=sim_time, provenance=_provenance(provenance)
            )
            return json.dumps({"allowed": decision.allowed, "reason": decision.reason})
        decision = broker.request_write(
            caller_id=caller_id,
            candidate=_candidate(candidate),
            attestations=[_attestation(a) for a in attestations or ()],
            sim_time=sim_time,
            provenance=_provenance(provenance),
        )
        result = decision.result
        record = getattr(result, "record", None)
        return json.dumps(
            {
                "allowed": decision.allowed,
                "reason": decision.reason,
                "admitted": bool(getattr(result, "admitted", False)),
                "write_reason": getattr(result, "reason", None),
                "threat_type": getattr(record, "threat_type", None),
            }
        )

    @server.tool(
        name="memory_tick",
        description="Advance immune memory to the core's tick and set its provenance ceiling.",
    )
    async def memory_tick(
        caller_id: str,
        sim_time: float,
        nonce: str,
        signature: str,
        ceiling: str,
        fleet_size: int,
    ) -> str:
        fields = {"ceiling": ceiling, "fleet_size": fleet_size}
        refused = gate.check_tick(caller_id, sim_time, nonce, signature, fields)
        if refused is not None:
            return json.dumps({"allowed": False, "reason": refused.reason})
        broker.at(float(sim_time), _provenance(ceiling), int(fleet_size))
        return json.dumps({"allowed": True, "reason": None})

    @server.tool(
        name="memory_adjudicate",
        description=(
            "Record an operator's verdict on a remembered incident. The console must have"
            " signed the verdict; the core only relays it."
        ),
    )
    async def memory_adjudicate(
        caller_id: str,
        sim_time: float,
        nonce: str,
        signature: str,
        record_id: str,
        status: str,
        decided_by: str,
        asked_at: float,
        verdict: str,
    ) -> str:
        fields = {
            "record_id": record_id,
            "status": status,
            "decided_by": decided_by,
            "asked_at": asked_at,
            "verdict": verdict,
        }
        refused = gate.check_tick(
            caller_id,
            sim_time,
            nonce,
            signature,
            fields,
            tool="memory_adjudicate",
            capability=ADJUDICATE_CAPABILITY,
            stale="stale_call",
        )
        reason = (
            refused.reason
            if refused is not None
            else _verdict_refused(
                broker, verdicts, record_id, status, decided_by, asked_at, verdict
            )
        )
        if reason is not None:
            if refused is None:
                broker.refuse(caller_id, ADJUDICATE_CAPABILITY, reason, broker.now)
            return json.dumps({"allowed": False, "reason": reason})
        assert verdicts is not None
        broker.store.adjudicate(
            record_id, status, actor=decided_by, sim_time=float(sim_time), key=verdicts.key
        )
        broker.served(caller_id, ADJUDICATE_CAPABILITY, broker.now)
        return json.dumps({"allowed": True, "reason": None})

    return server


def _verdict_refused(
    broker: InProcBroker,
    verdicts: OperatorVerdicts | None,
    record_id: str,
    status: str,
    decided_by: str,
    asked_at: float,
    verdict: str,
) -> str | None:
    """Why a relayed verdict is not recorded, or `None` to record it."""
    from shared.attestation import verdict_payload

    if verdicts is None:
        return "no_operator"
    if status not in ("confirmed", "benign"):
        return "bad_status"
    payload = verdict_payload(broker.run_id, record_id, float(asked_at), status, decided_by)
    if not verdicts.console.verify(payload, verdict):
        return "bad_verdict"
    record = broker.store.get(record_id) if broker.store is not None else None
    if record is None:
        return "unknown_record"
    if record.status != "pending":
        return "already_adjudicated"
    return None


def _digest(tools: Any) -> str:
    served = [
        {"name": t.name, "description": t.description, "input_schema": t.input_schema}
        for t in sorted(tools, key=lambda t: t.name)
    ]
    return hashlib.sha256(json.dumps(served, sort_keys=True).encode()).hexdigest()


def manifest_digest(server: Any) -> str:
    """SHA-256 over what a model would read of the tools: names, descriptions, schemas."""
    return _digest(asyncio.run(server.list_tools()))


def serve(
    server: Any,
    *,
    host: str,
    port: int,
    certfile: str | None = None,
    keyfile: str | None = None,
    ca_certs: str | None = None,
    allowed_hosts: list[str] | None = None,
) -> None:  # pragma: no cover
    """Serve over streamable HTTP; with certificates, over mutually authenticated TLS."""
    import ssl

    import uvicorn
    from mcp.server.transport_security import TransportSecuritySettings

    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=list(allowed_hosts or [f"{host}:{port}"]),
    )

    tls: dict[str, Any] = {}
    if certfile is not None:
        tls = {
            "ssl_certfile": certfile,
            "ssl_keyfile": keyfile,
            "ssl_ca_certs": ca_certs,
            "ssl_cert_reqs": ssl.CERT_REQUIRED,
        }
    app = server.streamable_http_app(host=host, transport_security=security)
    uvicorn.Server(uvicorn.Config(app, host=host, port=port, log_level="warning", **tls)).run()


def _provenance(value: str) -> Provenance:
    try:
        return Provenance(value)
    except ValueError:
        return Provenance.UNTRUSTED


def _default_identities() -> dict[str, SigningIdentity]:
    return {c: issue_signing_identity(c) for c in (CORRELATION_CLIENT, CURATOR_CLIENT)}


@dataclass
class McpBroker:
    """Client side: signs its calls, speaks MCP to the server, presents `recall`."""

    inner: InProcBroker | None = None
    caller_id: str = CORRELATION_CLIENT
    provenance: Provenance = Provenance.HIGH
    identities: dict[str, SigningIdentity] = field(default_factory=_default_identities)
    server: Any = field(default=None, repr=False)
    url: str | None = None
    token: str | None = None
    tls: tuple[str, str, str] | None = None
    verdicts: OperatorVerdicts | None = None
    calls: int = 0
    _now: float = 0.0

    def __post_init__(self) -> None:
        if self.url is None and self.server is None:
            if self.inner is None:
                raise ValueError("an in-process McpBroker needs the broker it fronts")
            self.server = build_server(
                self.inner,
                {c: i.public() for c, i in self.identities.items()},
                verdicts=self.verdicts,
            )
        digest = (
            _digest(asyncio.run(self._remote_tools())) if self.url else manifest_digest(self.server)
        )
        if digest != MANIFEST_DIGEST:
            raise ToolManifestChanged(f"{SERVER_NAME}: the served tools changed")

    @property
    def now(self) -> float:
        return self.inner.now if self.url is None and self.inner is not None else self._now

    def recognise(self, pattern_text: str) -> Any:
        payload = self._call(
            "memory_recall",
            self.caller_id,
            {"pattern_text": pattern_text, "provenance": self.provenance.value},
        )
        if not payload.get("allowed"):
            return None
        data = payload["recognition"]
        return _Recognition(
            recognised=data["recognised"],
            cti_boost=data["cti_boost"],
            hits=tuple(_Hit(**h) for h in data["hits"]),
        )

    def authorise_write(
        self,
        *,
        caller_id: str = CURATOR_CLIENT,
        sim_time: float,
        provenance: Provenance | None = None,
    ) -> BrokerDecision:
        """Authorise a write proposal over MCP."""
        payload = self._call(
            "memory_propose",
            caller_id,
            {
                "provenance": (provenance or self.provenance).value,
                "candidate": None,
                "attestations": None,
            },
            sim_time=sim_time,
        )
        return BrokerDecision(
            allowed=bool(payload.get("allowed")),
            capability=WRITE_CAPABILITY,
            caller_id=caller_id,
            reason=payload.get("reason"),
        )

    def submit(self, candidate: Any, attestations: Any, *, now_sim: float) -> Any:
        """`WritePath.submit` over the wire: the server's own quorum gate decides."""
        from m5_immune_memory.write_path import WriteResult

        payload = self._call(
            "memory_propose",
            CURATOR_CLIENT,
            {
                "provenance": self.provenance.value,
                "candidate": _jsonable(asdict(candidate)),
                "attestations": [_jsonable(asdict(a)) for a in attestations],
            },
            sim_time=now_sim,
        )
        reason = payload.get("write_reason") or payload.get("reason")
        admitted = bool(payload.get("admitted"))
        record = (
            MemoryRecord(
                sim_time=now_sim,
                run_id=candidate.run_id,
                seed=candidate.seed,
                config_hash=candidate.config_hash,
                record_id=candidate.record_id,
                pattern_text=candidate.pattern_text,
                threat_type=payload.get("threat_type") or candidate.threat_type,
                node_ids=list(candidate.node_ids),
                window_start_sim=candidate.window_start_sim,
                window_end_sim=candidate.window_end_sim,
                proposer_id=candidate.proposer_id,
            )
            if admitted
            else None
        )
        return WriteResult(admitted=admitted, decision=None, record=record, reason=reason)

    def adjudicate(self, verdict: Any, *, sim_time: float) -> dict[str, Any]:
        """Relay an operator's signed verdict."""
        return self._call(
            "memory_adjudicate",
            CORE_CLIENT,
            {
                "record_id": verdict.record_id,
                "status": verdict.status,
                "decided_by": verdict.decided_by,
                "asked_at": verdict.sim_time,
                "verdict": verdict.signature,
            },
            sim_time=sim_time,
        )

    def at(
        self, sim_time: float, ceiling: Provenance | None = None, fleet_size: int | None = None
    ) -> McpBroker:
        """Advance to the core's tick."""
        if self.url is None:
            if self.inner is not None:
                self.inner.at(sim_time, ceiling, fleet_size)
            return self
        self._now = float(sim_time)
        if CORE_CLIENT in self.identities:
            fields = {
                "ceiling": (ceiling or Provenance.HIGH).value,
                "fleet_size": int(fleet_size or 1),
            }
            self._call("memory_tick", CORE_CLIENT, fields, sim_time=sim_time)
        return self

    def signed(
        self, tool: str, caller_id: str, fields: Mapping[str, Any], sim_time: float
    ) -> dict[str, Any]:
        """The arguments of one call, signed as `caller_id`."""
        nonce = secrets.token_hex(8)
        identity = self.identities.get(caller_id) or issue_signing_identity(caller_id)
        signature = identity.sign(call_payload(tool, caller_id, sim_time, nonce, fields))
        return {
            "caller_id": caller_id,
            "sim_time": float(sim_time),
            "nonce": nonce,
            "signature": signature,
            **fields,
        }

    def _call(
        self,
        tool: str,
        caller_id: str,
        fields: Mapping[str, Any],
        *,
        sim_time: float | None = None,
    ) -> dict[str, Any]:
        self.calls += 1
        when = self.now if sim_time is None else sim_time
        arguments = self.signed(tool, caller_id, fields, when)
        if self.url is not None:
            return json.loads(asyncio.run(self._remote_call(tool, arguments)))
        result = asyncio.run(self.server.call_tool(tool, arguments))
        return json.loads(_text_of(result))

    def _http(self) -> Any:
        import ssl

        import httpx2

        verify: Any = True
        if self.tls is not None:
            ca, cert, key = self.tls
            context = ssl.create_default_context(cafile=ca)
            context.load_cert_chain(cert, key)
            verify = context
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        return httpx2.AsyncClient(headers=headers, verify=verify, timeout=10.0)

    async def _session(self) -> Any:
        from mcp import Client
        from mcp.client.streamable_http import streamable_http_client

        assert self.url is not None
        return Client(streamable_http_client(self.url, http_client=self._http()))

    async def _remote_tools(self) -> Any:
        async with await self._session() as session:
            return (await session.list_tools()).tools

    async def _remote_call(self, tool: str, arguments: dict[str, Any]) -> str:
        async with await self._session() as session:
            result = await session.call_tool(tool, arguments)
            return _text_of(result)


def _jsonable(value: Any) -> Any:
    """Tuples become lists: what JSON carries, and what the signature is made over."""
    return json.loads(json.dumps(value))


@dataclass
class RemoteWritePath:
    """The curator's side of a write when memory lives in another process."""

    client: McpBroker
    curator: Any = None
    authorises: bool = True
    outcomes: Counter[str] = field(default_factory=Counter)

    def __post_init__(self) -> None:
        if self.curator is None:
            from m5_immune_memory.write_path import MemoryCurator

            self.curator = MemoryCurator()

    def propose_and_submit(self, incident: Any, attesters: Mapping[str, Any], *, now_sim: float):
        from m5_immune_memory.write_path import WriteResult

        candidate = self.curator.propose(incident)
        if candidate is None:
            return WriteResult(admitted=False, decision=None, reason="immaterial")
        if hasattr(attesters, "collect"):
            signed = attesters.collect(candidate, sim_time=now_sim)
        else:
            signed = [
                a
                for _, attester in sorted(attesters.items())
                if (a := attester.review(candidate, sim_time=now_sim)) is not None
            ]
        if not signed:
            return WriteResult(admitted=False, decision=None, reason="attesters_disagree")
        result = self.client.submit(candidate, signed, now_sim=now_sim)
        self.outcomes["admitted" if result.admitted else str(result.reason).split(":")[0]] += 1
        return result


def _text_of(result: Any) -> str:
    """The text a tool returned, across the shapes the SDK may hand back."""
    if isinstance(result, str):
        return result
    if isinstance(result, tuple | list) and result:
        first = result[0]
        if isinstance(first, str):
            return first
        if isinstance(first, tuple | list) and first:
            return getattr(first[0], "text", str(first[0]))
        return getattr(first, "text", str(first))
    content = getattr(result, "content", None)
    if content:
        return getattr(content[0], "text", str(content[0]))
    return str(result)
