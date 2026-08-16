# OQ-05 teszt-jegyzőkönyv — szoftver-evidencia, nem pecsét

| | |
| --- | --- |
| **Iktató** | PCE-OQ-05-PROTOCOL / gépileg a unittest fából |
| **Dátum** | 2026-08-16 |
| **Státusz** | **ELŐTERJESZTVE — nem pecsét.** Nem counsel-állásfoglalás. Nem CE. Nem klinikai késztermék. |
| **Forrás** | `tests/test_*.py` AST + zárt evidenciatábla ebben a szkriptben |
| **OQ-05 brief** | `docs/pce/Outbound/OQ-05-counsel-brief.md` (V. pecsét üresen marad) |

Ez a jegyzőkönyv azt dokumentálja, hogy a D-49 hardening pontjai és a ráépült körök **milyen unittesttel** vannak a fában. A checklist zöldje azt jelenti, hogy ezek a pontok gépileg verifikáltak a kódban. **Nem** jelenti, hogy az OQ-05 be van pecsételve.

## 0. Repo-lakatok (mért konstans, nem szándék)

| Lakat | Érték a kódban |
| --- | --- |
| `LIVE_CDS` (`pce_report` / `pce_gateway`) | `false` / `false` |
| `MATCHER_ON` | `false` |
| `IIA_SAFE_BLOCK` | `true` |
| `ALLOWED_B41_TOP_LEVEL` | **47** (`src/pce_report/schema.py`) |
| `FORBIDDEN_B41_FIELDS` | **15** |
| Unittest készlet (loader) | **261** teszt |
| AST `test_*` metódus | **261** |
| Q1–Q4/III/OPS mapped egyedi teszt | **51** (nem a teljes 261) |

Az OQ-05 brief Q1 allow-list száma megegyezik a `schema.py` élő méretével.

## 1. Q1–Q4 és III. invariánsok

| ID | Tétel | Szoftver hatóköre | Mapped tesztek | Futás |
| --- | --- | --- | --- | --- |
| **Q1** | F1+ kimenet: teljes, szűretlen guideline-tábla gyógyszerlista nélkül | `partial` | 18 | OK / szoftver:partial |
| **Q2** | Beteg-specifikus szelekció hiánya — IIa alatti besoroláshoz elég-e | `partial` | 5 | OK / szoftver:partial |
| **Q3** | CI-invariánsok: LIVE_CDS false, nincs MedicationEntry / pipeline a reportban | `yes` | 10 | OK / szoftver:yes |
| **Q4** | COM(2025) 1023 javasolt Rule 11 — F1+ / L4-live; A.4.1 | `partial` | 4 | OK / szoftver:partial |
| **III.1** | Gyógyszerlista-vakság (FR-400-STATIC) | `yes` | 4 | OK / szoftver:yes |
| **III.2** | Nincs betegre szabott ha–akkor (A.1.2 / E-EDU-001 tokenek) | `partial` | 3 | OK / szoftver:partial |
| **III.3** | FR-410-EDU — oktató bekezdés, nem élő fenokonverzió a leleten | `partial` | 2 | OK / szoftver:partial |
| **III.4** | Aláírói kapu + matcher ki (FR-490 / FR-300) | `yes` | 7 | OK / szoftver:yes |
| **III.5** | Csatorna-izoláció (FR-470) | `yes` | 5 | OK / szoftver:yes |
| **III.6** | A.1.1 nyilatkozat a leleten — nem felelősségkizárás | `yes` | 2 | OK / szoftver:yes |
| **OPS-F5** | F5 live hálózat: szándékos fail-open (OSError → []) | `yes` | 3 | OK / szoftver:yes |
| **OPS-PHARMCAT** | PharmCAT hálózati zárás: unittest, nem a teljes CI job | `yes` | 3 | OK / szoftver:yes |

### Q1 — F1+ kimenet: teljes, szűretlen guideline-tábla gyógyszerlista nélkül

- Szakasz: OQ-05 Q1 (hatályos Rule 11 vs 11c) — szoftver-evidencia
- Szoftver hatóköre: `partial`
- Megjegyzés: A teszt azt méri, hogy a renderer nem kap gyógyszerlistát, és a meghívott génhez a pinelt táblát dump-olja. Rule 11 vs 11c a counsel kérdése.

| Teszt | Eredmény |
| --- | --- |
| `test_report.IsolationTests.test_render_signature_has_no_medication_entry` | OK |
| `test_report.IsolationTests.test_package_ast_has_no_medication_entry_or_gateway_pipeline` | OK |
| `test_report.RenderGoldTests.test_called_emits_all_pairs_and_recs` | OK |
| `test_report.RenderGoldTests.test_rejects_medication_payload` | OK |
| `test_report.Prepare12TableTests.test_cyp2c19_dumps_official_pairs` | OK |
| `test_report.B41ContractTests.test_full_allow_list_passes` | OK |
| `test_report.B41ContractTests.test_rejects_medications` | OK |
| `test_report.B41ContractTests.test_rejects_medication_entry_type` | OK |
| `test_report.B41ContractTests.test_rejects_medication_request` | OK |
| `test_report.B41ContractTests.test_rejects_medication_statement` | OK |
| `test_report.B41ContractTests.test_rejects_clinical_context` | OK |
| `test_report.B41ContractTests.test_rejects_hitl_review` | OK |
| `test_report.B41ContractTests.test_rejects_hitl_verdict` | OK |
| `test_report.B41ContractTests.test_rejects_unknown_top_level_and_nested_medications` | OK |
| `test_clinical.ConsentGateTests.test_create_report_does_not_load_medication_table` | OK |
| `test_fr_trace.Fr250NormalisationTests.test_e_map_001_is_catalogued_not_raised_by_f1plus_renderer` | OK |
| `test_prepare12_ready.HlaBUgt1a1LabIngestTests.test_f1plus_hla_b_dumps_abacavir_pair_from_lab_result` | OK |
| `test_prepare12_ready.HlaBUgt1a1LabIngestTests.test_f1plus_ugt1a1_dumps_atazanavir_pair_from_lab_result` | OK |

### Q2 — Beteg-specifikus szelekció hiánya — IIa alatti besoroláshoz elég-e

