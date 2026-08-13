#!/usr/bin/env python3
"""WP-H — HITL store, B.4.6 API, reviewer-blind UX, isolation from F1+ reports."""
from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pce_clinical.store import ClinicalStore  # noqa: E402
from pce_gateway.config import GatewayConfig  # noqa: E402
from pce_gateway.frequency import FrequencyTable  # noqa: E402
from pce_gateway.ingest import handle_pce_ingest  # noqa: E402
from pce_gateway.kcell import KCellStore  # noqa: E402
from pce_gateway.pipeline import process_his_event  # noqa: E402
from pce_gateway.transform import load_json  # noqa: E402
from pce_hitl.errors import HitlError  # noqa: E402
from pce_hitl.server import bind_hitl_server  # noqa: E402
from pce_hitl.service import HitlService, persist_inference  # noqa: E402
from pce_hitl.store import HitlStore  # noqa: E402

GOLD = ROOT / "tests" / "fixtures" / "gold-v0"
FREQ = FrequencyTable(GOLD / "frequency-config.v0.json")


def _anon_fhir(his_path: Path) -> dict:
    import copy

    bundle = copy.deepcopy(load_json(str(his_path)))
    for entry in bundle.get("entry") or []:
        res = entry.get("resource") or {}
        if res.get("resourceType") == "Patient":
            for k in ("name", "identifier", "telecom", "address", "id"):
                res.pop(k, None)
            bd = res.get("birthDate")
            if isinstance(bd, str) and len(bd) >= 4:
                res["birthDate"] = bd[:4]
        if res.get("resourceType") == "MedicationRequest":
            res["authoredOn"] = "2026-Q3"
            res.pop("dose_mg", None)
            instructions = res.get("dosageInstruction")
            if isinstance(instructions, list):
                for ins in instructions:
                    if isinstance(ins, dict):
                        ins.pop("doseQuantity", None)
                        ins.pop("rateQuantity", None)
                        ins.pop("doseAndRate", None)
            coding = (res.get("medicationCodeableConcept") or {}).get("coding") or []
            for c in coding:
                if isinstance(c, dict) and isinstance(c.get("code"), str) and len(c["code"]) > 5:
                    c["code"] = c["code"][:5]
                    c["display"] = None
    return bundle


def _hitl_store(test: unittest.TestCase) -> HitlStore:
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmp.close()
    path = Path(tmp.name)
    test.addCleanup(lambda: path.exists() and path.unlink())
    return HitlStore(path)


def _clinical_store(test: unittest.TestCase) -> ClinicalStore:
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmp.close()
    path = Path(tmp.name)
    test.addCleanup(lambda: path.exists() and path.unlink())
    return ClinicalStore(path)


def _kcell(test: unittest.TestCase) -> KCellStore:
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmp.close()
    path = Path(tmp.name)
    test.addCleanup(lambda: path.exists() and path.unlink())
    return KCellStore(path)


class PersistTests(unittest.TestCase):
    def test_accepted_ingest_writes_hitl_not_clinical_report(self) -> None:
        hitl = _hitl_store(self)
        clinical = _clinical_store(self)
        bundle = _anon_fhir(GOLD / "gw-v0-01-normal-his-in.json")
        status, body = handle_pce_ingest(
            bundle,
            GatewayConfig(),
            FREQ,
            authorization="gw-ok",
            allowed_accounts={"gw-ok"},
            hitl_store=hitl,
        )
        self.assertEqual(status, 202)
        self.assertTrue(body["hitl"])
        rows = hitl.query("SELECT id, case_display_id, body_json FROM shadow_inference")
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0]["case_display_id"]), 5)
        inf = json.loads(rows[0]["body_json"])
        self.assertEqual(inf["config_id"], "pgx-prepare-12@v0")
        self.assertEqual(inf["clinical_context"], "FHIR")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "INSUFFICIENT_RESOLUTION")
        self.assertEqual(inf["functional_phenotype"], [])
        self.assertEqual(clinical.query("SELECT id FROM report"), [])
        dumped = rows[0]["body_json"]
        self.assertNotIn("SYN-TAJ", dumped)
        self.assertNotIn("SYN-NAME", dumped)
        self.assertNotIn("dose_mg", dumped)

    def test_rare_drop_does_not_write_hitl(self) -> None:
        hitl = _hitl_store(self)
        bundle = _anon_fhir(GOLD / "gw-v0-02-rare-diplotype-his-in.json")
        status, body = handle_pce_ingest(
            bundle,
            GatewayConfig(),
            FREQ,
            authorization="gw-ok",
            allowed_accounts={"gw-ok"},
            hitl_store=hitl,
        )
        self.assertEqual(status, 202)
        self.assertEqual(body["error"], "E-SHADOW-003")
        self.assertFalse(body["hitl"])
        self.assertEqual(hitl.query("SELECT id FROM shadow_inference"), [])

    def test_atc5_writes_hitl(self) -> None:
        hitl = _hitl_store(self)
        bundle = load_json(str(GOLD / "gw-v0-03-atc5-pce-ingest.json"))
        status, body = handle_pce_ingest(
            bundle,
            GatewayConfig(),
            FREQ,
            authorization="gw-ok",
            allowed_accounts={"gw-ok"},
            hitl_store=hitl,
        )
        self.assertEqual(status, 202)
        self.assertTrue(body["hitl"])
        self.assertEqual(len(hitl.query("SELECT id FROM shadow_inference")), 1)

    def test_store_failure_is_fail_open_202(self) -> None:
        class Boom:
            def insert_inference(self, rec: dict) -> None:
                raise RuntimeError("hitl down")

        bundle = _anon_fhir(GOLD / "gw-v0-01-normal-his-in.json")
        status, body = handle_pce_ingest(
            bundle,
            GatewayConfig(),
            FREQ,
            authorization="gw-ok",
            allowed_accounts={"gw-ok"},
            hitl_store=Boom(),
        )
        self.assertEqual(status, 202)
        self.assertTrue(body["hitl"])


