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
        self.assertIn("Strong index inhibitors", fda)
        who = (OFFICIAL / "whocc-atc-n06ab05.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("N06AB05", who)
        self.assertIn("paroxetine", who)

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
