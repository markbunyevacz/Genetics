# PCE delivery plan (production-like, `main` only)

| | |
| --- | --- |
| **Repo** | `genetics` tree only |
| **Branch** | `main` |
| **Spec** | `docs/pce/PCE-SPEC-v1.2.md` **FAGYASZTVA** (§10.2) |
| **Lefedettség** | [SPEC-PLAN-TRACE.md](SPEC-PLAN-TRACE.md) — NOW 27/27 terv; a kódban 26 tétel a demóban kész, 1 szándékos tiltás (matcher ki); laborút 8/8, kutatási út 5/5; F2 cső (`pce_cds`) PARTIAL lakattal |
| **Adatfolyam / UX** | [DATAFLOW-AND-UX.md](DATAFLOW-AND-UX.md) |
| **Adat** | Gold V0 + hivatalos CPIC/DPWG/FDA táblák. Nincs élő HIS, kitalált gyártónév, dummy guideline-szöveg. |
| **Flag** | `LIVE_CDS = False`; F1+ `MATCHER_ON = False`; `IIA_SAFE_BLOCK = True`. CI assert. |

Egy szelet **kész**, ha a TRACE-ben PARTIAL vagy FULL, a B-szerződés tesztelve van, és a DATAFLOW útja SYN-en végigjárható. Nem kész: hardcoded JSON, `NotImplementedError`, második „sim” csomag.

**WP** = work package (megvalósítási csomag ebben a tervben). Például **WP-M** az árnyék-motor (élő gén–gyógyszer párosítás a kutatási úton), **WP-H** az ehhez tartozó emberi ellenőrző tároló és API. A szereplők **P1–P6** a spec §5.1 personái (P3 = klinikai farmakológus). **HITL** = human-in-the-loop, külön ellenőrző UI, nem a laborlelet.

## Hard rules

- F1+ renderer nem kap `medications` / HIS gyógyszerlistát (FR-470 / R-021).
- Shadow store ≠ report store (külön process, külön SQLite: `var/clinical.sqlite`, `var/hitl.sqlite`, `var/kcell.sqlite`).
- Ismeretlen diplotípus: A14 szerint ritkaként kezelendő (nincs az allowlisten).
- k-cella count soha nem a PCE payloadon.
- Teljes CPIC frequency sheet nem vendorolható; keep-set script: `tests/fixtures/gold-v0/extract_cpic_frequency_slice.py`.
- FR-100 kapu a report-render előtt; CLI sem kerülheti meg.
- Hibakódok csak B.5; W-* nem csendes 200.
- SYN org/lab/orvos: opák ID (`SYN-ORG-001`, `SYN-MD-001` slot), nem kitalált Kft./kórháznév (A9).

## Technológiai kötés (B, nem új architektúra)

| Réteg | SYN technológia | Spec |
| --- | --- | --- |
| Klinikai API | `src/pce_clinical/` + stdlib `ThreadingHTTPServer` (ugyanaz a minta mint a gateway serve) | B.3.1–3.3, B.4.1–4.3 |
| Klinikai store | SQLite `var/clinical.sqlite` | B.2.1; NFR-031 éles: Postgres+KMS később, nem F0 blokkoló |
| Gateway | `src/pce_gateway/` | B.3.5, E.3 |
| k-cella | SQLite `var/kcell.sqlite` intézményi zóna | E.3.1 |
| HITL | `src/pce_hitl/` + `var/hitl.sqlite` | B.2.2, B.4.6 |
| L4-static | `src/pce_report/` | FR-400-STATIC |
| L4-live | `src/pce_shadow/` — **nem** importálja `pce_report.render` | FR-400-LIVE, 410-LIVE |
| L6-cds | `src/pce_cds/` — **nem** a `pce_clinical` processzuson; repo `LIVE_CDS=false` | FR-520, FR-530 stub |
| IAM | SYN `Authorization` szerep: `counsellor` `lab_signer` `clinician` `hitl_reviewer` `dpo` `gateway` | E.4, FR-470 |
| FHIR | dict Bundle STU3 (`DiagnosticReport` + `Observation`); IG v3.0.0 mezők, nem STU4 operations | B.4.3 |
| PDF | reportlab + rendszer TTF (HU) | FR-500 |
| UX | `src/pce_ui/` HTML formok a fenti API-ra (B.1: v1 labor-UI átmeneti); F2 lakat: `cds.html` | FR-530 stub a `pce_cds`-en |