- Szakasz: OQ-05 Q2 — szoftver nem minősít
- Szoftver hatóköre: `partial`
- Megjegyzés: A kód a szelekció hiányát méri (teljes tábla, severity_means_replace_prescribed=false, nincs kitalált F5/VKORC1 pár). Az IIa-alatti osztály counsel.

| Teszt | Eredmény |
| --- | --- |
| `test_report.RenderGoldTests.test_called_emits_all_pairs_and_recs` | OK |
| `test_report.RenderGoldTests.test_indeterminate_no_normal_claim` | OK |
| `test_fr_trace.Fr420HighlightTests.test_severity_means_replace_prescribed_is_false_in_assembler` | OK |
| `test_report.Prepare12TableTests.test_f5_signals_missing_recommendation_without_inventing` | OK |
| `test_prepare12_ready.RemainingLivePairTests.test_f5_and_vkorc1_have_no_invented_pairing` | OK |

### Q3 — CI-invariánsok: LIVE_CDS false, nincs MedicationEntry / pipeline a reportban

- Szakasz: OQ-05 Q3 — MDCG modulhatár szoftver-evidencia
- Szoftver hatóköre: `yes`
- Megjegyzés: A flag és az import-izoláció mért. A MDCG Rev.1 jogi megfelelés ettől még counsel.

| Teszt | Eredmény |
| --- | --- |
| `test_report.IsolationTests.test_flags_frozen` | OK |
| `test_report.IsolationTests.test_package_ast_has_no_medication_entry_or_gateway_pipeline` | OK |
| `test_cds.FlagFreezeTests.test_repo_stays_locked` | OK |
| `test_prepare12_ready.FlagFreezeTests.test_repo_flags_stay_off` | OK |
| `test_pipeline.LiveCdsTests.test_compile_time_false` | OK |
| `test_cds.IsolationFromF1Tests.test_report_package_does_not_import_cds` | OK |
| `test_cds.IsolationFromF1Tests.test_clinical_package_does_not_import_cds` | OK |
| `test_fr_trace.Fr700LlmBanTests.test_clinical_and_report_have_no_llm_imports` | OK |
| `test_vcf_coverage.CoverageGoldTests.test_matcher_stays_off` | OK |
| `test_prepare12_ready.StarAlleleOnPathTests.test_clinical_add_vcf_default_still_off` | OK |

### Q4 — COM(2025) 1023 javasolt Rule 11 — F1+ / L4-live; A.4.1

- Szakasz: OQ-05 Q4 — javaslat, nem hatályos jog, nem pecsételi Q1–Q3-at
- Szoftver hatóköre: `partial`
- Megjegyzés: A pin és a brief Q4 sora mért. A javasolt osztály counsel. LIVE_CDS ettől nem billen.

| Teszt | Eredmény |
| --- | --- |
| `test_fr_trace.Com1023F3ForkTests.test_spec_has_a18_and_com_proposal` | OK |
| `test_fr_trace.Com1023F3ForkTests.test_oq05_has_q4_not_seal` | OK |
| `test_fr_trace.Com1023F3ForkTests.test_registry_s077_is_com_s065_stays_clopidogrel` | OK |
| `test_official_pins.OfficialPinTests.test_com_2025_1023_pins_2026_08_16` | OK |

### III.1 — Gyógyszerlista-vakság (FR-400-STATIC)

- Szakasz: OQ-05 III.1
- Szoftver hatóköre: `yes`
- Megjegyzés: Renderer szignatúra, AST, B.4.1 deny-list. A klinikai úton MedicationEntry nincs.

| Teszt | Eredmény |
| --- | --- |
| `test_report.IsolationTests.test_render_signature_has_no_medication_entry` | OK |
| `test_report.IsolationTests.test_package_ast_has_no_medication_entry_or_gateway_pipeline` | OK |
| `test_clinical.ConsentGateTests.test_create_report_does_not_load_medication_table` | OK |
| `test_report.B41ContractTests.test_rejects_medications` | OK |

### III.2 — Nincs betegre szabott ha–akkor (A.1.2 / E-EDU-001 tokenek)

- Szakasz: OQ-05 III.2
- Szoftver hatóköre: `partial`
- Megjegyzés: A tiltott tokenek a rendererben compile-time tuple. A teljes gén-tábla dump Q1 alatt. Nincs külön ≥5 ha–akkor fixture-készlet TC-EDU-001..010 néven.

| Teszt | Eredmény |
| --- | --- |
| `test_report.RenderGoldTests.test_called_emits_all_pairs_and_recs` | OK |
| `test_fr_trace.Fr420HighlightTests.test_severity_means_replace_prescribed_is_false_in_assembler` | OK |
| `test_report.B41ContractTests.test_delivery_plan_r9_matches_schema` | OK |

### III.3 — FR-410-EDU — oktató bekezdés, nem élő fenokonverzió a leleten

- Szakasz: OQ-05 III.3
- Szoftver hatóköre: `partial`
- Megjegyzés: Gold F1+: edu_phenoconversion is None (CPIC notesonusage üres volt). A pheno-gold N=32 a shadow FR-410-LIVE út, nem F1+ evidencia.

| Teszt | Eredmény |
| --- | --- |
| `test_report.RenderGoldTests.test_called_emits_all_pairs_and_recs` | OK |
| `test_report.StatementVerbatimTests.test_a11_in_appendix` | OK |

### III.4 — Aláírói kapu + matcher ki (FR-490 / FR-300)

- Szakasz: OQ-05 III.4
- Szoftver hatóköre: `yes`
- Megjegyzés: Outside-call default. MATCHER_ON=false. Consent/licence kapu a clinical service-en.

| Teszt | Eredmény |
| --- | --- |
| `test_clinical.ConsentGateTests.test_missing_counselling_e_consent_001` | OK |
| `test_clinical.ConsentGateTests.test_missing_consent_e_consent_003` | OK |
| `test_clinical.ConsentGateTests.test_missing_license_e_consent_005` | OK |
| `test_clinical.ConsentGateTests.test_admin_cannot_skip_gate` | OK |
| `test_clinical.CliGateTests.test_outside_call_cli_rejected` | OK |
| `test_prepare12_ready.StarAlleleOnPathTests.test_matcher_off_does_not_call_diplotype` | OK |
| `test_vcf_coverage.CoverageGoldTests.test_matcher_stays_off` | OK |

