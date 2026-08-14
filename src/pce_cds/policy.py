"""IIa-safe live-pair kill-switch (G §2.4 option (a)).

Default ON: the five high-harm pairs from A.4.1 get no live suggestion,
even when LIVE_CDS is true. OQ-06 may later set IIA_SAFE_BLOCK False.
INN list is sourced from A.4.1 / G §2.4 names. ATC5 codes are the WHO
5th-level substance codes for those same INNs (S032 structure).
"""
from __future__ import annotations

from typing import Any

# Compile-time. Do not flip in this repo until OQ-06 says the pairs may go live.
IIA_SAFE_BLOCK: bool = True

# A.4.1 / G §2.4 INNs (lowercase). Not a clinical-outcome mapping.
IIA_SAFE_INN: frozenset[str] = frozenset(
    {
        "fluorouracil",
        "5-fluorouracil",
        "5-fu",
        "capecitabine",
        "clopidogrel",
        "azathioprine",
        "mercaptopurine",
        "6-mercaptopurine",
        "codeine",
        "carbamazepine",
    }
)

# WHO ATC 5th level (7 characters) for the same substances.
IIA_SAFE_ATC5: frozenset[str] = frozenset(
    {
        "L01BC02",  # fluorouracil
        "L01BC06",  # capecitabine
        "B01AC04",  # clopidogrel
        "L04AX01",  # azathioprine
        "L01BB02",  # mercaptopurine
        "R05DA04",  # codeine
        "N03AF01",  # carbamazepine
    }
)

INFO_HU = (
    "Ehhez a párhoz élő párosítás nem elérhető (IIa-safe lista, G §2.4). "
    "Konzultáljon klinikai farmakológussal. Statikus F1+ guideline-szöveg a leleten."
)


def _inn_blob(med: dict[str, Any]) -> str:
    parts = [
        str(med.get("inn") or ""),
        str(med.get("inn_hu") or ""),
        str(med.get("display") or ""),
        str(med.get("name") or ""),
        str(med.get("code") or ""),
    ]
    return " ".join(parts).lower()


def is_iia_safe_med(med: dict[str, Any]) -> bool:
    code = str(med.get("code") or "").strip().upper()
    if code in IIA_SAFE_ATC5:
        return True
    if any(code.startswith(atc) for atc in IIA_SAFE_ATC5 if len(code) >= 7):
        return True
    blob = _inn_blob(med)
    return any(inn in blob for inn in IIA_SAFE_INN)


def blocked_live_pairing(med: dict[str, Any], *, block: bool = IIA_SAFE_BLOCK) -> bool:
    return bool(block) and is_iia_safe_med(med)
