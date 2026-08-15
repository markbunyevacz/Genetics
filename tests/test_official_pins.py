#!/usr/bin/env python3
"""Official CPIC/FDA/WHO files are on disk with an accessed date (D-38)."""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "docs" / "pce" / "Sources" / "official"
KNOWLEDGE = ROOT / "tests" / "fixtures" / "shadow-v0" / "cyp2d6-knowledge.v0.json"


class OfficialPinTests(unittest.TestCase):
    def test_manifest_and_binaries(self) -> None:
        manifest = json.loads((OFFICIAL / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["accessed"], "2026-08-13")
        by_id = {row["id"]: row for row in manifest["files"]}
        self.assertTrue(by_id["CPIC-SSRI-2023-PDF"]["ok"])
        self.assertTrue(by_id["FDA-DDI-TABLE-2-2-HTML"]["ok"])
        ssri = ROOT / by_id["CPIC-SSRI-2023-PDF"]["path"]
        opioid = ROOT / by_id["CPIC-OPIOID-2020-PDF"]["path"]
        self.assertTrue(ssri.read_bytes().startswith(b"%PDF"))
        self.assertTrue(opioid.read_bytes().startswith(b"%PDF"))
        fda = (ROOT / by_id["FDA-DDI-TABLE-2-2-HTML"]["path"]).read_text(encoding="utf-8", errors="replace")
        self.assertIn("Table 2-2", fda)
        self.assertIn("paroxetine", fda)
        self.assertIn("fluoxetine", fda)
        self.assertIn("quinidine", fda)
        self.assertIn("Strong index inhibitors", fda)
        who = (OFFICIAL / "whocc-atc-n06ab05.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("N06AB05", who)
        self.assertIn("paroxetine", who)
        esc = (OFFICIAL / "whocc-atc-n06ab10.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("escitalopram", esc.lower())
        qin = (OFFICIAL / "whocc-atc-c01ba01.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("quinidine", qin.lower())
        self.assertTrue((OFFICIAL / "edpb-guidelines-01-2025-pseudonymisation.pdf").read_bytes().startswith(b"%PDF"))
        self.assertTrue((OFFICIAL / "wp29-opinion-05-2014-wp216-anonymisation.pdf").read_bytes().startswith(b"%PDF"))
        dpc = (OFFICIAL / "ie-dpc-case-studies-2025.pdf").read_bytes()
        self.assertTrue(dpc.startswith(b"%PDF"))
        gdpr = by_id["EUR-LEX-GDPR-2016-679"]
        self.assertTrue(gdpr["ok"])
        html = (ROOT / gdpr["path"]).read_text(encoding="utf-8", errors="replace")
        self.assertIn(
            "without undue delay and in any event within one month of receipt of the request",
            html,
        )
        self.assertIn(
            "If the controller does not take action on the request of the data subject",
            html,
        )
        self.assertIn("Right to erasure", html)
        self.assertTrue((OFFICIAL / "eur-lex-gdpr-2016-679.pdf").read_bytes().startswith(b"%PDF"))
        ema = (OFFICIAL / "ema-anonymisation-report-form-instructions.pdf").read_bytes()
        self.assertTrue(ema.startswith(b"%PDF"))
        self.assertTrue(by_id["EMA-ANON-REPORT-FORM-INSTRUCTIONS"]["ok"])
        self.assertTrue((OFFICIAL / "mdcg-2021-24-en.pdf").read_bytes().startswith(b"%PDF"))
        self.assertTrue(by_id["MDCG-2021-24"]["ok"])
        hc = (OFFICIAL / "health-canada-prci-guidance-document.html").read_text(
            encoding="utf-8", errors="replace"
        )
        self.assertIn("target cell size of 11 patients", hc)
        self.assertIn("risk=0.09", hc)
        self.assertIn("9% re-identification risk threshold", hc)
        self.assertTrue(by_id["HEALTH-CANADA-PRCI-GUIDANCE"]["ok"])
        self.assertTrue(by_id["HEALTH-CANADA-PRCI-PROFILE"]["ok"])
        profile = (OFFICIAL / "health-canada-prci-guidance.html").read_text(
            encoding="utf-8", errors="replace"
        )
        self.assertIn("Public Release of Clinical Information", profile)
        dhcs = (OFFICIAL / "dhcs-ddg-v2-2.pdf").read_bytes()
        self.assertTrue(dhcs.startswith(b"%PDF"))
        self.assertTrue(by_id["DHCS-DDG-V2-2"]["ok"])
        self.assertGreater(len(dhcs), 1_000_000)
        for pin_id in (
            "HEALTH-CANADA-PRCI-PROFILE",
            "HEALTH-CANADA-PRCI-GUIDANCE",
            "DHCS-DDG-V2-2",
        ):
            row = by_id[pin_id]
            blob = (ROOT / row["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(blob).hexdigest(), row["sha256"])
            self.assertEqual(len(blob), row["bytes"])

    def test_etap0_dpwg_ensembl_and_clopidogrel_pins(self) -> None:
        manifest = json.loads((OFFICIAL / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["accessed"], "2026-08-13")
        by_id = {row["id"]: row for row in manifest["files"]}
        self.assertGreaterEqual(sum(1 for row in manifest["files"] if row.get("ok")), 26)
        dpwg = ROOT / by_id["CLINPGX-DPWG-GUIDELINE-ANNOTATIONS"]["path"]
        blob = json.loads(dpwg.read_text(encoding="utf-8"))
        self.assertEqual(blob["status"], "success")
        self.assertGreaterEqual(len(blob["data"]), 100)
        self.assertTrue(any(row.get("source") == "DPWG" for row in blob["data"]))
        ens = json.loads((OFFICIAL / "ensembl-prepare12-defining-snvs-2026-08-14.json").read_text())
        mappings = ens["grch38"]["rs1057910"]["mappings"]
        hit = next(m for m in mappings if str(m.get("seq_region_name")) == "10")
        self.assertEqual(hit["start"], 94981296)
        who = (OFFICIAL / "whocc-atc-b01ac04.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("B01AC04", who)
        self.assertIn("clopidogrel", who.lower())
        c19 = json.loads((OFFICIAL / "cpic-api-diplotype-cyp2c19-nm-im-pm.json").read_text())
        by_dip = {row["diplotype"]: row["generesult"] for row in c19}
        self.assertEqual(by_dip["*1/*1"], "Normal Metabolizer")
        self.assertEqual(by_dip["*1/*2"], "Intermediate Metabolizer")
        self.assertEqual(by_dip["*2/*2"], "Poor Metabolizer")
        dbsnp = json.loads((OFFICIAL / "ncbi-dbsnp-prepare12-defining-snvs-2026-08-14.json").read_text())
        self.assertEqual(dbsnp["result"]["8175347"]["snp_class"], "delins")
        for pin_id in (
            "CLINPGX-DPWG-GUIDELINE-ANNOTATIONS",
            "ENSEMBL-PREPARE12-DEFINING-SNVS",
            "WHO-ATC-B01AC04",
            "CPIC-DIPLOTYPE-CYP2C19-API",
        ):
            row = by_id[pin_id]
            raw = (ROOT / row["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
            self.assertEqual(len(raw), row["bytes"])

    def test_knowledge_json_points_at_on_disk_files(self) -> None:
        doc = json.loads(KNOWLEDGE.read_text(encoding="utf-8"))
        missing = []
        for src in doc["sources"]:
            on_disk = src.get("on_disk")
            if not on_disk:
                continue
            path = ROOT / on_disk
            if not path.is_file():
                missing.append(on_disk)
        self.assertEqual(missing, [])
        prepare12 = ROOT / "tests" / "fixtures" / "f1plus-v0" / "prepare12" / "index.v0.json"
        self.assertEqual(json.loads(prepare12.read_text(encoding="utf-8"))["accessed"], "2026-08-13")

    def test_prepare12_live_pair_pins_2026_08_15(self) -> None:
        manifest = json.loads((OFFICIAL / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["accessed"], "2026-08-13")
        by_id = {row["id"]: row for row in manifest["files"]}
        self.assertGreaterEqual(sum(1 for row in manifest["files"] if row.get("ok")), 41)
        who_inn = {
            "WHO-ATC-J05AG03": "efavirenz",
            "WHO-ATC-L04AD02": "tacrolimus",
            "WHO-ATC-L01BC02": "fluorouracil",
            "WHO-ATC-C10AA01": "simvastatin",
            "WHO-ATC-L04AX01": "azathioprine",
            "WHO-ATC-J05AF06": "abacavir",
            "WHO-ATC-J05AE08": "atazanavir",
            "WHO-ATC-M01AH01": "celecoxib",
        }
        for pin_id, inn in who_inn.items():
            row = by_id[pin_id]
            raw = (ROOT / row["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
            self.assertEqual(len(raw), row["bytes"])
            text = raw.decode("utf-8", errors="replace").lower()
            self.assertIn(inn, text)
        cyp2c9 = json.loads((OFFICIAL / "cpic-api-diplotype-cyp2c9-2026-08-15.json").read_text())
        by_dip = {row["diplotype"]: row for row in cyp2c9}
        self.assertEqual(by_dip["*1/*2"]["generesult"], "Intermediate Metabolizer")
        self.assertEqual(by_dip["*1/*2"]["totalactivityscore"], "1.5")
        self.assertEqual(by_dip["*1/*3"]["totalactivityscore"], "1.0")
        ugt = json.loads((OFFICIAL / "cpic-api-diplotype-ugt1a1-2026-08-15.json").read_text())
        by_ugt = {row["diplotype"]: row["generesult"] for row in ugt}
        self.assertEqual(by_ugt["*28/*28"], "Poor Metabolizer")
        dpyd = json.loads((OFFICIAL / "cpic-api-diplotype-dpyd-2026-08-15.json").read_text())
        by_dpyd = {row["diplotype"]: row["generesult"] for row in dpyd}
        self.assertEqual(by_dpyd["Reference/Reference"], "Normal Metabolizer")
        for pin_id in (
            "CPIC-DIPLOTYPE-CYP2B6-API",
            "CPIC-DIPLOTYPE-CYP2C9-API",
            "CPIC-DIPLOTYPE-CYP3A5-API",
            "CPIC-DIPLOTYPE-DPYD-API",
            "CPIC-DIPLOTYPE-SLCO1B1-API",
            "CPIC-DIPLOTYPE-TPMT-API",
            "CPIC-DIPLOTYPE-UGT1A1-API",
        ):
            row = by_id[pin_id]
            raw = (ROOT / row["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
            self.assertEqual(len(raw), row["bytes"])

    def test_software_ready_pins_2026_08_15(self) -> None:
        manifest = json.loads((OFFICIAL / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["accessed"], "2026-08-13")
        by_id = {row["id"]: row for row in manifest["files"]}
        self.assertGreaterEqual(sum(1 for row in manifest["files"] if row.get("ok")), 87)
        warfarin = ROOT / by_id["CPIC-WARFARIN-2017-PDF"]["path"]
        self.assertTrue(warfarin.read_bytes().startswith(b"%PDF"))
        who = (OFFICIAL / "whocc-atc-b01aa03.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("B01AA03", who)
        self.assertIn("warfarin", who.lower())
        pin = json.loads((OFFICIAL / "pharmcat-3.4.0-pin.json").read_text(encoding="utf-8"))
        self.assertEqual(pin["version"], "3.4.0")
        self.assertEqual(pin["license"], "MPL-2.0")
        self.assertTrue(pin["we_do_not_modify_the_jar"])
        extra = ROOT / "tests" / "fixtures" / "shadow-v0" / "prepare12-rec-pairings.v0.json"
        self.assertNotIn("dose_mg", extra.read_text(encoding="utf-8"))
        for pin_id in (
            "CPIC-WARFARIN-2017-PDF",
            "WHO-ATC-B01AA03",
            "WHO-ATC-N06AB04",
            "WHO-ATC-L01BC06",
            "WHO-ATC-L01BC03",
            "WHO-ATC-M04AA01",
            "WHO-ATC-R05DA04",
            "PHARMCAT-3.4.0-PIN",
        ):
            row = by_id[pin_id]
            raw = (ROOT / row["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
            self.assertEqual(len(raw), row["bytes"])


if __name__ == "__main__":
    unittest.main()
