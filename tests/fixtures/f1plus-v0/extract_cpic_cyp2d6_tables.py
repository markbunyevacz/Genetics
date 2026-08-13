#!/usr/bin/env python3
"""Regenerate CYP2D6 CPIC pair_view + recommendation_view slices.

Does not invent recommendation text.

  python3 extract_cpic_cyp2d6_tables.py
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

PAIR_URL = "https://api.cpicpgx.org/v1/pair_view?genesymbol=eq.CYP2D6"
REC_URL = "https://api.cpicpgx.org/v1/recommendation_view?lookupkey->>CYP2D6=not.is.null"
GUIDELINE_URL = "https://api.cpicpgx.org/v1/guideline?genes=cs.{CYP2D6}"
ACCESSED = "2026-08-13"


def fetch(url: str) -> list:
    req = urllib.request.Request(url, headers={"Prefer": "count=exact"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"unexpected payload from {url}")
    return data


def main() -> None:
    here = Path(__file__).resolve().parent
    pairs = fetch(PAIR_URL)
    recs = fetch(REC_URL)
    guidelines = fetch(GUIDELINE_URL)
    pair_doc = {
        "id": "pce-f1plus-cyp2d6-cpic-pair-view",
        "version": "v0",
        "accessed": ACCESSED,
        "source": {"name": "CPIC/ClinPGx pair_view", "api": PAIR_URL},
        "pair_count": len(pairs),
        "pairs": pairs,
    }
    rec_doc = {
        "id": "pce-f1plus-cyp2d6-cpic-recommendation-view",
        "version": "v0",
        "accessed": ACCESSED,
        "source": {
            "name": "CPIC/ClinPGx recommendation_view",
            "api": REC_URL,
            "pair_api": PAIR_URL,
            "do_not_invent_recommendation_text": True,
        },
        "pair_count": len(pairs),
        "pair_drugnames": sorted({p["drugname"] for p in pairs}),
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
        "rows": [
            {
                "recommendationid": rec["recommendationid"],
                "drugname": rec["drugname"],
                "lookupkey": rec["lookupkey"],
                "phenotypes": rec["phenotypes"],
                "activityscore": rec["activityscore"],
                "implications": rec["implications"],
                "drugrecommendation": rec["drugrecommendation"],
                "classification": rec["classification"],
                "population": rec["population"],
                "guidelinename": rec["guidelinename"],
                "guidelineurl": rec["guidelineurl"],
                "comments": rec["comments"],
            }
            for rec in recs
        ],
    }
    (here / "cyp2d6-cpic-pair-view.v0.json").write_text(
        json.dumps(pair_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (here / "cyp2d6-cpic-recommendation-view.v0.json").write_bytes(
        json.dumps(rec_doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )
    print(f"pairs={len(pairs)} recommendations={len(recs)}")


if __name__ == "__main__":
    main()
