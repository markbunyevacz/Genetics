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
    hitl_store: Any | None = None,
) -> tuple[int, dict[str, Any]]:
    """POST /v1/shadow/events defense-in-depth. HIS fail-open is the caller's job.

    Accepted 202 may persist a ShadowInference into the HITL store. A store
    failure must not change the HIS HTTP code (E.2).
    """
    if authorization not in allowed_accounts:
        return 403, {"error": "E-SHADOW-002", "http": 403, "hitl": False}
    if cfg.mode == "PSEUDO" and not cfg.research_consent:
        return 409, {
            "error": "E-CONSENT-006",
            "http": 409,
            "hitl": False,
            "message_hu": "Álnevesített shadow, nincs kutatási hozzájárulás (FR-115).",
        }
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
    if hitl_store is not None:
        try:
            from pce_hitl.service import persist_inference

            persist_inference(hitl_store, bundle)
        except Exception:
            pass
    return 202, {"ingest": "accepted", "http": 202, "hitl": True}
