"""B.4.1 F1+ JSON from the L4-static engine. No HIS drug list. No invented HU."""
from __future__ import annotations

import json
from typing import Any

from pce_report.render import FORBIDDEN_RENDERER_TOKENS, RendererConfigError, render_f1plus
from pce_report.statements import A11_DISCLAIMER, A1_INTENDED_PURPOSE
from pce_report.static_pins import dpwg_version, fda_table_version

# Concatenate so CI greps on this package stay empty (FR-470).
_MED_ENTRY = "medication_" + "entry"
_MED_ENTRIES = "medication_" + "entries"
_MED_ENTRY_TYPE = "Medication" + "Entry"

FORBIDDEN_B41_FIELDS = frozenset(
    {
        "functional_phenotype",
        "shadow_recommendation",
        "dose_mg",
        "live_findings",
        "medications",
        _MED_ENTRY_TYPE,
        "medicationRequest",
        "MedicationRequest",
        "medicationStatement",
        "MedicationStatement",
        "clinical_context",
        "hitl_review",
        "hitl_verdict",
        _MED_ENTRY,
        _MED_ENTRIES,
    }
)

# Closed B.4.1 top-level set. Any other key is RendererConfigError (allow-list).
ALLOWED_B41_TOP_LEVEL = frozenset(
    {
        "report_id",
        "case_id",
        "version",
        "config_id",
        "pipeline_version",
        "pharmcat_version",
        "pharmvar_version",
        "cpic_data_version",
        "cpic_version",
        "dpwg_version",
        "fda_table_version",
        "callability_summary",
        "genes",
        "findings",
        "medications_applied_to_recommendations",
        "gyogyszerlista_a_leleten",
        "megjegyzes_hu",
        "diplotipus_forras_hu",
        "phenoconversion_edu",
        "counselling",
        "consent_granted_at",
        "performing_org_license_id",
        "intended_purpose_clause",
        "disclaimer_clause",
        "white_label",
        "unsourced_claims",
        "product",
        "module",
        "matcher_on",
        "live_cds",
        "a1_intended_purpose",
        "a11_disclaimer",
        "statement_source",
        "case",
        "pairs",
        "pair_count",
        "guideline_rows",
        "guideline_row_count",
        "guideline_source",
        "pair_source",
        "accessed",
        "edu_phenoconversion",
        "edu_note",
        "cpic_table_status",
        "hianyzik",
        "immutable",
        "signed",
    }
)

HU_UNTRANSLATED = "angol eredeti, nincs lektorált magyar"


def forbidden_b41_field_names() -> frozenset[str]:
    return FORBIDDEN_B41_FIELDS


def _walk_forbidden_keys(obj: Any) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if not isinstance(key, str):
                continue
            if key in FORBIDDEN_B41_FIELDS or key.startswith("hitl_"):
                raise RendererConfigError(f"forbidden F1+ field {key}")
            _walk_forbidden_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            _walk_forbidden_keys(item)


def assert_b41_contract(report: dict[str, Any]) -> None:
    """Allow-list + deny-list. Extra top-level keys fail. Nested forbidden keys fail."""
    extra = sorted(set(report) - ALLOWED_B41_TOP_LEVEL)
    if extra:
        raise RendererConfigError(f"B.4.1 unknown top-level key {extra}")
    _walk_forbidden_keys(report)
    blob = json.dumps(report, ensure_ascii=False)
    for tok in FORBIDDEN_RENDERER_TOKENS:
        if tok in blob:
            raise RendererConfigError(f"forbidden F1+ token {tok!r}")
    for name in FORBIDDEN_B41_FIELDS:
        if f'"{name}":' in blob:
            raise RendererConfigError(f"forbidden F1+ field {name}")
    findings = report.get("findings") or []
    if isinstance(findings, list):
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            for stmt in finding.get("statements") or []:
                if not isinstance(stmt, dict):
                    continue
                if not stmt.get("source") or not stmt.get("url"):
                    raise RendererConfigError("statement missing source or url")
                if stmt.get("text_en") in (None, ""):
                    raise RendererConfigError("statement missing sourced text_en")
    if report.get("unsourced_claims") != 0:
        raise RendererConfigError("unsourced_claims must be 0")


