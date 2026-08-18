#!/usr/bin/env python3
"""SAIL selector learning and improvement-engine replay."""
from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sail.engine import ImprovementEngine, Interaction  # noqa: E402
from sail.memory import VectorMemory  # noqa: E402
from sail.selector import LaneSelector  # noqa: E402


def _fail_human(n: int = 5) -> list[Interaction]:
    return [
        Interaction(
            task_kind="plan",
            lane="human",
            payload="do the thing",
            text="do the thing",
            recipient="planner",
            success=False,
            parse_ok=True,
            bytes_len=12,
            elapsed_ms=1.0,
        )
        for _ in range(n)
    ]


class SelectorTests(unittest.TestCase):
    def test_after_human_fails_structured_wins(self) -> None:
        sel = LaneSelector(epsilon=0.0, rng=random.Random(1))
        for _ in range(6):
            sel.record("plan", "human", False)
        for _ in range(6):
            sel.record("plan", "structured", True)
        self.assertEqual(sel.choose("plan", explore=False), "structured")
        self.assertGreater(sel.rate("plan", "structured"), sel.rate("plan", "human"))

    def test_cold_start_prefers_structured(self) -> None:
        sel = LaneSelector(epsilon=0.0, rng=random.Random(2))
        self.assertEqual(sel.choose("plan", explore=False), "structured")


class EngineTests(unittest.TestCase):
    def test_one_step_raises_rolling_success(self) -> None:
        sel = LaneSelector(epsilon=0.0, rng=random.Random(0))
        mem = VectorMemory()
        engine = ImprovementEngine(sel, mem, window=5)
        for item in _fail_human(5):
            engine.record(item)
        before = engine.rolling_success()
        self.assertEqual(before, 0.0)
        report = engine.step()
        after = engine.rolling_success()
        self.assertGreater(after, before)
        self.assertGreater(report.after, report.before)
        self.assertEqual(sel.choose("plan", explore=False), "structured")

    def test_revert_when_replay_would_worsen(self) -> None:
        sel = LaneSelector(epsilon=0.0, rng=random.Random(0))
        mem = VectorMemory()

        def hostile_oracle(task_kind: str, lane: str, payload: object) -> bool:
            del task_kind, payload
            return lane == "human"

        engine = ImprovementEngine(sel, mem, window=4, oracle=hostile_oracle)
        engine.record(
            Interaction(
                task_kind="plan",
                lane="human",
                payload="do the thing",
                text="do the thing",
                recipient="planner",
                success=True,
                parse_ok=True,
                bytes_len=12,
                elapsed_ms=1.0,
            )
        )
        for _ in range(3):
            engine.record(
                Interaction(
                    task_kind="plan",
                    lane="structured",
                    payload={"goal": "x", "concepts": [], "relations": []},
                    text="x",
                    recipient="planner",
                    success=True,
                    parse_ok=True,
                    bytes_len=3,
                    elapsed_ms=1.0,
                )
            )
        before = engine.rolling_success()
        self.assertEqual(before, 1.0)
        report = engine.step()
        self.assertFalse(report.changed)
        self.assertEqual(engine.rolling_success(), before)


if __name__ == "__main__":
    unittest.main()
