"""Self-improvement loop: log, adopt best lanes, replay, revert if worse."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

from sail.envelope import LANE_HUMAN, LANES
from sail.memory import VectorMemory
from sail.selector import LaneSelector

Oracle = Callable[[str, str, Any], bool]


class SupportsSelector(Protocol):
    def choose(self, task_kind: str, *, explore: bool = True) -> str: ...
    def record(self, task_kind: str, lane: str, success: bool) -> None: ...
    def adopt_best(self, *, min_samples: int = 1) -> dict[str, str]: ...
    def snapshot(self) -> None: ...
    def restore(self) -> None: ...


@dataclass(frozen=True)
class Interaction:
    task_kind: str
    lane: str
    payload: Any
    text: str
    recipient: str
    success: bool
    parse_ok: bool
    bytes_len: int
    elapsed_ms: float


@dataclass(frozen=True)
class StepReport:
    changed: bool
    before: float
    after: float
    adopted: dict[str, str]


def default_oracle(task_kind: str, lane: str, payload: Any) -> bool:
    """Offline stand-in for 'did the recipient understand?'.

    Planning is unambiguous on the structured lane and fails on unconstrained
    human text. Numeric signals need express. Concepts need semantic.
    """
    del payload
    if task_kind == "plan":
        return lane != LANE_HUMAN
    if task_kind == "signal":
        return lane == "express"
    if task_kind == "concept":
        return lane in ("semantic", "structured")
    if task_kind == "analyze":
        return lane in ("express", "semantic", "structured")
    return lane in LANES and lane != LANE_HUMAN


class ImprovementEngine:
    def __init__(
        self,
        selector: LaneSelector | SupportsSelector,
        memory: VectorMemory,
        *,
        window: int = 8,
        oracle: Oracle | None = None,
    ) -> None:
        if window < 1:
            raise ValueError("window must be >= 1")
        self.selector = selector
        self.memory = memory
        self.window = window
        self.oracle = oracle or default_oracle
        self.log: list[Interaction] = []
        self._epochs: list[list[bool]] = [[]]

    def record(self, item: Interaction) -> None:
        self.log.append(item)
        self._epochs[-1].append(item.success)
        self.selector.record(item.task_kind, item.lane, item.success)
        self.memory.remember(
            item.text,
            lane=item.lane,
            task_kind=item.task_kind,
            recipient=item.recipient,
            success=item.success,
        )

    def rolling_success(self) -> float:
        outcomes = self._epochs[-1]
        if not outcomes:
            return 0.0
        return sum(1.0 for ok in outcomes if ok) / len(outcomes)

    def step(self) -> StepReport:
        before = self.rolling_success()
        self.selector.snapshot()
        adopted = self.selector.adopt_best(min_samples=1)
        recent = self.log[-self.window :]
        replay: list[bool] = []
        for item in recent:
            lane = self.selector.choose(item.task_kind, explore=False)
            replay.append(bool(self.oracle(item.task_kind, lane, item.payload)))
        after = (sum(1.0 for ok in replay if ok) / len(replay)) if replay else before
        if after < before:
            self.selector.restore()
            return StepReport(changed=False, before=before, after=before, adopted={})
        self._epochs.append(replay)
        return StepReport(changed=bool(adopted) or after != before, before=before, after=after, adopted=adopted)
