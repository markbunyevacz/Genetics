"""F5 CPIC recommendation_view ingest. Default off. Mock is not a published CPIC row.

CPIC_F5_SOURCE=off|mock|live
  off  — prod default: no F5 pairing (API is empty today).
  mock — local tests/fixtures/cpic_f5_mock.json; full parse/transform/infer.
  live — GET CPIC recommendation_view; empty list → no pairing, no invented text.
"""
from __future__ import annotations

import copy
import json
import logging
import os
import urllib.request
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Protocol, runtime_checkable

log = logging.getLogger("pce_shadow.f5_rec")

ROOT = Path(__file__).resolve().parents[2]
MOCK_PATH = ROOT / "tests" / "fixtures" / "cpic_f5_mock.json"
SCHEMA_PATH = ROOT / "tests" / "fixtures" / "cpic_f5_recommendation.schema.json"
LIVE_URL = "https://api.cpicpgx.org/v1/recommendation_view?lookupkey->>F5=not.is.null"


class F5Source(Enum):
    DISABLED = "off"
    MOCK = "mock"
    LIVE = "live"

# pair_view uses ATC:G03A (group). Mock pairing uses one 7-character example.
MOCK_ATC5 = "G03AA07"
F5_ATC5 = MOCK_ATC5
MOCK_INN = "levonorgestrel and ethinylestradiol"
F5_SCHEMA_PATH = SCHEMA_PATH

PHENO_FROM_LOOKUP = {
    "heterozygous": "HET",
    "heterozygote": "HET",
    "factor v leiden heterozygote": "HET",
    "leiden heterozygote": "HET",
    "wild type": "WT",
    "wild-type": "WT",
    "negative": "WT",
    "factor v leiden negative": "WT",
    "homozygous": "HOM",
    "homozygote": "HOM",
    "leiden/leiden": "HOM",
}

DIPLOTYPE_ALIASES = {
    "HET": ("HET", "Leiden/WT", "WT/Leiden", "heterozygous", "rs6025 het"),
    "HOM": ("HOM", "Leiden/Leiden", "homozygous"),
    "WT": ("WT", "WT/WT", "wild type", "rs6025 reference"),
}


@runtime_checkable
class F5DataProvider(Protocol):
    """Business logic talks only to this. No HTTP client in infer/transform."""

    def rows(self) -> list[dict[str, Any]]:
        ...


RecViewProvider = F5DataProvider


def resolve_source(explicit: str | F5Source | None = None) -> F5Source:
    if isinstance(explicit, F5Source):
        return explicit
    raw = explicit if explicit is not None else os.environ.get("CPIC_F5_SOURCE")
    if raw is None or str(raw).strip() == "":
        return F5Source.DISABLED
    token = str(raw).strip().lower()
    aliases = {
        "off": F5Source.DISABLED,
        "disabled": F5Source.DISABLED,
        "mock": F5Source.MOCK,
        "live": F5Source.LIVE,
    }
    if token in aliases:
        return aliases[token]
    raise ValueError(f"CPIC_F5_SOURCE invalid: {raw!r} (off|mock|live)")


def validate_rec_view_row(row: Any) -> dict[str, Any]:
    """Accept official CPIC fields and mock aliases. lookupkey.F5 may be null, not absent with a wrong type."""
    if not isinstance(row, dict):
        log.critical("recommendation_view row is not an object: %s", type(row).__name__)
        raise ValueError("recommendation_view row must be an object")
    if "lookupkey" not in row:
        raise ValueError("lookupkey is required")
    lookup = row.get("lookupkey")
    if lookup is None:
        raise ValueError("lookupkey is required")
    if not isinstance(lookup, dict):
        raise ValueError("lookupkey must be an object")
    if "F5" not in lookup:
        raise ValueError("lookupkey.F5 is required (string or null)")
    f5 = lookup.get("F5")
    if f5 is not None and not isinstance(f5, str):
        raise ValueError("lookupkey.F5 must be a string or null")
    return row


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


class OffF5Provider:
    def rows(self) -> list[dict[str, Any]]:
        return []


