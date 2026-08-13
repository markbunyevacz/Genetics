"""CLI: institutional transform, PCE ingest guard, or local HTTP ingest."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from pce_gateway.config import GatewayConfig
from pce_gateway.flags import LIVE_CDS
from pce_gateway.frequency import FrequencyTable
from pce_gateway.ingest import handle_pce_ingest
from pce_gateway.kcell import KCellStore
from pce_gateway.pipeline import process_his_event
from pce_gateway.server import bind_ingest_server
from pce_gateway.transform import ShadowReject, load_json, transform_bundle

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FREQ = ROOT / "tests" / "fixtures" / "gold-v0" / "frequency-config.v0.json"


def _cfg(args: argparse.Namespace) -> GatewayConfig:
    return GatewayConfig(
        max_atc_level=args.atc_level,
        time_grain=args.time_grain.upper(),
        on_small_cell=args.on_small_cell,
        on_rare=args.on_rare,
        frequency_table_path=Path(args.frequency_table),
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", "-i", help="FHIR Bundle JSON")
    p.add_argument("--mode", choices=("gateway", "ingest", "serve"), default="gateway")
    p.add_argument("--atc-level", type=int, default=4, choices=(1, 2, 3, 4, 5))
    p.add_argument("--time-grain", default="QUARTER", choices=("QUARTER", "YEAR", "quarter", "year"))
    p.add_argument("--on-small-cell", default="COARSEN", choices=("COARSEN", "DROP"))
    p.add_argument("--on-rare", default="DROP", choices=("COARSEN", "DROP"))
    p.add_argument("--frequency-table", default=str(DEFAULT_FREQ))
    p.add_argument("--kcell-db", default="var/kcell.sqlite")
    p.add_argument("--hitl-db", default="var/hitl.sqlite")
    p.add_argument("--seed-cell", type=int, default=0, help="pre-count for the event's cell (tests)")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument(
        "--account",
        default=os.environ.get("PCE_GW_ACCOUNT", ""),
        help="service-account token allowed to POST /v1/shadow/events",
    )
    args = p.parse_args(argv)
    if LIVE_CDS:
        print("LIVE_CDS is true — refusing to start", file=sys.stderr)
        return 1
    cfg = _cfg(args)
    freq = FrequencyTable(Path(args.frequency_table)) if Path(args.frequency_table).is_file() else None

    if args.mode == "serve":
        if not args.account:
            print("serve requires --account or PCE_GW_ACCOUNT", file=sys.stderr)
            return 1
        from pce_hitl.store import HitlStore

        httpd = bind_ingest_server(
            cfg,
            freq,
            {args.account},
            host="127.0.0.1",
            port=args.port,
            hitl_store=HitlStore(args.hitl_db),
        )
        bound = httpd.server_address[1]
        print(f"pce_gateway ingest on 127.0.0.1:{bound} LIVE_CDS={LIVE_CDS}")
        try:
            httpd.serve_forever()
        finally:
            httpd.server_close()
        return 0

    if not args.input:
        p.error("--input is required unless --mode serve")
    bundle = load_json(args.input)
    try:
        if args.mode == "ingest":
            from pce_hitl.store import HitlStore

            status, out = handle_pce_ingest(
                bundle,
                cfg,
                freq,
                authorization=args.account or "local",
                allowed_accounts={args.account or "local"},
                hitl_store=HitlStore(args.hitl_db),
            )
            json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
            sys.stdout.write("\n")
            return 0 if status < 400 else 2
        if freq is None:
            out = transform_bundle(
                bundle, max_atc_level=cfg.max_atc_level, time_grain=cfg.time_grain
            )
            json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
            sys.stdout.write("\n")
            return 0
        store = KCellStore(args.kcell_db)
        if args.seed_cell:
            from pce_gateway.genetics import extract_diplotypes

            dips = extract_diplotypes(bundle)
            base = transform_bundle(bundle, max_atc_level=cfg.max_atc_level)
            meds = base["medications"]
            if dips and meds:
                pclass = freq.coarsen_class(dips[0]["gene"], dips[0]["diplotype"])
                store.seed(pclass, meds[0]["code"], base["authoredOn"], args.seed_cell)
        result = process_his_event(bundle, cfg, freq, store)
        payload = result.event or {"error": result.error, "reason": result.reason}
        if result.error:
            payload = {
                "error": result.error,
                "http": result.http,
                "hitl": result.hitl,
                "reason": result.reason,
                "GatewayEvent": result.event,
            }
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0 if not result.suppressed else 0
    except ShadowReject as e:
        json.dump(e.as_dict(), sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
