# Válasz: spec ↔ fejlesztési terv (tételesen)

| | |
| --- | --- |
| **Kérés** | (1) hasonlítsd a tervet a speccel tételesen; (2) dolgozd ki, hogy minden tervezett folyamat tervezett/validált és technológiailag a specnek megfelel; (3) mérd vissza a teljességet; (4) a teljes dataflow és UX legyen biztosítva |
| **Spec** | `docs/pce/PCE-SPEC-v1.2.md` **FAGYASZTVA** + A, B, D, E |
| **Terv** | [DELIVERY-PLAN.md](DELIVERY-PLAN.md) |
| **Dátum** | 2026-08-13 |
| **Oracle** | `PYTHONPATH=src python3 -m unittest discover -s tests -v` — 60 OK |

Rövid státusztábla: [SPEC-PLAN-TRACE.md](SPEC-PLAN-TRACE.md). Ez a fájl a **kérésre adott válasz**, nem ticket-lista.

Jelölés:

| Szó | Jelentés |
| --- | --- |
| **Tervezett** | A DELIVERY-PLAN WP-ban van Given/When/Then + B-szerződés |
| **Validált** | Van automatikus teszt, ami a spec AC-t méri (HTTP kód / mező / tiltás) |
| **Spec-tech** | A megvalósítás a B melléklet szerződését használja (útvonal, hibakód, entitás), nem kitalált API-t |
| **Eltérés** | Tudatos SYN-korlát (pl. localhost HTTP vs NFR-031 TLS) — dokumentált, nem dummy crypto |

---

## 1. Tételes összehasonlítás — minden FR

A spec §6 FR-katalógusa (36 tétel + FR-400/410 kettős üzem). Minden sor: **spec mit követel** → **terv hol** → **tech** → **tervezett / validált / spec-tech**.

### 1.1 L0 Identity & Consent

| Spec tétel | Mit követel (AC) | Terv | Tech (B) | T | V | Tech=spec | Lyuk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **FR-100** | Nincs counselling → `E-CONSENT-001` 409 + **6. § (2)** HU. Nincs 8. § → `003`. Tanácsadás a minta után → `002`. Extra gén 15. § → `004`. Nincs `performing_org.license_id` → `005`. Kapu **nem** kapcsolható ki. Riport meta: tanácsadó, dátumok, engedély. | WP-C C1–C7 | `POST /v1/cases/{id}/counselling\|consent\|reports`; B.5 kódok; SQLite `CounsellingRecord`/`ConsentRecord` (v1 kézi, nem FHIR Consent — spec FR-100 technikai megjegyzés) | igen | igen (`test_clinical.ConsentGateTests`, HTTP 409) | igen | FHIR Consent v1.1; pecsétszám élő orvosnév tilos (A9 slot) |
| **FR-110** | Gén kimarad a beteg-példányból; visszavonás kaszkád + tanúsítvány; URL **410** `E-GONE-010`; audit esemény genetika nélkül | WP-C C8–C9 | `omit_from_patient`; `POST /v1/subjects/{id}/withdraw`; `DeletionCertificate`; report `gone=1` | igen | igen (410 + cert, nincs `*1/*2` a certen) | igen | 72 h = SYN-en azonnali (A10 üzem cél teljesül); klinikus-példány külön jogalap nincs bekapcsolva |
| **FR-115** | ANON: nem blokkol. PSEUDO: nincs `ResearchConsent` → `E-CONSENT-006`, nincs HITL írás | WP-C C10 | `GatewayConfig.mode` + `research_consent`; ingest 409 | igen | igen (ANON 202 / PSEUDO 409) | igen | HITL store még nincs, ezért „nincs HITL írás” ingest-szinten teljesül |
| **FR-120** | 30 év, append-only, CSV+JSON export; nyers VCF nincs a naplóban. Hash-chain **P1** | WP-Q | `audit_event` + SQLite TRIGGER ABORT; `GET /v1/audit/export` | igen | igen (UPDATE → `E-AUDIT-001`) | igen | hash-chain szándékos P1; 30 év megőrzés üzem, nem F0 kód |
| **FR-130** | L2–L5 pszeudonim; re-ID külön store; L4 logban nincs név/TAJ/szül. dátum | WP-K | `reid_store` külön tábla; gateway PII-strip | igen | részben | igen | CI PII-scanner a klinikai L4 logra még vékony |