Éles TLS 1.3 / MFA / EU régió: NFR-031/032/030 — SYN-en localhost, eltérés dokumentált; nem dummy titkosítás.

---

## WP-G — Gateway (F1s) — **kész / PARTIAL; G12 séma zárva**

Gold V0 + HTTP ingest a `main`-en. G12/G13 ezen az ágon:

| ID | AC | Technológia | Oracle |
| --- | --- | --- | --- |
| G12 | GatewayEvent `id`, `received_at`, `org_id`, `payload_hash` (B.2.2) | `pipeline.stamp_gateway_event` | `test_v0_01_raw_when_cell_meets_k` |
| G13 | Practitioner / ward / meta.source törlés | `strip_pii_fr460` | `test_practitioner_and_meta_source_stripped` |
| G14 | `POST /v1/shadow/events` 202; a perzisztencia **nem** ide tartozik — az WP-H | server már 202 | test_pipeline HTTP |

---

## WP-C — L0 consent kapu (FR-100/110/115) — **PARTIAL on this branch**

Enélkül az F1+ PDF nem spec-konform termék (FR-100).

| ID | Given / When / Then | HTTP | Teszt |
| --- | --- | --- | --- |
| C1 | Nincs counselling → riport | `E-CONSENT-001` 409, HU 6. § (2) | TC-CONSENT-001 |
| C2 | counselling.date > sample.collected_at | `E-CONSENT-002` 409 | TC-CONSENT-002 |
| C3 | Nincs 8. § consent | `E-CONSENT-003` 409 | TC-CONSENT-003 |
| C4 | Extra gén 15. § ismételt beleegyezés nélkül | gén kimarad / `E-CONSENT-004` | TC-CONSENT-004 |
| C5 | Nincs `performing_org.license_id` | `E-CONSENT-005` 409 | TC-CONSENT-005 |
| C6 | Admin / config nem kapcsolja ki a kaput | negatív | TC-CONSENT-006 |
| C7 | Érvényes kapu → riport meta: counsellor_id, dátumok, license_id | B.4.1 `counselling` | TC-CONSENT-001 pozitív |
| C8 | Gén-scope lemondás → beteg-példányból kimarad | FR-110 | TC-CONSENT-010 |
| C9 | Visszavonás 72 h: törlés vagy irreverzibilis anonim; URL `E-GONE-010` 410; DeletionCertificate genetikai tartalom nélkül | FR-110 A10 | TC-CONSENT-011..014 |
| C10 | ANON shadow: FR-115 nem blokkol. PSEUDO: nincs ResearchConsent → `E-CONSENT-006`, nincs HITL írás | FR-115 | TC-CONSENT-020..023 |

Store: `CounsellingRecord`, `ConsentRecord`, `Sample`, `DeletionCertificate` a clinical SQLite-ban. v1 kézi POST, nem FHIR Consent (spec FR-100).

---

## WP-K — Klinikai case + outside-call (B.2.1, FR-240, FR-130, FR-220 tárolás) — **PARTIAL**

| ID | AC | API |
| --- | --- | --- |
| K1 | Organization, Subject (`reid_key_ref` külön tábla), Case `DRAFT` | `POST /v1/orgs|subjects|cases` |
| K2 | Outside-call JSON tömb **és** TSV, UTF-8 | `POST /v1/cases/{id}/outside-calls` |
| K3 | Üres diplotípus | `E-CALL-001` 400 |
| K4 | Outside-call + VCF egyszerre | `W-CALL-010` 409, status `NEEDS_RESOLUTION`, nincs automatikus választás |
| K5 | callability enum CALLED/PARTIAL/INDETERMINATE/NOT_TESTED | Diplotype sor |
| K6 | `PUT .../clinical-context` tárol a kutatási úthoz; az aláírt lelet nem ebből a listából készül | FR-220 |
| K7 | L4 log: nincs név/TAJ/születési dátum | CI scanner FR-130 |

---

## WP-N — Normalizálás (FR-250)

