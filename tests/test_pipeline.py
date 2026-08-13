#!/usr/bin/env python3
"""PCE-GW-461-04..10, ingest account, LIVE_CDS freeze — Gold V0."""
from __future__ import annotations

import copy
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

from pce_gateway.config import GatewayConfig, KThresholdRejected  # noqa: E402
from pce_gateway.flags import LIVE_CDS  # noqa: E402
from pce_gateway.frequency import FrequencyTable  # noqa: E402
from pce_gateway.ingest import handle_pce_ingest  # noqa: E402
from pce_gateway.kcell import KCellStore  # noqa: E402
from pce_gateway.pipeline import process_his_event  # noqa: E402
from pce_gateway.server import bind_ingest_server  # noqa: E402
from pce_gateway.transform import load_json  # noqa: E402

GOLD = ROOT / "tests" / "fixtures" / "gold-v0"
FREQ = FrequencyTable(GOLD / "frequency-config.v0.json")


def _anon_fhir(his_path: Path) -> dict:
    """Valid ANON ingest: no Patient PII, ATC4, quarter authoredOn, genetics kept."""
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


def _store(test: unittest.TestCase) -> KCellStore:
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmp.close()
    path = Path(tmp.name)
    test.addCleanup(lambda: path.exists() and path.unlink())
    return KCellStore(path)


class FrequencyTests(unittest.TestCase):
    def test_keep_and_rare(self) -> None:
        self.assertFalse(FREQ.is_below_threshold("CYP2D6", "*1/*2"))
        self.assertTrue(FREQ.is_below_threshold("CYP2D6", "*6/*6"))
        self.assertTrue(FREQ.is_rarest("CYP2D6", "*3x2/*3x2"))
        self.assertFalse(FREQ.is_rarest("CYP2D6", "*6/*6"))
        self.assertEqual(FREQ.coarsen_class("CYP2D6", "*4/*4"), "REDUCED")
        self.assertEqual(FREQ.coarsen_class("CYP2D6", "*1/*2"), "UNCERTAIN")
        self.assertTrue(FREQ.is_below_threshold("CYP2D6", "*unknown/*unknown"))


class LiveCdsTests(unittest.TestCase):
    def test_compile_time_false(self) -> None:
        self.assertIs(LIVE_CDS, False)
        src = (ROOT / "src" / "pce_gateway" / "flags.py").read_text(encoding="utf-8")
        self.assertIn("LIVE_CDS: bool = False", src)


class KOverrideTests(unittest.TestCase):
    def test_reject_decrease(self) -> None:
        cfg = GatewayConfig()
        with self.assertRaises(KThresholdRejected):
            cfg.with_k(3)
        with self.assertRaises(KThresholdRejected):
            cfg.with_k(4)
        raised = cfg.with_k(10)
        self.assertEqual(raised.k, 10)


