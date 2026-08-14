#!/usr/bin/env python3
"""FR-520 CDS pipe: lock default, ON via parameter, fail-open, IIa-safe kill-switch."""
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
from pce_cds.policy import IIA_SAFE_BLOCK  # noqa: E402
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
