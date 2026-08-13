from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class KCellStore:
    """Institutional local counter. Raw counts never leave this store (E.3.1)."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cells (
                phenotype_class TEXT NOT NULL,
                atc TEXT NOT NULL,
                quarter TEXT NOT NULL,
                n INTEGER NOT NULL,
                PRIMARY KEY (phenotype_class, atc, quarter)
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS drops (
                quarter TEXT NOT NULL PRIMARY KEY,
                n INTEGER NOT NULL
            )
            """
        )
        self._conn.commit()

    def seed(self, phenotype_class: str, atc: str, quarter: str, n: int) -> None:
        self._conn.execute(
            """
            INSERT INTO cells (phenotype_class, atc, quarter, n)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(phenotype_class, atc, quarter) DO UPDATE SET n = excluded.n
            """,
            (phenotype_class, atc, quarter, n),
        )
        self._conn.commit()

    def peek(self, phenotype_class: str, atc: str, quarter: str) -> int:
        cur = self._conn.execute(
            "SELECT n FROM cells WHERE phenotype_class = ? AND atc = ? AND quarter = ?",
            (phenotype_class, atc, quarter),
        )
        row = cur.fetchone()
        return row[0] if row else 0

    def increment(self, phenotype_class: str, atc: str, quarter: str) -> int:
        cur = self._conn.execute(
            "SELECT n FROM cells WHERE phenotype_class = ? AND atc = ? AND quarter = ?",
            (phenotype_class, atc, quarter),
        )
        row = cur.fetchone()
        n = (row[0] if row else 0) + 1
        self._conn.execute(
            """
            INSERT INTO cells (phenotype_class, atc, quarter, n)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(phenotype_class, atc, quarter) DO UPDATE SET n = excluded.n
            """,
            (phenotype_class, atc, quarter, n),
        )
        self._conn.commit()
        return n

    def record_drop(self, quarter: str) -> None:
        self._conn.execute(
            """
            INSERT INTO drops (quarter, n) VALUES (?, 1)
            ON CONFLICT(quarter) DO UPDATE SET n = n + 1
            """,
            (quarter,),
        )
        self._conn.commit()

    def quarterly_report(self, quarter: str) -> dict[str, Any]:
        cells = list(
            self._conn.execute(
                "SELECT n FROM cells WHERE quarter = ?",
                (quarter,),
            )
        )
        hist = {"1": 0, "2": 0, "3": 0, "4": 0, "gte_k": 0}
        forwarded_raw_or_class = 0
        for (n,) in cells:
            forwarded_raw_or_class += n
            if n >= 5:
                hist["gte_k"] += 1
            elif str(n) in hist:
                hist[str(n)] += 1
        drop_row = self._conn.execute(
            "SELECT n FROM drops WHERE quarter = ?", (quarter,)
        ).fetchone()
        dropped = drop_row[0] if drop_row else 0
        seen = forwarded_raw_or_class + dropped
        drop_ratio = (dropped / seen) if seen else 0.0
        return {
            "report_type": "A14_quarterly_monitor",
            "quarter": quarter,
            "mode": "ANON",
            "k": 5,
            "events_seen_local": seen,
            "dropped_e_shadow_003": dropped,
            "drop_ratio": drop_ratio,
            "k_cell_size_histogram": hist,
            "g3_recall_drop_does_not_disable_suppression": True,
        }

    def close(self) -> None:
        self._conn.close()
