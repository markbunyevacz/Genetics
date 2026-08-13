"""FR-400-LIVE / FR-410-LIVE. genotype_phenotype is immutable. No dose_mg. No invented PM."""
from __future__ import annotations

import copy
import uuid
from typing import Any

from pce_shadow.event import event_from_payload
from pce_shadow.table import KnowledgeTable, default_table

ORGAN_REASON = "organ"


def _atc_code(med: dict[str, Any]) -> str | None:
    code = med.get("code")
    if isinstance(code, str) and code.strip():
        return code.strip().upper()
    return None


def _is_egfr(obs: dict[str, Any]) -> bool:
    blob = " ".join(
        str(obs.get(k) or "") for k in ("name", "loinc", "code", "display", "text")
    ).lower()
    return "egfr" in blob


def _egfr_value(obs: dict[str, Any]) -> float | None:
    raw = obs.get("value")
    if isinstance(raw, bool) or raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    try:
        return float(str(raw).strip())
    except ValueError:
        return None


def infer(
    payload: dict[str, Any],
    table: KnowledgeTable | None = None,
) -> dict[str, Any]:
    """Diplotype + current meds → live_findings. Never a Report FK."""
    knowledge = table or default_table()
    event = event_from_payload(payload)
    meds = list(event.get("medications") or [])
    dips = list(event.get("diplotypes") or [])
    obs = list(event.get("observations") or [])
    granularity = event.get("diplotype_granularity") or "RAW"

    if not meds:
        clinical_context = "ABSENT"
    elif event.get("medication_source") == "FHIR":
        clinical_context = "FHIR"
    else:
        clinical_context = "MANUAL"

    genotype: list[dict[str, Any]] = []
    for dip in dips:
        gene, star = dip.get("gene"), dip.get("diplotype")
        if not isinstance(gene, str) or not isinstance(star, str):
            continue
        mapped = knowledge.genotype_phenotype(gene, star)
        row: dict[str, Any] = {
            "gene": gene,
            "diplotype": star if granularity != "CLASS" else None,
            "genotype_phenotype": mapped["genotype_phenotype"] if mapped else None,
            "cpic_generesult": mapped["cpic_generesult"] if mapped else None,
            "immutable": True,
            "source_id": mapped["source_id"] if mapped else None,
        }
        if granularity == "CLASS":
            row["phenotype_class"] = event.get("phenotype_class")
            row["diplotype"] = None
        genotype.append(row)

    if not dips and event.get("phenotype_class"):
        genotype.append(
            {
                "gene": None,
                "diplotype": None,
                "genotype_phenotype": None,
                "phenotype_class": event.get("phenotype_class"),
                "immutable": True,
                "source_id": None,
            }
        )

    codes = [c for c in (_atc_code(m) for m in meds) if c]
    inhibitor = None
    inhibitor_match = "none"
    for code in codes:
        hit = knowledge.strong_inhibitor(code)
        if hit:
            inhibitor = hit
            inhibitor_match = "atc5"
            break
        if len(code) < 7:
            for atc5 in knowledge.inhibitor_atc5_codes():
                if atc5.startswith(code):
                    inhibitor_match = "atc_prefix_only"
                    break

    mapping_status = knowledge.adjustment_status
    if clinical_context == "ABSENT":
        mapping_status = "no_clinical_context"
        inhibitor_match = "none"
    elif inhibitor is None and inhibitor_match == "atc_prefix_only":
        mapping_status = "atc4_insufficient"
    elif inhibitor is None:
        mapping_status = "no_strong_inhibitor_atc5"
    elif knowledge.nm_plus_strong is None:
        mapping_status = knowledge.adjustment_status

    functional: list[dict[str, Any]] = []
    # Official CPIC 2023: consensus NM+inhibitor → PM/IM mapping is not established.
    # Do not invent PM. Record inhibitor class when ATC5 matched.

    live_findings: list[dict[str, Any]] = []
    if clinical_context != "ABSENT":
        for gene_row in genotype:
            gene = gene_row.get("gene") or "CYP2D6"
            pheno = gene_row.get("genotype_phenotype")
            for code in codes:
                pairing = knowledge.pairing(code)
                if pairing and pheno and pairing.get("by_phenotype"):
                    category = pairing["by_phenotype"].get(pheno)
                    if category:
                        live_findings.append(
                            {
                                "gene": gene,
                                "drug_atc": code,
                                "inn": pairing.get("inn"),
                                "strategy_category": category,
                                "source_id": pairing.get("source_id"),
                            }
                        )
                        continue
                if pairing and pairing.get("strategy"):
                    live_findings.append(
                        {
                            "gene": gene,
                            "drug_atc": code,
                            "inn": pairing.get("inn"),
                            "strategy_category": pairing["strategy"],
                            "source_id": pairing.get("source_id"),
                        }
                    )
                    continue
                prefix_hit = None
                for atc5 in knowledge.pairing_atc5_codes():
                    if atc5.startswith(code) and len(code) < 7:
                        prefix_hit = knowledge.pairing(atc5)
                        break
                if prefix_hit:
                    live_findings.append(
                        {
                            "gene": gene,
                            "drug_atc": code,
                            "inn": None,
                            "strategy_category": "INSUFFICIENT_RESOLUTION",
                            "source_id": prefix_hit.get("source_id"),
                            "reason": "atc4_cannot_identify_strong_inhibitor_inn",
                        }
                    )

    organ_flags: list[dict[str, Any]] = []
    for rec in obs:
        if not _is_egfr(rec):
            continue
        value = _egfr_value(rec)
        if value is not None and value < knowledge.egfr_threshold:
            organ_flags.append(
                {
                    "reason": ORGAN_REASON,
                    "name": "eGFR",
                    "value": value,
                    "threshold": knowledge.egfr_threshold,
                }
            )

    for finding in live_findings:
        if "dose_mg" in finding:
            finding.pop("dose_mg", None)
        if organ_flags:
            finding["reason_organ"] = ORGAN_REASON

    inference: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "gateway_event_id": event.get("id"),
        "config_id": knowledge.config_id,
        "guideline_versions": {
            "cpic_ssri": "2023",
            "knowledge_id": knowledge.config_id,
        },
        "diplotypes": copy.deepcopy(dips),
        "medications": copy.deepcopy(meds),
        "genotype_phenotype": genotype,
        "functional_phenotype": functional,
        "live_findings": live_findings,
        "clinical_context": clinical_context,
        "organ_flags": organ_flags,
        "phenoconversion": {
            "applied": False,
            "inhibitor_inn": inhibitor.get("inn") if inhibitor else None,
            "inhibitor_atc5": inhibitor.get("atc5") if inhibitor else None,
            "inhibitor_class": inhibitor.get("fda_class") if inhibitor else None,
            "match": inhibitor_match,
            "mapping_status": mapping_status,
            "functional_phenotype_written": False,
        },
        "diplotype_granularity": granularity,
        "phenotype_class": event.get("phenotype_class"),
        "payload_hash": event.get("payload_hash"),
    }
    return inference
