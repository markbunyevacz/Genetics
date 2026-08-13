# Spec ↔ delivery plan — tételes lefedettség (P06)

**Olvasható válasz a kérés négy pontjára:** [VALASZ-SPEC-TERV.md](VALASZ-SPEC-TERV.md) (összehasonlítás, folyamatok T/V/tech, mért számok, dataflow/UX). Ez a fájl a státusztábla.

| | |
| --- | --- |
| **Dátum** | 2026-08-13 (P06s: klinikai kapu kód után) |
| **Spec** | `docs/pce/PCE-SPEC-v1.2.md` **FAGYASZTVA** (§10.2) + A, B, D, E |
| **Terv** | [DELIVERY-PLAN.md](DELIVERY-PLAN.md) |
| **Adatfolyam / UX** | [DATAFLOW-AND-UX.md](DATAFLOW-AND-UX.md) |
| **Oracle** | `PYTHONPATH=src python3 -m unittest discover -s tests -v` — **60 OK** (2026-08-13) |
| **Nem** | Új FR, OQ-lezárás, kitalált gyártónév, dummy guideline-szöveg |

Mérés: minden spec-tétel **FULL** / **PARTIAL** / **PLANNED** / **DEFERRED** / **NG**. A kód a 2026-08-13 `cursor/pce-clinical-gates-3690` szerint. A terv **minden NOW-tételt** nevesít Given/When/Then + B-szerződéssel.

## 1. Pontszám (kvantitatív)

| Halmaz | N | Tervben nevesítve | Kód FULL | Kód PARTIAL | Kód MISSING (NOW) |
| --- | --- | --- | --- | --- | --- |
| FR katalógus (36) | 36 | **36 (100%)** | 0 | **21** | 5 NOW + P1/NG |
| §10.2 NOW kódolható sáv | 27 | **27 (100%)** | 0 | **21** + 1 LOCK (FR-300) | **5** |
| User story §5.2 | 21 | **21 (100%)** | 1 | **10** | F2 LOCK + P1 |
| B.2 entitás | 22 | **22 (100%)** | 0 | **16** | shadow HITL 4 |
| B.3 / B.4 API | 12 | **12 (100%)** | **4** | **4** | 2 P1 + HITL + CDS LOCK |
| B.5 hibakód | 22 | **22 (100%)** | **12** | 4 | F2/VCF maradék |
| NFR §7 | 13 | **13 (100%)** | 0 | 5 | P1/P2 |
| REG §8 | 16 | **16 (100%)** | 0 | 4 | pecsét |

**NOW sáv** (§10.2 F1+ mag + F1s fixture, pecsét nélkül): FR-100, 110, 115, 120, 130, 210, 220, 240, 250, 310, 400-STATIC, 400-LIVE, 410-EDU, 410-LIVE, 420 (F1+), 440, 450, 450-BLIND, 460, 461, 470, 490, 500, 610-P0, 700, 710, plusz FR-300 **kikapcsolva** (negatív). FR-200 VCF a NOW-ban *támogatott*, default FR-240.

**Kód FULL (FR) = 0** szándékos: egy FR akkor FULL, ha **minden** AC + B-szerződés + D.2 TC zöld. GatewayEvent `id` / `org_id` / `payload_hash` / `received_at` megvan (G12); FR-461 maradék: intézményi monitor org-név, Practitioner a Gold HIS-ben nem volt, a strip teszt szintetikus.

**Terv-teljesség NOW: 27/27 = 100%.** Kód-teljesség NOW: 0 FULL + 21 PARTIAL + 1 LOCK + 5 MISSING → **21/27 ≈ 78% legalább PARTIAL** (korábban 15/27 ≈ 56%). A 5 MISSING mind F1s motor/HITL: FR-400-LIVE, 410-LIVE, 440, 450, 450-BLIND (WP-M, WP-H).

**Dataflow F1+ (DATAFLOW §5, 8 lépés):** 8/8 SYN-en végigjárható HTTP-n (`test_ui_and_iso_and_walk`). F1s HITL store: 0/5 lépés (gateway ingest megvan, persist/HITL UI nincs).

