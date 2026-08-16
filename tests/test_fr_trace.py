#!/usr/bin/env python3
"""FR-id requirement→test inventory (IEC 62304 §5.1 / GSPR traceability).

The machine check is annotation: every spec FR heading must appear as a
token in tests/*.py. Behavioural coverage lives in the named test modules;
deferred P1/P2 items are asserted *absent* here, not pretended complete.

S3 (M4 audit): FR-420 exists as gene-tagged findings +
severity_means_replace_prescribed=false. FR-250 exists as WHO 7-character
ATC normalisation on the gateway; OGYÉI E-MAP-001 is catalogued, not wired
on the F1+ report path (the lelet does not consume MedicationEntry).
"""
from __future__ import annotations

import ast
import inspect
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pce_clinical.errors import B5  # noqa: E402
from pce_clinical.server import handle_request  # noqa: E402
from pce_clinical.service import ClinicalService  # noqa: E402
from pce_clinical.store import ClinicalStore  # noqa: E402
from pce_gateway.transform import normalize_atc_code, truncate_atc  # noqa: E402
from pce_report.schema import assemble_b41  # noqa: E402

SPEC = ROOT / "docs" / "pce" / "PCE-SPEC-v1.2.md"
FR_HEADING = re.compile(r"^#### (FR-[A-Z0-9-]+)", re.M)


def _tests_blob() -> str:
    parts: list[str] = []
    for path in sorted((ROOT / "tests").rglob("*.py")):
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _mentioned(hay: str, fr_id: str) -> bool:
    return re.search(rf"(?<![A-Z0-9-]){re.escape(fr_id)}(?![A-Z0-9-])", hay) is not None


class FrIdInventoryTests(unittest.TestCase):
    def test_every_spec_fr_appears_in_tests(self) -> None:
        spec = SPEC.read_text(encoding="utf-8")
        ids = FR_HEADING.findall(spec)
        self.assertGreaterEqual(len(ids), 36)
        hay = _tests_blob()
        missing = [fr_id for fr_id in ids if not _mentioned(hay, fr_id)]
        self.assertEqual(missing, [], msg=f"FR-id missing from tests/: {missing}")


class Fr250NormalisationTests(unittest.TestCase):
    """FR-250: 7-character WHO substance code. E-MAP-001 exists; F1+ does not map drugs."""

    def test_default_keeps_seven_character_substance_code(self) -> None:
        self.assertEqual(truncate_atc("N06AB10"), "N06AB10")
        self.assertEqual(normalize_atc_code("n06ab10"), "N06AB10")
        self.assertEqual(len(truncate_atc("N06AB10")), 7)

    def test_e_map_001_is_catalogued_not_raised_by_f1plus_renderer(self) -> None:
        self.assertIn("E-MAP-001", B5)
        src = inspect.getsource(assemble_b41)
        self.assertNotIn("E-MAP-001", src)
        self.assertNotIn("MedicationEntry", src)


class Fr420HighlightTests(unittest.TestCase):
    """FR-420: F1+ findings are gene-tagged; CRITICAL does not mean replace the prescribed drug."""

    def test_severity_means_replace_prescribed_is_false_in_assembler(self) -> None:
        src = inspect.getsource(assemble_b41)
        self.assertIn("severity_means_replace_prescribed", src)
        self.assertIn('"severity_means_replace_prescribed": False', src)


class Fr700LlmBanTests(unittest.TestCase):
    """FR-700: no LLM SDK on the clinical / report path (CI grep is the other gate)."""

    def test_clinical_and_report_have_no_llm_imports(self) -> None:
        banned = ("openai", "anthropic", "langchain")
        for pkg in ("pce_report", "pce_clinical", "pce_cds", "pce_shadow"):
            root = ROOT / "src" / pkg
            for path in root.rglob("*.py"):
                blob = path.read_text(encoding="utf-8").lower()
                for token in banned:
                    self.assertNotIn(token, blob, msg=str(path))
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.assertTrue(
                                all(token not in alias.name.lower() for token in banned),
                                msg=f"{path} import {alias.name}",
                            )
                    if isinstance(node, ast.ImportFrom) and node.module:
                        self.assertTrue(
                            all(token not in node.module.lower() for token in banned),
                            msg=f"{path} from {node.module}",
                        )