| ID | AC | Megjegyzés |
| --- | --- | --- |
| N1 | ATC + verziózott mapping a riport metaadatában | A gateway ATC-csonkolása már megvan; a klinikai út ugyanazt a csonkolást használja, ha gyógyszerlistát *tárol* |
| N2 | Ismeretlen kód → `NEEDS_MAPPING` / `E-MAP-001`, nincs csendes hiányos lista | Shadow LIVE input |
| N3 | HGVS/VRS left-align + trim | **HGVS/VRS előfeltétel: `MATCHER_ON=true`.** Amíg a repo flag false és F1 = FR-240, N3 nem NOW. Kapcsoláskor WP-V V8. |

OGYÉI gépi licence OQ-11 `[NEEDS VERIFICATION]` — SYN-en ATC WHO; nem kitalált HU törzs.

---

## WP-T — RuleSetVersion + PREPARE-12 + források (FR-310, 400-STATIC, 410-EDU)

| ID | AC | Adat |
| --- | --- | --- |
| T1 | `config_id = pgx-prepare-12@<file-version>` külső JSON, nem kód-tuple egyedül | PREPARE 12 gén a specből |
| T2 | HLA-A / NUDT15 külön config fájl | PGx-Passport opció |
| T3 | Change-control rekord konfigurációváltáskor | FR-310; FR-510 listázás P1 |
| T4 | CPIC `pair_view` + `recommendation_view` a **12 génre** (extract script) | S049; F5/VKORC1 üres rec **jelezve**, nincs kitalált szöveg |
| T5 | DPWG + FDA: hivatalos fájl/API vagy a leletben **nincs** kitalált DPWG sor; ha van forrás, mindkettő URL-lel, nincs szintetizált harmadik | **SYN kész:** ClinPGx DPWG pin + FDA Table 2-2 kivonat; `dpwg_version` / `fda_table_version` a B.4.1 JSON-on |
| T6 | EDU: hivatalos osztály-szöveg + URL, **vagy** `phenoconversion_edu: null` + TC hogy null megengedett forrás hiányában | FR-410-EDU; S043 notesonusage üres volt |
| T7 | ≥5 tiltott ha–akkor fixture → `E-EDU-001` | TC-EDU |

---

## WP-R — F1+ renderer (folytatás)

Már a `main`-en: CYP2D6 CPIC dump, INDETERMINATE, A.1/A.1.1, PDF, izoláció. Hiány:

| ID | AC | Oracle |
| --- | --- | --- |
| R8 | B.4.1 top-level: `report_id`, `case_id`, `callability_summary`, `findings[].statements[]`, `counselling`, `white_label` | séma teszt |
| R9 | Tiltott mezők reject: `functional_phenotype`, `shadow_recommendation`, `dose_mg`, `live_findings`, `medications`, `medication_entries`, `medication_entry`, `MedicationEntry`, `medicationRequest`, `MedicationRequest`, `medicationStatement`, `MedicationStatement`, `clinical_context`, `hitl_review`, `hitl_verdict`, `hitl_*` | TC-ISO |
| R10 | FR-420: génenként tagolt findings; CRITICAL nem „cseréld a felírt szert” | TC-ALRT-001 F1+ |
| R11 | Kapu: `render_f1plus` csak WP-C zöld case-re hívható | FR-100 |
| R12 | `unsourced_claims == 0` minden statement-en source+url | FR-400 |
| R13 | PDF **minden oldal**: config, callability, aláíró hely, A.1, A.1.1, kolofon | FR-490/500 |

---

## WP-F — Delivery szerződések (FR-500, B.4)

| ID | AC | Technológia |
| --- | --- | --- |
| F1 | `GET /v1/cases/{id}/reports/{rid}` B.4.1 JSON | pce_clinical |
| F2 | FHIR R4 Bundle, Genomics Reporting IG **STU3**: DiagnosticReport + Observation genotípus/genotípus-fenotípus; nincs functional_phenotype Observation a med-listából | teszt resourceType + LOINC; STU4 operations **nincs** |
| F3 | `DocumentReference.description` = A.1.1 | FR-490 |
| F4 | White-label: partner név/logo slot + PCE kolofon „technológiai szállító” | SYN-ORG display, nem kitalált cég |
| F5 | Report `immutable`; új verzió = új id (`parent_report_id` P1 FR-510) | |

---

## WP-U — Labor / tanácsadó / HITL HTML (B.1 átmeneti UI)

