# Spec ↔ delivery plan — tételes lefedettség (P06)

| | |
| --- | --- |
| **Dátum** | 2026-08-13 |
| **Spec** | `docs/pce/PCE-SPEC-v1.2.md` **FAGYASZTVA** (§10.2) + A, B, D, E |
| **Terv** | [DELIVERY-PLAN.md](DELIVERY-PLAN.md) |
| **Adatfolyam / UX** | [DATAFLOW-AND-UX.md](DATAFLOW-AND-UX.md) |
| **Nem** | Új FR, OQ-lezárás, kitalált gyártónév, dummy guideline-szöveg |

Mérés: minden spec-tétel **FULL** / **PARTIAL** / **PLANNED** / **DEFERRED** / **NG**. A kód a 2026-08-13 `main` szerint. A terv e dokumentum után **minden NOW-tételt** nevesít Given/When/Then + B-szerződéssel.

## 1. Pontszám (kvantitatív)

| Halmaz | N | Tervben nevesítve (e doksi előtt) | Tervben nevesítve (után) | Kód FULL | Kód PARTIAL |
| --- | --- | --- | --- | --- | --- |
| FR katalógus (36) | 36 | 14 (39%) | **36 (100%)** | 0 | 15 |
| §10.2 NOW kódolható sáv | 27 | 11 (41%) | **27 (100%)** | 0 | 15 |
| User story §5.2 | 21 | 4 implicit | **21 (100%)** | 1 | 5 |
| B.2 entitás | 22 | 3 | **22 (100%)** | 0 | 4 |
| B.3 / B.4 API | 12 | 1 (`POST /v1/shadow/events`) | **12 (100%)** | 1 | 1 |
| B.5 hibakód | 22 | 3 | **22 (100%)** | 3 | 0 |
| NFR §7 | 13 | 2 | **13 (100%)** | 0 | 3 |
| REG §8 | 16 | 4 (Outbound) | **16 (100%)** | 0 | 4 |

**NOW sáv** (§10.2 F1+ mag + F1s fixture, pecsét nélkül): FR-100, 110, 115, 120, 130, 210, 220, 240, 250, 310, 400-STATIC, 400-LIVE, 410-EDU, 410-LIVE, 420 (F1+), 440, 450, 450-BLIND, 460, 461, 470, 490, 500, 610-P0, 700, 710, plusz FR-300 **kikapcsolva** (negatív). FR-200 VCF a NOW-ban *támogatott*, default FR-240.

**Kód FULL = 0** szándékos: egy FR akkor FULL, ha **minden** AC + B-szerződés + D.2 TC zöld. A gateway Gold V0 a FR-461 ATC/idő/dózis/k-cella AC-k nagy részét lefedi, de FR-460-08 GatewayEvent séma (`id`, `payload_hash`, `org_id`) hiányzik → PARTIAL.

**Terv-teljesség a NOW sávra e doksi után: 27/27 = 100%.** Kód-teljesség: 0 FULL + 15 PARTIAL / 27 ≈ **56% PARTIAL, 0% FULL** (11 NOW tétel még MISSING a kódban).

Következő kód-mérföldkő: NOW F1+ mag AC-k közül FR-100, FR-210, FR-470, FR-400-STATIC zöldek, mielőtt labor-UX SYN-demo.

---

## 2. NOW vs LATER vs NG

| Partíció | Forrás | Delivery plan |
| --- | --- | --- |
| **NOW-F1+** | §10.2 L0–L2, FR-240, 210, 310, 400-STATIC, 410-EDU, 490, 500 PDF/FHIR, 470, 700 | WP-C, K, N, T, F, R, U, X, L, Q |
| **NOW-F1s** | §10.2 440/450/450-BLIND/460/461/410-LIVE SYN | WP-G (kész), H, M |
| **LOCK** | `LIVE_CDS=true`, matcher ON F1+, MedicationEntry a rendererben, élő HIS | WP-I negatív CI |
| **LATER-P1** | FR-230, 480, 510, 530, 540, 600, 610-EN-UI, 120 hash-chain, 220 FHIR | WP-P1 |
| **LATER-F2** | FR-520 élő, SMART interruptive | pecsét + REG-011 |
| **P2 / parking** | FR-430, §13, NG-01–06, EESZT írás | nem kód |

---

## 3. FR mátrix (38 tétel)