class PipelineGoldTests(unittest.TestCase):
    def test_v0_01_raw_when_cell_meets_k(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        store = _store(self)
        store.seed("UNCERTAIN", "N06AB", "2026-Q3", 4)
        cfg = GatewayConfig()
        result = process_his_event(bundle, cfg, FREQ, store)
        self.assertFalse(result.suppressed)
        assert result.event is not None
        self.assertEqual(result.event["diplotype_granularity"], "RAW")
        self.assertEqual(result.event["diplotypes"][0]["diplotype"], "*1/*2")
        self.assertNotIn("patient", result.event)
        self.assertIsNone(result.event.get("cell_count"))

    def test_v0_01_coarsen_when_cell_small(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        store = _store(self)
        cfg = GatewayConfig(on_small_cell="COARSEN")
        result = process_his_event(bundle, cfg, FREQ, store)
        assert result.event is not None
        self.assertEqual(result.event["diplotype_granularity"], "CLASS")
        self.assertEqual(result.event["phenotype_class"], "UNCERTAIN")
        self.assertIsNone(result.event["raw_diplotype"])

    def test_v0_04_small_cell_coarsen(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-04-small-cell-his-in.json"))
        store = _store(self)
        store.seed("REDUCED", "N06AB", "2026-Q3", 3)
        cfg = GatewayConfig(on_small_cell="COARSEN")
        result = process_his_event(bundle, cfg, FREQ, store)
        self.assertTrue(result.hitl)
        assert result.event is not None
        self.assertEqual(result.event["diplotype_granularity"], "CLASS")
        self.assertEqual(result.event["phenotype_class"], "REDUCED")
        self.assertIsNone(result.event["raw_diplotype"])

    def test_v0_05_small_cell_drop(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-04-small-cell-his-in.json"))
        store = _store(self)
        store.seed("REDUCED", "N06AB", "2026-Q3", 3)
        cfg = GatewayConfig(on_small_cell="DROP")
        result = process_his_event(bundle, cfg, FREQ, store)
        self.assertTrue(result.suppressed)
        self.assertEqual(result.error, "E-SHADOW-003")
        self.assertFalse(result.hitl)
        self.assertEqual(result.http, 202)

    def test_v0_02_rare_drop(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-02-rare-diplotype-his-in.json"))
        store = _store(self)
        store.seed("REDUCED", "N06AB", "2026-Q3", 20)
        cfg = GatewayConfig(on_rare="DROP")
        result = process_his_event(bundle, cfg, FREQ, store)
        self.assertTrue(result.suppressed)
        self.assertEqual(result.error, "E-SHADOW-003")

    def test_v0_02_rare_coarsen(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-02-rare-diplotype-his-in.json"))
        store = _store(self)
        store.seed("REDUCED", "N06AB", "2026-Q3", 20)
        cfg = GatewayConfig(on_rare="COARSEN")
        result = process_his_event(bundle, cfg, FREQ, store)
        assert result.event is not None
        self.assertEqual(result.event["phenotype_class"], "REDUCED")
        self.assertEqual(result.event["diplotype_granularity"], "CLASS")

    def test_v0_06_rarest_always_drop(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-06-rarest-his-in.json"))
        store = _store(self)
        store.seed("REDUCED", "N06AB", "2026-Q3", 100)
        cfg = GatewayConfig(on_rare="COARSEN", on_small_cell="COARSEN")
        result = process_his_event(bundle, cfg, FREQ, store)
        self.assertTrue(result.suppressed)
        self.assertEqual(result.error, "E-SHADOW-003")

    def test_monitor_has_no_pii(self) -> None:
        store = _store(self)
        store.seed("REDUCED", "N06AB", "2026-Q3", 4)
        store.record_drop("2026-Q3")
        report = store.quarterly_report("2026-Q3")
        blob = str(report)
        self.assertNotIn("SYN-TAJ", blob)
        self.assertNotIn("*4/*4", blob)
        self.assertEqual(report["report_type"], "A14_quarterly_monitor")
        self.assertTrue(report["g3_recall_drop_does_not_disable_suppression"])


class PceIngestTests(unittest.TestCase):
    def test_wrong_account(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-03-atc5-pce-ingest.json"))
        cfg = GatewayConfig()
        status, body = handle_pce_ingest(
            bundle, cfg, FREQ, authorization="nope", allowed_accounts={"gw-ok"}
        )
        self.assertEqual(status, 403)
        self.assertEqual(body["error"], "E-SHADOW-002")

    def test_atc5_with_account(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-03-atc5-pce-ingest.json"))
        cfg = GatewayConfig()
        status, body = handle_pce_ingest(
            bundle, cfg, FREQ, authorization="gw-ok", allowed_accounts={"gw-ok"}
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "E-SHADOW-001")
        self.assertFalse(body["hitl"])

    def test_rare_raw_genetics_on_ingest(self) -> None:
        bundle = _anon_fhir(GOLD / "gw-v0-02-rare-diplotype-his-in.json")
        cfg = GatewayConfig()
        status, body = handle_pce_ingest(
            bundle, cfg, FREQ, authorization="gw-ok", allowed_accounts={"gw-ok"}
        )
        self.assertEqual(status, 202)
        self.assertEqual(body["error"], "E-SHADOW-003")
        self.assertFalse(body["hitl"])

    def test_called_common_diplotype_accepted(self) -> None:
        bundle = _anon_fhir(GOLD / "gw-v0-01-normal-his-in.json")
        cfg = GatewayConfig()
        status, body = handle_pce_ingest(
            bundle, cfg, FREQ, authorization="gw-ok", allowed_accounts={"gw-ok"}
        )
        self.assertEqual(status, 202)
        self.assertEqual(body["ingest"], "accepted")
        self.assertTrue(body["hitl"])


class KCellIncrementTests(unittest.TestCase):
    def test_drop_does_not_increment_cell(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-04-small-cell-his-in.json"))
        store = _store(self)
        store.seed("REDUCED", "N06AB", "2026-Q3", 3)
        cfg = GatewayConfig(on_small_cell="DROP")
        process_his_event(bundle, cfg, FREQ, store)
        self.assertEqual(store.peek("REDUCED", "N06AB", "2026-Q3"), 3)

    def test_forward_increments_once(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        store = _store(self)
        store.seed("UNCERTAIN", "N06AB", "2026-Q3", 4)
        cfg = GatewayConfig()
        process_his_event(bundle, cfg, FREQ, store)
        self.assertEqual(store.peek("UNCERTAIN", "N06AB", "2026-Q3"), 5)


class KOverrideFixtureTests(unittest.TestCase):
    def test_v0_07_reject_from_fixture(self) -> None:
        spec = load_json(str(GOLD / "gw-v0-07-k-override-reject.json"))
        cfg = GatewayConfig(k=spec["reject"]["current_k"])
        with self.assertRaises(KThresholdRejected):
            cfg.with_k(spec["reject"]["requested_k"])
        raised = cfg.with_k(spec["allow_via_config_release"]["requested_k"])
        self.assertEqual(raised.k, 10)


class HttpIngestTests(unittest.TestCase):
    def test_post_shadow_events(self) -> None:
        cfg = GatewayConfig()
        httpd = bind_ingest_server(cfg, FREQ, {"gw-ok"}, port=0)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(httpd.shutdown)
        self.addCleanup(httpd.server_close)
        port = httpd.server_address[1]
        atc5 = load_json(str(GOLD / "gw-v0-03-atc5-pce-ingest.json"))
        data = json.dumps(atc5).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/shadow/events",
            data=data,
            method="POST",
            headers={"Content-Type": "application/json", "Authorization": "gw-ok"},
        )
        try:
            urllib.request.urlopen(req, timeout=5)
            self.fail("ATC5 ingest must not be 2xx")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)
            body = json.loads(e.read().decode("utf-8"))
            self.assertEqual(body["error"], "E-SHADOW-001")
        req_forbidden = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/shadow/events",
            data=data,
            method="POST",
            headers={"Content-Type": "application/json", "Authorization": "nope"},
        )
        try:
            urllib.request.urlopen(req_forbidden, timeout=5)
            self.fail("wrong account must not be 2xx")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 403)


if __name__ == "__main__":
    unittest.main()

