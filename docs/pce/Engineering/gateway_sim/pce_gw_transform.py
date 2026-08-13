#!/usr/bin/env python3
"""SYN gateway slice: PCE-GW-461-01 (ATC truncate) and PCE-GW-461-02 (time grain).

Stdlib only. Gold V0 fixtures. Not a live HIS gateway. Does not strip PII
(FR-460), dose (FR-461-03), k-cells, or rare diplotypes.

WHO ATC code lengths (S032): ATC3=4 chars (N06A), ATC4=5 (N06AB), ATC5=7 (N06AB10).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
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
        res = entry.get("resource") if isinstance(entry, dict) else None
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


def transform_bundle(
    bundle: dict[str, Any],
    *,
    max_atc_level: int = 4,
    time_grain: str = "QUARTER",
) -> dict[str, Any]:
    """Gateway projection: ATC + time only. Patient / dose / genetics are omitted."""
    medications: list[dict[str, Any]] = []
    times: list[str] = []
    for medreq in iter_resources(bundle, "MedicationRequest"):
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
    return {
        "mode": "ANON",
        "scope": ["PCE-GW-461-01", "PCE-GW-461-02"],
        "atc_level": max_atc_level,
        "time_grain": time_grain.upper(),
        "medications": medications,
        "authoredOn": authored_out,
    }


def ingest_guard(
    bundle: dict[str, Any],
    *,
    max_atc_level: int = 4,
) -> None:
    """PCE ANON ingest: ATC5 or day-level authoredOn → E-SHADOW-001."""
    max_len = WHO_ATC_LEN[max_atc_level]
    for medreq in iter_resources(bundle, "MedicationRequest"):
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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", "-i", required=True, help="FHIR Bundle JSON (Gold V0 HIS-in or ingest)")
    p.add_argument("--mode", choices=("gateway", "ingest"), default="gateway")
    p.add_argument("--atc-level", type=int, default=4, choices=(1, 2, 3, 4, 5))
    p.add_argument("--time-grain", default="QUARTER", choices=("QUARTER", "YEAR", "quarter", "year"))
    args = p.parse_args(argv)
    bundle = load_json(args.input)
    try:
        if args.mode == "ingest":
            ingest_guard(bundle, max_atc_level=args.atc_level)
            out = {
                "ingest": "accepted",
                "http": 202,
                "hitl": False,
                "note": "ATC/time guard only; FR-460 PII checks are not in this slice",
            }
        else:
            out = transform_bundle(
                bundle,
                max_atc_level=args.atc_level,
                time_grain=args.time_grain.upper(),
            )
    except ShadowReject as e:
        json.dump(e.as_dict(), sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 2
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
