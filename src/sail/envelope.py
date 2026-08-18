"""A2A-inspired in-process message envelope (no ACP SDK, no HTTP)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

LANE_EXPRESS = "express"
LANE_SEMANTIC = "semantic"
LANE_STRUCTURED = "structured"
LANE_HUMAN = "human"
LANES = (LANE_EXPRESS, LANE_SEMANTIC, LANE_STRUCTURED, LANE_HUMAN)

ROLES = ("user", "agent")


def new_id() -> str:
    return uuid4().hex


@dataclass(frozen=True)
class MessagePart:
    """One payload part. content_type is a media hint, not an HTTP header wire."""

    content_type: str
    data: Any


@dataclass(frozen=True)
class Envelope:
    role: str
    lane: str
    parts: tuple[MessagePart, ...]
    sender: str
    recipient: str
    task_kind: str
    task_id: str = field(default_factory=new_id)
    context_id: str = field(default_factory=new_id)
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise ValueError(f"role must be one of {ROLES}, got {self.role!r}")
        if self.lane not in LANES:
            raise ValueError(f"lane must be one of {LANES}, got {self.lane!r}")
        if not self.parts:
            raise ValueError("envelope needs at least one part")

    def primary(self) -> MessagePart:
        return self.parts[0]

    def meta_dict(self) -> dict[str, str]:
        return dict(self.metadata)