**UX zsákutca:** W-CALL-010 → `POST .../resolve-call` (emberi választás). FR-100 piros → nincs PDF. clinician → HITL `E-ISO-001`. CDS → `E-ISO-002`. P2-nek nincs belépés.

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
| FR-100 | Comp P0 F1+ | PARTIAL | **WP-C** | TC-CONSENT-001..006 HTTP | kapu nem kikapcsolható; meta tanácsadó/dátum/engedély; FHIR Consent v1.1 később |
| FR-110 | Comp P0 F1+ | PARTIAL | **WP-C** | omit + 410 + certificate | 72 h = azonnali SYN; klinikus-példány külön jogalap nincs bekapcsolva |
| FR-115 | Comp P0 ha ≠ ANON | PARTIAL | **WP-C** / H | ingest `E-CONSENT-006` | HITL írás még nincs (WP-H); ANON nem blokkol |
| FR-120 | Comp P0 F1+ | PARTIAL | **WP-Q** | append-only trigger + CSV/JSON | hash-chain **DEFERRED P1**; nyers VCF nincs a naplóban |
| FR-130 | Comp P0 F1+ | PARTIAL | **WP-K** | `reid_store` külön tábla | L4 log-scanner PII: gateway + report dump |
| FR-200 | Prod P0 VCF | PARTIAL | **WP-V** | `E-VCF-003`; W-CALL-010 | ≥3 missing-to-ref gold; 5 GB; parse gold |
| FR-210 | Prod P0 | PARTIAL | **WP-R / V** | OC INDETERMINATE klinikai path | ≥3 missing-to-ref VCF gold; PharmCAT flag vakon tilos |
| FR-220 | P0 F1s; F1+ nem L4 | PARTIAL | **WP-K / M** | PUT tárol; render nem olvassa | shadow `clinical_context=ABSENT` WP-M |
| FR-230 | P1 | — | **WP-P1** | — | DEFERRED |
| FR-240 | Prod P0 | PARTIAL | **WP-K** | JSON+TSV HTTP; `E-CALL-001`; `W-CALL-010` + resolve | HL7 P1 |
| FR-250 | Prod P0 | PARTIAL | **WP-N** | ATC truncate | HGVS/VRS VCF-path; OGYÉI `E-MAP-001` |
| FR-300 | Prod P0 VCF; F1 OFF | LOCK | **WP-I** | MATCHER_ON false | F1+ ON tilos |
| FR-310 | Prod P0 | PARTIAL | **WP-T** | PREPARE-12 tuple + config_id | külső `pgx-prepare-12@v`; change-control; 12 gén CPIC |
| FR-400-STATIC | Prod P0 F1+ | PARTIAL | **WP-T / R** | CYP2D6 79 pair findings; source+url | többi PREPARE-12 gén; DPWG+FDA hivatalos fájl |
| FR-400-LIVE | P0 F1s | MISSING | **WP-M** | — | diplotípus+MedicationEntry → live_findings; nincs FK Report-ra |
| FR-410-EDU | Prod P0 F1+ | PARTIAL | **WP-T / R** | token tiltás; EDU=null | forrásolt bekezdés vagy indokolt null; ≥5 ha–akkor gold |
| FR-410-LIVE | P0 F1s | MISSING | **WP-M** | — | paroxetin/fluoxetin NM→PM/IM; nincs dose_mg |
| FR-420 | P0 F1+ struktúra | PARTIAL | **WP-R** | génenként findings; `severity_means_replace_prescribed=false` | CRITICAL F2 card később |
| FR-430 | P2 | NG | — | — | nem épül |
| FR-440 | P0 F1s | MISSING | **WP-H** | — | aszinkron persist HITL DB |
| FR-450 | P0 F1s | MISSING | **WP-H / U** | clinician 403 `E-ISO-001` | `hitl_reviewer` UI; reason_code |
| FR-450-BLIND | P1; §10.2 SYN igen | MISSING | **WP-H** | — | 2 lépés, immutábilis vak döntés |
| FR-460 | Comp P0 F1s | PARTIAL | WP-G | PII + G12 id/hash/org + G13 Practitioner | Gold HIS Practitioner nem volt; strip tesztelt |
| FR-461 | Comp P0 F1s | PARTIAL | WP-G | TC-GW nagy része + séma mezők | monitor SYN org display |
| FR-470 | Comp P0 | PARTIAL | **WP-I** | LIVE_CDS; grep; CDS 404; HITL 403 | tiltott JSON mezők a B.4.1-en |
| FR-480 | P1 | — | **WP-P1** | — | DEFERRED |
| FR-490 | Comp P0 | PARTIAL | WP-R | A.1/A.1.1 minden PDF oldal chrome | FHIR description = A.1.1 |
| FR-500 | Prod P0 | PARTIAL | **WP-F / R** | B.4.1 + PDF + STU3 Bundle | teljes IG validátor; white-label logo fájl |
| FR-510 | P1 | — | **WP-P1** | — | DEFERRED |
| FR-520 | P0 F2; tilos F1+ | LOCK | **WP-I** | `E-ISO-002` 404 | endpoint nincs |
| FR-530 | P1 F2 | — | **WP-P1** | v1 labor-UI = WP-U HTML | SMART később |
| FR-540 | P1 | — | **WP-P1** | — | OQ-13 |
| FR-600 | P1 | — | **WP-P1** | — | HITL DISAGREE napló előkészítés H-ban |
| FR-610 | Comp P0 HU | PARTIAL | **WP-L** | HU A.1.1; `text_hu_status` jelölés | nem LLM; lektorált HU később |
| FR-700 | Comp P0 | PARTIAL | WP-I | CI grep + call-graph | klinikai path nem hív shadow motort (nincs motor) |
| FR-710 | Comp P0 | PARTIAL | **WP-X** | determinisztikus HU; hash; 6. § (6) | AuditEvent a kérésre megvan create_report mellett |

