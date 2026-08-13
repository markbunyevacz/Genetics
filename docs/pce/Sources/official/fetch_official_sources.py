#!/usr/bin/env python3
"""Pin public CPIC PDF + FDA + WHO pages with accessed date. Stdlib only.

The F1+ renderer and shadow engine read pinned JSON extracts, not these PDFs
at runtime. This script is how the manufacturer (this repo) obtains the
official files. Not a lab or hospital task.

Usage: python3 docs/pce/Sources/official/fetch_official_sources.py
"""
from __future__ import annotations

import hashlib
import json
import ssl
import time
import urllib.request
from datetime import date
from pathlib import Path

DEST = Path(__file__).resolve().parent
ROOT = DEST.parents[3]
TODAY = date.today().isoformat()
UA = "PrecisionClinicalEngine/0.1 (source-pin; educational)"

TARGETS = [
    {
        "id": "CPIC-SSRI-2023-PDF",
        "url": "https://files.cpicpgx.org/data/guideline/publication/serotonin_reuptake_inhibitor_antidepressants/2023/37032427.pdf",
        "path": DEST / "cpic-ssri-2023-37032427.pdf",
        "expect": "pdf",
    },
    {
        "id": "CPIC-OPIOID-2020-PDF",
        "url": "https://files.cpicpgx.org/data/guideline/publication/opioids/2020/33387367.pdf",
        "path": DEST / "cpic-opioid-2020-33387367.pdf",
        "expect": "pdf",
    },
    {
        "id": "FDA-DDI-TABLE-2-2-HTML",
        "url": "https://www.fda.gov/drugs/drug-interactions-labeling/drug-development-and-drug-interactions-table-substrates-inhibitors-and-inducers",
        "path": DEST / "fda-ddi-table-substrates-inhibitors-inducers-2026-08-13.html",
        "expect": "html",
    },
    {
        "id": "WHO-ATC-N06AB05",
        "url": "https://www.whocc.no/atc_ddd_index/?code=N06AB05",
        "path": DEST / "whocc-atc-n06ab05.html",
        "expect": "html",
    },
    {
        "id": "WHO-ATC-N06AB03",
        "url": "https://www.whocc.no/atc_ddd_index/?code=N06AB03",
        "path": DEST / "whocc-atc-n06ab03.html",
        "expect": "html",
    },
    {
        "id": "WHO-ATC-STRUCTURE",
        "url": "https://www.whocc.no/atc/structure_and_principles/",
        "path": DEST / "whocc-atc-structure-and-principles.html",
        "expect": "html",
    },
    {
        "id": "WHO-ATC-N06AB10",
        "url": "https://www.whocc.no/atc_ddd_index/?code=N06AB10",
        "path": DEST / "whocc-atc-n06ab10.html",
        "expect": "html",
    },
    {
        "id": "WHO-ATC-C01BA01",
        "url": "https://www.whocc.no/atc_ddd_index/?code=C01BA01",
        "path": DEST / "whocc-atc-c01ba01.html",
        "expect": "html",
    },
    {
        "id": "EDPB-01-2025-PSEUDONYMISATION",
        "url": "https://www.edpb.europa.eu/system/files/2025-01/edpb_guidelines_202501_pseudonymisation_en.pdf",
        "path": DEST / "edpb-guidelines-01-2025-pseudonymisation.pdf",
        "expect": "pdf",
    },
    {
        "id": "WP29-05-2014-WP216",
        "url": "https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf",
        "path": DEST / "wp29-opinion-05-2014-wp216-anonymisation.pdf",
        "expect": "pdf",
    },
    {
        "id": "IE-DPC-CASE-STUDIES-2025",
        "url": "https://www.dataprotection.ie/sites/default/files/uploads/2026-07/DPC-CaseStudies2025-Digital-AW.pdf",
        "path": DEST / "ie-dpc-case-studies-2025.pdf",
        "expect": "pdf",
    },
    {
        "id": "CPIC-DIPLOTYPE-CYP2D6-API",
        "url": "https://api.cpicpgx.org/v1/diplotype?genesymbol=eq.CYP2D6&diplotype=in.(*1/*1,*1/*2,*4/*4)",
        "path": DEST / "cpic-api-diplotype-cyp2d6-nm-pm.json",
        "expect": "json",
    },
    {
        "id": "EUR-LEX-GDPR-2016-679",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679",
        "path": DEST / "eur-lex-gdpr-2016-679.html",
        "expect": "html",
        "optional": True,
    },
]


def fetch(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "*/*"},
        method="GET",
    )
    last_err: Exception | None = None
    ctx = ssl.create_default_context()
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90, context=ctx) as resp:
                return resp.read(), (resp.headers.get("Content-Type") or "").split(";")[0].strip()
        except Exception as e:
            last_err = e
            time.sleep(2**attempt)
    assert last_err is not None
    raise last_err


def main() -> int:
    rows = []
    for t in TARGETS:
        rec = {
            "id": t["id"],
            "url": t["url"],
            "path": str(t["path"].relative_to(ROOT)),
            "accessed": TODAY,
            "ok": False,
        }
        try:
            data, ctype = fetch(t["url"])
        except Exception as exc:
            rec["path"] = None
            rec["error"] = str(exc)
            rows.append(rec)
            print(f"{t['id']} FAIL {exc}")
            if t.get("optional"):
                continue
            raise
        if not data.strip():
            rec["path"] = None
            rec["error"] = "empty body"
            rec["bytes"] = 0
            rows.append(rec)
            print(f"{t['id']} FAIL empty body")
            if t.get("optional"):
                continue
            raise RuntimeError(f"{t['id']} empty body")
        t["path"].write_bytes(data)
        rec["bytes"] = len(data)
        rec["sha256"] = hashlib.sha256(data).hexdigest()
        rec["content_type"] = ctype
        rec["ok"] = True
        if t["expect"] == "pdf" and not data.startswith(b"%PDF"):
            rec["ok"] = False
            rec["error"] = "not a PDF"
        if t["expect"] == "json":
            json.loads(data)
        rows.append(rec)
        print(f"{t['id']} {rec['bytes']} {ctype}")
    manifest = {
        "accessed": TODAY,
        "note": "Official public snapshots. Engine reads pinned JSON extracts, not these PDFs at runtime.",
        "files": rows,
    }
    (DEST / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
