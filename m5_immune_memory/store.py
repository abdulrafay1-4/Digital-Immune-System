"""Immune memory store: FAISS `IndexFlatIP` for vectors, SQLite for metadata."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass

import faiss
import numpy as np

from shared.integrity import canonical, sign
from shared.keys import derive
from shared.schemas import MemoryRecord

_SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    row_id             INTEGER PRIMARY KEY,
    record_id          TEXT    NOT NULL UNIQUE,
    pattern_text       TEXT    NOT NULL,
    threat_type        TEXT    NOT NULL,
    node_ids           TEXT    NOT NULL,
    window_start_sim   REAL    NOT NULL,
    window_end_sim     REAL    NOT NULL,
    proposer_id        TEXT    NOT NULL,
    embedding_dim      INTEGER NOT NULL,
    quorum_certificate TEXT,
    sim_time           REAL    NOT NULL,
    run_id             TEXT    NOT NULL,
    seed               INTEGER NOT NULL,
    config_hash        TEXT    NOT NULL,
    status             TEXT    NOT NULL DEFAULT 'pending',
    adjudicated_by     TEXT,
    adjudication_sim   REAL,
    adjudication_signature TEXT
);
CREATE INDEX IF NOT EXISTS idx_records_pattern ON records (pattern_text, threat_type);
"""


def adjudication_payload(record_id: str, status: str, actor: str, sim_time: float) -> bytes:
    """What an adjudication signature covers."""
    return canonical("memory-adjudication", record_id, status, actor, float(sim_time))


@dataclass(frozen=True)
class SearchHit:
    record: MemoryRecord
    similarity: float


class MemoryStore:
    """Vectors in FAISS, metadata in SQLite, kept in lockstep by insertion order."""

    def __init__(self, *, dim: int = 384, db_path: str = ":memory:") -> None:
        self._dim = dim
        self._index = faiss.IndexFlatIP(dim)
        self._db = sqlite3.connect(db_path)
        self._db.row_factory = sqlite3.Row
        self._db.executescript(_SCHEMA)

    @property
    def dim(self) -> int:
        return self._dim

    def __len__(self) -> int:
        return int(self._index.ntotal)

    def add(self, record: MemoryRecord, vector: np.ndarray) -> None:
        """Append one record."""
        vec = np.asarray(vector, dtype=np.float32).reshape(1, -1)
        if vec.shape[1] != self._dim:
            raise ValueError(f"expected a {self._dim}-d vector, got {vec.shape[1]}")
        if self.get(record.record_id) is not None:
            raise ValueError(f"record_id already stored: {record.record_id}")

        with self._db:
            self._db.execute(
                "INSERT INTO records (record_id, pattern_text, threat_type, node_ids,"
                " window_start_sim, window_end_sim, proposer_id, embedding_dim,"
                " quorum_certificate, sim_time, run_id, seed, config_hash, status)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    record.record_id,
                    record.pattern_text,
                    record.threat_type,
                    json.dumps(sorted(record.node_ids)),
                    record.window_start_sim,
                    record.window_end_sim,
                    record.proposer_id,
                    record.embedding_dim,
                    record.quorum_certificate,
                    record.sim_time,
                    record.run_id,
                    record.seed,
                    record.config_hash,
                    "pending",
                ),
            )
        self._index.add(vec)

    def search(self, vector: np.ndarray, k: int = 5) -> list[SearchHit]:
        """`k` nearest by cosine similarity, best first."""
        if k < 1:
            raise ValueError(f"k must be at least 1, got {k}")
        if len(self) == 0:
            return []

        vec = np.asarray(vector, dtype=np.float32).reshape(1, -1)
        if vec.shape[1] != self._dim:
            raise ValueError(f"expected a {self._dim}-d vector, got {vec.shape[1]}")

        scores, positions = self._index.search(vec, min(k, len(self)))
        hits = []
        for score, position in zip(scores[0], positions[0], strict=True):
            if position < 0:
                continue
            record = self._by_row_id(int(position) + 1)
            if record is not None:
                hits.append(SearchHit(record=record, similarity=float(score)))
        hits.sort(key=lambda h: (-h.similarity, h.record.record_id))
        return hits

    def adjudicate(
        self,
        record_id: str,
        status: str,
        *,
        actor: str,
        sim_time: float,
        key: bytes | None = None,
    ) -> MemoryRecord:
        """Record what an incident *meant*."""
        if status not in ("confirmed", "benign"):
            raise ValueError(f"adjudication must be confirmed or benign, got {status}")
        if self.get(record_id) is None:
            raise KeyError(record_id)
        signature = sign(
            adjudication_payload(record_id, status, actor, sim_time),
            key if key is not None else derive("adjudication"),
        )
        with self._db:
            self._db.execute(
                "UPDATE records SET status = ?, adjudicated_by = ?, adjudication_sim = ?,"
                " adjudication_signature = ? WHERE record_id = ?",
                (status, actor, float(sim_time), signature, record_id),
            )
        record = self.get(record_id)
        assert record is not None
        return record

    def get(self, record_id: str) -> MemoryRecord | None:
        row = self._db.execute("SELECT * FROM records WHERE record_id = ?", (record_id,)).fetchone()
        return _row_to_record(row) if row is not None else None

    def find_pattern(self, pattern_text: str, threat_type: str) -> MemoryRecord | None:
        """The first record stored for exactly this pattern and label, if any."""
        row = self._db.execute(
            "SELECT * FROM records WHERE pattern_text = ? AND threat_type = ?"
            " ORDER BY row_id LIMIT 1",
            (pattern_text, threat_type),
        ).fetchone()
        return _row_to_record(row) if row is not None else None

    def all_records(self) -> list[MemoryRecord]:
        rows = self._db.execute("SELECT * FROM records ORDER BY row_id").fetchall()
        return [_row_to_record(r) for r in rows]

    def close(self) -> None:
        self._db.close()

    def _by_row_id(self, row_id: int) -> MemoryRecord | None:
        row = self._db.execute("SELECT * FROM records WHERE row_id = ?", (row_id,)).fetchone()
        return _row_to_record(row) if row is not None else None


def _row_to_record(row: sqlite3.Row) -> MemoryRecord:
    return MemoryRecord(
        sim_time=row["sim_time"],
        run_id=row["run_id"],
        seed=row["seed"],
        config_hash=row["config_hash"],
        record_id=row["record_id"],
        pattern_text=row["pattern_text"],
        threat_type=row["threat_type"],
        node_ids=json.loads(row["node_ids"]),
        window_start_sim=row["window_start_sim"],
        window_end_sim=row["window_end_sim"],
        proposer_id=row["proposer_id"],
        embedding_dim=row["embedding_dim"],
        quorum_certificate=row["quorum_certificate"],
        status=row["status"],
        adjudicated_by=row["adjudicated_by"],
        adjudication_sim=row["adjudication_sim"],
        adjudication_signature=row["adjudication_signature"],
    )