---

## 4. User story mátrix (§5.2)

| # | Persona | Terv | Status | Spec |
| --- | --- | --- | --- | --- |
| 1 | P1 riport egy művelettel | WP-U + K + R | PARTIAL (HTTP + HTML) | FR-240, 400-STATIC, 500 |
| 2 | P1 guideline-verzió | WP-T + F | PARTIAL | FR-310, 500 |
| 3 | P1 hiányzó gén | WP-R / V | PARTIAL | FR-210 |
| 4 | P1 white-label + aláíró | WP-F + U | PARTIAL | SYN-ORG slot + signer_slot; logo fájl később |
| 5 | P1 újragenerálás | WP-P1 | DEFERRED | FR-510 |
| 6–10 | P2 felírási riasztás | LOCK | DEFERRED F2 | FR-520; NG-07 |
| 11–12 | P3 fenokonverzió HITL/F2 | WP-M + H | PLANNED SYN | FR-410-LIVE |
| 13 | P4 tanácsadás kapu | WP-C + U | PARTIAL | FR-100 HTTP + űrlap |
| 14 | P4 gén-hozzájárulás | WP-C | PARTIAL | scope + omit_from_patient |
| 15 | P5 visszavonás tanúsítvány | WP-C | PARTIAL | DeletionCertificate; 410 |
| 16 | P5 audit export | WP-Q | PARTIAL | CSV+JSON; hash-chain P1 |
| 17 | P6 FHIR/CDS | WP-F; CDS LOCK | PARTIAL | STU3 Bundle; `E-ISO-002` |
| 18 | P6 MDR határ | Outbound OQ-03 | PLANNED irat | REG-020/021 |
| 19 | nincs PGx explicit | WP-U / I | PLANNED | story 19 |
| 20 | csonka VCF | WP-V | PARTIAL | `E-VCF-001` prefix; gold később |
| 21 | CDS ne blokkoljon | WP-G fail-open | PARTIAL | E.2; FR-520 |

---

## 5. Entitás- és API-mátrix (B.2–B.4)

| Entitás / szerződés | Path | Terv | Kód |
| --- | --- | --- | --- |
| Organization | klinikai | WP-K | PARTIAL |
| Subject + reid_key_ref | klinikai | WP-K | PARTIAL |
| Case | klinikai | WP-K | PARTIAL |
| CounsellingRecord | klinikai | WP-C | PARTIAL |
| ConsentRecord | klinikai | WP-C | PARTIAL |
| Sample | klinikai | WP-C | PARTIAL |
| GenomicFile | klinikai | WP-V | PARTIAL |
| OutsideCall | klinikai | WP-K | PARTIAL |
| Diplotype / Phenotype | klinikai | WP-K | PARTIAL |
| MedicationEntry / LabObservation | nem L4 F1+ | WP-K | PARTIAL |
| RuleSetVersion | klinikai | WP-T | PARTIAL |
| Report | klinikai | WP-F | PARTIAL |
| AuditEvent | klinikai | WP-Q | PARTIAL |
| Explanation | klinikai | WP-X | PARTIAL |
| DeletionCertificate | klinikai | WP-C | PARTIAL |
| GatewayEvent | shadow | WP-G / H | PARTIAL |
| ResearchConsent | shadow PSEUDO | WP-C | PARTIAL (flag a gatewayen) |
| ShadowInference | shadow | WP-M / H | MISSING |
| HitlReview | shadow | WP-H | MISSING |
| BuildFlag LIVE_CDS | mindkettő | WP-I | FULL false |
| `POST /v1/cases/{id}/files` | B.3.1 | WP-V | PARTIAL |
| `POST /v1/cases/{id}/outside-calls` | B.3.2 | WP-K | FULL (JSON+TSV+hibák) |
| `PUT /v1/cases/{id}/clinical-context` | B.3.3 | WP-K | FULL |
| `POST /v1/hl7/oru` | B.3.4 P1 | WP-P1 | DEFERRED |
| `POST /v1/shadow/events` | B.3.5 | WP-G | PARTIAL |
| `GET /v1/cases/{id}/reports/{rid}` | B.4.1 | WP-F | FULL (kötelező mezők + tiltottak) |
| PDF oldalmeta | B.4.2 | WP-F / R | PARTIAL |
| FHIR STU3 Bundle | B.4.3 | WP-F | PARTIAL |
| CDS Hooks | B.4.4 | WP-I 404 | LOCK |
| `GET /v1/encyclopedia` | B.4.5 P1 | WP-P1 | DEFERRED |
| `/v1/hitl/**` | B.4.6 | WP-H | PARTIAL (403/404 kapu; store WP-H) |

