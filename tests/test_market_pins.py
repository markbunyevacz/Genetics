#!/usr/bin/env python3
"""Market/procurement pins for Sales pricing (not clinical tables)."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKET = ROOT / "docs" / "pce" / "Sources" / "market"
PRICING = ROOT / "docs" / "pce" / "Sales" / "pricing.md"
OFFICIAL = ROOT / "docs" / "pce" / "Sources" / "official"


class MarketPinTests(unittest.TestCase):
    def test_manifest_and_his_ceiling(self) -> None:
        manifest = json.loads((MARKET / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["accessed"], "2026-08-13")
        by_id = {row["id"]: row for row in manifest["files"]}
        self.assertTrue(by_id["SMART-YOUSCRIPT"]["ok"])
        self.assertTrue(by_id["SEMMELWEIS-GFI-9641-2020"]["ok"])
        self.assertTrue(by_id["EGOV-KE-2020-58"]["ok"])
        self.assertFalse(by_id["YOUSCRIPT-PROVIDER-1Y"]["ok"])
        self.assertFalse(by_id["EKR001266472024"]["ok"])
        smart = (ROOT / by_id["SMART-YOUSCRIPT"]["path"]).read_text(encoding="utf-8", errors="replace")
        self.assertIn("Per User", smart)
        self.assertIn("Site-Based", smart)
        sem = (ROOT / by_id["SEMMELWEIS-GFI-9641-2020"]["path"]).read_text(
            encoding="utf-8", errors="replace"
        )
        self.assertIn("816.636.406", sem)
        self.assertIn("MedSolution", sem)
        egov = (ROOT / by_id["EGOV-KE-2020-58"]["path"]).read_text(encoding="utf-8", errors="replace")
        self.assertIn("816.636.406", egov)
        self.assertIn("2020/58", egov)

    def test_pricing_doc_is_conclusion_not_list(self) -> None:
        text = PRICING.read_text(encoding="utf-8")
        self.assertIn("következtetés", text.lower())
        self.assertIn("365 USD", text)
        self.assertIn("816.636.406", text)
        self.assertIn("113 OK", text)
        self.assertNotIn("94 zöld", text)
        self.assertIn("UNVERIFIABLE", text)
        self.assertIn("nem megfigyelt", text.lower())
        self.assertIn("15 felíró", text)

    def test_official_pin_count_is_not_seven(self) -> None:
        manifest = json.loads((OFFICIAL / "MANIFEST.json").read_text(encoding="utf-8"))
        ok = [row for row in manifest["files"] if row.get("ok")]
        self.assertGreaterEqual(len(ok), 16)
        text = PRICING.read_text(encoding="utf-8")
        self.assertIn("**16**", text)


if __name__ == "__main__":
    unittest.main()
