"""CDS Hooks Card builder. No dose_mg. No invented poor-metabolizer label."""
from __future__ import annotations

import uuid
from typing import Any

from pce_cds.policy import INFO_HU, blocked_live_pairing
from pce_shadow.engine import infer

TIMEOUT_S = 2.0

LOCK_SUMMARY_HU = (
    "A PGx-CDSS ki van kapcsolva (LIVE_CDS=false). A felírás nem blokkolt."
)
NO_PGX_HU = "Nincs elérhető PGx-eredmény ehhez a felíráshoz."
TIMEOUT_HU = "A PGx-CDSS időtúllépés miatt nem válaszolt. A felírás nem blokkolt."


def _new_id() -> str:
    return str(uuid.uuid4())


def lock_discovery() -> dict[str, Any]:
    return {
        "services": [
            {
                "id": "pgx-order-sign",
                "hook": "order-sign",
                "title": "PCE PGx order-sign",
                "description": LOCK_SUMMARY_HU,
                "enabled": False,
            },
            {
                "id": "pgx-order-select",
                "hook": "order-select",
                "title": "PCE PGx order-select",
                "description": LOCK_SUMMARY_HU,
                "enabled": False,
            },
        ]
    }


def live_discovery() -> dict[str, Any]:
    body = lock_discovery()
    for svc in body["services"]:
        svc["enabled"] = True
        svc["description"] = "Farmakogenetikai CDS Card a felírás pillanatában."
    return body


def _info_card(summary: str, *, detail: str | None = None, source_url: str | None = None) -> dict[str, Any]:
    card: dict[str, Any] = {
        "uuid": _new_id(),
        "summary": summary,
        "indicator": "info",
        "source": {"label": "Precision Clinical Engine"},
        "suggestions": [],
    }
    if detail:
        card["detail"] = detail
    if source_url:
        card["links"] = [{"label": "Forrás", "url": source_url, "type": "absolute"}]
    return card


def _finding_card(finding: dict[str, Any]) -> dict[str, Any]:
    category = str(finding.get("strategy_category") or "")
    inn = finding.get("inn") or finding.get("drug_atc")
    gene = finding.get("gene")
    hu = finding.get("strategy_category_hu") or category
    source_id = finding.get("source_id")
    summary = f"{gene} / {inn}: {hu}"
    card: dict[str, Any] = {
        "uuid": _new_id(),
        "summary": summary[:140],
        "detail": hu,
        "source": {"label": "Precision Clinical Engine", "url": None},
        "suggestions": [],
        "links": [],
    }
    if source_id:
        card["links"] = [{"label": str(source_id), "url": "https://cpicpgx.org/", "type": "absolute"}]
    if category in {"CONSIDER_ALTERNATIVE", "CONSIDER_DOSE_CHANGE"}:
        card["indicator"] = "warning"
        card["suggestions"] = [
            {
                "label": hu,
                "uuid": _new_id(),
                "isRecommended": False,
                "actions": [],
            }
        ]
    else:
        card["indicator"] = "info"
    # Never a milligram action.
    for sug in card["suggestions"]:
        assert "dose_mg" not in sug
    return card


def _meds_from_hook(payload: dict[str, Any]) -> list[dict[str, Any]]:
    prefetch = payload.get("prefetch") if isinstance(payload.get("prefetch"), dict) else {}
    meds = list(prefetch.get("medications") or [])
    ctx = payload.get("context") if isinstance(payload.get("context"), dict) else {}
    draft = ctx.get("draftOrders")
    entries: list[Any] = []
    if isinstance(draft, dict):
        entries = list(draft.get("entry") or [])
    elif isinstance(draft, list):
        entries = draft
    for entry in entries:
        res = entry.get("resource") if isinstance(entry, dict) else entry
        if not isinstance(res, dict):
            continue
        if res.get("resourceType") not in {"MedicationRequest", "Medication"}:
            continue
        concept = res.get("medicationCodeableConcept") or {}
        coding = concept.get("coding") or []
        display = concept.get("text") or ""
        code = None
        for c in coding:
            if isinstance(c, dict) and c.get("code"):
                code = str(c["code"]).upper()
                display = display or str(c.get("display") or "")
                break
        meds.append({"code": code, "display": display, "inn": display})
    out: list[dict[str, Any]] = []
    for med in meds:
        if isinstance(med, dict):
            out.append(med)
        elif isinstance(med, str):
            out.append({"code": med})
    return out


def _dips_from_hook(payload: dict[str, Any]) -> list[dict[str, Any]]:
    prefetch = payload.get("prefetch") if isinstance(payload.get("prefetch"), dict) else {}
    dips = prefetch.get("diplotypes") or []
    return [d for d in dips if isinstance(d, dict)]


def build_cards(
    payload: dict[str, Any],
    *,
    live_cds: bool,
    iia_safe_block: bool = True,
    budget_s: float = TIMEOUT_S,
    infer_fn: Any = infer,
    monotonic: Any = None,
) -> dict[str, Any]:
    """Return a CDS Hooks card set. live_cds False → fail-open empty cards."""
    import time

    clock = monotonic or time.monotonic
    if not live_cds:
        return {"cards": [], "live_cds": False, "locked": True}

    t0 = clock()
    meds = _meds_from_hook(payload)
    dips = _dips_from_hook(payload)
    obs = []
    prefetch = payload.get("prefetch") if isinstance(payload.get("prefetch"), dict) else {}
    if isinstance(prefetch.get("observations"), list):
        obs = list(prefetch["observations"])

    if not dips:
        return {"cards": [_info_card(NO_PGX_HU)], "live_cds": True, "pgx": False}

    blocked = [m for m in meds if blocked_live_pairing(m, block=iia_safe_block)]
    live_meds = [m for m in meds if not blocked_live_pairing(m, block=iia_safe_block)]

    cards: list[dict[str, Any]] = []
    for med in blocked:
        label = med.get("inn") or med.get("display") or med.get("code") or "pár"
        cards.append(_info_card(f"{label}: élő párosítás nem elérhető.", detail=INFO_HU))

    if live_meds:
        infer_payload = {
            "diplotypes": dips,
            "medications": live_meds,
            "observations": obs,
        }
        result = infer_fn(infer_payload)
        if clock() - t0 > budget_s:
            return {"cards": [], "live_cds": True, "fail_open": True, "reason": TIMEOUT_HU}
        if result.get("functional_phenotype"):
            raise AssertionError("functional_phenotype must stay empty on CDS cards")
        findings = list(result.get("live_findings") or [])
        if not findings and not blocked:
            cards.append(_info_card(NO_PGX_HU))
        for finding in findings:
            cards.append(_finding_card(finding))

    if clock() - t0 > budget_s:
        return {"cards": [], "live_cds": True, "fail_open": True, "reason": TIMEOUT_HU}

    if not cards:
        cards.append(_info_card(NO_PGX_HU))
    return {"cards": cards, "live_cds": True}