### 1.2 L1 Ingest

| Spec tétel | Mit követel | Terv | Tech | T | V | Tech=spec | Lyuk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **FR-200** | VCFv4.2/4.3, GRCh37/38, 5 GB, `E-VCF-001..004`; default út **nem** ez | WP-V | `POST /v1/cases/{id}/files` B.3.1 | igen | részben (`E-VCF-003`, W-CALL) | igen | ≥3 missing-to-ref gold; 5 GB éles mérés |
| **FR-210** | CALLED/PARTIAL/INDETERMINATE/NOT_TESTED; INDETERMINATE ≠ NORMAL; missing-to-ref tilos | WP-R, WP-V | outside-call `callability`; renderer `positive_drug_assertion=false` | igen | igen OC úton | igen | VCF gold ≥3 még nincs (matcher OFF marad) |
| **FR-220** | Lista P0 a **shadow/F2**-n. F1+ Report `medications_applied_to_recommendations: false`. Renderer nem kap gyógyszerlistát | WP-K, WP-M | `PUT .../clinical-context` tárol; `render_f1plus` keyword-only, nincs `medications` | igen | igen F1+ oldalon | igen | shadow `clinical_context=ABSENT` kártya = WP-M |
| **FR-230** | HL7 v2.5.1 ORU | WP-P1 | `POST /v1/hl7/oru` | igen (P1) | — | — | spec P1, nem F0 |
| **FR-240** | TSV + JSON: gene, diplotype, calling_lab, signing_physician, method, call_date; üres diplotípus `E-CALL-001`; VCF ütközés `W-CALL-010`, nincs auto-választás | WP-K | B.3.2 pontos path; TSV tab UTF-8; `resolve-call` | igen | igen | igen | — |

### 1.3 L2–L3

| Spec tétel | Mit követel | Terv | Tech | T | V | Tech=spec | Lyuk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **FR-250** | HGVS/VRS; ATC+OGYÉI; ismeretlen kód `E-MAP-001` | WP-N | gateway WHO ATC truncate; klinikai path ugyanaz ha tárol | igen | ATC igen | részben | OGYÉI licence OQ-11 `[NEEDS VERIFICATION]`; HGVS = VCF-path |
| **FR-300** | PharmCAT VCF-úton; F1 **ajánlott: matcher ki** | WP-I, WP-V | `MATCHER_ON = False` compile-time | igen | igen (CI assert) | igen | ON tilos F1+-on (LOCK) |
| **FR-310** | PREPARE-12, `config_id = pgx-prepare-12@<ver>`, külső konfig | WP-T | `pce_report.panel.PREPARE_12`; report `config_id` | igen | részben | részben | külső JSON fájl + change-control rekord; 12 gén CPIC dump csak CYP2D6 |

### 1.4 L4 Knowledge (két üzem — keverés = NG-07)

