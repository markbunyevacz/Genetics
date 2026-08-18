"""In-process agent bus. No HTTP, no ACP, no A2A SDK."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from sail.envelope import Envelope

Handler = Callable[[Envelope], Envelope]


class UnknownAgentError(KeyError):
    pass


class InProcessBus:
    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}
        self.transits: list[dict[str, Any]] = []

    def register(self, name: str, handler: Handler) -> None:
        if not name:
            raise ValueError("agent name must be non-empty")
        self._handlers[name] = handler

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))

    def send(self, message: Envelope) -> Envelope:
        handler = self._handlers.get(message.recipient)
        if handler is None:
            raise UnknownAgentError(message.recipient)
        t0 = time.perf_counter()
        reply = handler(message)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if not isinstance(reply, Envelope):
            raise TypeError("handler must return Envelope")
        self.transits.append(
            {
                "task_id": message.task_id,
                "sender": message.sender,
                "recipient": message.recipient,
                "lane": message.lane,
                "elapsed_ms": elapsed_ms,
            }
        )
        return reply
