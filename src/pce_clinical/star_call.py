"""VCF star-allele path. Default off. matcher_on=True runs PharmCAT NamedAlleleMatcher."""
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
from pce_clinical.pharmcat import coverage_from_pharmcat, run_matcher_and_phenotyper
from pce_report.flags import MATCHER_ON
from pce_report.panel import PREPARE_12


def call_star_alleles(
    text: str,
    *,
    reference: str,
    catalog_path: Path | None = None,
    matcher_on: bool | None = None,
) -> list[dict[str, Any]]:
    """When matcher_on, run PharmCAT NamedAlleleMatcher + Phenotyper.

    Repo MATCHER_ON stays false. Missing site is never *1. Unphased alternatives
    are not picked. HLA-B stays NOT_TESTED on VCF.
    """
    enabled = MATCHER_ON if matcher_on is None else bool(matcher_on)
    if enabled:
        bundle = run_matcher_and_phenotyper(text)
        return coverage_from_pharmcat(bundle)
    catalog = json.loads((catalog_path or DEFAULT_CATALOG).read_text(encoding="utf-8"))
    sites, blocks = parse_vcf_sites(text)
    genes = catalog.get("genes") or {}
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
        out.append(
            {
                **base,
                "callability": "NOT_TESTED",
                "missing": [],
                "naive_missing_to_ref_would_claim": None,
                "note_hu": (
                    f"{gene}: a definiáló pozíció a VCF-ben megvan, de a PharmCAT NamedAlleleMatcher "
                    "ki van kapcsolva (MATCHER_ON=false). Nincs diplotípus a VCF-ből."
                ),
            }
        )
    return out
