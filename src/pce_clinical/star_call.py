"""VCF defining-SNV star-allele call. Default off. Missing site is never reference."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pce_clinical.coverage import (
    DEFAULT_CATALOG,
    _covered,
    _pos_for_build,
    parse_vcf_sites,
)
from pce_report.flags import MATCHER_ON
from pce_report.panel import PREPARE_12

ROOT = Path(__file__).resolve().parents[2]


def _chrom(raw: str) -> str:
    token = raw.strip()
    if token.lower().startswith("chr"):
        token = token[3:]
    return token


def _star_token(allele_name: str) -> str:
    name = allele_name.strip()
    if "*" in name:
        return "*" + name.split("*", 1)[1].split()[0]
    if "Leiden" in name:
        return "Leiden"
    if "-1639" in name:
        return "-1639A"
    return name


def _ref_token(allele_name: str) -> str:
    if "Leiden" in allele_name:
        return "WT"
    if "-1639" in allele_name:
        return "-1639G"
    return "*1"


def _parse_gt(sample: str) -> tuple[int, int] | None:
    token = sample.split(":")[0].replace("|", "/")
    if token in {".", "./.", ".|."}:
        return None
    parts = token.split("/")
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def parse_vcf_genotypes(text: str) -> dict[tuple[str, int], dict[str, Any]]:
    """Map (chrom, pos) → {ref, alts, alleles} for the first sample."""
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 10:
            continue
        chrom = _chrom(parts[0])
        try:
            pos = int(parts[1])
        except ValueError:
            continue
        ref = parts[3]
        alts = [a for a in parts[4].split(",") if a and a != "."]
        gt = _parse_gt(parts[9])
        if gt is None:
            continue
        alleles = []
        for idx in gt:
            if idx == 0:
                alleles.append(ref)
            elif 1 <= idx <= len(alts):
                alleles.append(alts[idx - 1])
            else:
                alleles.append(None)
        out[(chrom, pos)] = {"ref": ref, "alts": alts, "alleles": alleles, "gt": gt}
    return out


def _star_copies(gt_row: dict[str, Any], *, defining_alt: str, star_is_alt: bool) -> int | None:
    alleles = gt_row.get("alleles") or []
    if any(a is None for a in alleles) or len(alleles) != 2:
        return None
    if star_is_alt:
        return sum(1 for a in alleles if a == defining_alt)
    return sum(1 for a in alleles if a != defining_alt)


def _diplotype_from_counts(counts: dict[str, int], allele_names: dict[str, str]) -> str | None:
    stars = sorted((tok for tok, n in counts.items() if n), key=lambda t: allele_names.get(t, t))
    total = sum(counts.values())
    if total > 2:
        return None
    if not stars:
        refs = {_ref_token(allele_names[t]) for t in allele_names}
        ref = next(iter(refs)) if len(refs) == 1 else "*1"
        return f"{ref}/{ref}"
    if len(stars) == 1:
        tok = stars[0]
        n = counts[tok]
        ref = _ref_token(allele_names[tok])
        if n == 2:
            return f"{tok}/{tok}"
        if n == 1:
            left, right = sorted([ref, tok])
            if tok.startswith("*") and ref == "*1":
                return f"*1/{tok}"
            return f"{left}/{right}"
        return None
    if len(stars) == 2 and all(counts[t] == 1 for t in stars):
        a, b = stars
        return f"{a}/{b}"
    return None


def call_star_alleles(
    text: str,
    *,
    reference: str,
    catalog_path: Path | None = None,
    matcher_on: bool | None = None,
) -> list[dict[str, Any]]:
    """Call star alleles at pinned defining SNVs when matcher_on.

    HLA-B and UGT1A1*28 stay NOT_TESTED: they are not this SNV panel.
    Missing defining site → INDETERMINATE, never *1.
    """
    enabled = MATCHER_ON if matcher_on is None else bool(matcher_on)
    catalog = json.loads((catalog_path or DEFAULT_CATALOG).read_text(encoding="utf-8"))
    sites, blocks = parse_vcf_sites(text)
    genotypes = parse_vcf_genotypes(text) if enabled else {}
    genes = catalog.get("genes") or {}
    build_key = "grch37" if reference == "GRCh37" else "grch38"
    out: list[dict[str, Any]] = []
    for gene in PREPARE_12:
        meta = genes.get(gene) or {"catalog": "gap", "positions": []}
        positions = list(meta.get("positions") or [])
        base = {
            "gene": gene,
            "pharmcat_absent_to_ref": False,
            "matcher_on": enabled,
            "diplotype": None,
        }
        if meta.get("catalog") == "not_snv":
            note = str(meta.get("note_hu") or "").strip()
            out.append(
                {
                    **base,
                    "callability": "NOT_TESTED",
                    "missing": [],
                    "naive_missing_to_ref_would_claim": None,
                    "note_hu": (
                        note
                        + (" " if note else "")
                        + f"{gene}: ez a VCF pontmutációs panel ebből a laboreredményt nem számolja. "
                        "A labor HLA-B / UGT1A1*28 hívását outside-callban (laboreredmény-befogadás) kell beküldeni."
                    ).strip(),
                }
            )
            continue
        if meta.get("catalog") != "pinned" or not positions:
            out.append(
                {
                    **base,
                    "callability": "NOT_TESTED",
                    "missing": [],
                    "naive_missing_to_ref_would_claim": None,
                    "note_hu": f"{gene}: nincs pin-elt definiáló-pozíció. Nem NORMAL.",
                }
            )
            continue
        missing: list[dict[str, Any]] = []
        why: list[str] = []
        naive = None
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
                    **base,
                    "callability": "INDETERMINATE",
                    "missing": missing,
                    "naive_missing_to_ref_would_claim": naive,
                    "note_hu": (
                        f"{gene}: definiáló pozíció hiányzik a VCF-ből. "
                        "Ez nem referencia-allél és nem *1. INDETERMINATE. "
                        + " ".join(why)
                    ).strip(),
                }
            )
            continue
        if not enabled:
            out.append(
                {
                    **base,
                    "callability": "NOT_TESTED",
                    "missing": [],
                    "naive_missing_to_ref_would_claim": None,
                    "note_hu": (
                        f"{gene}: a definiáló pozíció a VCF-ben megvan, de a csillag-allél hívó ki van kapcsolva "
                        "(MATCHER_ON=false). Nincs diplotípus a VCF-ből."
                    ),
                }
            )
            continue
        counts: dict[str, int] = {}
        names: dict[str, str] = {}
        indeterminate = False
        for row in positions:
            chrom = str(row.get("chrom") or "")
            pos = _pos_for_build(row, reference)
            gt_row = genotypes.get((chrom, pos or -1))
            if not gt_row or pos is None:
                indeterminate = True
                break
            defining_alt = str(row.get(f"defining_alt_{build_key}") or row.get("defining_alt") or "")
            star_is_alt = bool(row.get(f"star_is_alt_{build_key}", row.get("star_is_alt", True)))
            if not defining_alt:
                indeterminate = True
                break
            copies = _star_copies(gt_row, defining_alt=defining_alt, star_is_alt=star_is_alt)
            if copies is None:
                indeterminate = True
                break
            tok = _star_token(str(row.get("allele_name") or ""))
            counts[tok] = counts.get(tok, 0) + copies
            names[tok] = str(row.get("allele_name") or tok)
        dip = None if indeterminate else _diplotype_from_counts(counts, names)
        if not dip:
            out.append(
                {
                    **base,
                    "callability": "INDETERMINATE",
                    "missing": [],
                    "naive_missing_to_ref_would_claim": None,
                    "note_hu": (
                        f"{gene}: a VCF-ben van pozíció, de a genotípus mezőből nem hívható "
                        "egyértelmű csillag-allél. Nem *1."
                    ),
                }
            )
            continue
        out.append(
            {
                **base,
                "callability": "CALLED",
                "diplotype": dip,
                "missing": [],
                "naive_missing_to_ref_would_claim": None,
                "note_hu": (
                    f"{gene}: csillag-allél a pin-elt definiáló pontmutációkból: {dip}. "
                    "Ez nem a teljes PharmCAT NamedAlleleMatcher: nincs kópiaszám, hibrid allél, "
                    "HLA-B laboratóriumi tipizálás, és UGT1A1*28 TATA-box (timin-adenin) ismétléshossz."
                ),
            }
        )
    return out
