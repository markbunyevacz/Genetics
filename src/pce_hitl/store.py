"""ShadowInference + HitlReview SQLite (B.2.2). Separate from clinical.sqlite."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS shadow_inference (
  id TEXT PRIMARY KEY,
  gateway_event_id TEXT,
  case_display_id TEXT NOT NULL,
  config_id TEXT NOT NULL,
  gene TEXT,
  phenotype_display TEXT,
  medications_json TEXT NOT NULL,
  clinical_context TEXT NOT NULL,
  body_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hitl_blind (
  inference_id TEXT PRIMARY KEY,
  choice TEXT NOT NULL CHECK(choice IN ('CONTINUE','ALTERNATIVE','DOSE_CHANGE','INSUFFICIENT')),
  reviewer_id TEXT NOT NULL,
  at TEXT NOT NULL,
  FOREIGN KEY(inference_id) REFERENCES shadow_inference(id)
);

CREATE TABLE IF NOT EXISTS hitl_review (
  inference_id TEXT PRIMARY KEY,
  verdict TEXT NOT NULL CHECK(verdict IN ('AGREE','DISAGREE','INSUFFICIENT_DATA')),
  reason_code TEXT NOT NULL,
  note TEXT,
  reviewer_id TEXT NOT NULL,
  at TEXT NOT NULL,
  FOREIGN KEY(inference_id) REFERENCES shadow_inference(id)
);

CREATE TRIGGER IF NOT EXISTS hitl_blind_no_update
BEFORE UPDATE ON hitl_blind
BEGIN
  SELECT RAISE(ABORT, 'E-HITL-IMMUTABLE');
END;

CREATE TRIGGER IF NOT EXISTS hitl_blind_no_delete
BEFORE DELETE ON hitl_blind
BEGIN
  SELECT RAISE(ABORT, 'E-HITL-IMMUTABLE');
END;

CREATE TRIGGER IF NOT EXISTS hitl_review_no_update
BEFORE UPDATE ON hitl_review
BEGIN
  SELECT RAISE(ABORT, 'E-HITL-IMMUTABLE');
END;

CREATE TRIGGER IF NOT EXISTS hitl_review_no_delete
BEFORE DELETE ON hitl_review
BEGIN
  SELECT RAISE(ABORT, 'E-HITL-IMMUTABLE');
END;
"""


class HitlStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def execute(self, sql: str, params: tuple | dict = ()) -> sqlite3.Cursor:
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    def query(self, sql: str, params: tuple | dict = ()) -> list[sqlite3.Row]:
        return list(self.conn.execute(sql, params))

    def one(self, sql: str, params: tuple | dict = ()) -> sqlite3.Row | None:
        return self.conn.execute(sql, params).fetchone()

    def insert_inference(self, rec: dict[str, Any]) -> None:
        self.execute(
            """
            INSERT INTO shadow_inference (
              id, gateway_event_id, case_display_id, config_id, gene,
              phenotype_display, medications_json, clinical_context, body_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec["id"],
                rec.get("gateway_event_id"),
                rec["case_display_id"],
                rec["config_id"],
                rec.get("gene"),
                rec.get("phenotype_display"),
                json.dumps(rec["medications"], ensure_ascii=False),
                rec["clinical_context"],
                json.dumps(rec["body"], ensure_ascii=False),
                rec["created_at"],
            ),
        )

    def close(self) -> None:
        self.conn.close()