class CardAndBlindTests(unittest.TestCase):
    def test_list_hides_motor_and_pii(self) -> None:
        store = _hitl_store(self)
        svc = HitlService(store)
        persist_inference(
            store,
            {
                "diplotypes": [{"gene": "CYP2D6", "diplotype": "*1/*2"}],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "N06AB"}],
            },
        )
        cards = svc.list_cards()
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertNotIn("motor_category", card)
        self.assertNotIn("live_findings", card)
        self.assertNotIn("name", card)
        self.assertNotIn("taj", card)
        self.assertEqual(card["medications"][0]["code"], "N06AB")
        self.assertEqual(len(card["case_display_id"]), 5)
        one = svc.get_card(card["id"])
        self.assertFalse(one["blind_complete"])
        self.assertNotIn("motor_category", one)

    def test_blind_then_review_immutable(self) -> None:
        store = _hitl_store(self)
        svc = HitlService(store)
        rec = persist_inference(
            store,
            {
                "diplotypes": [{"gene": "CYP2D6", "diplotype": "*1/*2"}],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "N06AB05"}],
            },
        )
        with self.assertRaises(HitlError) as ctx:
            svc.record_review(rec["id"], "AGREE", "MATCH", "hitl_reviewer")
        self.assertEqual(ctx.exception.code, "E-HITL-BLIND")
        revealed = svc.record_blind(rec["id"], "CONTINUE", "hitl_reviewer")
        self.assertEqual(revealed["motor_category"], "CONTINUE")
        self.assertEqual(revealed["functional_phenotype"], [])
        done = svc.record_review(rec["id"], "AGREE", "MATCH", "hitl_reviewer", note="forrásolt kategória")
        self.assertEqual(done["verdict"]["verdict"], "AGREE")
        with self.assertRaises(HitlError) as ctx:
            svc.record_blind(rec["id"], "ALTERNATIVE", "hitl_reviewer")
        self.assertEqual(ctx.exception.code, "E-HITL-IMMUTABLE")
        with self.assertRaises(HitlError) as ctx:
            svc.record_review(rec["id"], "DISAGREE", "MISMATCH", "hitl_reviewer")
        self.assertEqual(ctx.exception.code, "E-HITL-IMMUTABLE")

    def test_note_pii_rejected(self) -> None:
        store = _hitl_store(self)
        svc = HitlService(store)
        rec = persist_inference(
            store,
            {
                "diplotypes": [{"gene": "CYP2D6", "diplotype": "*1/*2"}],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "N06AB"}],
            },
        )
        svc.record_blind(rec["id"], "INSUFFICIENT", "hitl_reviewer")
        with self.assertRaises(HitlError) as ctx:
            svc.record_review(
                rec["id"],
                "INSUFFICIENT_DATA",
                "INSUFFICIENT_CONTEXT",
                "hitl_reviewer",
                note="TAJ 123-456-789",
            )
        self.assertEqual(ctx.exception.code, "E-HITL-PII")


class PseudoAtc5PairingTests(unittest.TestCase):
    def test_anon_accepts_seven_char_paroxetine(self) -> None:
        hitl = _hitl_store(self)
        bundle = load_json(str(ROOT / "tests" / "fixtures" / "shadow-v0" / "pseudo-atc5-paroxetine-pce-ingest.json"))
        status, body = handle_pce_ingest(
            bundle,
            GatewayConfig(),
            FREQ,
            authorization="gw-ok",
            allowed_accounts={"gw-ok"},
            hitl_store=hitl,
        )
        self.assertEqual(status, 202)
        rows = hitl.query("SELECT body_json FROM shadow_inference")
        self.assertEqual(len(rows), 1)
        inf = json.loads(rows[0]["body_json"])
        self.assertEqual(inf["live_findings"][0]["drug_atc"], "N06AB05")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONTINUE")
        self.assertEqual(inf["functional_phenotype"], [])
        self.assertFalse(inf["forras_allapot"]["functional_phenotype_iras"]["irtunk_szegeny_metabolizalot"])

    def test_pseudo_research_consent_keeps_paroxetine_code(self) -> None:
        hitl = _hitl_store(self)
        bundle = load_json(str(ROOT / "tests" / "fixtures" / "shadow-v0" / "pseudo-atc5-paroxetine-pce-ingest.json"))
        cfg = GatewayConfig(mode="PSEUDO", research_consent=True, max_atc_level=5)
        status, body = handle_pce_ingest(
            bundle,
            cfg,
            FREQ,
            authorization="gw-ok",
            allowed_accounts={"gw-ok"},
            hitl_store=hitl,
        )
        self.assertEqual(status, 202)
        rows = hitl.query("SELECT body_json FROM shadow_inference")
        self.assertEqual(len(rows), 1)
        inf = json.loads(rows[0]["body_json"])
        self.assertEqual(inf["live_findings"][0]["drug_atc"], "N06AB05")
        self.assertEqual(inf["live_findings"][0]["inn"], "paroxetine")
        self.assertEqual(inf["live_findings"][0]["strategy_category"], "CONTINUE")
        self.assertEqual(inf["genotype_phenotype"][0]["genotype_phenotype"], "NM")
        self.assertEqual(inf["functional_phenotype"], [])
        missing = " ".join(row["hu"] for row in inf["forras_allapot"]["hianyzik"])
        self.assertIn("nincs olyan sor", missing.lower())


