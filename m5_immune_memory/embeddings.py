"""
Embeddings for immune memory: a deterministic hashing embedder (the default) and an optional
sentence-transformer.
"""

from __future__ import annotations

import hashlib
from typing import Protocol, runtime_checkable

import numpy as np

EMBEDDING_DIM = 384

MODEL_NAME = "all-MiniLM-L6-v2"

MAX_EMBED_CHARS = 4096


@runtime_checkable
class Embedder(Protocol):
    @property
    def dim(self) -> int: ...

    def embed(self, text: str) -> np.ndarray: ...


def l2_normalise(vec: np.ndarray) -> np.ndarray:
    """Unit-length, with a zero vector returned unchanged rather than as NaN."""
    norm = float(np.linalg.norm(vec))
    if norm == 0.0:
        return vec.astype(np.float32)
    return (vec / norm).astype(np.float32)


class HashingEmbedder:
    """Deterministic bag-of-tokens hashing into a fixed-width vector."""

    def __init__(self, dim: int = EMBEDDING_DIM) -> None:
        if dim < 1:
            raise ValueError(f"dim must be at least 1, got {dim}")
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, text: str) -> np.ndarray:
        text = text[:MAX_EMBED_CHARS]
        vec = np.zeros(self._dim, dtype=np.float32)
        for token in _tokenise(text):
            digest = hashlib.sha256(token.encode()).digest()
            index = int.from_bytes(digest[:4], "big") % self._dim
            sign = 1.0 if digest[4] & 1 else -1.0
            vec[index] += sign
        return l2_normalise(vec)


class SentenceTransformerEmbedder:
    """`all-MiniLM-L6-v2`."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        self._dim = int(self._model.get_sentence_embedding_dimension())

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, text: str) -> np.ndarray:
        text = text[:MAX_EMBED_CHARS]
        vec = self._model.encode(text, convert_to_numpy=True, show_progress_bar=False)
        return l2_normalise(np.asarray(vec, dtype=np.float32))


def _tokenise(text: str) -> list[str]:
    """Lowercased alphanumeric runs."""
    out: list[str] = []
    current: list[str] = []
    for ch in text.lower():
        if ch.isalnum():
            current.append(ch)
        elif current:
            out.append("".join(current))
            current = []
    if current:
        out.append("".join(current))
    return out


def default_embedder() -> Embedder:
    """The deterministic one."""
    return HashingEmbedder()
