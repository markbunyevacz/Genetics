"""FR-310 PREPARE-12 default gene set from PCE-SPEC-v1.2 (Lancet 2023 start panel)."""

from __future__ import annotations

# Spec FR-310: CYP2B6, CYP2C9, CYP2C19, CYP2D6, CYP3A5, DPYD, F5, HLA-B,
# SLCO1B1, TPMT, UGT1A1, VKORC1. HLA-A and NUDT15 are optional, separate config.
PREPARE_12: tuple[str, ...] = (
    "CYP2B6",
    "CYP2C9",
    "CYP2C19",
    "CYP2D6",
    "CYP3A5",
    "DPYD",
    "F5",
    "HLA-B",
    "SLCO1B1",
    "TPMT",
    "UGT1A1",
    "VKORC1",
)

CONFIG_ID_PREFIX = "pgx-prepare-12"
