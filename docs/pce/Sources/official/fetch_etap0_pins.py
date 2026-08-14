#!/usr/bin/env python3
"""Fetch ETAP 0 official pins (DPWG, Ensembl POST, CYP2C19 diplotype, WHO B01AC04, KNMP).

Does not rewrite 2026-08-13 MANIFEST accessed date. Merges new file rows only.

Usage: python3 docs/pce/Sources/official/fetch_etap0_pins.py
"""
from __future__ import annotations

import hashlib
import json
import ssl
import time
import urllib.request
from pathlib import Path

DEST = Path(__file__).resolve().parent
ROOT = DEST.parents[3]
TODAY = "2026-08-14"
UA = "PrecisionClinicalEngine/0.1 (source-pin; educational)"
RSIDS = [
    "rs3745274",
    "rs1799853",
    "rs1057910",
    "rs776746",
    "rs6025",
    "rs4149056",
    "rs1800462",
    "rs1142345",
    "rs9923231",
    "rs8175347",
]


def fetch(url: str, accept: str = "*/*", extra: dict | None = None, data: bytes | None = None) -> tuple[str, bytes]:
    headers = {"User-Agent": UA, "Accept": accept}
    if extra:
        headers.update(extra)
    req = urllib.request.Request(
        url, headers=headers, data=data, method="POST" if data else "GET"
    )
    ctx = ssl.create_default_context()
    last: Exception | None = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
                body = resp.read()
                ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip()
                return ctype, body
        except Exception as exc:
            last = exc
            time.sleep(min(32, 3 * (2**attempt)))
    assert last is not None
    raise last


def main() -> int:
    rows = []

    url = "https://api.clinpgx.org/v1/data/guidelineAnnotation?source=DPWG"
    _ctype, data = fetch(url, "application/json")
    json.loads(data)
    path = DEST / "clinpgx-dpwg-guideline-annotations-2026-08-14.json"
    path.write_bytes(data)
    rows.append(("CLINPGX-DPWG-GUIDELINE-ANNOTATIONS", url, path, "application/json"))
    time.sleep(0.6)

    url = "https://api.cpicpgx.org/v1/diplotype?genesymbol=eq.CYP2C19&diplotype=in.(*1/*1,*1/*2,*2/*2)"
    _ctype, data = fetch(url, "application/json")
    json.loads(data)
    path = DEST / "cpic-api-diplotype-cyp2c19-nm-im-pm.json"
    path.write_bytes(data)
    rows.append(("CPIC-DIPLOTYPE-CYP2C19-API", url, path, "application/json"))
    time.sleep(0.6)

    url = "https://www.whocc.no/atc_ddd_index/?code=B01AC04"
    _ctype, data = fetch(url, "text/html")
    path = DEST / "whocc-atc-b01ac04.html"
    path.write_bytes(data)
    rows.append(("WHO-ATC-B01AC04", url, path, "text/html"))
    time.sleep(0.6)

    url = "https://www.knmp.nl/dossiers/farmacogenetica"
    _ctype, data = fetch(url, "text/html")
    path = DEST / "knmp-farmacogenetica-2026-08-14.html"
    path.write_bytes(data)
    rows.append(("KNMP-FARMACOGENETICA-LANDING", url, path, "text/html"))
    time.sleep(0.6)

    payload = json.dumps({"ids": RSIDS}).encode()
    _ctype, data38 = fetch(
        "https://rest.ensembl.org/variation/homo_sapiens",
        "application/json",
        extra={"Content-Type": "application/json"},
        data=payload,
    )
    time.sleep(1)
    _ctype, data37 = fetch(
        "https://grch37.rest.ensembl.org/variation/homo_sapiens",
        "application/json",
        extra={"Content-Type": "application/json"},
        data=payload,
    )
    bundle = {
        "accessed": TODAY,
        "grch38_url": "https://rest.ensembl.org/variation/homo_sapiens",
        "grch37_url": "https://grch37.rest.ensembl.org/variation/homo_sapiens",
        "ids": RSIDS,
        "grch38": json.loads(data38),
        "grch37": json.loads(data37),
    }
    path = DEST / "ensembl-prepare12-defining-snvs-2026-08-14.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rows.append(
        (
            "ENSEMBL-PREPARE12-DEFINING-SNVS",
            "https://rest.ensembl.org/variation/homo_sapiens",
            path,
            "application/json",
        )
    )

    ids = ",".join(r[2:] for r in RSIDS)
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        f"?db=snp&id={ids}&retmode=json"
    )
    _ctype, data = fetch(url, "application/json")
    json.loads(data)
    path = DEST / "ncbi-dbsnp-prepare12-defining-snvs-2026-08-14.json"
    path.write_bytes(data)
    rows.append(("NCBI-DBSNP-PREPARE12-DEFINING-SNVS", url, path, "application/json"))

    man_path = DEST / "MANIFEST.json"
    manifest = json.loads(man_path.read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in manifest["files"]}
    for pin_id, url, path, ctype in rows:
        rec = {
            "id": pin_id,
            "url": url,
            "path": str(path.relative_to(ROOT)),
            "accessed": TODAY,
            "ok": True,
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "content_type": ctype,
        }
        by_id[pin_id] = rec
    # keep original order then append new ids
    seen = []
    files = []
    for row in manifest["files"]:
        files.append(by_id[row["id"]])
        seen.append(row["id"])
    for pin_id, *_rest in rows:
        if pin_id not in seen:
            files.append(by_id[pin_id])
    manifest["files"] = files
    man_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ok", sum(1 for r in files if r.get("ok")), "accessed", manifest["accessed"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
