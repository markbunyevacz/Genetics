"""Load versioned CPIC pair + recommendation tables. No invented row text."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class GuidelineTable:
    def __init__(self, pairs_path: Path, recommendations_path: Path) -> None:
        pairs_doc = json.loads(pairs_path.read_text(encoding="utf-8"))
        recs_doc = json.loads(recommendations_path.read_text(encoding="utf-8"))
        self.pairs: list[dict[str, Any]] = list(pairs_doc["pairs"])
        self.recommendations: list[dict[str, Any]] = list(recs_doc["rows"])
        self.pairs_source = pairs_doc.get("source") or {}
        self.recs_source = recs_doc.get("source") or {}
        self.accessed = recs_doc.get("accessed") or pairs_doc.get("accessed")
        self.guidelines = recs_doc.get("guidelines") or []

    def rows_for_gene(self, gene: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for rec in self.recommendations:
            lk = rec.get("lookupkey") or {}
            ph = rec.get("phenotypes") or {}
            if gene in lk or gene in ph:
                out.append(rec)
        return out

    def pairs_for_gene(self, gene: str) -> list[dict[str, Any]]:
        return [p for p in self.pairs if p.get("genesymbol") == gene]
