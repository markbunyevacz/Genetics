from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FrequencyTable:
    """A14 allowlist from CPIC European HW diplotype frequencies. Unknown → rare."""

    def __init__(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"{path} is not a JSON object")
        self.threshold = float(data["rare_diplotype_threshold"])
        self.keep: dict[tuple[str, str], float] = {}
        for rec in data.get("keep_european_cyp2d6_freq_gte_0_005") or []:
            self.keep[(rec["gene"], rec["diplotype"])] = float(rec["frequency"])
        for rec in data.get("keep_european_cyp2c19_freq_gte_0_005") or []:
            self.keep[(rec["gene"], rec["diplotype"])] = float(rec["frequency"])
        rare = data.get("fixture_rare") or {}
        self._rare_extra: dict[tuple[str, str], float] = {}
        if rare:
            self._rare_extra[(rare["gene"], rare["diplotype"])] = float(rare["frequency"])
        rarest = data.get("rarest_positive_in_full_cpic_european_diplotype_sheet") or {}
        self.rarest_key: tuple[str, str] | None = None
        if rarest:
            self.rarest_key = (rarest["gene"], rarest["diplotype"])
            self._rare_extra[self.rarest_key] = float(rarest["frequency"])
        self._phenotype: dict[str, dict[str, Any]] = {}
        for rec in data.get("phenotype_for_fixtures") or []:
            self._phenotype[rec["diplotype"]] = rec

    def frequency(self, gene: str, diplotype: str) -> float | None:
        key = (gene, diplotype)
        if key in self.keep:
            return self.keep[key]
        if key in self._rare_extra:
            return self._rare_extra[key]
        return None

    def is_rarest(self, gene: str, diplotype: str) -> bool:
        return self.rarest_key == (gene, diplotype)

    def is_below_threshold(self, gene: str, diplotype: str) -> bool:
        freq = self.frequency(gene, diplotype)
        if freq is None:
            return True
        return freq < self.threshold

    def coarsen_class(self, gene: str, diplotype: str) -> str:
        ph = self._phenotype.get(diplotype) or {}
        explicit = ph.get("coarsen_class_if_needed")
        if explicit in {"REDUCED", "INCREASED", "UNCERTAIN"}:
            return explicit
        summary = str(ph.get("cpic_summary") or "")
        if "Poor Metabolizer" in summary or "Intermediate Metabolizer" in summary:
            return "REDUCED"
        if "Ultrarapid" in summary:
            return "INCREASED"
        return "UNCERTAIN"
