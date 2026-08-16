#!/usr/bin/env python3
"""FR-520 CDS pipe: lock default, ON via parameter, fail-open, IIa-safe kill-switch.

Also FR-530 SMART stub, FR-700 isolation (no pce_cds import from F1+).
IIa-safe: G §2.4 mechanisms, not English INN literals only.
"""
from __future__ import annotations

import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pce_cds.cards import TIMEOUT_S, build_cards  # noqa: E402
from pce_cds.policy import (  # noqa: E402
    IIA_SAFE_ATC_PREFIXES,
    IIA_SAFE_ATC5,
    IIA_SAFE_BLOCK,
    IIA_SAFE_FAMILIES,
    blocked_live_pairing,
    is_iia_safe_med,
    matching_families,
)
from pce_cds.server import bind_cds_server  # noqa: E402
from pce_gateway.flags import LIVE_CDS  # noqa: E402
from pce_report.flags import LIVE_CDS as REPORT_LIVE_CDS  # noqa: E402
from pce_report.flags import MATCHER_ON  # noqa: E402


def _hook(atc: str = "N06AB05", gene: str = "CYP2D6", star: str = "*1/*2") -> dict:
    return {
        "hook": "order-sign",
        "prefetch": {
            "diplotypes": [{"gene": gene, "diplotype": star}],
            "medications": [{"code": atc, "inn": "paroxetine"}],
        },
    }


class FlagFreezeTests(unittest.TestCase):
    def test_repo_stays_locked(self) -> None:
        self.assertIs(LIVE_CDS, False)
        self.assertIs(REPORT_LIVE_CDS, False)
        self.assertIs(MATCHER_ON, False)
        self.assertIs(IIA_SAFE_BLOCK, True)


class LockPathTests(unittest.TestCase):
    def test_lock_returns_empty_cards(self) -> None:
        out = build_cards(_hook(), live_cds=False)
        self.assertEqual(out["cards"], [])
        self.assertTrue(out["locked"])

    def test_http_lock_discovery_and_empty_post(self) -> None:
        httpd = bind_cds_server(live_cds=False)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        port = httpd.server_address[1]
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/cds-services") as resp:
                disc = json.loads(resp.read().decode("utf-8"))
            self.assertFalse(disc["services"][0]["enabled"])
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/cds-services/pgx-order-sign",
                data=json.dumps(_hook()).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(resp.headers.get("X-PCE-LIVE-CDS"), "false")
            self.assertEqual(body["cards"], [])
        finally:
            httpd.shutdown()
            httpd.server_close()


