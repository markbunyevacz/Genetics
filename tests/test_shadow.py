#!/usr/bin/env python3
"""WP-M — live pairing + phenoconversion without invented PM (FR-400-LIVE, FR-410-LIVE).

FR-220 clinical context is stored, not applied on F1+. FR-440 writes HITL via ingest.
"""
from __future__ import annotations

import ast
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pce_shadow.engine import infer  # noqa: E402
from pce_shadow.table import KnowledgeTable  # noqa: E402

KNOWLEDGE = ROOT / "tests" / "fixtures" / "shadow-v0" / "cyp2d6-knowledge.v0.json"


def _event(**kwargs: object) -> dict:
    base: dict = {
        "diplotypes": [{"gene": "CYP2D6", "diplotype": "*1/*2", "callability": "CALLED"}],
        "medications": [],
    }
    base.update(kwargs)
    return base


class KnowledgePinTests(unittest.TestCase):
    def test_mapping_is_officially_null(self) -> None:
        table = KnowledgeTable(KNOWLEDGE)
        self.assertIsNone(table.nm_plus_strong)
        self.assertEqual(table.adjustment_status, "not_established_by_cpic_2023")
        self.assertEqual(table.strong_inhibitor("N06AB05")["inn"], "paroxetine")
        self.assertEqual(table.strong_inhibitor("N06AB03")["inn"], "fluoxetine")
        self.assertIsNone(table.strong_inhibitor("N06AB"))
        nm = table.genotype_phenotype("CYP2D6", "*1/*2")
        self.assertEqual(nm["genotype_phenotype"], "NM")


class LivePairingTests(unittest.TestCase):
    def test_atc5_paroxetine_nm_pairs_without_writing_pm(self) -> None:
        inf = infer(
            _event(
                medications=[
                    {"system": "http://www.whocc.no/atc", "code": "N06AB05", "display": "paroxetine"}
                ]
            )
        )
        self.assertEqual(inf["clinical_context"], "MANUAL")
        self.assertEqual(inf["genotype_phenotype"][0]["genotype_phenotype"], "NM")
        self.assertTrue(inf["genotype_phenotype"][0]["immutable"])
        self.assertEqual(inf["functional_phenotype"], [])
        self.assertFalse(inf["phenoconversion"]["applied"])
        self.assertFalse(inf["phenoconversion"]["functional_phenotype_written"])
        self.assertEqual(inf["phenoconversion"]["inhibitor_inn"], "paroxetine")
        self.assertEqual(inf["phenoconversion"]["inhibitor_class"], "strong")
        self.assertEqual(inf["phenoconversion"]["mapping_status"], "not_established_by_cpic_2023")
        self.assertEqual(len(inf["live_findings"]), 1)
        finding = inf["live_findings"][0]
        self.assertEqual(finding["strategy_category"], "CONTINUE")
        self.assertEqual(finding["drug_atc"], "N06AB05")
        self.assertNotIn("dose_mg", finding)
        dumped = json.dumps(inf)
        self.assertNotIn("dose_mg", dumped)

    def test_atc5_fluoxetine_no_gene_based_dosing_and_no_pm(self) -> None:
        inf = infer(
            _event(
                medications=[{"system": "http://www.whocc.no/atc", "code": "N06AB03"}]
            )
        )
        self.assertEqual(inf["functional_phenotype"], [])
        self.assertEqual(inf["phenoconversion"]["inhibitor_inn"], "fluoxetine")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "NO_GENE_BASED_DOSING")

    def test_atc4_does_not_claim_paroxetine_or_pm(self) -> None:
        inf = infer(
            _event(
                medications=[
                    {
                        "system": "http://www.whocc.no/atc",
                        "code": "N06AB",
                        "display": "Selective serotonin reuptake inhibitors",
                    }
                ]
            )
        )
        self.assertIsNone(inf["phenoconversion"]["inhibitor_inn"])
        self.assertEqual(inf["phenoconversion"]["mapping_status"], "atc4_insufficient")
        self.assertEqual(inf["functional_phenotype"], [])
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "INSUFFICIENT_RESOLUTION")
        self.assertIsNone(inf["live_findings"][0]["inn"])
        self.assertNotIn("functional_phenotype", inf["live_findings"][0])

    def test_absent_meds_is_not_silent_nm(self) -> None:
        inf = infer(_event(medications=[]))
        self.assertEqual(inf["clinical_context"], "ABSENT")
        self.assertEqual(inf["live_findings"], [])
        self.assertEqual(inf["functional_phenotype"], [])
        self.assertEqual(inf["phenoconversion"]["mapping_status"], "no_clinical_context")

    def test_egfr_below_30_flags_organ_not_a_dose(self) -> None:
        inf = infer(
            _event(
                medications=[{"system": "http://www.whocc.no/atc", "code": "N06AB"}],
                observations=[{"name": "eGFR", "value": 22, "unit": "mL/min/1.73m2"}],
            )
        )
        self.assertEqual(inf["organ_flags"][0]["reason"], "organ")
        self.assertEqual(inf["live_findings"][0]["reason_organ"], "organ")
        self.assertNotIn("dose_mg", json.dumps(inf))

    def test_pm_diplotype_paroxetine_is_dose_change_category(self) -> None:
        inf = infer(
            {
                "diplotypes": [{"gene": "CYP2D6", "diplotype": "*4/*4"}],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "N06AB05"}],
            }
        )
        self.assertEqual(inf["genotype_phenotype"][0]["genotype_phenotype"], "PM")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_DOSE_CHANGE")
        self.assertEqual(inf["functional_phenotype"], [])

    def test_deterministic_findings(self) -> None:
        payload = _event(medications=[{"system": "http://www.whocc.no/atc", "code": "N06AB05"}])
        a, b = infer(payload), infer(payload)
        self.assertEqual(a["live_findings"], b["live_findings"])
        self.assertEqual(a["phenoconversion"]["mapping_status"], b["phenoconversion"]["mapping_status"])
        self.assertEqual(a["config_id"], "pgx-prepare-12@v0")


