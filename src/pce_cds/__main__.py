"""CLI: F2 CDS Hooks process. Compile-time LIVE_CDS from pce_gateway.flags."""
from __future__ import annotations

import argparse
import sys

from pce_cds.policy import IIA_SAFE_BLOCK
from pce_cds.server import bind_cds_server
from pce_gateway.flags import LIVE_CDS


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=int, default=8092)
    args = p.parse_args(argv)
    httpd = bind_cds_server(port=args.port, live_cds=LIVE_CDS, iia_safe_block=IIA_SAFE_BLOCK)
    bound = httpd.server_address[1]
    state = "LIVE" if LIVE_CDS else "LOCKED"
    print(f"pce_cds on 127.0.0.1:{bound} LIVE_CDS={LIVE_CDS} ({state})")
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