class HitlHttpTests(unittest.TestCase):
    def setUp(self) -> None:
        store = _hitl_store(self)
        persist_inference(
            store,
            {
                "diplotypes": [{"gene": "CYP2D6", "diplotype": "*1/*2"}],
                "medications": [{"system": "http://www.whocc.no/atc", "code": "N06AB"}],
            },
        )
        self.httpd = bind_hitl_server(store.path, port=0)
        thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.httpd.shutdown)
        self.addCleanup(self.httpd.server_close)
        self.port = self.httpd.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"

    def _req(self, method: str, path: str, body: dict | None = None, role: str = "hitl_reviewer") -> tuple[int, dict | bytes]:
        data = None
        headers = {"Authorization": role}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
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

    def test_ui_and_clinician_forbidden_and_walk(self) -> None:
        status, html = self._req("GET", "/", role="hitl_reviewer")
        self.assertEqual(status, 200)
        self.assertIn(b"hitl_reviewer", html if isinstance(html, bytes) else html.encode())
        self.assertIn(b"vak", html if isinstance(html, bytes) else html.encode())
        status, body = self._req("GET", "/v1/hitl/inferences", role="clinician")
        self.assertEqual(status, 403)
        self.assertEqual(body["error"], "E-ISO-001")
        status, cards = self._req("GET", "/v1/hitl/inferences")
        self.assertEqual(status, 200)
        self.assertEqual(len(cards), 1)
        inf_id = cards[0]["id"]
        self.assertNotIn("motor_category", cards[0])
        status, _ = self._req("POST", f"/v1/hitl/inferences/{inf_id}/reviews", {"verdict": "AGREE", "reason_code": "MATCH"})
        self.assertEqual(status, 409)
        status, revealed = self._req("POST", f"/v1/hitl/inferences/{inf_id}/blind", {"choice": "CONTINUE"})
        self.assertEqual(status, 200)
        self.assertIn("motor_category", revealed)
        status, done = self._req(
            "POST",
            f"/v1/hitl/inferences/{inf_id}/reviews",
            {"verdict": "AGREE", "reason_code": "MATCH"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(done["verdict"]["verdict"], "AGREE")


class F1sDataflowTests(unittest.TestCase):
    def test_his_gateway_ingest_hitl_report_untouched(self) -> None:
        his = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        kcell = _kcell(self)
        kcell.seed("UNCERTAIN", "N06AB10", "2026-Q3", 4)
        gw = process_his_event(his, GatewayConfig(), FREQ, kcell)
        self.assertEqual(gw.http, 202)
        self.assertTrue(gw.hitl)
        self.assertIsNotNone(gw.event)
        hitl = _hitl_store(self)
        clinical = _clinical_store(self)
        status, body = handle_pce_ingest(
            gw.event,
            GatewayConfig(),
            FREQ,
            authorization="gw-ok",
            allowed_accounts={"gw-ok"},
            hitl_store=hitl,
        )
        self.assertEqual(status, 202)
        self.assertTrue(body["hitl"])
        svc = HitlService(hitl)
        cards = svc.list_cards()
        self.assertEqual(len(cards), 1)
        svc.record_blind(cards[0]["id"], "INSUFFICIENT", "hitl_reviewer")
        svc.record_review(
            cards[0]["id"],
            "INSUFFICIENT_DATA",
            "INSUFFICIENT_CONTEXT",
            "hitl_reviewer",
        )
        self.assertEqual(clinical.query("SELECT id FROM report"), [])
        taj = load_json(str(GOLD / "gw-v0-08-taj-pce-ingest.json"))
        status, body = handle_pce_ingest(
            taj,
            GatewayConfig(),
            FREQ,
            authorization="gw-ok",
            allowed_accounts={"gw-ok"},
            hitl_store=hitl,
        )
        self.assertEqual(status, 400)
        self.assertEqual(len(hitl.query("SELECT id FROM shadow_inference")), 1)


if __name__ == "__main__":
    unittest.main()