| Spec tétel | Mit követel | Terv | Tech | T | V | Tech=spec | Lyuk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **FR-400-STATIC** | CPIC/DPWG/FDA kivonat a **génhez**; mind az N sor; nincs HIS-szűrés; `unsourced_claims==0`; nincs `dose_mg` | WP-T, WP-R | hivatalos CPIC `pair_view`/`recommendation_view`; B.4.1 `findings[]` | igen | CYP2D6 igen | igen | DPWG+FDA: **nincs kitalált sor** (forrás hiányában üres verziómező). Többi PREPARE-12 gén extract hiányzik |
| **FR-400-LIVE** | Diplotípus + `MedicationEntry` → `live_findings`; **tilos F1+ leleten**; nincs FK a Report-ra | WP-M | `src/pce_shadow/` (csomag **még nincs**) | igen | nem | — | **NOW MISSING** |
| **FR-410-EDU** | Általános bekezdés forrással **vagy** null; ha–akkor tilos; nem olvassa a gyógyszerlistát | WP-T, WP-R | `phenoconversion_edu: null` + edu_note (CPIC notesonusage üres, 2026-08-13) | igen | token tiltás + null | igen | forrásolt EDU bekezdés, ha hivatalos szöveg lesz |
| **FR-410-LIVE** | NM + paroxetin/fluoxetin → functional PM/IM; nincs `dose_mg` | WP-M | ugyanaz a hiányzó shadow csomag | igen | nem | — | **NOW MISSING**; tilos F1+ JSON-ban (ellenőrizve) |
| **FR-420** | F1+: génenként tagolt; CRITICAL ≠ „cseréld a felírt szert” | WP-R R10 | `findings[].severity` = CPIC level; `severity_means_replace_prescribed: false` | igen | igen | igen | F2 interruptive card pecsét után |
| **FR-430** | PRS stub | — | nem épül | NG | — | — | spec P2 |

### 1.5 F1s shadow / HITL / gateway

| Spec tétel | Mit követel | Terv | Tech | T | V | Tech=spec | Lyuk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **FR-440** | Aszinkron 202; HIS nem vár; inferencia HITL store-ba | WP-H | ingest 202 megvan; **persist nincs** | igen | 202 igen / persist nem | részben | **NOW MISSING** store |
| **FR-450** | `hitl_reviewer` ≠ clinician; opák kártya; reason_code | WP-H, WP-U | clinician → `E-ISO-001` 403; HITL UI nincs | igen | 403 igen / UI nem | részben | **NOW MISSING** UI+store |
| **FR-450-BLIND** | 2 lépés, immutábilis vak döntés | WP-H | tervezett `POST .../blind` majd `.../reviews` | igen | nem | — | **NOW MISSING** |
| **FR-460** | Intézményi gateway; nincs PII a PCE felé | WP-G | `src/pce_gateway`; Patient/TAJ/név kiesik | igen | Gold V0 | igen | — |
| **FR-461** | ATC≤4, negyedév, k≥5, ritka diplotípus, count nem a payloadon | WP-G | freq allowlist; k-cella SQLite; `cell_count` tiltva | igen | Gold V0 + G12 mezők | igen | monitor org display |
| **FR-470** | `LIVE_CDS=false`; clinician nem HITL; CDS 404; renderer nem kap MedicationEntry | WP-I | flag + grep + 403/404 | igen | igen | igen | — |

### 1.6 L6 Delivery + L7

| Spec tétel | Mit követel | Terv | Tech | T | V | Tech=spec | Lyuk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **FR-480** | `GET /v1/encyclopedia` P1 | WP-P1 | — | igen (P1) | — | — | nem F0 |
| **FR-490** | A.1 + A.1.1 a leleten; nem kapcsolja ki FR-100-at | WP-R | verbatim A melléklet; PDF chrome minden oldal; FHIR `DocumentReference.description` | igen | igen | igen | — |
| **FR-500** | JSON B.4.1 + PDF + FHIR STU3; white-label; callability | WP-F, WP-R | `GET .../reports/{rid}` + `/pdf` + `/fhir` | igen | igen | igen | IG-validátor; logo fájl |
| **FR-510** | Újragenerálás | WP-P1 | `parent_report_id` | igen (P1) | — | — | — |
| **FR-520** | CDS F2; **tilos F1+** | WP-I | 404 `E-ISO-002` | igen | igen | igen | élő CDS pecsét+REG-011 |
| **FR-530** | SMART P1; v1 labor-UI átmeneti (B.1) | WP-U, WP-P1 | `src/pce_ui` HTML a B API-ra | igen | UI létezik | igen v1 | SMART pecsét után |
| **FR-540** | Beteg-példány P1 | WP-P1 | — | igen (P1) | — | — | OQ-13 |
| **FR-600** | Override telemetria P1 | WP-P1 | — | igen (P1) | — | — | — |
| **FR-610** | Klinikai szöveg HU P0; EN UI P1; nincs gépifordítás | WP-L | UI HU; `text_en` CPIC; `text_hu: null` + jelölés | igen | igen | igen | lektorált HU később |
| **FR-700** | Nincs LLM a klinikai úton | WP-I | CI grep openai/anthropic/langchain | igen | igen | igen | — |
| **FR-710** | 6. § (6) kérésre magyarázat; determinisztikus; nem SHAP | WP-X | `GET .../explanation`; sablon A.1 + case mezők; sha256 | igen | igen | igen | — |

