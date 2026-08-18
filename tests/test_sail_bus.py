#!/usr/bin/env python3
"""SAIL bus delegation, CLI demo, and PCE isolation."""
from __future__ import annotations

import ast
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sail.__main__ import main, run_demo  # noqa: E402
from sail.agents import ANALYZER, PLANNER, AnalyzerAgent, CoordinatorAgent, PlannerAgent  # noqa: E402
from sail.bus import InProcessBus, UnknownAgentError  # noqa: E402
from sail.engine import ImprovementEngine  # noqa: E402
from sail.envelope import Envelope  # noqa: E402
from sail.lanes import encode  # noqa: E402
from sail.memory import VectorMemory  # noqa: E402
from sail.selector import LaneSelector  # noqa: E402

PCE_PACKAGES = (
    "pce_gateway",
    "pce_report",
    "pce_clinical",
    "pce_cds",
    "pce_hitl",
    "pce_shadow",
)


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


class BusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bus = InProcessBus()
        self.bus.register(ANALYZER, AnalyzerAgent().handle)
        self.bus.register(PLANNER, PlannerAgent().handle)
        self.selector = LaneSelector(epsilon=0.0)
        self.memory = VectorMemory()
        self.engine = ImprovementEngine(self.selector, self.memory, window=6)
        self.coord = CoordinatorAgent(
            self.bus, self.selector, self.memory, self.engine, explore=False
        )

    def test_plan_goes_to_planner(self) -> None:
        reply = self.coord.run("Plan the next delegation steps")
        self.assertEqual(reply.sender, PLANNER)
        self.assertEqual(reply.meta_dict().get("ok"), "1")

    def test_analyze_goes_to_analyzer(self) -> None:
        reply = self.coord.run("Analyze CPU load numbers")
        self.assertEqual(reply.sender, ANALYZER)
        self.assertEqual(reply.meta_dict().get("ok"), "1")

    def test_planner_rejects_human_lane(self) -> None:
        msg = Envelope(
            role="user",
            lane="human",
            parts=(encode("human", "please do something clever"),),
            sender="coordinator",
            recipient=PLANNER,
            task_kind="plan",
        )
        reply = self.bus.send(msg)
        self.assertEqual(reply.meta_dict().get("ok"), "0")

    def test_unknown_recipient(self) -> None:
        msg = Envelope(
            role="user",
            lane="human",
            parts=(encode("human", "x"),),
            sender="coordinator",
            recipient="no-such-agent",
            task_kind="plan",
        )
        with self.assertRaises(UnknownAgentError):
            self.bus.send(msg)


class DemoTests(unittest.TestCase):
    def test_main_exits_zero(self) -> None:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            code = main([])
        finally:
            sys.stdout = old
        self.assertEqual(code, 0)
        self.assertIn("before", buf.getvalue())

    def test_run_demo_has_metrics(self) -> None:
        metrics = run_demo()
        self.assertIn("adopted", metrics)
        self.assertGreaterEqual(metrics["memory_size"], 1)
        self.assertEqual(len(metrics["first_pass"]), 6)


class IsolationTests(unittest.TestCase):
    def test_sail_does_not_import_clinical_packages(self) -> None:
        sail_root = ROOT / "src" / "sail"
        forbidden = tuple(PCE_PACKAGES) + tuple(p + "." for p in PCE_PACKAGES)
        for path in sorted(sail_root.rglob("*.py")):
            for mod in _imported_modules(path):
                self.assertFalse(
                    mod in PCE_PACKAGES or any(mod.startswith(p) for p in forbidden),
                    msg=f"{path} imports {mod}",
                )

    def test_clinical_packages_do_not_import_sail(self) -> None:
        src = ROOT / "src"
        for pkg in PCE_PACKAGES:
            root = src / pkg
            if not root.exists():
                continue
            for path in sorted(root.rglob("*.py")):
                for mod in _imported_modules(path):
                    self.assertFalse(
                        mod == "sail" or mod.startswith("sail."),
                        msg=f"{path} imports {mod}",
                    )

    def test_llm_hook_is_optional(self) -> None:
        from sail.llm import require_dspy

        try:
            import dspy  # noqa: F401
        except ImportError:
            with self.assertRaises(ImportError):
                require_dspy()
        else:
            self.assertIsNotNone(require_dspy())


if __name__ == "__main__":
    unittest.main()
