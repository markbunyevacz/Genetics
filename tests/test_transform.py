#!/usr/bin/env python3
"""FR-130 / FR-250 / FR-460 / PCE-GW-461-01..03 against Gold V0.

FR-250: default 7-character WHO substance code (truncate_atc).
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pce_gateway.transform import (  # noqa: E402
    ShadowReject,
    generalize_time,
    ingest_guard,
    load_json,
    local_counter_demographics,
    strip_pii_fr460,
    suppress_dose_fr461_03,
    truncate_atc,
    transform_bundle,
)

GOLD = ROOT / "tests" / "fixtures" / "gold-v0"


class TruncateAtcTests(unittest.TestCase):
    def test_default_keeps_substance_code(self) -> None:
        self.assertEqual(truncate_atc("N06AB10"), "N06AB10")

    def test_atc5_to_atc4(self) -> None:
        self.assertEqual(truncate_atc("N06AB10", max_level=4), "N06AB")

    def test_atc5_to_atc3(self) -> None:
        self.assertEqual(truncate_atc("N06AB10", max_level=3), "N06A")

    def test_already_atc4(self) -> None:
        self.assertEqual(truncate_atc("N06AB"), "N06AB")


class GeneralizeTimeTests(unittest.TestCase):
    def test_gold_v0_timestamp(self) -> None:
        self.assertEqual(generalize_time("2026-08-13T01:15:00Z"), "2026-Q3")

    def test_quarter_boundaries(self) -> None:
        self.assertEqual(generalize_time("2026-01-01"), "2026-Q1")
        self.assertEqual(generalize_time("2026-10-01"), "2026-Q4")

    def test_wall_clock_not_utc_shift(self) -> None:
        self.assertEqual(generalize_time("2026-10-01T00:00:00+02:00"), "2026-Q4")


class GoldV0TransformTests(unittest.TestCase):
    def test_v0_01_atc_time_pii_dose(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        expected = load_json(str(GOLD / "gw-v0-01-normal-gateway-out.json"))
        out = transform_bundle(bundle)
        self.assertEqual(out["medications"][0]["code"], expected["GatewayEvent"]["medications"][0]["code"])
        self.assertEqual(out["authoredOn"], expected["GatewayEvent"]["authoredOn"])
        blob = json.dumps(out)
        self.assertNotIn("SYN-NAME-001", blob)
        self.assertNotIn("SYN-TAJ-001", blob)
        self.assertIn("N06AB10", blob)
        self.assertNotIn("escitalopram", blob)
        self.assertNotIn("patient", blob)
        self.assertNotIn("doseQuantity", blob)

    def test_pii_strip_gold_v0_01(self) -> None:
        original = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        snapshot = json.dumps(original)
        cleaned = strip_pii_fr460(original)
        self.assertEqual(json.dumps(original), snapshot)
        patient = next(e["resource"] for e in cleaned["entry"] if e["resource"]["resourceType"] == "Patient")
        self.assertNotIn("name", patient)
        self.assertNotIn("identifier", patient)
        self.assertEqual(patient["birthDate"], "1980")
        self.assertEqual(
            local_counter_demographics(cleaned),
            {"gender": "unknown", "birth_year": "1980"},
        )

    def test_dose_r4_gold_v0_01(self) -> None:
        original = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        cleaned = suppress_dose_fr461_03(original)
        med = next(e["resource"] for e in cleaned["entry"] if e["resource"]["resourceType"] == "MedicationRequest")
        self.assertNotIn("doseAndRate", med["dosageInstruction"][0])
        self.assertEqual(
            original["entry"][2]["resource"]["dosageInstruction"][0]["doseAndRate"][0]["doseQuantity"]["value"],
            10,
        )


class IngestGuardTests(unittest.TestCase):
    def test_atc5_accepted_by_default(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-03-atc5-pce-ingest.json"))
        ingest_guard(bundle)

    def test_atc5_rejected_when_dpo_caps_at_level_4(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-03-atc5-pce-ingest.json"))
        with self.assertRaises(ShadowReject) as ctx:
            ingest_guard(bundle, max_atc_level=4)
        self.assertEqual(ctx.exception.code, "E-SHADOW-001")

    def test_taj(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-08-taj-pce-ingest.json"))
        with self.assertRaises(ShadowReject):
            ingest_guard(bundle)

    def test_day(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-09-day-pce-ingest.json"))
        with self.assertRaises(ShadowReject):
            ingest_guard(bundle)


    def test_practitioner_and_meta_source_stripped(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        bundle["entry"].append(
            {
                "resource": {
                    "resourceType": "Practitioner",
                    "id": "syn-md",
                    "name": [{"text": "SYN-MD-001"}],
                }
            }
        )
        bundle["entry"][2]["resource"]["meta"] = {"source": "urn:ward:SYN-WARD"}
        cleaned = strip_pii_fr460(bundle)
        types = [e["resource"]["resourceType"] for e in cleaned["entry"]]
        self.assertNotIn("Practitioner", types)
        med = next(e["resource"] for e in cleaned["entry"] if e["resource"]["resourceType"] == "MedicationRequest")
        self.assertNotIn("source", (med.get("meta") or {}))
        out = transform_bundle(bundle)
        blob = json.dumps(out)
        self.assertNotIn("Practitioner", blob)
        self.assertNotIn("SYN-WARD", blob)


if __name__ == "__main__":
    unittest.main()