| FR | Pri / path | Kód | Terv WP | Validáció most | Rés |
| --- | --- | --- | --- | --- | --- |
| FR-100 | Comp P0 F1+ | MISSING | **WP-C** | — | `E-CONSENT-001..005`; kapu nem kikapcsolható; riport meta tanácsadó/dátum/engedély |
| FR-110 | Comp P0 F1+ | MISSING | **WP-C** | — | gén-scope; 72 h kaszkád; 410 Gone; DeletionCertificate |
| FR-115 | Comp P0 ha ≠ ANON | MISSING | **WP-C** / H | — | ANON: nem blokkol. PSEUDO: `E-CONSENT-006` |
| FR-120 | Comp P0 F1+ | MISSING | **WP-Q** | — | append-only AuditEvent; CSV+JSON export; hash-chain **DEFERRED P1** |
| FR-130 | Comp P0 F1+ | PARTIAL | **WP-K** | gateway PII-strip | klinikai `subject_id` + külön reid store; L4 log-scanner |
| FR-200 | Prod P0 VCF | MISSING | **WP-V** | — | v4.2/4.3, GRCh37/38, 5 GB, `E-VCF-001..004`; default út FR-240 |
| FR-210 | Prod P0 | PARTIAL | **WP-R / V** | OC INDETERMINATE | ≥3 missing-to-ref VCF gold; PARTIAL/NOT_TESTED; PharmCAT flag vakon tilos |
| FR-220 | P0 F1s; F1+ nem L4 | PARTIAL | **WP-K / M** | report flag `false` | lista a case-en tárolható; renderer nem olvassa; shadow `clinical_context=ABSENT` |
| FR-230 | P1 | — | **WP-P1** | — | DEFERRED |
| FR-240 | Prod P0 | PARTIAL | **WP-K** | JSON fájl CLI | `POST /v1/cases/{id}/outside-calls` JSON+TSV; `E-CALL-001`; `W-CALL-010` |
| FR-250 | Prod P0 | PARTIAL | **WP-N** | ATC truncate | HGVS/VRS VCF-path; OGYÉI `E-MAP-001`; verzió a riportban |
| FR-300 | Prod P0 VCF; F1 OFF | LOCK | **WP-I** | MATCHER_ON false | F1+ ON tilos |
| FR-310 | Prod P0 | PARTIAL | **WP-T** | PREPARE-12 tuple | külső `pgx-prepare-12@v`; change-control |
| FR-400-STATIC | Prod P0 F1+ | PARTIAL | **WP-T / R** | CYP2D6 CPIC 79+1316 | többi PREPARE-12 gén; DPWG+FDA; B.4.1 `findings[]` |
| FR-400-LIVE | P0 F1s | MISSING | **WP-M** | — | diplotípus+MedicationEntry → live_findings; nincs FK Report-ra |
| FR-410-EDU | Prod P0 F1+ | PARTIAL | **WP-T / R** | token tiltás; EDU=null | forrásolt bekezdés vagy indokolt null; ≥5 ha–akkor gold; `E-EDU-001` |
| FR-410-LIVE | P0 F1s | MISSING | **WP-M** | — | paroxetin/fluoxetin NM→PM/IM; nincs dose_mg |
| FR-420 | P0 F1+ struktúra | MISSING | **WP-R** | — | génenként tagolt tábla; CRITICAL ≠ csere-utasítás |
| FR-430 | P2 | NG | — | — | nem épül |
| FR-440 | P0 F1s | MISSING | **WP-H** | — | aszinkron 202; HIS nem vár; config_id |
| FR-450 | P0 F1s | MISSING | **WP-H / U** | — | `hitl_reviewer` ≠ clinician; opák kártya; reason_code |
| FR-450-BLIND | P1; §10.2 SYN igen | MISSING | **WP-H** | — | 2 lépés, immutábilis vak döntés |
| FR-460 | Comp P0 F1s | PARTIAL | WP-G | Gold V0 PII | GatewayEvent `id/org_id/payload_hash`; Practitioner/meta |
| FR-461 | Comp P0 F1s | PARTIAL | WP-G | TC-GW nagy része | 460-08 séma; monitor SYN org |
| FR-470 | Comp P0 | PARTIAL | **WP-I** | LIVE_CDS; grep | clinician 403 `E-ISO-001`; CDS 404 `E-ISO-002`; tiltott JSON mezők |
| FR-480 | P1 | — | **WP-P1** | — | DEFERRED |
| FR-490 | Comp P0 | PARTIAL | WP-R | A.1/A.1.1 | minden PDF oldal; FHIR description; nem kapcsolja ki FR-100-at |
| FR-500 | Prod P0 | PARTIAL | **WP-F / R** | JSON+PDF | B.4.1 mezők; STU3 Bundle; white-label; callability_summary |
| FR-510 | P1 | — | **WP-P1** | — | DEFERRED |
| FR-520 | P0 F2; tilos F1+ | LOCK | **WP-I** | — | endpoint nincs; `E-ISO-002` |
| FR-530 | P1 F2 | — | **WP-P1** | — | v1 labor-UI = WP-U (B.1 átmeneti) |
| FR-540 | P1 | — | **WP-P1** | — | OQ-13 |
| FR-600 | P1 | — | **WP-P1** | — | HITL DISAGREE napló előkészítés H-ban |
| FR-610 | Comp P0 HU | PARTIAL | **WP-L** | HU A.1.1 | CPIC EN + „nincs lektorált HU” jelölés; nem LLM |
| FR-700 | Comp P0 | PARTIAL | WP-I | CI grep | klinikai call-graph |
| FR-710 | Comp P0 | MISSING | **WP-X** | — | determinisztikus HU magyarázat; nem SHAP |

