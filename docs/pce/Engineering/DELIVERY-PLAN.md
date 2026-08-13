# PCE delivery plan (production-like, `main` only)

| | |
| --- | --- |
| **Repo** | this `genetics` tree only |
| **Branch** | `main` |
| **Spec** | `docs/pce/PCE-SPEC-v1.2.md` frozen (§10.2) |
| **Data** | Gold V0 + official CPIC tables. No live HIS, no invented manufacturer/lab names, no dummy guideline text. |
| **Flag** | `LIVE_CDS = False` in `src/pce_gateway/flags.py`. CI asserts it. |

This plan is the work queue. A slice is done when Gold V0 (or the named official file) passes and the function is the same code that would run in an institution — not a stub that returns hardcoded JSON.

## Hard rules

- No `NotImplementedError` placeholders, no `TODO return {}`, no second “sim” package.
- F1+ renderer must not read `MedicationEntry` (FR-470 / R-021). CI grep.
- Shadow store ≠ report store (separate process, separate DB file).
- Unknown diplotype = below A14 threshold (allowlist, not denylist).
- k-cell counts stay in the institutional SQLite file; they never appear on the PCE payload.
- Do not vendor 4005-row CPIC sheets; regenerate keep-sets with `tests/fixtures/gold-v0/extract_cpic_frequency_slice.py`.

## WP-G — Gateway (F1s, fixture HIS) — **done on main**

| ID | Ticket | Code | Oracle |
| --- | --- | --- | --- |
| G0 | Package + CI | `src/pce_gateway/`, `.github/workflows/ci.yml` | `unittest discover` |
| G1 | FR-460 PII | `transform.strip_pii_fr460` | gw-v0-01, gw-v0-08 |
| G2 | 461-01 ATC | `truncate_atc` | gw-v0-01, gw-v0-03 |
| G3 | 461-02 time | `generalize_time` | gw-v0-01, gw-v0-09 |
| G4 | 461-03 dose | `suppress_dose_fr461_03` | gw-v0-01 |
| G5 | 461-06 freq | `frequency.FrequencyTable` | gw-v0-02, frequency-config.v0.json |
| G6 | 461-04/05 k-cell | `kcell.KCellStore` + `pipeline.process_his_event` | gw-v0-04, gw-v0-05 |
| G7 | 461-07 rarest | `FrequencyTable.is_rarest` | gw-v0-06 `*3x2/*3x2` |
| G8 | 461-08 k lock | `GatewayConfig.with_k` | gw-v0-07 |
| G9 | 461-09 ingest | `ingest.handle_pce_ingest` | gw-v0-03/08/09 + E-SHADOW-002 |
| G10 | 461-10 monitor | `KCellStore.quarterly_report` | shape of gw-v0-10 (no PII); live counts from SQLite |
| G11 | HTTP | `python -m pce_gateway --mode serve` | POST `/v1/shadow/events` |

Done when: every Gold V0 HIS/ingest case is covered by `tests/test_transform.py` and `tests/test_pipeline.py`, and CI is green on `main`. **Met 2026-08-13** (39 tests; HTTP POST `/v1/shadow/events` included).

## WP-R — F1+ report renderer (clinical path, matcher OFF) — **started on main**

Official inputs only:

1. Outside-call JSON (gene, diplotype, callability) — FR-240.
2. Versioned CPIC/DPWG/FDA **gene-level** tables downloaded from ClinPGx `current/` (same pattern as the frequency xlsx). Do not invent row text.
3. PREPARE-12 gene list from the frozen spec (FR-310), not a guessed panel.

Build `src/pce_report/`:

| ID | FR | Behaviour | Status |
| --- | --- | --- | --- |
| R1 | FR-210 | callability INDETERMINATE / missing-to-ref → no NORMAL claim | `tests/fixtures/f1plus-v0/outside-call-cyp2d6-indeterminate.json` |
| R2 | FR-400-STATIC | emit **all** guideline rows for the gene; zero filter on a medication list | CYP2D6: 79 `pair_view` + 1316 `recommendation_view` rows from CPIC API 2026-08-13 |
| R3 | FR-410-EDU | educational phenoconversion paragraph; no case-drug application | **omitted**: official `guideline.notesonusage` was empty; no invented EDU text |
| R4 | FR-490 | A.1 + A.1.1 statement on every PDF/JSON | copied from Appendix A |
| R5 | FR-500 | JSON + PDF (reportlab + DejaVu/Liberation/Noto TTF) | `python -m pce_report --pdf-out` |
| R6 | FR-470 | CI: `pce_report` does not import `pce_gateway.pipeline`; no `MedicationEntry` token | `.github/workflows/ci.yml` |
| R7 | FR-700 | no LLM client on this path | CI grep openai/anthropic/langchain |

Gold for R: checked-in outside-call fixture (opaque IDs) + official CPIC API slice. Not a mocked CPIC sentence.

## WP-H — HITL store (shadow only)

| ID | FR | Behaviour |
| --- | --- | --- |
| H1 | FR-440 | persist GatewayEvent in a **second** SQLite (or Postgres later) with no Patient |
| H2 | FR-450 | reviewer UI later; first: JSON list API with opaque `case_display_id` |
| H3 | FR-450-BLIND | two-step payload: motor category hidden until step 2 |
| H4 | FR-410-LIVE | phenoconversion engine runs **only** here, never in `pce_report` |

## WP-I — Isolation / QMS hooks

| ID | Item |
| --- | --- |
| I1 | FR-470 CI job as above |
| I2 | IEC 62304 SOUP list for PharmCAT / CPIC files (versions + hashes) |
| I3 | OQ-01 process notes stay in Outbound; no fake ISO certificate in git |

## Explicitly out of scope until seals / CE

Éles HIS, `LIVE_CDS=true`, matcher ON in F1+, real TAJ, invented G1/G2/C2, US F2 unlock (OQ-17), §13 clinical gold-set SOP, PRS (FR-430).

## Execution order

G0–G11 **done**. Next: remaining PREPARE-12 genes as additional official slices (same extract script pattern) → H1–H4 → I1–I3.

Do not start H by copying gateway events onto the F1+ report. Do not invent EDU/CPIC sentences.
