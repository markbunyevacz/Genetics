#!/usr/bin/env python3
"""WP-C / WP-K / WP-F / WP-Q / WP-X — FR-100 gate, B.3/B.4, B.5 HTTP."""
from __future__ import annotations

import inspect
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

from pce_clinical.errors import ClinicalError  # noqa: E402
from pce_clinical.server import bind_clinical_server  # noqa: E402
from pce_clinical.service import ClinicalService  # noqa: E402
from pce_clinical.store import ClinicalStore  # noqa: E402

F1 = ROOT / "tests" / "fixtures" / "f1plus-v0"
TSV = ROOT / "tests" / "fixtures" / "clinical-v0" / "outside-call.tsv"


def _svc() -> ClinicalService:
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmp.close()
    return ClinicalService(ClinicalStore(tmp.name))


def _called() -> dict:
    return json.loads((F1 / "outside-call-cyp2d6-called.json").read_text(encoding="utf-8"))


def _indeterminate() -> dict:
    return json.loads((F1 / "outside-call-cyp2d6-indeterminate.json").read_text(encoding="utf-8"))


def _bootstrap(
    svc: ClinicalService,
    *,
    counselling_at: str | None = "2026-08-09",
    collected_at: str = "2026-08-10",
    scopes: list[str] | None = None,
    license_id: str | None = "SYN-LIC-001",
    omit: list[str] | None = None,
    consent: bool = True,
) -> tuple[dict, dict, dict]:
    org = svc.create_org(
        {"name": "SYN-ORG-001", "license_id": license_id, "role": "lab"}, "lab_signer"
    )
    sub = svc.create_subject({"org_id": org["id"]}, "lab_signer")
    case = svc.create_case(
        {
            "org_id": org["id"],
            "subject_id": sub["id"],
            "sample": {"collected_at": collected_at, "type": "blood", "origin": "SYN-LAB-001"},
        },
        "lab_signer",
    )
    if counselling_at:
        svc.add_counselling(
            case["id"],
            {"counsellor_id": "SYN-MD-001", "occurred_at": counselling_at},
            "counsellor",
        )
    if consent:
        svc.add_consent(
            case["id"],
            {
                "granted_at": counselling_at or collected_at,
                "scopes": scopes if scopes is not None else ["CYP2D6", "pgx_report"],
                "omit_from_patient": omit or [],
            },
            "counsellor",
        )
    return org, sub, case