class MockF5Provider:
    def rows(self) -> list[dict[str, Any]]:
        doc = json.loads(MOCK_PATH.read_text(encoding="utf-8"))
        raw = doc.get("rows") if isinstance(doc, dict) else doc
        if not isinstance(raw, list):
            raise ValueError("cpic_f5_mock.json must be a list or {rows: [...]}")
        return [copy.deepcopy(validate_rec_view_row(item)) for item in raw]


class LiveF5Provider:
    def __init__(self, fetch: Callable[[], list[Any]] | None = None) -> None:
        self._fetch = fetch or _http_fetch_live

    def rows(self) -> list[dict[str, Any]]:
        try:
            payload = self._fetch()
        except ValueError:
            raise
        except Exception:
            log.exception("live F5 recommendation_view fetch failed")
            return []
        if not isinstance(payload, list):
            log.critical("recommendation_view payload is not a list: %s", type(payload).__name__)
            raise ValueError("recommendation_view payload must be a list")
        return [validate_rec_view_row(item) for item in payload]


def _http_fetch_live() -> list[Any]:
    req = urllib.request.Request(
        LIVE_URL,
        headers={"User-Agent": "PrecisionClinicalEngine/0.1 (f5-rec-view)", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not isinstance(data, list):
        log.critical("recommendation_view HTTP body is not a list: %s", type(data).__name__)
        raise ValueError("recommendation_view payload must be a list")
    return data


def provider_for(
    source: str | F5Source, *, fetch: Callable[[], list[Any]] | None = None
) -> F5DataProvider:
    resolved = source if isinstance(source, F5Source) else resolve_source(source)
    if resolved is F5Source.MOCK:
        return MockF5Provider()
    if resolved is F5Source.LIVE:
        return LiveF5Provider(fetch=fetch)
    return OffF5Provider()


def _rec_text(row: dict[str, Any]) -> str:
    for key in ("drugrecommendation", "recommendation"):
        val = row.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _lookup_f5(row: dict[str, Any]) -> str | None:
    lookup = row.get("lookupkey") or {}
    if not isinstance(lookup, dict):
        return None
    raw = lookup.get("F5")
    if not isinstance(raw, str) or not raw.strip():
        return None
    return raw.strip()


def _pheno_code(lookup_val: str, row: dict[str, Any]) -> str | None:
    key = lookup_val.strip().lower()
    if key in PHENO_FROM_LOOKUP:
        return PHENO_FROM_LOOKUP[key]
    phenos = row.get("phenotypes")
    if isinstance(phenos, dict) and isinstance(phenos.get("F5"), str):
        mapped = PHENO_FROM_LOOKUP.get(phenos["F5"].strip().lower())
        if mapped:
            return mapped
    if isinstance(row.get("phenotype"), str):
        mapped = PHENO_FROM_LOOKUP.get(str(row["phenotype"]).strip().lower())
        if mapped:
            return mapped
    return None


def classify_recommendation(text: str) -> str | None:
    """Strategy category only. No milligrams."""
    low = (text or "").strip().lower()
    if not low:
        return None
    if low in {"no recommendation", "n/a"} or low.startswith("no recommendation"):
        return "NO_RECOMMENDATION"
    if "avoid" in low or "consider alternative" in low or "not recommended" in low:
        return "CONSIDER_ALTERNATIVE"
    if "continue" in low or "no genotype-based change" in low or "no action" in low:
        return "CONTINUE"
    if "dose" in low:
        return "CONSIDER_DOSE_CHANGE"
    return None


def _atc_for_row(row: dict[str, Any], mock_meta: dict[str, Any]) -> tuple[str, str] | None:
    atc = str(row.get("atc5") or mock_meta.get("atc5") or "").strip().upper()
    inn = str(row.get("drugname") or mock_meta.get("inn") or "").strip()
    if len(atc) == 7 and inn:
        return atc, inn
    return None


def transform_rows(
    rows: list[dict[str, Any]],
    *,
    mocked: bool,
    mock_meta: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, str]]]:
    meta = mock_meta or {}
    by_pheno: dict[str, str] = {}
    inn = str(meta.get("inn") or MOCK_INN)
    atc5 = str(meta.get("atc5") or MOCK_ATC5).upper()
    for row in rows:
        lookup_val = _lookup_f5(row)
        if not lookup_val:
            continue
        code = _pheno_code(lookup_val, row)
        category = classify_recommendation(_rec_text(row))
        if not code or not category:
            continue
        mapped = _atc_for_row(row, meta)
        if mapped:
            atc5, inn = mapped
        by_pheno[code] = category
    if not by_pheno:
        return [], [], {}
    pairings: list[dict[str, Any]] = [
        {
            "gene": "F5",
            "atc5": atc5,
            "inn": inn,
            "inn_hu": str(meta.get("inn_hu") or inn),
            "source_id": "CPIC-F5-MOCK" if mocked else "CPIC-F5-REC-LIVE",
            "mocked": mocked,
            "by_phenotype": by_pheno,
            "strategy_hu": {
                "CONSIDER_ALTERNATIVE": (
                    "MOCK F5 pipeline: stratégia-kategória a lokális fixture szövegéből. "
                    "Nem hivatalos CPIC recommendation_view. Nincs milligramm."
                    if mocked
                    else "CPIC F5 recommendation_view: más szer megfontolandó. Nincs milligramm."
                ),
                "CONTINUE": (
                    "MOCK F5 pipeline: nincs gén-alapú váltás a fixture szerint. Nem hivatalos CPIC sor."
                    if mocked
                    else "CPIC F5 recommendation_view: folytatás, nincs milligramm."
                ),
                "CONSIDER_DOSE_CHANGE": "F5: dózisváltoztatás megfontolandó. Nincs milligramm.",
                "NO_RECOMMENDATION": "F5: a rec_view ezen a lookupkulcson nem ad ajánlást.",
            },
        }
    ]
    dips: list[dict[str, Any]] = []
    src = "CPIC-F5-MOCK" if mocked else "CPIC-F5-REC-LIVE"
    for code, aliases in DIPLOTYPE_ALIASES.items():
        for alias in aliases:
            dips.append(
                {
                    "gene": "F5",
                    "diplotype": alias,
                    "genotype_phenotype": code,
                    "cpic_generesult": alias,
                    "activity_score": None,
                    "source_id": src,
                }
            )
    labels = {
        "HET": {"en": "Factor V Leiden heterozygote", "hu": "V. faktor Leiden heterozigóta"},
        "HOM": {"en": "Factor V Leiden homozygote", "hu": "V. faktor Leiden homozigóta"},
        "WT": {"en": "Factor V Leiden negative / wild type", "hu": "V. faktor Leiden negatív (vad típus)"},
    }
    return pairings, dips, labels


