# PCE delivery plan (production-like, `main` only)

| | |
| --- | --- |
| **Repo** | `genetics` tree only |
| **Branch** | `main` |
| **Spec** | `docs/pce/PCE-SPEC-v1.2.md` **FAGYASZTVA** (§10.2) |
| **Lefedettség** | [VALASZ-SPEC-TERV.md](VALASZ-SPEC-TERV.md) (tételes válasz) · [SPEC-PLAN-TRACE.md](SPEC-PLAN-TRACE.md) — NOW 27/27 terv; kód 0 FULL / **21 PARTIAL** / 5 MISSING (F1s HITL); F1+ dataflow 8/8 |
| **Adatfolyam / UX** | [DATAFLOW-AND-UX.md](DATAFLOW-AND-UX.md) |
| **Adat** | Gold V0 + hivatalos CPIC/DPWG/FDA táblák. Nincs élő HIS, kitalált gyártónév, dummy guideline-szöveg. |
| **Flag** | `LIVE_CDS = False`; F1+ `MATCHER_ON = False`. CI assert. |

Egy szelet **kész**, ha a TRACE-ben PARTIAL vagy FULL, a B-szerződés tesztelve, és a DATAFLOW útja SYN-en végigjárható. Nem kész: hardcoded JSON, `NotImplementedError`, második „sim” csomag.

**WP** = work package (megvalósítási csomag ebben a tervben). Például **WP-M** az árnyék-motor (élő gén–gyógyszer párosítás a kutatási úton), **WP-H** az ehhez tartozó emberi ellenőrző tároló és API. A szereplők **P1–P6** a spec §5.1 personái (P3 = klinikai farmakológus). **HITL** = human-in-the-loop, külön ellenőrző UI, nem a laborlelet.

## Hard rules

- F1+ renderer nem kap `medications` / HIS gyógyszerlistát (FR-470 / R-021).
- Shadow store ≠ report store (külön process, külön SQLite: `var/clinical.sqlite`, `var/hitl.sqlite`, `var/kcell.sqlite`).
- Ismeretlen diplotípus = A14 küszöb alatt (allowlist).
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
| IAM | SYN `Authorization` szerep: `counsellor` `lab_signer` `clinician` `hitl_reviewer` `dpo` `gateway` | E.4, FR-470 |
| FHIR | dict Bundle STU3 (`DiagnosticReport` + `Observation`); IG v3.0.0 mezők, nem STU4 operations | B.4.3 |
| PDF | reportlab + rendszer TTF (HU) | FR-500 |
| UX | `src/pce_ui/` HTML formok a fenti API-ra (B.1: v1 labor-UI átmeneti) | FR-530 megjegyzés |

Éles TLS 1.3 / MFA / EU régió: NFR-031/032/030 — SYN-en localhost, eltérés dokumentált; nem dummy titkosítás.

---

## WP-G — Gateway (F1s) — **done / PARTIAL séma closed G12**

Gold V0 + HTTP ingest a `main`-en. G12/G13 ezen az ágon:

| ID | AC | Technológia | Oracle |
| --- | --- | --- | --- |
| G12 | GatewayEvent `id`, `received_at`, `org_id`, `payload_hash` (B.2.2) | `pipeline.stamp_gateway_event` | `test_v0_01_raw_when_cell_meets_k` |
| G13 | Practitioner / ward / meta.source törlés | `strip_pii_fr460` | `test_practitioner_and_meta_source_stripped` |
| G14 | `POST /v1/shadow/events` 202 + persist **nem** ide; persist WP-H | server már 202 | test_pipeline HTTP |

---

## WP-C — L0 consent kapu (FR-100/110/115) — **PARTIAL on this branch**

Without this the F1+ PDF is not a spec-conform product (FR-100).

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
| K6 | `PUT .../clinical-context` tárol; F1+ render **nem** olvassa | FR-220 |
| K7 | L4 log: nincs név/TAJ/születési dátum | CI scanner FR-130 |

---

## WP-N — Normalizálás (FR-250)

| ID | AC | Megjegyzés |
| --- | --- | --- |
| N1 | ATC + verziózott mapping a riport metaadatában | Gateway ATC már van; klinikai path ugyanaz a truncate, ha med listát *tárol* |
| N2 | Ismeretlen kód → `NEEDS_MAPPING` / `E-MAP-001`, nincs csendes hiányos lista | Shadow LIVE input |
| N3 | HGVS/VRS left-align | csak WP-V VCF-path |

OGYÉI gépi licence OQ-11 `[NEEDS VERIFICATION]` — SYN-en ATC WHO; nem kitalált HU törzs.

---

## WP-T — RuleSetVersion + PREPARE-12 + források (FR-310, 400-STATIC, 410-EDU)

| ID | AC | Adat |
| --- | --- | --- |
| T1 | `config_id = pgx-prepare-12@<file-version>` külső JSON, nem kód-tuple egyedül | PREPARE 12 gén a specből |
| T2 | HLA-A / NUDT15 külön config fájl | PGx-Passport opció |
| T3 | Change-control rekord konfigurációváltáskor | FR-310; FR-510 listázás P1 |
| T4 | CPIC `pair_view` + `recommendation_view` a **12 génre** (extract script, mint CYP2D6) | S043 minta |
| T5 | DPWG + FDA: hivatalos fájl/API vagy a leletben **nincs** kitalált DPWG sor; ha van forrás, mindkettő URL-lel, nincs szintetizált harmadik | FR-400-STATIC |
| T6 | EDU: hivatalos osztály-szöveg + URL, **vagy** `phenoconversion_edu: null` + TC hogy null megengedett forrás hiányában | FR-410-EDU; S043 notesonusage üres volt |
| T7 | ≥5 tiltott ha–akkor fixture → `E-EDU-001` | TC-EDU |