---

## 6. Hibakatalógus (B.5) — UX

| Kód | Terv | Kód most | UX |
| --- | --- | --- | --- |
| E-CONSENT-001..005 | WP-C | FULL | Labor UI + HTTP 409 HU |
| E-CONSENT-006 | WP-C/H | FULL (ingest) | PSEUDO: nincs HITL írás |
| E-VCF-001..004 | WP-V | PARTIAL | 003 tesztelt; 001 prefix; 002/004 váz |
| E-CALL-001, W-CALL-010 | WP-K | FULL | resolve-call zsákutca nélkül |
| E-MAP-001 | WP-N | — | `NEEDS_MAPPING` |
| E-CALLABILITY | WP-R | PARTIAL | INDETERMINATE a leleten |
| E-GONE-010 | WP-C | FULL | 410 |
| E-SHADOW-001..003 | WP-G | PARTIAL | HIS fail-open |
| E-ISO-001, E-ISO-002 | WP-I | FULL | 403 / 404 |
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

A 2026-08-13 első terv WP-G + vékony R volt; a B.1 klinikai lánc hiányzott. **P06s (ugyanez a nap):** WP-C+K+F+X+Q+U a `src/pce_clinical/` + `src/pce_ui/` csomagban. A renderer CLI `--outside-call` kapu nélkül **409 E-CONSENT-001**.

| Rés | Spec | Állapot P06s után |
| --- | --- | --- |
| Nincs Case/Consent, mégis PDF | FR-100 | **zárva** — kapu + HTTP + CLI |
| JSON nem B.4.1 | FR-500 | **PARTIAL** — kötelező top-level + findings |
| Nincs FHIR STU3 | FR-500 | **PARTIAL** — DiagnosticReport+Observation+DocumentReference |
| CYP2D6-only, nincs DPWG/FDA | FR-400-STATIC | nyitva WP-T (nincs kitalált DPWG sor) |
| EDU null | FR-410-EDU, FR-610 | spec-OK null; HU jelölés a statements-en |
| Nincs 6. § (6) magyarázat | FR-710 | **PARTIAL** — determinisztikus HU |
| HITL váz, nincs motor | FR-400-LIVE, 410-LIVE, 440–450 | **nyitva** WP-M, H |
| Nincs IAM | FR-470, E.4 | **PARTIAL** — SYN szerep-token |
| VCF gold ≥3 | FR-210 | nyitva WP-V; matcher OFF |

**FR-410-EDU (forrásolt, nem kitalálás):** A CPIC `guideline.notesonusage` 2026-08-13-án üres volt a CYP2D6 rekordokon (S043). A spec: a lelet *tartalmazhat* EDU bekezdést. Ha nincs forrásolt szöveg → `phenoconversion_edu = null` **megfelel**, TC-EDU-001: null ≠ kitalált bekezdés; tiltott token CI marad. Hivatalos osztály-szöveg később WP-T + URL.

---

## 9. P06s ellenőrzés (2026-08-13)

| Szabály | Eredmény |
| --- | --- |
| (1) NOW-sorok PARTIAL vagy FULL | **21/27 PARTIAL** + 1 LOCK; 5 MISSING = F1s HITL/motor |
| (2) DATAFLOW F1+ SYN végigjárható | **PASS** `test_ui_and_iso_and_walk` |
| (3) érintett B.5 HTTP | **PASS** 001–005, 006, CALL, GONE, ISO |
| (4) `unsourced_claims == 0` | **PASS** |
| (5) FR-470 grepek | **PASS** (CI + IsolationTests) |

F1+ WP-C/K/F/X/Q/U **PARTIAL-VERIFIED**. WP-M/H **nincs VERIFIED**. Spec-t nem írunk.
