from __future__ import annotations

from typing import Any

from pce_gateway.config import GatewayConfig
from pce_gateway.frequency import FrequencyTable
from pce_gateway.genetics import payload_diplotypes
from pce_gateway.transform import ShadowReject, ShadowSuppress, ingest_guard


def handle_pce_ingest(
    bundle: dict[str, Any],
    cfg: GatewayConfig,
    freq: FrequencyTable | None = None,
    *,
    authorization: str | None,
    allowed_accounts: set[str],
) -> tuple[int, dict[str, Any]]:
    """POST /v1/shadow/events defense-in-depth. HIS fail-open is the caller's job."""
    if authorization not in allowed_accounts:
        return 403, {"error": "E-SHADOW-002", "http": 403, "hitl": False}
    try:
        ingest_guard(bundle, max_atc_level=cfg.max_atc_level)
    except ShadowReject as e:
        return e.http, e.as_dict()
    if freq is not None:
        for dip in payload_diplotypes(bundle):
            if freq.is_rarest(dip["gene"], dip["diplotype"]) or freq.is_below_threshold(
                dip["gene"], dip["diplotype"]
            ):
                err = ShadowSuppress("raw rare diplotype forbidden on ANON ingest")
                return err.http, err.as_dict()
    return 202, {"ingest": "accepted", "http": 202, "hitl": True}