---

## WP-R — F1+ renderer (folytatás)

Már a `main`-en: CYP2D6 CPIC dump, INDETERMINATE, A.1/A.1.1, PDF, izoláció. Hiány:

| ID | AC | Oracle |
| --- | --- | --- |
| R8 | B.4.1 top-level: `report_id`, `case_id`, `callability_summary`, `findings[].statements[]`, `counselling`, `white_label` | séma teszt |
| R9 | Tiltott mezők reject: `functional_phenotype`, `shadow_recommendation`, `dose_mg`, `live_findings`, `hitl_*` | TC-ISO |
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

Szöveg sablon a spec/A.1 tényekből + a case mezői; nem szabadon írt klinikai tanács.

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
| M1 | Input: coarsened/raw diplotípus + ATC≤4 meds | GatewayEvent |
| M2 | Output: `live_findings[]` stratégia-kategória, **nincs** `dose_mg` | B.2.2 |
| M3 | CYP2D6 NM + paroxetin vagy fluoxetin → `genotype_phenotype=NM`, `functional_phenotype=PM` vagy `IM` a **verziózott inhibitor táblából** (hivatalos forrás, nem kitalált) | TC-PHENO-001 |
| M4 | Nincs med lista → `clinical_context=ABSENT`, nem hallgatólagos NM | FR-220/410-LIVE |
| M5 | eGFR < 30 → `reason: organ`, nem számított dózis | B.6.2 |
| M6 | Determinisztikus | NFR-060 |
| M7 | CI: `pce_report` AST-ban nincs `pce_shadow` | FR-470 |

Inhibitor tábla: CPIC/DPWG publikált lista extract; ha a sor nem forrásolható, a teszt skip helyett **fail** (nincs dummy PM).

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
| I1 | FR-470 grepek + clinician 403 + CDS 404 |
| I2 | SOUP lista: CPIC API dátum+URL, reportlab, (később PharmCAT pin) SPDX váz | REG-080 |
| I3 | OQ-01 folyamat Outboundban; nincs hamis ISO cert a gitben |
| I4 | `MATCHER_ON is False`; `LIVE_CDS is False` |
| I5 | Nincs openai/anthropic/langchain a klinikai + shadow pathen | FR-700 |

---

## WP-V — VCF út (FR-200, FR-210 gold) — matcher OFF

F1 default marad FR-240. VCF kell a missing-to-ref P0 teszthez.

| ID | AC |
| --- | --- |
| V1 | `POST /v1/cases/{id}/files` v4.2/4.3, `.vcf`/`.vcf.gz`, `##reference` GRCh37/38 | `E-VCF-003` |
| V2 | Csonka fájl → `E-VCF-001`, **nincs** részleges riport | story 20 |
| V3 | Multi-sample hozzárendelés nélkül → `E-VCF-002` | |
| V4 | > 5 GB → `E-VCF-004` | |
| V5 | ≥3 gold: missing defining position → INDETERMINATE, nem NORMAL | FR-210; PharmCAT `--absent-to-ref` **nincs** hívva |
| V6 | NamedAlleleMatcher **ki** | FR-300 / OQ-05 |

---

## WP-P1 — Spec P1 (nevesítve, nem F0 kód)

FR-230 LRI, FR-480 enciklopédia `GET /v1/encyclopedia` (nincs order-sign Card), FR-510 delta-riport, FR-530 SMART F2, FR-540 beteg-példány (OQ-13), FR-600 override séma, FR-610 teljes EN UI, FR-120 hash-chain, FR-220 FHIR medication bundle. **F2:** FR-520 fail-open 2 s, story 6–10, 21.

---

## Expliciten tilos pecsét / CE előtt

Éles HIS, `LIVE_CDS=true`, matcher ON F1+, valódi TAJ, kitalált G1/G2/C2, US F2 (OQ-17), §13 gold-set SOP, PRS (FR-430), EESZT írás (NG-05), LLM klinikai szöveg.

---

## Végrehajtási sorrend (függőség)

```
WP-C + WP-K     →  WP-R (R8–R13) + WP-T + WP-F + WP-L + WP-X
                →  WP-U (labor UX, zsákutca nélkül)
WP-G (kész)     →  WP-M → WP-H → WP-U HITL
WP-I            →  végig CI
WP-Q            →  C/K mellett
WP-N            →  M előtt (mapping)
WP-V            →  R FR-210 gold; matcher OFF
WP-P1 / F2      →  pecsét után
```

Ne másold a gateway eseményt a F1+ reportra. Ne találj ki EDU/CPIC/DPWG mondatot.

## Kész definíció — F1+ SYN demo

P4+P1 végigjárja a DATAFLOW §5 F1+ listát; FR-100 piros fixture nem gyárt PDF-et; INDETERMINATE nem NORMAL; B.4.1 JSON + PDF + STU3 Bundle; clinician HITL 403; TRACE NOW-F1+ sorok legalább PARTIAL.