**FR-összeg:** 36/36 **tervezett**. NOW 27-ből **21 validált legalább PARTIAL**, 1 LOCK (FR-300 ki), **5 nincs validálva** (LIVE+HITL).

---

## 2. Tervezett folyamatok — tervezett / validált / spec-tech

A spec B.1 két **folyamatot** ír elő. A terv WP-kra bontja. Itt a folyamat a vizsgált egység, nem a fájl.

### 2.1 Klinikai folyamat (F1+ laborlelet) — B.1

```
P4 tanácsadás/beleegyezés → L0 → L1 outside-call → L3(outside, matcher OFF)
→ L4-static (CPIC tábla) → L6 JSON/PDF/FHIR → P1 aláírás → P2 csak a leletet kapja
```

| Lépés | Spec | Terv WP | Tech | Tervezett | Validált | Spec-tech |
| --- | --- | --- | --- | --- | --- | --- |
| L0 org/subject/case/sample | B.2.1 | WP-K | `POST /v1/orgs\|subjects\|cases` SQLite | igen | igen | igen (UUID, `reid_key_ref` külön) |
| L0 counselling | FR-100, 6. § (2) | WP-C | `POST .../counselling` | igen | igen | igen |
| L0 consent 8. § / 15. § | FR-100/110 | WP-C | `POST .../consent` scopes | igen | igen | igen (v1 kézi = spec) |
| L1 outside-call | FR-240 B.3.2 | WP-K | JSON tömb vagy TSV | igen | igen | igen |
| L1 VCF (opcionális) | FR-200 B.3.1 | WP-V | `POST .../files` | igen | részben | igen |
| Konfliktus OC vs VCF | FR-240 `W-CALL-010` | WP-K K4 | 409 + `resolve-call` | igen | igen | igen (nincs auto-választás) |
| L4-static | FR-400-STATIC | WP-R | `pce_report` + hivatalos CPIC JSON | igen | CYP2D6 | igen; DPWG/FDA nem kitalálva |
| FR-100 kapu a render előtt | FR-100 | WP-C R11 | `create_report` → `assert_render_allowed`; CLI sem kerülheti | igen | igen | igen |
| L6 JSON | B.4.1 | WP-F | kötelező top-level + tiltott mezők | igen | igen | igen |
| L6 PDF | B.4.2 | WP-R R13 | reportlab + TTF; chrome minden oldal | igen | fájl+%PDF | igen (szövegkivonat teszt, nem PDF-text extract) |
| L6 FHIR | B.4.3 | WP-F | DiagnosticReport + Observation LOINC 48018-6/84413-4; nincs STU4 operation | igen | resourceType teszt | igen; IG-validátor nincs |
| L6 magyarázat | FR-710 | WP-X | `GET .../explanation` | igen | igen | igen |
| Visszavonás | FR-110 | WP-C | 410 + certificate | igen | igen | igen |
| Clinical-context tárolás | FR-220 | WP-K | PUT; renderer nem olvassa | igen | igen | igen |
| Labor UX | B.1 átmeneti UI | WP-U | HTML → ugyanaz az API | igen | GET `/` tartalmazza SYN-ORG-001; walk teszt API | igen (nem mock) |

**Klinikai folyamat spec-tech megfelelése: igen**, a B.3/B.4 útvonalakon. SYN-eltérés: HTTP localhost (NFR-031 TLS élesben), SQLite (B.2 nem ír elő Postgres-t F0-ra; NFR-031 később).