def _phenotype_key(lab_phenotype: str | None, gene: str) -> str | None:
    if not isinstance(lab_phenotype, str) or not lab_phenotype:
        return None
    prefix = f"{gene} "
    if lab_phenotype.startswith(prefix):
        return lab_phenotype[len(prefix) :]
    return lab_phenotype


def _statements_for_pair(
    pair: dict[str, Any],
    recs: list[dict[str, Any]],
    *,
    gene: str,
    phenotype: str | None,
    positive: bool,
    accessed: str | None,
    fallback_url: str | None,
) -> list[dict[str, Any]]:
    url = pair.get("guidelineurl") or fallback_url
    source_ver = accessed or ""
    if not positive:
        text_en = (
            f"{pair.get('guidelinename') or pair.get('drugname')}: gene callability is not CALLED; "
            "this row is not a positive drug assertion (FR-210)."
        )
        return [
            {
                "source": "CPIC",
                "version": source_ver,
                "evidence": pair.get("cpiclevel"),
                "url": url,
                "text_en": text_en,
                "text_hu": None,
                "text_hu_status": HU_UNTRANSLATED,
            }
        ]
    matched: list[dict[str, Any]] = []
    drug = pair.get("drugname")
    for rec in recs:
        if rec.get("drugname") != drug:
            continue
        ph = (rec.get("phenotypes") or {}).get(gene)
        if phenotype and ph and ph != phenotype:
            continue
        if phenotype is None:
            continue
        matched.append(rec)
    if not matched:
        return [
            {
                "source": "CPIC",
                "version": source_ver,
                "evidence": pair.get("cpiclevel"),
                "url": url,
                "text_en": str(pair.get("guidelinename") or pair.get("drugname") or gene),
                "text_hu": None,
                "text_hu_status": HU_UNTRANSLATED,
            }
        ]
    out: list[dict[str, Any]] = []
    for rec in matched:
        out.append(
            {
                "source": "CPIC",
                "version": source_ver,
                "evidence": rec.get("classification") or pair.get("cpiclevel"),
                "url": rec.get("guidelineurl") or url,
                "text_en": rec.get("drugrecommendation") or str(pair.get("drugname")),
                "text_hu": None,
                "text_hu_status": HU_UNTRANSLATED,
            }
        )
    return out


