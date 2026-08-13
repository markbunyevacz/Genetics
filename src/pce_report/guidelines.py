"""Load versioned CPIC pair + recommendation tables. No invented row text."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PREPARE12_INDEX = ROOT / "tests" / "fixtures" / "f1plus-v0" / "prepare12" / "index.v0.json"


class GuidelineTable:
    def __init__(
        self,
        pairs_path: Path | None = None,
        recommendations_path: Path | None = None,
        *,
        index_path: Path | None = None,
    ) -> None:
        self.pairs: list[dict[str, Any]] = []
        self.recommendations: list[dict[str, Any]] = []
        self.guidelines: list[dict[str, Any]] = []
        self.gene_meta: dict[str, dict[str, Any]] = {}
        self.pairs_source: dict[str, Any] = {}
        self.recs_source: dict[str, Any] = {}
        self.accessed: str | None = None
        self.index_source: dict[str, Any] = {}
        if index_path is not None:
            self._load_index(Path(index_path))
            return
        if pairs_path is None or recommendations_path is None:
            raise ValueError("GuidelineTable needs index_path or both pair and recommendation files")
        self._load_pair_rec(Path(pairs_path), Path(recommendations_path))

    def _load_pair_rec(self, pairs_path: Path, recommendations_path: Path) -> None:
        pairs_doc = json.loads(pairs_path.read_text(encoding="utf-8"))
        recs_doc = json.loads(recommendations_path.read_text(encoding="utf-8"))
        self.pairs = list(pairs_doc["pairs"])
        self.recommendations = list(recs_doc["rows"])
        self.pairs_source = pairs_doc.get("source") or {}
        self.recs_source = recs_doc.get("source") or {}
        self.accessed = recs_doc.get("accessed") or pairs_doc.get("accessed")
        self.guidelines = recs_doc.get("guidelines") or []
        genes = {p.get("genesymbol") for p in self.pairs if p.get("genesymbol")}
        for gene in genes:
            if not isinstance(gene, str):
                continue
            self.gene_meta[gene] = {
                "pair_count": len(self.pairs_for_gene(gene)),
                "recommendation_count": len(self.rows_for_gene(gene)),
                "pair_api": self.pairs_source.get("api"),
                "rec_api": self.recs_source.get("api"),
                "hianyzik": [],
            }

    def _load_index(self, index_path: Path) -> None:
        index = json.loads(index_path.read_text(encoding="utf-8"))
        base = index_path.parent.parent
        self.accessed = index.get("accessed")
        self.index_source = index.get("source") or {}
        self.pairs_source = {
            "name": self.index_source.get("name"),
            "api": self.index_source.get("pair_api_template"),
            "who_obtains_hu": self.index_source.get("who_obtains_hu"),
        }
        self.recs_source = {
            "name": self.index_source.get("name"),
            "api": self.index_source.get("rec_api_template"),
            "do_not_invent_recommendation_text": True,
        }
        seen_pairs: set[Any] = set()
        seen_recs: set[Any] = set()
        seen_guidelines: set[Any] = set()
        for gene, meta in (index.get("genes") or {}).items():
            pair_file = base / meta["pairs_file"]
            rec_file = base / meta["recs_file"]
            pairs_doc = json.loads(pair_file.read_text(encoding="utf-8"))
            recs_doc = json.loads(rec_file.read_text(encoding="utf-8"))
            for pair in pairs_doc.get("pairs") or []:
                pid = pair.get("pairid")
                if pid in seen_pairs:
                    continue
                if pid is not None:
                    seen_pairs.add(pid)
                self.pairs.append(pair)
            for rec in recs_doc.get("rows") or []:
                rid = rec.get("recommendationid")
                if rid in seen_recs:
                    continue
                if rid is not None:
                    seen_recs.add(rid)
                self.recommendations.append(rec)
            for guideline in recs_doc.get("guidelines") or []:
                gid = guideline.get("id")
                if gid in seen_guidelines:
                    continue
                if gid is not None:
                    seen_guidelines.add(gid)
                self.guidelines.append(guideline)
            hianyzik = list(meta.get("hianyzik") or [])
            notes = [
                g.get("notesonusage")
                for g in (recs_doc.get("guidelines") or [])
                if g.get("notesonusage")
            ]
            status = {
                "pair_count": int(meta.get("pair_count") or 0),
                "recommendation_count": int(meta.get("recommendation_count") or 0),
                "pair_api": meta.get("pair_api"),
                "rec_api": meta.get("rec_api"),
                "hianyzik": hianyzik,
                "guideline_notesonusage": notes,
            }
            self.gene_meta[gene] = status

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

    def status_for_gene(self, gene: str) -> dict[str, Any]:
        meta = dict(self.gene_meta.get(gene) or {})
        pairs = self.pairs_for_gene(gene)
        recs = self.rows_for_gene(gene)
        meta.setdefault("pair_count", len(pairs))
        meta.setdefault("recommendation_count", len(recs))
        meta.setdefault("pair_api", (self.pairs_source or {}).get("api"))
        meta.setdefault("rec_api", (self.recs_source or {}).get("api"))
        hianyzik = list(meta.get("hianyzik") or [])
        for note in meta.get("guideline_notesonusage") or []:
            if note and str(note) not in hianyzik:
                hianyzik.append(str(note))
        if not pairs:
            msg = (
                f"CPIC pair_view tábla kell a {gene} génhez. "
                "Letöltés: a gyártó (ez a repo) a nyilvános CPIC API-ról, nem a labor. "
                f"URL: {meta.get('pair_api') or 'https://api.cpicpgx.org/v1/pair_view'}"
            )
            if msg not in hianyzik:
                hianyzik.append(msg)
        if not recs:
            msg = (
                f"CPIC recommendation_view sor nincs a {gene} génhez (kitalált adagolási szöveg nincs). "
                "Ha a CPIC később kiadja, a gyártó tölti le ugyaninnen. "
                f"URL: {meta.get('rec_api') or 'https://api.cpicpgx.org/v1/recommendation_view'}"
            )
            if msg not in hianyzik:
                hianyzik.append(msg)
        meta["hianyzik"] = hianyzik
        meta["beszerzes"] = {
            "kinek": "gyártó (ez a repo / engineering), nem a labor",
            "kitol": "CPIC / ClinPGx nyilvános API",
            "hogyan": "python3 tests/fixtures/f1plus-v0/extract_cpic_prepare12_tables.py",
            "mikorra": "a pair_view/recommendation_view már 2026-08-13-án letöltve; üres recommendation_view-nál nincs mit kitalálni, amíg a CPIC nem ad sort",
        }
        return meta


def prepare12_table(index_path: Path | None = None) -> GuidelineTable:
    return GuidelineTable(index_path=index_path or PREPARE12_INDEX)
