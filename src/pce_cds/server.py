"""HTTP for CDS Hooks + SMART stub. Not mounted on pce_clinical (FR-470)."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pce_cds.cards import build_cards, live_discovery, lock_discovery
from pce_cds.policy import IIA_SAFE_BLOCK
from pce_cds.smart import smart_configuration

UI_PATH = Path(__file__).resolve().parents[1] / "pce_ui" / "cds.html"

HOOKS = {
    "/cds-services/pgx-order-sign": "order-sign",
    "/cds-services/pgx-order-select": "order-select",
}


def _json_bytes(body: dict[str, Any], status: int = 200) -> tuple[int, bytes, str]:
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    return status, raw, "application/json; charset=utf-8"


def handle_request(
    method: str,
    path: str,
    raw: bytes,
    *,
    live_cds: bool,
    iia_safe_block: bool = IIA_SAFE_BLOCK,
) -> tuple[int, bytes, str]:
    route = urlparse(path).path

    if route in {"/", "/ui", "/ui/"} and method == "GET":
        html = UI_PATH.read_text(encoding="utf-8") if UI_PATH.is_file() else "<p>missing UI</p>"
        return 200, html.encode("utf-8"), "text/html; charset=utf-8"

    if route == "/cds-services" and method == "GET":
        body = live_discovery() if live_cds else lock_discovery()
        return _json_bytes(body)

    if route == "/.well-known/smart-configuration" and method == "GET":
        return _json_bytes(smart_configuration(live_cds=live_cds))

    if route in HOOKS and method == "POST":
        payload: dict[str, Any] = {}
        if raw:
            loaded = json.loads(raw.decode("utf-8") or "{}")
            if isinstance(loaded, dict):
                payload = loaded
        payload.setdefault("hook", HOOKS[route])
        cards = build_cards(payload, live_cds=live_cds, iia_safe_block=iia_safe_block)
        return _json_bytes(cards)

    return 404, json.dumps({"error": "not_found", "http": 404}).encode("utf-8"), "application/json"


def make_handler(*, live_cds: bool, iia_safe_block: bool = IIA_SAFE_BLOCK) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

        def _read(self) -> bytes:
            length = int(self.headers.get("Content-Length") or "0")
            return self.rfile.read(length) if length else b""

        def _write(self, status: int, payload: bytes, ctype: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("X-PCE-LIVE-CDS", "true" if live_cds else "false")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:  # noqa: N802
            status, payload, ctype = handle_request(
                "GET", self.path, b"", live_cds=live_cds, iia_safe_block=iia_safe_block
            )
            self._write(status, payload, ctype)

        def do_POST(self) -> None:  # noqa: N802
            status, payload, ctype = handle_request(
                "POST", self.path, self._read(), live_cds=live_cds, iia_safe_block=iia_safe_block
            )
            self._write(status, payload, ctype)

    return Handler


def bind_cds_server(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    live_cds: bool,
    iia_safe_block: bool = IIA_SAFE_BLOCK,
) -> ThreadingHTTPServer:
    handler = make_handler(live_cds=live_cds, iia_safe_block=iia_safe_block)
    return ThreadingHTTPServer((host, port), handler)
