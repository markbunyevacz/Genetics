"""Versioned PREPARE-12 knowledge extract. Pairing is keyed by (gene, ATC5). Missing mapping stays null — no dummy PM."""
from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pce_shadow.f5_rec import apply_f5_source

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "tests" / "fixtures" / "shadow-v0" / "cyp2d6-knowledge.v0.json"


class KnowledgeTable:
    def __init__(
        self,
        path: str | Path | None = None,
        *,
        f5_source: str | None = None,
        f5_fetch: Callable[[], list[Any]] | None = None,
    ) -> None:
        self.path = Path(path) if path else DEFAULT_PATH
        self.f5_source = "off"
        self.doc: dict[str, Any] = json.loads(self.path.read_text(encoding="utf-8"))
        self.config_id: str = str(self.doc["id"])
        self._dip: dict[tuple[str, str], dict[str, Any]] = {}
        for row in self.doc.get("diplotype_phenotype") or []:
            self._dip[(row["gene"], row["diplotype"])] = row
        self._inhibitors: dict[str, dict[str, Any]] = {}
        for row in self.doc.get("strong_cyp2d6_inhibitors") or []:
            self._inhibitors[str(row["atc5"]).upper()] = row
        self._pairings: dict[tuple[str, str], dict[str, Any]] = {}
        for row in self.doc.get("pairings") or []:
            gene = str(row.get("gene") or "").strip()
            atc5 = str(row.get("atc5") or "").strip().upper()
            if gene and atc5:
                self._pairings[(gene, atc5)] = row
        for rel in self.doc.get("extra_pairing_files") or []:
            extra = json.loads((ROOT / rel).read_text(encoding="utf-8"))
            for row in extra.get("pairings") or []:
                self.add_pairing(row, source=str(rel))
        self.warfarin = dict(self.doc.get("warfarin_diagram") or {})
        adj = self.doc.get("phenotype_adjustment") or {}
        self.nm_plus_strong: str | None = adj.get("nm_plus_strong_inhibitor")
        self.adjustment_status: str = str(adj.get("status") or "unknown")
        self.adjustment_status_hu: str = str(adj.get("status_hu") or "")
        self.egfr_threshold = int(self.doc.get("egfr_threshold") or 30)
        self.inventory: dict[str, Any] = dict(self.doc.get("inventory") or {})
        self.phenotype_labels: dict[str, Any] = dict(self.doc.get("phenotype_labels") or {})
        self.strategy_labels_hu: dict[str, str] = {
            str(k): str(v) for k, v in (self.doc.get("strategy_labels_hu") or {}).items()
        }
        apply_f5_source(self, source=f5_source, fetch=f5_fetch)

    def phenotype_hu(self, code: str | None) -> str | None:
        if not code:
            return None
        row = self.phenotype_labels.get(code) or {}
        hu = row.get("hu")
        return str(hu) if hu else None

    def genotype_phenotype(self, gene: str, diplotype: str) -> dict[str, Any] | None:
        exact = self._dip.get((gene, diplotype))
        if exact:
            return exact
        if "/" in diplotype:
            left, right = diplotype.split("/", 1)
            swapped = self._dip.get((gene, f"{right}/{left}"))
            if swapped:
                return swapped
        if gene == "HLA-B":
            return self._hla_b_row(diplotype)
        return None

    def _hla_b_row(self, diplotype: str) -> dict[str, Any] | None:
        blob = diplotype.replace("HLA-B", "").replace(" ", "").lower()
        checks = (
            ("57:01", "POS_5701", "NEG_5701", "*57:01 positive", "*57:01 negative"),
            ("58:01", "POS_5801", "NEG_5801", "*58:01 positive", "*58:01 negative"),
            ("15:02", "POS_1502", "NEG_1502", "*15:02 positive", "*15:02 negative"),
        )
        for token, _pos, _neg, pos_dip, neg_dip in checks:
            if token in blob and "neg" in blob:
                return self._dip.get(("HLA-B", neg_dip))
            if token in blob:
                return self._dip.get(("HLA-B", pos_dip))
        if blob in {"*x/*x", "negative", "negatív"}:
            return self._dip.get(("HLA-B", "*57:01 negative"))
        return None

    def strong_inhibitor(self, atc: str) -> dict[str, Any] | None:
        return self._inhibitors.get(atc.strip().upper())

    def add_pairing(self, row: dict[str, Any], *, source: str = "extra") -> None:
        gene = str(row.get("gene") or "").strip()
        atc5 = str(row.get("atc5") or "").strip().upper()
        if not gene or not atc5:
            raise ValueError(f"pairing from {source} needs gene and atc5")
        key = (gene, atc5)
        if key in self._pairings:
            raise ValueError(
                f"refusing to overwrite pairing {gene} {atc5} from {source}; "
                "index pairs are immutable"
            )
        self._pairings[key] = row

    def pairing(self, gene: str, atc5: str) -> dict[str, Any] | None:
        return self._pairings.get((gene, atc5.strip().upper()))

    def pairings(self) -> list[dict[str, Any]]:
        return list(self._pairings.values())

    def inhibitor_atc5_codes(self) -> list[str]:
        return list(self._inhibitors)

    def pairing_atc5_codes(self, gene: str | None = None) -> list[str]:
        if gene is None:
            return [atc5 for (_gene, atc5) in self._pairings]
        return [atc5 for (g, atc5) in self._pairings if g == gene]


def default_table() -> KnowledgeTable:
    return KnowledgeTable()
