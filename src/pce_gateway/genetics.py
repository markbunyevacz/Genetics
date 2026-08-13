from __future__ import annotations

from typing import Any

from pce_gateway.transform import iter_resources


def extract_diplotypes(bundle: dict[str, Any]) -> list[dict[str, str]]:
    """Read gene + diplotype from FHIR R4 Observation components (LOINC 48018-6 / 84413-4)."""
    found: list[dict[str, str]] = []
    for obs in iter_resources(bundle, "Observation"):
        gene = None
        diplotype = None
        for comp in obs.get("component") or []:
            if not isinstance(comp, dict):
                continue
            coding = ((comp.get("code") or {}).get("coding") or [{}])[0]
            code = coding.get("code") if isinstance(coding, dict) else None
            if code == "48018-6":
                vcc = comp.get("valueCodeableConcept") or {}
                gene = vcc.get("text") if isinstance(vcc, dict) else None
            elif code == "84413-4":
                val = comp.get("valueString")
                if isinstance(val, str):
                    diplotype = val
        if isinstance(gene, str) and isinstance(diplotype, str):
            found.append({"gene": gene, "diplotype": diplotype, "callability": "CALLED"})
    return found


def payload_diplotypes(payload: dict[str, Any]) -> list[dict[str, str]]:
    """FHIR Bundle Observations, or already-exported GatewayEvent.diplotypes."""
    found = extract_diplotypes(payload)
    if found:
        return found
    nested = payload.get("GatewayEvent")
    blob = nested if isinstance(nested, dict) else payload
    extra = blob.get("diplotypes") or []
    out: list[dict[str, str]] = []
    if isinstance(extra, list):
        for rec in extra:
            if not isinstance(rec, dict):
                continue
            gene, dip = rec.get("gene"), rec.get("diplotype")
            if isinstance(gene, str) and isinstance(dip, str):
                out.append({"gene": gene, "diplotype": dip, "callability": "CALLED"})
    return out
