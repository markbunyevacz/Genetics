"""CLI: F1+ JSON (+ PDF). FR-100: requires a clinical case; cannot skip the gate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pce_report.flags import LIVE_CDS

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--outside-call",
        "-i",
        help="rejected: outside-call files cannot bypass FR-100",
    )
    p.add_argument("--clinical-db", default="var/clinical.sqlite")
    p.add_argument("--case-id")
    p.add_argument("--json-out", default="-")
    p.add_argument("--pdf-out")
    p.add_argument("--actor", default="lab_signer")
    args = p.parse_args(argv)
    if LIVE_CDS:
        print("LIVE_CDS must be false on the F1+ renderer", file=sys.stderr)
        return 1
    if args.outside_call and not args.case_id:
        print(
            json.dumps(
                {
                    "error": "E-CONSENT-001",
                    "http": 409,
                    "message_hu": "Mintavétel előtti genetikai tanácsadás hiányzik (2008/XXI. 6. § (2)).",
                    "reason": "FR-100: python -m pce_report requires --clinical-db and --case-id",
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2
    if not args.case_id:
        p.error("--case-id and --clinical-db are required (FR-100)")
    from pce_clinical.errors import ClinicalError
    from pce_clinical.service import ClinicalService
    from pce_clinical.store import ClinicalStore

    svc = ClinicalService(ClinicalStore(args.clinical_db))
    try:
        report = svc.create_report(args.case_id, args.actor, role=args.actor)
    except ClinicalError as exc:
        json.dump(exc.as_dict(), sys.stderr, ensure_ascii=False, indent=2)
        sys.stderr.write("\n")
        return 2
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json_out == "-":
        sys.stdout.write(text + "\n")
    else:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")
    if args.pdf_out:
        svc.write_report_pdf(args.case_id, report["report_id"], Path(args.pdf_out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