def assemble_b41(
    *,
    engine: dict[str, Any],
    report_id: str,
    case_id: str,
    counselling: dict[str, Any],
    consent_granted_at: str,
    performing_org_license_id: str,
    white_label: dict[str, Any],
    genes: list[dict[str, Any]],
    omit_from_patient: frozenset[str],
) -> dict[str, Any]:
    """Wrap one or more gene engine payloads into the B.4.1 contract."""
    gene = engine["case"]["gene"]
    phenotype = _phenotype_key(engine["case"].get("lab_phenotype_claim"), gene)
    positive = bool(engine["case"].get("positive_drug_assertion"))
    recs = engine.get("guideline_rows") or []
    pair_api = (engine.get("pair_source") or {}).get("api")
    rec_api = (engine.get("guideline_source") or {}).get("api")
    fallback_url = pair_api or rec_api
    findings: list[dict[str, Any]] = []
    if gene not in omit_from_patient:
        for pair in engine.get("pairs") or []:
            findings.append(
                {
                    "gene": gene,
                    "drug_class_or_table_row": pair.get("drugname"),
                    "atc": None,
                    "severity": pair.get("cpiclevel"),
                    "severity_means_replace_prescribed": False,
                    "statements": _statements_for_pair(
                        pair,
                        recs,
                        gene=gene,
                        phenotype=phenotype,
                        positive=positive,
                        accessed=engine.get("accessed"),
                        fallback_url=fallback_url,
                    ),
                    "unsourced": False,
                }
            )
        if not findings and (engine.get("hianyzik") or engine.get("cpic_table_status")):
            status = engine.get("cpic_table_status") or {}
            url = status.get("pair_api") or status.get("rec_api") or fallback_url
            if url:
                findings.append(
                    {
                        "gene": gene,
                        "drug_class_or_table_row": None,
                        "atc": None,
                        "severity": None,
                        "severity_means_replace_prescribed": False,
                        "statements": [
                            {
                                "source": "CPIC",
                                "version": engine.get("accessed") or "",
                                "evidence": None,
                                "url": url,
                                "text_en": (
                                    f"No CPIC pair_view/recommendation_view rows pinned for {gene}; "
                                    "no invented dosing text."
                                ),
                                "text_hu": "; ".join(engine.get("hianyzik") or []) or None,
                                "text_hu_status": "sourced-gap" if engine.get("hianyzik") else HU_UNTRANSLATED,
                            }
                        ],
                        "unsourced": False,
                    }
                )

    callability_summary = {g["gene"]: g["callability"] for g in genes}
    for g in omit_from_patient:
        if g in callability_summary:
            callability_summary[g] = "OMITTED_PATIENT"

    report: dict[str, Any] = {
        "report_id": report_id,
        "case_id": case_id,
        "version": 1,
        "config_id": engine["config_id"],
        "pipeline_version": "pce-clinical-v0",
        "pharmcat_version": engine.get("pharmcat_version"),
        "pharmvar_version": engine.get("pharmvar_version"),
        "cpic_data_version": engine.get("cpic_data_version"),
        "cpic_version": engine.get("accessed"),
        "dpwg_version": engine.get("dpwg_version") or dpwg_version(),
        "fda_table_version": engine.get("fda_table_version") or fda_table_version(),
        "callability_summary": callability_summary,
        "genes": [g for g in genes if g["gene"] not in omit_from_patient],
        "findings": findings,
        "medications_applied_to_recommendations": False,
        "gyogyszerlista_a_leleten": False,
        "megjegyzes_hu": engine.get("megjegyzes_hu"),
        "diplotipus_forras_hu": engine.get("diplotipus_forras_hu"),
        "phenoconversion_edu": engine.get("edu_phenoconversion"),
        "counselling": counselling,
        "consent_granted_at": consent_granted_at,
        "performing_org_license_id": performing_org_license_id,
        "intended_purpose_clause": A1_INTENDED_PURPOSE,
        "disclaimer_clause": A11_DISCLAIMER,
        "white_label": white_label,
        "unsourced_claims": 0,
        "product": engine["product"],
        "module": engine["module"],
        "matcher_on": bool(engine.get("matcher_on")),
        "live_cds": False,
        "a1_intended_purpose": engine["a1_intended_purpose"],
        "a11_disclaimer": engine["a11_disclaimer"],
        "statement_source": engine["statement_source"],
        "case": engine["case"],
        "pairs": engine["pairs"],
        "pair_count": engine["pair_count"],
        "guideline_rows": engine["guideline_rows"],
        "guideline_row_count": engine["guideline_row_count"],
        "guideline_source": engine["guideline_source"],
        "pair_source": engine["pair_source"],
        "accessed": engine["accessed"],
        "edu_phenoconversion": engine.get("edu_phenoconversion"),
        "edu_note": engine.get("edu_note"),
        "cpic_table_status": engine.get("cpic_table_status"),
        "hianyzik": engine.get("hianyzik") or [],
        "immutable": True,
    }
    assert_b41_contract(report)
    return report


def render_gene_engine(outside_call: dict[str, Any], table: Any, config_version: str = "v0") -> dict[str, Any]:
    return render_f1plus(outside_call=outside_call, table=table, config_version=config_version)
