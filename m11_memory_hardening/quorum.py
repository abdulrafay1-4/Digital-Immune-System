"""M11 quorum gate: no single component writes to immune memory."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from m10_persona_drift.nhi import AgentIdentity

DEFAULT_K = 3


class RejectReason(StrEnum):
    """Why one attestation did not count."""

    UNKNOWN_ATTESTER = "unknown_attester"
    BAD_SIGNATURE = "bad_signature"
    WRONG_RECORD = "wrong_record"
    EXPIRED = "expired"
    DUPLICATE = "duplicate"
    PROPOSER = "proposer"
    QUARANTINED = "quarantined"


@dataclass(frozen=True)
class MemoryCandidate:
    """A proposed record."""

    record_id: str
    pattern_text: str
    threat_type: str
    node_ids: tuple[str, ...]
    window_start_sim: float
    window_end_sim: float
    run_id: str
    seed: int
    config_hash: str
    proposer_id: str

    def record_hash(self) -> str:
        """Canonical hash every attester signs."""
        parts = (
            self.record_id,
            self.pattern_text,
            self.threat_type,
            ",".join(sorted(self.node_ids)),
            f"{self.window_start_sim!r}",
            f"{self.window_end_sim!r}",
            self.run_id,
            str(self.seed),
            self.config_hash,
        )
        return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()


@dataclass(frozen=True)
class Attestation:
    """One attester's signature over a candidate's record hash."""

    record_hash: str
    attester_id: str
    signature: str
    sim_time: float


@dataclass(frozen=True)
class QuorumParams:
    k: int = DEFAULT_K
    window_sim: float = 3.0

    def __post_init__(self) -> None:
        if self.k < 1:
            raise ValueError(f"k must be at least 1, got {self.k}")
        if self.window_sim <= 0:
            raise ValueError(f"window_sim must be positive, got {self.window_sim}")


@dataclass(frozen=True)
class QuorumDecision:
    admitted: bool
    can_admit: bool = True
    usable: int = 0
    accepted: tuple[str, ...] = ()
    rejected: tuple[tuple[str, RejectReason], ...] = ()
    certificate: str | None = None
    k: int = 0
    n: int = 0

    @property
    def shortfall(self) -> int:
        return max(0, self.k - len(self.accepted))


def attest(
    candidate: MemoryCandidate,
    identity: AgentIdentity,
    *,
    sim_time: float,
) -> Attestation:
    """Produce one attester's signature."""
    record_hash = candidate.record_hash()
    return Attestation(
        record_hash=record_hash,
        attester_id=identity.agent_id,
        signature=identity.sign(record_hash.encode()),
        sim_time=sim_time,
    )


@dataclass
class QuorumGate:
    """Counts attestations."""

    registry: Mapping[str, AgentIdentity]
    params: QuorumParams = field(default_factory=QuorumParams)
    quarantined: frozenset[str] = frozenset()

    @property
    def n(self) -> int:
        return len(self.registry)

    @property
    def usable(self) -> int:
        """Registered attesters not currently quarantined."""
        return len(set(self.registry) - set(self.quarantined))

    @property
    def can_admit(self) -> bool:
        """False when quarantine has left fewer than `k` attesters available."""
        return self.usable >= self.params.k

    def admit(
        self,
        candidate: MemoryCandidate,
        attestations: Iterable[Attestation],
        *,
        now_sim: float,
    ) -> QuorumDecision:
        expected_hash = candidate.record_hash()
        accepted: list[str] = []
        rejected: list[tuple[str, RejectReason]] = []
        signatures: dict[str, str] = {}
        seen: set[str] = set()

        for att in attestations:
            reason = self._reject_reason(att, candidate, expected_hash, now_sim, seen)
            if reason is not None:
                rejected.append((att.attester_id, reason))
                continue
            seen.add(att.attester_id)
            accepted.append(att.attester_id)
            signatures[att.attester_id] = att.signature

        admitted = len(accepted) >= self.params.k
        return QuorumDecision(
            can_admit=self.can_admit,
            usable=self.usable,
            admitted=admitted,
            accepted=tuple(sorted(accepted)),
            rejected=tuple(rejected),
            certificate=_certificate(expected_hash, signatures) if admitted else None,
            k=self.params.k,
            n=self.n,
        )

    def _reject_reason(
        self,
        att: Attestation,
        candidate: MemoryCandidate,
        expected_hash: str,
        now_sim: float,
        seen: set[str],
    ) -> RejectReason | None:
        """First failing rule wins."""
        if att.attester_id == candidate.proposer_id:
            return RejectReason.PROPOSER
        if att.attester_id in seen:
            return RejectReason.DUPLICATE
        identity = self.registry.get(att.attester_id)
        if identity is None:
            return RejectReason.UNKNOWN_ATTESTER
        if att.attester_id in self.quarantined:
            return RejectReason.QUARANTINED
        if att.record_hash != expected_hash:
            return RejectReason.WRONG_RECORD
        age = now_sim - att.sim_time
        if age < 0 or age > self.params.window_sim:
            return RejectReason.EXPIRED
        if not identity.verify(expected_hash.encode(), att.signature):
            return RejectReason.BAD_SIGNATURE
        return None


def _certificate(record_hash: str, signatures: Mapping[str, str]) -> str:
    """Deterministic certificate: sorted `attester:signature` pairs over one hash."""
    body = ";".join(f"{a}:{signatures[a]}" for a in sorted(signatures))
    return f"{record_hash}|{body}"


def verify_certificate(
    certificate: str,
    candidate: MemoryCandidate,
    registry: Mapping[str, AgentIdentity],
    *,
    k: int = DEFAULT_K,
) -> bool:
    """Re-check a stored certificate without re-running the gate."""
    expected_hash = candidate.record_hash()
    head, _, body = certificate.partition("|")
    if head != expected_hash or not body:
        return False

    valid: set[str] = set()
    for pair in body.split(";"):
        attester_id, _, signature = pair.partition(":")
        identity = registry.get(attester_id)
        if identity is None or attester_id == candidate.proposer_id:
            return False
        if not identity.verify(expected_hash.encode(), signature):
            return False
        valid.add(attester_id)
    return len(valid) >= k