class ConsentGateTests(unittest.TestCase):
    def test_missing_counselling_e_consent_001(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc, counselling_at=None, consent=True)
        svc.add_outside_calls(case["id"], [_called()], "lab_signer")
        with self.assertRaises(ClinicalError) as ctx:
            svc.create_report(case["id"], "lab_signer")
        self.assertEqual(ctx.exception.code, "E-CONSENT-001")
        self.assertEqual(ctx.exception.http, 409)
        self.assertIn("6. § (2)", ctx.exception.message_hu)

    def test_counselling_after_sample_e_consent_002(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc, counselling_at="2026-08-11", collected_at="2026-08-10")
        svc.add_outside_calls(case["id"], [_called()], "lab_signer")
        with self.assertRaises(ClinicalError) as ctx:
            svc.create_report(case["id"], "lab_signer")
        self.assertEqual(ctx.exception.code, "E-CONSENT-002")

    def test_missing_consent_e_consent_003(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc, consent=False)
        svc.add_outside_calls(case["id"], [_called()], "lab_signer")
        with self.assertRaises(ClinicalError) as ctx:
            svc.create_report(case["id"], "lab_signer")
        self.assertEqual(ctx.exception.code, "E-CONSENT-003")
        self.assertIn("8. §", ctx.exception.message_hu)

    def test_extra_gene_e_consent_004(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc, scopes=["CYP2D6"])
        extra = dict(_called())
        extra["gene"] = "CYP2C19"
        extra["diplotype"] = "*1/*1"
        svc.add_outside_calls(case["id"], [_called(), extra], "lab_signer")
        with self.assertRaises(ClinicalError) as ctx:
            svc.create_report(case["id"], "lab_signer")
        self.assertEqual(ctx.exception.code, "E-CONSENT-004")

    def test_missing_license_e_consent_005(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc, license_id=None)
        svc.add_outside_calls(case["id"], [_called()], "lab_signer")
        with self.assertRaises(ClinicalError) as ctx:
            svc.create_report(case["id"], "lab_signer")
        self.assertEqual(ctx.exception.code, "E-CONSENT-005")

    def test_admin_cannot_skip_gate(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc, counselling_at=None, consent=False)
        svc.add_outside_calls(case["id"], [_called()], "lab_signer")
        with self.assertRaises(ClinicalError) as ctx:
            svc.create_report(case["id"], "admin", skip_consent=True, role="admin")
        self.assertEqual(ctx.exception.code, "E-CONSENT-001")

    def test_happy_path_meta_and_b41(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc)
        svc.put_clinical_context(
            case["id"],
            {
                "medications": [
                    {
                        "code_system": "http://www.whocc.no/atc",
                        "code": "N06AB",
                        "name": "SSRI-class",
                        "source": "MANUAL",
                    }
                ],
                "observations": [],
            },
            "lab_signer",
        )
        svc.add_outside_calls(case["id"], [_called()], "lab_signer")
        report = svc.create_report(case["id"], "lab_signer")
        self.assertEqual(report["unsourced_claims"], 0)
        self.assertFalse(report["medications_applied_to_recommendations"])
        self.assertFalse(report["gyogyszerlista_a_leleten"])
        self.assertIn("publikált guideline-sorokat listázza", report["megjegyzes_hu"])
        self.assertIn("counselling", report)
        self.assertEqual(report["counselling"]["counsellor_id"], "SYN-MD-001")
        self.assertEqual(report["performing_org_license_id"], "SYN-LIC-001")
        self.assertEqual(report["white_label"]["org"], "SYN-ORG-001")
        self.assertNotIn("functional_phenotype", report)
        self.assertNotIn("live_findings", report)
        self.assertNotIn("dose_mg", report)
        self.assertGreaterEqual(len(report["findings"]), 70)
        self.assertFalse(report["findings"][0]["severity_means_replace_prescribed"])
        self.assertTrue(all(st.get("url") for f in report["findings"] for st in f["statements"]))
        self.assertIsNone(report["phenoconversion_edu"])
        self.assertEqual(report["pair_count"], len(report["pairs"]))
        expl = svc.get_explanation(case["id"], report["report_id"])
        again = svc.get_explanation(case["id"], report["report_id"])
        self.assertEqual(expl["body_hu"], again["body_hu"])
        self.assertEqual(expl["hash"], again["hash"])
        self.assertIn("6. § (6)", expl["body_hu"])
        fhir = svc.get_report_fhir(case["id"], report["report_id"])
        self.assertEqual(fhir["resourceType"], "Bundle")
        types = {e["resource"]["resourceType"] for e in fhir["entry"]}
        self.assertIn("DiagnosticReport", types)
        self.assertIn("Observation", types)
        self.assertIn("DocumentReference", types)
        desc = next(e["resource"] for e in fhir["entry"] if e["resource"]["resourceType"] == "DocumentReference")
        self.assertIn("nem végez egyedi", desc["description"])
        self.assertNotIn("functional_phenotype", json.dumps(fhir))
        pdf = Path(tempfile.mkdtemp()) / "out.pdf"
        svc.write_report_pdf(case["id"], report["report_id"], pdf)
        self.assertTrue(pdf.read_bytes().startswith(b"%PDF"))

    def test_create_report_does_not_load_medication_table(self) -> None:
        src = inspect.getsource(ClinicalService.create_report)
        self.assertNotIn("medication_entry", src)
        self.assertNotIn("SELECT * FROM medication", src)

    def test_omit_from_patient(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc, omit=["CYP2D6"])
        svc.add_outside_calls(case["id"], [_called()], "lab_signer")
        with self.assertRaises(ClinicalError) as ctx:
            svc.create_report(case["id"], "lab_signer")
        self.assertEqual(ctx.exception.code, "E-CONSENT-004")

    def test_withdraw_410_and_certificate(self) -> None:
        svc = _svc()
        _, sub, case = _bootstrap(svc)
        svc.add_outside_calls(case["id"], [_called()], "lab_signer")
        report = svc.create_report(case["id"], "lab_signer")
        cert = svc.withdraw_subject(sub["id"], "dpo")
        self.assertIn("objects_destroyed", cert)
        self.assertNotIn("*1/*2", json.dumps(cert))
        with self.assertRaises(ClinicalError) as ctx:
            svc.get_report(case["id"], report["report_id"])
        self.assertEqual(ctx.exception.code, "E-GONE-010")
        self.assertEqual(ctx.exception.http, 410)

    def test_audit_append_only(self) -> None:
        svc = _svc()
        _bootstrap(svc)
        with self.assertRaises(ClinicalError) as ctx:
            svc.try_update_audit()
        self.assertEqual(ctx.exception.code, "E-AUDIT-001")
        export = json.loads(svc.export_audit("json"))
        self.assertGreaterEqual(len(export), 1)
        csv_text = svc.export_audit("csv")
        self.assertIn("object_type", csv_text)
        self.assertNotIn("##fileformat=VCF", csv_text)


