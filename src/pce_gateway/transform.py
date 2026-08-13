"""FR-460 PII strip and PCE-GW-461-01..03 (ATC, time, dose).

Stdlib only. WHO ATC lengths (S032): ATC3=4 (N06A), ATC4=5 (N06AB), ATC5=7 (N06AB10).

The GatewayEvent export has no Patient resource. Gender and birth year stay
on a local_counter dict and are not POSTed to PCE. CLI: python -m pce_gateway.
"""
from __future__ import annotations

import copy
import json
import re
from typing import Any, Iterator

WHO_ATC_LEN = {1: 1, 2: 3, 3: 4, 4: 5, 5: 7}
WHO_LEN_TO_LEVEL = {v: k for k, v in WHO_ATC_LEN.items()}
ATC_CODE_RE = re.compile(r"^[A-Z]\d{2}[A-Z]{0,2}\d{0,2}$")
QUARTER_RE = re.compile(r"^(\d{4})-Q([1-4])$")
YEAR_RE = re.compile(r"^(\d{4})$")
DATE_PREFIX_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")
ATC_SYSTEMS = {
    "http://www.whocc.no/atc",
    "https://www.whocc.no/atc",
    "http://whocc.no/atc",
    "https://whocc.no/atc",
    "http://whocc.no",
    "https://whocc.no",
}
DIRECT_PII_KEYS = ("name", "identifier", "telecom", "address")
DOSE_KEYS = frozenset({"doseQuantity", "rateQuantity", "dose_mg", "doseRange", "rateRange"})


class ShadowSuppress(Exception):
    """Gateway drop: HIS fail-open, no HITL row, local counter only (E-SHADOW-003)."""

    def __init__(self, reason: str, code: str = "E-SHADOW-003") -> None:
        super().__init__(reason)
        self.code = code
        self.reason = reason
        self.http = 202
        self.hitl = False
        self.counter_only = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "error": self.code,
            "http": self.http,
            "hitl": self.hitl,
            "counter_only": self.counter_only,
            "reason": self.reason,
        }


class ShadowReject(Exception):
    """PCE ingest defense (E-SHADOW-001)."""

    def __init__(self, reason: str, code: str = "E-SHADOW-001") -> None:
        super().__init__(reason)
        self.code = code
        self.reason = reason
        self.http = 400
        self.hitl = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "error": self.code,
            "http": self.http,
            "hitl": self.hitl,
            "reason": self.reason,
        }


def is_atc_system(system: str | None) -> bool:
    if not system:
        return False
    return system.rstrip("/").lower() in ATC_SYSTEMS


def normalize_atc_code(code: str) -> str:
    c = code.strip().upper().replace(" ", "")
    if not ATC_CODE_RE.fullmatch(c):
        raise ValueError(f"not a WHO ATC code: {code!r}")
    if len(c) not in WHO_LEN_TO_LEVEL:
        raise ValueError(f"ATC length {len(c)} is not a WHO level: {c!r}")
    return c


def atc_level_of(code: str) -> int:
    return WHO_LEN_TO_LEVEL[len(normalize_atc_code(code))]


def truncate_atc(code: str, max_level: int = 4) -> str:
    """FR-461-01: cut to at most max_level. Already-coarser codes stay as-is."""
    if max_level not in WHO_ATC_LEN:
        raise ValueError(f"max_level must be 1..5, got {max_level}")
    c = normalize_atc_code(code)
    target = WHO_ATC_LEN[max_level]
    if len(c) <= target:
        return c
    return c[:target]


def calendar_quarter(year: int, month: int) -> str:
    if month < 1 or month > 12:
        raise ValueError(f"month out of range: {month}")
    q = (month - 1) // 3 + 1
    return f"{year:04d}-Q{q}"


