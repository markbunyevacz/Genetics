#!/usr/bin/env python3
"""Slice CPIC CYP2D6 Diplotype frequency / European into Gold V0 keep-set.

Does not invent frequencies. Requires the official xlsx:
https://files.cpicpgx.org/data/report/current/frequency/CYP2D6_frequency_table.xlsx

Usage:
  python3 extract_cpic_frequency_slice.py /path/to/CYP2D6_frequency_table.xlsx
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    raise SystemExit("openpyxl required: pip install openpyxl")

THRESHOLD = 0.005  # A14 assumption; not a CPIC constant


def main(xlsx: Path) -> None:
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    ws = wb["Diplotype frequency"]
    rows = list(ws.iter_rows(values_only=True))
    header = list(rows[1])
    ei = header.index("European")
    keep = []
    rare_66 = None
    for r in rows[2:]:
        if not r or not r[0]:
            continue
        try:
            f = float(r[ei])
        except (TypeError, ValueError):
            continue
        rec = {
            "gene": "CYP2D6",
            "diplotype": r[0],
            "biogeographic_group": "European",
            "frequency": f,
        }
        if f >= THRESHOLD:
            keep.append(rec)
        if r[0] == "*6/*6":
            rare_66 = rec
    wb.close()
    keep.sort(key=lambda x: -x["frequency"])
    print(json.dumps({"keep_n": len(keep), "keep": keep, "fixture_rare": rare_66}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