class HungarianGapSignalTests(unittest.TestCase):
    def test_paroxetine_card_says_what_exists_and_what_is_missing(self) -> None:
        inf = infer(
            _event(
                medications=[
                    {"system": "http://www.whocc.no/atc", "code": "N06AB05", "display": "paroxetine"}
                ]
            )
        )
        self.assertEqual(
            inf["genotype_phenotype"][0]["genotype_phenotype_hu"],
            "normál metabolizáló (a gén alapján az enzim rendesen működik)",
        )
        fa = inf["forras_allapot"]
        van_text = " ".join(row["hu"] for row in fa["van"])
        missing_text = " ".join(row["hu"] for row in fa["hianyzik"])
        self.assertIn("FDA", van_text)
        self.assertIn("N06AB05", van_text)
        self.assertIn("erős", van_text)
        self.assertIn("nincs olyan sor", missing_text.lower())
        self.assertIn("szegény metabolizáló", missing_text)
        self.assertFalse(fa["functional_phenotype_iras"]["irtunk_szegeny_metabolizalot"])
        self.assertIn("gyártó", fa["beszerzes"]["kinek"])
        self.assertEqual(inf["functional_phenotype"], [])
        self.assertIn("paroxetin", inf["live_findings"][0]["strategy_category_hu"] or "")

    def test_atc4_explains_substance_code_not_patient_identity(self) -> None:
        inf = infer(
            _event(medications=[{"system": "http://www.whocc.no/atc", "code": "N06AB"}])
        )
        hu = inf["live_findings"][0]["strategy_category_hu"] or ""
        self.assertIn("hatóanyag", hu)
        self.assertIn("eszcitaloprám", hu)
        self.assertNotIn("azonosít a beteget", hu.lower())
        missing = " ".join(row["hu"] or "" for row in inf["forras_allapot"]["hianyzik"])
        self.assertIn("7 karakter", missing)


class IsolationFromReportTests(unittest.TestCase):
    def test_shadow_package_does_not_import_report_renderer(self) -> None:
        src_root = ROOT / "src" / "pce_shadow"
        for path in src_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    self.assertFalse(node.module.startswith("pce_report"))
                    self.assertFalse(node.module.startswith("pce_clinical"))


if __name__ == "__main__":
    unittest.main()
