#!/usr/bin/env python3
"""PREPARE-12 remaining live pairs, HLA-B / UGT1A1*28 lab ingest, VCF star-allele ON path."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pce_clinical.service import ClinicalService  # noqa: E402
from pce_clinical.star_call import call_star_alleles  # noqa: E402
from pce_clinical.store import ClinicalStore  # noqa: E402
from pce_cds.policy import IIA_SAFE_BLOCK  # noqa: E402
from pce_gateway.flags import LIVE_CDS  # noqa: E402
from pce_report.flags import LIVE_CDS as REPORT_LIVE_CDS  # noqa: E402
from pce_report.flags import MATCHER_ON  # noqa: E402
from pce_report.guidelines import prepare12_table  # noqa: E402
from pce_report.render import render_f1plus  # noqa: E402
from pce_shadow.engine import infer  # noqa: E402
from pce_shadow.table import KnowledgeTable  # noqa: E402

F1 = ROOT / "tests" / "fixtures" / "f1plus-v0"
GOLD = ROOT / "tests" / "fixtures" / "vcf-gold-v0"


def _infer(gene: str, diplotype: str, atc: str) -> dict:
    return infer(
        {
            "diplotypes": [{"gene": gene, "diplotype": diplotype, "callability": "CALLED"}],
            "medications": [{"system": "http://www.whocc.no/atc", "code": atc}],
        }
    )


def _svc() -> ClinicalService:
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmp.close()
    return ClinicalService(ClinicalStore(tmp.name))


def _bootstrap(svc: ClinicalService, scopes: list[str] | None = None) -> dict:
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
        case["id"],
        {"counsellor_id": "SYN-MD-001", "occurred_at": "2026-08-09"},
        "counsellor",
    )
    svc.add_consent(
        case["id"],
        {
            "granted_at": "2026-08-09",
            "scopes": scopes if scopes is not None else ["pgx_report"],
            "omit_from_patient": [],
        },
        "counsellor",
    )
    return case


class FlagFreezeTests(unittest.TestCase):
    def test_repo_flags_stay_off(self) -> None:
        self.assertIs(MATCHER_ON, False)
        self.assertIs(LIVE_CDS, False)
        self.assertIs(REPORT_LIVE_CDS, False)
        self.assertIs(IIA_SAFE_BLOCK, True)


class HlaBUgt1a1LabIngestTests(unittest.TestCase):
    def test_f1plus_hla_b_dumps_abacavir_pair_from_lab_result(self) -> None:
        call = json.loads((F1 / "outside-call-hla-b-5701-positive.json").read_text(encoding="utf-8"))
        engine = render_f1plus(outside_call=call, table=prepare12_table())
        self.assertEqual(engine["case"]["gene"], "HLA-B")
        self.assertEqual(engine["case"]["diplotype"], "*57:01 positive")
        self.assertIn("abacavir", {p["drugname"] for p in engine["pairs"]})
        blob = json.dumps(engine, ensure_ascii=False)
        self.assertNotIn("dose_mg", blob)

    def test_f1plus_ugt1a1_dumps_atazanavir_pair_from_lab_result(self) -> None:
        call = json.loads((F1 / "outside-call-ugt1a1-star28-pm.json").read_text(encoding="utf-8"))
        engine = render_f1plus(outside_call=call, table=prepare12_table())
        self.assertEqual(engine["case"]["gene"], "UGT1A1")
        self.assertEqual(engine["case"]["diplotype"], "*28/*28")
        self.assertIn("atazanavir", {p["drugname"] for p in engine["pairs"]})

    def test_clinical_hla_b_outside_call_renders(self) -> None:
        svc = _svc()
        case = _bootstrap(svc, scopes=["HLA-B", "pgx_report"])
        call = json.loads((F1 / "outside-call-hla-b-5701-positive.json").read_text(encoding="utf-8"))
        svc.add_outside_calls(case["id"], [call], "lab_signer")
        report = svc.create_report(case["id"], "lab_signer")
        self.assertEqual(report["case"]["gene"], "HLA-B")
        self.assertIn("abacavir", {p["drugname"] for p in report["pairs"]})
        self.assertNotIn("dose_mg", json.dumps(report))

    def test_hla_b_5701_positive_abacavir_alternative(self) -> None:
        inf = _infer("HLA-B", "*57:01 positive", "J05AF06")
        self.assertEqual(inf["genotype_phenotype"][0]["genotype_phenotype"], "POS_5701")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")
        self.assertEqual(inf["live_findings"][0]["inn"], "abacavir")
        self.assertNotIn("dose_mg", inf["live_findings"][0])
        self.assertEqual(inf["functional_phenotype"], [])

    def test_hla_b_5701_negative_abacavir_continue(self) -> None:
        inf = _infer("HLA-B", "*57:01 negative", "J05AF06")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONTINUE")

    def test_ugt1a1_star28_hom_atazanavir_alternative(self) -> None:
        inf = _infer("UGT1A1", "*28/*28", "J05AE08")
        self.assertEqual(inf["genotype_phenotype"][0]["genotype_phenotype"], "PM")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")
        self.assertEqual(inf["live_findings"][0]["inn"], "atazanavir")
        self.assertNotIn("dose_mg", inf["live_findings"][0])

    def test_ugt1a1_star1_het_atazanavir_continue(self) -> None:
        inf = _infer("UGT1A1", "*1/*28", "J05AE08")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONTINUE")


class RemainingLivePairTests(unittest.TestCase):
    def test_cyp2b6_pm_efavirenz_dose_change(self) -> None:
        inf = _infer("CYP2B6", "*6/*6", "J05AG03")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_DOSE_CHANGE")
        self.assertEqual(inf["live_findings"][0]["inn"], "efavirenz")
        self.assertNotIn("dose_mg", inf["live_findings"][0])

    def test_cyp2c9_as15_celecoxib_continue_not_blanket_im(self) -> None:
        inf = _infer("CYP2C9", "*1/*2", "M01AH01")
        self.assertEqual(inf["genotype_phenotype"][0]["genotype_phenotype"], "IM")
        self.assertEqual(inf["genotype_phenotype"][0]["activity_score"], "1.5")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONTINUE")

    def test_cyp2c9_as10_celecoxib_dose_change(self) -> None:
        inf = _infer("CYP2C9", "*1/*3", "M01AH01")
        self.assertEqual(inf["genotype_phenotype"][0]["activity_score"], "1.0")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_DOSE_CHANGE")

    def test_cyp3a5_expresser_tacrolimus_dose_change(self) -> None:
        inf = _infer("CYP3A5", "*1/*1", "L04AD02")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_DOSE_CHANGE")

    def test_cyp3a5_nonexpresser_tacrolimus_continue(self) -> None:
        inf = _infer("CYP3A5", "*3/*3", "L04AD02")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONTINUE")

    def test_dpyd_pm_fluorouracil_alternative(self) -> None:
        inf = _infer("DPYD", "*2A/*2A", "L01BC02")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")
        self.assertNotIn("dose_mg", json.dumps(inf))

    def test_dpyd_cpic_hgvs_reference_continue(self) -> None:
        inf = _infer("DPYD", "Reference/Reference", "L01BC02")
        self.assertEqual(inf["genotype_phenotype"][0]["genotype_phenotype"], "NM")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONTINUE")

    def test_slco1b1_poor_function_simvastatin_alternative(self) -> None:
        inf = _infer("SLCO1B1", "*5/*5", "C10AA01")
        self.assertEqual(inf["genotype_phenotype"][0]["genotype_phenotype"], "PF")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")

    def test_cyp2d6_pm_codeine_alternative(self) -> None:
        inf = _infer("CYP2D6", "*4/*4", "R05DA04")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")
        self.assertEqual(inf["live_findings"][0]["inn"], "codeine")
        self.assertNotIn("dose_mg", inf["live_findings"][0])

    def test_dpyd_pm_capecitabine_alternative(self) -> None:
        inf = _infer("DPYD", "*2A/*2A", "L01BC06")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")
        self.assertEqual(inf["live_findings"][0]["inn"], "capecitabine")

    def test_hla_b_5801_allopurinol_alternative(self) -> None:
        inf = _infer("HLA-B", "*58:01 positive", "M04AA01")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")
        self.assertEqual(inf["live_findings"][0]["inn"], "allopurinol")

    def test_cyp2c19_pm_citalopram_dose_change(self) -> None:
        inf = _infer("CYP2C19", "*2/*2", "N06AB04")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_DOSE_CHANGE")
        self.assertEqual(inf["live_findings"][0]["inn"], "citalopram")

    def test_rec_view_pairings_are_loaded(self) -> None:
        table = KnowledgeTable()
        self.assertEqual(table.pairing("CYP2D6", "R05DA04")["inn"], "codeine")
        self.assertEqual(table.pairing("DPYD", "L01BC06")["inn"], "capecitabine")
        self.assertGreaterEqual(len(table.pairings()), 50)
        inf = _infer("TPMT", "*3C/*3C", "L04AX01")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")

    def test_f5_and_vkorc1_have_no_invented_pairing(self) -> None:
        table = KnowledgeTable()
        self.assertIsNone(table.pairing("F5", "B01AA03"))
        self.assertIsNone(table.pairing("VKORC1", "B01AA03"))
        inf = _infer("F5", "Leiden/Leiden", "B01AA03")
        self.assertEqual(inf["live_findings"], [])
        missing = " ".join(row["hu"] for row in inf["forras_allapot"]["hianyzik"])
        self.assertIn("F5", missing)

    def test_warfarin_needs_both_genes_and_has_no_mg(self) -> None:
        only_vkor = infer(
            {
                "diplotypes": [
                    {"gene": "VKORC1", "diplotype": "-1639G/-1639G", "callability": "CALLED"}
                ],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "B01AA03"}],
            }
        )
        self.assertEqual(only_vkor["live_findings"], [])
        both = infer(
            {
                "diplotypes": [
                    {"gene": "CYP2C9", "diplotype": "*1/*1", "callability": "CALLED"},
                    {"gene": "VKORC1", "diplotype": "-1639G/-1639G", "callability": "CALLED"},
                ],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "B01AA03"}],
            }
        )
        self.assertEqual(both["live_findings"][0]["inn"], "warfarin")
        self.assertEqual(both["live_findings"][0]["strategy_category"], "CONSIDER_DOSE_CHANGE")
        self.assertNotIn("dose_mg", both["live_findings"][0])
        pm = infer(
            {
                "diplotypes": [
                    {"gene": "CYP2C9", "diplotype": "*3/*3", "callability": "CALLED"},
                    {"gene": "VKORC1", "diplotype": "-1639A/-1639A", "callability": "CALLED"},
                ],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "B01AA03"}],
            }
        )
        self.assertEqual(pm["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")
        self.assertNotIn("dose_mg", json.dumps(pm))

    def test_rec_view_pairings_have_no_milligrams(self) -> None:
        blob = (ROOT / "tests" / "fixtures" / "shadow-v0" / "prepare12-rec-pairings.v0.json").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("dose_mg", blob)
        table = KnowledgeTable()
        self.assertIsNone(table.pairing("F5", "G03AA"))
        inf = _infer("SLCO1B1", "*5/*5", "C10AA05")
        self.assertEqual(inf["live_findings"][0]["inn"], "atorvastatin")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONSIDER_DOSE_CHANGE")
        self.assertNotIn("dose_mg", inf["live_findings"][0])
        mp = _infer("TPMT", "*3C/*3C", "L01BB02")
        self.assertEqual(mp["live_findings"][0]["inn"], "mercaptopurine")
        self.assertEqual(mp["live_findings"][0]["strategy_category"], "CONSIDER_ALTERNATIVE")


class StarAlleleOnPathTests(unittest.TestCase):
    def test_matcher_off_does_not_call_diplotype(self) -> None:
        text = (GOLD / "called-cyp2d6-star4-hom.vcf").read_text(encoding="utf-8")
        rows = {r["gene"]: r for r in call_star_alleles(text, reference="GRCh38", matcher_on=False)}
        self.assertIsNone(rows["CYP2D6"]["diplotype"])
        self.assertEqual(rows["CYP2D6"]["callability"], "NOT_TESTED")
        self.assertEqual(rows["HLA-B"]["callability"], "NOT_TESTED")
        self.assertEqual(rows["UGT1A1"]["callability"], "NOT_TESTED")

    def test_matcher_on_calls_cyp2d6_star4_hom_from_pharmcat(self) -> None:
        text = (GOLD / "called-cyp2d6-star4-hom.vcf").read_text(encoding="utf-8")
        rows = {r["gene"]: r for r in call_star_alleles(text, reference="GRCh38", matcher_on=True)}
        self.assertEqual(rows["CYP2D6"]["callability"], "CALLED")
        self.assertEqual(rows["CYP2D6"]["diplotype"], "*4/*4")
        self.assertEqual(rows["CYP2C9"]["callability"], "CALLED")
        self.assertEqual(rows["CYP2C9"]["diplotype"], "*4/*4")
        self.assertEqual(rows["HLA-B"]["callability"], "NOT_TESTED")
        self.assertIsNone(rows["HLA-B"]["diplotype"])
        self.assertEqual(rows["UGT1A1"]["callability"], "NOT_TESTED")
        self.assertIsNone(rows["UGT1A1"]["diplotype"])
        self.assertEqual(rows["CYP2C19"]["callability"], "INDETERMINATE")
        self.assertIsNone(rows["CYP2C19"]["diplotype"])
        self.assertGreaterEqual(len(rows["CYP2C19"].get("ambiguous_diplotypes") or []), 2)
        self.assertEqual(rows["CYP2D6"]["pharmcat_version"], "3.4.0")
        self.assertTrue(rows["CYP2D6"].get("pharmvar_version"))
        self.assertTrue(rows["CYP2D6"].get("cpic_data_version"))
        self.assertIs(rows["CYP2D6"].get("sv_determined"), False)

    def test_matcher_on_missing_site_is_indeterminate_not_star1(self) -> None:
        text = (GOLD / "missing-cyp2d6-star4.vcf").read_text(encoding="utf-8")
        rows = {r["gene"]: r for r in call_star_alleles(text, reference="GRCh38", matcher_on=True)}
        self.assertNotEqual(rows["CYP2D6"]["diplotype"], "*1/*1")
        self.assertNotEqual(rows["CYP2D6"]["callability"], "CALLED")
        self.assertIsNone(rows["CYP2D6"]["diplotype"])

    def test_clinical_add_vcf_matcher_on_persists_diplotype(self) -> None:
        svc = _svc()
        case = _bootstrap(svc, scopes=["pgx_report"])
        raw = (GOLD / "called-cyp2d6-star4-hom.vcf").read_bytes()
        stored = svc.add_vcf(case["id"], raw, "lab_signer", matcher_on=True)
        self.assertTrue(stored["matcher_on"])
        cov = {row["gene"]: row for row in stored["coverage"]}
        self.assertEqual(cov["CYP2D6"]["callability"], "CALLED")
        self.assertEqual(cov["CYP2D6"]["diplotype"], "*4/*4")
        self.assertEqual(cov["CYP2C9"]["callability"], "CALLED")
        self.assertEqual(cov["CYP2C9"]["diplotype"], "*4/*4")
        self.assertEqual(cov["HLA-B"]["callability"], "NOT_TESTED")
        report = svc.create_report(case["id"], "lab_signer")
        cyp = next(g for g in report["genes"] if g["gene"] == "CYP2D6")
        self.assertEqual(cyp["diplotype"], "*4/*4")
        self.assertEqual(cyp["callability"], "CALLED")
        cyp2c9 = next(g for g in report["genes"] if g["gene"] == "CYP2C9")
        self.assertEqual(cyp2c9["diplotype"], "*4/*4")
        self.assertEqual(cyp2c9["callability"], "CALLED")
        hla = next(g for g in report["genes"] if g["gene"] == "HLA-B")
        self.assertEqual(hla["callability"], "NOT_TESTED")
        self.assertIsNone(hla["diplotype"])
        self.assertEqual(report["pharmcat_version"], "3.4.0")
        self.assertTrue(report["pharmvar_version"])
        self.assertTrue(report["cpic_data_version"])
        self.assertEqual(report["pipeline_version"], "pce-clinical-v0")
        self.assertTrue(report["matcher_on"])
        self.assertIn("NamedAlleleMatcher", report["diplotipus_forras_hu"])

    def test_clinical_add_vcf_default_still_off(self) -> None:
        svc = _svc()
        case = _bootstrap(svc, scopes=["pgx_report"])
        raw = (GOLD / "called-cyp2d6-star4-hom.vcf").read_bytes()
        stored = svc.add_vcf(case["id"], raw, "lab_signer")
        self.assertFalse(stored["matcher_on"])
        cov = {row["gene"]: row for row in stored["coverage"]}
        self.assertIsNone(cov["CYP2D6"]["diplotype"])
        self.assertEqual(cov["CYP2D6"]["callability"], "NOT_TESTED")


if __name__ == "__main__":
    unittest.main()
