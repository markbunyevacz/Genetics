#!/usr/bin/env python3
"""OQ-05 test protocol from the unittest tree. Not a seal.

Walks tests/*.py via AST, maps a frozen claim table onto existing test ids,
optionally runs those tests, and writes a Hungarian evidence protocol.

This script does not mark OQ-05 closed. Classification remains counsel.
"""
from __future__ import annotations

import argparse
import ast
import io
import sys
import unittest
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src"
TESTS = ROOT / "tests"
DEFAULT_OUT = ROOT / "docs" / "pce" / "ProcessArtifacts" / "OQ-05-TEST-PROTOCOL.md"
DEFAULT_DATE = "2026-08-16"
OQ05_BRIEF = ROOT / "docs" / "pce" / "Outbound" / "OQ-05-counsel-brief.md"

for _p in (SRC, TESTS, ROOT):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

SEAL_FORBIDDEN = (
    "OQ-05 LEZÁRVA",
    "OQ-05 pecsételve",
    "OQ-05 pecsételt",
    "**SEALED**",
    "100% hermetikus",
)


class Claim(NamedTuple):
    claim_id: str
    title: str
    section: str
    software_scope: str
    note: str
    tests: tuple[str, ...]


# Frozen map: Q1–Q4 + A.1.2 / III invariants. Tests not listed are out of
# OQ-05 classification scope (F1s, F2, gateway, pins, sales records).
CLAIMS: tuple[Claim, ...] = (
    Claim(
        "Q1",
        "F1+ kimenet: teljes, szűretlen guideline-tábla gyógyszerlista nélkül",
        "OQ-05 Q1 (hatályos Rule 11 vs 11c) — szoftver-evidencia",
        "partial",
        "A teszt azt méri, hogy a renderer nem kap gyógyszerlistát, és a meghívott génhez a pinelt táblát dump-olja. Rule 11 vs 11c a counsel kérdése.",
        (
            "test_report.IsolationTests.test_render_signature_has_no_medication_entry",
            "test_report.IsolationTests.test_package_ast_has_no_medication_entry_or_gateway_pipeline",
            "test_report.RenderGoldTests.test_called_emits_all_pairs_and_recs",
            "test_report.RenderGoldTests.test_rejects_medication_payload",
            "test_report.Prepare12TableTests.test_cyp2c19_dumps_official_pairs",
            "test_report.B41ContractTests.test_full_allow_list_passes",
            "test_report.B41ContractTests.test_rejects_medications",
            "test_report.B41ContractTests.test_rejects_medication_entry_type",
            "test_report.B41ContractTests.test_rejects_medication_request",
            "test_report.B41ContractTests.test_rejects_medication_statement",
            "test_report.B41ContractTests.test_rejects_clinical_context",
            "test_report.B41ContractTests.test_rejects_hitl_review",
            "test_report.B41ContractTests.test_rejects_hitl_verdict",
            "test_report.B41ContractTests.test_rejects_unknown_top_level_and_nested_medications",
            "test_clinical.ConsentGateTests.test_create_report_does_not_load_medication_table",
            "test_fr_trace.Fr250NormalisationTests.test_e_map_001_is_catalogued_not_raised_by_f1plus_renderer",
            "test_prepare12_ready.HlaBUgt1a1LabIngestTests.test_f1plus_hla_b_dumps_abacavir_pair_from_lab_result",
            "test_prepare12_ready.HlaBUgt1a1LabIngestTests.test_f1plus_ugt1a1_dumps_atazanavir_pair_from_lab_result",
        ),
    ),
    Claim(
        "Q2",
        "Beteg-specifikus szelekció hiánya — IIa alatti besoroláshoz elég-e",
        "OQ-05 Q2 — szoftver nem minősít",
        "partial",
        "A kód a szelekció hiányát méri (teljes tábla, severity_means_replace_prescribed=false, nincs kitalált F5/VKORC1 pár). Az IIa-alatti osztály counsel.",
        (
            "test_report.RenderGoldTests.test_called_emits_all_pairs_and_recs",
            "test_report.RenderGoldTests.test_indeterminate_no_normal_claim",
            "test_fr_trace.Fr420HighlightTests.test_severity_means_replace_prescribed_is_false_in_assembler",
            "test_report.Prepare12TableTests.test_f5_signals_missing_recommendation_without_inventing",
            "test_prepare12_ready.RemainingLivePairTests.test_f5_and_vkorc1_have_no_invented_pairing",
        ),
    ),
    Claim(
        "Q3",
        "CI-invariánsok: LIVE_CDS false, nincs MedicationEntry / pipeline a reportban",
        "OQ-05 Q3 — MDCG modulhatár szoftver-evidencia",
        "yes",
        "A flag és az import-izoláció mért. A MDCG Rev.1 jogi megfelelés ettől még counsel.",
        (
            "test_report.IsolationTests.test_flags_frozen",
            "test_report.IsolationTests.test_package_ast_has_no_medication_entry_or_gateway_pipeline",
            "test_cds.FlagFreezeTests.test_repo_stays_locked",
            "test_prepare12_ready.FlagFreezeTests.test_repo_flags_stay_off",
            "test_pipeline.LiveCdsTests.test_compile_time_false",
            "test_cds.IsolationFromF1Tests.test_report_package_does_not_import_cds",
            "test_cds.IsolationFromF1Tests.test_clinical_package_does_not_import_cds",
            "test_fr_trace.Fr700LlmBanTests.test_clinical_and_report_have_no_llm_imports",
            "test_vcf_coverage.CoverageGoldTests.test_matcher_stays_off",
            "test_prepare12_ready.StarAlleleOnPathTests.test_clinical_add_vcf_default_still_off",
        ),
    ),
    Claim(
        "Q4",
        "COM(2025) 1023 javasolt Rule 11 — F1+ / L4-live; A.4.1",
        "OQ-05 Q4 — javaslat, nem hatályos jog, nem pecsételi Q1–Q3-at",
        "partial",
        "A pin és a brief Q4 sora mért. A javasolt osztály counsel. LIVE_CDS ettől nem billen.",
        (
            "test_fr_trace.Com1023F3ForkTests.test_spec_has_a18_and_com_proposal",
            "test_fr_trace.Com1023F3ForkTests.test_oq05_has_q4_not_seal",
            "test_fr_trace.Com1023F3ForkTests.test_registry_s077_is_com_s065_stays_clopidogrel",
            "test_official_pins.OfficialPinTests.test_com_2025_1023_pins_2026_08_16",
        ),
    ),
    Claim(
        "III.1",
        "Gyógyszerlista-vakság (FR-400-STATIC)",
        "OQ-05 III.1",
        "yes",
        "Renderer szignatúra, AST, B.4.1 deny-list. A klinikai úton MedicationEntry nincs.",
        (
            "test_report.IsolationTests.test_render_signature_has_no_medication_entry",
            "test_report.IsolationTests.test_package_ast_has_no_medication_entry_or_gateway_pipeline",
            "test_clinical.ConsentGateTests.test_create_report_does_not_load_medication_table",
            "test_report.B41ContractTests.test_rejects_medications",
        ),
    ),
    Claim(
        "III.2",
        "Nincs betegre szabott ha–akkor (A.1.2 / E-EDU-001 tokenek)",
        "OQ-05 III.2",
        "partial",
        "A tiltott tokenek a rendererben compile-time tuple. A teljes gén-tábla dump Q1 alatt. Nincs külön ≥5 ha–akkor fixture-készlet TC-EDU-001..010 néven.",
        (
            "test_report.RenderGoldTests.test_called_emits_all_pairs_and_recs",
            "test_fr_trace.Fr420HighlightTests.test_severity_means_replace_prescribed_is_false_in_assembler",
            "test_report.B41ContractTests.test_delivery_plan_r9_matches_schema",
        ),
    ),
    Claim(
        "III.3",
        "FR-410-EDU — oktató bekezdés, nem élő fenokonverzió a leleten",
        "OQ-05 III.3",
        "partial",
        "Gold F1+: edu_phenoconversion is None (CPIC notesonusage üres volt). A pheno-gold N=32 a shadow FR-410-LIVE út, nem F1+ evidencia.",
        (
            "test_report.RenderGoldTests.test_called_emits_all_pairs_and_recs",
            "test_report.StatementVerbatimTests.test_a11_in_appendix",
        ),
    ),
    Claim(
        "III.4",
        "Aláírói kapu + matcher ki (FR-490 / FR-300)",
        "OQ-05 III.4",
        "yes",
        "Outside-call default. MATCHER_ON=false. Consent/licence kapu a clinical service-en.",
        (
            "test_clinical.ConsentGateTests.test_missing_counselling_e_consent_001",
            "test_clinical.ConsentGateTests.test_missing_consent_e_consent_003",
            "test_clinical.ConsentGateTests.test_missing_license_e_consent_005",
            "test_clinical.ConsentGateTests.test_admin_cannot_skip_gate",
            "test_clinical.CliGateTests.test_outside_call_cli_rejected",
            "test_prepare12_ready.StarAlleleOnPathTests.test_matcher_off_does_not_call_diplotype",
            "test_vcf_coverage.CoverageGoldTests.test_matcher_stays_off",
        ),
    ),
    Claim(
        "III.5",
        "Csatorna-izoláció (FR-470)",
        "OQ-05 III.5",
        "yes",
        "pce_report és pce_clinical nem importál pce_cds / pce_shadow. LIVE_CDS compile-time false. F2 cső külön processzus, lakat alatt.",
        (
            "test_report.IsolationTests.test_package_ast_has_no_medication_entry_or_gateway_pipeline",
            "test_cds.IsolationFromF1Tests.test_report_package_does_not_import_cds",
            "test_cds.IsolationFromF1Tests.test_clinical_package_does_not_import_cds",
            "test_cds.LockPathTests.test_lock_returns_empty_cards",
            "test_shadow.IsolationFromReportTests.test_shadow_package_does_not_import_report_renderer",
        ),
    ),
    Claim(
        "III.6",
        "A.1.1 nyilatkozat a leleten — nem felelősségkizárás",
        "OQ-05 III.6",
        "yes",
        "A sablon a PDF/JSON-on. A disclaimer nem MDSW-kimenekülés (A.0) — ezt a teszt nem minősíti, csak a szöveg jelenlétét.",
        (
            "test_report.StatementVerbatimTests.test_a11_in_appendix",
            "test_report.RenderGoldTests.test_pdf_contains_disclaimer_and_pair",
        ),
    ),
    Claim(
        "OPS-F5",
        "F5 live hálózat: szándékos fail-open (OSError → [])",
        "Működési lakat — nem OQ-05 Q1–Q3",
        "yes",
        "LiveF5Provider.rows() OSError-t elnyel. Nem fail-fast. Prod default CPIC_F5_SOURCE=off. Mock nem megy az aláírt leletre.",
        (
            "test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_live_network_error_skips_without_exception",
            "test_f5_rec_pipeline.F5ProviderSwitchTests.test_default_source_is_off",
            "test_f5_rec_pipeline.F5ProviderSwitchTests.test_prod_table_has_no_f5_pairing",
        ),
    ),
    Claim(
        "OPS-PHARMCAT",
        "PharmCAT hálózati zárás: unittest, nem a teljes CI job",
        "Működési lakat — nem OQ-05 Q1–Q3",
        "yes",
        "CI a tesztek előtt HTTP-n tölti a pinelt JAR-t (--jar-only). A teszt PCE_PHARMCAT_OFFLINE=1 mellett fut. MATCHER_ON=false nem indít Javát.",
        (
            "test_f5_rec_pipeline.RepoConformHardeningTests.test_matcher_off_circuit_breaker_does_not_spawn_java",
            "test_f5_rec_pipeline.RepoConformHardeningTests.test_pharmcat_wrapper_is_argv_list_not_shell",
            "test_prepare12_ready.StarAlleleOnPathTests.test_matcher_off_does_not_call_diplotype",
        ),
    ),
)