def generalize_time(authored_on: str, time_grain: str = "QUARTER") -> str:
    """FR-461-02. Wall-clock date prefix, not UTC conversion.

    QUARTER → YYYY-Qn. YEAR → YYYY. Does not invent a quarter from a year-only value.
    """
    grain = time_grain.upper()
    if grain not in {"QUARTER", "YEAR"}:
        raise ValueError(f"time_grain must be QUARTER or YEAR, got {time_grain!r}")
    raw = authored_on.strip()
    m_q = QUARTER_RE.fullmatch(raw)
    if m_q:
        return raw[:4] if grain == "YEAR" else raw
    m_y = YEAR_RE.fullmatch(raw)
    if m_y:
        return raw
    m_d = DATE_PREFIX_RE.match(raw)
    if not m_d:
        raise ValueError(f"authoredOn is not a date, datetime, YYYY, or YYYY-Qn: {authored_on!r}")
    year = int(m_d.group(1))
    month = int(m_d.group(2))
    if grain == "YEAR":
        return f"{year:04d}"
    return calendar_quarter(year, month)


def iter_resources(bundle: dict[str, Any], resource_type: str | None = None) -> Iterator[dict[str, Any]]:
    for entry in bundle.get("entry") or []:
        if not isinstance(entry, dict):
            continue
        res = entry.get("resource")
        if not isinstance(res, dict):
            continue
        if resource_type is None or res.get("resourceType") == resource_type:
            yield res


def _medication_codings(medreq: dict[str, Any]) -> list[dict[str, Any]]:
    concept = medreq.get("medicationCodeableConcept")
    if not isinstance(concept, dict):
        concept = medreq.get("medication")
    if not isinstance(concept, dict):
        return []
    coding = concept.get("coding") or []
    return [c for c in coding if isinstance(c, dict)]


def _year_only_birth(birth: str) -> str | None:
    raw = birth.strip()
    if YEAR_RE.fullmatch(raw):
        return raw
    m = DATE_PREFIX_RE.match(raw)
    if m:
        return m.group(1)
    return None


def _contains_keys(obj: Any, keys: frozenset[str]) -> bool:
    if isinstance(obj, dict):
        if keys & obj.keys():
            return True
        return any(_contains_keys(v, keys) for v in obj.values())
    if isinstance(obj, list):
        return any(_contains_keys(v, keys) for v in obj)
    return False


def strip_pii_fr460(fhir_bundle: dict[str, Any]) -> dict[str, Any]:
    """FR-460: drop direct identifiers on Patient. Does not mutate the input.

    birthDate → year for the local counter. Patient.id is dropped so it cannot
    become a manufacturer join-key. The GatewayEvent export still omits Patient.
    """
    out = copy.deepcopy(fhir_bundle)
    for res in iter_resources(out, "Patient"):
        for key in DIRECT_PII_KEYS:
            res.pop(key, None)
        res.pop("id", None)
        bd = res.get("birthDate")
        if isinstance(bd, str):
            year = _year_only_birth(bd)
            if year is None:
                res.pop("birthDate", None)
            else:
                res["birthDate"] = year
    return out


def suppress_dose_fr461_03(fhir_bundle: dict[str, Any]) -> dict[str, Any]:
    """FR-461-03: destroy doseQuantity / dose_mg (R4 doseAndRate and DSTU2)."""
    out = copy.deepcopy(fhir_bundle)
    for medreq in iter_resources(out, "MedicationRequest"):
        medreq.pop("dose_mg", None)
        instructions = medreq.get("dosageInstruction")
        if not isinstance(instructions, list):
            continue
        for ins in instructions:
            if not isinstance(ins, dict):
                continue
            ins.pop("doseQuantity", None)
            ins.pop("rateQuantity", None)
            dar = ins.get("doseAndRate")
            if isinstance(dar, list):
                kept: list[Any] = []
                for item in dar:
                    if not isinstance(item, dict):
                        continue
                    for k in DOSE_KEYS:
                        item.pop(k, None)
                    if item:
                        kept.append(item)
                if kept:
                    ins["doseAndRate"] = kept
                else:
                    ins.pop("doseAndRate", None)
    return out