def load_mock_meta() -> dict[str, Any]:
    doc = json.loads(MOCK_PATH.read_text(encoding="utf-8"))
    return doc if isinstance(doc, dict) else {}


def apply_f5_source(
    table: Any,
    source: str | None = None,
    *,
    fetch: Callable[[], list[Any]] | None = None,
) -> str:
    """Mutate a KnowledgeTable. Never overwrites an existing (gene, ATC5) pairing."""
    resolved = resolve_source(source)
    table.f5_source = resolved.value
    if resolved is F5Source.DISABLED:
        return resolved.value
    rows = provider_for(resolved, fetch=fetch).rows()
    mocked = resolved is F5Source.MOCK
    meta = load_mock_meta() if mocked else {}
    pairings, dips, labels = transform_rows(rows, mocked=mocked, mock_meta=meta)
    for row in pairings:
        table.add_pairing(row, source="f5_rec")
    for row in dips:
        key = (row["gene"], row["diplotype"])
        if key not in table._dip:
            table._dip[key] = row
    for code, label in labels.items():
        table.phenotype_labels.setdefault(code, label)
    if mocked:
        van = list(table.inventory.get("van") or [])
        if not any(row.get("id") == "CPIC-F5-MOCK" for row in van):
            van.append(
                {
                    "id": "CPIC-F5-MOCK",
                    "hu": (
                        "MOCK: a CPIC recommendation_view F5-re 0 sor. A pipeline a "
                        "tests/fixtures/cpic_f5_mock.json fájlon fut. Ez nem hivatalos CPIC ajánlás."
                    ),
                }
            )
            table.inventory["van"] = van
    return resolved.value
