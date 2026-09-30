"""
Agent identities (NHI): HMAC-SHA256 keys for telemetry, and Ed25519 key pairs where the verifier
must not be able to sign.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str
    public_id: str
    _secret: bytes

    def sign(self, payload: bytes) -> str:
        return hmac.new(self._secret, payload, hashlib.sha256).hexdigest()

    def verify(self, payload: bytes, signature: str) -> bool:
        expected = self.sign(payload)
        return hmac.compare_digest(expected, signature)


def issue_identity(agent_id: str, *, seed: bytes | None = None) -> AgentIdentity:
    """Issue a software-bound identity."""
    secret = seed if seed is not None else secrets.token_bytes(32)
    public_id = hashlib.sha256(secret + agent_id.encode()).hexdigest()[:16]
    return AgentIdentity(agent_id=agent_id, public_id=public_id, _secret=secret)


def verify_binding(identity: AgentIdentity, claimed_agent_id: str) -> bool:
    return identity.agent_id == claimed_agent_id


@dataclass(frozen=True)
class VerifyingIdentity:
    """A public key under an agent's name."""

    agent_id: str
    public_key: bytes

    @property
    def public_id(self) -> str:
        return hashlib.sha256(self.public_key).hexdigest()[:16]

    def sign(self, payload: bytes) -> str:
        raise PermissionError(f"{self.agent_id}: a public key cannot sign")

    def verify(self, payload: bytes, signature: str) -> bool:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        try:
            Ed25519PublicKey.from_public_bytes(self.public_key).verify(
                bytes.fromhex(signature), payload
            )
        except (InvalidSignature, ValueError):
            return False
        return True


@dataclass(frozen=True)
class SigningIdentity:
    """An Ed25519 private key under an agent's name, held by that agent alone."""

    agent_id: str
    _private: bytes

    def public(self) -> VerifyingIdentity:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

        key = Ed25519PrivateKey.from_private_bytes(self._private).public_key()
        return VerifyingIdentity(
            agent_id=self.agent_id,
            public_key=key.public_bytes(Encoding.Raw, PublicFormat.Raw),
        )

    @property
    def public_id(self) -> str:
        return self.public().public_id

    def sign(self, payload: bytes) -> str:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        return Ed25519PrivateKey.from_private_bytes(self._private).sign(payload).hex()

    def verify(self, payload: bytes, signature: str) -> bool:
        return self.public().verify(payload, signature)


def issue_signing_identity(agent_id: str, *, seed: bytes | None = None) -> SigningIdentity:
    """An Ed25519 identity."""
    material = hashlib.sha256(seed).digest() if seed is not None else secrets.token_bytes(32)
    return SigningIdentity(agent_id=agent_id, _private=material)
