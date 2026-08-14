"""FR-210 VCF coverage. Matcher OFF. Missing defining position is not reference."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pce_report.flags import DIPLOTIPUS_FORRAS_HU, MATCHER_ON
from pce_report.panel import PREPARE_12

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "tests" / "fixtures" / "vcf-gold-v0" / "defining-positions.v0.json"


def _chrom(raw: str) -> str:
    token = raw.strip()
    if token.lower().startswith("chr"):
        token = token[3:]
    return token


def parse_vcf_sites(text: str) -> tuple[set[tuple[str, int]], set[tuple[str, int, int]]]:
    """Return exact POS hits and gVCF [POS, END] blocks (inclusive)."""
    sites: set[tuple[str, int]] = set()
    blocks: set[tuple[str, int, int]] = set()
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 8:
            continue
        chrom = _chrom(parts[0])
        try:
            pos = int(parts[1])
        except ValueError:
            continue
        sites.add((chrom, pos))
        info = parts[7]
        end = None
        for field in info.split(";"):
            if field.startswith("END="):
                try:
                    end = int(field.split("=", 1)[1])
                except ValueError:
                    end = None
        if end is not None and end >= pos:
            blocks.add((chrom, pos, end))
    return sites, blocks


def _covered(
    chrom: str,
    pos: int,
    sites: set[tuple[str, int]],
    blocks: set[tuple[str, int, int]],
) -> bool:
    if (chrom, pos) in sites:
        return True
    for c, start, end in blocks:
        if c == chrom and start <= pos <= end:
            return True
    return False


def _pos_for_build(row: dict[str, Any], reference: str) -> int | None:
    if reference == "GRCh37":
        raw = row.get("grch37_pos")
    else:
        raw = row.get("grch38_pos")
    if isinstance(raw, int):
        return raw
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def assess_coverage(
    text: str,
    *,
    reference: str,
    catalog_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Per PREPARE-12 gene: INDETERMINATE if a pinned defining site is missing.

    Never CALLED. Never NORMAL. PharmCAT --absent-to-ref is not invoked.
    """
    if MATCHER_ON:
        raise RuntimeError("F1 coverage must not run with MATCHER_ON")
    catalog = json.loads((catalog_path or DEFAULT_CATALOG).read_text(encoding="utf-8"))
    sites, blocks = parse_vcf_sites(text)
    genes = catalog.get("genes") or {}
    out: list[dict[str, Any]] = []
    for gene in PREPARE_12:
        meta = genes.get(gene) or {"catalog": "gap", "positions": []}
        positions = list(meta.get("positions") or [])
        if meta.get("catalog") == "not_snv":
            note = str(meta.get("note_hu") or "").strip()
            out.append(
                {
                    "gene": gene,
                    "callability": "NOT_TESTED",
                    "missing": [],
                    "naive_missing_to_ref_would_claim": None,
                    "note_hu": (
                        note
                        + (" " if note else "")
                        + f"{gene}: nem egyszerű SNV. Nem NORMAL. "
                        + DIPLOTIPUS_FORRAS_HU
                    ).strip(),
                    "pharmcat_absent_to_ref": False,
                    "catalog": "not_snv",
                }
            )
            continue
        if meta.get("catalog") != "pinned" or not positions:
            out.append(
                {
                    "gene": gene,
                    "callability": "NOT_TESTED",
                    "missing": [],
                    "naive_missing_to_ref_would_claim": None,
                    "note_hu": (
                        f"{gene}: nincs pin-elt definiáló-pozíció katalógus. Nem NORMAL. "
                        + DIPLOTIPUS_FORRAS_HU
                    ),
                    "pharmcat_absent_to_ref": False,
                }
            )
            continue
        missing: list[dict[str, Any]] = []
        naive = None
        why = []
        for row in positions:
            chrom = str(row.get("chrom") or "")
            pos = _pos_for_build(row, reference)
            if pos is None:
                missing.append({"rsid": row.get("rsid"), "reason": "no_coordinate_for_build"})
                continue
            if not _covered(chrom, pos, sites, blocks):
                missing.append(
                    {
                        "rsid": row.get("rsid"),
                        "allele_name": row.get("allele_name"),
                        "chrom": chrom,
                        "pos": pos,
                        "build": reference,
                    }
                )
                naive = row.get("naive_missing_to_ref_would_claim") or naive
                if row.get("why_opposite_hu"):
                    why.append(str(row["why_opposite_hu"]))
        if missing:
            out.append(
                {
                    "gene": gene,
                    "callability": "INDETERMINATE",
                    "missing": missing,
                    "naive_missing_to_ref_would_claim": naive,
                    "note_hu": (
                        f"{gene}: definiáló pozíció hiányzik a VCF-ből, nincs lefedő gVCF-blokk. "
                        "Ez nem referencia-allél és nem NORMAL. INDETERMINATE. "
                        + " ".join(why)
                        + " "
                        + DIPLOTIPUS_FORRAS_HU
                    ).strip(),
                    "pharmcat_absent_to_ref": False,
                }
            )
        else:
            out.append(
                {
                    "gene": gene,
                    "callability": "NOT_TESTED",
                    "missing": [],
                    "naive_missing_to_ref_would_claim": None,
                    "note_hu": (
                        f"{gene}: a pin-elt definiáló pozíció szerepel a VCF-ben. "
                        "Ettől még nincs diplotípus és nincs NORMAL állítás. "
                        + DIPLOTIPUS_FORRAS_HU
                    ),
                    "pharmcat_absent_to_ref": False,
                }
            )
    return out