class OnPathTests(unittest.TestCase):
    def test_paroxetine_nm_continue_card(self) -> None:
        out = build_cards(_hook(), live_cds=True)
        self.assertTrue(out["live_cds"])
        summaries = " ".join(c["summary"] for c in out["cards"])
        self.assertIn("paroxetin", summaries.lower() + summaries)
        self.assertTrue(any(c.get("indicator") == "info" for c in out["cards"]))
        blob = json.dumps(out)
        self.assertNotIn("dose_mg", blob)
        self.assertNotIn("szegény metabolizáló", blob)

    def test_no_pgx_info_card(self) -> None:
        out = build_cards({"hook": "order-sign", "prefetch": {"medications": [{"code": "N06AB05"}]}}, live_cds=True)
        self.assertTrue(out["cards"])
        self.assertIn("Nincs elérhető PGx", out["cards"][0]["summary"])

    def test_fail_open_on_timeout(self) -> None:
        class Clock:
            def __init__(self) -> None:
                self.t = 0.0

            def __call__(self) -> float:
                self.t += TIMEOUT_S + 0.5
                return self.t

        out = build_cards(_hook(), live_cds=True, monotonic=Clock())
        self.assertEqual(out["cards"], [])
        self.assertTrue(out["fail_open"])

    def test_iia_safe_codeine_no_suggestion(self) -> None:
        hook = _hook(atc="R05DA04", gene="CYP2D6", star="*4/*4")
        hook["prefetch"]["medications"] = [{"code": "R05DA04", "inn": "codeine"}]
        out = build_cards(hook, live_cds=True, iia_safe_block=True)
        self.assertTrue(out["cards"])
        self.assertTrue(all(c.get("suggestions") == [] for c in out["cards"]))
        self.assertIn("nem elérhető", json.dumps(out, ensure_ascii=False))

    def test_iia_safe_tramadol_no_suggestion(self) -> None:
        hook = _hook(atc="N02AX02", gene="CYP2D6", star="*4/*4")
        hook["prefetch"]["medications"] = [{"code": "N02AX02", "inn": "tramadol"}]
        out = build_cards(hook, live_cds=True, iia_safe_block=True)
        self.assertTrue(out["cards"])
        self.assertTrue(all(c.get("suggestions") == [] for c in out["cards"]))
        self.assertIn("nem elérhető", json.dumps(out, ensure_ascii=False))
        blob = json.dumps(out, ensure_ascii=False)
        self.assertNotIn("dose_mg", blob)

    def test_iia_safe_off_does_not_invent_codeine_row(self) -> None:
        hook = _hook(atc="R05DA04")
        hook["prefetch"]["medications"] = [{"code": "R05DA04", "inn": "codeine"}]
        out = build_cards(hook, live_cds=True, iia_safe_block=False)
        blob = json.dumps(out, ensure_ascii=False)
        self.assertNotIn("dose_mg", blob)
        self.assertNotIn("szegény metabolizáló", blob)

    def test_http_on_order_sign(self) -> None:
        httpd = bind_cds_server(live_cds=True)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        port = httpd.server_address[1]
        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/cds-services/pgx-order-select",
                data=json.dumps(_hook()).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(resp.headers.get("X-PCE-LIVE-CDS"), "true")
            self.assertTrue(body["cards"])
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/.well-known/smart-configuration") as resp:
                smart = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(smart["live_cds"])
        finally:
            httpd.shutdown()
            httpd.server_close()


