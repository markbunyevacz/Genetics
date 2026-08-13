"""FR-400-STATIC / FR-210 / FR-490 F1+ report. Matcher OFF. No HIS medication list."""
from __future__ import annotations

from typing import Any

from pce_report.flags import LIVE_CDS, MATCHER_ON
from pce_report.guidelines import GuidelineTable
from pce_report.panel import CONFIG_ID_PREFIX, PREPARE_12
from pce_report.statements import A11_DISCLAIMER, A1_INTENDED_PURPOSE, SOURCE as STATEMENT_SOURCE

FORBIDDEN_RENDERER_TOKENS = (
    "Ön",
    "ennél a betegnél",
    "a most felírt",
    "dose_mg",
    "functional_phenotype",
)

CALLABILITY_OK = {"CALLED", "PARTIAL", "INDETERMINATE", "NOT_TESTED"}


class RendererConfigError(ValueError):
    pass


def _scan_wrapper(text: str) -> None:
    for tok in FORBIDDEN_RENDERER_TOKENS:
        if tok in text:
            raise RendererConfigError(f"forbidden F1+ token {tok!r}")


def render_f1plus(
    *,
    outside_call: dict[str, Any],
    table: GuidelineTable,
    config_version: str = "v0",
) -> dict[str, Any]:
    """Build the signed-lab JSON report.

    Keyword-only. There is no medications parameter (FR-470).
    """
    if MATCHER_ON or LIVE_CDS:
        raise RendererConfigError("F1+ matcher and LIVE_CDS must be false")
    if not isinstance(outside_call, dict):
        raise RendererConfigError("outside_call must be an object")
    for banned in ("medications", "MedicationRequest", "dose_mg"):
        if banned in outside_call:
            raise RendererConfigError("F1+ renderer must not receive a medication list")

    gene = outside_call.get("gene")
    diplotype = outside_call.get("diplotype")
    callability = outside_call.get("callability")
    if not isinstance(gene, str) or not gene:
        raise RendererConfigError("outside_call.gene required")
    if callability not in CALLABILITY_OK:
        raise RendererConfigError(f"callability must be one of {sorted(CALLABILITY_OK)}")
    if callability in {"CALLED", "PARTIAL"} and not isinstance(diplotype, str):
        raise RendererConfigError("CALLED/PARTIAL requires diplotype")

    pairs = table.pairs_for_gene(gene)
    if not pairs:
        raise RendererConfigError(f"no CPIC pair_view rows for {gene}")
    recs = table.rows_for_gene(gene)
    if not recs:
        raise RendererConfigError(f"no CPIC recommendation_view rows for {gene}")

    positive = callability == "CALLED"
    case: dict[str, Any] = {
        "case_display_id": outside_call.get("case_display_id"),
        "gene": gene,
        "diplotype": diplotype if callability in {"CALLED", "PARTIAL"} else None,
        "callability": callability,
        "positive_drug_assertion": positive,
        "in_prepare_12": gene in PREPARE_12,
        "lab_phenotype_claim": None,
    }
    if not positive:
        case["fr210"] = (
            "INDETERMINATE/NOT_TESTED/PARTIAL: no NORMAL claim; gene-drug "
            "statements are not positive assertions for this case (FR-210)"
        )
    elif isinstance(outside_call.get("lab_phenotype"), str):
        case["lab_phenotype_claim"] = outside_call["lab_phenotype"]

    wrapper = A1_INTENDED_PURPOSE + "\n" + A11_DISCLAIMER
    _scan_wrapper(wrapper)
    _scan_wrapper(json_safe_case(case))

    report = {
        "product": "Precision Clinical Engine",
        "module": "F1+",
        "config_id": f"{CONFIG_ID_PREFIX}@{config_version}",
        "matcher_on": False,
        "live_cds": False,
        "medications_applied_to_recommendations": False,
        "a1_intended_purpose": A1_INTENDED_PURPOSE,
        "a11_disclaimer": A11_DISCLAIMER,
        "statement_source": STATEMENT_SOURCE,
        "case": case,
        "pairs": pairs,
        "pair_count": len(pairs),
        "guideline_rows": recs,
        "guideline_row_count": len(recs),
        "guideline_source": table.recs_source,
        "pair_source": table.pairs_source,
        "accessed": table.accessed,
        "unsourced_claims": 0,
        "edu_phenoconversion": None,
        "edu_note": (
            "FR-410-EDU omitted: CPIC guideline.notesonusage was empty on the "
            "fetched guideline records; no invented educational paragraph."
        ),
    }
    return report


def json_safe_case(case: dict[str, Any]) -> str:
    import json

    return json.dumps(case, ensure_ascii=False)
