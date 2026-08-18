"""CLI demo: a few tasks, one improvement step, printed metrics. Always exits 0 on success."""

from __future__ import annotations

import json
import random
import sys

from sail.agents import ANALYZER, PLANNER, AnalyzerAgent, CoordinatorAgent, PlannerAgent
from sail.bus import InProcessBus
from sail.engine import ImprovementEngine
from sail.memory import VectorMemory
from sail.selector import LaneSelector

DEMO_TASKS = (
    "Analyze CPU load vector for the last window",
    "Plan the next three delegation steps for the analyzer",
    "Count signal spikes in the metric stream",
    "Design a goal graph for collaborative planning",
    "Analyze the number of failed human-lane messages",
    "Plan how to delegate structured tasks to the planner",
)


def build_system(*, epsilon: float = 0.35, seed: int = 7) -> CoordinatorAgent:
    rng = random.Random(seed)
    bus = InProcessBus()
    bus.register(ANALYZER, AnalyzerAgent().handle)
    bus.register(PLANNER, PlannerAgent().handle)
    selector = LaneSelector(epsilon=epsilon, rng=rng)
    memory = VectorMemory()
    engine = ImprovementEngine(selector, memory, window=6)
    return CoordinatorAgent(bus, selector, memory, engine, explore=True)


def run_demo() -> dict:
    coord = build_system()
    first_pass = []
    for text in DEMO_TASKS:
        reply = coord.run(text)
        first_pass.append({"task": text, "ok": reply.meta_dict().get("ok") == "1", "from": reply.sender})
    before = coord.engine.rolling_success()
    report = coord.engine.step()
    coord.explore = False
    second_pass = []
    for text in DEMO_TASKS:
        reply = coord.run(text)
        second_pass.append({"task": text, "ok": reply.meta_dict().get("ok") == "1", "from": reply.sender})
    return {
        "before": before,
        "step_after": report.after,
        "step_changed": report.changed,
        "adopted": report.adopted,
        "after_second_pass": coord.engine.rolling_success(),
        "memory_size": len(coord.engine.memory),
        "first_pass": first_pass,
        "second_pass": second_pass,
    }


def main(argv: list[str] | None = None) -> int:
    del argv
    metrics = run_demo()
    json.dump(metrics, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
