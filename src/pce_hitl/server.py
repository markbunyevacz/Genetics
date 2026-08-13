"""HTTP API for /v1/hitl/** (B.4.6). Separate process from pce_clinical."""
from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pce_clinical.auth import HITL, parse_role, require_role
from pce_clinical.errors import ClinicalError
from pce_hitl.errors import HitlError
from pce_hitl.service import HitlService
from pce_hitl.store import HitlStore

UI_PATH = Path(__file__).resolve().parents[1] / "pce_ui" / "hitl.html"
INF_RE = re.compile(r"^/v1/hitl/inferences/([^/]+)(/.*)?$")


def _json_bytes(body: dict[str, Any] | list[Any], status: int = 200) -> tuple[int, bytes, str]:
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    return status, raw, "application/json; charset=utf-8"


def handle_request(
    svc: HitlService,
    method: str,
    path: str,
    headers: Any,
    raw: bytes,
) -> tuple[int, bytes, str]:
    route = urlparse(path).path
    auth = headers.get("Authorization") if hasattr(headers, "get") else None
    ctype = (headers.get("Content-Type") if hasattr(headers, "get") else "") or ""

    if route in {"/", "/ui", "/ui/"} and method == "GET":
        html = UI_PATH.read_text(encoding="utf-8") if UI_PATH.is_file() else "<p>missing UI</p>"
        return 200, html.encode("utf-8"), "text/html; charset=utf-8"

    role = parse_role(auth)
    if role == "clinician" or role not in HITL:
        err = ClinicalError("E-ISO-001")
        return err.http, json.dumps(err.as_dict()).encode("utf-8"), "application/json"

    try:
        body: dict[str, Any] = {}
        if raw and "json" in ctype.lower():
            loaded = json.loads(raw.decode("utf-8") or "{}")
            if isinstance(loaded, dict):
                body = loaded

        if route == "/v1/hitl/inferences" and method == "GET":
            require_role(auth, HITL)
            return _json_bytes(svc.list_cards())

        m = INF_RE.match(route)
        if not m:
            return 404, json.dumps({"error": "not_found", "http": 404}).encode("utf-8"), "application/json"
        inf_id, rest = m.group(1), m.group(2) or ""

        if rest == "" and method == "GET":
            require_role(auth, HITL)
            return _json_bytes(svc.get_card(inf_id))
        if rest == "/blind" and method == "POST":
            reviewer = require_role(auth, frozenset({"hitl_reviewer"}))
            return _json_bytes(svc.record_blind(inf_id, str(body.get("choice") or ""), reviewer))
        if rest == "/reviews" and method == "POST":
            reviewer = require_role(auth, frozenset({"hitl_reviewer"}))
            return _json_bytes(
                svc.record_review(
                    inf_id,
                    str(body.get("verdict") or ""),
                    str(body.get("reason_code") or ""),
                    reviewer,
                    body.get("note") if isinstance(body.get("note"), str) else None,
                )
            )
        return 404, json.dumps({"error": "not_found", "http": 404}).encode("utf-8"), "application/json"
    except ClinicalError as exc:
        return exc.http, json.dumps(exc.as_dict(), ensure_ascii=False).encode("utf-8"), "application/json"
    except HitlError as exc:
        return exc.http, json.dumps(exc.as_dict(), ensure_ascii=False).encode("utf-8"), "application/json"


def make_handler(svc: HitlService) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

        def _read(self) -> bytes:
            length = int(self.headers.get("Content-Length") or "0")
            return self.rfile.read(length) if length else b""

        def _write(self, status: int, payload: bytes, ctype: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:  # noqa: N802
            status, payload, ctype = handle_request(svc, "GET", self.path, self.headers, b"")
            self._write(status, payload, ctype)

        def do_POST(self) -> None:  # noqa: N802
            status, payload, ctype = handle_request(svc, "POST", self.path, self.headers, self._read())
            self._write(status, payload, ctype)

    return Handler


def bind_hitl_server(
    db_path: str | Path,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
) -> ThreadingHTTPServer:
    store = HitlStore(db_path)
    svc = HitlService(store)
    handler = make_handler(svc)
    return ThreadingHTTPServer((host, port), handler)
