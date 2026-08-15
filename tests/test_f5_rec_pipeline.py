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
    F5Source,
    MockF5Provider,
    OffF5Provider,
    classify_recommendation,
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


if __name__ == "__main__":
    unittest.main()