# Historical 195→241 (D-49 hardening → D-54). Frozen. Later rounds append after this.
DELTA_195_241: tuple[tuple[str, str, str], ...] = (
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_add_outside_call_merges_hla_b"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_builder_script_cannot_emit_clopidogrel"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_cyp2d6_cnv_not_assumed_wild_type"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_classify_dose_and_no_recommendation"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_http_fetch_live_mocked"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_live_network_error_skips_without_exception"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_mock_fixture_immutable_and_het_hom"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_pheno_from_phenotypes_and_atc_on_row"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_pipeline_idempotent_no_duplicate_pairing"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_provider_is_interface_not_http"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_unknown_json_keys_do_not_crash"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_html_truncated_who_pin_exits_nonzero"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_matcher_off_circuit_breaker_does_not_spawn_java"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_pharmcat_wrapper_is_argv_list_not_shell"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_rec_pairings_forbid_dose_mg_token"),
    ("D-50", "F5/F1s/ops", "test_f5_rec_pipeline.RepoConformHardeningTests.test_who_html_pins_parse_with_stdlib_parser"),
    ("D-51", "F2 IIa-safe / FR-id", "test_cds.IiaSafeMechanismTests.test_blocks_audit_matrix"),
    ("D-51", "F2 IIa-safe / FR-id", "test_cds.IiaSafeMechanismTests.test_does_not_block_outside_the_five_mechanisms"),
    ("D-51", "F2 IIa-safe / FR-id", "test_cds.IiaSafeMechanismTests.test_families_are_named_mechanisms"),
    ("D-51", "F2 IIa-safe / FR-id", "test_cds.IiaSafeMechanismTests.test_hungarian_brand_does_not_need_english_inn"),
    ("D-51", "F2 IIa-safe / FR-id", "test_cds.IiaSafeMechanismTests.test_who_pins_cover_new_atc5"),
    ("D-51", "F2 IIa-safe / FR-id", "test_cds.OnPathTests.test_iia_safe_tramadol_no_suggestion"),
    ("D-51", "GSPR annotáció", "test_fr_trace.DeferredFrTests.test_fr_230_no_hl7_v2_parser"),
    ("D-51", "GSPR annotáció", "test_fr_trace.DeferredFrTests.test_fr_430_prs_interface_not_built"),
    ("D-51", "GSPR annotáció", "test_fr_trace.DeferredFrTests.test_fr_480_encyclopedia_view_not_built"),
    ("D-51", "GSPR annotáció", "test_fr_trace.DeferredFrTests.test_fr_510_report_regen_not_built"),
    ("D-51", "GSPR annotáció", "test_fr_trace.DeferredFrTests.test_fr_540_patient_copy_endpoint_not_built"),
    ("D-51", "GSPR annotáció", "test_fr_trace.DeferredFrTests.test_fr_600_alert_telemetry_not_built"),
    ("D-51", "OQ-05 III (FR-250/420/700)", "test_fr_trace.Fr250NormalisationTests.test_default_keeps_seven_character_substance_code"),
    ("D-51", "OQ-05 III (FR-250/420/700)", "test_fr_trace.Fr250NormalisationTests.test_e_map_001_is_catalogued_not_raised_by_f1plus_renderer"),
    ("D-51", "OQ-05 III (FR-250/420/700)", "test_fr_trace.Fr420HighlightTests.test_severity_means_replace_prescribed_is_false_in_assembler"),
    ("D-51", "OQ-05 III (FR-250/420/700)", "test_fr_trace.Fr700LlmBanTests.test_clinical_and_report_have_no_llm_imports"),
    ("D-51", "GSPR annotáció", "test_fr_trace.FrIdInventoryTests.test_every_spec_fr_appears_in_tests"),
    ("D-52", "stratégia-rekord, nem minősítés", "test_fr_trace.FallenGtmRecordTests.test_sku_and_buyers_records_fallen_longevity"),
    ("D-52", "stratégia-rekord, nem minősítés", "test_fr_trace.FallenGtmRecordTests.test_spec_has_a16_a17_rows"),
    ("D-52", "stratégia-rekord, nem minősítés", "test_fr_trace.FallenGtmRecordTests.test_src_has_no_zero_knowledge_or_local_first"),
    ("D-53", "OQ-06 IIa-safe", "test_cds.IiaSafeMechanismTests.test_ba_reaudit_block_pass_and_hungarian_names"),
    ("D-53", "OQ-06 IIa-safe", "test_cds.IiaSafeMechanismTests.test_l01bc_prefix_would_false_positive_on_pinned_who"),
    ("D-53", "OQ-05 III.4 matcher-kapu", "test_fr_trace.MatcherOnHgvsGateTests.test_spec_and_trace_bind_hgvs_to_matcher_on"),
    ("D-53", "OQ-05 III.4 matcher-kapu", "test_fr_trace.MatcherOnHgvsGateTests.test_src_has_no_hgvs_or_vrs_implementation"),
    ("D-53", "pin / MANIFEST", "test_official_pins.OfficialPinTests.test_l01bc_counterexample_pins_2026_08_16"),
    ("D-53", "pin / MANIFEST", "test_official_pins.OfficialPinTests.test_manifest_accessed_is_pin_day_not_unified"),
    ("D-54", "OQ-05 Q4", "test_fr_trace.Com1023F3ForkTests.test_oq05_has_q4_not_seal"),
    ("D-54", "OQ-05 Q4", "test_fr_trace.Com1023F3ForkTests.test_registry_s077_is_com_s065_stays_clopidogrel"),
    ("D-54", "OQ-05 Q4", "test_fr_trace.Com1023F3ForkTests.test_spec_has_a18_and_com_proposal"),
    ("D-54", "OQ-05 Q4", "test_official_pins.OfficialPinTests.test_com_2025_1023_pins_2026_08_16"),
)