def local_counter_demographics(stripped_bundle: dict[str, Any]) -> dict[str, Any] | None:
    """Gender + birth year only. Not part of the PCE payload."""
    patients = list(iter_resources(stripped_bundle, "Patient"))
    if not patients:
        return None
    p = patients[0]
    demo: dict[str, Any] = {}
    if "gender" in p:
        demo["gender"] = p["gender"]
    if "birthDate" in p:
        demo["birth_year"] = p["birthDate"]
    return demo or None


def transform_bundle(
    bundle: dict[str, Any],
    *,
    max_atc_level: int = 4,
    time_grain: str = "QUARTER",
    include_local: bool = False,
) -> dict[str, Any]:
    """ANON GatewayEvent: ATC + time. No Patient, no dose, no genetics."""
    stripped = strip_pii_fr460(bundle)
    work = suppress_dose_fr461_03(stripped)
    medications: list[dict[str, Any]] = []
    times: list[str] = []
    for medreq in iter_resources(work, "MedicationRequest"):
        authored = medreq.get("authoredOn")
        grain_out = None
        if isinstance(authored, str) and authored.strip():
            grain_out = generalize_time(authored, time_grain)
            times.append(grain_out)
        for coding in _medication_codings(medreq):
            if not is_atc_system(coding.get("system")):
                continue
            code = coding.get("code")
            if not isinstance(code, str):
                continue
            cut = truncate_atc(code, max_atc_level)
            rec: dict[str, Any] = {
                "system": "http://www.whocc.no/atc",
                "code": cut,
            }
            if cut != normalize_atc_code(code):
                rec["display"] = None
            elif coding.get("display"):
                rec["display"] = coding["display"]
            if grain_out is not None:
                rec["authoredOn"] = grain_out
            medications.append(rec)
    unique_times = list(dict.fromkeys(times))
    authored_out: str | list[str] | None
    if not unique_times:
        authored_out = None
    elif len(unique_times) == 1:
        authored_out = unique_times[0]
    else:
        authored_out = unique_times
    event: dict[str, Any] = {
        "mode": "ANON",
        "scope": ["PCE-GW-460", "PCE-GW-461-01", "PCE-GW-461-02", "PCE-GW-461-03"],
        "atc_level": max_atc_level,
        "time_grain": time_grain.upper(),
        "medications": medications,
        "authoredOn": authored_out,
    }
    if include_local:
        event["local_counter"] = local_counter_demographics(stripped)
        event["local_counter_note"] = "institutional gateway only; not POSTed to PCE"
    return event


def ingest_guard(
    bundle: dict[str, Any],
    *,
    max_atc_level: int = 4,
) -> None:
    """PCE ANON ingest: PII, dose, ATC5, or day-level authoredOn → E-SHADOW-001."""
    max_len = WHO_ATC_LEN[max_atc_level]
    for patient in iter_resources(bundle, "Patient"):
        for key in DIRECT_PII_KEYS:
            if key in patient:
                raise ShadowReject(f"Patient.{key} forbidden on ANON ingest")
    for medreq in iter_resources(bundle, "MedicationRequest"):
        if _contains_keys(medreq, DOSE_KEYS):
            raise ShadowReject("doseQuantity forbidden on ANON ingest")
        authored = medreq.get("authoredOn")
        if isinstance(authored, str) and authored.strip():
            raw = authored.strip()
            if not (QUARTER_RE.fullmatch(raw) or YEAR_RE.fullmatch(raw)):
                raise ShadowReject(
                    "authoredOn finer than calendar quarter forbidden on ANON ingest"
                )
        for coding in _medication_codings(medreq):
            if not is_atc_system(coding.get("system")):
                continue
            code = coding.get("code")
            if not isinstance(code, str):
                continue
            n = normalize_atc_code(code)
            if len(n) > max_len:
                raise ShadowReject(
                    f"ATC{atc_level_of(n)} ({len(n)}-character {n}) forbidden on ANON ingest"
                )


def load_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data