| ID | Persona | Képernyő | API |
| --- | --- | --- | --- |
| U1 | P4 | counselling + consent form | WP-C |
| U2 | P1 | case + TSV/JSON feltöltés + előnézet + aláírás | WP-K, F |
| U3 | P1 | hibák HU-ul (B.5) | 409/400 body |
| U4 | P3/HITL | batch lista, vak lépés, verdict | WP-H |
| U5 | P5 | audit export gomb, A14 monitor letöltés | WP-Q, G10 |
| U6 | P2 | **nincs** belépés; dokumentált: lelet a laborból | FR-470 |

HTML POST a valós API-ra, nem screenshot-mock.

---

## WP-X — Magyarázat (FR-710)

| ID | AC |
| --- | --- |
| X1 | `GET /v1/cases/{id}/explanation` → gének, diplotípus, callability, `config_id`, guideline URL, **laikus HU** |
| X2 | ugyanaz a case+config → **bitre azonos** body (NFR-060) |
| X3 | nincs LLM, nincs SHAP | CI |
| X4 | 6. § (6) kérés napló AuditEvent | WP-Q |

Szövegsablon a spec/A.1 tényeiből és a case mezőiből; nem szabadon írt klinikai tanács.

---

## WP-L — Nyelv (FR-610 P0)

| ID | AC |
| --- | --- |
| L1 | UI HU (WP-U) |
| L2 | Guideline-sor: `text_en` kötelező (hivatalos CPIC); `text_hu` csak lektorált forrásból — különben jelölés „angol eredeti, nincs lektorált magyar”, **nem** gépi fordítás |
| L3 | A.1.1 HU marad (Appendix A) |

---

## WP-Q — Audit, RBAC, CI secrets (FR-120, NFR-032/033/040)

| ID | AC |
| --- | --- |
| Q1 | AuditEvent append-only; UPDATE elutasítva | TC-AUDIT |
| Q2 | Export CSV+JSON; genetikai nyers VCF nincs a naplóban | FR-120 |
| Q3 | Szerep-token SYN; clinician ≠ hitl_reviewer | E.4 |
| Q4 | gitleaks + secret nincs a repóban | NFR-033 |
| Q5 | Hash-chain | **DEFERRED P1** |

---

## WP-M — Shadow motor (FR-400-LIVE, FR-410-LIVE)

Külön csomag: `src/pce_shadow/`. `pce_report` nem importálja.

| ID | AC | Oracle |
| --- | --- | --- |
| M1 | Input: coarsened/raw diplotípus + meds (default 7 karakteres hatóanyag-kód) | GatewayEvent |
| M2 | Output: `live_findings[]` stratégia-kategória, **nincs** `dose_mg` | B.2.2 |
| M3 | CYP2D6 gén szerinti **normál metabolizáló** + **7 karakteres** paroxetin (`N06AB05`) vagy fluoxetin (`N06AB03`): a gén szerinti osztály megmarad; FDA `strong` gátló rögzítve; **funkcionális szegény metabolizáló üres**, mert a 2023-as CPIC SSRI guideline-ban **nincs** NM→szegény sor (a hiány a HITL `forras_allapot` listán). Dummy szegény címke = **fail**. Csoportkód `N06AB`: hatóanyag nem ismert (az SSRI-csoportban az eszcitaloprám is benne van) → gátló-állítás szünetel. ANON ingest a 7 karakteres kódot **elfogadja** (D-38). **G3 nevező:** `tests/fixtures/pheno-gold-v0/` (N=32). | TC-PHENO-001; `tests/test_shadow.py`; `tests/test_pheno_gold.py`; `tests/test_hitl.py` |
| M4 | Nincs med lista → `clinical_context=ABSENT`, nem hallgatólagos NM | FR-220/410-LIVE |
| M5 | eGFR < 30 → `reason: organ`, nem számított dózis | B.6.2 |
| M6 | Determinisztikus | NFR-060 |
| M7 | CI: `pce_report` AST-ban nincs `pce_shadow` | FR-470 |
| M8 | PREPARE-12 élő párok a pinelt CPIC recommendation_view stratégia-kategóriájából: index párok **és** a rec-táblás többi szer (kodein, kapecitabin, allopurinol, citalopram, …; ≥50 pár). Warfarin: 2017-es 2. ábra, CYP2C9+VKORC1, nincs mg. F5: adat-agnosztikus ingest (`CPIC_F5_SOURCE=off\|mock\|live`); prod **off**; mock nem hivatalos CPIC sor; nincs kitalált élő pár. Nincs `dose_mg`. | `tests/test_prepare12_ready.py`; `tests/test_f5_rec_pipeline.py` |