def discover_tests() -> dict[str, str]:
    """Return dotted test id → source path for every test_* in tests/."""
    out: dict[str, str] = {}
    for path in sorted(TESTS.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        rel = path.relative_to(TESTS).as_posix()
        mod = rel[:-3].replace("/", ".")
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                    out[f"{mod}.{node.name}.{item.name}"] = f"tests/{rel}"
    return out


def suite_count() -> int:
    loader = unittest.TestLoader()
    suite = loader.discover(str(TESTS), pattern="test_*.py", top_level_dir=str(TESTS))
    return suite.countTestCases()


def mapped_ids() -> tuple[str, ...]:
    seen: list[str] = []
    for claim in CLAIMS:
        for tid in claim.tests:
            if tid not in seen:
                seen.append(tid)
    return tuple(seen)


def run_ids(ids: tuple[str, ...]) -> dict[str, str]:
    loader = unittest.TestLoader()
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=0)
    results: dict[str, str] = {}
    for tid in ids:
        try:
            suite = loader.loadTestsFromName(tid)
        except (ImportError, AttributeError, ValueError):
            results[tid] = "LOAD_ERROR"
            continue
        if suite.countTestCases() == 0:
            results[tid] = "MISSING"
            continue
        outcome = runner.run(suite)
        if outcome.failures or outcome.errors:
            results[tid] = "FAIL"
        elif outcome.testsRun == 0:
            results[tid] = "NOT_RUN"
        else:
            results[tid] = "OK"
    return results


