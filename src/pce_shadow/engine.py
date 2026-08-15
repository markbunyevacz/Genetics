"""FR-400-LIVE / FR-410-LIVE. genotype_phenotype is immutable. No dose_mg. No invented PM."""
from __future__ import annotations

import copy
import uuid
from typing import Any

from pce_gateway.transform import DEFAULT_MAX_ATC_LEVEL
from pce_shadow.event import event_from_payload
from pce_shadow.table import KnowledgeTable, default_table

ORGAN_REASON = "organ"


def _activity_key(raw: Any) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text.lower() in {"n/a", "none", "null"}:
        return None
    return text


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
    *,
    max_atc_level: int = DEFAULT_MAX_ATC_LEVEL,
) -> dict[str, Any]:
    """Diplotype + current meds → live_findings. Never a Report FK."""
    knowledge = table or default_table()
    event = event_from_payload(payload, max_atc_level=max_atc_level)
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
        code = mapped["genotype_phenotype"] if mapped else None
        row: dict[str, Any] = {
            "gene": gene,
            "diplotype": star if granularity != "CLASS" else None,
            "genotype_phenotype": code,
            "genotype_phenotype_hu": knowledge.phenotype_hu(code),
            "cpic_generesult": mapped["cpic_generesult"] if mapped else None,
            "activity_score": mapped.get("activity_score") if mapped else None,
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
    # CPIC SSRI 2023: no NM+inhibitor → poor-metabolizer row. Do not invent it.
    # Record FDA strong class when ATC5 matched. Signal the missing mapping in Hungarian.

    def _finding(
        *,
        gene: str,
        code: str,
        inn: str | None,
        category: str,
        source_id: str | None,
        pairing: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        hu = None
        if pairing:
            hu = (pairing.get("strategy_hu") or {}).get(category)
        if not hu:
            hu = knowledge.strategy_labels_hu.get(category)
        rec: dict[str, Any] = {
            "gene": gene,
            "drug_atc": code,
            "inn": inn,
            "strategy_category": category,
            "strategy_category_hu": hu,
            "source_id": source_id,
        }
        if extra:
            rec.update(extra)
        return rec

    live_findings: list[dict[str, Any]] = []
    if clinical_context != "ABSENT":
        for gene_row in genotype:
            gene = gene_row.get("gene")
            if not isinstance(gene, str) or not gene:
                continue
            pheno = gene_row.get("genotype_phenotype")
            for code in codes:
                pairing = knowledge.pairing(gene, code)
                category = None
                if pairing:
                    as_map = pairing.get("by_activity_score")
                    as_key = _activity_key(gene_row.get("activity_score"))
                    if isinstance(as_map, dict) and as_key and as_key in as_map:
                        category = as_map.get(as_key)
                    elif pheno and pairing.get("by_phenotype"):
                        category = pairing["by_phenotype"].get(pheno)
                if pairing and category:
                    live_findings.append(
                        _finding(
                            gene=gene,
                            code=code,
                            inn=pairing.get("inn"),
                            category=category,
                            source_id=pairing.get("source_id"),
                            pairing=pairing,
                        )
                    )
                    continue
                if pairing and pairing.get("strategy"):
                    live_findings.append(
                        _finding(
                            gene=gene,
                            code=code,
                            inn=pairing.get("inn"),
                            category=pairing["strategy"],
                            source_id=pairing.get("source_id"),
                            pairing=pairing,
                        )
                    )
                    continue
                prefix_hit = None
                for atc5 in knowledge.pairing_atc5_codes(gene):
                    if atc5.startswith(code) and len(code) < 7:
                        prefix_hit = knowledge.pairing(gene, atc5)
                        break
                if prefix_hit:
                    live_findings.append(
                        _finding(
                            gene=gene,
                            code=code,
                            inn=None,
                            category="INSUFFICIENT_RESOLUTION",
                            source_id=prefix_hit.get("source_id"),
                            pairing=prefix_hit,
                            extra={
                                "reason": "atc4_cannot_identify_strong_inhibitor_inn",
                                "reason_hu": knowledge.strategy_labels_hu.get("INSUFFICIENT_RESOLUTION"),
                            },
                        )
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

    mapping_hu = {
        "not_established_by_cpic_2023": knowledge.adjustment_status_hu,
        "atc4_insufficient": knowledge.strategy_labels_hu.get("INSUFFICIENT_RESOLUTION"),
        "no_clinical_context": (
            "Nincs aktuális gyógyszerlista; a párosítás nem értékelhető, nem hallgatólagos normál metabolizáló."
        ),
        "no_strong_inhibitor_atc5": (
            "Nincs erős CYP2D6-gátló 7 karakteres hatóanyag-kóddal (paroxetin N06AB05 / fluoxetin N06AB03) a listán."
        ),
    }.get(mapping_status)

    inv = knowledge.inventory
    van = list(inv.get("van") or [])
    hianyzik = list(inv.get("hianyzik") or [])
    if mapping_status == "atc4_insufficient":
        hianyzik.append(
            {
                "id": "ATC5-HATÓANYAG",
                "hu": knowledge.strategy_labels_hu.get("INSUFFICIENT_RESOLUTION"),
            }
        )
    elif mapping_status == "no_clinical_context":
        hianyzik.append(
            {
                "id": "NINCS-GYÓGYSZERLISTA",
                "hu": "Nincs aktuális gyógyszerlista; a gén–gyógyszer párosítás nem értékelhető (clinical_context = ABSENT), nem hallgatólagos normál metabolizáló.",
            }
        )

    forras_allapot = {
        "van": van,
        "hianyzik": hianyzik,
        "beszerzes": inv.get("beszerzes") or {},
        "functional_phenotype_iras": {
            "irtunk_szegeny_metabolizalot": False,
            "hu": knowledge.adjustment_status_hu
            or (
                "Funkcionális szegény metabolizáló címke üres: a CPIC SSRI 2023-ban nincs NM→szegény sor, "
                "az FDA csak erős gátlót mond."
            ),
        },
    }

    inference: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "gateway_event_id": event.get("id"),
        "config_id": knowledge.config_id,
        "guideline_versions": {
            "cpic_ssri": "2023",
            "cpic_opioid": "2020",
            "cpic_cyp2c19_clopidogrel": "PA166251443",
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
            "inhibitor_inn_hu": inhibitor.get("inn_hu") if inhibitor else None,
            "inhibitor_atc5": inhibitor.get("atc5") if inhibitor else None,
            "inhibitor_class": inhibitor.get("fda_class") if inhibitor else None,
            "inhibitor_class_hu": inhibitor.get("fda_class_hu") if inhibitor else None,
            "match": inhibitor_match,
            "mapping_status": mapping_status,
            "mapping_status_hu": mapping_hu,
            "functional_phenotype_written": False,
        },
        "forras_allapot": forras_allapot,
        "diplotype_granularity": granularity,
        "phenotype_class": event.get("phenotype_class"),
        "payload_hash": event.get("payload_hash"),
        "max_atc_level": max_atc_level,
    }
    return inference
