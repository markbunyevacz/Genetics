"""FHIR R4 Bundle using Genomics Reporting IG STU3 resources (B.4.3). No STU4 operations."""
from __future__ import annotations

from typing import Any

from pce_report.statements import A11_DISCLAIMER


def to_stu3_bundle(report: dict[str, Any]) -> dict[str, Any]:
    report_id = report["report_id"]
    observations: list[dict[str, Any]] = []
    for gene_row in report.get("genes") or []:
        gene = gene_row["gene"]
        obs_id = f"obs-{gene.lower()}"
        components: list[dict[str, Any]] = [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "48018-6",
                            "display": "Gene studied [ID]",
                        }
                    ]
                },
                "valueCodeableConcept": {"text": gene},
            }
        ]
        dip = gene_row.get("diplotype")
        if isinstance(dip, str) and gene_row.get("callability") in {"CALLED", "PARTIAL"}:
            components.append(
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "84413-4",
                                "display": "Genotype display name",
                            }
                        ]
                    },
                    "valueString": dip,
                }
            )
        observations.append(
            {
                "resourceType": "Observation",
                "id": obs_id,
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "84413-4",
                            "display": "Genotype display name",
                        }
                    ]
                },
                "component": components,
            }
        )
        gp = gene_row.get("genotype_phenotype")
        if isinstance(gp, str) and gene_row.get("callability") == "CALLED":
            observations.append(
                {
                    "resourceType": "Observation",
                    "id": f"pheno-{gene.lower()}",
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "81247-9",
                                "display": "Master HL7 genetic variant reporting panel",
                            }
                        ]
                    },
                    "valueString": gp,
                    "note": [{"text": "genotype_phenotype only; no medication-list-derived phenotype"}],
                }
            )

    diagnostic = {
        "resourceType": "DiagnosticReport",
        "id": report_id,
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "81247-9",
                    "display": "Master HL7 genetic variant reporting panel",
                }
            ]
        },
        "result": [{"reference": f"Observation/{o['id']}"} for o in observations],
        "conclusion": report.get("intended_purpose_clause"),
    }
    docref = {
        "resourceType": "DocumentReference",
        "id": f"doc-{report_id}",
        "status": "current",
        "description": A11_DISCLAIMER,
        "content": [{"attachment": {"contentType": "application/pdf", "title": "F1+ report"}}],
    }
    entries = [{"resource": diagnostic}]
    entries.extend({"resource": o} for o in observations)
    entries.append({"resource": docref})
    blob = {
        "resourceType": "Bundle",
        "type": "collection",
        "id": f"bundle-{report_id}",
        "entry": entries,
    }
    dumped = str(blob)
    for banned in ("functional_phenotype", "live_findings", "dose_mg", "$operations"):
        if banned in dumped:
            raise ValueError(f"FHIR bundle leaked {banned}")
    return blob