---

## 4. User story mátrix (§5.2)

| # | Persona | Terv | Status | Spec |
| --- | --- | --- | --- | --- |
| 1 | P1 riport egy művelettel | WP-U + K + R | PARTIAL (CLI) | FR-240, 400-STATIC, 500 |
| 2 | P1 guideline-verzió | WP-T + F | PARTIAL | FR-310, 500 |
| 3 | P1 hiányzó gén | WP-R / V | PARTIAL | FR-210 |
| 4 | P1 white-label + aláíró | WP-F + U | MISSING | FR-500, REG-020 |
| 5 | P1 újragenerálás | WP-P1 | DEFERRED | FR-510 |
| 6–10 | P2 felírási riasztás | LOCK | DEFERRED F2 | FR-520; NG-07 |
| 11–12 | P3 fenokonverzió HITL/F2 | WP-M + H | PLANNED SYN | FR-410-LIVE |
| 13 | P4 tanácsadás kapu | WP-C + U | MISSING | FR-100 |
| 14 | P4 gén-hozzájárulás | WP-C | MISSING | FR-110 |
| 15 | P5 visszavonás tanúsítvány | WP-C | MISSING | FR-110 |
| 16 | P5 audit export | WP-Q | MISSING | FR-120 |
| 17 | P6 FHIR/CDS | WP-F; CDS LOCK | PARTIAL | B.4.3; FR-520 tilos |
| 18 | P6 MDR határ | Outbound OQ-03 | PLANNED irat | REG-020/021 |
| 19 | nincs PGx explicit | WP-U / I | PLANNED | story 19 |
| 20 | csonka VCF | WP-V | PLANNED | `E-VCF-001` |
| 21 | CDS ne blokkoljon | WP-G fail-open | PARTIAL | E.2; FR-520 |

---

## 5. Entitás- és API-mátrix (B.2–B.4)

| Entitás / szerződés | Path | Terv | Kód |
| --- | --- | --- | --- |
| Organization | klinikai | WP-K | MISSING |
| Subject + reid_key_ref | klinikai | WP-K | MISSING |
| Case | klinikai | WP-K | MISSING |
| CounsellingRecord | klinikai | WP-C | MISSING |
| ConsentRecord | klinikai | WP-C | MISSING |
| Sample | klinikai | WP-C | MISSING |
| GenomicFile | klinikai | WP-V | MISSING |
| OutsideCall | klinikai | WP-K | PARTIAL |
| Diplotype / Phenotype | klinikai | WP-K | PARTIAL |
| MedicationEntry / LabObservation | nem L4 F1+ | WP-K | MISSING |
| RuleSetVersion | klinikai | WP-T | PARTIAL |
| Report | klinikai | WP-F | PARTIAL |
| AuditEvent | klinikai | WP-Q | MISSING |
| Explanation | klinikai | WP-X | MISSING |
| DeletionCertificate | klinikai | WP-C | MISSING |
| GatewayEvent | shadow | WP-G / H | PARTIAL |
| ResearchConsent | shadow PSEUDO | WP-C | MISSING |
| ShadowInference | shadow | WP-M / H | MISSING |
| HitlReview | shadow | WP-H | MISSING |
| BuildFlag LIVE_CDS | mindkettő | WP-I | FULL false |
| `POST /v1/cases/{id}/files` | B.3.1 | WP-V | MISSING |
| `POST /v1/cases/{id}/outside-calls` | B.3.2 | WP-K | MISSING |
| `PUT /v1/cases/{id}/clinical-context` | B.3.3 | WP-K | MISSING |
| `POST /v1/hl7/oru` | B.3.4 P1 | WP-P1 | DEFERRED |
| `POST /v1/shadow/events` | B.3.5 | WP-G | PARTIAL |
| `GET /v1/cases/{id}/reports/{rid}` | B.4.1 | WP-F | MISSING |
| PDF oldalmeta | B.4.2 | WP-F / R | PARTIAL |
| FHIR STU3 Bundle | B.4.3 | WP-F | MISSING |
| CDS Hooks | B.4.4 | WP-I 404 | LOCK |
| `GET /v1/encyclopedia` | B.4.5 P1 | WP-P1 | DEFERRED |
| `/v1/hitl/**` | B.4.6 | WP-H | MISSING |

