#!/usr/bin/env python3
"""OQ-05 protocol generator: evidence pack from unittest, not a seal."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs" / "pce" / "ProcessArtifacts" / "BuildScripts" / "generate_oq05_protocol.py"
SEND_SCRIPT = ROOT / "docs" / "pce" / "ProcessArtifacts" / "BuildScripts" / "generate_oq05_send_pack.py"
PROTOCOL = ROOT / "docs" / "pce" / "ProcessArtifacts" / "OQ-05-TEST-PROTOCOL.md"
BRIEF = ROOT / "docs" / "pce" / "Outbound" / "OQ-05-counsel-brief.md"
TERVEZET = ROOT / "docs" / "pce" / "Outbound" / "OQ-05-feltetellel-tervezet.md"
SEND_PACK = ROOT / "docs" / "pce" / "Outbound" / "OQ-05-SEND-PACK.md"
GOLD = ROOT / "tests" / "fixtures" / "f1plus-v0" / "outside-call-cyp2d6-called.json"


def _mod():
    spec = importlib.util.spec_from_file_location("generate_oq05_protocol", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _send_mod():
    spec = importlib.util.spec_from_file_location("generate_oq05_send_pack", SEND_SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Oq05CounselSendPackTests(unittest.TestCase):
    """Counsel-csomag hivatkozásai léteznek; V. üres. Nem pecsét; nem Class I QMS."""

    def test_outbound_listed_paths_exist(self) -> None:
        listed = (
            ROOT / "docs" / "pce" / "Outbound" / "OQ-05-counsel-brief.md",
            ROOT / "docs" / "pce" / "Outbound" / "OQ-05-feltetellel-tervezet.md",
            ROOT / "docs" / "pce" / "Outbound" / "OQ-05-SEND-PACK.md",
            ROOT / "docs" / "pce" / "Outbound" / "README.md",
            ROOT / "docs" / "pce" / "A-intended-purpose-and-modules.md",
            ROOT / "docs" / "pce" / "D-risk-and-traceability.md",
            ROOT / "docs" / "pce" / "F-decision-package.md",
            ROOT / "docs" / "pce" / "G-open-items.md",
            ROOT / "docs" / "pce" / "PCE-SPEC-v1.2.md",
            ROOT / "docs" / "pce" / "ProcessArtifacts" / "OQ-05-TEST-PROTOCOL.md",
            ROOT / "docs" / "pce" / "ProcessArtifacts" / "SOURCE-REGISTRY.md",
            ROOT / "docs" / "pce" / "ProcessArtifacts" / "BuildScripts" / "generate_oq05_protocol.py",
            ROOT / "docs" / "pce" / "ProcessArtifacts" / "BuildScripts" / "generate_oq05_send_pack.py",
            ROOT / "docs" / "pce" / "Sources" / "official" / "fetch_software_ready_pins.py",
            ROOT / "docs" / "pce" / "Sources" / "official" / "com-2025-1023-act.pdf",
            ROOT / "docs" / "pce" / "Sources" / "official" / "eur-lex-com-2025-1023.html",
            ROOT / "src" / "pce_report" / "schema.py",
            ROOT / "src" / "pce_report" / "render.py",
            ROOT / "src" / "pce_cds" / "policy.py",
            ROOT / "src" / "pce_shadow" / "f5_rec.py",
            ROOT / "src" / "pce_clinical" / "pharmcat.py",
            ROOT / "tests" / "test_report.py",
            ROOT / ".github" / "workflows" / "ci.yml",
            GOLD,
        )
        missing = [str(p.relative_to(ROOT)) for p in listed if not p.is_file()]
        self.assertEqual(missing, [])

    def test_brief_does_not_freeze_suite_size_as_igen_argument(self) -> None:
        brief = BRIEF.read_text(encoding="utf-8")
        self.assertNotIn("250 teszt", brief)
        self.assertNotIn("251 teszt", brief)
        self.assertIn("A unittest-suite mérete **nem** IGEN", brief)
        self.assertIn("tests/fixtures/f1plus-v0/outside-call-cyp2d6-called.json", brief)
        self.assertNotIn("példa-lelet", brief)
        self.assertNotIn("E-31/HGVS", brief)
        self.assertIn("G §3.4", brief)
        self.assertIn("Q3-claim **10** unittest-id", brief)
        self.assertIn("OQ-05-SEND-PACK.md", brief)
        self.assertIn("MATCHER_ON is False", brief)
        self.assertIn("IIA_SAFE_BLOCK is True", brief)
        self.assertRegex(brief, r"- \[ \] \*\*IGEN\*\*")
        self.assertRegex(brief, r"- \[ \] \*\*NEM\*\*")
        self.assertRegex(brief, r"- \[ \] \*\*FELTÉTELLEL\*\*")
        self.assertNotIn("- [x] **IGEN**", brief)
        self.assertNotIn("- [x] **NEM**", brief)
        self.assertNotIn("- [x] **FELTÉTELLEL**", brief)

    def test_gold_fixture_is_unsigned_json_not_pdf(self) -> None:
        self.assertTrue(GOLD.is_file())
        self.assertFalse(GOLD.with_suffix(".pdf").is_file())
        payload = json.loads(GOLD.read_text(encoding="utf-8"))
        self.assertEqual(payload["gene"], "CYP2D6")
        self.assertEqual(payload["method"], "outside-call")

    def test_tervezet_send_gate_is_citation_not_reg030(self) -> None:
        text = TERVEZET.read_text(encoding="utf-8")
        self.assertIn("test_outbound_listed_paths_exist", text)
        self.assertIn("REG-030", text)
        self.assertIn("**nem** küldési feltétel", text)
        self.assertIn("kezdeti", text)
        self.assertIn("REG-010", text)
        self.assertIn("OQ-05-SEND-PACK.md", text)
        self.assertNotIn("OQ-05 LEZÁRVA", text)

    def test_g_q1_points_to_gold_fixture(self) -> None:
        g = (ROOT / "docs" / "pce" / "G-open-items.md").read_text(encoding="utf-8")
        self.assertIn("tests/fixtures/f1plus-v0/outside-call-cyp2d6-called.json", g)
        self.assertNotIn("példa-lelet", g)
        self.assertIn("mapped evidenciatábla **51**", g)
        self.assertIn("Q3 **10**", g)
        self.assertIn("REG-030 **nem** az OQ-05 counsel-küldés előfeltétele", g)

    def test_ci_freezes_iia_safe_block(self) -> None:
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("IIA_SAFE_BLOCK", ci)
        self.assertIn("assert IIA_SAFE_BLOCK is True", ci)

    def test_send_pack_committed_matches_generator(self) -> None:
        gen = _send_mod()
        self.assertEqual(SEND_PACK.read_text(encoding="utf-8"), gen.render("2026-08-16"))

    def test_send_pack_hashes_match_bytes(self) -> None:
        gen = _send_mod()
        recs = gen.records()
        self.assertEqual(len(recs), len(gen.PACK_ITEMS))
        ids = {r.item.pack_id for r in recs}
        self.assertEqual(ids, {"COVER", "FELT", "SPEC", "REG-010", "F1", "G", "D1", "PROTOCOL", "REGISTRY", "GOLD", "TEST-REPORT", "SCHEMA", "CI", "S077", "S080"})
        for rec in recs:
            blob = (ROOT / rec.item.relpath).read_bytes()
            self.assertEqual(rec.size, len(blob))
            self.assertEqual(rec.sha256, hashlib.sha256(blob).hexdigest())
            self.assertNotEqual(rec.item.relpath, "docs/pce/Outbound/OQ-05-SEND-PACK.md")

    def test_send_pack_is_not_a_seal_and_names_handover_files(self) -> None:
        text = SEND_PACK.read_text(encoding="utf-8")
        self.assertIn("**Átadás-átvételi boríték — nem pecsét.**", text)
        self.assertIn("Csomag-ujjlenyomat", text)
        self.assertIn("REG-010", text)
        self.assertIn("tests/fixtures/f1plus-v0/outside-call-cyp2d6-called.json", text)
        self.assertIn("docs/pce/D-risk-and-traceability.md", text)
        self.assertIn("docs/pce/Outbound/OQ-05-feltetellel-tervezet.md", text)
        self.assertIn("Mapped 51 egyedi teszt; Q3 = 10", text)
        self.assertNotIn("OQ-05 LEZÁRVA", text)
        self.assertNotIn("- [x]", text)
        self.assertNotIn("E-31/HGVS", text)
        self.assertIn("saját SHA-256-ját nem tartalmazza", text)
        self.assertIn("Aláírt példa-lelet PDF", text)
        self.assertIn("REG-030 QMS fájl", text)
        self.assertIn("nem COM-mentesség", text)
        gold_pdf = GOLD.with_suffix(".pdf")
        self.assertFalse(gold_pdf.is_file())


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

    def test_mapped_unique_and_q3_count_are_classification_evidence(self) -> None:
        self.assertEqual(len(self.gen.mapped_ids()), 51)
        scopes = {c.claim_id: c.software_scope for c in self.gen.CLAIMS}
        self.assertEqual(scopes["Q1"], "partial")
        self.assertEqual(scopes["Q2"], "partial")
        self.assertEqual(scopes["Q3"], "yes")
        self.assertEqual(scopes["Q4"], "partial")
        self.assertEqual(scopes["III.1"], "yes")
        self.assertEqual(scopes["III.2"], "partial")
        self.assertEqual(scopes["III.3"], "partial")
        self.assertEqual(scopes["III.4"], "yes")
        self.assertEqual(scopes["III.5"], "yes")
        self.assertEqual(scopes["III.6"], "yes")
        q3 = next(c for c in self.gen.CLAIMS if c.claim_id == "Q3")
        self.assertEqual(len(q3.tests), 10)

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
        self.assertIn("suite méret **nem** IGEN pecsét", text)
        self.assertIn("R-OPS-01", text)
        self.assertIn("R-OPS-02", text)
        self.assertIn("nem pecsét-feloldó", text)
        self.assertIn("Nem outside-call, nem HGVS", text)
        self.assertIn("D-57", text)
        self.assertIn("REG-030", text)
        self.assertIn("Oq05CounselSendPackTests", text)
        self.assertIn("D-58", text)
        self.assertIn("OQ-05-SEND-PACK.md", text)

    def test_feltetellel_tervezet_is_not_a_seal(self) -> None:
        path = ROOT / "docs" / "pce" / "Outbound" / "OQ-05-feltetellel-tervezet.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("**Nem** pecsét", text)
        self.assertIn("LIVE_CDS=false", text)
        self.assertIn("MATCHER_ON=false", text)
        self.assertIn("IIA_SAFE_BLOCK=true", text)
        self.assertIn("R-OPS-01", text)
        self.assertIn("R-OPS-02", text)
        self.assertIn("A unittest-suite mérete **nem** IGEN pecsét", text)
        self.assertIn("A két ops-kockázat **nem** NEM pecsét", text)
        self.assertNotIn("OQ-05 LEZÁRVA", text)
        self.assertNotIn("- [x]", text)
        self.assertNotIn("E-31/HGVS", text)
        self.assertIn("45 → 47", text)
        self.assertIn("Class I MDSW", text)
        self.assertIn("REG-030", text)
        self.assertIn("**nem** küldési feltétel", text)
        self.assertIn("test_outbound_listed_paths_exist", text)
        self.assertIn("OQ-05-SEND-PACK.md", text)

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
