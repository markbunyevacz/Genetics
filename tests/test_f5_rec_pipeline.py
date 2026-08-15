#!/usr/bin/env python3
"""F5 rec_view ingest is data-agnostic: mock now, live later, prod off.

Mock is not a published CPIC recommendation. Signed F1+ lelet still has 0 rec rows.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pce_clinical.pharmcat import PharmcatError, ensure_jar  # noqa: E402
from pce_clinical.server import bind_clinical_server  # noqa: E402
from pce_clinical.star_call import call_star_alleles  # noqa: E402
from pce_report.flags import MATCHER_ON  # noqa: E402
from pce_report.guidelines import prepare12_table  # noqa: E402
from pce_report.render import RendererConfigError, render_f1plus  # noqa: E402
from pce_report.schema import assemble_b41  # noqa: E402
from pce_shadow.engine import infer  # noqa: E402
from pce_shadow.f5_rec import (  # noqa: E402
    F5_ATC5,
    F5_SCHEMA_PATH,
    MOCK_PATH,
    F5DataProvider,
    F5Source,
    LiveF5Provider,
    MockF5Provider,
    OffF5Provider,
    apply_f5_source,
    classify_recommendation,
    provider_for,
    resolve_source,
    transform_rows,
    validate_rec_view_row,
)
from pce_shadow.table import KnowledgeTable  # noqa: E402

GOLD = ROOT / "tests" / "fixtures" / "vcf-gold-v0"
EXTRA = ROOT / "tests" / "fixtures" / "shadow-v0" / "prepare12-rec-pairings.v0.json"
BUILDER = ROOT / "docs" / "pce" / "Sources" / "official" / "build_prepare12_live_pairings.py"


def _infer_with(table: KnowledgeTable, gene: str, diplotype: str, atc: str) -> dict:
    return infer(
        {
            "diplotypes": [{"gene": gene, "diplotype": diplotype, "callability": "CALLED"}],
            "medications": [{"system": "http://www.whocc.no/atc", "code": atc}],
        },
        table=table,
    )


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_prepare12_live_pairings", BUILDER)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class F5SchemaTests(unittest.TestCase):
    def test_schema_file_exists(self) -> None:
        self.assertTrue(F5_SCHEMA_PATH.is_file())
        schema = json.loads(F5_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "pce-cpic-f5-recommendation-view")
        self.assertIn("lookupkey", schema["properties"])
        self.assertEqual(schema["properties"]["lookupkey"]["type"], ["object", "null"])

    def test_mock_fixture_validates(self) -> None:
        payload = json.loads(MOCK_PATH.read_text(encoding="utf-8"))
        self.assertTrue(payload["mocked"])
        self.assertEqual(payload["atc5"], "G03AA07")
        self.assertEqual(len(payload["rows"]), 4)
        for row in payload["rows"]:
            validate_rec_view_row(row)
        comments = " ".join(str(r.get("comments") or "") for r in payload["rows"])
        self.assertIn("Not CPIC published", comments)
        lookup_vals = [r["lookupkey"]["F5"] for r in payload["rows"]]
        self.assertIn("Leiden/Leiden", lookup_vals)
        self.assertIn("heterozygous", lookup_vals)

    def test_null_f5_lookup_is_valid_but_skipped(self) -> None:
        row = {
            "recommendationid": 1,
            "drugid": "RxNorm:203159",
            "guidelineid": 12,
            "lookupkey": {"F5": None, "CYP2C9": "*1/*1"},
            "phenotype": "x",
            "implication": "x",
            "recommendation": "Avoid estrogen-containing contraceptives.",
            "comments": "x",
        }
        validate_rec_view_row(row)
        pairings, dips, labels = transform_rows([row], mocked=True)
        self.assertEqual(pairings, [])
        self.assertEqual(dips, [])
        self.assertEqual(labels, {})

    def test_classify_avoid_and_continue(self) -> None:
        self.assertEqual(
            classify_recommendation("Avoid estrogen-containing contraceptives."),
            "CONSIDER_ALTERNATIVE",
        )
        self.assertEqual(
            classify_recommendation("No genotype-based change. Continue therapy."),
            "CONTINUE",
        )


class F5ProviderSwitchTests(unittest.TestCase):
    def test_default_source_is_off(self) -> None:
        self.assertIs(resolve_source(None), F5Source.DISABLED)
        self.assertEqual(resolve_source(None).value, "off")
        self.assertEqual(OffF5Provider().rows(), [])
        self.assertEqual(len(MockF5Provider().rows()), 4)

    def test_prod_table_has_no_f5_pairing(self) -> None:
        table = KnowledgeTable()
        self.assertEqual(table.f5_source, "off")
        self.assertIsNone(table.pairing("F5", F5_ATC5))
        self.assertIsNone(table.pairing("F5", "B01AA03"))

    def test_mock_source_loads_het_and_wt(self) -> None:
        table = KnowledgeTable(f5_source="mock")
        pair = table.pairing("F5", F5_ATC5)
        self.assertIsNotNone(pair)
        assert pair is not None
        self.assertTrue(pair["mocked"])
        self.assertEqual(pair["source_id"], "CPIC-F5-MOCK")
        self.assertEqual(pair["by_phenotype"]["HET"], "CONSIDER_ALTERNATIVE")
        self.assertEqual(pair["by_phenotype"]["WT"], "CONTINUE")
        self.assertEqual(pair["by_phenotype"]["HOM"], "CONSIDER_ALTERNATIVE")
        self.assertNotIn("dose_mg", pair)
        van = " ".join(row["hu"] for row in table.inventory.get("van") or [])
        self.assertIn("MOCK", van)
        self.assertIn("nem hivatalos cpic", van.lower())

    def test_mock_does_not_overwrite_index_pairs(self) -> None:
        table = KnowledgeTable(f5_source="mock")
        px = table.pairing("CYP2D6", "N06AB05")
        self.assertIsNotNone(px)
        assert px is not None
        self.assertEqual(px["source_id"], "CPIC-SSRI-2023")
        self.assertEqual(px["inn"], "paroxetine")
        clop = table.pairing("CYP2C19", "B01AC04")
        self.assertIsNotNone(clop)
        assert clop is not None
        self.assertEqual(clop["inn"], "clopidogrel")

    def test_live_empty_fetch_adds_nothing(self) -> None:
        table = KnowledgeTable(f5_source="live", f5_fetch=lambda: [])
        self.assertEqual(table.f5_source, "live")
        self.assertIsNone(table.pairing("F5", F5_ATC5))

    def test_infer_mock_het_positive(self) -> None:
        table = KnowledgeTable(f5_source="mock")
        out = _infer_with(table, "F5", "heterozygous", F5_ATC5)
        self.assertEqual(len(out["live_findings"]), 1)
        self.assertEqual(out["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")
        self.assertEqual(out["genotype_phenotype"][0]["genotype_phenotype"], "HET")
        self.assertNotIn("dose_mg", json.dumps(out))
        self.assertTrue(out["live_findings"][0]["source_id"].endswith("MOCK"))
        hom = _infer_with(table, "F5", "Leiden/Leiden", F5_ATC5)
        self.assertEqual(hom["genotype_phenotype"][0]["genotype_phenotype"], "HOM")
        self.assertEqual(hom["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")

    def test_infer_mock_wt_negative(self) -> None:
        table = KnowledgeTable(f5_source="mock")
        out = _infer_with(table, "F5", "WT/WT", F5_ATC5)
        self.assertEqual(out["live_findings"][0]["strategy_category"], "CONTINUE")
        self.assertEqual(out["genotype_phenotype"][0]["genotype_phenotype"], "WT")

    def test_infer_off_no_finding(self) -> None:
        table = KnowledgeTable(f5_source="off")
        out = _infer_with(table, "F5", "heterozygous", F5_ATC5)
        self.assertEqual(out["live_findings"], [])

    def test_env_mock_switch(self) -> None:
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {"CPIC_F5_SOURCE": "MOCK"}):
            table = KnowledgeTable()
            self.assertEqual(table.f5_source, "mock")
            self.assertIsNotNone(table.pairing("F5", F5_ATC5))


class F5DoesNotLeakOntoSignedLeletTests(unittest.TestCase):
    def test_f1_plus_f5_still_has_no_guideline_row(self) -> None:
        report = render_f1plus(
            outside_call={
                "gene": "F5",
                "diplotype": "rs6025 het",
                "callability": "CALLED",
                "case_display_id": "SYN-CASE-F5-MOCK",
            },
            table=prepare12_table(),
        )
        self.assertEqual(report["guideline_row_count"], 0)
        blob = json.dumps(report)
        self.assertNotIn("Avoid estrogen", blob)
        self.assertNotIn("pce_shadow", blob)
        self.assertNotIn("CPIC-F5-MOCK", blob)
        self.assertIn("recommendation_view", " ".join(report["hianyzik"]))


class RecViewAndWarfarinChecklistTests(unittest.TestCase):
    def test_index_paroxetine_not_in_extra_json(self) -> None:
        extra = json.loads(EXTRA.read_text(encoding="utf-8"))
        keys = {(p["gene"], p["atc5"]) for p in extra["pairings"]}
        self.assertNotIn(("CYP2D6", "N06AB05"), keys)
        self.assertNotIn(("CYP2C19", "B01AC04"), keys)
        self.assertNotIn(("CYP2D6", "N06AB03"), keys)
        self.assertNotIn(("HLA-B", "J05AF06"), keys)
        self.assertNotIn(("UGT1A1", "J05AE08"), keys)
        self.assertNotIn("dose_mg", json.dumps(extra))

    def test_builder_skip_protects_index_pairs(self) -> None:
        mod = _load_builder()
        self.assertIsInstance(mod.SKIP, frozenset)
        self.assertIn(("CYP2D6", "paroxetine"), mod.SKIP)
        self.assertIn(("CYP2C19", "clopidogrel"), mod.SKIP)
        self.assertIn(("HLA-B", "abacavir"), mod.SKIP)
        self.assertIn(("UGT1A1", "atazanavir"), mod.SKIP)
        table = KnowledgeTable()
        self.assertEqual(table.pairing("CYP2D6", "N06AB05")["source_id"], "CPIC-SSRI-2023")

    def test_warfarin_cyp2c9_star2_star3_is_alternative(self) -> None:
        out = infer(
            {
                "diplotypes": [
                    {"gene": "CYP2C9", "diplotype": "*2/*3", "callability": "CALLED"},
                    {"gene": "VKORC1", "diplotype": "-1639G/-1639G", "callability": "CALLED"},
                ],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "B01AA03"}],
            }
        )
        self.assertEqual(len(out["live_findings"]), 1)
        self.assertEqual(out["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")
        self.assertEqual(out["live_findings"][0]["source_id"], "CPIC-WARFARIN-2017")
        self.assertNotIn("dose_mg", json.dumps(out))

    def test_warfarin_cyp2c9_alone_no_finding(self) -> None:
        out = infer(
            {
                "diplotypes": [
                    {"gene": "CYP2C9", "diplotype": "*2/*3", "callability": "CALLED"},
                ],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "B01AA03"}],
            }
        )
        self.assertEqual(out["live_findings"], [])
        self.assertEqual(out["warfarin_eval"]["status"], "MISSING_GENETIC_DATA")
        self.assertEqual(out["warfarin_eval"]["missing"], ["VKORC1"])


class PharmcatHttpMatcherOnTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        tmp.close()
        self.httpd = bind_clinical_server(tmp.name, port=0)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.httpd.shutdown)
        self.addCleanup(self.httpd.server_close)
        self.port = self.httpd.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"

    def _req(
        self,
        method: str,
        path: str,
        body: dict | bytes | None = None,
        role: str = "lab_signer",
        ctype: str = "application/json",
        timeout: int = 60,
    ) -> tuple[int, dict | bytes]:
        data = None
        headers = {"Authorization": role}
        if isinstance(body, dict):
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif isinstance(body, bytes):
            data = body
            headers["Content-Type"] = ctype
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                if resp.headers.get_content_type() == "application/json":
                    return resp.status, json.loads(raw.decode("utf-8"))
                return resp.status, raw
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                return e.code, raw

    def test_files_query_matcher_on_true(self) -> None:
        self.assertFalse(MATCHER_ON)
        gold = GOLD / "called-cyp2d6-star4-hom.vcf"
        if not gold.is_file():
            self.skipTest("gold VCF missing")
        status, org = self._req(
            "POST", "/v1/orgs", {"name": "SYN-ORG-001", "license_id": "SYN-LIC-001", "role": "lab"}
        )
        self.assertEqual(status, 201)
        assert isinstance(org, dict)
        status, sub = self._req("POST", "/v1/subjects", {"org_id": org["id"]})
        assert isinstance(sub, dict)
        status, case = self._req(
            "POST",
            "/v1/cases",
            {
                "org_id": org["id"],
                "subject_id": sub["id"],
                "sample": {"collected_at": "2026-08-10", "type": "blood", "origin": "SYN-LAB-001"},
            },
        )
        self.assertEqual(status, 201)
        assert isinstance(case, dict)
        self._req(
            "POST",
            f"/v1/cases/{case['id']}/counselling",
            {"counsellor_id": "SYN-MD-001", "occurred_at": "2026-08-09"},
            role="counsellor",
        )
        self._req(
            "POST",
            f"/v1/cases/{case['id']}/consent",
            {"granted_at": "2026-08-09", "scopes": ["pgx_report"]},
            role="counsellor",
        )
        status, stored = self._req(
            "POST",
            f"/v1/cases/{case['id']}/files?matcher_on=true",
            gold.read_bytes(),
            ctype="text/plain",
        )
        self.assertEqual(status, 201)
        assert isinstance(stored, dict)
        self.assertTrue(stored["matcher_on"])
        cov = {row["gene"]: row for row in stored["coverage"]}
        self.assertEqual(cov["CYP2D6"]["diplotype"], "*4/*4")
        self.assertEqual(cov["CYP2D6"]["callability"], "CALLED")
        self.assertEqual(cov["CYP2C9"]["diplotype"], "*4/*4")
        self.assertEqual(cov["CYP2C9"]["callability"], "CALLED")
        self.assertEqual(cov["HLA-B"]["callability"], "NOT_TESTED")
        self.assertEqual(stored["pharmcat_version"], "3.4.0")
        self.assertTrue(stored["pharmvar_version"])
        self.assertTrue(stored["cpic_data_version"])
        self.assertFalse(MATCHER_ON)


class RepoConformHardeningTests(unittest.TestCase):
    def test_f5_source_invalid_token_throws(self) -> None:
        with self.assertRaises(ValueError):
            resolve_source("prod")
        with self.assertRaises(ValueError):
            resolve_source("yes")
        with patch.dict(os.environ, {"CPIC_F5_SOURCE": "bogus"}):
            with self.assertRaises(ValueError):
                KnowledgeTable()

    def test_f5_empty_recommendation_skipped(self) -> None:
        row = {
            "recommendationid": 1,
            "drugid": "RxNorm:203159",
            "guidelineid": 12,
            "lookupkey": {"F5": "heterozygous"},
            "phenotype": "Factor V Leiden Heterozygote",
            "recommendation": "",
            "comments": "empty rec must skip",
        }
        validate_rec_view_row(row)
        pairings, dips, labels = transform_rows([row], mocked=True)
        self.assertIsNone(classify_recommendation(""))
        self.assertEqual(pairings, [])
        self.assertEqual(dips, [])
        self.assertEqual(labels, {})

    def test_f5_empty_array_does_not_crash(self) -> None:
        pairings, dips, labels = transform_rows([], mocked=True)
        self.assertEqual(pairings, [])
        self.assertEqual(dips, [])
        self.assertEqual(labels, {})
        table = KnowledgeTable(f5_source="live", f5_fetch=lambda: [])
        self.assertEqual(table.f5_source, "live")
        self.assertIsNone(table.pairing("F5", F5_ATC5))
        out = _infer_with(table, "F5", "heterozygous", F5_ATC5)
        self.assertEqual(out["live_findings"], [])

    def test_f5_live_non_dict_row_fails_fast(self) -> None:
        with self.assertRaises(ValueError):
            validate_rec_view_row(["not-a-dict"])
        with self.assertRaises(ValueError):
            KnowledgeTable(f5_source="live", f5_fetch=lambda: ["not-a-dict"])
        with self.assertRaises(ValueError):
            KnowledgeTable(f5_source="live", f5_fetch=lambda: {"rows": []})

    def test_index_pair_overwrite_throws_exception(self) -> None:
        table = KnowledgeTable()
        with self.assertRaises(ValueError):
            table.add_pairing(
                {"gene": "CYP2D6", "atc5": "N06AB05", "inn": "paroxetine"},
                source="overwrite-test",
            )
        with self.assertRaises(ValueError):
            table.add_pairing(
                {"gene": "CYP2C19", "atc5": "B01AC04", "inn": "clopidogrel"},
                source="overwrite-test",
            )
        self.assertEqual(table.pairing("CYP2D6", "N06AB05")["source_id"], "CPIC-SSRI-2023")
        self.assertEqual(table.pairing("CYP2C19", "B01AC04")["inn"], "clopidogrel")

    def test_atc_dict_keys_valid_format(self) -> None:
        mod = _load_builder()
        self.assertIsInstance(mod.SKIP, frozenset)
        for key, val in mod.ATC.items():
            code = val[0] if isinstance(val, tuple) else val
            self.assertRegex(code, r"^[A-Z][0-9]{2}[A-Z]{2}[0-9]{2}$")
            self.assertEqual(len(code), 7)
        mod.validate_atc_dict()
        with self.assertRaises(ValueError):
            mod.validate_atc_dict({("CYP2D6", "bad"): ("N06AB", "x")})

    def test_warfarin_full_matrix_parametric(self) -> None:
        vkor_any = (
            "-1639G/-1639G",
            "-1639G/-1639A",
            "-1639A/-1639A",
            "rs9923231 reference (C)/rs9923231 reference (C)",
        )
        war = [{"system": "http://www.whocc.no/atc", "code": "B01AA03"}]
        for cyp in ("*2/*3", "*3/*3"):
            for vkor in vkor_any:
                with self.subTest(cyp=cyp, vkor=vkor):
                    out = infer(
                        {
                            "diplotypes": [
                                {"gene": "CYP2C9", "diplotype": cyp, "callability": "CALLED"},
                                {"gene": "VKORC1", "diplotype": vkor, "callability": "CALLED"},
                            ],
                            "medications": war,
                        }
                    )
                    self.assertEqual(len(out["live_findings"]), 1)
                    self.assertEqual(out["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")
                    self.assertNotIn("dose_mg", json.dumps(out))
        gg_aliases = (
            "-1639G/-1639G",
            "rs9923231 reference (C)/rs9923231 reference (C)",
        )
        dose_change_cases = (
            ("*1/*1", "-1639A/-1639A"),
            ("*1/*2", "-1639G/-1639G"),
        )
        for cyp, vkor in dose_change_cases:
            with self.subTest(branch="dose_change", cyp=cyp, vkor=vkor):
                out = infer(
                    {
                        "diplotypes": [
                            {"gene": "CYP2C9", "diplotype": cyp, "callability": "CALLED"},
                            {"gene": "VKORC1", "diplotype": vkor, "callability": "CALLED"},
                        ],
                        "medications": war,
                    }
                )
                self.assertEqual(out["live_findings"][0]["strategy_category"], "CONSIDER_DOSE_CHANGE")
                self.assertEqual(out["warfarin_eval"]["status"], "OK")
                self.assertNotIn("dose_mg", json.dumps(out))
        for vkor in gg_aliases:
            with self.subTest(branch="dose_change", vkor=vkor):
                out = infer(
                    {
                        "diplotypes": [
                            {"gene": "CYP2C9", "diplotype": "*1/*2", "callability": "CALLED"},
                            {"gene": "VKORC1", "diplotype": vkor, "callability": "CALLED"},
                        ],
                        "medications": war,
                    }
                )
                self.assertEqual(out["live_findings"][0]["strategy_category"], "CONSIDER_DOSE_CHANGE")
        missing_cases = (
            [{"gene": "CYP2C9", "diplotype": "*2/*3", "callability": "CALLED"}],
            [{"gene": "VKORC1", "diplotype": "-1639G/-1639G", "callability": "CALLED"}],
            [],
        )
        for dips in missing_cases:
            with self.subTest(missing=dips):
                out = infer({"diplotypes": dips, "medications": war})
                self.assertEqual(out["live_findings"], [])
                self.assertEqual(out["warfarin_eval"]["status"], "MISSING_GENETIC_DATA")
                self.assertTrue(out["warfarin_eval"]["missing"])

    def test_ensure_jar_offline_missing_raises(self) -> None:
        missing = Path("/tmp/pce-no-such-pharmcat-3.4.0-all.jar")
        with patch.dict(os.environ, {"PCE_PHARMCAT_OFFLINE": "1"}):
            with patch("pce_clinical.pharmcat.jar_path", return_value=missing):
                with patch("pce_clinical.pharmcat.urllib.request.urlopen") as urlopen:
                    with self.assertRaises(PharmcatError):
                        ensure_jar()
                    urlopen.assert_not_called()

    def test_missing_version_metadata_raises_exception(self) -> None:
        engine = render_f1plus(
            outside_call={
                "gene": "CYP2D6",
                "diplotype": "*4/*4",
                "callability": "CALLED",
                "case_display_id": "SYN-CASE-VER",
            },
            table=prepare12_table(),
        )
        engine = dict(engine)
        engine["matcher_on"] = True
        kwargs = dict(
            engine=engine,
            report_id="SYN-RPT-VER",
            case_id="SYN-CASE-VER",
            counselling={"id": "SYN-C", "at": "2026-01-01T00:00:00+00:00", "counsellor_id": "SYN-MD-001"},
            consent_granted_at="2026-01-02T00:00:00+00:00",
            performing_org_license_id="SYN-LIC-001",
            white_label={"org": "SYN-ORG-001", "signer_slot": "SYN-MD-001", "colophon": "Precision Clinical Engine"},
            genes=[
                {
                    "gene": "CYP2D6",
                    "diplotype": "*4/*4",
                    "genotype_phenotype": None,
                    "callability": "CALLED",
                }
            ],
            omit_from_patient=frozenset(),
        )
        with self.assertRaises(RendererConfigError):
            assemble_b41(**kwargs)
        engine["pipeline_version"] = "pce-clinical-v0"
        engine["pharmcat_version"] = "3.4.0"
        engine["pharmvar_version"] = "pinned"
        engine["cpic_data_version"] = "pinned"
        ok = assemble_b41(**kwargs)
        self.assertTrue(ok["matcher_on"])
        engine["pharmvar_version"] = ""
        with self.assertRaises(RendererConfigError):
            assemble_b41(**kwargs)
        engine["pharmvar_version"] = "pinned"
        engine["cpic_data_version"] = None
        with self.assertRaises(RendererConfigError):
            assemble_b41(**kwargs)

    def test_pharmcat_concurrent_requests_isolation(self) -> None:
        self.assertFalse(MATCHER_ON)
        gold = GOLD / "called-cyp2d6-star4-hom.vcf"
        if not gold.is_file():
            self.skipTest("gold VCF missing")
        text = gold.read_text(encoding="utf-8")
        errors: list[BaseException] = []
        results: dict[str, object] = {}
        flags: list[bool] = []

        def run_on() -> None:
            try:
                flags.append(MATCHER_ON)
                results["on"] = call_star_alleles(text, reference="GRCh38", matcher_on=True)
            except BaseException as exc:
                errors.append(exc)

        def run_off() -> None:
            try:
                flags.append(MATCHER_ON)
                results["off"] = call_star_alleles(text, reference="GRCh38", matcher_on=False)
            except BaseException as exc:
                errors.append(exc)

        t_on = threading.Thread(target=run_on)
        t_off = threading.Thread(target=run_off)
        t_on.start()
        t_off.start()
        t_on.join(180)
        t_off.join(180)
        self.assertFalse(t_on.is_alive())
        self.assertFalse(t_off.is_alive())
        self.assertEqual(errors, [])
        on_rows = {r["gene"]: r for r in results["on"]}  # type: ignore[arg-type]
        off_rows = {r["gene"]: r for r in results["off"]}  # type: ignore[arg-type]
        self.assertTrue(on_rows["CYP2D6"]["matcher_on"])
        self.assertFalse(off_rows["CYP2D6"]["matcher_on"])
        self.assertEqual(on_rows["CYP2D6"]["diplotype"], "*4/*4")
        self.assertEqual(on_rows["CYP2C9"]["diplotype"], "*4/*4")
        self.assertIsNone(off_rows["CYP2D6"]["diplotype"])
        self.assertEqual(off_rows["CYP2D6"]["callability"], "NOT_TESTED")
        self.assertFalse(MATCHER_ON)
        self.assertTrue(all(flag is False for flag in flags))

    def test_ci_forbids_live_f5_and_offline_jar(self) -> None:
        yml = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("CPIC_F5_SOURCE", yml)
        self.assertIn("PCE_PHARMCAT_OFFLINE", yml)
        self.assertIn("fetch_software_ready_pins.py --jar-only", yml)
        self.assertIn("actions/setup-java@v4", yml)
        self.assertIn("config/production.env", yml)
        prod = (ROOT / "config" / "production.env").read_text(encoding="utf-8")
        self.assertIn("CPIC_F5_SOURCE=off", prod)
        self.assertNotIn("CPIC_F5_SOURCE=live", prod)
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("var/pharmcat/", gitignore)
        self.assertIn("*.jar", gitignore)

    def test_f5_provider_is_interface_not_http(self) -> None:
        off: F5DataProvider = OffF5Provider()
        mock: F5DataProvider = provider_for(F5Source.MOCK)
        live: F5DataProvider = provider_for(F5Source.LIVE, fetch=lambda: [])
        self.assertIsInstance(off, F5DataProvider)
        self.assertIsInstance(mock, F5DataProvider)
        self.assertIsInstance(live, F5DataProvider)
        self.assertEqual(off.rows(), [])
        self.assertGreater(len(mock.rows()), 0)
        self.assertEqual(live.rows(), [])
        src = (ROOT / "src" / "pce_shadow" / "engine.py").read_text(encoding="utf-8")
        self.assertNotIn("api.cpicpgx.org", src)
        self.assertNotIn("urlopen", src)

    def test_f5_mock_fixture_immutable_and_het_hom(self) -> None:
        before = MOCK_PATH.read_bytes()
        payload = json.loads(before.decode("utf-8"))
        lookup_vals = [r["lookupkey"]["F5"] for r in payload["rows"]]
        self.assertIn("heterozygous", lookup_vals)
        self.assertIn("Leiden/Leiden", lookup_vals)
        rows = MockF5Provider().rows()
        rows[0]["recommendation"] = "MUTATED-MUST-NOT-WRITE"
        rows[0]["lookupkey"]["F5"] = "MUTATED"
        KnowledgeTable(f5_source="mock")
        self.assertEqual(MOCK_PATH.read_bytes(), before)

    def test_f5_unknown_json_keys_do_not_crash(self) -> None:
        row = {
            "recommendationid": 1,
            "lookupkey": {"F5": "heterozygous", "extraGene": "*1/*1"},
            "recommendation": "Avoid estrogen-containing contraceptives.",
            "unexpected": {"nested": True},
        }
        validate_rec_view_row(row)
        pairings, _dips, _labels = transform_rows([row], mocked=True)
        self.assertEqual(len(pairings), 1)

    def test_f5_pipeline_idempotent_no_duplicate_pairing(self) -> None:
        table = KnowledgeTable(f5_source="mock")
        n = len(table.pairings())
        mock_ids = [row["id"] for row in table.inventory.get("van") or [] if row.get("id") == "CPIC-F5-MOCK"]
        self.assertEqual(len(mock_ids), 1)
        apply_f5_source(table, source="mock")
        self.assertEqual(len(table.pairings()), n)
        mock_ids = [row["id"] for row in table.inventory.get("van") or [] if row.get("id") == "CPIC-F5-MOCK"]
        self.assertEqual(len(mock_ids), 1)
        out1 = _infer_with(table, "F5", "heterozygous", F5_ATC5)
        out2 = _infer_with(table, "F5", "heterozygous", F5_ATC5)
        self.assertEqual(len(out1["live_findings"]), 1)
        self.assertEqual(len(out2["live_findings"]), 1)

    def test_f5_live_network_error_skips_without_exception(self) -> None:
        def boom() -> list:
            raise OSError("offline")

        rows = LiveF5Provider(fetch=boom).rows()
        self.assertEqual(rows, [])
        table = KnowledgeTable(f5_source="live", f5_fetch=boom)
        self.assertEqual(table.f5_source, "live")
        self.assertIsNone(table.pairing("F5", F5_ATC5))

    def test_f5_classify_dose_and_no_recommendation(self) -> None:
        self.assertEqual(classify_recommendation("Consider a lower dose."), "CONSIDER_DOSE_CHANGE")
        self.assertEqual(classify_recommendation("No recommendation"), "NO_RECOMMENDATION")
        self.assertIsNone(classify_recommendation("unmapped prose"))

    def test_f5_pheno_from_phenotypes_and_atc_on_row(self) -> None:
        row = {
            "lookupkey": {"F5": "not-a-mapped-token"},
            "phenotypes": {"F5": "homozygous"},
            "recommendation": "Avoid estrogen-containing contraceptives.",
            "atc5": "G03AA07",
            "drugname": "hormonal contraceptives for systemic use",
        }
        validate_rec_view_row(row)
        pairings, _dips, _labels = transform_rows([row], mocked=True)
        self.assertEqual(pairings[0]["by_phenotype"]["HOM"], "CONSIDER_ALTERNATIVE")
        row2 = {
            "lookupkey": {"F5": "still-unmapped"},
            "phenotype": "wild type",
            "recommendation": "No genotype-based change. Continue therapy.",
        }
        pairings2, _d, _l = transform_rows([row2], mocked=True)
        self.assertEqual(pairings2[0]["by_phenotype"]["WT"], "CONTINUE")

    def test_builder_script_cannot_emit_clopidogrel(self) -> None:
        mod = _load_builder()
        original = dict(mod.ATC)
        mod.ATC[("CYP2C19", "clopidogrel")] = ("B01AC04", "klopidogrel")
        try:
            doc = mod.build()
            keys = {(p["gene"], p["inn"]) for p in doc["pairings"]}
            self.assertNotIn(("CYP2C19", "clopidogrel"), keys)
            atcs = {(p["gene"], p["atc5"]) for p in doc["pairings"]}
            self.assertNotIn(("CYP2C19", "B01AC04"), atcs)
        finally:
            mod.ATC.clear()
            mod.ATC.update(original)

    def test_html_truncated_who_pin_exits_nonzero(self) -> None:
        mod = _load_builder()
        tmp = Path(tempfile.mkdtemp()) / "whocc-atc-n06ab05.html"
        tmp.write_text("<html><body>truncated, no ATC code</body></html>", encoding="utf-8")
        with self.assertRaises(ValueError):
            mod.verify_who_html(tmp, "N06AB05", ["paroxetine"])
        with self.assertRaises(ValueError):
            mod.verify_who_html_pins(
                {("CYP2D6", "paroxetine"): ("N06AB05", "paroxetin")},
                dest=tmp.parent,
            )

    def test_who_html_pins_parse_with_stdlib_parser(self) -> None:
        mod = _load_builder()
        mod.verify_who_html_pins()

    def test_matcher_off_circuit_breaker_does_not_spawn_java(self) -> None:
        text = (GOLD / "called-cyp2d6-star4-hom.vcf").read_text(encoding="utf-8")
        with patch("pce_clinical.star_call.run_matcher_and_phenotyper") as run:
            with patch("pce_clinical.pharmcat.subprocess.run") as sp:
                call_star_alleles(text, reference="GRCh38", matcher_on=False)
                call_star_alleles(text, reference="GRCh38")
                run.assert_not_called()
                sp.assert_not_called()
        self.assertFalse(MATCHER_ON)

    def test_pharmcat_wrapper_is_argv_list_not_shell(self) -> None:
        src = (ROOT / "src" / "pce_clinical" / "pharmcat.py").read_text(encoding="utf-8")
        self.assertNotIn("shell=True", src)
        self.assertIn("shell=False", src)
        self.assertNotIn(".first(", src)
        self.assertNotIn(".fallback(", src)
        self.assertIn("if len(names) == 1:", src)
        self.assertIn("name = names[0]", src)

    def test_add_outside_call_merges_hla_b(self) -> None:
        from pce_clinical.service import ClinicalService
        from pce_clinical.store import ClinicalStore

        tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        tmp.close()
        svc = ClinicalService(ClinicalStore(tmp.name))
        org = svc.create_org(
            {"name": "SYN-ORG-001", "license_id": "SYN-LIC-001", "role": "lab"}, "lab_signer"
        )
        sub = svc.create_subject({"org_id": org["id"]}, "lab_signer")
        case = svc.create_case(
            {
                "org_id": org["id"],
                "subject_id": sub["id"],
                "sample": {"collected_at": "2026-08-10", "type": "blood", "origin": "SYN-LAB-001"},
            },
            "lab_signer",
        )
        svc.add_counselling(
            case["id"], {"counsellor_id": "SYN-MD-001", "occurred_at": "2026-08-09"}, "counsellor"
        )
        svc.add_consent(
            case["id"],
            {"granted_at": "2026-08-09", "scopes": ["pgx_report"], "omit_from_patient": []},
            "counsellor",
        )
        out = svc.add_outside_call(
            case["id"],
            {
                "gene": "HLA-B",
                "diplotype": "*57:01 positive",
                "callability": "CALLED",
                "calling_lab": "SYN-LAB-001",
                "signing_physician": "SYN-MD-001",
                "method": "HLA typing",
                "call_date": "2026-08-10",
            },
            "lab_signer",
        )
        self.assertEqual(out["calls"][0]["gene"], "HLA-B")
        self.assertEqual(out["calls"][0]["diplotype"], "*57:01 positive")

    def test_f5_http_fetch_live_mocked(self) -> None:
        class _Resp:
            def read(self) -> bytes:
                return b"[]"

            def __enter__(self) -> "_Resp":
                return self

            def __exit__(self, *args: object) -> None:
                return None

        with patch("pce_shadow.f5_rec.urllib.request.urlopen", return_value=_Resp()):
            self.assertEqual(LiveF5Provider().rows(), [])
        class _Obj:
            def read(self) -> bytes:
                return b"{}"

            def __enter__(self) -> "_Obj":
                return self

            def __exit__(self, *args: object) -> None:
                return None

        with patch("pce_shadow.f5_rec.urllib.request.urlopen", return_value=_Obj()):
            with self.assertRaises(ValueError):
                LiveF5Provider().rows()

    def test_cyp2d6_cnv_not_assumed_wild_type(self) -> None:
        text = (GOLD / "called-cyp2d6-star4-hom.vcf").read_text(encoding="utf-8")
        rows = {r["gene"]: r for r in call_star_alleles(text, reference="GRCh38", matcher_on=True)}
        self.assertEqual(rows["CYP2D6"]["callability"], "CALLED")
        self.assertIs(rows["CYP2D6"].get("sv_determined"), False)
        self.assertIn("kópiaszám", rows["CYP2D6"]["note_hu"])

    def test_rec_pairings_forbid_dose_mg_token(self) -> None:
        blob = EXTRA.read_text(encoding="utf-8")
        self.assertNotIn("dose_mg", blob)
        self.assertNotIn("dose/day", blob.lower())
        out = infer(
            {
                "diplotypes": [
                    {"gene": "CYP2C9", "diplotype": "*1/*1", "callability": "CALLED"},
                    {"gene": "VKORC1", "diplotype": "-1639A/-1639A", "callability": "CALLED"},
                ],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "B01AA03"}],
            }
        )
        finding = json.dumps(out["live_findings"])
        self.assertNotIn("dose_mg", finding)
        self.assertNotIn("mg/day", finding.lower())


if __name__ == "__main__":
    unittest.main()
