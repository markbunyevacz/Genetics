"""HTTP API for the clinical path (B.3 / B.4) plus isolation 404/403."""
from __future__ import annotations

import json
import re
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from pce_clinical.auth import (
    DPO,
    HITL,
    READ_REPORT,
    WRITE_CASE,
    WRITE_CONSENT,
    WRITE_REPORT,
    parse_role,
    require_role,
)
from pce_clinical.errors import ClinicalError
from pce_clinical.service import ClinicalService
from pce_clinical.store import ClinicalStore

UI_PATH = Path(__file__).resolve().parents[1] / "pce_ui" / "index.html"

CASE_RE = re.compile(r"^/v1/cases/([^/]+)(/.*)?$")
SUBJECT_RE = re.compile(r"^/v1/subjects/([^/]+)(/.*)?$")


def _json_bytes(body: dict[str, Any] | list[Any] | str, status: int = 200) -> tuple[int, bytes, str]:
    if isinstance(body, str):
        raw = body.encode("utf-8")
        return status, raw, "application/json; charset=utf-8"
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    return status, raw, "application/json; charset=utf-8"


def handle_request(
    svc: ClinicalService,
    method: str,
    path: str,
    headers: Any,
    raw: bytes,
) -> tuple[int, bytes, str]:
    parsed = urlparse(path)
    route = parsed.path
    query = parse_qs(parsed.query)
    auth = headers.get("Authorization") if hasattr(headers, "get") else None
    ctype = (headers.get("Content-Type") if hasattr(headers, "get") else "") or ""

    if route in {"/", "/ui", "/ui/"} and method == "GET":
        html = UI_PATH.read_text(encoding="utf-8") if UI_PATH.is_file() else "<p>missing UI</p>"
        return 200, html.encode("utf-8"), "text/html; charset=utf-8"

    if route.startswith("/cds-services/"):
        err = ClinicalError("E-ISO-002")
        return err.http, json.dumps(err.as_dict()).encode("utf-8"), "application/json"

    if route.startswith("/v1/hitl/") or route.startswith("/v1/shadow/"):
        role = parse_role(auth)
        if role == "clinician" or role not in HITL:
            err = ClinicalError("E-ISO-001")
            return err.http, json.dumps(err.as_dict()).encode("utf-8"), "application/json"
        err = ClinicalError("E-ISO-001", http=404, message_hu="HITL store nincs ezen a clinical processen (külön pce_hitl).")
        return 404, json.dumps(err.as_dict()).encode("utf-8"), "application/json"

    try:
        body: dict[str, Any] = {}
        if raw and "json" in ctype.lower():
            loaded = json.loads(raw.decode("utf-8") or "{}")
            if isinstance(loaded, dict):
                body = loaded

        if route == "/v1/orgs" and method == "POST":
            role = require_role(auth, WRITE_CASE)
            return _json_bytes(svc.create_org(body, role), 201)

        if route == "/v1/subjects" and method == "POST":
            role = require_role(auth, WRITE_CASE)
            return _json_bytes(svc.create_subject(body, role), 201)

        if route == "/v1/cases" and method == "POST":
            role = require_role(auth, WRITE_CASE)
            return _json_bytes(svc.create_case(body, role), 201)

        if route == "/v1/audit/export" and method == "GET":
            require_role(auth, DPO)
            fmt = (query.get("format") or ["json"])[0]
            payload = svc.export_audit(fmt)
            mime = "text/csv" if fmt == "csv" else "application/json"
            return 200, payload.encode("utf-8"), mime

        if route == "/v1/audit/tamper" and method == "POST":
            require_role(auth, DPO)
            svc.try_update_audit()
            return _json_bytes({"ok": True})

        m_subj = SUBJECT_RE.match(route)
        if m_subj:
            sid, rest = m_subj.group(1), m_subj.group(2) or ""
            if rest == "/withdraw" and method == "POST":
                role = require_role(auth, DPO)
                return _json_bytes(svc.withdraw_subject(sid, role))
            if rest.startswith("/certificates/") and method == "GET":
                require_role(auth, DPO)
                cert_id = rest.rsplit("/", 1)[-1]
                return _json_bytes(svc.get_certificate(cert_id))

        m = CASE_RE.match(route)
        if not m:
            err = {"error": "not_found", "http": 404}
            return 404, json.dumps(err).encode("utf-8"), "application/json"
        case_id, rest = m.group(1), m.group(2) or ""

        if rest == "/counselling" and method == "POST":
            role = require_role(auth, WRITE_CONSENT)
            return _json_bytes(svc.add_counselling(case_id, body, role), 201)
        if rest == "/consent" and method == "POST":
            role = require_role(auth, WRITE_CONSENT)
            return _json_bytes(svc.add_consent(case_id, body, role), 201)
        if rest == "/outside-calls" and method == "POST":
            role = require_role(auth, WRITE_CASE)
            items = svc.parse_outside_payload(raw, ctype)
            return _json_bytes(svc.add_outside_calls(case_id, items, role), 201)
        if rest == "/files" and method == "POST":
            role = require_role(auth, WRITE_CASE)
            sample_id = (query.get("sample_id") or [None])[0]
            length = int(headers.get("Content-Length") or len(raw))
            if length > 5 * 1024 * 1024 * 1024:
                raise ClinicalError("E-VCF-004")
            return _json_bytes(svc.add_vcf(case_id, raw, role, sample_id=sample_id), 201)
        if rest == "/clinical-context" and method == "PUT":
            role = require_role(auth, WRITE_CASE)
            return _json_bytes(svc.put_clinical_context(case_id, body, role))
        if rest == "/resolve-call" and method == "POST":
            role = require_role(auth, WRITE_CASE)
            return _json_bytes(svc.resolve_call(case_id, body.get("source") or "", role))
        if rest == "/reports" and method == "POST":
            role = require_role(auth, WRITE_REPORT)
            skip = bool(body.get("skip_consent"))
            return _json_bytes(
                svc.create_report(case_id, role, skip_consent=skip, role=role),
                201,
            )
        if rest == "/explanation" and method == "GET":
            require_role(auth, READ_REPORT)
            rid = (query.get("report_id") or [None])[0]
            return _json_bytes(svc.get_explanation(case_id, rid))

        rm = re.match(r"^/reports/([^/]+)(.*)$", rest)
        if rm:
            rid, tail = rm.group(1), rm.group(2) or ""
            if tail == "" and method == "GET":
                require_role(auth, READ_REPORT)
                return _json_bytes(svc.get_report(case_id, rid))
            if tail == "/fhir" and method == "GET":
                require_role(auth, READ_REPORT)
                return _json_bytes(svc.get_report_fhir(case_id, rid))
            if tail == "/pdf" and method == "GET":
                require_role(auth, READ_REPORT)
                tmp = Path(tempfile.mkdtemp()) / "report.pdf"
                svc.write_report_pdf(case_id, rid, tmp)
                return 200, tmp.read_bytes(), "application/pdf"
            if tail == "/sign" and method == "POST":
                role = require_role(auth, WRITE_REPORT)
                return _json_bytes(svc.sign_report(case_id, rid, body.get("signer_slot") or "SYN-MD-001", role))

        err = {"error": "not_found", "http": 404}
        return 404, json.dumps(err).encode("utf-8"), "application/json"
    except ClinicalError as exc:
        return exc.http, json.dumps(exc.as_dict(), ensure_ascii=False).encode("utf-8"), "application/json"


def make_handler(svc: ClinicalService) -> type[BaseHTTPRequestHandler]:
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

        def do_PUT(self) -> None:  # noqa: N802
            status, payload, ctype = handle_request(svc, "PUT", self.path, self.headers, self._read())
            self._write(status, payload, ctype)

    return Handler


def bind_clinical_server(
    db_path: str | Path,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
) -> ThreadingHTTPServer:
    store = ClinicalStore(db_path)
    svc = ClinicalService(store)
    handler = make_handler(svc)
    return ThreadingHTTPServer((host, port), handler)
