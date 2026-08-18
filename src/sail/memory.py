"""Deterministic hash embeddings and in-memory nearest-neighbour store.

No vendor embedding API, no numpy, no Faiss. SHA-256 projection is a local
stand-in for semantic vectors so tests run offline. It is not a
foundation-model embedding.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Any

VECTOR_DIM = 32
_TOKEN = re.compile(r"[0-9a-zà-öø-ÿ]+", re.IGNORECASE)


def embed(text: str, dim: int = VECTOR_DIM) -> tuple[float, ...]:
    """Feature-hash a string into a unit vector. Stable across processes."""
    if dim <= 0:
        raise ValueError("dim must be positive")
    acc = [0.0] * dim
    tokens = _TOKEN.findall(text.lower())
    if not tokens:
        tokens = ["_empty"]
    grams: list[str] = []
    for tok in tokens:
        grams.append(tok)
        if len(tok) >= 3:
            for i in range(len(tok) - 2):
                grams.append(tok[i : i + 3])
    for gram in grams:
        digest = hashlib.sha256(gram.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        acc[idx] += sign
    return _l2_normalize(acc)


def cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    if len(a) != len(b):
        raise ValueError("vector length mismatch")
    num = sum(x * y for x, y in zip(a, b))
    da = math.sqrt(sum(x * x for x in a))
    db = math.sqrt(sum(y * y for y in b))
    if da == 0.0 or db == 0.0:
        return 0.0
    return num / (da * db)


def _l2_normalize(acc: list[float]) -> tuple[float, ...]:
    norm = math.sqrt(sum(x * x for x in acc))
    if norm == 0.0:
        return tuple(acc)
    return tuple(x / norm for x in acc)


@dataclass(frozen=True)
class MemoryRecord:
    text: str
    vector: tuple[float, ...]
    lane: str
    task_kind: str
    recipient: str
    success: bool
    extra: tuple[tuple[str, str], ...] = ()


class VectorMemory:
    def __init__(self) -> None:
        self._rows: list[MemoryRecord] = []

    def __len__(self) -> int:
        return len(self._rows)

    def remember(
        self,
        text: str,
        *,
        lane: str,
        task_kind: str,
        recipient: str,
        success: bool,
        extra: dict[str, str] | None = None,
    ) -> MemoryRecord:
        rec = MemoryRecord(
            text=text,
            vector=embed(text),
            lane=lane,
            task_kind=task_kind,
            recipient=recipient,
            success=success,
            extra=tuple(sorted((extra or {}).items())),
        )
        self._rows.append(rec)
        return rec

    def nearest(
        self,
        text: str,
        *,
        k: int = 3,
        success_only: bool = True,
    ) -> list[tuple[float, MemoryRecord]]:
        query = embed(text)
        scored: list[tuple[float, MemoryRecord]] = []
        for rec in self._rows:
            if success_only and not rec.success:
                continue
            scored.append((cosine(query, rec.vector), rec))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[:k]

    def dump(self) -> list[dict[str, Any]]:
        return [
            {
                "text": r.text,
                "lane": r.lane,
                "task_kind": r.task_kind,
                "recipient": r.recipient,
                "success": r.success,
            }
            for r in self._rows
        ]
