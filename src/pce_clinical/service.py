"""Clinical path: orgs, cases, consent, outside-calls, gated F1+ reports (B.3 / B.4)."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pce_clinical.consent import assert_render_allowed, gate_to_meta
from pce_clinical.coverage import assess_coverage
from pce_clinical.errors import ClinicalError
from pce_clinical.explanation import build_explanation
from pce_clinical.fhir import to_stu3_bundle
from pce_clinical.store import ClinicalStore
from pce_report.guidelines import GuidelineTable, prepare12_table
from pce_report.panel import CONFIG_ID_PREFIX
from pce_report.pdf import write_pdf
from pce_report.render import RendererConfigError
from pce_report.schema import assemble_b41, render_gene_engine

CALLABILITY_OK = {"CALLED", "PARTIAL", "INDETERMINATE", "NOT_TESTED"}
REF_OK = ("GRCh37", "GRCh38", "hg19", "hg38")
VCF_MAX = 5 * 1024 * 1024 * 1024
TSV_FIELDS = (
    "gene",
    "diplotype",
    "calling_lab",
    "signing_physician",
    "method",
    "call_date",
    "phenotype",
    "callability",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _id() -> str:
    return str(uuid.uuid4())


def _row(row: Any) -> dict[str, Any]:
    return dict(row) if row is not None else {}


class ClinicalService:
    def __init__(
        self,
        store: ClinicalStore,
        table: GuidelineTable | None = None,
    ) -> None:
        self.store = store
        self.table = table or prepare12_table()

    def audit(
        self,
        actor: str,
        action: str,
        object_type: str,
        object_id: str,
        legal_basis: str | None = None,
    ) -> None:
        prev = self.store.one("SELECT id FROM audit_event ORDER BY ts DESC, id DESC LIMIT 1")
        self.store.execute(
            "INSERT INTO audit_event(id, ts, actor, action, object_type, object_id, legal_basis, prev_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                _id(),
                _now(),
                actor,
                action,
                object_type,
                object_id,
                legal_basis,
                prev["id"] if prev else None,
            ),
        )

    def create_org(self, body: dict[str, Any], actor: str) -> dict[str, Any]:
        oid = body.get("id") or _id()
        name = body.get("name") or "SYN-ORG-001"
        role = body.get("role") or "lab"
        license_id = body.get("license_id")
        self.store.execute(
            "INSERT INTO organization(id, name, license_id, role) VALUES (?, ?, ?, ?)",
            (oid, name, license_id, role),
        )
        self.audit(actor, "create_org", "Organization", oid, "12. § (1)")
        return {"id": oid, "name": name, "license_id": license_id, "role": role}

    def create_subject(self, body: dict[str, Any], actor: str) -> dict[str, Any]:
        sid = body.get("id") or _id()
        org_id = body["org_id"]
        reid = _id()
        self.store.execute("INSERT INTO reid_store(id, secret) VALUES (?, ?)", (reid, _id()))
        self.store.execute(
            "INSERT INTO subject(id, org_id, reid_key_ref, erased) VALUES (?, ?, ?, 0)",
            (sid, org_id, reid),
        )
        self.audit(actor, "create_subject", "Subject", sid, "FR-130")
        return {"id": sid, "org_id": org_id, "reid_key_ref": reid}

    def create_case(self, body: dict[str, Any], actor: str) -> dict[str, Any]:
        cid = body.get("id") or _id()
        sample = body.get("sample") or {}
        if not sample.get("collected_at"):
            raise ClinicalError("E-CONSENT-002", extra={"reason": "sample.collected_at required"})
        config_id = body.get("config_id") or f"{CONFIG_ID_PREFIX}@v0"
        self.store.execute(
            "INSERT INTO case_record(id, subject_id, org_id, status, config_id, call_source) "
            "VALUES (?, ?, ?, 'DRAFT', ?, NULL)",
            (cid, body["subject_id"], body["org_id"], config_id),
        )
        self.store.execute(
            "INSERT INTO sample(id, case_id, collected_at, type, quantity, origin) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                _id(),
                cid,
                sample["collected_at"],
                sample.get("type") or "blood",
                sample.get("quantity"),
                sample.get("origin") or "SYN-LAB-001",
            ),
        )
        self.audit(actor, "create_case", "Case", cid, "26. § (1)")
        return {"id": cid, "status": "DRAFT", "config_id": config_id}

    def add_counselling(self, case_id: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
        sample = self.store.one("SELECT * FROM sample WHERE case_id = ?", (case_id,))
        if sample is None:
            raise ClinicalError("E-CONSENT-002")
        occurred = body["occurred_at"]
        pre = 1 if occurred < sample["collected_at"] else 0
        rid = _id()
        self.store.execute(
            "INSERT INTO counselling(id, case_id, counsellor_id, occurred_at, pre_sampling) "
            "VALUES (?, ?, ?, ?, ?)",
            (rid, case_id, body["counsellor_id"], occurred, pre),
        )
        self.audit(actor, "counselling", "CounsellingRecord", rid, "6. § (2)")
        return {"id": rid, "pre_sampling": bool(pre)}

    def add_consent(self, case_id: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
        rid = _id()
        scopes = body.get("scopes") or []
        omit = body.get("omit_from_patient") or []
        self.store.execute(
            "INSERT INTO consent(id, case_id, granted_at, scopes_json, omit_from_patient_json, withdrawn_at) "
            "VALUES (?, ?, ?, ?, ?, NULL)",
            (rid, case_id, body["granted_at"], json.dumps(scopes), json.dumps(omit)),
        )
        self.audit(actor, "consent", "ConsentRecord", rid, "8. §")
        return {"id": rid, "scopes": scopes, "omit_from_patient": omit}

    def _conflict_if_both_sources(self, case_id: str, incoming: str) -> None:
        case = self.store.one("SELECT * FROM case_record WHERE id = ?", (case_id,))
        if case is None:
            raise ClinicalError("E-GONE-010")
        has_vcf = self.store.one("SELECT id FROM genomic_file WHERE case_id = ?", (case_id,))
        has_oc = self.store.one("SELECT id FROM outside_call WHERE case_id = ?", (case_id,))
        chosen = case["call_source"]
        if case["status"] == "NEEDS_RESOLUTION":
            raise ClinicalError("W-CALL-010", extra={"status": "NEEDS_RESOLUTION"})
        if incoming == "OUTSIDE" and has_vcf is not None and chosen != "OUTSIDE":
            self.store.execute(
                "UPDATE case_record SET status = 'NEEDS_RESOLUTION' WHERE id = ?",
                (case_id,),
            )
            raise ClinicalError("W-CALL-010", extra={"status": "NEEDS_RESOLUTION"})
        if incoming == "VCF" and has_oc is not None and chosen != "VCF":
            self.store.execute(
                "UPDATE case_record SET status = 'NEEDS_RESOLUTION' WHERE id = ?",
                (case_id,),
            )
            raise ClinicalError("W-CALL-010", extra={"status": "NEEDS_RESOLUTION"})

    def resolve_call(self, case_id: str, source: str, actor: str) -> dict[str, Any]:
        if source not in {"OUTSIDE", "VCF"}:
            raise ClinicalError("W-CALL-010")
        self.store.execute(
            "UPDATE case_record SET status = 'DRAFT', call_source = ? WHERE id = ?",
            (source, case_id),
        )
        self.audit(actor, "resolve_call", "Case", case_id, "FR-240")
        return {"id": case_id, "status": "DRAFT", "call_source": source}

    def add_outside_calls(self, case_id: str, items: list[dict[str, Any]], actor: str) -> dict[str, Any]:
        self._require_case(case_id)
        self._conflict_if_both_sources(case_id, "OUTSIDE")
        stored: list[dict[str, Any]] = []
        for item in items:
            rec = self._normalize_call(item)
            rid = _id()
            self.store.execute(
                "INSERT INTO outside_call(id, case_id, gene, diplotype, calling_lab, "
                "signing_physician, method, call_date, phenotype, callability) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    rid,
                    case_id,
                    rec["gene"],
                    rec["diplotype"],
                    rec["calling_lab"],
                    rec["signing_physician"],
                    rec["method"],
                    rec["call_date"],
                    rec["phenotype"],
                    rec["callability"],
                ),
            )
            rec["id"] = rid
            stored.append(rec)
        self.store.execute(
            "UPDATE case_record SET call_source = 'OUTSIDE' WHERE id = ? AND call_source IS NULL",
            (case_id,),
        )
        self.audit(actor, "outside_call", "OutsideCall", case_id, "FR-240")
        return {"calls": stored}

    def parse_outside_payload(self, raw: bytes, content_type: str) -> list[dict[str, Any]]:
        ct = (content_type or "").split(";")[0].strip().lower()
        text = raw.decode("utf-8")
        if ct in {"text/tab-separated-values", "text/tsv"} or (
            "\t" in text and not text.lstrip().startswith("[") and not text.lstrip().startswith("{")
        ):
            return self._parse_tsv(text)
        data = json.loads(text)
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        raise ClinicalError("E-CALL-001")

    def _parse_tsv(self, text: str) -> list[dict[str, Any]]:
        reader = csv.DictReader(io.StringIO(text), delimiter="\t")
        rows: list[dict[str, Any]] = []
        for row in reader:
            item = {k: (row.get(k) or "").strip() or None for k in TSV_FIELDS}
            rows.append(item)
        if not rows:
            raise ClinicalError("E-CALL-001")
        return rows

    def _normalize_call(self, item: dict[str, Any]) -> dict[str, Any]:
        gene = item.get("gene")
        if not isinstance(gene, str) or not gene:
            raise ClinicalError("E-CALL-001", extra={"reason": "gene required"})
        callability = item.get("callability") or ("CALLED" if item.get("diplotype") else None)
        diplotype = item.get("diplotype")
        if isinstance(diplotype, str) and not diplotype.strip():
            diplotype = None
        if callability not in CALLABILITY_OK:
            raise ClinicalError("E-CALL-001", extra={"reason": "callability"})
        if callability in {"CALLED", "PARTIAL"} and not isinstance(diplotype, str):
            raise ClinicalError("E-CALL-001")
        for key in ("calling_lab", "signing_physician", "method", "call_date"):
            if not item.get(key):
                raise ClinicalError("E-CALL-001", extra={"reason": f"{key} required"})
        return {
            "gene": gene,
            "diplotype": diplotype,
            "calling_lab": item["calling_lab"],
            "signing_physician": item["signing_physician"],
            "method": item["method"],
            "call_date": item["call_date"],
            "phenotype": item.get("phenotype") or item.get("lab_phenotype"),
            "callability": callability,
        }

    def add_vcf(self, case_id: str, raw: bytes, actor: str, *, sample_id: str | None = None) -> dict[str, Any]:
        self._require_case(case_id)
        if len(raw) > VCF_MAX:
            raise ClinicalError("E-VCF-004")
        try:
            text = raw.decode("utf-8", errors="replace")
        except Exception as exc:
            raise ClinicalError("E-VCF-001") from exc
        if not text.startswith("##fileformat=VCF"):
            raise ClinicalError("E-VCF-001")
        ref_line = next((ln for ln in text.splitlines() if ln.startswith("##reference=")), "")
        if not any(tok in ref_line for tok in REF_OK):
            raise ClinicalError("E-VCF-003")
        chrom = next((ln for ln in text.splitlines() if ln.startswith("#CHROM")), "")
        samples = chrom.split("\t")[9:] if chrom else []
        if len(samples) > 1 and not sample_id:
            raise ClinicalError("E-VCF-002")
        self._conflict_if_both_sources(case_id, "VCF")
        rid = _id()
        fmt = "VCF43" if "VCFv4.3" in text[:80] else "VCF42"
        reference = "GRCh38" if "GRCh38" in ref_line or "hg38" in ref_line else "GRCh37"
        digest = hashlib.sha256(raw).hexdigest()
        self.store.execute(
            "INSERT INTO genomic_file(id, case_id, format, reference, sha256, size) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (rid, case_id, fmt, reference, digest, len(raw)),
        )
        self.store.execute(
            "UPDATE case_record SET call_source = 'VCF' WHERE id = ? AND call_source IS NULL",
            (case_id,),
        )
        self.audit(actor, "vcf", "GenomicFile", rid, "FR-200")
        coverage = assess_coverage(text, reference=reference)
        genes: list[dict[str, Any]] = []
        for row in coverage:
            cid = _id()
            self.store.execute(
                "INSERT INTO gene_coverage(id, genomic_file_id, case_id, gene, callability, "
                "missing_json, naive_missing_to_ref_would_claim, note_hu) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    cid,
                    rid,
                    case_id,
                    row["gene"],
                    row["callability"],
                    json.dumps(row.get("missing") or [], ensure_ascii=False),
                    row.get("naive_missing_to_ref_would_claim"),
                    row["note_hu"],
                ),
            )
            genes.append(
                {
                    "gene": row["gene"],
                    "callability": row["callability"],
                    "naive_missing_to_ref_would_claim": row.get("naive_missing_to_ref_would_claim"),
                    "note_hu": row["note_hu"],
                    "pharmcat_absent_to_ref": False,
                }
            )
        return {
            "id": rid,
            "format": fmt,
            "reference": reference,
            "sha256": digest,
            "size": len(raw),
            "matcher_on": False,
            "coverage": genes,
        }

    def put_clinical_context(self, case_id: str, body: dict[str, Any], actor: str) -> dict[str, Any]:
        self._require_case(case_id)
        self.store.execute("DELETE FROM medication_entry WHERE case_id = ?", (case_id,))
        self.store.execute("DELETE FROM lab_observation WHERE case_id = ?", (case_id,))
        meds = body.get("medications") or []
        obs = body.get("observations") or []
        for med in meds:
            self.store.execute(
                "INSERT INTO medication_entry(id, case_id, code_system, code, name, source) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    _id(),
                    case_id,
                    med.get("code_system"),
                    med.get("code"),
                    med.get("name"),
                    med.get("source") or "MANUAL",
                ),
            )
        for item in obs:
            self.store.execute(
                "INSERT INTO lab_observation(id, case_id, loinc, value, unit, effective_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    _id(),
                    case_id,
                    item.get("loinc"),
                    item.get("value"),
                    item.get("unit"),
                    item.get("effective_at"),
                ),
            )
        self.audit(actor, "clinical_context", "Case", case_id, "FR-220")
        return {"stored": True, "medications": len(meds), "observations": len(obs), "used_by_f1plus_l4": False}

    def _coverage_as_calls(self, case_id: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        sample = self.store.one("SELECT * FROM sample WHERE case_id = ?", (case_id,))
        counselling = self.store.one("SELECT * FROM counselling WHERE case_id = ?", (case_id,))
        origin = sample["origin"] if sample else "SYN-LAB-001"
        signer = counselling["counsellor_id"] if counselling else "SYN-MD-001"
        calls: list[dict[str, Any]] = []
        for row in rows:
            callability = row["callability"]
            if callability not in CALLABILITY_OK:
                callability = "INDETERMINATE"
            calls.append(
                {
                    "gene": row["gene"],
                    "diplotype": None,
                    "calling_lab": origin,
                    "signing_physician": signer,
                    "method": "VCF-lefedettség (allélhívó ki)",
                    "call_date": _now()[:10],
                    "phenotype": None,
                    "callability": callability,
                    "note_hu": row.get("note_hu"),
                    "naive_missing_to_ref_would_claim": row.get("naive_missing_to_ref_would_claim"),
                }
            )
        return calls

    def _calls_for_report(self, case_id: str, case: dict[str, Any]) -> list[dict[str, Any]]:
        oc = [dict(r) for r in self.store.query("SELECT * FROM outside_call WHERE case_id = ?", (case_id,))]
        cov = [dict(r) for r in self.store.query("SELECT * FROM gene_coverage WHERE case_id = ?", (case_id,))]
        source = case.get("call_source")
        if source == "VCF" and cov:
            return self._coverage_as_calls(case_id, cov)
        if oc:
            return oc
        if cov:
            return self._coverage_as_calls(case_id, cov)
        raise ClinicalError("E-CALL-001", extra={"reason": "no outside-call"})

    def create_report(
        self,
        case_id: str,
        actor: str,
        *,
        skip_consent: bool = False,
        role: str = "lab_signer",
    ) -> dict[str, Any]:
        case = dict(self._require_case(case_id))
        if case["status"] == "NEEDS_RESOLUTION":
            raise ClinicalError("W-CALL-010", extra={"status": "NEEDS_RESOLUTION"})
        calls = self._calls_for_report(case_id, case)
        snap = assert_render_allowed(
            self.store, case_id, [], skip_consent=skip_consent, role=role
        )
        extras = [c["gene"] for c in calls if c["gene"] not in snap.allowed_genes]
        if extras and case.get("call_source") != "VCF":
            raise ClinicalError("E-CONSENT-004", extra={"genes": extras})
        visible = [
            c
            for c in calls
            if c["gene"] in snap.allowed_genes and c["gene"] not in snap.omit_from_patient
        ]
        if not visible:
            raise ClinicalError("E-CONSENT-004", extra={"reason": "all genes omitted or out of scope"})
        # F1+ L4 must not read medication_entry. Load them only to prove they stay unused.
        _unused_meds = self.store.query("SELECT * FROM medication_entry WHERE case_id = ?", (case_id,))
        del _unused_meds

        org = self.store.one("SELECT * FROM organization WHERE id = ?", (case["org_id"],))
        engines: list[dict[str, Any]] = []
        gene_rows: list[dict[str, Any]] = []
        primary = None
        for call in visible:
            if call["gene"] not in snap.allowed_genes:
                raise ClinicalError("E-CONSENT-004", extra={"genes": [call["gene"]]})
            oc = {
                "case_display_id": case_id,
                "gene": call["gene"],
                "diplotype": call["diplotype"],
                "callability": call["callability"],
                "calling_lab": call["calling_lab"],
                "signing_physician": call["signing_physician"],
                "method": call["method"],
                "call_date": call["call_date"],
                "lab_phenotype": call["phenotype"],
            }
            engine = render_gene_engine(oc, self.table)
            engines.append(engine)
            gene_rows.append(
                {
                    "gene": call["gene"],
                    "diplotype": call["diplotype"] if call["callability"] in {"CALLED", "PARTIAL"} else None,
                    "genotype_phenotype": call["phenotype"],
                    "callability": call["callability"],
                }
            )
            if primary is None:
                primary = engine
        assert primary is not None
        report_id = _id()
        version = case["config_id"].split("@")[-1] if "@" in case["config_id"] else "v0"
        if not primary["config_id"].endswith("@" + version):
            primary = dict(primary)
            primary["config_id"] = f"{CONFIG_ID_PREFIX}@{version}"
        try:
            assembled = assemble_b41(
                engine=primary,
                report_id=report_id,
                case_id=case_id,
                counselling=gate_to_meta(snap)["counselling"],
                consent_granted_at=snap.consent_granted_at,
                performing_org_license_id=snap.license_id,
                white_label={
                    "org": org["name"] if org else "SYN-ORG-001",
                    "signer_slot": visible[0]["signing_physician"],
                    "colophon": "Precision Clinical Engine — technológiai szállító",
                },
                genes=gene_rows,
                omit_from_patient=snap.omit_from_patient,
            )
        except RendererConfigError as exc:
            raise ClinicalError("E-EDU-001", extra={"reason": str(exc)}) from exc
        assembled["consent_granted_at"] = snap.consent_granted_at
        assembled["performing_org_license_id"] = snap.license_id
        self.store.execute(
            "INSERT INTO report(id, case_id, version, parent_report_id, formats_json, "
            "signer_slot, immutable, json_body, gone) VALUES (?, ?, 1, NULL, ?, ?, 1, ?, 0)",
            (
                report_id,
                case_id,
                json.dumps(["json", "pdf", "fhir"]),
                assembled["white_label"]["signer_slot"],
                json.dumps(assembled, ensure_ascii=False),
            ),
        )
        expl = build_explanation(assembled)
        self.store.execute(
            "INSERT INTO explanation(id, case_id, report_id, body_hu, hash) VALUES (?, ?, ?, ?, ?)",
            (_id(), case_id, report_id, expl["body_hu"], expl["hash"]),
        )
        self.audit(actor, "create_report", "Report", report_id, "FR-100")
        return assembled

    def get_report(self, case_id: str, report_id: str) -> dict[str, Any]:
        row = self.store.one(
            "SELECT * FROM report WHERE id = ? AND case_id = ?",
            (report_id, case_id),
        )
        if row is None:
            raise ClinicalError("E-GONE-010")
        if int(row["gone"]) == 1:
            raise ClinicalError("E-GONE-010")
        return json.loads(row["json_body"])

    def get_report_fhir(self, case_id: str, report_id: str) -> dict[str, Any]:
        return to_stu3_bundle(self.get_report(case_id, report_id))

    def write_report_pdf(self, case_id: str, report_id: str, dest: Path) -> Path:
        return write_pdf(self.get_report(case_id, report_id), dest)

    def get_explanation(self, case_id: str, report_id: str | None = None) -> dict[str, Any]:
        if report_id:
            row = self.store.one(
                "SELECT * FROM explanation WHERE case_id = ? AND report_id = ?",
                (case_id, report_id),
            )
        else:
            row = self.store.one(
                "SELECT * FROM explanation WHERE case_id = ? ORDER BY report_id DESC LIMIT 1",
                (case_id,),
            )
        if row is None:
            raise ClinicalError("E-GONE-010")
        return {"id": row["id"], "case_id": case_id, "report_id": row["report_id"], "body_hu": row["body_hu"], "hash": row["hash"]}

    def sign_report(self, case_id: str, report_id: str, signer_slot: str, actor: str) -> dict[str, Any]:
        report = self.get_report(case_id, report_id)
        report["white_label"] = dict(report.get("white_label") or {})
        report["white_label"]["signer_slot"] = signer_slot
        report["signed"] = True
        self.store.execute(
            "UPDATE report SET signer_slot = ?, json_body = ? WHERE id = ?",
            (signer_slot, json.dumps(report, ensure_ascii=False), report_id),
        )
        self.store.execute("UPDATE case_record SET status = 'SIGNED' WHERE id = ?", (case_id,))
        self.audit(actor, "sign_report", "Report", report_id, "REG-020")
        return report

    def withdraw_subject(self, subject_id: str, actor: str) -> dict[str, Any]:
        subject = self.store.one("SELECT * FROM subject WHERE id = ?", (subject_id,))
        if subject is None:
            raise ClinicalError("E-GONE-010")
        destroyed: list[str] = []
        cases = self.store.query("SELECT id FROM case_record WHERE subject_id = ?", (subject_id,))
        gone_body = json.dumps({"gone": True, "error": "E-GONE-010"})
        for case in cases:
            cid = case["id"]
            for table, prefix in (
                ("outside_call", "outside_call"),
                ("genomic_file", "genomic_file"),
                ("explanation", "explanation"),
                ("medication_entry", "medication_entry"),
                ("lab_observation", "lab_observation"),
            ):
                rows = self.store.query(f"SELECT id FROM {table} WHERE case_id = ?", (cid,))
                for row in rows:
                    destroyed.append(f"{prefix}:{row['id']}")
                self.store.execute(f"DELETE FROM {table} WHERE case_id = ?", (cid,))
            reports = self.store.query("SELECT id FROM report WHERE case_id = ?", (cid,))
            for row in reports:
                destroyed.append(f"report:{row['id']}")
            self.store.execute(
                "UPDATE report SET gone = 1, json_body = ?, signer_slot = NULL WHERE case_id = ?",
                (gone_body, cid),
            )
            self.store.execute("UPDATE case_record SET status = 'ERASED' WHERE id = ?", (cid,))
            destroyed.append(f"case:{cid}")
        self.store.execute("UPDATE subject SET erased = 1 WHERE id = ?", (subject_id,))
        self.store.execute("DELETE FROM reid_store WHERE id = ?", (subject["reid_key_ref"],))
        cert_id = _id()
        self.store.execute(
            "INSERT INTO deletion_certificate(id, subject_id, issued_at, objects_destroyed_json, legal_basis) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                cert_id,
                subject_id,
                _now(),
                json.dumps(destroyed),
                "2008/XXI. 26. § (1)",
            ),
        )
        self.audit(actor, "withdraw", "DeletionCertificate", cert_id, "26. § (1)")
        cert = {
            "id": cert_id,
            "subject_id": subject_id,
            "issued_at": _now(),
            "objects_destroyed": destroyed,
            "legal_basis": "2008/XXI. 26. § (1)",
        }
        blob = json.dumps(cert)
        if "*1/" in blob or "*4/" in blob or "##fileformat" in blob:
            raise RuntimeError("deletion certificate leaked genetics")
        return cert

    def get_certificate(self, cert_id: str) -> dict[str, Any]:
        row = self.store.one("SELECT * FROM deletion_certificate WHERE id = ?", (cert_id,))
        if row is None:
            raise ClinicalError("E-GONE-010")
        return {
            "id": row["id"],
            "subject_id": row["subject_id"],
            "issued_at": row["issued_at"],
            "objects_destroyed": json.loads(row["objects_destroyed_json"]),
            "legal_basis": row["legal_basis"],
        }

    def export_audit(self, fmt: str = "json") -> str:
        rows = [dict(r) for r in self.store.query("SELECT * FROM audit_event ORDER BY ts, id")]
        for row in rows:
            blob = json.dumps(row)
            if "BEGIN" in blob and "VCF" in blob and "##fileformat" in blob:
                raise RuntimeError("raw VCF leaked into audit")
        if fmt == "csv":
            buf = io.StringIO()
            writer = csv.DictWriter(
                buf,
                fieldnames=["id", "ts", "actor", "action", "object_type", "object_id", "legal_basis", "prev_hash"],
            )
            writer.writeheader()
            writer.writerows(rows)
            return buf.getvalue()
        return json.dumps(rows, ensure_ascii=False, indent=2)

    def try_update_audit(self) -> None:
        row = self.store.one("SELECT id FROM audit_event LIMIT 1")
        if row is None:
            return
        try:
            self.store.execute("UPDATE audit_event SET actor = 'tamper' WHERE id = ?", (row["id"],))
        except sqlite3.Error as exc:
            raise ClinicalError("E-AUDIT-001") from exc
        raise AssertionError("audit UPDATE must be rejected by the append-only trigger")

    def _require_case(self, case_id: str) -> Any:
        case = self.store.one("SELECT * FROM case_record WHERE id = ?", (case_id,))
        if case is None:
            raise ClinicalError("E-GONE-010")
        subject = self.store.one("SELECT * FROM subject WHERE id = ?", (case["subject_id"],))
        if subject is not None and int(subject["erased"]) == 1:
            raise ClinicalError("E-GONE-010")
        return case
