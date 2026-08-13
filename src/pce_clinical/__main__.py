"""CLI: clinical HTTP server or gated F1+ render (FR-100)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pce_clinical.server import bind_clinical_server
from pce_clinical.service import ClinicalService
from pce_clinical.store import ClinicalStore
from pce_report.flags import LIVE_CDS, MATCHER_ON


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("serve", "report"), default="serve")
    p.add_argument("--db", default="var/clinical.sqlite")
    p.add_argument("--port", type=int, default=8090)
    p.add_argument("--case-id")
    p.add_argument("--json-out", default="-")
    p.add_argument("--pdf-out")
    p.add_argument("--actor", default="lab_signer")
    args = p.parse_args(argv)
    if MATCHER_ON or LIVE_CDS:
        print("F1+ matcher/LIVE_CDS must be false", file=sys.stderr)
        return 1
    if args.mode == "serve":
        httpd = bind_clinical_server(args.db, port=args.port)
        bound = httpd.server_address[1]
        print(f"pce_clinical on 127.0.0.1:{bound} db={args.db}")
        try:
            httpd.serve_forever()
        finally:
            httpd.server_close()
        return 0
    if not args.case_id:
        p.error("--case-id is required for --mode report")
    svc = ClinicalService(ClinicalStore(args.db))
    from pce_clinical.errors import ClinicalError

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
