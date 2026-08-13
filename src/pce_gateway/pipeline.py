from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from pce_gateway.config import GatewayConfig
from pce_gateway.flags import LIVE_CDS
from pce_gateway.frequency import FrequencyTable
from pce_gateway.genetics import extract_diplotypes
from pce_gateway.kcell import KCellStore
from pce_gateway.transform import (
    local_counter_demographics,
    strip_pii_fr460,
    transform_bundle,
)


@dataclass
class GatewayResult:
    event: dict[str, Any] | None
    http: int
    hitl: bool
    suppressed: bool
    error: str | None = None
    reason: str | None = None


def process_his_event(
    bundle: dict[str, Any],
    cfg: GatewayConfig,
    freq: FrequencyTable,
    store: KCellStore,
) -> GatewayResult:
    """Institutional gateway: PII/dose/ATC/time, then A14 freq + k-cell.

    LIVE_CDS stays false. Genetics on the wire are RAW or CLASS or dropped.
    """
    if LIVE_CDS:
        raise RuntimeError("LIVE_CDS must be false in this package")

    base = transform_bundle(bundle, max_atc_level=cfg.max_atc_level, time_grain=cfg.time_grain)
    meds = base.get("medications") or []
    atc = meds[0]["code"] if meds else None
    quarter = base.get("authoredOn")
    if not isinstance(quarter, str):
        quarter = "unknown"
    dips = extract_diplotypes(bundle)
    stripped = strip_pii_fr460(bundle)

    granularity = "RAW"
    phenotype_class = None
    raw_dips: list[dict[str, str]] = []
    suppressed = False
    cells_to_count: list[tuple[str, str, str]] = []

    for dip in dips:
        gene, diplotype = dip["gene"], dip["diplotype"]
        pclass = freq.coarsen_class(gene, diplotype)
        phenotype_class = pclass
        prior = store.peek(pclass, atc or "", quarter) if atc else 0
        including = prior + 1

        drop = False
        coarsen = False
        if freq.is_rarest(gene, diplotype):
            drop = True
        elif freq.is_below_threshold(gene, diplotype):
            if cfg.on_rare == "DROP":
                drop = True
            else:
                coarsen = True
        elif including < cfg.k:
            if cfg.on_small_cell == "DROP":
                drop = True
            else:
                coarsen = True

        if drop:
            store.record_drop(quarter)
            dropped = stamp_gateway_event(
                {
                    "mode": cfg.mode,
                    "org_id": cfg.org_id,
                    "suppressed": True,
                    "diplotype_granularity": None,
                    "payload_genetics": None,
                    "atc_level": cfg.max_atc_level,
                    "time_grain": cfg.time_grain,
                }
            )
            return GatewayResult(
                event=dropped,
                http=202,
                hitl=False,
                suppressed=True,
                error="E-SHADOW-003",
                reason="rare or small-cell drop",
            )
        if coarsen:
            granularity = "CLASS"
        else:
            raw_dips.append(dip)
        if atc:
            cells_to_count.append((pclass, atc, quarter))

    seen: set[tuple[str, str, str]] = set()
    for cell in cells_to_count:
        if cell in seen:
            continue
        seen.add(cell)
        store.increment(*cell)

    event: dict[str, Any] = {
        "mode": cfg.mode,
        "org_id": cfg.org_id,
        "scope": [
            "PCE-GW-460",
            "PCE-GW-461-01",
            "PCE-GW-461-02",
            "PCE-GW-461-03",
            "PCE-GW-461-04",
            "PCE-GW-461-05",
            "PCE-GW-461-06",
            "PCE-GW-461-07",
        ],
        "atc_level": cfg.max_atc_level,
        "time_grain": cfg.time_grain,
        "medications": meds,
        "authoredOn": base.get("authoredOn"),
        "suppressed": suppressed,
        "diplotype_granularity": granularity,
    }
    if granularity == "CLASS":
        event["phenotype_class"] = phenotype_class
        event["raw_diplotype"] = None
        event["diplotypes"] = None
    else:
        event["diplotypes"] = raw_dips
    event = stamp_gateway_event(event)
    blob_keys = json_keys_must_be_absent(event)
    if blob_keys:
        raise RuntimeError(f"export leaked {blob_keys}")
    _ = local_counter_demographics(stripped)
    return GatewayResult(event=event, http=202, hitl=True, suppressed=False)


def stamp_gateway_event(event: dict[str, Any]) -> dict[str, Any]:
    """B.2.2 GatewayEvent: id, received_at, org_id, payload_hash."""
    out = dict(event)
    out["id"] = str(uuid.uuid4())
    out["received_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    canon = {k: v for k, v in out.items() if k not in {"id", "received_at", "payload_hash"}}
    payload = json.dumps(canon, sort_keys=True, separators=(",", ":"), default=str)
    out["payload_hash"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return out


def json_keys_must_be_absent(event: dict[str, Any]) -> list[str]:
    leaked: list[str] = []
    dumped = str(event)
    for token in (
        "SYN-NAME",
        "SYN-TAJ",
        "doseQuantity",
        "escitalopram",
        "Practitioner",
        "RelatedPerson",
    ):
        if token in dumped:
            leaked.append(token)
    if "patient" in event:
        leaked.append("patient")
    if event.get("cell_count") is not None:
        leaked.append("cell_count")
    return leaked
