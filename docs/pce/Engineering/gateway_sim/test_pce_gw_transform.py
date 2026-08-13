#!/usr/bin/env python3
"""Gold V0 tests: FR-460 PII, PCE-GW-461-01..03 (ATC, time, dose)."""
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
    local_counter_demographics,
    strip_pii_fr460,
    suppress_dose_fr461_03,
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
        self.assertNotIn("patient", blob)
        self.assertNotIn("doseQuantity", blob)
        self.assertNotIn('"value": 10', blob)

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


class PiiStripTests(unittest.TestCase):
    """PCE-GW-460-02 / 460-06. Gold V0 opaque IDs only — no invented legal names."""

    def test_gold_v0_01_direct_identifiers_removed(self) -> None:
        original = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        snapshot = json.dumps(original)
        cleaned = strip_pii_fr460(original)
        self.assertEqual(json.dumps(original), snapshot)
        patient = next(
            e["resource"]
            for e in cleaned["entry"]
            if e["resource"]["resourceType"] == "Patient"
        )
        self.assertNotIn("name", patient)
        self.assertNotIn("identifier", patient)
        self.assertNotIn("telecom", patient)
        self.assertNotIn("address", patient)
        self.assertNotIn("id", patient)
        self.assertEqual(patient["birthDate"], "1980")
        self.assertEqual(patient["gender"], "unknown")
        his_patient = original["entry"][0]["resource"]
        self.assertEqual(his_patient["name"][0]["text"], "SYN-NAME-001")
        self.assertEqual(his_patient["identifier"][0]["value"], "SYN-TAJ-001")

    def test_export_omits_patient_local_keeps_year(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        event = transform_bundle(bundle)
        self.assertNotIn("patient", event)
        local = local_counter_demographics(strip_pii_fr460(bundle))
        self.assertEqual(local, {"gender": "unknown", "birth_year": "1980"})
        with_local = transform_bundle(bundle, include_local=True)
        self.assertEqual(with_local["local_counter"]["birth_year"], "1980")
        self.assertNotIn("patient", with_local)


class DoseSuppressionTests(unittest.TestCase):
    """TC-GW-014 / PCE-GW-461-03."""

    def test_gold_v0_01_r4_dose_and_rate(self) -> None:
        original = load_json(str(GOLD / "gw-v0-01-normal-his-in.json"))
        cleaned = suppress_dose_fr461_03(original)
        med = next(
            e["resource"]
            for e in cleaned["entry"]
            if e["resource"]["resourceType"] == "MedicationRequest"
        )
        ins = med["dosageInstruction"][0]
        self.assertNotIn("doseQuantity", ins)
        self.assertNotIn("doseAndRate", ins)
        his_med = original["entry"][2]["resource"]
        self.assertEqual(
            his_med["dosageInstruction"][0]["doseAndRate"][0]["doseQuantity"]["value"],
            10,
        )

    def test_dstu2_style_dose_quantity_on_instruction(self) -> None:
        sample = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "MedicationRequest",
                        "dosageInstruction": [
                            {"sequence": 1, "doseQuantity": {"value": 10, "unit": "mg"}}
                        ],
                    }
                }
            ],
        }
        cleaned = suppress_dose_fr461_03(sample)
        ins = cleaned["entry"][0]["resource"]["dosageInstruction"][0]
        self.assertNotIn("doseQuantity", ins)
        self.assertEqual(ins.get("sequence"), 1)


class GoldV0IngestPiiDoseTests(unittest.TestCase):
    def test_v0_08_taj_rejected(self) -> None:
        bundle = load_json(str(GOLD / "gw-v0-08-taj-pce-ingest.json"))
        with self.assertRaises(ShadowReject) as ctx:
            ingest_guard(bundle)
        expected = load_json(str(GOLD / "gw-v0-08-taj-expected.json"))
        self.assertEqual(ctx.exception.code, expected["expected"]["error"])
        self.assertEqual(ctx.exception.http, expected["expected"]["http"])
        self.assertFalse(ctx.exception.hitl)

    def test_dose_on_ingest_rejected(self) -> None:
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "MedicationRequest",
                        "authoredOn": "2026-Q3",
                        "medicationCodeableConcept": {
                            "coding": [
                                {"system": "http://www.whocc.no/atc", "code": "N06AB"}
                            ]
                        },
                        "dosageInstruction": [
                            {
                                "doseAndRate": [
                                    {"doseQuantity": {"value": 10, "unit": "mg"}}
                                ]
                            }
                        ],
                    }
                }
            ],
        }
        with self.assertRaises(ShadowReject) as ctx:
            ingest_guard(bundle)
        self.assertEqual(ctx.exception.code, "E-SHADOW-001")
        self.assertIn("doseQuantity", ctx.exception.reason)


class CliTests(unittest.TestCase):
    def test_gateway_cli_gold_v0_01(self) -> None:
        proc = _cli("--input", str(GOLD / "gw-v0-01-normal-his-in.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["medications"][0]["code"], "N06AB")
        self.assertEqual(out["authoredOn"], "2026-Q3")
        self.assertNotIn("patient", out)
        self.assertNotIn("doseQuantity", json.dumps(out))
        self.assertNotIn("local_counter", out)

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

    def test_ingest_cli_taj(self) -> None:
        proc = _cli(
            "--mode",
            "ingest",
            "--input",
            str(GOLD / "gw-v0-08-taj-pce-ingest.json"),
        )
        self.assertEqual(proc.returncode, 2, proc.stdout)
        out = json.loads(proc.stdout)
        self.assertEqual(out["error"], "E-SHADOW-001")


if __name__ == "__main__":
    unittest.main()
