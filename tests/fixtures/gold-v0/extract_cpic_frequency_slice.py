#!/usr/bin/env python3
"""Slice official CPIC Diplotype frequency / European into Gold V0 keep-sets.

Does not invent frequencies. Requires the official xlsx files:

  https://files.cpicpgx.org/data/report/current/frequency/CYP2D6_frequency_table.xlsx
  https://files.cpicpgx.org/data/report/current/frequency/CYP2C19_frequency_table.xlsx

Usage:
  python3 extract_cpic_frequency_slice.py /path/to/CYP2D6_frequency_table.xlsx \\
      /path/to/CYP2C19_frequency_table.xlsx
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


def slice_gene(xlsx: Path, gene: str) -> dict:
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    ws = wb["Diplotype frequency"]
    rows = list(ws.iter_rows(values_only=True))
    header = list(rows[1])
    ei = header.index("European")
    keep = []
    rare_66 = None
    min_pos = None
    n_below = n_zero = n_none = 0
    for r in rows[2:]:
        if not r or not r[0]:
            continue
        raw = r[ei]
        if raw in (None, ""):
            n_none += 1
            continue
        try:
            f = float(raw)
        except (TypeError, ValueError):
            n_none += 1
            continue
        rec = {
            "gene": gene,
            "diplotype": r[0],
            "biogeographic_group": "European",
            "frequency": f,
        }
        if f == 0.0:
            n_zero += 1
        elif f < THRESHOLD:
            n_below += 1
            if min_pos is None or f < min_pos["frequency"]:
                min_pos = rec
        else:
            keep.append(rec)
        if gene == "CYP2D6" and r[0] == "*6/*6":
            rare_66 = rec
    wb.close()
    keep.sort(key=lambda x: -x["frequency"])
    return {
        "keep": keep,
        "fixture_rare": rare_66,
        "rarest_positive": min_pos,
        "n_below": n_below,
        "n_zero": n_zero,
        "n_none": n_none,
        "n_numeric": len(keep) + n_below + n_zero,
    }


def main(d6: Path, c19: Path) -> None:
    a = slice_gene(d6, "CYP2D6")
    b = slice_gene(c19, "CYP2C19")
    out = {
        "keep_n_cyp2d6": len(a["keep"]),
        "keep_cyp2d6": a["keep"],
        "fixture_rare": a["fixture_rare"],
        "rarest_positive_cyp2d6": a["rarest_positive"],
        "cyp2d6_numeric_european_rows": a["n_numeric"],
        "cyp2d6_positive_below_threshold": a["n_below"],
        "cyp2d6_zero": a["n_zero"],
        "keep_n_cyp2c19": len(b["keep"]),
        "keep_cyp2c19": b["keep"],
        "rarest_positive_cyp2c19": b["rarest_positive"],
        "threshold": THRESHOLD,
        "threshold_status": "A14_ASSUMPTION",
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
