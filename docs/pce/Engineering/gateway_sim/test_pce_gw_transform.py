#!/usr/bin/env python3
"""TC-GW-010..013 slice tests against Gold V0 (PCE-GW-461-01 / 461-02)."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLD = HERE.parent / "fixtures" / "gold-v0"
SCRIPT = HERE / "pce_gw_transform.py"

sys.path.insert(0, str(HERE))
from pce_gw_transform import (  # noqa: E402
    ShadowReject,
    generalize_time,
    ingest_guard,
    load_json,
    truncate_atc,
    transform_bundle,
)


def _cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


class TruncateAtcTests(unittest.TestCase):
    def test_atc5_to_atc4(self) -> None:
        self.assertEqual(truncate_atc("N06AB10"), "N06AB")
        self.assertEqual(truncate_atc("n06ab10"), "N06AB")

    def test_atc5_to_atc3(self) -> None:
        self.assertEqual(truncate_atc("N06AB10", max_level=3), "N06A")

    def test_already_atc4(self) -> None:
        self.assertEqual(truncate_atc("N06AB"), "N06AB")

    def test_already_coarser_than_max(self) -> None:
        self.assertEqual(truncate_atc("N06A", max_level=4), "N06A")

    def test_rejects_non_atc(self) -> None:
        with self.assertRaises(ValueError):
            truncate_atc("escitalopram")


class GeneralizeTimeTests(unittest.TestCase):
    def test_gold_v0_timestamp(self) -> None:
        self.assertEqual(generalize_time("2026-08-13T01:15:00Z"), "2026-Q3")

    def test_quarter_boundaries(self) -> None:
        self.assertEqual(generalize_time("2026-01-01"), "2026-Q1")
        self.assertEqual(generalize_time("2026-03-31T23:59:59Z"), "2026-Q1")
        self.assertEqual(generalize_time("2026-04-01"), "2026-Q2")
        self.assertEqual(generalize_time("2026-07-01"), "2026-Q3")
        self.assertEqual(generalize_time("2026-09-30"), "2026-Q3")
        self.assertEqual(generalize_time("2026-10-01"), "2026-Q4")
        self.assertEqual(generalize_time("2026-12-31"), "2026-Q4")

    def test_already_quarter(self) -> None:
        self.assertEqual(generalize_time("2026-Q3"), "2026-Q3")

    def test_year_grain(self) -> None:
        self.assertEqual(generalize_time("2026-08-13T01:15:00Z", "YEAR"), "2026")
        self.assertEqual(generalize_time("2026-Q3", "YEAR"), "2026")

    def test_year_only_does_not_invent_quarter(self) -> None:
        self.assertEqual(generalize_time("2026", "QUARTER"), "2026")

    def test_wall_clock_not_utc_shift(self) -> None:
        self.assertEqual(generalize_time("2026-10-01T00:00:00+02:00"), "2026-Q4")


class GoldV0GatewayTests(unittest.TestCase):
    def test_v0_01_atc_and_time(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        expected = load_json(str(GOLD / "gw-v0-01-normal-gateway-out.json"))
        out = transform_bundle(bundle)
        self.assertEqual(out["medications"][0]["code"], expected["GatewayEvent"]["medications"][0]["code"])
        self.assertEqual(out["authoredOn"], expected["GatewayEvent"]["authoredOn"])
        self.assertEqual(out["atc_level"], expected["GatewayEvent"]["atc_level"])
        self.assertEqual(out["time_grain"], expected["GatewayEvent"]["time_grain"])
        blob = json.dumps(out)
        self.assertNotIn("SYN-NAME-001", blob)
        self.assertNotIn("SYN-TAJ-001", blob)
        self.assertNotIn("N06AB10", blob)
        self.assertNotIn("2026-08-13", blob)
        self.assertNotIn("escitalopram", blob)

    def test_v0_02_already_atc4_still_generalizes_time(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-02-rare-diplotype-his-in.json"))
        out = transform_bundle(bundle)
        self.assertEqual(out["medications"][0]["code"], "N06AB")
        self.assertEqual(out["authoredOn"], "2026-Q3")
        self.assertEqual(out["medications"][0]["display"], "Selective serotonin reuptake inhibitors")

    def test_atc3_config(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        out = transform_bundle(bundle, max_atc_level=3)
        self.assertEqual(out["medications"][0]["code"], "N06A")
        self.assertEqual(out["atc_level"], 3)


class GoldV0IngestTests(unittest.TestCase):
    def test_v0_03_atc5_rejected(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-03-atc5-pce-ingest.json"))
        with self.assertRaises(ShadowReject) as ctx:
            ingest_guard(bundle)
        self.assertEqual(ctx.exception.code, "E-SHADOW-001")
        self.assertEqual(ctx.exception.http, 400)
        self.assertFalse(ctx.exception.hitl)
        expected = load_json(str(GOLD / "gw-v0-03-atc5-expected.json"))
        self.assertEqual(ctx.exception.code, expected["expected"]["error"])
        self.assertEqual(ctx.exception.http, expected["expected"]["http"])

    def test_v0_09_day_timestamp_rejected(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-09-day-pce-ingest.json"))
        with self.assertRaises(ShadowReject) as ctx:
            ingest_guard(bundle)
        self.assertEqual(ctx.exception.code, "E-SHADOW-001")
        expected = load_json(str(GOLD / "gw-v0-09-day-expected.json"))
        self.assertEqual(ctx.exception.http, expected["expected"]["http"])

    def test_gateway_then_ingest_accepts_atc_and_time(self) -> None:
        his = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        event = transform_bundle(his)
        synthetic = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "MedicationRequest",
                        "authoredOn": event["authoredOn"],
                        "medicationCodeableConcept": {
                            "coding": [
                                {
                                    "system": "http://www.whocc.no/atc",
                                    "code": event["medications"][0]["code"],
                                }
                            ]
                        },
                    }
                }
            ],
        }
        ingest_guard(synthetic)


class CliTests(unittest.TestCase):
    def test_gateway_cli_gold_v0_01(self) -> None:
        proc = _cli("--input", str(GOLD / "gw-v0-01-normal-his-in.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["medications"][0]["code"], "N06AB")
        self.assertEqual(out["authoredOn"], "2026-Q3")

    def test_ingest_cli_atc5(self) -> None:
        proc = _cli(
            "--mode",
            "ingest",
            "--input",
            str(GOLD / "gw-v0-03-atc5-pce-ingest.json"),
        )
        self.assertEqual(proc.returncode, 2, proc.stdout)
        out = json.loads(proc.stdout)
        self.assertEqual(out["error"], "E-SHADOW-001")
        self.assertFalse(out["hitl"])


if __name__ == "__main__":
    unittest.main()
