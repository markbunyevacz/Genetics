#!/usr/bin/env python3
"""Pin WHO ATC pages, CPIC warfarin PDF, PharmCAT jar checksum (jar lives in var/).

Does not rewrite MANIFEST top-level accessed (must stay 2026-08-13).
Manufacturer (this repo) fetches. Not a lab or hospital task.

Usage: python3 docs/pce/Sources/official/fetch_software_ready_pins.py
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
TODAY = "2026-08-15"
UA = "PrecisionClinicalEngine/0.1 (source-pin; educational)"

# INN → WHO ATC 5th level (7 characters). Verified against the downloaded HTML.
WHO_ATC = [
    ("N06AB06", "sertraline"),
    ("N06AA09", "amitriptyline"),
    ("N06AB04", "citalopram"),
    ("N06AA04", "clomipramine"),
    ("A02BC06", "dexlansoprazole"),
    ("N06AA12", "doxepin"),
    ("N06AA02", "imipramine"),
    ("A02BC03", "lansoprazole"),
    ("A02BC01", "omeprazole"),
    ("A02BC02", "pantoprazole"),
    ("J02AC03", "voriconazole"),
    ("M01AE09", "flurbiprofen"),
    ("C10AA04", "fluvastatin"),
    ("N03AB05", "fosphenytoin"),
    ("M01AE01", "ibuprofen"),
    ("M01AC05", "lornoxicam"),
    ("M01AC06", "meloxicam"),
    ("N03AB02", "phenytoin"),
    ("M01AC01", "piroxicam"),
    ("M01AC02", "tenoxicam"),
    ("N06BA09", "atomoxetine"),
    ("R05DA04", "codeine"),
    ("N06AA01", "desipramine"),
    ("N06AB08", "fluvoxamine"),
    ("R05DA03", "hydrocodone"),
    ("C07AB02", "metoprolol"),
    ("N06AA10", "nortriptyline"),
    ("L02BA01", "tamoxifen"),
    ("N02AX02", "tramadol"),
    ("N06AA06", "trimipramine"),
    ("N06AX16", "venlafaxine"),
    ("N06AX26", "vortioxetine"),
    ("L01BC06", "capecitabine"),
    ("M04AA01", "allopurinol"),
    ("N03AF01", "carbamazepine"),
    ("N03AF02", "oxcarbazepine"),
    ("C10AA05", "atorvastatin"),
    ("C10AA02", "lovastatin"),
    ("C10AA08", "pitavastatin"),
    ("C10AA03", "pravastatin"),
    ("C10AA07", "rosuvastatin"),
    ("L01BB02", "mercaptopurine"),
    ("L01BB03", "tioguanine"),
    ("B01AA03", "warfarin"),
]

PHARMCAT_VERSION = "3.4.0"
PHARMCAT_JAR_URL = (
    f"https://github.com/PharmGKB/PharmCAT/releases/download/v{PHARMCAT_VERSION}/"
    f"pharmcat-{PHARMCAT_VERSION}-all.jar"
)
PHARMCAT_JAR_SHA256 = "9317ef632bf6c9786ff0d9d455d4c9f6d2882ebd66ad7256b4ae958ddf454741"


def fetch(url: str, accept: str = "*/*") -> tuple[str, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
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


def merge_manifest(rows: list[tuple[str, str, Path, str]]) -> None:
    man_path = DEST / "MANIFEST.json"
    manifest = json.loads(man_path.read_text(encoding="utf-8"))
    assert manifest["accessed"] == "2026-08-13"
    by_id = {row["id"]: row for row in manifest["files"]}
    for pin_id, url, path, ctype in rows:
        by_id[pin_id] = {
            "id": pin_id,
            "url": url,
            "path": str(path.relative_to(ROOT)),
            "accessed": TODAY,
            "ok": True,
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "content_type": ctype,
        }
    seen: list[str] = []
    files: list[dict] = []
    for row in manifest["files"]:
        files.append(by_id[row["id"]])
        seen.append(row["id"])
    for pin_id, *_rest in rows:
        if pin_id not in seen:
            files.append(by_id[pin_id])
    manifest["files"] = files
    man_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ok", sum(1 for r in files if r.get("ok")), "accessed", manifest["accessed"])


def main() -> int:
    rows: list[tuple[str, str, Path, str]] = []

    url = "https://files.cpicpgx.org/data/guideline/publication/warfarin/2017/28198005.pdf"
    _ctype, data = fetch(url, "application/pdf")
    path = DEST / "cpic-warfarin-2017-28198005.pdf"
    path.write_bytes(data)
    if not data.startswith(b"%PDF"):
        raise SystemExit("warfarin PDF is not a PDF")
    rows.append(("CPIC-WARFARIN-2017-PDF", url, path, "application/pdf"))
    time.sleep(0.4)

    for code, inn in WHO_ATC:
        url = f"https://www.whocc.no/atc_ddd_index/?code={code}"
        _ctype, data = fetch(url, "text/html")
        path = DEST / f"whocc-atc-{code.lower()}.html"
        path.write_bytes(data)
        text = data.decode("utf-8", errors="replace").lower()
        if code.lower() not in text:
            raise SystemExit(f"WHO page missing code {code}")
        if inn.lower() not in text:
            raise SystemExit(f"WHO page {code} missing inn {inn}")
        rows.append((f"WHO-ATC-{code}", url, path, "text/html"))
        time.sleep(0.35)

    jar_dir = ROOT / "var" / "pharmcat"
    jar_dir.mkdir(parents=True, exist_ok=True)
    jar_path = jar_dir / f"pharmcat-{PHARMCAT_VERSION}-all.jar"
    if not jar_path.is_file() or hashlib.sha256(jar_path.read_bytes()).hexdigest() != PHARMCAT_JAR_SHA256:
        _ctype, blob = fetch(PHARMCAT_JAR_URL, "application/java-archive")
        jar_path.write_bytes(blob)
    digest = hashlib.sha256(jar_path.read_bytes()).hexdigest()
    if digest != PHARMCAT_JAR_SHA256:
        raise SystemExit(f"PharmCAT jar sha256 mismatch: {digest}")
    pin_meta = DEST / "pharmcat-3.4.0-pin.json"
    pin_meta.write_text(
        json.dumps(
            {
                "id": "PHARMCAT-3.4.0-ALL-JAR",
                "accessed": TODAY,
                "url": PHARMCAT_JAR_URL,
                "version": PHARMCAT_VERSION,
                "license": "MPL-2.0",
                "license_url": "https://www.mozilla.org/en-US/MPL/2.0/",
                "sha256": PHARMCAT_JAR_SHA256,
                "bytes": jar_path.stat().st_size,
                "runtime_path": str(jar_path.relative_to(ROOT)),
                "gitignored": True,
                "who_obtains_hu": (
                    "A gyártó (ez a repo) tölti le a PharmCAT all-jar-t. "
                    "A jar nincs a gitben (méret). Script: fetch_software_ready_pins.py."
                ),
                "we_do_not_modify_the_jar": True,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    rows.append(("PHARMCAT-3.4.0-PIN", PHARMCAT_JAR_URL, pin_meta, "application/json"))

    merge_manifest(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
