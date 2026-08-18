"""Encode/decode for the four SAIL lanes. Roundtrip is an invariant."""

from __future__ import annotations

import json
import struct
from typing import Any

from sail.envelope import (
    LANE_EXPRESS,
    LANE_HUMAN,
    LANE_SEMANTIC,
    LANE_STRUCTURED,
    LANES,
    MessagePart,
)
from sail.memory import VECTOR_DIM, embed

CONTENT_EXPRESS = "application/sail.express"
CONTENT_SEMANTIC = "application/sail.semantic+json"
CONTENT_STRUCTURED = "application/sail.structured+json"
CONTENT_HUMAN = "text/plain"

_STRUCT_HDR = struct.Struct("!I")


def encode(lane: str, payload: Any) -> MessagePart:
    if lane == LANE_EXPRESS:
        values = _as_float_tuple(payload)
        body = _pack_floats(values)
        return MessagePart(CONTENT_EXPRESS, body)
    if lane == LANE_SEMANTIC:
        text, vector = _semantic_pair(payload)
        return MessagePart(
            CONTENT_SEMANTIC,
            json.dumps({"text": text, "vector": list(vector)}, ensure_ascii=False, separators=(",", ":")),
        )
    if lane == LANE_STRUCTURED:
        doc = _as_structured(payload)
        return MessagePart(
            CONTENT_STRUCTURED,
            json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        )
    if lane == LANE_HUMAN:
        if not isinstance(payload, str):
            raise TypeError("human lane payload must be str")
        return MessagePart(CONTENT_HUMAN, payload)
    raise ValueError(f"unknown lane {lane!r}")


def decode(lane: str, part: MessagePart) -> Any:
    if lane == LANE_EXPRESS:
        if part.content_type != CONTENT_EXPRESS:
            raise ValueError(f"express part has content_type {part.content_type!r}")
        return _unpack_floats(part.data)
    if lane == LANE_SEMANTIC:
        if part.content_type != CONTENT_SEMANTIC:
            raise ValueError(f"semantic part has content_type {part.content_type!r}")
        raw = json.loads(part.data)
        text = raw["text"]
        vector = tuple(float(x) for x in raw["vector"])
        return {"text": text, "vector": vector}
    if lane == LANE_STRUCTURED:
        if part.content_type != CONTENT_STRUCTURED:
            raise ValueError(f"structured part has content_type {part.content_type!r}")
        doc = json.loads(part.data)
        return {
            "goal": doc.get("goal", ""),
            "concepts": list(doc.get("concepts") or []),
            "relations": list(doc.get("relations") or []),
        }
    if lane == LANE_HUMAN:
        if part.content_type != CONTENT_HUMAN:
            raise ValueError(f"human part has content_type {part.content_type!r}")
        if not isinstance(part.data, str):
            raise TypeError("human part data must be str")
        return part.data
    raise ValueError(f"unknown lane {lane!r}")


def _as_float_tuple(payload: Any) -> tuple[float, ...]:
    if isinstance(payload, (int, float)):
        return (float(payload),)
    if not isinstance(payload, (list, tuple)):
        raise TypeError("express lane payload must be a float or a sequence of floats")
    return tuple(float(x) for x in payload)


def _pack_floats(values: tuple[float, ...]) -> bytes:
    return _STRUCT_HDR.pack(len(values)) + struct.pack("!" + "d" * len(values), *values)


def _unpack_floats(data: bytes) -> tuple[float, ...]:
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("express part data must be bytes")
    (n,) = _STRUCT_HDR.unpack(data[:4])
    expected = 4 + 8 * n
    if len(data) != expected:
        raise ValueError(f"express payload length {len(data)} != {expected}")
    if n == 0:
        return ()
    return struct.unpack("!" + "d" * n, data[4:])


def _semantic_pair(payload: Any) -> tuple[str, tuple[float, ...]]:
    if isinstance(payload, str):
        text = payload
        vector = embed(text)
    elif isinstance(payload, dict):
        text = str(payload.get("text", ""))
        stored = payload.get("vector")
        vector = tuple(float(x) for x in stored) if stored is not None else embed(text)
        if len(vector) != VECTOR_DIM:
            raise ValueError(f"semantic vector dim {len(vector)} != {VECTOR_DIM}")
    else:
        raise TypeError("semantic lane payload must be str or {text, vector}")
    return text, vector


def _as_structured(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TypeError("structured lane payload must be a dict")
    goal = payload.get("goal", "")
    if not isinstance(goal, str):
        raise TypeError("structured.goal must be str")
    concepts = list(payload.get("concepts") or [])
    if not all(isinstance(c, str) for c in concepts):
        raise TypeError("structured.concepts must be str list")
    relations = []
    for rel in payload.get("relations") or []:
        if not isinstance(rel, dict):
            raise TypeError("structured.relations items must be dicts")
        relations.append(
            {
                "src": str(rel.get("src", rel.get("from", ""))),
                "dst": str(rel.get("dst", rel.get("to", ""))),
                "type": str(rel.get("type", "")),
            }
        )
    return {"goal": goal, "concepts": concepts, "relations": relations}


__all__ = ["LANES", "decode", "encode"]
