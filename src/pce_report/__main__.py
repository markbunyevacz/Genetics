"""CLI: F1+ JSON (+ PDF) from an outside-call file and pinned CPIC tables."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pce_report.flags import LIVE_CDS, MATCHER_ON
from pce_report.guidelines import GuidelineTable
from pce_report.pdf import write_pdf
from pce_report.render import render_f1plus

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PAIRS = ROOT / "tests" / "fixtures" / "f1plus-v0" / "cyp2d6-cpic-pair-view.v0.json"
DEFAULT_RECS = ROOT / "tests" / "fixtures" / "f1plus-v0" / "cyp2d6-cpic-recommendation-view.v0.json"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outside-call", "-i", required=True)
    p.add_argument("--pairs", default=str(DEFAULT_PAIRS))
    p.add_argument("--recommendations", default=str(DEFAULT_RECS))
    p.add_argument("--json-out", default="-")
    p.add_argument("--pdf-out")
    args = p.parse_args(argv)
    if MATCHER_ON or LIVE_CDS:
        print("F1+ matcher/LIVE_CDS must be false", file=sys.stderr)
        return 1
    call = json.loads(Path(args.outside_call).read_text(encoding="utf-8"))
    table = GuidelineTable(Path(args.pairs), Path(args.recommendations))
    report = render_f1plus(outside_call=call, table=table)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json_out == "-":
        sys.stdout.write(text + "\n")
    else:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")
    if args.pdf_out:
        write_pdf(report, Path(args.pdf_out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
