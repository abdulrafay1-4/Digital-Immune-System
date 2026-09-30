"""M5 read path: recall, and the one route it has into behaviour."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from m5_immune_memory.embeddings import Embedder, default_embedder
from m5_immune_memory.store import MemoryStore, adjudication_payload
from m10_persona_drift.nhi import AgentIdentity
from m11_memory_hardening.quorum import DEFAULT_K, MemoryCandidate, verify_certificate
from shared.integrity import verify
from shared.keys import derive

RECOGNITION_THRESHOLD = 0.60

MAX_CTI_BOOST = 0.25


@dataclass(frozen=True)
class MemoryHit:
    """What a caller gets back."""

    record_id: str
    similarity: float
    threat_type: str
    node_ids: tuple[str, ...]


@dataclass(frozen=True)
class Recognition:
    """The answer to "have we seen this before", in a form fusion can consume."""

    recognised: bool
    hits: tuple[MemoryHit, ...] = ()
    uncertified: tuple[str, ...] = ()
    pending: tuple[str, ...] = ()
    suppressed_by: tuple[str, ...] = ()

    @property
    def best(self) -> MemoryHit | None:
        return self.hits[0] if self.hits else None

    @property
    def cti_boost(self) -> float:
        """Bounded contribution to `CTI_i`."""
        if not self.recognised or self.best is None:
            return 0.0
        span = 1.0 - RECOGNITION_THRESHOLD
        over = (self.best.similarity - RECOGNITION_THRESHOLD) / span
        return round(max(0.0, min(1.0, over)) * MAX_CTI_BOOST, 6)


@dataclass
class MemoryQuery:
    """Read-only view of immune memory."""

    store: MemoryStore
    registry: Mapping[str, AgentIdentity]
    embedder: Embedder = field(default_factory=default_embedder)
    k: int = 5
    threshold: float = RECOGNITION_THRESHOLD
    quorum_k: int = DEFAULT_K
    adjudication_key: bytes = field(default_factory=lambda: derive("adjudication"), repr=False)

    def recognise(self, pattern_text: str) -> Recognition:
        """Search on a pattern the deterministic layer built, not caller free text."""
        vector = self.embedder.embed(pattern_text)
        hits: list[MemoryHit] = []
        uncertified: list[str] = []
        pending: list[str] = []
        benign: list[tuple[float, str]] = []

        for hit in self.store.search(vector, k=self.k):
            record = hit.record
            if not self._certified(record):
                uncertified.append(record.record_id)
                continue
            if hit.similarity < self.threshold:
                continue
            if record.status == "pending":
                pending.append(record.record_id)
                continue
            if not self._adjudicated(record):
                uncertified.append(record.record_id)
                continue
            if record.status == "benign":
                benign.append((hit.similarity, record.record_id))
                continue
            hits.append(
                MemoryHit(
                    record_id=record.record_id,
                    similarity=round(hit.similarity, 6),
                    threat_type=record.threat_type,
                    node_ids=tuple(record.node_ids),
                )
            )

        best_benign = max((sim for sim, _ in benign), default=None)
        suppressed_by: tuple[str, ...] = ()
        if best_benign is not None:
            kept = [h for h in hits if h.similarity > best_benign]
            if len(kept) < len(hits):
                suppressed_by = tuple(sorted(rid for sim, rid in benign if sim == best_benign))
            hits = kept

        return Recognition(
            recognised=bool(hits),
            hits=tuple(hits),
            uncertified=tuple(sorted(uncertified)),
            pending=tuple(sorted(pending)),
            suppressed_by=suppressed_by,
        )

    def _adjudicated(self, record) -> bool:
        if not record.adjudication_signature or record.adjudicated_by is None:
            return False
        if record.adjudication_sim is None:
            return False
        return verify(
            adjudication_payload(
                record.record_id, record.status, record.adjudicated_by, record.adjudication_sim
            ),
            record.adjudication_signature,
            self.adjudication_key,
        )

    def _certified(self, record) -> bool:
        """Re-verify on every read."""
        if not record.quorum_certificate:
            return False
        candidate = MemoryCandidate(
            record_id=record.record_id,
            pattern_text=record.pattern_text,
            threat_type=record.threat_type,
            node_ids=tuple(sorted(record.node_ids)),
            window_start_sim=record.window_start_sim,
            window_end_sim=record.window_end_sim,
            run_id=record.run_id,
            seed=record.seed,
            config_hash=record.config_hash,
            proposer_id=record.proposer_id,
        )
        return verify_certificate(
            record.quorum_certificate, candidate, self.registry, k=self.quorum_k
        )