Inhibitor tábla: FDA Table 2-2 erős index (paroxetin, fluoxetin) + WHO ATC 5. szint (7 karakter) + CPIC SSRI 2023 Table 2a stratégia-kategória. CPIC SSRI 2023: nincs NM→szegény metabolizáló sor. CPIC opioid 2020: van ilyen szabály opioidra — a paroxetin-SSRI példára **nem** keverjük. A HITL kártya kiírja: mi van, mi hiányzik, kitől, kinek kell beszerezni.

**ETAP 0:** a párosítás `(gén, ATC5)` kulcsú. CYP2C19–clopidogrel (`B01AC04`, WHO) a pinelt CPIC recommendation_view stratégia-kategóriájából. CYP2D6 + clopidogrel nem ad findinget. Funkcionális szegény metabolizáló továbbra is üres.

**2026-08-15:** a maradék PREPARE-12 élő párok + HLA-B / UGT1A1\*28 laboreredmény-befogadás (outside-call). A rendszer **nem** végzi a laborvizsgálatot.

**SYN kód:** `src/pce_shadow/`, `src/pce_hitl/` + `var/hitl.sqlite`, `src/pce_ui/hitl.html`. `python -m pce_hitl`. A klinikai folyamat a `/v1/hitl/**` hívásokra továbbra is 403/404-et ad (FR-470).

---

## WP-H — HITL store + API (FR-440, 450, 450-BLIND)

| ID | AC | API |
| --- | --- | --- |
| H1 | Ingest 202 → ShadowInference a **hitl** DB-be; HIS nem vár | FR-440 |
| H2 | `config_id` + guideline verzió a rekordon | reprodukálhatóság |
| H3 | `GET /v1/hitl/inferences` opák `case_display_id`; nincs PII | FR-450 |
| H4 | `POST .../blind` CONTINUE/ALTERNATIVE/DOSE_CHANGE/INSUFFICIENT; motor rejtve | FR-450-BLIND |
| H5 | `POST .../reviews` AGREE/DISAGREE/INSUFFICIENT_DATA + reason_code; szabad szöveg PII-scan | FR-450 |
| H6 | Vak döntés + verdict immutábilis | E.4.1 |
| H7 | clinician token → `E-ISO-001` | FR-470 |

---

## WP-I — Izoláció / QMS horog

| ID | Item |
| --- | --- |
| I1 | FR-470 grepek (`MedicationEntry`, `medication_entry`, `pce_gateway.pipeline`, `pce_shadow`, `pce_cds` a `pce_report`/`pce_clinical` ellen) + R9↔séma deny-list + clinician 403 + CDS 404 a `pce_clinical`-en |
| I2 | SOUP lista: CPIC API dátum+URL, reportlab, (később PharmCAT pin) SPDX váz | REG-080 |
| I3 | OQ-01 folyamat Outboundban; nincs hamis ISO cert a gitben |
| I4 | `MATCHER_ON is False`; `LIVE_CDS is False` |
| I5 | Nincs openai/anthropic/langchain a klinikai + shadow pathen | FR-700 |

---

## WP-V — VCF út (FR-200, FR-210 gold) — matcher repo flag OFF

F1 default marad FR-240. VCF kell a missing-to-ref P0 teszthez. A csillag-allél BE-út megvan, mint a F2 CDS: paraméterrel tesztelve, repo konstans ki.

