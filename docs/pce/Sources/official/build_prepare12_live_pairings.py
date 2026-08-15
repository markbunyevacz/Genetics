#!/usr/bin/env python3
"""Map pinned CPIC recommendation_view rows to strategy categories. No milligrams.

Manufacturer (this repo) runs this. Companion-gene rows keep the other gene at
Normal Metabolizer / No Result / n/a so a one-gene lookup is a published row,
not a blended guess.

Usage: python3 docs/pce/Sources/official/build_prepare12_live_pairings.py
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PREPARE = ROOT / "tests" / "fixtures" / "f1plus-v0" / "prepare12"
OUT = ROOT / "tests" / "fixtures" / "shadow-v0" / "prepare12-rec-pairings.v0.json"
TODAY = "2026-08-15"

# WHO ATC 5th level, 7 characters. HTML pins: fetch_software_ready_pins.py
ATC = {
    ("CYP2B6", "sertraline"): ("N06AB06", "szertralin"),
    ("CYP2C19", "amitriptyline"): ("N06AA09", "amitriptilin"),
    ("CYP2C19", "citalopram"): ("N06AB04", "citalopram"),
    ("CYP2C19", "clomipramine"): ("N06AA04", "klomipramin"),
    ("CYP2C19", "dexlansoprazole"): ("A02BC06", "dexlansoprazol"),
    ("CYP2C19", "doxepin"): ("N06AA12", "doxepin"),
    ("CYP2C19", "escitalopram"): ("N06AB10", "eszcitaloprám"),
    ("CYP2C19", "imipramine"): ("N06AA02", "imipramin"),
    ("CYP2C19", "lansoprazole"): ("A02BC03", "lanzoprazol"),
    ("CYP2C19", "omeprazole"): ("A02BC01", "omeprazol"),
    ("CYP2C19", "pantoprazole"): ("A02BC02", "pantoprazol"),
    ("CYP2C19", "sertraline"): ("N06AB06", "szertralin"),
    ("CYP2C19", "trimipramine"): ("N06AA06", "trimipramin"),
    ("CYP2C19", "voriconazole"): ("J02AC03", "vorikonazol"),
    ("CYP2C9", "flurbiprofen"): ("M01AE09", "flurbiprofen"),
    ("CYP2C9", "fluvastatin"): ("C10AA04", "fluvasztatin"),
    ("CYP2C9", "fosphenytoin"): ("N03AB05", "foszfenitoin"),
    ("CYP2C9", "ibuprofen"): ("M01AE01", "ibuprofen"),
    ("CYP2C9", "lornoxicam"): ("M01AC05", "lornoxicam"),
    ("CYP2C9", "meloxicam"): ("M01AC06", "meloxicam"),
    ("CYP2C9", "phenytoin"): ("N03AB02", "fenitoin"),
    ("CYP2C9", "piroxicam"): ("M01AC01", "piroxicam"),
    ("CYP2C9", "tenoxicam"): ("M01AC02", "tenoxicam"),
    ("CYP2D6", "amitriptyline"): ("N06AA09", "amitriptilin"),
    ("CYP2D6", "atomoxetine"): ("N06BA09", "atomoxetin"),
    ("CYP2D6", "clomipramine"): ("N06AA04", "klomipramin"),
    ("CYP2D6", "codeine"): ("R05DA04", "kodein"),
    ("CYP2D6", "desipramine"): ("N06AA01", "dezipramin"),
    ("CYP2D6", "doxepin"): ("N06AA12", "doxepin"),
    ("CYP2D6", "fluvoxamine"): ("N06AB08", "fluvoxamin"),
    ("CYP2D6", "hydrocodone"): ("R05DA03", "hidrokodon"),
    ("CYP2D6", "imipramine"): ("N06AA02", "imipramin"),
    ("CYP2D6", "metoprolol"): ("C07AB02", "metoprolol"),
    ("CYP2D6", "nortriptyline"): ("N06AA10", "nortriptilin"),
    ("CYP2D6", "tamoxifen"): ("L02BA01", "tamoxifen"),
    ("CYP2D6", "tramadol"): ("N02AX02", "tramadol"),
    ("CYP2D6", "trimipramine"): ("N06AA06", "trimipramin"),
    ("CYP2D6", "venlafaxine"): ("N06AX16", "venlafaxin"),
    ("CYP2D6", "vortioxetine"): ("N06AX26", "vortioxetin"),
    ("DPYD", "capecitabine"): ("L01BC06", "kapecitabin"),
    ("HLA-B", "allopurinol"): ("M04AA01", "allopurinol"),
    ("HLA-B", "carbamazepine"): ("N03AF01", "karbamazepin"),
    ("HLA-B", "fosphenytoin"): ("N03AB05", "foszfenitoin"),
    ("HLA-B", "oxcarbazepine"): ("N03AF02", "oxkarbazepin"),
    ("HLA-B", "phenytoin"): ("N03AB02", "fenitoin"),
    ("SLCO1B1", "atorvastatin"): ("C10AA05", "atorvasztatin"),
    ("SLCO1B1", "fluvastatin"): ("C10AA04", "fluvasztatin"),
    ("SLCO1B1", "lovastatin"): ("C10AA02", "lovasztatin"),
    ("SLCO1B1", "pitavastatin"): ("C10AA08", "pitavasztatin"),
    ("SLCO1B1", "pravastatin"): ("C10AA03", "pravasztatin"),
    ("SLCO1B1", "rosuvastatin"): ("C10AA07", "rozuvasztatin"),
    ("TPMT", "mercaptopurine"): ("L01BB02", "merkaptopurin"),
    ("TPMT", "thioguanine"): ("L01BB03", "tioguanin"),
}

# Index pairs already in cyp2d6-knowledge.v0.json — do not overwrite.
SKIP = {
    ("CYP2D6", "paroxetine"),
    ("CYP2D6", "fluoxetine"),
    ("CYP2C19", "clopidogrel"),
    ("CYP2B6", "efavirenz"),
    ("CYP2C9", "celecoxib"),
    ("CYP3A5", "tacrolimus"),
    ("DPYD", "fluorouracil"),
    ("SLCO1B1", "simvastatin"),
    ("TPMT", "azathioprine"),
    ("HLA-B", "abacavir"),
    ("UGT1A1", "atazanavir"),
}

PHENO = {
    "ultrarapid metabolizer": "UM",
    "rapid metabolizer": "RM",
    "normal metabolizer": "NM",
    "likely intermediate metabolizer": "LIM",
    "intermediate metabolizer": "IM",
    "likely poor metabolizer": "LPM",
    "poor metabolizer": "PM",
    "normal function": "NF",
    "increased function": "IF",
    "possible decreased function": "PDF",
    "decreased function": "DF",
    "poor function": "PF",
    "possible intermediate metabolizer": "PIM",
}

COMPANION_OK = {
    "Normal Metabolizer",
    "Normal Function",
    "No Result",
    "n/a",
    "N/A",
}

STRENGTH = {"Strong": 3, "Moderate": 2, "Optional": 1, "No Recommendation": 0, "n/a": 0, None: 0}


def pheno_code(name: str | None) -> str | None:
    if not name:
        return None
    n = name.strip().lower()
    if n in {"indeterminate", "no result", "n/a", "unknown"}:
        return None
    return PHENO.get(n)


def classify(rec: str, *, inn: str) -> str | None:
    t = (rec or "").strip()
    if not t:
        return None
    low = t.lower()
    if low in {"no recommendation", "n/a"}:
        return "NO_RECOMMENDATION"
    if low.startswith("no recommendation"):
        return "NO_RECOMMENDATION"
    if "no action recommended based on genotype" in low:
        return "NO_RECOMMENDATION"
    if "no recommendation for" in low and ("insufficient evidence" in low or "minimal evidence" in low or "lack of evidence" in low):
        return "NO_RECOMMENDATION"
    if "no recommendation due to lack of evidence" in low:
        return "NO_RECOMMENDATION"

    if "initiate with a dose of" in low:
        if "4 hours after dosing" in low:
            return "CONSIDER_DOSE_CHANGE"
        return "CONTINUE"
    if "increase starting daily dose" in low or "increase the starting daily dose" in low:
        return "CONSIDER_DOSE_CHANGE"
    if "initiate therapy with standard starting dose" in low:
        return "CONTINUE"
    if "initiate standard starting daily dose" in low or "initiate standard starting" in low:
        return "CONTINUE"
    if "choose an alternative therapy" in low:
        return "CONSIDER_ALTERNATIVE"
    # Label dose first, optional switch if no response — that is CONTINUE, not alternative.
    if re.search(r"use \w+ label recommended", low) or "label recommended age- or weight-specific dosing" in low:
        return "CONTINUE"
    inn_l = inn.lower()
    avoid_drug = bool(
        re.search(rf"\bavoid {re.escape(inn_l)}\b", low)
        or re.search(rf"\bdo not use {re.escape(inn_l)}\b", low)
        or f"{inn_l} is not recommended" in low
        or f"{inn_l} is contraindicated" in low
        or f"avoid use of {inn_l}" in low
        or "avoid codeine use" in low
        or "avoid tramadol use" in low
        or "avoid use of 5-fluorouracil" in low
        or "do not use phenytoin" in low
        or "do not use carbamazepine" in low
        or "do not use oxcarbazepine" in low
        or "abacavir is not recommended" in low
    )
    alt = bool(
        "select alternative" in low
        or "recommend alternative" in low
        or "consider alternative" in low
        or "consider an alternative" in low
        or "consider a clinically appropriate alternative" in low
        or "consider a non-tramadol opioid" in low
        or "consider a non-codeine" in low
        or "consider non-codeine" in low
        or "prescribe an alternative statin" in low
        or "consider hormonal therapy" in low
        or "consider selecting another" in low
        or "alternative hormonal therapy" in low
        or "non-thiopurine" in low
        or "alternative agent" in low
    )
    # Tamoxifen NM: "Avoid moderate and strong CYP2D6 inhibitors. Initiate ... standard of care"
    inhibitor_avoid_only = "avoid moderate and strong cyp2d6 inhibitors" in low and "initiate therapy with recommended standard" in low
    if inhibitor_avoid_only:
        return "CONTINUE"
    if avoid_drug or (alt and "initiate therapy with recommended starting dose" not in low):
        # vortioxetine PM: 50% dose OR alternative → dose change is also present; prefer alternative if "or consider ... alternative" after a dose cut? CPIC lists both. Prefer CONSIDER_DOSE_CHANGE if a numeric dose cut for THIS drug comes first.
        if re.search(r"initiate 50% of starting dose", low) and "or consider" in low:
            return "CONSIDER_DOSE_CHANGE"
        return "CONSIDER_ALTERNATIVE"

    dose = bool(
        re.search(r"\breduc", low)
        or "25%" in low
        or "50%" in low
        or "lowest recommended starting" in low
        or "increase starting dose" in low
        or "limit dose" in low
        or "≤40mg" in low
        or "<=40mg" in low
        or "≤20mg" in low
        or "25-50%" in low
        or "approximately 25% less" in low
        or "approximately 50% less" in low
        or "prescribe ≤" in low
    )
    cont = bool(
        "initiate therapy with recommended starting dose" in low
        or "initiate standard dosing" in low
        or "initiate therapy with standard recommended dose" in low
        or "no indication to change dose or therapy" in low
        or "no need to avoid prescribing" in low
        or "desired starting dose" in low
        or "label recommended" in low
        or "use the recommended" in low
        or "per standard dosing" in low
        or "no adjustments needed" in low
        or "use codeine label recommended" in low
        or "use tramadol label recommended" in low
        or "use hydrocodone label recommended" in low
        or "recommended standard of care dosing" in low
    )
    if dose and not cont:
        return "CONSIDER_DOSE_CHANGE"
    if cont:
        return "CONTINUE"
    if dose:
        return "CONSIDER_DOSE_CHANGE"
    return None


def companion_ok(lookup: dict, gene: str) -> bool:
    for other, val in (lookup or {}).items():
        if other == gene:
            continue
        if str(other).startswith("HLA-"):
            if val in {"No Result", "n/a"} or str(val).endswith("negative"):
                continue
            return False
        if val in COMPANION_OK:
            continue
        # activity score 2.0 = normal for CYP2C9 when this gene is HLA-B
        if str(val) in {"2.0"}:
            continue
        return False
    return True


def population_rank(pop: str | None) -> int:
    p = (pop or "general").strip().lower()
    if p == "general":
        return 0
    if p == "adults":
        return 1
    if "naive" in p:
        return 2
    if "pediatr" in p:
        return 5
    if "3 mos" in p or "3mos" in p or ">3" in p:
        return 9
    return 4


def rec_file(gene: str) -> Path:
    token = "hlab" if gene == "HLA-B" else gene.lower()
    return PREPARE / f"{token}-cpic-recommendation-view.v0.json"


def hla_pheno(lookup_val: str) -> str | None:
    v = lookup_val.replace("HLA-B", "").strip()
    if "57:01" in v and "positive" in v:
        return "POS_5701"
    if "57:01" in v and "negative" in v:
        return "NEG_5701"
    if "58:01" in v and "positive" in v:
        return "POS_5801"
    if "58:01" in v and "negative" in v:
        return "NEG_5801"
    if "15:02" in v and "positive" in v:
        return "POS_1502"
    if "15:02" in v and "negative" in v:
        return "NEG_1502"
    return None


def build() -> dict:
    pairings: list[dict] = []
    skipped: list[dict] = []
    for (gene, inn), (atc5, inn_hu) in sorted(ATC.items()):
        if (gene, inn) in SKIP:
            continue
        path = rec_file(gene)
        doc = json.loads(path.read_text(encoding="utf-8"))
        rows = [r for r in doc.get("rows") or [] if r.get("drugname") == inn]
        by_pheno: dict[str, list[tuple[int, int, str, str]]] = defaultdict(list)
        by_as: dict[str, list[tuple[int, int, str, str]]] = defaultdict(list)
        for r in rows:
            lookup = r.get("lookupkey") or {}
            phenos = r.get("phenotypes") or {}
            rec = r.get("drugrecommendation") or ""
            if not companion_ok(lookup, gene):
                continue
            classification = r.get("classification")
            cat = classify(rec, inn=inn)
            if cat is None:
                skipped.append({"gene": gene, "inn": inn, "rec": rec[:160], "why": "unmapped"})
                continue
            if classification in {"No Recommendation", "n/a"} and cat == "NO_RECOMMENDATION":
                # keep only if this phenotype has no actionable row (handled after grouping)
                pass
            pop_r = population_rank(r.get("population"))
            st = STRENGTH.get(r.get("classification"), 0)
            if gene == "HLA-B":
                code = hla_pheno(str(lookup.get("HLA-B") or ""))
            else:
                code = pheno_code(phenos.get(gene) if isinstance(phenos, dict) else None)
            as_map = r.get("activityscore") or {}
            as_key = None
            if isinstance(as_map, dict):
                raw = as_map.get(gene)
                if raw not in {None, "n/a", "N/A", "No Result"}:
                    as_key = str(raw)
            if as_key:
                by_as[as_key].append((pop_r, -st, cat, rec[:240]))
            if code:
                by_pheno[code].append((pop_r, -st, cat, rec[:240]))
        by_phenotype: dict[str, str] = {}
        for code, items in by_pheno.items():
            items.sort()
            best_pop = items[0][0]
            at_pop = [(pop, st, c, rec) for pop, st, c, rec in items if pop == best_pop]
            actionable = [c for _p, _s, c, _r in at_pop if c != "NO_RECOMMENDATION"]
            cats = set(actionable) if actionable else {c for _p, _s, c, _r in at_pop}
            if len(cats) != 1:
                skipped.append({"gene": gene, "inn": inn, "pheno": code, "why": "conflict", "cats": sorted(cats)})
                continue
            by_phenotype[code] = next(iter(cats))
        by_activity: dict[str, str] = {}
        for key, items in by_as.items():
            items.sort()
            best_pop = items[0][0]
            at_pop = [(pop, st, c, rec) for pop, st, c, rec in items if pop == best_pop]
            actionable = [c for _p, _s, c, _r in at_pop if c != "NO_RECOMMENDATION"]
            cats = set(actionable) if actionable else {c for _p, _s, c, _r in at_pop}
            if len(cats) == 1:
                by_activity[key] = next(iter(cats))
        if not by_phenotype and not by_activity:
            skipped.append({"gene": gene, "inn": inn, "why": "empty_after_filter"})
            continue
        rec0 = next((r for r in rows if r.get("guidelineurl")), rows[0] if rows else {})
        pairing = {
            "gene": gene,
            "atc5": atc5,
            "inn": inn,
            "inn_hu": inn_hu,
            "source_id": f"CPIC-REC-{gene}-{inn.upper().replace(' ', '-')}",
            "guidelineurl": rec0.get("guidelineurl"),
            "guidelinename": rec0.get("guidelinename"),
            "companion_rule": "other genes in lookupkey are Normal Metabolizer, Normal Function, No Result, n/a, or HLA negative",
            "by_phenotype": by_phenotype or None,
            "by_activity_score": by_activity or None,
        }
        pairings.append(pairing)
    return {
        "id": "pgx-prepare-12-rec-pairings@v0",
        "accessed": TODAY,
        "note": (
            "Strategy categories from pinned CPIC recommendation_view. No milligrams. "
            "F5 and VKORC1 rec_view are empty: F5 has no live pair; warfarin is the 2017 diagram, not this file."
        ),
        "pairings": pairings,
        "skipped": skipped,
    }


def main() -> int:
    doc = build()
    OUT.write_text(
        json.dumps({k: doc[k] for k in ("id", "accessed", "note", "pairings")}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    print("pairings", len(doc["pairings"]), "skipped", len(doc["skipped"]))
    for p in doc["pairings"]:
        print(p["gene"], p["inn"], p["atc5"], "pheno", p.get("by_phenotype"), "as", p.get("by_activity_score"))
    print("--- skipped ---")
    for s in doc["skipped"][:40]:
        print(s)
    if len(doc["skipped"]) > 40:
        print("...", len(doc["skipped"]) - 40, "more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
