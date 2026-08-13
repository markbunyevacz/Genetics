"""CLI: HITL reviewer HTTP (separate from the clinical F1+ server)."""
from __future__ import annotations

import argparse
import sys

from pce_hitl.server import bind_hitl_server
from pce_gateway.flags import LIVE_CDS


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", default="var/hitl.sqlite")
    p.add_argument("--port", type=int, default=8091)
    args = p.parse_args(argv)
    if LIVE_CDS:
        print("LIVE_CDS is true — refusing to start HITL as a clinical CDS", file=sys.stderr)
        return 1
    httpd = bind_hitl_server(args.db, port=args.port)
    bound = httpd.server_address[1]
    print(f"pce_hitl on 127.0.0.1:{bound} db={args.db}")
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
