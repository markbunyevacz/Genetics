"""Pinned DPWG / FDA version stamps for the F1+ lelet. No invented dosing rows."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PINS_PATH = ROOT / "tests" / "fixtures" / "f1plus-v0" / "static-guideline-pins.v0.json"
DPWG_INDEX_PATH = ROOT / "tests" / "fixtures" / "f1plus-v0" / "dpwg-prepare12-index.v0.json"
FDA_EXTRACT_PATH = ROOT / "tests" / "fixtures" / "f1plus-v0" / "fda-ddi-table-2-2-cyp2d6-strong.v0.json"


@lru_cache(maxsize=1)
def pins() -> dict[str, Any]:
    return json.loads(PINS_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def dpwg_index() -> dict[str, Any]:
    return json.loads(DPWG_INDEX_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def fda_extract() -> dict[str, Any]:
    return json.loads(FDA_EXTRACT_PATH.read_text(encoding="utf-8"))


def dpwg_version() -> str:
    return str(pins()["dpwg_version"])


def fda_table_version() -> str:
    return str(pins()["fda_table_version"])


def dpwg_for_gene(gene: str) -> dict[str, Any]:
    idx = dpwg_index()
    meta = (idx.get("genes") or {}).get(gene) or {"count": 0, "annotations": []}
    annotations = []
    for row in meta.get("annotations") or []:
        annotations.append(
            {
                "id": row.get("id"),
                "name": row.get("name"),
                "url": row.get("url"),
                "recommendation": row.get("recommendation"),
                "drugs": list(row.get("drugs") or []),
                "summary_en": row.get("summary_en"),
            }
        )
    src = idx.get("source") or {}
    return {
        "source": "DPWG",
        "version": dpwg_version(),
        "api": src.get("api") or pins().get("dpwg_api"),
        "accessed": idx.get("accessed") or pins().get("dpwg_accessed"),
        "on_disk": src.get("on_disk"),
        "publisher_landing": src.get("publisher_landing"),
        "do_not_invent_recommendation_text": True,
        "do_not_merge_with_cpic": True,
        "annotation_count": int(meta.get("count") or 0),
        "annotations": annotations,
    }


def fda_source() -> dict[str, Any]:
    ext = fda_extract()
    return {
        "source": "FDA",
        "version": fda_table_version(),
        "table": ext.get("table"),
        "url": ext.get("url") or pins().get("fda_url"),
        "accessed": ext.get("accessed") or pins().get("fda_accessed"),
        "on_disk_html": ext.get("on_disk_html"),
        "cyp2d6_strong_index_inhibitors": list(ext.get("cyp2d6_strong_index_inhibitors") or []),
        "claim_en": ext.get("claim_en"),
        "dosing_rows_extracted": False,
    }
