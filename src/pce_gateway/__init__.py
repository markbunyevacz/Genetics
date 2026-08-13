"""Institutional ANON gateway (FR-460 / FR-461). LIVE_CDS is compile-time false."""

from pce_gateway.flags import LIVE_CDS
from pce_gateway.config import GatewayConfig, KThresholdRejected
from pce_gateway.frequency import FrequencyTable
from pce_gateway.kcell import KCellStore
from pce_gateway.pipeline import GatewayResult, process_his_event
from pce_gateway.ingest import handle_pce_ingest
from pce_gateway.transform import ShadowReject, ShadowSuppress, ingest_guard, transform_bundle

__all__ = [
    "LIVE_CDS",
    "GatewayConfig",
    "KThresholdRejected",
    "FrequencyTable",
    "KCellStore",
    "GatewayResult",
    "process_his_event",
    "handle_pce_ingest",
    "ShadowReject",
    "ShadowSuppress",
    "ingest_guard",
    "transform_bundle",
]