def flags() -> dict[str, object]:
    from pce_cds.policy import IIA_SAFE_BLOCK
    from pce_gateway.flags import LIVE_CDS as GW_LIVE
    from pce_report.flags import LIVE_CDS, MATCHER_ON
    from pce_report.schema import ALLOWED_B41_TOP_LEVEL, FORBIDDEN_B41_FIELDS

    return {
        "LIVE_CDS": LIVE_CDS,
        "GATEWAY_LIVE_CDS": GW_LIVE,
        "MATCHER_ON": MATCHER_ON,
        "IIA_SAFE_BLOCK": IIA_SAFE_BLOCK,
        "ALLOWED_B41": len(ALLOWED_B41_TOP_LEVEL),
        "FORBIDDEN_B41": len(FORBIDDEN_B41_FIELDS),
    }


def brief_allowed_cite() -> int | None:
    text = OQ05_BRIEF.read_text(encoding="utf-8")
    marker = "ALLOWED_B41_TOP_LEVEL` = "
    idx = text.find(marker)
    if idx < 0:
        return None
    rest = text[idx + len(marker) :]
    digits = []
    for ch in rest:
        if ch.isdigit():
            digits.append(ch)
        else:
            break
    if not digits:
        return None
    return int("".join(digits))


def _status_cell(software_scope: str, results: dict[str, str], tests: tuple[str, ...]) -> str:
    vals = [results.get(t, "NOT_RUN") for t in tests]
    if any(v in {"FAIL", "LOAD_ERROR", "MISSING"} for v in vals):
        run = "FAIL"
    elif all(v == "OK" for v in vals):
        run = "OK"
    elif all(v == "INVENTORIED" for v in vals):
        run = "INVENTORIED"
    else:
        run = ",".join(sorted(set(vals)))
    return f"{run} / szoftver:{software_scope}"


