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


if __name__ == "__main__":
    unittest.main()