### III.5 — Csatorna-izoláció (FR-470)

- Szakasz: OQ-05 III.5
- Szoftver hatóköre: `yes`
- Megjegyzés: pce_report és pce_clinical nem importál pce_cds / pce_shadow. LIVE_CDS compile-time false. F2 cső külön processzus, lakat alatt.

| Teszt | Eredmény |
| --- | --- |
| `test_report.IsolationTests.test_package_ast_has_no_medication_entry_or_gateway_pipeline` | OK |
| `test_cds.IsolationFromF1Tests.test_report_package_does_not_import_cds` | OK |
| `test_cds.IsolationFromF1Tests.test_clinical_package_does_not_import_cds` | OK |
| `test_cds.LockPathTests.test_lock_returns_empty_cards` | OK |
| `test_shadow.IsolationFromReportTests.test_shadow_package_does_not_import_report_renderer` | OK |

### III.6 — A.1.1 nyilatkozat a leleten — nem felelősségkizárás

- Szakasz: OQ-05 III.6
- Szoftver hatóköre: `yes`
- Megjegyzés: A sablon a PDF/JSON-on. A disclaimer nem MDSW-kimenekülés (A.0) — ezt a teszt nem minősíti, csak a szöveg jelenlétét.

| Teszt | Eredmény |
| --- | --- |
| `test_report.StatementVerbatimTests.test_a11_in_appendix` | OK |
| `test_report.RenderGoldTests.test_pdf_contains_disclaimer_and_pair` | OK |

### OPS-F5 — F5 live hálózat: szándékos fail-open (OSError → [])

- Szakasz: Működési lakat — nem OQ-05 Q1–Q3
- Szoftver hatóköre: `yes`
- Megjegyzés: LiveF5Provider.rows() OSError-t elnyel. Nem fail-fast. Prod default CPIC_F5_SOURCE=off. Mock nem megy az aláírt leletre.

| Teszt | Eredmény |
| --- | --- |
| `test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_live_network_error_skips_without_exception` | OK |
| `test_f5_rec_pipeline.F5ProviderSwitchTests.test_default_source_is_off` | OK |
| `test_f5_rec_pipeline.F5ProviderSwitchTests.test_prod_table_has_no_f5_pairing` | OK |

### OPS-PHARMCAT — PharmCAT hálózati zárás: unittest, nem a teljes CI job

- Szakasz: Működési lakat — nem OQ-05 Q1–Q3
- Szoftver hatóköre: `yes`
- Megjegyzés: CI a tesztek előtt HTTP-n tölti a pinelt JAR-t (--jar-only). A teszt PCE_PHARMCAT_OFFLINE=1 mellett fut. MATCHER_ON=false nem indít Javát.

| Teszt | Eredmény |
| --- | --- |
| `test_f5_rec_pipeline.RepoConformHardeningTests.test_matcher_off_circuit_breaker_does_not_spawn_java` | OK |
| `test_f5_rec_pipeline.RepoConformHardeningTests.test_pharmcat_wrapper_is_argv_list_not_shell` | OK |
| `test_prepare12_ready.StarAlleleOnPathTests.test_matcher_off_does_not_call_diplotype` | OK |

## 2. 195 → 241 delta (D-49 → D-54), történeti

D-49 (`42ff2b0`, 195 teszt) a hardening alapszint. A következő 46 teszt **nem** vette vissza a D-49 pontokat. A 46-ból a többség **nem** F1+ minősítési evidencia:

| Kör | Darab | Fókusz | OQ-05 viszony |
| --- | --- | --- | --- |
| D-50 (195→211) | 16 | F5 Protocol, live `OSError` fail-open, warfarin `MISSING_GENETIC_DATA`, stdlib HTML, PharmCAT circuit breaker | ops / F1s. Fail-open **nem** fail-fast. |
| D-51 (211→228) | 17 | IIa-safe mechanizmus (F2) + FR-id annotáció; FR-250/420/700 | IIa-safe = OQ-06. FR-250/420/700 = III. |
| D-52 (228→231) | 3 | A16/A17 elesett GTM, ZK/local-first tilalom | stratégia-rekord, nem Rule 11 |
| D-53 (231→237) | 6 | L01BC* ellenpélda; HGVS `MATCHER_ON` kapu; MANIFEST pin-nap | L01BC = OQ-06. HGVS-kapu = III.4. |
| D-54 (237→241) | 4 | COM(2025) 1023 pin + Q4 a briefben, pecsét nélkül | Q4 evidencia, nem Q1–Q3 pecsét |

Összesen **46** új teszt a 195→241 ablakban.