---

## 6. Hibakatalógus (B.5) — UX

| Kód | Terv | Kód most | UX |
| --- | --- | --- | --- |
| E-CONSENT-001..005 | WP-C | — | Labor UI: riport gomb + HU indok |
| E-CONSENT-006 | WP-C/H | — | PSEUDO: nincs HITL sor |
| E-VCF-001..004 | WP-V | — | nincs részleges PDF |
| E-CALL-001, W-CALL-010 | WP-K | — | W-* nem csendes siker |
| E-MAP-001 | WP-N | — | `NEEDS_MAPPING` |
| E-CALLABILITY | WP-R | PARTIAL | INDETERMINATE a leleten |
| E-GONE-010 | WP-C | — | 410 |
| E-SHADOW-001..003 | WP-G | PARTIAL | HIS fail-open |
| E-ISO-001, E-ISO-002 | WP-I | — | 403 / 404 |
| E-EDU-001 | WP-R | PARTIAL | 422 tiltott formula |
| E-TIMEOUT-CDS | F2 | DEFERRED | felírás nem blokkol |

---

## 7. NFR / REG

| ID | Terv | Megjegyzés |
| --- | --- | --- |
| NFR-010 | WP-V után mérés | F0 WES nélkül nem kapu |
| NFR-011 | F2 | DEFERRED |
| NFR-020 | üzem | nem F0 feature |
| NFR-030 | WP-K | EU tenancy; DPA = REG-050 |
| NFR-031 | SYN HTTP eltérés dokumentált | éles TLS 1.3 |
| NFR-032 | WP-Q | SYN szerepek; MFA éles |
| NFR-033 | WP-I | gitleaks CI |
| NFR-040 | WP-Q | = FR-120 |
| NFR-050 | P2 | DEFERRED |
| NFR-060 | WP-X + R | bitre azonos JSON |
| NFR-070 | CI | klinikai út 100% WP-C után |
| NFR-080 | QMS | nem F0 feature |
| NFR-090 | P1 | DEFERRED |
| REG-010 | A melléklet | irat |
| REG-011 | F2 | DEFERRED |
| REG-020/021 | OQ-03 | irat; WP-U aláíró slot |
| REG-030/031 | F2 QMS | DEFERRED kód |
| REG-040a | C + OQ-01 | 2026-09-30 |
| REG-040b | NG-05 | nem F1 |
| REG-050/090/091 | OQ-16/15 | pecsét élő HIS-hez |
| REG-060 | P1 | DEFERRED |
| REG-061 | QMS | AI literacy napló |
| REG-070 | enterprise | DEFERRED |
| REG-080 | WP-I | CPIC pin + reportlab; PharmCAT ha WP-V |

---

## 8. Korábbi terv részei (lezárva e doksiban)

A 2026-08-13 terv WP-G + vékony R/H/I volt. A B.1 klinikai lánc (L0→L6) hiányzott: a renderer CLI PDF-et ír consent-kapu nélkül — ez **ellentétes** FR-100-zal, ha labor-termékként használják.

| Rés | Spec | Új WP |
| --- | --- | --- |
| Nincs Case/Consent, mégis PDF | FR-100 | WP-C, WP-K: render csak kapu után |
| JSON nem B.4.1 | FR-500 | WP-F |
| Nincs FHIR STU3 | FR-500 | WP-F |
| CYP2D6-only, nincs DPWG/FDA | FR-400-STATIC | WP-T |
| EDU null | FR-410-EDU, FR-610 | lásd alább |
| Nincs 6. § (6) magyarázat | FR-710 | WP-X |
| HITL váz, nincs motor | FR-400-LIVE, 410-LIVE, 440–450 | WP-M, H |
| Nincs IAM | FR-470, E.4 | WP-Q, U |
| VCF gold ≥3 | FR-210 | WP-V, matcher OFF |

**FR-410-EDU (forrásolt, nem kitalálás):** A CPIC `guideline.notesonusage` 2026-08-13-án üres volt a CYP2D6 rekordokon (S043). A spec: a lelet *tartalmazhat* EDU bekezdést. Ha nincs forrásolt szöveg → `phenoconversion_edu = null` **megfelel**, TC-EDU-001: null ≠ kitalált bekezdés; tiltott token CI marad. Hivatalos osztály-szöveg később WP-T + URL.

---

## 9. P06 újrafuttatás

WP **VERIFIED**, ha: (1) érintett NOW-sorok PARTIAL vagy FULL; (2) a DATAFLOW-AND-UX.md útja SYN-en végigjárható; (3) érintett B.5 kódok HTTP-tesztelve; (4) F1+ `unsourced_claims == 0`; (5) FR-470 grepek zöldek.

Spec-t nem írunk.
