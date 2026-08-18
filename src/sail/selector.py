"""Empirical lane selector: epsilon-greedy over (task_kind, lane) success."""

from __future__ import annotations

import random
from dataclasses import dataclass

from sail.envelope import (
    LANE_EXPRESS,
    LANE_HUMAN,
    LANE_SEMANTIC,
    LANE_STRUCTURED,
    LANES,
)

# Cold-start and tie-break: structured first (planning/delegation default).
_TIE_BREAK = {
    LANE_STRUCTURED: 4,
    LANE_SEMANTIC: 3,
    LANE_EXPRESS: 2,
    LANE_HUMAN: 1,
}


@dataclass(frozen=True)
class LaneStats:
    success: int = 0
    total: int = 0

    @property
    def rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.success / self.total


class LaneSelector:
    def __init__(self, *, epsilon: float = 0.1, rng: random.Random | None = None) -> None:
        if not 0.0 <= epsilon <= 1.0:
            raise ValueError("epsilon must be in [0, 1]")
        self.epsilon = epsilon
        self._rng = rng or random.Random(0)
        self._stats: dict[tuple[str, str], LaneStats] = {}
        self._stats_snap: dict[tuple[str, str], LaneStats] | None = None
        self._preferred: dict[str, str] = {}
        self._preferred_snap: dict[str, str] | None = None

    def record(self, task_kind: str, lane: str, success: bool) -> None:
        if lane not in LANES:
            raise ValueError(f"unknown lane {lane!r}")
        key = (task_kind, lane)
        cur = self._stats.get(key, LaneStats())
        self._stats[key] = LaneStats(
            success=cur.success + (1 if success else 0),
            total=cur.total + 1,
        )

    def rate(self, task_kind: str, lane: str) -> float:
        return self._stats.get((task_kind, lane), LaneStats()).rate

    def samples(self, task_kind: str, lane: str) -> int:
        return self._stats.get((task_kind, lane), LaneStats()).total

    def choose(self, task_kind: str, *, explore: bool = True) -> str:
        if explore and self._rng.random() < self.epsilon:
            return self._rng.choice(LANES)
        preferred = self._preferred.get(task_kind)
        if preferred:
            return preferred
        return self.best_lane(task_kind)

    def best_lane(self, task_kind: str) -> str:
        scored: list[tuple[float, int, str]] = []
        for lane in LANES:
            st = self._stats.get((task_kind, lane), LaneStats())
            scored.append((st.rate, _TIE_BREAK[lane], lane))
        scored.sort(reverse=True)
        return scored[0][2]

    def adopt_best(self, *, min_samples: int = 1) -> dict[str, str]:
        """Pin each seen task_kind to its empirically best lane."""
        kinds = {k for (k, _lane) in self._stats}
        changed: dict[str, str] = {}
        for kind in kinds:
            totals = sum(self.samples(kind, lane) for lane in LANES)
            if totals < min_samples:
                continue
            lane = self.best_lane(kind)
            self._preferred[kind] = lane
            changed[kind] = lane
        return changed

    def snapshot(self) -> None:
        self._stats_snap = dict(self._stats)
        self._preferred_snap = dict(self._preferred)

    def restore(self) -> None:
        if self._stats_snap is None:
            return
        self._stats = dict(self._stats_snap)
        self._preferred = dict(self._preferred_snap or {})
