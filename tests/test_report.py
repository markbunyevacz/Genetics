#!/usr/bin/env python3
"""F1+ renderer: official CPIC tables, FR-210, FR-470 isolation, FR-500 PDF."""
from __future__ import annotations

import ast
import inspect
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pce_report.flags import LIVE_CDS, MATCHER_ON  # noqa: E402
from pce_report.guidelines import GuidelineTable  # noqa: E402
from pce_report.pdf import write_pdf  # noqa: E402
from pce_report.render import RendererConfigError, render_f1plus  # noqa: E402
from pce_report.schema import (  # noqa: E402
    ALLOWED_B41_TOP_LEVEL,
    assemble_b41,
    assert_b41_contract,
    forbidden_b41_field_names,
)
from pce_report.statements import A11_DISCLAIMER, A1_INTENDED_PURPOSE  # noqa: E402

F1 = ROOT / "tests" / "fixtures" / "f1plus-v0"
SPEC_A = ROOT / "docs" / "pce" / "A-intended-purpose-and-modules.md"


def _table() -> GuidelineTable:
    return GuidelineTable(
        F1 / "cyp2d6-cpic-pair-view.v0.json",
        F1 / "cyp2d6-cpic-recommendation-view.v0.json",
    )


class IsolationTests(unittest.TestCase):
    def test_flags_frozen(self) -> None:
        self.assertIs(MATCHER_ON, False)
        self.assertIs(LIVE_CDS, False)

    def test_render_signature_has_no_medication_entry(self) -> None:
        params = inspect.signature(render_f1plus).parameters
        self.assertNotIn("MedicationEntry", params)
        self.assertNotIn("medications", params)

    def test_package_ast_has_no_medication_entry_or_gateway_pipeline(self) -> None:
        src_root = ROOT / "src" / "pce_report"
        for path in src_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            blob = path.read_text(encoding="utf-8")
            self.assertNotIn("MedicationEntry", blob, msg=str(path))
            self.assertNotIn("medication_entry", blob, msg=str(path))
            self.assertNotIn("pce_gateway.pipeline", blob, msg=str(path))
            self.assertNotIn("pce_shadow", blob, msg=str(path))
            self.assertNotIn("pce_hitl", blob, msg=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    self.assertFalse(node.module.startswith("pce_gateway"))


class StatementVerbatimTests(unittest.TestCase):
    def test_a11_in_appendix(self) -> None:
        appendix = SPEC_A.read_text(encoding="utf-8")
        for para in A11_DISCLAIMER.split("\n\n")[:3]:
            self.assertIn(para, appendix)
        self.assertIn("Aláíró orvos:", appendix)
        self.assertIn("adminisztratív adatkezelő és riport-előállító", A1_INTENDED_PURPOSE)
        self.assertIn("adminisztratív adatkezelő és riport-előállító", appendix)


class RenderGoldTests(unittest.TestCase):
    def test_called_emits_all_pairs_and_recs(self) -> None:
        call = json.loads((F1 / "outside-call-cyp2d6-called.json").read_text(encoding="utf-8"))
        table = _table()
        report = render_f1plus(outside_call=call, table=table)
        pairs_doc = json.loads((F1 / "cyp2d6-cpic-pair-view.v0.json").read_text(encoding="utf-8"))
        recs_doc = json.loads(
            (F1 / "cyp2d6-cpic-recommendation-view.v0.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["pair_count"], pairs_doc["pair_count"])
        self.assertEqual(report["pair_count"], len(report["pairs"]))
        self.assertEqual(report["guideline_row_count"], recs_doc["recommendation_count"])
        self.assertEqual(report["guideline_row_count"], len(report["guideline_rows"]))
        self.assertTrue(report["case"]["positive_drug_assertion"])
        self.assertEqual(report["case"]["lab_phenotype_claim"], "CYP2D6 Normal Metabolizer")
        self.assertFalse(report["medications_applied_to_recommendations"])
        self.assertFalse(report["gyogyszerlista_a_leleten"])
        self.assertIn("publikált guideline-sorokat listázza", report["megjegyzes_hu"])
        self.assertNotIn("olvas", report["megjegyzes_hu"].lower())
        self.assertIn("partnerlabor", report["diplotipus_forras_hu"])
        self.assertIn("NamedAlleleMatcher", report["diplotipus_forras_hu"])
        self.assertEqual(report["unsourced_claims"], 0)
        self.assertIn("codeine", {p["drugname"] for p in report["pairs"]})
        self.assertIn(A11_DISCLAIMER, report["a11_disclaimer"])
        self.assertIsNone(report["edu_phenoconversion"])

    def test_indeterminate_no_normal_claim(self) -> None:
        call = json.loads(
            (F1 / "outside-call-cyp2d6-indeterminate.json").read_text(encoding="utf-8")
        )
        report = render_f1plus(outside_call=call, table=_table())
        self.assertFalse(report["case"]["positive_drug_assertion"])
        self.assertIsNone(report["case"]["lab_phenotype_claim"])
        self.assertIsNone(report["case"]["diplotype"])
        self.assertIn("FR-210", report["case"]["fr210"])
        self.assertNotEqual(report["case"].get("lab_phenotype_claim"), "NORMAL")

    def test_rejects_medication_payload(self) -> None:
        call = json.loads((F1 / "outside-call-cyp2d6-called.json").read_text(encoding="utf-8"))
        call["medications"] = [{"code": "N06AB10"}]
        with self.assertRaises(RendererConfigError):
            render_f1plus(outside_call=call, table=_table())

    def test_pdf_contains_disclaimer_and_pair(self) -> None:
        call = json.loads((F1 / "outside-call-cyp2d6-called.json").read_text(encoding="utf-8"))
        report = render_f1plus(outside_call=call, table=_table())
        tmp = Path(tempfile.mkdtemp()) / "f1plus.pdf"
        write_pdf(report, tmp)
        raw = tmp.read_bytes()
        self.assertTrue(raw.startswith(b"%PDF"))
        self.assertGreater(tmp.stat().st_size, 10_000)
        # Extractable strings are compressed; still require a real file + JSON oracle.
        self.assertEqual(report["a11_disclaimer"], A11_DISCLAIMER)


class Prepare12TableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from pce_report.guidelines import prepare12_table

        cls.table = prepare12_table()

    def test_cyp2c19_dumps_official_pairs(self) -> None:
        call = {
            "gene": "CYP2C19",
            "diplotype": "*1/*1",
            "callability": "CALLED",
            "case_display_id": "SYN-CASE-C19",
        }
        report = render_f1plus(outside_call=call, table=self.table)
        self.assertEqual(report["pair_count"], 27)
        self.assertEqual(report["unsourced_claims"], 0)
        self.assertIn("clopidogrel", {p["drugname"] for p in report["pairs"]})
        self.assertFalse(report["hianyzik"])

    def test_f5_signals_missing_recommendation_without_inventing(self) -> None:
        call = {
            "gene": "F5",
            "diplotype": "rs6025 het",
            "callability": "CALLED",
            "case_display_id": "SYN-CASE-F5",
        }
        report = render_f1plus(outside_call=call, table=self.table)
        self.assertEqual(report["pair_count"], 2)
        self.assertEqual(report["guideline_row_count"], 0)
        blob = " ".join(report["hianyzik"])
        self.assertIn("recommendation_view", blob)
        self.assertIn("PharmCAT", blob)
        self.assertEqual(report["unsourced_claims"], 0)

    def test_vkorc1_pair_exists_recommendation_view_gap_is_flagged(self) -> None:
        call = {
            "gene": "VKORC1",
            "diplotype": "*1/*1",
            "callability": "CALLED",
            "case_display_id": "SYN-CASE-VK",
        }
        report = render_f1plus(outside_call=call, table=self.table)
        self.assertEqual(report["pair_count"], 1)
        self.assertEqual(report["pairs"][0]["drugname"], "warfarin")
        blob = " ".join(report["hianyzik"])
        self.assertIn("recommendation_view", blob)
        self.assertIn("Warfarin", blob)


def _assembled() -> dict:
    call = json.loads((F1 / "outside-call-cyp2d6-called.json").read_text(encoding="utf-8"))
    engine = render_f1plus(outside_call=call, table=_table())
    return assemble_b41(
        engine=engine,
        report_id="SYN-RPT-B41",
        case_id="SYN-CASE-B41",
        counselling={"id": "SYN-C", "at": "2026-01-01T00:00:00+00:00", "counsellor_id": "SYN-MD-001"},
        consent_granted_at="2026-01-02T00:00:00+00:00",
        performing_org_license_id="SYN-LIC-001",
        white_label={"org": "SYN-ORG-001", "signer_slot": "SYN-MD-001", "colophon": "Precision Clinical Engine"},
        genes=[
            {
                "gene": "CYP2D6",
                "diplotype": "*1/*2",
                "genotype_phenotype": "CYP2D6 Normal Metabolizer",
                "callability": "CALLED",
            }
        ],
        omit_from_patient=frozenset(),
    )


class B41ContractTests(unittest.TestCase):
    def test_full_allow_list_passes(self) -> None:
        report = _assembled()
        assert_b41_contract(report)
        self.assertEqual(set(report.keys()), ALLOWED_B41_TOP_LEVEL - {"signed"})
        self.assertTrue(set(report.keys()) <= ALLOWED_B41_TOP_LEVEL)

    def test_rejects_medications(self) -> None:
        report = _assembled()
        report["medications"] = [{"atc": "N06AB05", "name": "paroxetin"}]
        with self.assertRaises(RendererConfigError):
            assert_b41_contract(report)

    def test_rejects_medication_entry_type(self) -> None:
        report = _assembled()
        report["Medication" + "Entry"] = {"id": "x"}
        with self.assertRaises(RendererConfigError):
            assert_b41_contract(report)

    def test_rejects_medication_request(self) -> None:
        report = _assembled()
        report["medicationRequest"] = {"id": "x"}
        with self.assertRaises(RendererConfigError):
            assert_b41_contract(report)

    def test_rejects_medication_statement(self) -> None:
        report = _assembled()
        report["medicationStatement"] = {"id": "x"}
        with self.assertRaises(RendererConfigError):
            assert_b41_contract(report)

    def test_rejects_clinical_context(self) -> None:
        report = _assembled()
        report["clinical_context"] = {"meds": ["paroxetin"]}
        with self.assertRaises(RendererConfigError):
            assert_b41_contract(report)

    def test_rejects_hitl_review(self) -> None:
        report = _assembled()
        report["hitl_review"] = {"verdict": "AGREE"}
        with self.assertRaises(RendererConfigError):
            assert_b41_contract(report)

    def test_rejects_hitl_verdict(self) -> None:
        report = _assembled()
        report["hitl_verdict"] = "AGREE"
        with self.assertRaises(RendererConfigError):
            assert_b41_contract(report)

    def test_rejects_unknown_top_level_and_nested_medications(self) -> None:
        report = _assembled()
        report["future_field"] = True
        with self.assertRaises(RendererConfigError):
            assert_b41_contract(report)
        report = _assembled()
        case = dict(report["case"])
        case["medications"] = [{"atc": "N06AB05"}]
        report["case"] = case
        with self.assertRaises(RendererConfigError):
            assert_b41_contract(report)

    def test_delivery_plan_r9_matches_schema(self) -> None:
        import re

        plan = (ROOT / "docs" / "pce" / "Engineering" / "DELIVERY-PLAN.md").read_text(encoding="utf-8")
        line = next(ln for ln in plan.splitlines() if ln.startswith("| R9 |"))
        names = re.findall(r"`([^`]+)`", line)
        schema_names = forbidden_b41_field_names()
        self.assertIn("hitl_*", names)
        for name in names:
            if name in {"hitl_*"}:
                continue
            self.assertIn(name, schema_names, msg=f"R9 {name!r} missing from schema deny-list")
        for name in sorted(schema_names):
            self.assertIn(f"`{name}`", line, msg=f"schema {name!r} missing from DELIVERY-PLAN R9")


if __name__ == "__main__":
    unittest.main()
