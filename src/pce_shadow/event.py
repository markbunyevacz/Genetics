"""Turn a FHIR Bundle or GatewayEvent-like dict into engine input."""
from __future__ import annotations

import json
from typing import Any

from pce_gateway.genetics import payload_diplotypes
from pce_gateway.transform import iter_resources, transform_bundle


def _looks_like_bundle(payload: dict[str, Any]) -> bool:
    if payload.get("resourceType") == "Bundle":
        return True
    entries = payload.get("entry")
    return isinstance(entries, list) and any(
        isinstance(e, dict) and isinstance(e.get("resource"), dict) for e in entries
    )


def extract_observations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    extra = payload.get("observations")
    if isinstance(extra, list):
        for rec in extra:
            if isinstance(rec, dict):
                found.append(dict(rec))
    if not _looks_like_bundle(payload):
        return found
    for obs in iter_resources(payload, "Observation"):
        blob = json.dumps(obs, default=str).lower()
        if "egfr" not in blob and "glomerular filtration" not in blob:
            continue
        vq = obs.get("valueQuantity") if isinstance(obs.get("valueQuantity"), dict) else {}
        value = vq.get("value") if vq else obs.get("value")
        found.append(
            {
                "name": "eGFR",
                "value": value,
                "unit": (vq or {}).get("unit"),
                "loinc": _first_loinc(obs),
            }
        )
    return found


def _first_loinc(obs: dict[str, Any]) -> str | None:
    for coding in (obs.get("code") or {}).get("coding") or []:
        if isinstance(coding, dict) and str(coding.get("system") or "").endswith("loinc.org"):
            code = coding.get("code")
            if isinstance(code, str):
                return code
    return None


def event_from_payload(
    payload: dict[str, Any],
    *,
    max_atc_level: int = 4,
    time_grain: str = "QUARTER",
) -> dict[str, Any]:
    """Normalize ingest JSON to diplotypes + medications + observations."""
    nested = payload.get("GatewayEvent")
    blob = nested if isinstance(nested, dict) else payload
    if _looks_like_bundle(payload):
        base = transform_bundle(payload, max_atc_level=max_atc_level, time_grain=time_grain)
        meds = list(base.get("medications") or [])
        dips = payload_diplotypes(payload)
        granularity = "RAW" if dips else blob.get("diplotype_granularity") or "RAW"
        source = "FHIR"
        authored = base.get("authoredOn")
    else:
        meds = list(blob.get("medications") or [])
        dips = payload_diplotypes(payload)
        granularity = blob.get("diplotype_granularity") or ("CLASS" if blob.get("phenotype_class") else "RAW")
        source = "MANUAL"
        authored = blob.get("authoredOn")
    return {
        "id": blob.get("id"),
        "org_id": blob.get("org_id"),
        "mode": blob.get("mode") or "ANON",
        "diplotypes": dips,
        "medications": meds,
        "observations": extract_observations(payload),
        "diplotype_granularity": granularity,
        "phenotype_class": blob.get("phenotype_class"),
        "authoredOn": authored,
        "medication_source": source,
        "payload_hash": blob.get("payload_hash"),
    }
