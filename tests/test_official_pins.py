#!/usr/bin/env python3
"""Official CPIC/FDA/WHO files are on disk with an accessed date (D-38)."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "docs" / "pce" / "Sources" / "official"
KNOWLEDGE = ROOT / "tests" / "fixtures" / "shadow-v0" / "cyp2d6-knowledge.v0.json"


class OfficialPinTests(unittest.TestCase):
    def test_manifest_and_binaries(self) -> None:
        manifest = json.loads((OFFICIAL / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["accessed"], "2026-08-13")
        by_id = {row["id"]: row for row in manifest["files"]}
        self.assertTrue(by_id["CPIC-SSRI-2023-PDF"]["ok"])
        self.assertTrue(by_id["FDA-DDI-TABLE-2-2-HTML"]["ok"])
        ssri = ROOT / by_id["CPIC-SSRI-2023-PDF"]["path"]
        opioid = ROOT / by_id["CPIC-OPIOID-2020-PDF"]["path"]
        self.assertTrue(ssri.read_bytes().startswith(b"%PDF"))
        self.assertTrue(opioid.read_bytes().startswith(b"%PDF"))
        fda = (ROOT / by_id["FDA-DDI-TABLE-2-2-HTML"]["path"]).read_text(encoding="utf-8", errors="replace")
        self.assertIn("Table 2-2", fda)
        self.assertIn("paroxetine", fda)
        self.assertIn("fluoxetine", fda)
        self.assertIn("quinidine", fda)
        self.assertIn("Strong index inhibitors", fda)
        who = (OFFICIAL / "whocc-atc-n06ab05.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("N06AB05", who)
        self.assertIn("paroxetine", who)
        esc = (OFFICIAL / "whocc-atc-n06ab10.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("escitalopram", esc.lower())
        qin = (OFFICIAL / "whocc-atc-c01ba01.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("quinidine", qin.lower())
        self.assertTrue((OFFICIAL / "edpb-guidelines-01-2025-pseudonymisation.pdf").read_bytes().startswith(b"%PDF"))
        self.assertTrue((OFFICIAL / "wp29-opinion-05-2014-wp216-anonymisation.pdf").read_bytes().startswith(b"%PDF"))
        dpc = (OFFICIAL / "ie-dpc-case-studies-2025.pdf").read_bytes()
        self.assertTrue(dpc.startswith(b"%PDF"))
        gdpr = by_id["EUR-LEX-GDPR-2016-679"]
        self.assertTrue(gdpr["ok"])
        html = (ROOT / gdpr["path"]).read_text(encoding="utf-8", errors="replace")
        self.assertIn(
            "without undue delay and in any event within one month of receipt of the request",
            html,
        )
        self.assertIn(
            "If the controller does not take action on the request of the data subject",
            html,
        )
        self.assertIn("Right to erasure", html)
        self.assertTrue((OFFICIAL / "eur-lex-gdpr-2016-679.pdf").read_bytes().startswith(b"%PDF"))
        ema = (OFFICIAL / "ema-anonymisation-report-form-instructions.pdf").read_bytes()
        self.assertTrue(ema.startswith(b"%PDF"))
        self.assertTrue(by_id["EMA-ANON-REPORT-FORM-INSTRUCTIONS"]["ok"])
        self.assertTrue((OFFICIAL / "mdcg-2021-24-en.pdf").read_bytes().startswith(b"%PDF"))
        self.assertTrue(by_id["MDCG-2021-24"]["ok"])

    def test_knowledge_json_points_at_on_disk_files(self) -> None:
        doc = json.loads(KNOWLEDGE.read_text(encoding="utf-8"))
        missing = []
        for src in doc["sources"]:
            on_disk = src.get("on_disk")
            if not on_disk:
                continue
            path = ROOT / on_disk
            if not path.is_file():
                missing.append(on_disk)
        self.assertEqual(missing, [])
        prepare12 = ROOT / "tests" / "fixtures" / "f1plus-v0" / "prepare12" / "index.v0.json"
        self.assertEqual(json.loads(prepare12.read_text(encoding="utf-8"))["accessed"], "2026-08-13")


if __name__ == "__main__":
    unittest.main()