class OutsideCallTests(unittest.TestCase):
    def test_empty_diplotype_called(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc)
        bad = dict(_called())
        bad["diplotype"] = ""
        with self.assertRaises(ClinicalError) as ctx:
            svc.add_outside_calls(case["id"], [bad], "lab_signer")
        self.assertEqual(ctx.exception.code, "E-CALL-001")

    def test_tsv(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc)
        items = svc.parse_outside_payload(TSV.read_bytes(), "text/tab-separated-values")
        out = svc.add_outside_calls(case["id"], items, "lab_signer")
        self.assertEqual(out["calls"][0]["gene"], "CYP2D6")

    def test_indeterminate_allowed(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc)
        svc.add_outside_calls(case["id"], [_indeterminate()], "lab_signer")
        report = svc.create_report(case["id"], "lab_signer")
        self.assertFalse(report["case"]["positive_drug_assertion"])
        self.assertNotEqual(report["case"].get("lab_phenotype_claim"), "NORMAL")

    def test_vcf_conflict(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc)
        vcf = (
            b"##fileformat=VCFv4.2\n##reference=GRCh38\n"
            b"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tsyn1\n"
            b"1\t1\t.\tA\tC\t.\tPASS\t.\tGT\t0/1\n"
        )
        svc.add_vcf(case["id"], vcf, "lab_signer")
        with self.assertRaises(ClinicalError) as ctx:
            svc.add_outside_calls(case["id"], [_called()], "lab_signer")
        self.assertEqual(ctx.exception.code, "W-CALL-010")
        self.assertEqual(ctx.exception.http, 409)
        svc.resolve_call(case["id"], "OUTSIDE", "lab_signer")
        svc.add_outside_calls(case["id"], [_called()], "lab_signer")

    def test_vcf_missing_reference(self) -> None:
        svc = _svc()
        _, _, case = _bootstrap(svc)
        vcf = b"##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
        with self.assertRaises(ClinicalError) as ctx:
            svc.add_vcf(case["id"], vcf, "lab_signer")
        self.assertEqual(ctx.exception.code, "E-VCF-003")

    def test_vcf_missing_defining_position_is_indeterminate_not_normal(self) -> None:
        gold = ROOT / "tests" / "fixtures" / "vcf-gold-v0"
        cases = (
            ("missing-cyp2d6-star4.vcf", "CYP2D6"),
            ("missing-cyp2c19-star2.vcf", "CYP2C19"),
            ("missing-dpyd-star2a.vcf", "DPYD"),
        )
        for name, gene in cases:
            with self.subTest(name=name):
                svc = _svc()
                _, _, case = _bootstrap(svc, scopes=[gene, "pgx_report"])
                raw = (gold / name).read_bytes()
                stored = svc.add_vcf(case["id"], raw, "lab_signer")
                cov = {row["gene"]: row for row in stored["coverage"]}
                self.assertEqual(cov[gene]["callability"], "INDETERMINATE")
                self.assertEqual(cov[gene]["naive_missing_to_ref_would_claim"], "Normal Metabolizer")
                self.assertFalse(stored["matcher_on"])
                report = svc.create_report(case["id"], "lab_signer")
                summary = report["callability_summary"]
                self.assertEqual(summary[gene], "INDETERMINATE")
                self.assertNotEqual(summary[gene], "NORMAL")
                gene_row = next(g for g in report["genes"] if g["gene"] == gene)
                self.assertEqual(gene_row["callability"], "INDETERMINATE")
                self.assertIsNone(gene_row["diplotype"])


class HttpClinicalTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        tmp.close()
        self.httpd = bind_clinical_server(tmp.name, port=0)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.httpd.shutdown)
        self.addCleanup(self.httpd.server_close)
        self.port = self.httpd.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"

    def _req(
        self,
        method: str,
        path: str,
        body: dict | bytes | None = None,
        role: str = "lab_signer",
        ctype: str = "application/json",
    ) -> tuple[int, dict | bytes]:
        data = None
        headers = {"Authorization": role}
        if isinstance(body, dict):
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif isinstance(body, bytes):
            data = body
            headers["Content-Type"] = ctype
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
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

    def test_ui_and_iso_and_walk(self) -> None:
        status, html = self._req("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"SYN-ORG-001", html if isinstance(html, bytes) else html.encode())
        status, body = self._req("GET", "/cds-services/pgx-order-sign", role="clinician")
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "E-ISO-002")
        status, body = self._req("GET", "/v1/hitl/inferences", role="clinician")
        self.assertEqual(status, 403)
        self.assertEqual(body["error"], "E-ISO-001")
        status, org = self._req("POST", "/v1/orgs", {"name": "SYN-ORG-001", "license_id": "SYN-LIC-001", "role": "lab"})
        self.assertEqual(status, 201)
        status, sub = self._req("POST", "/v1/subjects", {"org_id": org["id"]})
        status, case = self._req(
            "POST",
            "/v1/cases",
            {
                "org_id": org["id"],
                "subject_id": sub["id"],
                "sample": {"collected_at": "2026-08-10", "type": "blood", "origin": "SYN-LAB-001"},
            },
        )
        self._req(
            "POST",
            f"/v1/cases/{case['id']}/counselling",
            {"counsellor_id": "SYN-MD-001", "occurred_at": "2026-08-09"},
            role="counsellor",
        )
        self._req(
            "POST",
            f"/v1/cases/{case['id']}/consent",
            {"granted_at": "2026-08-09", "scopes": ["CYP2D6", "pgx_report"]},
            role="counsellor",
        )
        status, _ = self._req(
            "POST",
            f"/v1/cases/{case['id']}/outside-calls",
            _called(),
        )
        self.assertEqual(status, 201)
        status, report = self._req("POST", f"/v1/cases/{case['id']}/reports", {})
        self.assertEqual(status, 201)
        self.assertEqual(report["unsourced_claims"], 0)
        status, got = self._req("GET", f"/v1/cases/{case['id']}/reports/{report['report_id']}")
        self.assertEqual(status, 200)
        self.assertEqual(got["report_id"], report["report_id"])
        status, expl = self._req("GET", f"/v1/cases/{case['id']}/explanation")
        self.assertEqual(status, 200)
        self.assertIn("config_id", expl["body_hu"])
        status, _pdf = self._req("GET", f"/v1/cases/{case['id']}/reports/{report['report_id']}/pdf")
        self.assertEqual(status, 200)
        status, body = self._req("POST", f"/v1/cases/{case['id']}/reports", {"skip_consent": True}, role="admin")
        self.assertEqual(status, 201)
        status, gone = self._req("POST", f"/v1/subjects/{sub['id']}/withdraw", {}, role="dpo")
        self.assertEqual(status, 200)
        status, err = self._req("GET", f"/v1/cases/{case['id']}/reports/{report['report_id']}")
        self.assertEqual(status, 410)
        self.assertEqual(err["error"], "E-GONE-010")

    def test_report_without_counselling_http(self) -> None:
        status, org = self._req("POST", "/v1/orgs", {"name": "SYN-ORG-001", "license_id": "SYN-LIC-001", "role": "lab"})
        status, sub = self._req("POST", "/v1/subjects", {"org_id": org["id"]})
        status, case = self._req(
            "POST",
            "/v1/cases",
            {
                "org_id": org["id"],
                "subject_id": sub["id"],
                "sample": {"collected_at": "2026-08-10", "type": "blood", "origin": "SYN-LAB-001"},
            },
        )
        self._req("POST", f"/v1/cases/{case['id']}/consent", {"granted_at": "2026-08-09", "scopes": ["CYP2D6"]})
        self._req("POST", f"/v1/cases/{case['id']}/outside-calls", _called())
        status, body = self._req("POST", f"/v1/cases/{case['id']}/reports", {})
        self.assertEqual(status, 409)
        self.assertEqual(body["error"], "E-CONSENT-001")


class CliGateTests(unittest.TestCase):
    def test_outside_call_cli_rejected(self) -> None:
        from pce_report.__main__ import main

        oc = F1 / "outside-call-cyp2d6-called.json"
        rc = main(["--outside-call", str(oc)])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
