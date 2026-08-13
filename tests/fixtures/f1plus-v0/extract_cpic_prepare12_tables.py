#!/usr/bin/env python3
"""Download CPIC pair_view + recommendation_view for every PREPARE-12 gene.

Does not invent recommendation text. Run:

  python3 extract_cpic_prepare12_tables.py
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PREPARE_12 = (
    "CYP2B6",
    "CYP2C9",
    "CYP2C19",
    "CYP2D6",
    "CYP3A5",
    "DPYD",
    "F5",
    "HLA-B",
    "SLCO1B1",
    "TPMT",
    "UGT1A1",
    "VKORC1",
)
ACCESSED = "2026-08-13"
UA = {"User-Agent": "PCE-research/1.0", "Prefer": "count=exact"}


def fetch(url: str) -> tuple[list, str | None]:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
        cr = r.headers.get("content-range")
    if not isinstance(data, list):
        raise SystemExit(f"unexpected payload from {url}")
    return data, cr


def rec_url(gene: str) -> str:
    # PostgREST JSON-path filter. Hyphenated gene symbols need quoting.
    if "-" in gene:
        return (
            "https://api.cpicpgx.org/v1/recommendation_view?"
            + urllib.parse.urlencode({f"lookupkey->>{gene}": "not.is.null"})
        )
    return f"https://api.cpicpgx.org/v1/recommendation_view?lookupkey->>{gene}=not.is.null"


def pair_url(gene: str) -> str:
    return f"https://api.cpicpgx.org/v1/pair_view?genesymbol=eq.{urllib.parse.quote(gene)}"


def guideline_url(gene: str) -> str:
    return f"https://api.cpicpgx.org/v1/guideline?genes=cs.{{{gene}}}"


def slim_rec(rec: dict) -> dict:
    return {
        "recommendationid": rec.get("recommendationid"),
        "drugname": rec.get("drugname"),
        "lookupkey": rec.get("lookupkey"),
        "phenotypes": rec.get("phenotypes"),
        "activityscore": rec.get("activityscore"),
        "implications": rec.get("implications"),
        "drugrecommendation": rec.get("drugrecommendation"),
        "classification": rec.get("classification"),
        "population": rec.get("population"),
        "guidelinename": rec.get("guidelinename"),
        "guidelineurl": rec.get("guidelineurl"),
        "comments": rec.get("comments"),
    }


def main() -> None:
    here = Path(__file__).resolve().parent
    out = here / "prepare12"
    out.mkdir(exist_ok=True)
    index: dict = {
        "id": "pce-f1plus-prepare12-cpic-index",
        "version": "v0",
        "accessed": ACCESSED,
        "source": {
            "name": "CPIC/ClinPGx pair_view + recommendation_view",
            "pair_api_template": "https://api.cpicpgx.org/v1/pair_view?genesymbol=eq.{GENE}",
            "rec_api_template": "https://api.cpicpgx.org/v1/recommendation_view?lookupkey->>{GENE}=not.is.null",
            "do_not_invent_recommendation_text": True,
            "who_obtains": "manufacturer",
            "who_obtains_hu": (
                "A gyártó (ez a repo) tölti le a nyilvános CPIC API-t, és rögzíti az accessed dátumot. "
                "Nem a labor és nem a kórház feladata."
            ),
        },
        "genes": {},
    }
    for gene in PREPARE_12:
        slug = gene.lower().replace("-", "")
        pu, ru, gu = pair_url(gene), rec_url(gene), guideline_url(gene)
        pairs, _ = fetch(pu)
        try:
            recs, _ = fetch(ru)
        except urllib.error.HTTPError as exc:
            recs = []
            rec_error = f"HTTP {exc.code}"
        else:
            rec_error = None
        try:
            guidelines, _ = fetch(gu)
        except urllib.error.HTTPError:
            guidelines = []
        pair_path = out / f"{slug}-cpic-pair-view.v0.json"
        rec_path = out / f"{slug}-cpic-recommendation-view.v0.json"
        pair_doc = {
            "id": f"pce-f1plus-{slug}-cpic-pair-view",
            "version": "v0",
            "accessed": ACCESSED,
            "source": {"name": "CPIC/ClinPGx pair_view", "api": pu},
            "pair_count": len(pairs),
            "pairs": pairs,
        }
        rec_doc = {
            "id": f"pce-f1plus-{slug}-cpic-recommendation-view",
            "version": "v0",
            "accessed": ACCESSED,
            "source": {
                "name": "CPIC/ClinPGx recommendation_view",
                "api": ru,
                "pair_api": pu,
                "do_not_invent_recommendation_text": True,
            },
            "pair_count": len(pairs),
            "pair_drugnames": sorted({p.get("drugname") for p in pairs if p.get("drugname")}),
            "recommendation_count": len(recs),
            "guidelines": [
                {
                    "id": g.get("id"),
                    "name": g.get("name"),
                    "url": g.get("url"),
                    "clinpgxid": g.get("clinpgxid"),
                    "notesonusage": g.get("notesonusage"),
                    "version": g.get("version"),
                }
                for g in guidelines
            ],
            "rows": [slim_rec(r) for r in recs],
        }
        if rec_error:
            rec_doc["fetch_error"] = rec_error
        pair_path.write_text(json.dumps(pair_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        rec_path.write_bytes(json.dumps(rec_doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        hianyzik = []
        if not pairs:
            hianyzik.append("CPIC pair_view üres ehhez a génhez")
        if not recs:
            hianyzik.append("CPIC recommendation_view üres vagy nem olvasható ehhez a génhez")
        if gene == "F5":
            hianyzik.append(
                "A PharmCAT 2.11.0 eltávolította az F5-öt, mert a DPWG visszavonta az F5–szisztémás hormonális kontraceptívum ajánlást. A CPIC pair_view sorai megmaradnak, kitalált ajánlásszöveg nincs."
            )
        index["genes"][gene] = {
            "pairs_file": str(pair_path.relative_to(here)),
            "recs_file": str(rec_path.relative_to(here)),
            "pair_count": len(pairs),
            "recommendation_count": len(recs),
            "pair_api": pu,
            "rec_api": ru,
            "hianyzik": hianyzik,
        }
        print(gene, "pairs", len(pairs), "recs", len(recs), "hianyzik", hianyzik or "-")
    (out / "index.v0.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote", out / "index.v0.json")


if __name__ == "__main__":
    main()
