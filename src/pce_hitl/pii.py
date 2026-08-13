"""Reject free-text that looks like TAJ, email, or direct identifiers (FR-450)."""
from __future__ import annotations

import re

TAJ_RE = re.compile(r"\b\d{3}[-\s]?\d{3}[-\s]?\d{3}\b")
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
FORBIDDEN = (
    "taj",
    "szület",
    "szulet",
    "birth",
    "patient.name",
    "orvosnév",
    "orvosnev",
    "syn-taj",
    "syn-name",
)


def pii_hits(text: str) -> list[str]:
    hits: list[str] = []
    raw = text or ""
    lower = raw.lower()
    if TAJ_RE.search(raw):
        hits.append("taj_digits")
    if EMAIL_RE.search(raw):
        hits.append("email")
    for token in FORBIDDEN:
        if token in lower:
            hits.append(token)
    return hits
