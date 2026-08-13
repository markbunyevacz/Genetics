#!/usr/bin/env python3
"""pheno-gold-v0: official-null phenoconversion (G3). No invented PM."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pce_shadow.engine import infer  # noqa: E402

GOLD = ROOT / "tests" / "fixtures" / "pheno-gold-v0" / "cases.v0.json"


class PhenoGoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = json.loads(GOLD.read_text(encoding="utf-8"))
        cls.cases = list(cls.doc["cases"])

    def test_n_at_least_30(self) -> None:
        self.assertEqual(self.doc["n"], len(self.cases))
        self.assertGreaterEqual(len(self.cases), 30)

    def test_g3_recall_on_pheno_gold(self) -> None:
        hits = 0
        misses: list[str] = []
        for case in self.cases:
            inf = infer(case["payload"])
            exp = case["expect"]
            ok = True
            if inf["functional_phenotype"] != exp["functional_phenotype"]:
                ok = False
            if inf["phenoconversion"]["applied"] != exp["phenoconversion_applied"]:
                ok = False
            if inf["phenoconversion"]["functional_phenotype_written"] != exp["functional_phenotype_written"]:
                ok = False
            if inf["phenoconversion"]["mapping_status"] != exp["mapping_status"]:
                ok = False
            if inf["phenoconversion"]["inhibitor_atc5"] != exp["inhibitor_atc5"]:
                ok = False
            if inf["phenoconversion"]["inhibitor_class"] != exp["inhibitor_class"]:
                ok = False
            if inf["clinical_context"] != exp["clinical_context"]:
                ok = False
            cats = [f["strategy_category"] for f in inf.get("live_findings") or []]
            if cats != exp["live_findings_categories"]:
                ok = False
            organ = bool(inf.get("organ_flags"))
            if organ != exp["organ_flag"]:
                ok = False
            gp = (inf.get("genotype_phenotype") or [{}])[0].get("genotype_phenotype")
            if gp != exp["genotype_phenotype"]:
                ok = False
            dumped = json.dumps(inf)
            if "dose_mg" in dumped:
                ok = False
            if inf["forras_allapot"]["functional_phenotype_iras"]["irtunk_szegeny_metabolizalot"]:
                ok = False
            if ok:
                hits += 1
            else:
                misses.append(
                    f"{case['id']} mapping={inf['phenoconversion']['mapping_status']} "
                    f"cats={cats} organ={organ} gp={gp}"
                )
        n = len(self.cases)
        recall = hits / n
        self.assertGreaterEqual(recall, 0.90, msg=f"G3 recall {hits}/{n}={recall:.3f} misses={misses}")
        self.assertEqual(misses, [], msg=f"SYN oracle must be exact; misses={misses}")

    def test_no_case_expects_functional_pm(self) -> None:
        for case in self.cases:
            self.assertEqual(case["expect"]["functional_phenotype"], [])
            self.assertFalse(case["expect"]["phenoconversion_applied"])
            self.assertFalse(case["expect"]["functional_phenotype_written"])


if __name__ == "__main__":
    unittest.main()