class DeferredFrTests(unittest.TestCase):
    """P1/P2 items that the spec names and the plan parks. Not implemented — asserted absent."""

    def test_fr_230_no_hl7_v2_parser(self) -> None:
        """FR-230 HL7 v2 LRI is P1 deferred."""
        for path in (ROOT / "src").rglob("*.py"):
            blob = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("hl7 v2", blob, msg=str(path))
            self.assertNotIn("hl7v2", blob, msg=str(path))

    def test_fr_430_prs_interface_not_built(self) -> None:
        """FR-430 PRS is P2 / not built: no /prs/score route."""
        tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        tmp.close()
        svc = ClinicalService(ClinicalStore(tmp.name))
        status, _body, _ctype = handle_request(svc, "POST", "/prs/score", {}, b"{}")
        self.assertEqual(status, 404)

    def test_fr_480_encyclopedia_view_not_built(self) -> None:
        """FR-480 encyclopedia view is P1 deferred."""
        tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        tmp.close()
        svc = ClinicalService(ClinicalStore(tmp.name))
        status, _body, _ctype = handle_request(svc, "GET", "/encyclopedia", {}, b"")
        self.assertEqual(status, 404)
        self.assertFalse(hasattr(ClinicalService, "encyclopedia"))

    def test_fr_510_report_regen_not_built(self) -> None:
        """FR-510 guideline-refresh regeneration is P1 deferred."""
        self.assertFalse(hasattr(ClinicalService, "regenerate_report"))
        self.assertFalse(hasattr(ClinicalService, "rebuild_report"))

    def test_fr_540_patient_copy_endpoint_not_built(self) -> None:
        """FR-540 patient-copy report is P1 (OQ-13). Gene omit is FR-110, not this."""
        tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        tmp.close()
        svc = ClinicalService(ClinicalStore(tmp.name))
        status, _body, _ctype = handle_request(
            svc, "GET", "/v1/cases/x/reports/y/patient-copy", {}, b""
        )
        self.assertEqual(status, 404)

    def test_fr_600_alert_telemetry_not_built(self) -> None:
        """FR-600 alert-fatigue / override telemetry is P1 deferred."""
        self.assertFalse(hasattr(ClinicalService, "record_override"))
        src_blob = "\n".join(
            p.read_text(encoding="utf-8") for p in (ROOT / "src").rglob("*.py")
        )
        self.assertNotIn("alert_fatigue", src_blob)


class FallenGtmRecordTests(unittest.TestCase):
    """A16/A17: original phase-1 speed rationale and ZK/local-first fell. Stay on the record."""

    def test_spec_has_a16_a17_rows(self) -> None:
        spec = SPEC.read_text(encoding="utf-8")
        self.assertIn("| A16 |", spec)
        self.assertIn("| A17 |", spec)
        self.assertIn("longevity / biohacking", spec)
        self.assertIn("Zero-Knowledge / local-first", spec)
        self.assertIn("elesett", spec)
        self.assertIn("### 0.2 Elesett eredeti GTM és architektúra (A16, A17)", spec)

    def test_sku_and_buyers_records_fallen_longevity(self) -> None:
        sku = (ROOT / "docs" / "pce" / "Sales" / "sku-and-buyers.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("A16", sku)
        self.assertIn("longevity", sku.lower())
        self.assertIn("biohacking", sku.lower())
        self.assertIn("elesett", sku)
        self.assertIn("A17", sku)
        self.assertIn("Zero-Knowledge", sku)

    def test_src_has_no_zero_knowledge_or_local_first(self) -> None:
        for path in (ROOT / "src").rglob("*.py"):
            blob = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("zero-knowledge", blob, msg=str(path))
            self.assertNotIn("zero knowledge", blob, msg=str(path))
            self.assertNotIn("local-first", blob, msg=str(path))
            self.assertNotIn("local first", blob, msg=str(path))


if __name__ == "__main__":
    unittest.main()