def render(date: str, *, run_mapped: bool) -> str:
    inventory = discover_tests()
    total = suite_count()
    fl = flags()
    brief_n = brief_allowed_cite()
    ids = mapped_ids()
    if run_mapped:
        results = run_ids(ids)
    else:
        results = {tid: "INVENTORIED" for tid in ids}

    missing = [tid for tid in ids if tid not in inventory]
    if missing:
        raise SystemExit("mapped test missing from AST: " + ", ".join(missing))

    mapped_set = set(ids)
    lines: list[str] = []
    a = lines.append
    a("# OQ-05 teszt-jegyzőkönyv — szoftver-evidencia, nem pecsét")
    a("")
    a("| | |")
    a("| --- | --- |")
    a("| **Iktató** | PCE-OQ-05-PROTOCOL / gépileg a unittest fából |")
    a(f"| **Dátum** | {date} |")
    a("| **Státusz** | **ELŐTERJESZTVE — nem pecsét.** Nem counsel-állásfoglalás. Nem CE. Nem klinikai késztermék. |")
    a("| **Forrás** | `tests/test_*.py` AST + zárt evidenciatábla ebben a szkriptben |")
    a("| **OQ-05 brief** | `docs/pce/Outbound/OQ-05-counsel-brief.md` (V. pecsét üresen marad) |")
    a("")
    a("Ez a jegyzőkönyv azt dokumentálja, hogy a D-49 hardening pontjai és a ráépült körök **milyen unittesttel** vannak a fában. A checklist zöldje azt jelenti, hogy ezek a pontok gépileg verifikáltak a kódban. **Nem** jelenti, hogy az OQ-05 be van pecsételve.")
    a("")
    a("## 0. Repo-lakatok (mért konstans, nem szándék)")
    a("")
    a("| Lakat | Érték a kódban |")
    a("| --- | --- |")
    a(f"| `LIVE_CDS` (`pce_report` / `pce_gateway`) | `{str(fl['LIVE_CDS']).lower()}` / `{str(fl['GATEWAY_LIVE_CDS']).lower()}` |")
    a(f"| `MATCHER_ON` | `{str(fl['MATCHER_ON']).lower()}` |")
    a(f"| `IIA_SAFE_BLOCK` | `{str(fl['IIA_SAFE_BLOCK']).lower()}` |")
    a(f"| `ALLOWED_B41_TOP_LEVEL` | **{fl['ALLOWED_B41']}** (`src/pce_report/schema.py`) |")
    a(f"| `FORBIDDEN_B41_FIELDS` | **{fl['FORBIDDEN_B41']}** |")
    a(f"| Unittest készlet (loader) | **{total}** teszt |")
    a(f"| AST `test_*` metódus | **{len(inventory)}** |")
    a(f"| Q1–Q4/III/OPS mapped egyedi teszt | **{len(mapped_set)}** (nem a teljes {total}) |")
    a("")
    if fl["LIVE_CDS"] or fl["GATEWAY_LIVE_CDS"] or fl["MATCHER_ON"] or not fl["IIA_SAFE_BLOCK"]:
        raise SystemExit("repo locks drifted; refusing to emit a protocol that would hide it")
    if brief_n is not None and brief_n != fl["ALLOWED_B41"]:
        a(
            f"**E-31:** az OQ-05 brief Q1 melléklete `ALLOWED_B41_TOP_LEVEL` = {brief_n}-öt ír; "
            f"a `schema.py` {fl['ALLOWED_B41']}. A jegyzőkönyv a kódot veszi. A briefet külön kell igazítani."
        )
        a("")
    else:
        a("Az OQ-05 brief Q1 allow-list száma megegyezik a `schema.py` élő méretével.")
        a("")
    a("## 1. Q1–Q4 és III. invariánsok")
    a("")
    a("| ID | Tétel | Szoftver hatóköre | Mapped tesztek | Futás |")
    a("| --- | --- | --- | --- | --- |")
    for claim in CLAIMS:
        a(
            f"| **{claim.claim_id}** | {claim.title} | `{claim.software_scope}` | {len(claim.tests)} | "
            f"{_status_cell(claim.software_scope, results, claim.tests)} |"
        )
    a("")
    for claim in CLAIMS:
        a(f"### {claim.claim_id} — {claim.title}")
        a("")
        a(f"- Szakasz: {claim.section}")
        a(f"- Szoftver hatóköre: `{claim.software_scope}`")
        a(f"- Megjegyzés: {claim.note}")
        a("")
        a("| Teszt | Eredmény |")
        a("| --- | --- |")
        for tid in claim.tests:
            a(f"| `{tid}` | {results.get(tid, 'NOT_RUN')} |")
        a("")
    a("## 2. 195 → 241 delta (D-49 → D-54), történeti")
    a("")
    a("D-49 (`42ff2b0`, 195 teszt) a hardening alapszint. A következő 46 teszt **nem** vette vissza a D-49 pontokat. A 46-ból a többség **nem** F1+ minősítési evidencia:")
    a("")
    a("| Kör | Darab | Fókusz | OQ-05 viszony |")
    a("| --- | --- | --- | --- |")
    a("| D-50 (195→211) | 16 | F5 Protocol, live `OSError` fail-open, warfarin `MISSING_GENETIC_DATA`, stdlib HTML, PharmCAT circuit breaker | ops / F1s. Fail-open **nem** fail-fast. |")
    a("| D-51 (211→228) | 17 | IIa-safe mechanizmus (F2) + FR-id annotáció; FR-250/420/700 | IIa-safe = OQ-06. FR-250/420/700 = III. |")
    a("| D-52 (228→231) | 3 | A16/A17 elesett GTM, ZK/local-first tilalom | stratégia-rekord, nem Rule 11 |")
    a("| D-53 (231→237) | 6 | L01BC* ellenpélda; HGVS `MATCHER_ON` kapu; MANIFEST pin-nap | L01BC = OQ-06. HGVS-kapu = III.4. |")
    a("| D-54 (237→241) | 4 | COM(2025) 1023 pin + Q4 a briefben, pecsét nélkül | Q4 evidencia, nem Q1–Q3 pecsét |")
    a("")
    a(f"Összesen **{len(DELTA_195_241)}** új teszt a 195→241 ablakban.")
    a("")
    a("| Kör | Osztály | Teszt |")
    a("| --- | --- | --- |")
    for round_id, klass, tid in DELTA_195_241:
        a(f"| {round_id} | {klass} | `{tid}` |")
    a("")
    a("## 3. Teljes unittest-inventárium")
    a("")
    a("Minden `test_*` a fában. A `mapped` oszlop akkor `igen`, ha a teszt szerepel a fenti evidenciatáblában.")
    a("")
    a("| Modul | Teszt | Mapped |")
    a("| --- | --- | --- |")
    for tid in sorted(inventory):
        flag = "igen" if tid in mapped_set else "nem"
        a(f"| `{inventory[tid]}` | `{tid.split('.')[-1]}` | {flag} |")
    a("")
    a("## 4. Ami ez a jegyzőkönyv nem")
    a("")
    a("- Nem tölti ki az OQ-05 V. szakasz IGEN / NEM / FELTÉTELLEL pecsétjét.")
    a("- Nem állítja, hogy a szoftver CE-jelölt orvostechnikai eszköz.")
    a("- Nem állítja, hogy a CI job hermetikusan hálózat nélkül fut. A JAR-pin HTTP a tesztek *előtt* fut; az air-gap a `PCE_PHARMCAT_OFFLINE=1` tesztfázis.")
    a("- Nem állítja, hogy az F5 live út fail-fast. Hálózati `OSError` → üres lista (fail-open).")
    a("- Nem pecsételi az OQ-06-ot (IIa-safe párok) és nem billenti a `LIVE_CDS` / `MATCHER_ON` / `IIA_SAFE_BLOCK` lakatot.")
    a(f"- A {total}-es suite méret **nem** IGEN pecsét. Az F5 fail-open és a CI JAR HTTP **nem** NEM pecsét.")
    a("")
    a("## 5. Maradék ops-kockázat — nem Q1–Q3 döntő, nem pecsét-feloldó")
    a("")
    a("Két szándékos viselkedés. A gyártói záradék-tervezet: `docs/pce/Outbound/OQ-05-feltetellel-tervezet.md`. D-56: fail-fast-re váltás **nem** OQ-05 előfeltétel.")
    a("")
    a("| ID | Tény | Hol | OQ-05 viszony |")
    a("| --- | --- | --- | --- |")
    a("| **R-OPS-01** | F5 live `OSError` → `[]` (fail-open). Prod `CPIC_F5_SOURCE=off`. Mock nem megy az aláírt leletre. | `LiveF5Provider.rows()`; OPS-F5 tesztek | Shadow/F1s ops. Nem Rule 11 vs 11c. |")
    a("| **R-OPS-02** | CI a tesztek előtt HTTP-n tölti a pinelt JAR-t. Tesztfázis: `PCE_PHARMCAT_OFFLINE=1`. | `.github/workflows/ci.yml`; OPS-PHARMCAT tesztek | Matcher default ki. Nem a teljes job air-gap. |")
    a("")
    a("**E-31** a brief/G allow-list 45→47 (`schema.py`). Nem outside-call, nem HGVS.")
    a("")
    q3 = next(c for c in CLAIMS if c.claim_id == "Q3")
    a(
        f"**D-57:** a counsel-küldés kapuja a brief melléklet-útvonalai, nem a REG-030 teljes Class I QMS. "
        f"D.1 kezdeti 14971, nem teljes dosszié. REG-010 = A melléklet. "
        f"A Q1–Q4/III/OPS mapped egyedi teszt **{len(mapped_set)}**, a Q3 **{len(q3.tests)}**; "
        "a suite méret **nem** IGEN. Send-pack citáció: `tests/test_oq05_protocol.py` "
        "`Oq05CounselSendPackTests` (**nem** mapped Q1–Q3 evidencia)."
    )
    a("")
    a(
        "**D-58:** átadás-átvételi SHA-256 boríték: `docs/pce/Outbound/OQ-05-SEND-PACK.md`. "
        "Nem pecsét. A boríték a saját hashét nem tartalmazza. REG-030 nincs a hash-táblában."
    )
    a("")
    a("*Generálta: `docs/pce/ProcessArtifacts/BuildScripts/generate_oq05_protocol.py`. Újragenerálás: `PYTHONPATH=src python3 …/generate_oq05_protocol.py --write`.*")
    a("")
    text = "\n".join(lines)
    for tok in SEAL_FORBIDDEN:
        if tok in text:
            raise SystemExit(f"protocol would contain forbidden seal token: {tok!r}")
    return text


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--date", default=DEFAULT_DATE)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--write", action="store_true", help="overwrite the committed protocol")
    p.add_argument(
        "--inventory-only",
        action="store_true",
        help="do not run mapped tests (status=INVENTORIED)",
    )
    args = p.parse_args(argv)
    text = render(args.date, run_mapped=not args.inventory_only)
    if args.write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        sys.stdout.write(f"wrote {args.out}\n")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