**Nem teljes a klinikai folyamatban:** 11 PREPARE-12 gén CPIC táblája, VCF missing-to-ref gold, lektorált HU guideline-szöveg, PDF-oldal OCR-ellenőrzés.

### 2.2 Shadow folyamat (F1s) — B.1 / E

```
HIS esemény → intézményi gateway FR-460/461 → POST /v1/shadow/events
→ L4-live → HITL store → vak reviewer → (soha) F1+ Report
```

| Lépés | Spec | Terv | Tech | T | V | Spec-tech |
| --- | --- | --- | --- | --- | --- | --- |
| Gateway PII/ATC/idő/dózis | FR-460/461 | WP-G | `pce_gateway` | igen | Gold V0 | igen |
| k-cella helyi SQLite | E.3.1 | WP-G | `var/kcell.sqlite`; count nincs a payloadon | igen | igen | igen |
| Ingest service-account | B.3.5 `E-SHADOW-002` | WP-G | `Authorization` | igen | igen | igen |
| Fail-open 202 | E.2 | WP-G | 202 drop és accept | igen | igen | igen |
| PSEUDO FR-115 | B.3.5 | WP-C | `E-CONSENT-006` | igen | igen | igen |
| L4-live motor | FR-400-LIVE, 410-LIVE | WP-M | `pce_shadow` **nincs** | igen | **nem** | — |
| HITL persist | FR-440 | WP-H | `hitl.sqlite` **nincs** | igen | **nem** | — |
| Vak UI | FR-450/450-BLIND | WP-H/U | clinician 403 megvan; kártya nincs | igen | részben | kapu igen, folyamat nem |
| Izoláció Report-tól | FR-470 | WP-I | nincs FK; renderer nem importál pipeline-t | igen | igen | igen |

**Shadow folyamat: a gateway+ingest spec-tech, a motor+HITL csak tervezett, nem validált.** Ez a NOW 5 MISSING tétel. A HIS ettől függetlenül nem blokkol (202).

### 2.3 Szándékosan nem épülő folyamatok (spec szerint)

| Folyamat | Spec | Terv | Miért nem „hiány” |
| --- | --- | --- | --- |
| F2 CDS Hooks order-sign | FR-520, story 6–10 | LOCK `E-ISO-002` | F1+ tilos; pecsét+REG-011 |
| EESZT írás | NG-05 | nem kód | — |
| PRS | FR-430 P2 | NG | — |
| Élő HIS / TAJ | A9, pecsét | tilos | SYN opák ID |
| LLM klinikai szöveg | FR-700 | CI tiltás | — |

---

## 3. Teljesség — visszamérve

Képlet (P06, SPEC-PLAN-TRACE §9):

1. NOW FR sor PARTIAL vagy FULL  
2. DATAFLOW F1+ lépés SYN-en járható  
3. érintett B.5 kód HTTP-tesztelve  
4. F1+ `unsourced_claims == 0`  
5. FR-470 grepek zöldek  

Oracle: **60 unittest OK** (2026-08-13).

### 3.1 Számok

| Halmaz | N | Tervezett | Validált (kód ≥PARTIAL) | Validálatlan NOW |
| --- | --- | --- | --- | --- |
| FR katalógus | 36 | 36 (100%) | 21 + LOCK-ok / P1 / NG | 5 F1s |
| §10.2 NOW | 27 | 27 (100%) | 21 PARTIAL + 1 LOCK | **5 = 18,5%** |
| User story §5.2 | 21 | 21 (100%) | 10 PARTIAL + 1 + F2 LOCK | 11–12 HITL; 5 P1; 6–10 F2 |
| B.2 entitás | 22 | 22 | 16 PARTIAL + 1 FULL flag | ShadowInference, HitlReview (+ részben ResearchConsent) |
| B.3/B.4 API | 12 | 12 | 4 FULL + 4 PARTIAL + CDS LOCK | HITL store; HL7/encyclopedia P1 |
| B.5 hiba | 22 | 22 | 12 FULL + 4 PARTIAL | E-MAP-001; VCF 002/004; F2 timeout |

