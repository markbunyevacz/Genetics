"""IIa-safe live-pair kill-switch (G §2.4 option (a)).

Default ON: the A.4.1 / G §2.4 high-harm *mechanisms* get no live suggestion,
even when LIVE_CDS is true. OQ-06 may later set IIA_SAFE_BLOCK False.

The block is mechanism → WHO ATC 5th-level codes + INN variants (EN + HU),
not a one-off English INN list. Same-guideline companions already in the
repo pins are included (tramadol with codeine; tegafur with fluorouracil /
capecitabine; thioguanine with the thiopurines; oxcarbazepine / phenytoin
with HLA-B*15:02 carbamazepine).

WHO 4th-level L01BC is "pyrimidine analogues" (gemcitabine sits there) and
L01BB is "purine analogues" (fludarabine sits there). Those prefixes are
therefore *not* used as catch-alls. Fluoropyrimidine / thiopurine coverage
is the CPIC pair_drugnames set plus the matching WHO 5th-level codes.

N03AF (carboxamide derivatives) *is* the WHO 4th-level for the
carbamazepine / oxcarbazepine guideline family (S049 HLA-B rec_view).
"""
from __future__ import annotations

import re
from typing import Any, NamedTuple

# Compile-time. Do not flip in this repo until OQ-06 says the pairs may go live.
IIA_SAFE_BLOCK: bool = True


class IiaSafeFamily(NamedTuple):
    mechanism_id: str
    source: str
    atc5: frozenset[str]
    atc_prefixes: frozenset[str]
    inn_variants: frozenset[str]


# Pin citations are repo paths / source ids, not new clinical claims.
IIA_SAFE_FAMILIES: tuple[IiaSafeFamily, ...] = (
    IiaSafeFamily(
        mechanism_id="DPYD-fluoropyrimidine",
        source=(
            "A.4.1; G §2.4; S049 DPYD rec_view pair_drugnames "
            "capecitabine/fluorouracil/tegafur; WHO L01BC02/L01BC06/L01BC03"
        ),
        atc5=frozenset({"L01BC02", "L01BC06", "L01BC03"}),
        atc_prefixes=frozenset(),
        inn_variants=frozenset(
            {
                "fluorouracil",
                "5-fluorouracil",
                "5-fu",
                "5fu",
                "capecitabine",
                "kapecitabin",
                "tegafur",
            }
        ),
    ),
    IiaSafeFamily(
        mechanism_id="CYP2C19-clopidogrel",
        source="A.4.1; G §2.4; S065 WHO B01AC04",
        atc5=frozenset({"B01AC04"}),
        atc_prefixes=frozenset(),
        inn_variants=frozenset({"clopidogrel", "klopidogrel"}),
    ),
    IiaSafeFamily(
        mechanism_id="TPMT-NUDT15-thiopurine",
        source=(
            "A.4.1; G §2.4; S049 TPMT rec_view pair_drugnames "
            "azathioprine/mercaptopurine/thioguanine; WHO L04AX01/L01BB02/L01BB03"
        ),
        atc5=frozenset({"L04AX01", "L01BB02", "L01BB03"}),
        atc_prefixes=frozenset(),
        inn_variants=frozenset(
            {
                "azathioprine",
                "azatioprin",
                "mercaptopurine",
                "6-mercaptopurine",
                "merkaptopurin",
                "thioguanine",
                "tioguanine",
                "tioguanin",
            }
        ),
    ),
    IiaSafeFamily(
        mechanism_id="CYP2D6-opioid",
        source=(
            "A.4.1 CYP2D6–kodein; S048 CPIC opioid 2020 PDF; "
            "S049 CYP2D6 pair_view drugname tramadol; WHO R05DA04/N02AX02"
        ),
        atc5=frozenset({"R05DA04", "N02AX02"}),
        atc_prefixes=frozenset(),
        inn_variants=frozenset({"codeine", "kodein", "tramadol"}),
    ),
    IiaSafeFamily(
        mechanism_id="HLA-B-1502-aromatic-anticonvulsant",
        source=(
            "A.4.1 HLA-B*15:02–karbamazepin; S049 HLA-B rec_view "
            "carbamazepine/oxcarbazepine/phenytoin/fosphenytoin; "
            "WHO N03AF + N03AB02/N03AB05"
        ),
        atc5=frozenset({"N03AF01", "N03AF02", "N03AB02", "N03AB05"}),
        atc_prefixes=frozenset({"N03AF"}),
        inn_variants=frozenset(
            {
                "carbamazepine",
                "karbamazepin",
                "oxcarbazepine",
                "oxkarbazepin",
                "phenytoin",
                "fenitoin",
                "fosphenytoin",
                "foszfenitoin",
            }
        ),
    ),
)

IIA_SAFE_ATC5: frozenset[str] = frozenset().union(*(f.atc5 for f in IIA_SAFE_FAMILIES))
IIA_SAFE_ATC_PREFIXES: frozenset[str] = frozenset().union(
    *(f.atc_prefixes for f in IIA_SAFE_FAMILIES)
)
IIA_SAFE_INN: frozenset[str] = frozenset().union(*(f.inn_variants for f in IIA_SAFE_FAMILIES))

_SHORT_INN = re.compile(r"^[a-z0-9-]{1,4}$")

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


def _atc_hits(code: str, family: IiaSafeFamily) -> bool:
    if not code:
        return False
    if code in family.atc5:
        return True
    if any(code.startswith(p) and len(code) >= len(p) for p in family.atc_prefixes):
        return True
    if len(code) > 7 and any(code.startswith(a) for a in family.atc5):
        return True
    return False


def _blob_has_variant(blob: str, variant: str) -> bool:
    v = variant.strip().lower()
    if not v:
        return False
    if _SHORT_INN.fullmatch(v.replace(" ", "")):
        return re.search(rf"(?<![a-z0-9]){re.escape(v)}(?![a-z0-9])", blob) is not None
    return v in blob


def matching_families(med: dict[str, Any]) -> tuple[str, ...]:
    code = str(med.get("code") or "").strip().upper()
    blob = _inn_blob(med)
    hits: list[str] = []
    for family in IIA_SAFE_FAMILIES:
        if _atc_hits(code, family):
            hits.append(family.mechanism_id)
            continue
        if any(_blob_has_variant(blob, inn) for inn in family.inn_variants):
            hits.append(family.mechanism_id)
    return tuple(hits)


def is_iia_safe_med(med: dict[str, Any]) -> bool:
    return bool(matching_families(med))


def blocked_live_pairing(med: dict[str, Any], *, block: bool = IIA_SAFE_BLOCK) -> bool:
    return bool(block) and is_iia_safe_med(med)
