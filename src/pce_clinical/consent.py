"""FR-100 / FR-110 consent gate. Not a config flag. Admin cannot skip."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from pce_clinical.errors import ClinicalError
from pce_clinical.store import ClinicalStore
from pce_report.panel import PREPARE_12

PURPOSE_SCOPES = frozenset({"pgx_report", "counselling", "research"})


@dataclass(frozen=True)
class GateSnapshot:
    counselling_id: str
    counsellor_id: str
    counselling_at: str
    consent_id: str
    consent_granted_at: str
    license_id: str
    allowed_genes: frozenset[str]
    omit_from_patient: frozenset[str]


def _scopes(raw: str) -> list[str]:
    data = json.loads(raw)
    if not isinstance(data, list):
        return []
    return [str(x) for x in data]


def allowed_genes(scopes: list[str]) -> frozenset[str]:
    genes = {s for s in scopes if s in PREPARE_12 or s in {"HLA-A", "NUDT15"}}
    purposes = {s for s in scopes if s in PURPOSE_SCOPES}
    if genes:
        return frozenset(genes)
    if "pgx_report" in purposes:
        return frozenset(PREPARE_12)
    return frozenset()


def assert_render_allowed(
    store: ClinicalStore,
    case_id: str,
    requested_genes: list[str],
    *,
    skip_consent: bool = False,
    role: str = "lab_signer",
) -> GateSnapshot:
    """FR-100. skip_consent and admin role are ignored (TC-CONSENT-006)."""
    _ = skip_consent
    _ = role

    case = store.one("SELECT * FROM case_record WHERE id = ?", (case_id,))
    if case is None:
        raise ClinicalError("E-GONE-010", extra={"reason": "unknown case"})
    subject = store.one("SELECT * FROM subject WHERE id = ?", (case["subject_id"],))
    if subject is not None and int(subject["erased"]) == 1:
        raise ClinicalError("E-GONE-010")

    org = store.one("SELECT * FROM organization WHERE id = ?", (case["org_id"],))
    if org is None or not org["license_id"]:
        raise ClinicalError("E-CONSENT-005")

    counselling = store.one(
        "SELECT * FROM counselling WHERE case_id = ? ORDER BY occurred_at LIMIT 1",
        (case_id,),
    )
    if counselling is None:
        raise ClinicalError("E-CONSENT-001")

    sample = store.one("SELECT * FROM sample WHERE case_id = ?", (case_id,))
    if sample is None:
        raise ClinicalError("E-CONSENT-002")
    if counselling["occurred_at"] >= sample["collected_at"]:
        raise ClinicalError("E-CONSENT-002")

    consent = store.one(
        "SELECT * FROM consent WHERE case_id = ? AND withdrawn_at IS NULL "
        "ORDER BY granted_at DESC LIMIT 1",
        (case_id,),
    )
    if consent is None:
        raise ClinicalError("E-CONSENT-003")

    scopes = _scopes(consent["scopes_json"])
    allowed = allowed_genes(scopes)
    omit = frozenset(_scopes(consent["omit_from_patient_json"]))
    extras = [g for g in requested_genes if g not in allowed]
    if extras:
        raise ClinicalError("E-CONSENT-004", extra={"genes": extras})

    return GateSnapshot(
        counselling_id=counselling["id"],
        counsellor_id=counselling["counsellor_id"],
        counselling_at=counselling["occurred_at"],
        consent_id=consent["id"],
        consent_granted_at=consent["granted_at"],
        license_id=str(org["license_id"]),
        allowed_genes=allowed,
        omit_from_patient=omit,
    )


def gate_to_meta(snap: GateSnapshot) -> dict[str, Any]:
    return {
        "counselling": {
            "id": snap.counselling_id,
            "at": snap.counselling_at,
            "counsellor_id": snap.counsellor_id,
        },
        "consent_granted_at": snap.consent_granted_at,
        "performing_org_license_id": snap.license_id,
    }
