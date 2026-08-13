"""Local HTTP ingest for POST /v1/shadow/events (PCE-GW-461-09)."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from pce_gateway.config import GatewayConfig
from pce_gateway.frequency import FrequencyTable
from pce_gateway.ingest import handle_pce_ingest


def make_ingest_handler(
    cfg: GatewayConfig,
    freq: FrequencyTable | None,
    allowed_accounts: set[str],
) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

        def do_POST(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path != "/v1/shadow/events":
                self._send(404, {"error": "not_found", "http": 404})
                return
            length = int(self.headers.get("Content-Length") or "0")
            raw = self.rfile.read(length)
            try:
                bundle = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                self._send(400, {"error": "E-SHADOW-001", "reason": "invalid JSON", "hitl": False})
                return
            if not isinstance(bundle, dict):
                self._send(400, {"error": "E-SHADOW-001", "reason": "JSON object required", "hitl": False})
                return
            status, body = handle_pce_ingest(
                bundle,
                cfg,
                freq,
                authorization=self.headers.get("Authorization"),
                allowed_accounts=allowed_accounts,
            )
            self._send(status, body)

        def _send(self, status: int, body: dict[str, Any]) -> None:
            payload = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    return Handler


def bind_ingest_server(
    cfg: GatewayConfig,
    freq: FrequencyTable | None,
    allowed_accounts: set[str],
    *,
    host: str = "127.0.0.1",
    port: int = 0,
) -> ThreadingHTTPServer:
    handler = make_ingest_handler(cfg, freq, allowed_accounts)
    return ThreadingHTTPServer((host, port), handler)
