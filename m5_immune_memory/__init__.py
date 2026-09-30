"""M5 immune memory: FAISS and SQLite, quorum-gated writes, certificate-checked reads."""

from m5_immune_memory.embeddings import (
    EMBEDDING_DIM,
    Embedder,
    HashingEmbedder,
    SentenceTransformerEmbedder,
    default_embedder,
)
from m5_immune_memory.query import (
    MAX_CTI_BOOST,
    RECOGNITION_THRESHOLD,
    MemoryHit,
    MemoryQuery,
    Recognition,
)
from m5_immune_memory.store import MemoryStore, SearchHit
from m5_immune_memory.write_path import (
    CURATOR_ID,
    MATERIAL_LEVEL,
    IncidentSummary,
    LivenessMonitor,
    MemoryCurator,
    WritePath,
    WriteResult,
    is_material,
)

__all__ = [
    "CURATOR_ID",
    "EMBEDDING_DIM",
    "MATERIAL_LEVEL",
    "MAX_CTI_BOOST",
    "RECOGNITION_THRESHOLD",
    "Embedder",
    "HashingEmbedder",
    "IncidentSummary",
    "LivenessMonitor",
    "MemoryCurator",
    "MemoryHit",
    "MemoryQuery",
    "MemoryStore",
    "Recognition",
    "SearchHit",
    "SentenceTransformerEmbedder",
    "WritePath",
    "WriteResult",
    "default_embedder",
    "is_material",
]
