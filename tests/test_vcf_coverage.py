#!/usr/bin/env python3
"""FR-210: missing defining position is INDETERMINATE, not NORMAL. Matcher OFF."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pce_clinical.coverage import assess_coverage  # noqa: E402
from pce_report.flags import MATCHER_ON  # noqa: E402

GOLD = ROOT / "tests" / "fixtures" / "vcf-gold-v0"
CATALOG = GOLD / "defining-positions.v0.json"


class CoverageGoldTests(unittest.TestCase):
    def test_matcher_stays_off(self) -> None:
        self.assertIs(MATCHER_ON, False)
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.assertFalse(catalog["matcher_on"])
        self.assertFalse(catalog["pharmcat_absent_to_ref"])

    def test_three_missing_sites_are_indeterminate_not_normal(self) -> None:
        cases = (
            ("missing-cyp2d6-star4.vcf", "CYP2D6", "rs3892097"),
            ("missing-cyp2c19-star2.vcf", "CYP2C19", "rs4244285"),
            ("missing-dpyd-star2a.vcf", "DPYD", "rs3918290"),
        )
        for name, gene, rsid in cases:
            with self.subTest(name=name):
                text = (GOLD / name).read_text(encoding="utf-8")
                rows = {r["gene"]: r for r in assess_coverage(text, reference="GRCh38")}
                row = rows[gene]
                self.assertEqual(row["callability"], "INDETERMINATE")
                self.assertNotEqual(row["callability"], "CALLED")
                self.assertEqual(row["naive_missing_to_ref_would_claim"], "Normal Metabolizer")
                self.assertFalse(row["pharmcat_absent_to_ref"])
                missing_ids = {m.get("rsid") for m in row["missing"]}
                self.assertIn(rsid, missing_ids)
                self.assertIn("INDETERMINATE", row["note_hu"])
                self.assertNotEqual(row["callability"], "NORMAL")

    def test_catalog_gap_is_not_tested_not_normal(self) -> None:
        text = (GOLD / "missing-cyp2d6-star4.vcf").read_text(encoding="utf-8")
        rows = {r["gene"]: r for r in assess_coverage(text, reference="GRCh38")}
        self.assertEqual(rows["HLA-B"]["callability"], "NOT_TESTED")
        self.assertIsNone(rows["HLA-B"]["naive_missing_to_ref_would_claim"])


if __name__ == "__main__":
    unittest.main()