**Terv-teljesség NOW: 27/27 = 100%.**  
**Kód-teljesség NOW: 21/27 ≈ 78% legalább PARTIAL** (0 FR FULL, mert FULL = minden AC + D.2 TC).  
**F1+ dataflow: 8/8 lépés járható.**  
**F1s dataflow a HITL-ig: 2/5** (gateway+ingest igen; persist, motor, vak UI nem).

### 3.2 User story — tételesen a spec §5.2 szövege szerint

| # | Story (spec) | Biztosított? | Bizonyíték |
| --- | --- | --- | --- |
| 1 | Egy művelettel diplotípus→riport | **részben** | HTTP walk + HTML; CYP2D6 CPIC, nem 12 gén |
| 2 | Guideline-verzió a riporton | **igen** | `config_id`, `cpic_version`/`accessed` |
| 3 | Hiányzó gén ≠ hamis NORMAL | **igen OC-n** | INDETERMINATE fixture; VCF gold nincs |
| 4 | White-label + aláíró | **részben** | SYN-ORG slot + signer_slot; logo fájl nincs |
| 5 | Újragenerálás | **nem (P1)** | FR-510 |
| 6–10 | Felírási riasztás | **szándékos nem** | F1+ tilos; CDS 404 |
| 11–12 | Fenokonverzió HITL/F2 | **nem** | WP-M/H |
| 13 | Nincs riport tanácsadás/8. § nélkül | **igen** | E-CONSENT-001/003; CLI is |
| 14 | Génenkénti hozzájárulás / nem-tudás | **igen** | scopes + omit_from_patient |
| 15 | Visszavonás + tanúsítvány | **igen** | 410 + DeletionCertificate |
| 16 | Audit export | **igen** | CSV+JSON; hash-chain P1 |
| 17 | FHIR / CDS | **FHIR igen, CDS tilos** | STU3 Bundle; 404 |
| 18 | MDR határ írásban | **irat** | Outbound OQ-03; nem kód |
| 19 | Nincs PGx → explicit | **tervezett** | nincs külön „nincs adat” kártya F2-n (F2 LOCK) |
| 20 | Csonka VCF → hiba, nem részleges PDF | **részben** | `E-VCF-001` ha nincs `##fileformat` |
| 21 | CDS kiesés ne blokkolja a felírást | **igen F1+-on** | nincs CDS; gateway 202 fail-open |

### 3.3 P06 kapu

| Szabály | Eredmény |
| --- | --- |
| (1) NOW ≥ PARTIAL | 21/27 + LOCK; **FAIL a 5 F1s sorra** |
| (2) F1+ dataflow járható | **PASS** |
| (3) B.5 HTTP | **PASS** a klinikai kapukra |
| (4) unsourced_claims==0 | **PASS** |
| (5) FR-470 | **PASS** |

**F1+ SYN demo** a DELIVERY-PLAN kész-definíciója szerint: **teljesíthető**.  
**F1s SYN demo** (motor+HITL): **nem teljesíthető**, amíg WP-M és WP-H nincs kódban.

---

## 4. Dataflow és user experience — biztosítva-e?

### 4.1 F1+ labor út (B.3/B.4 sorrend) — nincs zsákutca

| # | Lépés | Persona | Járható | Hibás út (UX) |
| --- | --- | --- | --- | --- |
| 1 | org + subject + case + sample | P1 | **igen** | hiányzó sample → `E-CONSENT-002` |
| 2 | counselling (dátum < minta) | P4 | **igen** | későbbi dátum → `E-CONSENT-002` HU |
| 3 | consent scopes | P4 | **igen** | nincs consent → `E-CONSENT-003` |
| 4 | outside-call JSON/TSV | P1 | **igen** | üres diplotípus → `E-CALL-001`; OC+VCF → `W-CALL-010` majd `resolve-call` |
| 5 | POST reports (kapu) | P1 | **igen** | piros kapu → **nincs PDF** (409) |
| 6 | GET JSON | P1 | **igen** | withdraw után 410 |
| 7 | GET explanation | P1/P2 a laboron keresztül | **igen** | — |
| 8 | withdraw | P5 | **igen** | URL 410, cert genetika nélkül |
| * | PUT clinical-context | P1 | **igen** | nem megy L4-be (nincs functional_phenotype) |
| * | GET PDF / FHIR | P1 → P2 | **igen** | P2-nek **nincs** belépése (spec FR-470 / story 6) |