| ID | AC |
| --- | --- |
| V1 | `POST /v1/cases/{id}/files` v4.2/4.3, `.vcf`/`.vcf.gz`, `##reference` GRCh37/38 | `E-VCF-003` |
| V2 | Csonka fájl → `E-VCF-001`, **nincs** részleges riport | story 20 |
| V3 | Multi-sample hozzárendelés nélkül → `E-VCF-002` | |
| V4 | > 5 GB → `E-VCF-004` | |
| V5 | ≥3 gold: hiányzó definiáló pozíció → INDETERMINATE, nem NORMAL. Minták: `tests/fixtures/vcf-gold-v0/` (gyártó SYN, Ensembl/dbSNP pin). 4. fájl: CYP2C9\*3. HLA-B / UGT1A1\*28 `not_snv`. CDC GeT-RM fizikai minta labor-QC, nem ezek a fájlok. | FR-210; PharmCAT `--absent-to-ref` **nincs** hívva |
| V6 | Repo `MATCHER_ON is False`. Default `add_vcf` nem hív diplotípust. | FR-300 / OQ-05 |
| V7 | `matcher_on=True`: PharmCAT 3.4.0 NamedAlleleMatcher + Phenotyper **hívva**. CYP2D6 \*4/\*4 CALLED a gold VCF-en. Több diplotípus / hiányzó hely → INDETERMINATE, soha nem kitalált `*1`. HLA-B / UGT1A1\*28 `NOT_TESTED`. Riport: pipeline / PharmVar / CPIC-adat verzió. | `tests/test_prepare12_ready.py`; mint F2 `live_cds=True` |
| V8 | HGVS + GA4GH VRS, left-align + trim a VCF variáns-bemeneten | **Előfeltétel:** repo vagy tenancy `MATCHER_ON=true`. N3. Amíg false, nincs mit normalizálni (FR-240 diplotípus-string). |

---

## WP-F2 — CDS Hooks cső lakattal (FR-520 / FR-530 stub)

A cső a dobozban van. A kimenet compile-time lakat. Bekapcsolás a fejlesztés végén: signed `LIVE_CDS=true`, nem újraírás. Az ON utat a tesztek **paraméterrel** járják (`live_cds=True`); a repo konstans **false** marad.

| ID | AC | Spec |
| --- | --- | --- |
| F2-1 | `python -m pce_cds` SYN port 8092. `GET /cds-services` `enabled: false`. POST order-sign / order-select **200** `cards: []`. Header `X-PCE-LIVE-CDS: false`. | FR-520 lock |
| F2-2 | `pce_clinical` `GET/POST /cds-services/` → 404 `E-ISO-002` | FR-470 |
| F2-3 | Teszt `live_cds=True`: Card a shadow motorból; nincs `dose_mg`; nincs kitalált „szegény metabolizáló”; nincs PGx → info Card | FR-520 ON |
| F2-4 | Timeout 2 s → üres `cards` (fail-open). A felírás nem blokkolódik. | NFR-011; R-010; E-TIMEOUT-CDS |
| F2-5 | IIa-safe mechanizmus (A.4.1 / G §2.4): ATC5 + HU INN-variáns; `IIA_SAFE_BLOCK=true` → info „élő párosítás nem elérhető”, üres suggestion. Tramadol / tegafur / tioguanin / `klopidogrel` bent. | OQ-06 nyitott |
| F2-6 | `GET /.well-known/smart-configuration` lakat: üres capabilities, magyar üzenet | FR-530 stub |
| F2-7 | `pce_report` / `pce_clinical` **nem** importálja a `pce_cds`-t | FR-470 |

**Given/When/Then**

- Given repo `LIVE_CDS=false`, When HIS `POST /cds-services/pgx-order-sign`, Then 200 üres `cards`.
- Given `pce_clinical`, When `GET /cds-services/pgx-order-sign`, Then 404 `E-ISO-002`.
- Given teszt `live_cds=True` + paroxetin ATC5 + CYP2D6 NM, When order-sign, Then van Card, nincs `dose_mg`.
- Given teszt `live_cds=True` + kodein ATC5 + `IIA_SAFE_BLOCK`, When order-sign, Then info, nincs suggestion.
- Given teszt `live_cds=True` + tramadol ATC5 / `Klopidogrel Actavis` + `IIA_SAFE_BLOCK`, When order-sign, Then info, nincs suggestion.

---

## WP-P1 — Spec P1 (nevesítve, nem F0 kód)

FR-230 LRI, FR-480 enciklopédia `GET /v1/encyclopedia` (nincs order-sign Card a `pce_clinical`-en), FR-510 delta-riport, FR-530 **éles** EHR-launch (a stub WP-F2), FR-540 beteg-példány (OQ-13), FR-600 override séma, FR-610 teljes EN UI, FR-120 hash-chain, FR-220 FHIR medication bundle. **F2 élő Card a felírónak:** signed `LIVE_CDS=true` + pecsét (REG-011); story 6–10 élő suggestion.

