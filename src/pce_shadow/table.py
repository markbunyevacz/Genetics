"""Versioned CYP2D6 knowledge extract. Missing mapping stays null — no dummy PM."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "tests" / "fixtures" / "shadow-v0" / "cyp2d6-knowledge.v0.json"


class KnowledgeTable:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else DEFAULT_PATH
        self.doc: dict[str, Any] = json.loads(self.path.read_text(encoding="utf-8"))
        self.config_id: str = str(self.doc["id"])
        self._dip: dict[tuple[str, str], dict[str, Any]] = {}
        for row in self.doc.get("diplotype_phenotype") or []:
            self._dip[(row["gene"], row["diplotype"])] = row
        self._inhibitors: dict[str, dict[str, Any]] = {}
        for row in self.doc.get("strong_cyp2d6_inhibitors") or []:
            self._inhibitors[str(row["atc5"]).upper()] = row
        self._pairings: dict[str, dict[str, Any]] = {}
        for row in self.doc.get("pairings") or []:
            self._pairings[str(row["atc5"]).upper()] = row
        adj = self.doc.get("phenotype_adjustment") or {}
        self.nm_plus_strong: str | None = adj.get("nm_plus_strong_inhibitor")
        self.adjustment_status: str = str(adj.get("status") or "unknown")
        self.egfr_threshold = int(self.doc.get("egfr_threshold") or 30)

    def genotype_phenotype(self, gene: str, diplotype: str) -> dict[str, Any] | None:
        return self._dip.get((gene, diplotype))

    def strong_inhibitor(self, atc: str) -> dict[str, Any] | None:
        return self._inhibitors.get(atc.strip().upper())

    def pairing(self, atc5: str) -> dict[str, Any] | None:
        return self._pairings.get(atc5.strip().upper())

    def pairings(self) -> list[dict[str, Any]]:
        return list(self._pairings.values())

    def inhibitor_atc5_codes(self) -> list[str]:
        return list(self._inhibitors)

    def pairing_atc5_codes(self) -> list[str]:
        return list(self._pairings)


def default_table() -> KnowledgeTable:
    return KnowledgeTable()