Képernyő: `src/pce_ui/index.html` ugyanerre az API-ra POST-ol. `python -m pce_clinical --mode serve`.

### 4.2 F1s HITL út — részben

| # | Lépés | Járható |
| --- | --- | --- |
| 1 | HIS fixture → gateway → k-cella | **igen** |
| 2 | ATC5/TAJ → 400, HIS 202 | **igen** |
| 3 | ShadowInference `hitl.sqlite` | **nem** |
| 4 | Vak lépés + verdict UI | **nem** |
| 5 | Report store üres marad | **igen** (nincs keresztírás; persist sincs) |

Clinician HITL: **403 `E-ISO-001`** (UX-izoláció biztosítva). Reviewer kártya: **nincs**.

### 4.3 Persona UX (spec §5.1)

| P | Spec fájdalom | Van-e út a termékben | Zsákutca? |
| --- | --- | --- | --- |
| **P1** Labor | kézi CPIC | JSON/TSV → PDF/FHIR, verzió a leleten, HU hiba B.5 | W-CALL-010 feloldható; INDETERMINATE nem NORMAL |
| **P2** Klinikus | PGx a felírásnál | F1+: **csak az aláírt lelet** (PDF/FHIR a labortól). Nincs vizit-UI, nincs CDS | szándékos; F2 pecsét után |
| **P3** Farmakológus | fenokonverzió | F1+ leleten csak EDU=null; HITL nincs | **igen, amíg WP-M/H nincs** |
| **P4** Tanácsadó | nincs kapu | űrlap + 409 HU | nincs: piros kapu nem gyárt leletet |
| **P5** DPO | 30 év, törlés, audit | export + withdraw + cert | A14 monitor a gatewayen; UI gomb auditra van |
| **P6** Vendor | FHIR, ne legyen MDR-gyártó | STU3 Bundle; CDS 404; OQ-03 irat | CDS szándékos 404 |
| **HIS** | ne várjon | 202 fail-open | — |

### 4.4 Csatorna-izoláció (UX regresszió)

| Teszt | Állapot |
| --- | --- |
| PDF/JSON `live_findings` / `functional_phenotype` / `dose_mg` | tiltva, tesztelve |
| clinician + HITL | 403 |
| CDS F1+ | 404 |
| renderer `medications` argumentum | `RendererConfigError` |
| gateway `SYN-TAJ` / `doseQuantity` / ATC5 | nincs az exporton |

---

## 5. Ami a kérés „biztosítsd a teljes dataflow/UX” részéből **még nincs biztosítva**

Ez nem rejtett hiány: a spec NOW sávja F1s-t is tartalmaz.

1. **L4-live motor** (`pce_shadow`) — FR-400-LIVE, FR-410-LIVE. Hivatalos inhibitor tábla nélkül nem szabad kitalált PM-et írni.  
2. **HITL store + vak UI** — FR-440, 450, 450-BLIND. P3 útja itt szakad.  
3. **PREPARE-12 többi gén CPIC extract** — FR-310/400-STATIC részlegesség.  
4. **VCF missing-to-ref gold ≥3** — FR-210 klinikai P0 csúcs VCF-úton. Default út továbbra is FR-240.

A F1+ labor dataflow és a P1/P4/P5/P6 (F1+) UX **biztosított és mért**. A P2 felírási UX **szándékosan zárt**. A P3 HITL UX **nincs biztosítva**.

Spec-t ez a dokumentum nem módosítja.