| Kör | Osztály | Teszt |
| --- | --- | --- |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_add_outside_call_merges_hla_b` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_builder_script_cannot_emit_clopidogrel` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_cyp2d6_cnv_not_assumed_wild_type` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_classify_dose_and_no_recommendation` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_http_fetch_live_mocked` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_live_network_error_skips_without_exception` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_mock_fixture_immutable_and_het_hom` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_pheno_from_phenotypes_and_atc_on_row` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_pipeline_idempotent_no_duplicate_pairing` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_provider_is_interface_not_http` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_f5_unknown_json_keys_do_not_crash` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_html_truncated_who_pin_exits_nonzero` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_matcher_off_circuit_breaker_does_not_spawn_java` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_pharmcat_wrapper_is_argv_list_not_shell` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_rec_pairings_forbid_dose_mg_token` |
| D-50 | F5/F1s/ops | `test_f5_rec_pipeline.RepoConformHardeningTests.test_who_html_pins_parse_with_stdlib_parser` |
| D-51 | F2 IIa-safe / FR-id | `test_cds.IiaSafeMechanismTests.test_blocks_audit_matrix` |
| D-51 | F2 IIa-safe / FR-id | `test_cds.IiaSafeMechanismTests.test_does_not_block_outside_the_five_mechanisms` |
| D-51 | F2 IIa-safe / FR-id | `test_cds.IiaSafeMechanismTests.test_families_are_named_mechanisms` |
| D-51 | F2 IIa-safe / FR-id | `test_cds.IiaSafeMechanismTests.test_hungarian_brand_does_not_need_english_inn` |
| D-51 | F2 IIa-safe / FR-id | `test_cds.IiaSafeMechanismTests.test_who_pins_cover_new_atc5` |
| D-51 | F2 IIa-safe / FR-id | `test_cds.OnPathTests.test_iia_safe_tramadol_no_suggestion` |
| D-51 | GSPR annotáció | `test_fr_trace.DeferredFrTests.test_fr_230_no_hl7_v2_parser` |
| D-51 | GSPR annotáció | `test_fr_trace.DeferredFrTests.test_fr_430_prs_interface_not_built` |
| D-51 | GSPR annotáció | `test_fr_trace.DeferredFrTests.test_fr_480_encyclopedia_view_not_built` |
| D-51 | GSPR annotáció | `test_fr_trace.DeferredFrTests.test_fr_510_report_regen_not_built` |
| D-51 | GSPR annotáció | `test_fr_trace.DeferredFrTests.test_fr_540_patient_copy_endpoint_not_built` |
| D-51 | GSPR annotáció | `test_fr_trace.DeferredFrTests.test_fr_600_alert_telemetry_not_built` |
| D-51 | OQ-05 III (FR-250/420/700) | `test_fr_trace.Fr250NormalisationTests.test_default_keeps_seven_character_substance_code` |
| D-51 | OQ-05 III (FR-250/420/700) | `test_fr_trace.Fr250NormalisationTests.test_e_map_001_is_catalogued_not_raised_by_f1plus_renderer` |
| D-51 | OQ-05 III (FR-250/420/700) | `test_fr_trace.Fr420HighlightTests.test_severity_means_replace_prescribed_is_false_in_assembler` |
| D-51 | OQ-05 III (FR-250/420/700) | `test_fr_trace.Fr700LlmBanTests.test_clinical_and_report_have_no_llm_imports` |
| D-51 | GSPR annotáció | `test_fr_trace.FrIdInventoryTests.test_every_spec_fr_appears_in_tests` |
| D-52 | stratégia-rekord, nem minősítés | `test_fr_trace.FallenGtmRecordTests.test_sku_and_buyers_records_fallen_longevity` |
| D-52 | stratégia-rekord, nem minősítés | `test_fr_trace.FallenGtmRecordTests.test_spec_has_a16_a17_rows` |
| D-52 | stratégia-rekord, nem minősítés | `test_fr_trace.FallenGtmRecordTests.test_src_has_no_zero_knowledge_or_local_first` |
| D-53 | OQ-06 IIa-safe | `test_cds.IiaSafeMechanismTests.test_ba_reaudit_block_pass_and_hungarian_names` |
| D-53 | OQ-06 IIa-safe | `test_cds.IiaSafeMechanismTests.test_l01bc_prefix_would_false_positive_on_pinned_who` |
| D-53 | OQ-05 III.4 matcher-kapu | `test_fr_trace.MatcherOnHgvsGateTests.test_spec_and_trace_bind_hgvs_to_matcher_on` |
| D-53 | OQ-05 III.4 matcher-kapu | `test_fr_trace.MatcherOnHgvsGateTests.test_src_has_no_hgvs_or_vrs_implementation` |
| D-53 | pin / MANIFEST | `test_official_pins.OfficialPinTests.test_l01bc_counterexample_pins_2026_08_16` |
| D-53 | pin / MANIFEST | `test_official_pins.OfficialPinTests.test_manifest_accessed_is_pin_day_not_unified` |
| D-54 | OQ-05 Q4 | `test_fr_trace.Com1023F3ForkTests.test_oq05_has_q4_not_seal` |
| D-54 | OQ-05 Q4 | `test_fr_trace.Com1023F3ForkTests.test_registry_s077_is_com_s065_stays_clopidogrel` |
| D-54 | OQ-05 Q4 | `test_fr_trace.Com1023F3ForkTests.test_spec_has_a18_and_com_proposal` |
| D-54 | OQ-05 Q4 | `test_official_pins.OfficialPinTests.test_com_2025_1023_pins_2026_08_16` |

## 3. Teljes unittest-inventárium

Minden `test_*` a fában. A `mapped` oszlop akkor `igen`, ha a teszt szerepel a fenti evidenciatáblában.

| Modul | Teszt | Mapped |
| --- | --- | --- |
| `tests/test_cds.py` | `test_repo_stays_locked` | igen |
| `tests/test_cds.py` | `test_ba_reaudit_block_pass_and_hungarian_names` | nem |
| `tests/test_cds.py` | `test_blocks_audit_matrix` | nem |
| `tests/test_cds.py` | `test_does_not_block_outside_the_five_mechanisms` | nem |
| `tests/test_cds.py` | `test_families_are_named_mechanisms` | nem |
| `tests/test_cds.py` | `test_hungarian_brand_does_not_need_english_inn` | nem |
| `tests/test_cds.py` | `test_l01bc_prefix_would_false_positive_on_pinned_who` | nem |
| `tests/test_cds.py` | `test_who_pins_cover_new_atc5` | nem |
| `tests/test_cds.py` | `test_clinical_package_does_not_import_cds` | igen |
| `tests/test_cds.py` | `test_report_package_does_not_import_cds` | igen |
| `tests/test_cds.py` | `test_http_lock_discovery_and_empty_post` | nem |
| `tests/test_cds.py` | `test_lock_returns_empty_cards` | igen |
| `tests/test_cds.py` | `test_fail_open_on_timeout` | nem |
| `tests/test_cds.py` | `test_http_on_order_sign` | nem |
| `tests/test_cds.py` | `test_iia_safe_codeine_no_suggestion` | nem |
| `tests/test_cds.py` | `test_iia_safe_off_does_not_invent_codeine_row` | nem |
| `tests/test_cds.py` | `test_iia_safe_tramadol_no_suggestion` | nem |
| `tests/test_cds.py` | `test_no_pgx_info_card` | nem |
| `tests/test_cds.py` | `test_paroxetine_nm_continue_card` | nem |
| `tests/test_clinical.py` | `test_outside_call_cli_rejected` | igen |
| `tests/test_clinical.py` | `test_admin_cannot_skip_gate` | igen |
| `tests/test_clinical.py` | `test_audit_append_only` | nem |
| `tests/test_clinical.py` | `test_counselling_after_sample_e_consent_002` | nem |
| `tests/test_clinical.py` | `test_create_report_does_not_load_medication_table` | igen |
| `tests/test_clinical.py` | `test_dsr_overdue_alert` | nem |
| `tests/test_clinical.py` | `test_extra_gene_e_consent_004` | nem |
| `tests/test_clinical.py` | `test_happy_path_meta_and_b41` | nem |
| `tests/test_clinical.py` | `test_missing_consent_e_consent_003` | igen |
| `tests/test_clinical.py` | `test_missing_counselling_e_consent_001` | igen |
| `tests/test_clinical.py` | `test_missing_license_e_consent_005` | igen |
| `tests/test_clinical.py` | `test_omit_from_patient` | nem |
| `tests/test_clinical.py` | `test_refuse_erasure_letter_keeps_report` | nem |
| `tests/test_clinical.py` | `test_withdraw_410_and_certificate` | nem |
| `tests/test_clinical.py` | `test_report_without_counselling_http` | nem |
| `tests/test_clinical.py` | `test_ui_and_iso_and_walk` | nem |
| `tests/test_clinical.py` | `test_empty_diplotype_called` | nem |
| `tests/test_clinical.py` | `test_indeterminate_allowed` | nem |
| `tests/test_clinical.py` | `test_tsv` | nem |
| `tests/test_clinical.py` | `test_vcf_conflict` | nem |
| `tests/test_clinical.py` | `test_vcf_missing_defining_position_is_indeterminate_not_normal` | nem |
| `tests/test_clinical.py` | `test_vcf_missing_reference` | nem |
| `tests/test_etap0.py` | `test_prepare12_cyp2c19_keeps_cpic_and_adds_dpwg_index` | nem |
| `tests/test_etap0.py` | `test_versions_and_urls_are_separate_sources` | nem |
| `tests/test_etap0.py` | `test_quarterly_report_has_opaque_syn_org_display` | nem |
| `tests/test_etap0.py` | `test_cyp2c19_nm_clopidogrel_continue_without_mg` | nem |
| `tests/test_etap0.py` | `test_cyp2c19_pm_clopidogrel_alternative_without_invented_pm_label` | nem |
| `tests/test_etap0.py` | `test_cyp2d6_does_not_pair_clopidogrel` | nem |
| `tests/test_etap0.py` | `test_pairing_table_is_keyed_by_gene_and_atc5` | nem |
| `tests/test_etap0.py` | `test_missing_cyp2c9_star3_is_indeterminate` | nem |
| `tests/test_etap0.py` | `test_prepare12_snv_genes_are_pinned` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f1_plus_f5_still_has_no_guideline_row` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_default_source_is_off` | igen |
| `tests/test_f5_rec_pipeline.py` | `test_env_mock_switch` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_infer_mock_het_positive` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_infer_mock_wt_negative` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_infer_off_no_finding` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_live_empty_fetch_adds_nothing` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_mock_does_not_overwrite_index_pairs` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_mock_source_loads_het_and_wt` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_prod_table_has_no_f5_pairing` | igen |
| `tests/test_f5_rec_pipeline.py` | `test_classify_avoid_and_continue` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_mock_fixture_validates` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_null_f5_lookup_is_valid_but_skipped` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_schema_file_exists` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_files_query_matcher_on_true` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_builder_skip_protects_index_pairs` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_index_paroxetine_not_in_extra_json` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_warfarin_cyp2c9_alone_no_finding` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_warfarin_cyp2c9_star2_star3_is_alternative` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_add_outside_call_merges_hla_b` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_atc_dict_keys_valid_format` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_builder_script_cannot_emit_clopidogrel` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_ci_forbids_live_f5_and_offline_jar` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_cyp2d6_cnv_not_assumed_wild_type` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_ensure_jar_offline_missing_raises` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f5_classify_dose_and_no_recommendation` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f5_empty_array_does_not_crash` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f5_empty_recommendation_skipped` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f5_http_fetch_live_mocked` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f5_live_network_error_skips_without_exception` | igen |
| `tests/test_f5_rec_pipeline.py` | `test_f5_live_non_dict_row_fails_fast` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f5_mock_fixture_immutable_and_het_hom` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f5_pheno_from_phenotypes_and_atc_on_row` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f5_pipeline_idempotent_no_duplicate_pairing` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f5_provider_is_interface_not_http` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f5_source_invalid_token_throws` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_f5_unknown_json_keys_do_not_crash` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_html_truncated_who_pin_exits_nonzero` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_index_pair_overwrite_throws_exception` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_matcher_off_circuit_breaker_does_not_spawn_java` | igen |
| `tests/test_f5_rec_pipeline.py` | `test_missing_version_metadata_raises_exception` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_pharmcat_concurrent_requests_isolation` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_pharmcat_wrapper_is_argv_list_not_shell` | igen |
| `tests/test_f5_rec_pipeline.py` | `test_rec_pairings_forbid_dose_mg_token` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_warfarin_full_matrix_parametric` | nem |
| `tests/test_f5_rec_pipeline.py` | `test_who_html_pins_parse_with_stdlib_parser` | nem |
| `tests/test_fr_trace.py` | `test_oq05_has_q4_not_seal` | igen |
| `tests/test_fr_trace.py` | `test_registry_s077_is_com_s065_stays_clopidogrel` | igen |
| `tests/test_fr_trace.py` | `test_spec_has_a18_and_com_proposal` | igen |
| `tests/test_fr_trace.py` | `test_fr_230_no_hl7_v2_parser` | nem |
| `tests/test_fr_trace.py` | `test_fr_430_prs_interface_not_built` | nem |
| `tests/test_fr_trace.py` | `test_fr_480_encyclopedia_view_not_built` | nem |
| `tests/test_fr_trace.py` | `test_fr_510_report_regen_not_built` | nem |
| `tests/test_fr_trace.py` | `test_fr_540_patient_copy_endpoint_not_built` | nem |
| `tests/test_fr_trace.py` | `test_fr_600_alert_telemetry_not_built` | nem |
| `tests/test_fr_trace.py` | `test_sku_and_buyers_records_fallen_longevity` | nem |
| `tests/test_fr_trace.py` | `test_spec_has_a16_a17_rows` | nem |
| `tests/test_fr_trace.py` | `test_src_has_no_zero_knowledge_or_local_first` | nem |
| `tests/test_fr_trace.py` | `test_default_keeps_seven_character_substance_code` | nem |
| `tests/test_fr_trace.py` | `test_e_map_001_is_catalogued_not_raised_by_f1plus_renderer` | igen |
| `tests/test_fr_trace.py` | `test_severity_means_replace_prescribed_is_false_in_assembler` | igen |
| `tests/test_fr_trace.py` | `test_clinical_and_report_have_no_llm_imports` | igen |
| `tests/test_fr_trace.py` | `test_every_spec_fr_appears_in_tests` | nem |
| `tests/test_fr_trace.py` | `test_spec_and_trace_bind_hgvs_to_matcher_on` | nem |
| `tests/test_fr_trace.py` | `test_src_has_no_hgvs_or_vrs_implementation` | nem |
| `tests/test_hitl.py` | `test_blind_then_review_immutable` | nem |
| `tests/test_hitl.py` | `test_list_hides_motor_and_pii` | nem |
| `tests/test_hitl.py` | `test_note_pii_rejected` | nem |
| `tests/test_hitl.py` | `test_his_gateway_ingest_hitl_report_untouched` | nem |
| `tests/test_hitl.py` | `test_ui_and_clinician_forbidden_and_walk` | nem |
| `tests/test_hitl.py` | `test_accepted_ingest_writes_hitl_not_clinical_report` | nem |
| `tests/test_hitl.py` | `test_atc5_writes_hitl` | nem |
| `tests/test_hitl.py` | `test_rare_drop_does_not_write_hitl` | nem |
| `tests/test_hitl.py` | `test_store_failure_is_fail_open_202` | nem |
| `tests/test_hitl.py` | `test_anon_accepts_seven_char_paroxetine` | nem |
| `tests/test_hitl.py` | `test_pseudo_research_consent_keeps_paroxetine_code` | nem |
| `tests/test_market_pins.py` | `test_manifest_and_his_ceiling` | nem |
| `tests/test_market_pins.py` | `test_official_pin_count_is_not_seven` | nem |
| `tests/test_market_pins.py` | `test_pricing_doc_is_conclusion_not_list` | nem |
| `tests/test_official_pins.py` | `test_com_2025_1023_pins_2026_08_16` | igen |
| `tests/test_official_pins.py` | `test_etap0_dpwg_ensembl_and_clopidogrel_pins` | nem |
| `tests/test_official_pins.py` | `test_knowledge_json_points_at_on_disk_files` | nem |
| `tests/test_official_pins.py` | `test_l01bc_counterexample_pins_2026_08_16` | nem |
| `tests/test_official_pins.py` | `test_manifest_accessed_is_pin_day_not_unified` | nem |
| `tests/test_official_pins.py` | `test_manifest_and_binaries` | nem |
| `tests/test_official_pins.py` | `test_prepare12_live_pair_pins_2026_08_15` | nem |
| `tests/test_official_pins.py` | `test_software_ready_pins_2026_08_15` | nem |
| `tests/test_oq05_protocol.py` | `test_brief_does_not_freeze_suite_size_as_igen_argument` | nem |
| `tests/test_oq05_protocol.py` | `test_ci_freezes_iia_safe_block` | nem |
| `tests/test_oq05_protocol.py` | `test_g_q1_points_to_gold_fixture` | nem |
| `tests/test_oq05_protocol.py` | `test_gold_fixture_is_unsigned_json_not_pdf` | nem |
| `tests/test_oq05_protocol.py` | `test_outbound_listed_paths_exist` | nem |
| `tests/test_oq05_protocol.py` | `test_send_pack_committed_matches_generator` | nem |
| `tests/test_oq05_protocol.py` | `test_send_pack_hashes_match_bytes` | nem |
| `tests/test_oq05_protocol.py` | `test_send_pack_is_not_a_seal_and_names_handover_files` | nem |
| `tests/test_oq05_protocol.py` | `test_tervezet_send_gate_is_citation_not_reg030` | nem |
| `tests/test_oq05_protocol.py` | `test_brief_q1_allow_list_matches_schema` | nem |
| `tests/test_oq05_protocol.py` | `test_committed_protocol_matches_generator` | nem |
| `tests/test_oq05_protocol.py` | `test_delta_195_241_has_46_and_all_exist` | nem |
| `tests/test_oq05_protocol.py` | `test_every_mapped_id_exists_in_ast` | nem |
| `tests/test_oq05_protocol.py` | `test_feltetellel_tervezet_is_not_a_seal` | nem |
| `tests/test_oq05_protocol.py` | `test_generated_text_is_not_a_seal` | nem |
| `tests/test_oq05_protocol.py` | `test_mapped_tests_run_ok` | nem |
| `tests/test_oq05_protocol.py` | `test_mapped_unique_and_q3_count_are_classification_evidence` | nem |
| `tests/test_oq05_protocol.py` | `test_q2_is_partial_and_q4_does_not_unlock_flags` | nem |
| `tests/test_oq05_protocol.py` | `test_repo_locks_are_the_compile_time_values` | nem |
| `tests/test_oq05_protocol.py` | `test_script_and_protocol_exist` | nem |
| `tests/test_pheno_gold.py` | `test_g3_recall_on_pheno_gold` | nem |
| `tests/test_pheno_gold.py` | `test_n_at_least_30` | nem |
| `tests/test_pheno_gold.py` | `test_no_case_expects_functional_pm` | nem |
| `tests/test_pipeline.py` | `test_keep_and_rare` | nem |
| `tests/test_pipeline.py` | `test_post_shadow_events` | nem |
| `tests/test_pipeline.py` | `test_drop_does_not_increment_cell` | nem |
| `tests/test_pipeline.py` | `test_forward_increments_once` | nem |
| `tests/test_pipeline.py` | `test_v0_07_reject_from_fixture` | nem |
| `tests/test_pipeline.py` | `test_reject_decrease` | nem |
| `tests/test_pipeline.py` | `test_compile_time_false` | igen |
| `tests/test_pipeline.py` | `test_anon_does_not_require_research_consent` | nem |
| `tests/test_pipeline.py` | `test_atc5_rejected_when_dpo_caps_at_level_4` | nem |
| `tests/test_pipeline.py` | `test_atc5_with_account` | nem |
| `tests/test_pipeline.py` | `test_called_common_diplotype_accepted` | nem |
| `tests/test_pipeline.py` | `test_pseudo_without_research_consent` | nem |
| `tests/test_pipeline.py` | `test_rare_raw_genetics_on_ingest` | nem |
| `tests/test_pipeline.py` | `test_wrong_account` | nem |
| `tests/test_pipeline.py` | `test_monitor_has_no_pii` | nem |
| `tests/test_pipeline.py` | `test_v0_01_coarsen_when_cell_small` | nem |
| `tests/test_pipeline.py` | `test_v0_01_raw_when_cell_meets_k` | nem |
| `tests/test_pipeline.py` | `test_v0_02_rare_coarsen` | nem |
| `tests/test_pipeline.py` | `test_v0_02_rare_drop` | nem |
| `tests/test_pipeline.py` | `test_v0_04_small_cell_coarsen` | nem |
| `tests/test_pipeline.py` | `test_v0_05_small_cell_drop` | nem |
| `tests/test_pipeline.py` | `test_v0_06_rarest_always_drop` | nem |
| `tests/test_prepare12_ready.py` | `test_repo_flags_stay_off` | igen |
| `tests/test_prepare12_ready.py` | `test_clinical_hla_b_outside_call_renders` | nem |
| `tests/test_prepare12_ready.py` | `test_f1plus_hla_b_dumps_abacavir_pair_from_lab_result` | igen |
| `tests/test_prepare12_ready.py` | `test_f1plus_ugt1a1_dumps_atazanavir_pair_from_lab_result` | igen |
| `tests/test_prepare12_ready.py` | `test_hla_b_5701_negative_abacavir_continue` | nem |
| `tests/test_prepare12_ready.py` | `test_hla_b_5701_positive_abacavir_alternative` | nem |
| `tests/test_prepare12_ready.py` | `test_ugt1a1_star1_het_atazanavir_continue` | nem |
| `tests/test_prepare12_ready.py` | `test_ugt1a1_star28_hom_atazanavir_alternative` | nem |
| `tests/test_prepare12_ready.py` | `test_cyp2b6_pm_efavirenz_dose_change` | nem |
| `tests/test_prepare12_ready.py` | `test_cyp2c19_pm_citalopram_dose_change` | nem |
| `tests/test_prepare12_ready.py` | `test_cyp2c9_as10_celecoxib_dose_change` | nem |
| `tests/test_prepare12_ready.py` | `test_cyp2c9_as15_celecoxib_continue_not_blanket_im` | nem |
| `tests/test_prepare12_ready.py` | `test_cyp2d6_pm_codeine_alternative` | nem |
| `tests/test_prepare12_ready.py` | `test_cyp3a5_expresser_tacrolimus_dose_change` | nem |
| `tests/test_prepare12_ready.py` | `test_cyp3a5_nonexpresser_tacrolimus_continue` | nem |
| `tests/test_prepare12_ready.py` | `test_dpyd_cpic_hgvs_reference_continue` | nem |
| `tests/test_prepare12_ready.py` | `test_dpyd_pm_capecitabine_alternative` | nem |
| `tests/test_prepare12_ready.py` | `test_dpyd_pm_fluorouracil_alternative` | nem |
| `tests/test_prepare12_ready.py` | `test_f5_and_vkorc1_have_no_invented_pairing` | igen |
| `tests/test_prepare12_ready.py` | `test_hla_b_5801_allopurinol_alternative` | nem |
| `tests/test_prepare12_ready.py` | `test_rec_view_pairings_are_loaded` | nem |
| `tests/test_prepare12_ready.py` | `test_rec_view_pairings_have_no_milligrams` | nem |
| `tests/test_prepare12_ready.py` | `test_slco1b1_poor_function_simvastatin_alternative` | nem |
| `tests/test_prepare12_ready.py` | `test_warfarin_needs_both_genes_and_has_no_mg` | nem |
| `tests/test_prepare12_ready.py` | `test_clinical_add_vcf_default_still_off` | igen |
| `tests/test_prepare12_ready.py` | `test_clinical_add_vcf_matcher_on_persists_diplotype` | nem |
| `tests/test_prepare12_ready.py` | `test_matcher_off_does_not_call_diplotype` | igen |
| `tests/test_prepare12_ready.py` | `test_matcher_on_calls_cyp2d6_star4_hom_from_pharmcat` | nem |
| `tests/test_prepare12_ready.py` | `test_matcher_on_missing_site_is_indeterminate_not_star1` | nem |
| `tests/test_report.py` | `test_delivery_plan_r9_matches_schema` | igen |
| `tests/test_report.py` | `test_full_allow_list_passes` | igen |
| `tests/test_report.py` | `test_rejects_clinical_context` | igen |
| `tests/test_report.py` | `test_rejects_hitl_review` | igen |
| `tests/test_report.py` | `test_rejects_hitl_verdict` | igen |
| `tests/test_report.py` | `test_rejects_medication_entry_type` | igen |
| `tests/test_report.py` | `test_rejects_medication_request` | igen |
| `tests/test_report.py` | `test_rejects_medication_statement` | igen |
| `tests/test_report.py` | `test_rejects_medications` | igen |
| `tests/test_report.py` | `test_rejects_unknown_top_level_and_nested_medications` | igen |
| `tests/test_report.py` | `test_flags_frozen` | igen |
| `tests/test_report.py` | `test_package_ast_has_no_medication_entry_or_gateway_pipeline` | igen |
| `tests/test_report.py` | `test_render_signature_has_no_medication_entry` | igen |
| `tests/test_report.py` | `test_cyp2c19_dumps_official_pairs` | igen |
| `tests/test_report.py` | `test_f5_signals_missing_recommendation_without_inventing` | igen |
| `tests/test_report.py` | `test_vkorc1_pair_exists_recommendation_view_gap_is_flagged` | nem |
| `tests/test_report.py` | `test_called_emits_all_pairs_and_recs` | igen |
| `tests/test_report.py` | `test_indeterminate_no_normal_claim` | igen |
| `tests/test_report.py` | `test_pdf_contains_disclaimer_and_pair` | igen |
| `tests/test_report.py` | `test_rejects_medication_payload` | igen |
| `tests/test_report.py` | `test_a11_in_appendix` | igen |
| `tests/test_shadow.py` | `test_atc4_explains_substance_code_not_patient_identity` | nem |
| `tests/test_shadow.py` | `test_paroxetine_card_says_what_exists_and_what_is_missing` | nem |
| `tests/test_shadow.py` | `test_shadow_package_does_not_import_report_renderer` | igen |
| `tests/test_shadow.py` | `test_mapping_is_officially_null` | nem |
| `tests/test_shadow.py` | `test_absent_meds_is_not_silent_nm` | nem |
| `tests/test_shadow.py` | `test_atc4_does_not_claim_paroxetine_or_pm` | nem |
| `tests/test_shadow.py` | `test_atc5_fluoxetine_no_gene_based_dosing_and_no_pm` | nem |
| `tests/test_shadow.py` | `test_atc5_paroxetine_nm_pairs_without_writing_pm` | nem |
| `tests/test_shadow.py` | `test_deterministic_findings` | nem |
| `tests/test_shadow.py` | `test_egfr_below_30_flags_organ_not_a_dose` | nem |
| `tests/test_shadow.py` | `test_pm_diplotype_paroxetine_is_dose_change_category` | nem |
| `tests/test_transform.py` | `test_gold_v0_timestamp` | nem |
| `tests/test_transform.py` | `test_quarter_boundaries` | nem |
| `tests/test_transform.py` | `test_wall_clock_not_utc_shift` | nem |
| `tests/test_transform.py` | `test_dose_r4_gold_v0_01` | nem |
| `tests/test_transform.py` | `test_pii_strip_gold_v0_01` | nem |
| `tests/test_transform.py` | `test_v0_01_atc_time_pii_dose` | nem |
| `tests/test_transform.py` | `test_atc5_accepted_by_default` | nem |
| `tests/test_transform.py` | `test_atc5_rejected_when_dpo_caps_at_level_4` | nem |
| `tests/test_transform.py` | `test_day` | nem |
| `tests/test_transform.py` | `test_practitioner_and_meta_source_stripped` | nem |
| `tests/test_transform.py` | `test_taj` | nem |
| `tests/test_transform.py` | `test_already_atc4` | nem |
| `tests/test_transform.py` | `test_atc5_to_atc3` | nem |
| `tests/test_transform.py` | `test_atc5_to_atc4` | nem |
| `tests/test_transform.py` | `test_default_keeps_substance_code` | nem |
| `tests/test_vcf_coverage.py` | `test_hla_and_ugt_are_not_snv_not_tested` | nem |
| `tests/test_vcf_coverage.py` | `test_matcher_stays_off` | igen |
| `tests/test_vcf_coverage.py` | `test_three_missing_sites_are_indeterminate_not_normal` | nem |

## 4. Ami ez a jegyzőkönyv nem

- Nem tölti ki az OQ-05 V. szakasz IGEN / NEM / FELTÉTELLEL pecsétjét.
- Nem állítja, hogy a szoftver CE-jelölt orvostechnikai eszköz.
- Nem állítja, hogy a CI job hermetikusan hálózat nélkül fut. A JAR-pin HTTP a tesztek *előtt* fut; az air-gap a `PCE_PHARMCAT_OFFLINE=1` tesztfázis.
- Nem állítja, hogy az F5 live út fail-fast. Hálózati `OSError` → üres lista (fail-open).
- Nem pecsételi az OQ-06-ot (IIa-safe párok) és nem billenti a `LIVE_CDS` / `MATCHER_ON` / `IIA_SAFE_BLOCK` lakatot.
- A 261-es suite méret **nem** IGEN pecsét. Az F5 fail-open és a CI JAR HTTP **nem** NEM pecsét.

## 5. Maradék ops-kockázat — nem Q1–Q3 döntő, nem pecsét-feloldó

Két szándékos viselkedés. A gyártói záradék-tervezet: `docs/pce/Outbound/OQ-05-feltetellel-tervezet.md`. D-56: fail-fast-re váltás **nem** OQ-05 előfeltétel.

| ID | Tény | Hol | OQ-05 viszony |
| --- | --- | --- | --- |
| **R-OPS-01** | F5 live `OSError` → `[]` (fail-open). Prod `CPIC_F5_SOURCE=off`. Mock nem megy az aláírt leletre. | `LiveF5Provider.rows()`; OPS-F5 tesztek | Shadow/F1s ops. Nem Rule 11 vs 11c. |
| **R-OPS-02** | CI a tesztek előtt HTTP-n tölti a pinelt JAR-t. Tesztfázis: `PCE_PHARMCAT_OFFLINE=1`. | `.github/workflows/ci.yml`; OPS-PHARMCAT tesztek | Matcher default ki. Nem a teljes job air-gap. |

**E-31** a brief/G allow-list 45→47 (`schema.py`). Nem outside-call, nem HGVS.

**D-57:** a counsel-küldés kapuja a brief melléklet-útvonalai, nem a REG-030 teljes Class I QMS. D.1 kezdeti 14971, nem teljes dosszié. REG-010 = A melléklet. A Q1–Q4/III/OPS mapped egyedi teszt **51**, a Q3 **10**; a suite méret **nem** IGEN. Send-pack citáció: `tests/test_oq05_protocol.py` `Oq05CounselSendPackTests` (**nem** mapped Q1–Q3 evidencia).

**D-58:** átadás-átvételi SHA-256 boríték: `docs/pce/Outbound/OQ-05-SEND-PACK.md`. Nem pecsét. A boríték a saját hashét nem tartalmazza. REG-030 nincs a hash-táblában.

*Generálta: `docs/pce/ProcessArtifacts/BuildScripts/generate_oq05_protocol.py`. Újragenerálás: `PYTHONPATH=src python3 …/generate_oq05_protocol.py --write`.*
