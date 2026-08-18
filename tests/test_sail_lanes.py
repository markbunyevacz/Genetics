#!/usr/bin/env python3
"""SAIL lane encode/decode roundtrip (stdlib only)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sail.lanes import decode, encode  # noqa: E402
from sail.memory import embed  # noqa: E402


class LaneRoundtripTests(unittest.TestCase):
    def test_express_floats(self) -> None:
        payload = (1.0, -2.5, 3.25, 0.0)
        got = decode("express", encode("express", payload))
        self.assertEqual(got, payload)

    def test_express_single_int(self) -> None:
        self.assertEqual(decode("express", encode("express", 4)), (4.0,))

    def test_human_unicode(self) -> None:
        text = "árvíztűrő tükörfúrógép"
        self.assertEqual(decode("human", encode("human", text)), text)

    def test_structured_goal_graph(self) -> None:
        payload = {
            "goal": "delegate analysis",
            "concepts": ["task", "analyzer"],
            "relations": [{"src": "task", "dst": "analyzer", "type": "assigned"}],
        }
        got = decode("structured", encode("structured", payload))
        self.assertEqual(got, payload)

    def test_structured_accepts_from_to_keys(self) -> None:
        payload = {
            "goal": "x",
            "concepts": ["a"],
            "relations": [{"from": "a", "to": "x", "type": "is"}],
        }
        got = decode("structured", encode("structured", payload))
        self.assertEqual(got["relations"][0]["src"], "a")
        self.assertEqual(got["relations"][0]["dst"], "x")

    def test_semantic_text_to_stable_vector(self) -> None:
        part = encode("semantic", "market probability field")
        got = decode("semantic", part)
        self.assertEqual(got["text"], "market probability field")
        self.assertEqual(got["vector"], embed("market probability field"))
        again = decode("semantic", encode("semantic", got))
        self.assertEqual(again, got)

    def test_embed_is_deterministic(self) -> None:
        self.assertEqual(embed("hello"), embed("hello"))
        self.assertNotEqual(embed("hello"), embed("world"))

    def test_unknown_lane_rejected(self) -> None:
        with self.assertRaises(ValueError):
            encode("quantum", "nope")


if __name__ == "__main__":
    unittest.main()
