"""Audit log: append-only, hash-chained under a key, and verifiable after the fact."""

from __future__ import annotations

import hmac
import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from shared.integrity import AUDIT_KEY, canonical, chain_hash, sign
from shared.schemas import AuditRecord

GENESIS = "0" * 64


def record_payload(record: AuditRecord) -> bytes:
    """Canonical bytes for one record."""
    return json.dumps(record.model_dump(), sort_keys=True, default=str).encode()


@dataclass(frozen=True)
class ChainedRecord:
    record: AuditRecord
    previous_hash: str
    hash: str

    def to_json(self) -> str:
        return json.dumps(
            {
                "previous_hash": self.previous_hash,
                "hash": self.hash,
                "record": self.record.model_dump(),
            },
            sort_keys=True,
            default=str,
        )


@dataclass(frozen=True)
class AuditCheckpoint:
    """How long the log was and where it ended, signed."""

    count: int
    head: str
    signature: str

    def as_dict(self) -> dict[str, object]:
        return {"count": self.count, "head": self.head, "signature": self.signature}


def _checkpoint_signature(count: int, head: str, key: bytes) -> str:
    return sign(canonical("audit-checkpoint", count, head), key)


def verify_checkpoint(checkpoint: AuditCheckpoint, key: bytes = AUDIT_KEY) -> bool:
    expected = _checkpoint_signature(checkpoint.count, checkpoint.head, key)
    return hmac.compare_digest(expected, checkpoint.signature)


@dataclass
class AuditLog:
    """Append-only chain."""

    path: Path | None = None
    max_in_memory: int = 20_000
    key: bytes = field(default=AUDIT_KEY, repr=False)
    _chain: list[ChainedRecord] = field(default_factory=list)
    _trimmed: bool = False
    _appended: int = 0
    _head: str = GENESIS

    def __post_init__(self) -> None:
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("", encoding="utf-8")

    @property
    def head(self) -> str:
        return self._head

    def __len__(self) -> int:
        return len(self._chain)

    def __iter__(self) -> Iterator[ChainedRecord]:
        return iter(self._chain)

    def append(self, record: AuditRecord) -> ChainedRecord:
        entry = ChainedRecord(
            record=record,
            previous_hash=self._head,
            hash=chain_hash(self._head, record_payload(record), self.key),
        )
        self._chain.append(entry)
        self._head = entry.hash
        self._appended += 1
        if 0 < self.max_in_memory < len(self._chain):
            del self._chain[0]
            self._trimmed = True
        if self.path is not None:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(entry.to_json() + "\n")
        return entry

    def checkpoint(self) -> AuditCheckpoint:
        """Record count and head, signed."""
        return AuditCheckpoint(
            count=self._appended,
            head=self._head,
            signature=_checkpoint_signature(self._appended, self._head, self.key),
        )

    @property
    def records(self) -> list[AuditRecord]:
        return [e.record for e in self._chain]

    def verify(self) -> int | None:
        """First broken link in the retained window, or `None` when it holds."""
        return verify_chain(self._chain, key=self.key, expect_genesis=not self._trimmed)


def verify_chain(
    entries: Iterable[ChainedRecord],
    *,
    key: bytes = AUDIT_KEY,
    expect_genesis: bool = True,
    checkpoint: AuditCheckpoint | None = None,
) -> int | None:
    """Recompute every link."""
    expected: str | None = GENESIS if expect_genesis else None
    count = 0
    for index, entry in enumerate(entries):
        if expected is None:
            expected = entry.previous_hash
        if entry.previous_hash != expected:
            return index
        if entry.hash != chain_hash(entry.previous_hash, record_payload(entry.record), key):
            return index
        expected = entry.hash
        count = index + 1

    if checkpoint is not None:
        if not verify_checkpoint(checkpoint, key):
            return 0
        head = expected if expected is not None else GENESIS
        if (expect_genesis and count != checkpoint.count) or head != checkpoint.head:
            return count
    return None


def load_chain(path: Path) -> list[ChainedRecord]:
    """Read a log back for offline verification."""
    out: list[ChainedRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        blob = json.loads(line)
        out.append(
            ChainedRecord(
                record=AuditRecord.model_validate(blob["record"]),
                previous_hash=blob["previous_hash"],
                hash=blob["hash"],
            )
        )
    return out
