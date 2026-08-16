#!/usr/bin/env python3
"""OQ-05 protocol generator: evidence pack from unittest, not a seal."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs" / "pce" / "ProcessArtifacts" / "BuildScripts" / "generate_oq05_protocol.py"
PROTOCOL = ROOT / "docs" / "pce" / "ProcessArtifacts" / "OQ-05-TEST-PROTOCOL.md"
BRIEF = ROOT / "docs" / "pce" / "Outbound" / "OQ-05-counsel-brief.md"


def _mod():
    spec = importlib.util.spec_from_file_location("generate_oq05_protocol", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Oq05ProtocolGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gen = _mod()
        cls.inventory = cls.gen.discover_tests()
        cls.flags = cls.gen.flags()

    def test_script_and_protocol_exist(self) -> None:
        self.assertTrue(SCRIPT.is_file())
        self.assertTrue(PROTOCOL.is_file())

    def test_every_mapped_id_exists_in_ast(self) -> None:
        missing = [tid for tid in self.gen.mapped_ids() if tid not in self.inventory]
        self.assertEqual(missing, [])

    def test_delta_195_241_has_46_and_all_exist(self) -> None:
        delta = self.gen.DELTA_195_241
        self.assertEqual(len(delta), 46)
        missing = [tid for _r, _k, tid in delta if tid not in self.inventory]
        self.assertEqual(missing, [])

    def test_repo_locks_are_the_compile_time_values(self) -> None:
        self.assertIs(self.flags["LIVE_CDS"], False)
        self.assertIs(self.flags["GATEWAY_LIVE_CDS"], False)
        self.assertIs(self.flags["MATCHER_ON"], False)
        self.assertIs(self.flags["IIA_SAFE_BLOCK"], True)
        self.assertEqual(self.flags["ALLOWED_B41"], 47)
        self.assertEqual(self.flags["FORBIDDEN_B41"], 15)

    def test_brief_q1_allow_list_matches_schema(self) -> None:
        cited = self.gen.brief_allowed_cite()
        self.assertEqual(cited, self.flags["ALLOWED_B41"])
        self.assertIn("ALLOWED_B41_TOP_LEVEL` = 47", BRIEF.read_text(encoding="utf-8"))

    def test_generated_text_is_not_a_seal(self) -> None:
        text = self.gen.render("2026-08-16", run_mapped=False)
        self.assertIn("ELŐTERJESZTVE — nem pecsét", text)
        self.assertIn("Nem counsel-állásfoglalás", text)
        self.assertIn("LIVE_CDS", text)
        self.assertIn("`false`", text)
        self.assertIn("IIA_SAFE_BLOCK", text)
        self.assertIn("`true`", text)
        self.assertIn("fail-open", text)
        self.assertIn("PCE_PHARMCAT_OFFLINE=1", text)
        self.assertIn("195 → 241", text)
        for tok in self.gen.SEAL_FORBIDDEN:
            self.assertNotIn(tok, text)

    def test_q2_is_partial_and_q4_does_not_unlock_flags(self) -> None:
        text = self.gen.render("2026-08-16", run_mapped=False)
        self.assertIn("szoftver nem minősít", text)
        self.assertIn("LIVE_CDS ettől nem billen", text)
        self.assertIn("Nem tölti ki az OQ-05 V. szakasz", text)

    def test_committed_protocol_matches_generator(self) -> None:
        expected = self.gen.render("2026-08-16", run_mapped=True)
        actual = PROTOCOL.read_text(encoding="utf-8")
        self.assertEqual(actual, expected)

    def test_mapped_tests_run_ok(self) -> None:
        results = self.gen.run_ids(self.gen.mapped_ids())
        failed = {tid: st for tid, st in results.items() if st != "OK"}
        self.assertEqual(failed, {})


if __name__ == "__main__":
    unittest.main()
