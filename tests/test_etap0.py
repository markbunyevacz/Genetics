#!/usr/bin/env python3
"""ETAP 0: DPWG/FDA on the lelet, PREPARE-12 SNV catalog, gene-keyed shadow pairing, monitor org display."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pce_clinical.coverage import assess_coverage  # noqa: E402
from pce_gateway.config import GatewayConfig  # noqa: E402
from pce_gateway.kcell import KCellStore  # noqa: E402
from pce_report.guidelines import GuidelineTable, prepare12_table  # noqa: E402
from pce_report.render import render_f1plus  # noqa: E402
from pce_report.schema import assemble_b41, assert_b41_contract  # noqa: E402
from pce_report.static_pins import dpwg_version, fda_table_version  # noqa: E402
from pce_shadow.engine import infer  # noqa: E402
from pce_shadow.table import KnowledgeTable  # noqa: E402

F1 = ROOT / "tests" / "fixtures" / "f1plus-v0"
GOLD = ROOT / "tests" / "fixtures" / "vcf-gold-v0"
CATALOG = GOLD / "defining-positions.v0.json"


def _b41(engine: dict) -> dict:
    return assemble_b41(
        engine=engine,
        report_id="SYN-RPT-ETAP0",
        case_id="SYN-CASE-ETAP0",
        counselling={"id": "SYN-C", "at": "2026-01-01T00:00:00+00:00", "counsellor_id": "SYN-MD-001"},
        consent_granted_at="2026-01-02T00:00:00+00:00",
        performing_org_license_id="SYN-LIC-001",
        white_label={"org": "SYN-ORG-001", "signer_slot": "SYN-MD-001", "colophon": "Precision Clinical Engine"},
        genes=[
            {
                "gene": engine["case"]["gene"],
                "diplotype": engine["case"].get("diplotype"),
                "genotype_phenotype": engine["case"].get("lab_phenotype_claim"),
                "callability": engine["case"]["callability"],
            }
        ],
        omit_from_patient=frozenset(),
    )


class DpwgFdaOnLeletTests(unittest.TestCase):
    def test_versions_and_urls_are_separate_sources(self) -> None:
        call = json.loads((F1 / "outside-call-cyp2d6-called.json").read_text(encoding="utf-8"))
        table = GuidelineTable(
            F1 / "cyp2d6-cpic-pair-view.v0.json",
            F1 / "cyp2d6-cpic-recommendation-view.v0.json",
        )
        engine = render_f1plus(outside_call=call, table=table)
        self.assertEqual(engine["dpwg_version"], dpwg_version())
        self.assertEqual(engine["fda_table_version"], fda_table_version())
        dpwg = engine["guideline_source"]["dpwg"]
        fda = engine["guideline_source"]["fda_table_2_2"]
        self.assertTrue(dpwg["api"].startswith("https://api.clinpgx.org/"))
        self.assertIn("source=DPWG", dpwg["api"])
        self.assertGreater(dpwg["annotation_count"], 0)
        self.assertTrue(dpwg["do_not_merge_with_cpic"])
        self.assertIn("paroxetine", {r["inn"] for r in fda["cyp2d6_strong_index_inhibitors"]})
        self.assertIn("fluoxetine", {r["inn"] for r in fda["cyp2d6_strong_index_inhibitors"]})
        report = _b41(engine)
        assert_b41_contract(report)
        self.assertEqual(report["dpwg_version"], dpwg_version())
        self.assertEqual(report["fda_table_version"], fda_table_version())
        self.assertIsNotNone(report["dpwg_version"])
        self.assertIsNotNone(report["fda_table_version"])
        blob = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("dose_mg", blob)
        # No synthesized third rec that mixes the three sources into one statement.
        for finding in report["findings"]:
            for stmt in finding.get("statements") or []:
                src = stmt.get("source") or ""
                self.assertNotEqual(src, "CPIC+DPWG+FDA")
                if src == "DPWG":
                    self.assertIn("clinpgx.org", stmt.get("url") or "")

    def test_prepare12_cyp2c19_keeps_cpic_and_adds_dpwg_index(self) -> None:
        report = render_f1plus(
            outside_call={
                "gene": "CYP2C19",
                "diplotype": "*1/*1",
                "callability": "CALLED",
                "case_display_id": "SYN-CASE-C19",
            },
            table=prepare12_table(),
        )
        self.assertFalse(report["hianyzik"])
        self.assertIn("clopidogrel", {p["drugname"] for p in report["pairs"]})
        self.assertGreater(report["guideline_source"]["dpwg"]["annotation_count"], 0)
        self.assertTrue(any(a.get("url") for a in report["guideline_source"]["dpwg"]["annotations"]))


class VcfCatalogTests(unittest.TestCase):
    def test_prepare12_snv_genes_are_pinned(self) -> None:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        pinned = {
            "CYP2B6",
            "CYP2C9",
            "CYP2C19",
            "CYP2D6",
            "CYP3A5",
            "DPYD",
            "F5",
            "SLCO1B1",
            "TPMT",
            "VKORC1",
        }
        for gene in pinned:
            self.assertEqual(catalog["genes"][gene]["catalog"], "pinned", gene)
            self.assertTrue(catalog["genes"][gene]["positions"], gene)
        self.assertEqual(catalog["genes"]["HLA-B"]["catalog"], "not_snv")
        self.assertEqual(catalog["genes"]["UGT1A1"]["catalog"], "not_snv")
        self.assertEqual(catalog["genes"]["CYP2C9"]["positions"][1]["rsid"], "rs1057910")
        self.assertEqual(catalog["genes"]["CYP2C9"]["positions"][1]["grch38_pos"], 94981296)

    def test_missing_cyp2c9_star3_is_indeterminate(self) -> None:
        text = (GOLD / "missing-cyp2c9-star3.vcf").read_text(encoding="utf-8")
        rows = {r["gene"]: r for r in assess_coverage(text, reference="GRCh38")}
        row = rows["CYP2C9"]
        self.assertEqual(row["callability"], "INDETERMINATE")
        self.assertIn("rs1057910", {m.get("rsid") for m in row["missing"]})
        self.assertNotEqual(row["callability"], "NORMAL")
        self.assertFalse(row["pharmcat_absent_to_ref"])
        self.assertEqual(rows["HLA-B"]["callability"], "NOT_TESTED")
        self.assertEqual(rows["UGT1A1"]["callability"], "NOT_TESTED")
        self.assertIn("laboratóriumi HLA-tipizálás", rows["HLA-B"]["note_hu"])
        self.assertIn("TATA-box", rows["UGT1A1"]["note_hu"])
        self.assertEqual(rows["CYP2D6"]["callability"], "NOT_TESTED")


class ShadowGeneKeyedPairingTests(unittest.TestCase):
    def test_cyp2d6_does_not_pair_clopidogrel(self) -> None:
        inf = infer(
            {
                "diplotypes": [{"gene": "CYP2D6", "diplotype": "*1/*2"}],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "B01AC04"}],
            }
        )
        self.assertEqual(inf["live_findings"], [])
        self.assertEqual(inf["functional_phenotype"], [])

    def test_cyp2c19_nm_clopidogrel_continue_without_mg(self) -> None:
        inf = infer(
            {
                "diplotypes": [{"gene": "CYP2C19", "diplotype": "*1/*1"}],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "B01AC04"}],
            }
        )
        self.assertEqual(inf["genotype_phenotype"][0]["genotype_phenotype"], "NM")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONTINUE")
        self.assertEqual(inf["live_findings"][0]["gene"], "CYP2C19")
        self.assertEqual(inf["live_findings"][0]["drug_atc"], "B01AC04")
        self.assertNotIn("dose_mg", inf["live_findings"][0])
        self.assertEqual(inf["functional_phenotype"], [])
        self.assertIn("PA166251443", inf["live_findings"][0]["strategy_category_hu"] or "")

    def test_cyp2c19_pm_clopidogrel_alternative_without_invented_pm_label(self) -> None:
        inf = infer(
            {
                "diplotypes": [{"gene": "CYP2C19", "diplotype": "*2/*2"}],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "B01AC04"}],
            }
        )
        self.assertEqual(inf["genotype_phenotype"][0]["genotype_phenotype"], "PM")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")
        self.assertEqual(inf["functional_phenotype"], [])
        self.assertFalse(inf["phenoconversion"]["functional_phenotype_written"])

    def test_pairing_table_is_keyed_by_gene_and_atc5(self) -> None:
        table = KnowledgeTable()
        self.assertIsNone(table.pairing("CYP2D6", "B01AC04"))
        self.assertEqual(table.pairing("CYP2C19", "B01AC04")["inn"], "clopidogrel")
        self.assertEqual(table.pairing("CYP2D6", "N06AB05")["inn"], "paroxetine")


class MonitorOrgDisplayTests(unittest.TestCase):
    def test_quarterly_report_has_opaque_syn_org_display(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        store = KCellStore(Path(tmp.name) / "kcell.sqlite")
        try:
            store.seed("REDUCED", "N06AB05", "2026-Q3", 4)
            store.record_drop("2026-Q3")
            cfg = GatewayConfig()
            report = store.quarterly_report(
                "2026-Q3", org_id=cfg.org_id, org_display=cfg.org_display
            )
            self.assertEqual(report["org_id"], "SYN-ORG-001")
            self.assertEqual(report["org_display"], "SYN-ORG-001")
            blob = json.dumps(report)
            self.assertNotIn("kórház", blob.lower())
            self.assertNotIn("hospital", blob.lower())
            self.assertNotIn("SYN-TAJ", blob)
            self.assertNotIn("*4/*4", blob)
        finally:
            store.close()
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
