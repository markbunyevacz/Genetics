"""HITL operational errors. Not the B.5 clinical catalogue."""
from __future__ import annotations

from typing import Any


class HitlError(Exception):
    def __init__(
        self,
        code: str,
        *,
        http: int = 400,
        message_hu: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.http = http
        self.message_hu = message_hu
        self.extra = extra or {}
        super().__init__(code)

    def as_dict(self) -> dict[str, Any]:
        body = {"error": self.code, "http": self.http, "message_hu": self.message_hu}
        body.update(self.extra)
        return body