---

## Expliciten tilos pecsét / CE előtt

Éles HIS, `LIVE_CDS=true` a *repo konstansban* / LOCK tenancyen, matcher ON F1+ HGVS/VRS nélkül (N3/V8), valódi TAJ, kitalált G1/G2/C2, US F2 (OQ-17), §13 gold-set SOP, PRS (FR-430), EESZT írás (NG-05), LLM klinikai szöveg. A `pce_cds` cső **nem** tilos — a suggestion a felírónak tilos. HGVS/VRS előfeltétel: `MATCHER_ON=true`.

---

## Végrehajtási sorrend (függőség)

```
WP-C + WP-K     →  WP-R (R8–R13) + WP-T + WP-F + WP-L + WP-X
                →  WP-U (labor UX, zsákutca nélkül)
WP-G (kész)     →  WP-M → WP-H → WP-U HITL
WP-M            →  WP-F2 (CDS a shadow motort hívja lock/ON paraméterrel)
WP-I            →  végig CI (F1+ 404 + pce_cds izoláció)
WP-Q            →  C/K mellett
WP-N            →  M előtt (mapping)
WP-V            →  R FR-210 gold; matcher repo flag OFF; BE-út paraméterrel
WP-P1 / élő F2  →  pecsét + signed LIVE_CDS=true
```

Ne másold a gateway eseményt az F1+ reportra. Ne találj ki EDU/CPIC/DPWG mondatot.

## Kész definíció — F1+ SYN demo

P4+P1 végigjárja a DATAFLOW §5 F1+ listát; FR-100 piros fixture nem gyárt PDF-et; INDETERMINATE nem NORMAL; B.4.1 JSON + PDF + STU3 Bundle; clinician HITL 403; TRACE NOW-F1+ sorok legalább PARTIAL.

## Kész definíció — F1s SYN demo

HIS fixture → intézményi gateway → `POST /v1/shadow/events` 202 → sor a `hitl.sqlite`-ban → reviewer vak lépés, majd verdict → F1+ `report` tábla üres marad. 7 karakteres kód → 202. TAJ → 400, nincs extra HITL sor. HIS ettől függetlenül 202. Nincs kitalált szegény metabolizáló.

## Kész definíció — F2 SYN lakat

`python -m pce_cds` → LOCKED. `GET /cds-services` `enabled: false`. POST üres `cards`. `pce_clinical` CDS 404. A teszt `live_cds=True` paraméterrel Card-ot ad `dose_mg` nélkül. Repo konstans false.

## Kész definíció — PREPARE-12 élő párok + laboreredmény (2026-08-15)

Shadow: index párok **és** a rec-táblás többi szer stratégia-kategóriát adnak milligramm nélkül. HLA-B\*57:01 pozitív + abakavir → CONSIDER_ALTERNATIVE. HLA-B\*58:01 pozitív + allopurinol → CONSIDER_ALTERNATIVE. CYP2D6 PM + kodein → CONSIDER_ALTERNATIVE. Warfarin: CYP2C9+VKORC1 a 2017-es 2. ábrából, nincs mg. F5 rec_view 0 → nincs kitalált pár. VCF: `matcher_on=True` PharmCAT NamedAlleleMatcher + Phenotyper; CYP2D6 \*4/\*4 CALLED; több diplotípus INDETERMINATE. Default `add_vcf` nem hív diplotípust. Repo flagok false. OQ pecsét nincs.

## Kész definíció — ETAP 0 SYN

F1+ lelet JSON-on `dpwg_version` és `fda_table_version` nem null; DPWG és FDA külön URL; nincs kitalált DPWG adagolási sor és nincs CPIC+DPWG+FDA egy mondatba keverve. PREPARE-12 SNV-katalógus 10 génre pinelve; HLA-B / UGT1A1\*28 `NOT_TESTED` (nem SNV). Hiányzó CYP2C9\*3 VCF → `INDETERMINATE`. Shadow: CYP2C19–clopidogrel élő párosítás gén-kulcson; CYP2D6+clopidogrel nem párosít; `functional_phenotype` üres. A14 monitor `org_display=SYN-ORG-001`. `LIVE_CDS` / `MATCHER_ON` false.


