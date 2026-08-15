"""Clinical SQLite (B.2.1). Re-ID keys live in a separate table (FR-130)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS organization (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  license_id TEXT,
  role TEXT NOT NULL CHECK(role IN ('lab','clinic','vendor'))
);

CREATE TABLE IF NOT EXISTS reid_store (
  id TEXT PRIMARY KEY,
  secret TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subject (
  id TEXT PRIMARY KEY,
  org_id TEXT NOT NULL,
  reid_key_ref TEXT NOT NULL,
  erased INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY(org_id) REFERENCES organization(id)
);

CREATE TABLE IF NOT EXISTS case_record (
  id TEXT PRIMARY KEY,
  subject_id TEXT NOT NULL,
  org_id TEXT NOT NULL,
  status TEXT NOT NULL,
  config_id TEXT NOT NULL,
  call_source TEXT,
  FOREIGN KEY(subject_id) REFERENCES subject(id),
  FOREIGN KEY(org_id) REFERENCES organization(id)
);

CREATE TABLE IF NOT EXISTS sample (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL UNIQUE,
  collected_at TEXT NOT NULL,
  type TEXT NOT NULL,
  quantity TEXT,
  origin TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS counselling (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  counsellor_id TEXT NOT NULL,
  occurred_at TEXT NOT NULL,
  pre_sampling INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS consent (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  granted_at TEXT NOT NULL,
  scopes_json TEXT NOT NULL,
  omit_from_patient_json TEXT NOT NULL DEFAULT '[]',
  withdrawn_at TEXT
);

CREATE TABLE IF NOT EXISTS genomic_file (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  format TEXT,
  reference TEXT,
  sha256 TEXT NOT NULL,
  size INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS gene_coverage (
  id TEXT PRIMARY KEY,
  genomic_file_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  gene TEXT NOT NULL,
  callability TEXT NOT NULL,
  diplotype TEXT,
  missing_json TEXT NOT NULL,
  naive_missing_to_ref_would_claim TEXT,
  note_hu TEXT NOT NULL,
  FOREIGN KEY(genomic_file_id) REFERENCES genomic_file(id)
);

CREATE TABLE IF NOT EXISTS outside_call (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  gene TEXT NOT NULL,
  diplotype TEXT,
  calling_lab TEXT NOT NULL,
  signing_physician TEXT NOT NULL,
  method TEXT NOT NULL,
  call_date TEXT NOT NULL,
  phenotype TEXT,
  callability TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS medication_entry (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  code_system TEXT,
  code TEXT,
  name TEXT,
  source TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lab_observation (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  loinc TEXT,
  value TEXT,
  unit TEXT,
  effective_at TEXT
);

CREATE TABLE IF NOT EXISTS report (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  parent_report_id TEXT,
  formats_json TEXT NOT NULL,
  signer_slot TEXT,
  immutable INTEGER NOT NULL DEFAULT 1,
  json_body TEXT NOT NULL,
  gone INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS deletion_certificate (
  id TEXT PRIMARY KEY,
  subject_id TEXT NOT NULL,
  issued_at TEXT NOT NULL,
  objects_destroyed_json TEXT NOT NULL,
  legal_basis TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dsr_request (
  id TEXT PRIMARY KEY,
  subject_id TEXT NOT NULL,
  received_at TEXT NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('withdraw','erasure','erasure_refused')),
  response_issued_at TEXT,
  letter_json TEXT,
  deletion_certificate_id TEXT,
  legal_basis TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_event (
  id TEXT PRIMARY KEY,
  ts TEXT NOT NULL,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  object_type TEXT NOT NULL,
  object_id TEXT NOT NULL,
  legal_basis TEXT,
  prev_hash TEXT
);

CREATE TABLE IF NOT EXISTS explanation (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  report_id TEXT NOT NULL,
  body_hu TEXT NOT NULL,
  hash TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS audit_event_no_update
BEFORE UPDATE ON audit_event
BEGIN
  SELECT RAISE(ABORT, 'E-AUDIT-001');
END;

CREATE TRIGGER IF NOT EXISTS audit_event_no_delete
BEFORE DELETE ON audit_event
BEGIN
  SELECT RAISE(ABORT, 'E-AUDIT-001');
END;
"""


class ClinicalStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        cols = {row[1] for row in self.conn.execute("PRAGMA table_info(gene_coverage)")}
        if "diplotype" not in cols:
            self.conn.execute("ALTER TABLE gene_coverage ADD COLUMN diplotype TEXT")
        self.conn.commit()

    def execute(self, sql: str, params: tuple | dict = ()) -> sqlite3.Cursor:
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    def query(self, sql: str, params: tuple | dict = ()) -> list[sqlite3.Row]:
        return list(self.conn.execute(sql, params))

    def one(self, sql: str, params: tuple | dict = ()) -> sqlite3.Row | None:
        row = self.conn.execute(sql, params).fetchone()
        return row

    def close(self) -> None:
        self.conn.close()
