"""Securing the bus: transport encryption **and** message authentication."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from shared.bus import Bus, Handler
from shared.integrity import canonical
from shared.provenance import tag_external_tool
from shared.schemas import Provenance

SENDER_FIELD = "__sender__"
SIGNATURE_FIELD = "__signature__"


@dataclass(frozen=True)
class TLSConfig:
    """Certificate material for a TLS or mTLS transport."""

    enabled: bool = False
    ca_cert: Path | None = None
    client_cert: Path | None = None
    client_key: Path | None = None
    check_hostname: bool = True

    @property
    def mutual(self) -> bool:
        return self.client_cert is not None and self.client_key is not None

    def validate(self) -> None:
        """Fail loudly at construction rather than quietly at first connection."""
        if not self.enabled:
            return
        if self.ca_cert is None:
            raise ValueError(
                "TLS enabled without a CA certificate: verifying an internal "
                "broker against the public trust store is not a check"
            )
        missing = [
            str(p)
            for p in (self.ca_cert, self.client_cert, self.client_key)
            if p is not None and not p.exists()
        ]
        if missing:
            raise ValueError(f"TLS material not found: {', '.join(missing)}")
        if (self.client_cert is None) != (self.client_key is None):
            raise ValueError("client_cert and client_key must be supplied together")

    def describe(self) -> str:
        if not self.enabled:
            return "plaintext"
        return "mTLS" if self.mutual else "TLS (server-authenticated only)"


class Signer(Protocol):
    """Minimal interface a publisher identity must satisfy (M10 `AgentIdentity`)."""

    agent_id: str

    def sign(self, payload: bytes) -> str: ...  # pragma: no cover

    def verify(self, payload: bytes, signature: str) -> bool: ...  # pragma: no cover


def message_payload(topic: str, model: BaseModel, sender: str) -> bytes:
    """Bytes a signature covers: the topic, the sender, and the whole message."""
    return payload_bytes(topic, sender, model.model_dump_json())


def payload_bytes(topic: str, sender: str, body: str) -> bytes:
    """The same bytes, from a body already serialised."""
    return canonical(topic, sender, body)


@dataclass
class SignedBus:
    """Wraps any `Bus`, signing on publish and verifying on delivery."""

    inner: Bus
    identity: Signer
    registry: Mapping[str, Signer] = field(default_factory=dict)
    tls: TLSConfig = field(default_factory=TLSConfig)
    strict: bool = True
    topics: frozenset[str] | None = None

    rejected: list[tuple[str, str]] = field(default_factory=list)
    delivered: int = 0

    @property
    def published(self) -> int:
        """Messages the underlying bus carried."""
        return getattr(self.inner, "published", 0)

    @property
    def rejected_count(self) -> int:
        """Refused **deliveries**, not messages."""
        return len(self.rejected)

    def covers(self, topic: str) -> bool:
        return self.topics is None or topic in self.topics

    def publish(self, topic: str, model: BaseModel) -> None:
        if not self.covers(topic):
            self.inner.publish(topic, model)
            return
        signature = self.identity.sign(message_payload(topic, model, self.identity.agent_id))
        envelope = _Envelope(
            topic=topic,
            model=model,
            sender=self.identity.agent_id,
            signature=signature,
        )
        self.inner.publish(topic, envelope)  # type: ignore[arg-type]

    def subscribe(self, topic: str, handler: Handler) -> None:
        if not self.covers(topic):
            self.inner.subscribe(topic, handler)
            return
        self.inner.subscribe(topic, self._guard(topic, handler))

    def _guard(self, topic: str, handler: Handler) -> Callable[[BaseModel], None]:
        def verified(message: BaseModel) -> None:
            if not isinstance(message, _Envelope):
                self.rejected.append(("<unsigned>", "not_signed"))
                if not self.strict:
                    handler(message)
                return

            signer = self.registry.get(message.sender)
            if signer is None:
                self.rejected.append((message.sender, "unknown_sender"))
                return
            payload = message_payload(message.topic, message.model, message.sender)
            if not signer.verify(payload, message.signature):
                self.rejected.append((message.sender, "bad_signature"))
                return
            claimed = getattr(message.model, "agent_id", None)
            if claimed is not None and claimed != message.sender:
                self.rejected.append((message.sender, "agent_mismatch"))
                return

            self.delivered += 1
            handler(message.model)

        return verified

    def provenance_for(self, sender: str) -> Provenance:
        """What a message from `sender` is worth if it arrived unverified."""
        return Provenance.HIGH if sender in self.registry else tag_external_tool()


def inner_model(message: BaseModel) -> BaseModel:
    """The message inside a signed envelope, or the message itself."""
    return message.model if isinstance(message, _Envelope) else message


@dataclass(slots=True)
class _Envelope:
    """Signed wrapper."""

    topic: str
    model: BaseModel
    sender: str
    signature: str
