from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path


class KThresholdRejected(Exception):
    """ANON k cannot be lowered at runtime (PCE-GW-461-08)."""


@dataclass(frozen=True)
class GatewayConfig:
    mode: str = "ANON"
    max_atc_level: int = 4
    time_grain: str = "QUARTER"
    k: int = 5
    on_small_cell: str = "COARSEN"
    on_rare: str = "DROP"
    rare_diplotype_threshold: float = 0.005
    frequency_table_path: Path | None = None
    org_id: str = "SYN-ORG-001"
    research_consent: bool = False

    def with_k(self, new_k: int) -> GatewayConfig:
        if self.mode != "ANON":
            raise KThresholdRejected("PSEUDO k relief is locked until OQ-16 = NEM + DPIA + FR-115")
        if new_k < 5:
            raise KThresholdRejected("ANON k below 5 is forbidden")
        if new_k < self.k:
            raise KThresholdRejected("ANON k decrease is forbidden; raise k only via config release")
        return replace(self, k=new_k)