class IiaSafeMechanismTests(unittest.TestCase):
    """Behaviour of the G §2.4 kill-switch: mechanism families, not INN literals."""

    def test_families_are_named_mechanisms(self) -> None:
        ids = {f.mechanism_id for f in IIA_SAFE_FAMILIES}
        self.assertEqual(
            ids,
            {
                "DPYD-fluoropyrimidine",
                "CYP2C19-clopidogrel",
                "TPMT-NUDT15-thiopurine",
                "CYP2D6-opioid",
                "HLA-B-1502-aromatic-anticonvulsant",
            },
        )
        self.assertIn("N02AX02", IIA_SAFE_ATC5)
        self.assertIn("L01BC03", IIA_SAFE_ATC5)
        self.assertIn("L01BB03", IIA_SAFE_ATC5)
        self.assertIn("N03AF", IIA_SAFE_ATC_PREFIXES)
        self.assertNotIn("L01BC", IIA_SAFE_ATC_PREFIXES)
        self.assertNotIn("L01BB", IIA_SAFE_ATC_PREFIXES)

    def test_blocks_audit_matrix(self) -> None:
        blocked = (
            ({"code": "B01AC04", "inn": "clopidogrel"}, "CYP2C19-clopidogrel"),
            ({"code": "L01BC06", "inn": "capecitabine"}, "DPYD-fluoropyrimidine"),
            ({"code": "R05DA04", "inn": "codeine"}, "CYP2D6-opioid"),
            ({"code": "N03AF01", "inn": "carbamazepine"}, "HLA-B-1502-aromatic-anticonvulsant"),
            ({"code": "L04AX01", "inn": "azathioprine"}, "TPMT-NUDT15-thiopurine"),
            ({"display": "5-FU infúzió"}, "DPYD-fluoropyrimidine"),
            ({"code": "N02AX02", "inn": "tramadol"}, "CYP2D6-opioid"),
            ({"code": "L01BC03", "inn": "tegafur"}, "DPYD-fluoropyrimidine"),
            ({"code": "L01BB03", "inn": "tioguanine"}, "TPMT-NUDT15-thiopurine"),
            ({"code": "N03AB02", "inn": "phenytoin"}, "HLA-B-1502-aromatic-anticonvulsant"),
            ({"display": "Klopidogrel Actavis 75 mg"}, "CYP2C19-clopidogrel"),
            ({"inn_hu": "karbamazepin"}, "HLA-B-1502-aromatic-anticonvulsant"),
            ({"inn_hu": "azatioprin"}, "TPMT-NUDT15-thiopurine"),
            ({"inn_hu": "merkaptopurin"}, "TPMT-NUDT15-thiopurine"),
            ({"inn_hu": "kapecitabin"}, "DPYD-fluoropyrimidine"),
            ({"inn_hu": "kodein"}, "CYP2D6-opioid"),
            ({"inn_hu": "fenitoin"}, "HLA-B-1502-aromatic-anticonvulsant"),
            ({"code": "N03AF02"}, "HLA-B-1502-aromatic-anticonvulsant"),
            ({"code": "N03AF03"}, "HLA-B-1502-aromatic-anticonvulsant"),
        )
        for med, family in blocked:
            with self.subTest(med=med):
                self.assertTrue(is_iia_safe_med(med), msg=med)
                self.assertTrue(blocked_live_pairing(med, block=True))
                self.assertIn(family, matching_families(med))

    def test_does_not_block_outside_the_five_mechanisms(self) -> None:
        allowed = (
            {"code": "N06AB05", "inn": "paroxetine"},
            {"code": "L01BC05", "inn": "gemcitabine"},
            {"code": "L01BB05", "inn": "fludarabine"},
            {"code": "M04AA01", "inn": "allopurinol"},
            {"code": "N02AA01", "inn": "morphine"},
            {"code": "C07AB02", "inn": "metoprolol"},
        )
        for med in allowed:
            with self.subTest(med=med):
                self.assertFalse(is_iia_safe_med(med), msg=med)
                self.assertFalse(blocked_live_pairing(med, block=True))

    def test_hungarian_brand_does_not_need_english_inn(self) -> None:
        self.assertTrue(is_iia_safe_med({"name": "Klopidogrel Actavis 75 mg"}))
        self.assertFalse(is_iia_safe_med({"name": "Paroxetin Actavis 20 mg"}))

    def test_ba_reaudit_block_pass_and_hungarian_names(self) -> None:
        """BA 2026-08-16 matrix: 13 blocked, 6 pass, 7 HU display without ATC."""
        blocked = (
            {"code": "R05DA04", "inn": "codeine"},
            {"code": "N02AX02", "inn": "tramadol"},
            {"code": "L01BC02", "inn": "fluorouracil"},
            {"code": "L01BC06", "inn": "capecitabine"},
            {"code": "L01BC03", "inn": "tegafur"},
            {"code": "L04AX01", "inn": "azathioprine"},
            {"code": "L01BB02", "inn": "mercaptopurine"},
            {"code": "L01BB03", "inn": "thioguanine"},
            {"code": "N03AF01", "inn": "carbamazepine"},
            {"code": "N03AF02", "inn": "oxcarbazepine"},
            {"code": "N03AB02", "inn": "phenytoin"},
            {"code": "N03AB05", "inn": "fosphenytoin"},
            {"code": "B01AC04", "inn": "clopidogrel"},
        )
        self.assertEqual(len(blocked), 13)
        for med in blocked:
            with self.subTest(block=med):
                self.assertTrue(is_iia_safe_med(med), msg=med)

        allowed = (
            {"code": "N06AB05", "inn": "paroxetine"},
            {"code": "L01BC05", "inn": "gemcitabine"},
            {"code": "L01BB05", "inn": "fludarabine"},
            {"code": "L01BC01", "inn": "cytarabine"},
            {"code": "L01BB04", "inn": "cladribine"},
            {"code": "N06AB06", "inn": "sertraline"},
        )
        self.assertEqual(len(allowed), 6)
        for med in allowed:
            with self.subTest(pass_=med):
                self.assertFalse(is_iia_safe_med(med), msg=med)

        hungarian = (
            "Klopidogrel Actavis 75 mg",
            "Karbamazepin Teva 200mg",
            "Azatioprin retard",
            "Kodein-foszfát",
            "Tramadol-hidroklorid",
            "Kapecitabin Accord",
            "5-FU infúzió",
        )
        self.assertEqual(len(hungarian), 7)
        for name in hungarian:
            with self.subTest(hu=name):
                self.assertTrue(is_iia_safe_med({"name": name}), msg=name)

    def test_who_pins_cover_new_atc5(self) -> None:
        official = ROOT / "docs" / "pce" / "Sources" / "official"
        checks = (
            ("whocc-atc-n02ax02.html", "N02AX02", "tramadol"),
            ("whocc-atc-l01bc03.html", "L01BC03", "tegafur"),
            ("whocc-atc-l01bb03.html", "L01BB03", "tioguanine"),
            ("whocc-atc-n03ab02.html", "N03AB02", "phenytoin"),
            ("whocc-atc-n03af02.html", "N03AF02", "oxcarbazepine"),
            ("whocc-atc-b01ac04.html", "B01AC04", "clopidogrel"),
            ("whocc-atc-l01bc01.html", "L01BC01", "cytarabine"),
            ("whocc-atc-l01bc05.html", "L01BC05", "gemcitabine"),
            ("whocc-atc-l01bb04.html", "L01BB04", "cladribine"),
            ("whocc-atc-l01bb05.html", "L01BB05", "fludarabine"),
        )
        for name, code, inn in checks:
            blob = (official / name).read_text(encoding="utf-8", errors="replace").lower()
            with self.subTest(name=name):
                self.assertIn(code.lower(), blob)
                self.assertIn(inn.lower(), blob)

    def test_l01bc_prefix_would_false_positive_on_pinned_who(self) -> None:
        official = ROOT / "docs" / "pce" / "Sources" / "official"
        gem = (official / "whocc-atc-l01bc05.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("Pyrimidine analogues", gem)
        self.assertIn("L01BC05", gem)
        self.assertIn("gemcitabine", gem.lower())
        cla = (official / "whocc-atc-l01bb04.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("Purine analogues", cla)
        self.assertIn("L01BB04", cla)
        self.assertIn("cladribine", cla.lower())
        self.assertNotIn("L01BC", IIA_SAFE_ATC_PREFIXES)
        self.assertNotIn("L01BB", IIA_SAFE_ATC_PREFIXES)
        self.assertFalse(is_iia_safe_med({"code": "L01BC05"}))
        self.assertFalse(is_iia_safe_med({"code": "L01BC01"}))
        self.assertFalse(is_iia_safe_med({"code": "L01BB04"}))
        self.assertFalse(is_iia_safe_med({"code": "L01BB05"}))


class IsolationFromF1Tests(unittest.TestCase):
    def test_report_package_does_not_import_cds(self) -> None:
        import ast

        src_root = ROOT / "src" / "pce_report"
        for path in src_root.rglob("*.py"):
            blob = path.read_text(encoding="utf-8")
            self.assertNotIn("pce_cds", blob, msg=str(path))
            tree = ast.parse(blob, filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    self.assertFalse(node.module.startswith("pce_cds"))

    def test_clinical_package_does_not_import_cds(self) -> None:
        src_root = ROOT / "src" / "pce_clinical"
        for path in src_root.rglob("*.py"):
            self.assertNotIn("pce_cds", path.read_text(encoding="utf-8"), msg=str(path))


if __name__ == "__main__":
    unittest.main()
