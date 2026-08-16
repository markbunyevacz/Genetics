# Spec ↔ delivery plan — tételes lefedettség (P06)

Ez a fájl a spec ↔ terv **státusztábla**. Terv: [DELIVERY-PLAN.md](DELIVERY-PLAN.md). Adatút: [DATAFLOW-AND-UX.md](DATAFLOW-AND-UX.md). Nincs külön „válasz” dokumentum.

**Mit jelent a tábla (magyarul):**

| Szó a táblában | Mit jelent | Mikor lesz belőle a következő |
| --- | --- | --- |
| **PARTIAL** | A kód + teszt megvan a SYN úton; a spec pipái közül a **Rés** oszlopban lévők még nyitva (a termékben jelezve, ahol kell). | A Rés bezárása. |
| **FULL** | A spec **minden** pipája + a D melléklet **minden** tesztje zöld arra a tételre. | — |
| **Hiányzik** (MISSING) | A mostani sávban nincs kód. | Kód + teszt. |
| **Később** (P1 / DEFERRED) | A spec is későbbre tette. | Nem most. |
| **Szándékos tiltás** (LOCK / NG) | Pl. élő felírási riasztás pecsét előtt. | Pecsét / más termékfázis. |

A rendszer a fagyasztott spec NOW-sávját építi (klinikai lánc + kutatási párosítás + VCF-lefedettség). A Rés oszlop a még hiányzó spec-pipa.

| | |
| --- | --- |
| **Dátum** | 2026-08-14 (P06ae: ETAP 0 — D-45) |
| **Spec** | `docs/pce/PCE-SPEC-v1.2.md` **FAGYASZTVA** (§10.2) + A, B, D, E; D-45 ETAP 0 |
| **Terv** | [DELIVERY-PLAN.md](DELIVERY-PLAN.md) |
| **Adatfolyam / UX** | [DATAFLOW-AND-UX.md](DATAFLOW-AND-UX.md) |
| **Oracle** | `PYTHONPATH=src python3 -m unittest discover -s tests -v` |
| **Nem** | Új FR, OQ-lezárás, kitalált gyártónév, dummy guideline-szöveg, `LIVE_CDS=true` a repo konstansban |

Mérés: minden spec-tétel **FULL** / **PARTIAL** / **PLANNED** / **DEFERRED** / **NG**. A kód a 2026-08-13 `cursor/pce-clinical-gates-3690` szerint. A terv **minden NOW-tételt** nevesít Given/When/Then + B-szerződéssel.

## 1. Pontszám (kvantitatív)

| Halmaz | N | Tervben nevesítve | Kód FULL | Kód PARTIAL | Kód MISSING (NOW) |
| --- | --- | --- | --- | --- | --- |
| FR katalógus (36) | 36 | **36 (100%)** | 0 | **26** | 0 NOW + P1/NG |
| §10.2 NOW kódolható sáv | 27 | **27 (100%)** | 0 | **27** PARTIAL | **0** |
| User story §5.2 | 21 | **21 (100%)** | 1 | **17** | élő F2 Card LOCK + P1 |
| B.2 entitás | 22 | **22 (100%)** | 1 flag | **18** | 0 NOW (P1 maradék) |
| B.3 / B.4 API | 12 | **12 (100%)** | **4** | **6** | 2 P1 (enciklopédia, HL7) |
| B.5 hibakód | 22 | **22 (100%)** | **12** | 4 | F2/VCF maradék |
| NFR §7 | 13 | **13 (100%)** | 0 | 5 | P1/P2 |
| REG §8 | 16 | **16 (100%)** | 0 | 4 | pecsét |

**NOW sáv** (§10.2 F1+ mag + F1s fixture, pecsét nélkül): FR-100, 110, 115, 120, 130, 210, 220, 240, 250, 310, 400-STATIC, 400-LIVE, 410-EDU, 410-LIVE, 420 (F1+), 440, 450, 450-BLIND, 460, 461, 470, 490, 500, 610-P0, 700, 710, plusz FR-300 **kikapcsolva** (negatív). FR-200 VCF a NOW-ban *támogatott*, default FR-240.

**Kód FULL (FR) = 0** szándékos: egy FR akkor FULL, ha **minden** AC + B-szerződés + D.2 TC zöld. GatewayEvent `id` / `org_id` / `payload_hash` / `received_at` megvan (G12); FR-461 monitor `org_id` / `org_display` = `SYN-ORG-001` (opák, nem kitalált kórháznév). Practitioner a Gold HIS-ben nem volt, a strip teszt szintetikus.

**Terv-teljesség NOW: 27/27 = 100%.** Kód-teljesség NOW: 0 FULL + **27 PARTIAL** + 0 LOCK + **0 MISSING**. Plusz F2 cső (FR-520/530): **PARTIAL** lakattal, nem a 27 F1+/F1s NOW-sor. A Rés oszlop a még nyitott spec-pipa (HLA-B / UGT1A1\*28 a VCF pontmutációs panelből továbbra sem számolható — a laboreredmény outside-callban jön; F5 recommendation_view üres; pecsét előtti élő Card). A termék jelzi a hiányt ott, ahol a guideline-tábla üres.

**Dataflow F1+ (DATAFLOW §5, 8 lépés):** 8/8 SYN-en végigjárható HTTP-n (`test_ui_and_iso_and_walk`). **F1s HITL (5 lépés):** 5/5 (`test_his_gateway_ingest_hitl_report_untouched` + HTTP vak walk).

**UX zsákutca:** W-CALL-010 → `POST .../resolve-call` (emberi választás). FR-100 piros → nincs PDF. clinician → HITL `E-ISO-001`. CDS a `pce_clinical`-en → `E-ISO-002`. CDS a `pce_cds`-en lock → üres `cards`. P2-nek nincs élő Card.

---

## 2. NOW vs LATER vs NG

| Partíció | Forrás | Delivery plan |
| --- | --- | --- |
| **NOW-F1+** | §10.2 L0–L2, FR-240, 210, 310, 400-STATIC, 410-EDU, 490, 500 PDF/FHIR, 470, 700 | WP-C, K, N, T, F, R, U, X, L, Q |
| **NOW-F1s** | §10.2 440/450/450-BLIND/460/461/410-LIVE SYN | WP-G (kész), H, M |
| **NOW-F2-PIPE** | FR-520 cső + FR-530 stub; `LIVE_CDS=false` | **WP-F2** |
| **LOCK** | `LIVE_CDS=true` a repo konstansban; matcher ON F1+ **HGVS/VRS nélkül** (N3/V8); MedicationEntry a rendererben; élő HIS; élő suggestion a felírónak | WP-I negatív CI |
| **LATER-P1** | FR-230, 480, 510, 540, 600, 610-EN-UI, 120 hash-chain, 220 FHIR | WP-P1 |
| **LATER-F2** | élő Card / SMART interruptive pecsét után | signed `LIVE_CDS=true` + REG-011 |
| **P2 / parking** | FR-430, §13, NG-01–06, EESZT írás | nem kód |

---

## 3. FR mátrix (38 tétel)

| FR | Pri / path | Kód | Terv WP | Validáció most | Rés |
| --- | --- | --- | --- | --- | --- |
| FR-100 | Comp P0 F1+ | PARTIAL | **WP-C** | TC-CONSENT-001..006 HTTP | kapu nem kikapcsolható; meta tanácsadó/dátum/engedély; FHIR Consent v1.1 később |
| FR-110 | Comp P0 F1+ | PARTIAL | **WP-C** | omit + 410 + certificate **és** Art. 12(3) válaszlevél; Art. 12(4) `refuse_erasure`; `E-DSR-OVERDUE` dashboard | SYN-en a 72 h SLA azonnalinak van implementálva; klinikus-példány külön jogalap nincs bekapcsolva. S055 **LEZÁRVA**. |
| FR-115 | Comp P0 ha ≠ ANON | PARTIAL | **WP-C** / H | ingest `E-CONSENT-006`; nincs HITL sor | ANON nem blokkol |
| FR-120 | Comp P0 F1+ | PARTIAL | **WP-Q** | append-only trigger + CSV/JSON | hash-chain **DEFERRED P1**; nyers VCF nincs a naplóban |
| FR-130 | Comp P0 F1+ | PARTIAL | **WP-K** | `reid_store` külön tábla | L4 log-scanner PII: gateway + report dump |
| FR-200 | Prod P0 VCF | PARTIAL | **WP-V** | `E-VCF-001..004`; W-CALL-010; coverage `add_vcf`-kor | 5 GB chunked; gz/tabix élesben |
| FR-210 | Prod P0 | PARTIAL | **WP-R / V** | OC INDETERMINATE; **4 SYN VCF gold** (CYP2D6\*4, CYP2C19\*2, DPYD\*2A, CYP2C9\*3) → `INDETERMINATE`, nem NORMAL; 10 PREPARE-12 gén SNV-katalógus pinelve (Ensembl POST + NCBI); HLA-B / UGT1A1\*28 `not_snv` → `NOT_TESTED` a VCF-en; laboreredmény outside-callban befogadva (HLA-B\*57:01, UGT1A1\*28/\*28) | VCF pontmutációs panel nem HLA-tipizálás és nem TATA-box ismétléshossz (szándékos, nincs kitalált HLA pontmutáció); gz/tabix élesben |
| FR-220 | P0 F1s; F1+ nem L4 | PARTIAL | **WP-K / M** | PUT tárol; a renderernek nincs gyógyszerlista-argumentuma; a lelet a gén guideline-tábláját listázza (`gyogyszerlista_a_leleten=false`); shadow `ABSENT` | FHIR medication bundle P1 |
| FR-230 | P1 | — | **WP-P1** | — | DEFERRED |
| FR-240 | Prod P0 | PARTIAL | **WP-K** | JSON+TSV HTTP; `E-CALL-001`; `W-CALL-010` + resolve | HL7 P1 |
| FR-250 | Prod P0 | PARTIAL | **WP-N** | default 7 karakteres hatóanyag-kód (`truncate_atc`); `E-MAP-001` a B.5 katalógusban; teszt: `tests/test_fr_trace.py` | ATC/OGYÉI: mapping **nincs bekötve** (F1+ nem fogyaszt `MedicationEntry`-t). **HGVS/VRS előfeltétel: `MATCHER_ON=true`.** Amíg false + FR-240, a spec „ahol variáns bemenet van” ága nem él — nem külön hátralék. |
| FR-300 | Prod P0 VCF; F1 OFF | PARTIAL | **WP-I / V** | PharmCAT 3.4.0 NamedAlleleMatcher + Phenotyper **hívva** `call_star_alleles(..., matcher_on=True)` / `POST .../files?matcher_on=true`. Riport: `pipeline_version`, `pharmcat_version`, `pharmvar_version`, `cpic_data_version`. Több diplotípus → INDETERMINATE, nincs önkényes `*1`. HLA-B VCF-ből NOT_TESTED. Repo `MATCHER_ON=false`. Jar SOUP, MPL 2.0, nem fork. | F1+ default ON tilos változáskezelés nélkül. CYP2D6 kópiaszám/hibrid SNP-VCF-ből nem jön ki → jelzett, nem kitalált |
| FR-310 | Prod P0 | PARTIAL | **WP-T** | PREPARE-12 + `config_id`; 12 gén CPIC `pair_view` pin (S049) | change-control rekord; HLA-A/NUDT15 külön config |
| FR-400-STATIC | Prod P0 F1+ | PARTIAL | **WP-T / R** | 12 gén CPIC pair dump; F5/VKORC1 üres rec **jelezve**; `dpwg_version` + ClinPGx DPWG annotation index URL-lel; `fda_table_version` + Table 2-2 CYP2D6 strong extract; nincs szintetizált harmadik ajánlás | DPWG teljes HTML tábla nem a findings-ben (index + pin); lektorált HU DPWG-szöveg |
| FR-400-LIVE | P0 F1s | PARTIAL | **WP-M** | párosítás `(gén, 7 karakteres kód)` kulcson; index párok + a pinelt rec_view többi PREPARE-12 szere (≥50 pár, WHO ATC); warfarin: CYP2C9+VKORC1 a 2017-es 2. ábrából, **nincs** mg; **nincs** `dose_mg`; CYP2D6+clopidogrel nem párosít; F5: `CPIC_F5_SOURCE=off\|mock\|live` (prod/default **off**). Mock fixture a pipeline-t futtatja; **nem** hivatalos CPIC rec. LIVE üres fetch → nincs pár. F1+ lelet F5 rec_view továbbra is 0 sor. | F5 élő pár a signed leleten csak ha a CPIC rec_view sort ad; mock nem szivárog a leletre; nincs FK Report-ra |
| FR-410-EDU | Prod P0 F1+ | PARTIAL | **WP-T / R** | token tiltás; EDU=null | forrásolt bekezdés vagy indokolt null; ≥5 ha–akkor gold |
| FR-410-LIVE | P0 F1s | PARTIAL | **WP-M** | gén szerinti osztály immutábilis; FDA erős gátló ATC5-ön; **funkcionális szegény metabolizáló üres**; **pheno-gold-v0 N=32** | SSRI NM→szegény sor, ha a CPIC/FDA kiadja |
| FR-420 | P0 F1+ struktúra | PARTIAL | **WP-R** | génenként findings; `severity_means_replace_prescribed=false` (`assemble_b41` + `tests/test_clinical.py` / `tests/test_fr_trace.py`) | CRITICAL F2 interruptive card pecsét után |
| FR-430 | P2 | NG | — | — | nem épül |
| FR-440 | P0 F1s | PARTIAL | **WP-H** | ingest 202 persist `hitl.sqlite`; store-hiba is 202 | aszinkron worker élesben |
| FR-450 | P0 F1s | PARTIAL | **WP-H / U** | `hitl_reviewer` HTML + kártya; reason_code; clinician `E-ISO-001` | MFA éles |
| FR-450-BLIND | P1; §10.2 SYN igen | PARTIAL | **WP-H** | `POST .../blind` majd `.../reviews`; immutábilis; default be | OQ-15 nem lezárt pecsét |
| FR-460 | Comp P0 F1s | PARTIAL | WP-G | PII + G12 id/hash/org + G13 Practitioner | Gold HIS Practitioner nem volt; strip tesztelt |
| FR-461 | Comp P0 F1s | PARTIAL | WP-G | default 7 karakteres kód; PII/dózis/nap 400; k-cella; negyedéves monitor `org_id`/`org_display`=`SYN-ORG-001` | Gold HIS Practitioner nem volt; A14 k≥5 `[ASSUMPTION]` |
| FR-470 | Comp P0 | PARTIAL | **WP-I** | LIVE_CDS; grep; CDS 404 a `pce_clinical`-en; HITL 403; **allow-list** B.4.1; R9↔séma; `create_report` nem SELECT a gyógyszerlista-táblára; `pce_cds` izoláció | élő CDS pecsétig LOCK |
| FR-480 | P1 | — | **WP-P1** | — | DEFERRED |
| FR-490 | Comp P0 | PARTIAL | WP-R | A.1/A.1.1 minden PDF oldal chrome | FHIR description = A.1.1 |
| FR-500 | Prod P0 | PARTIAL | **WP-F / R** | B.4.1 + PDF + STU3 Bundle | teljes IG validátor; white-label logo fájl |
| FR-510 | P1 | — | **WP-P1** | — | DEFERRED |
| FR-520 | P0 F2; tilos F1+ processzuson | PARTIAL | **WP-F2** | lock HTTP üres `cards`; ON paraméteres teszt; timeout fail-open; IIa-safe | éles HIS + signed `LIVE_CDS=true` |
| FR-530 | P1 F2 stub | PARTIAL | **WP-F2** | SMART `/.well-known/smart-configuration` lakat + SYN stub | éles EHR-launch pecsét után |
| FR-540 | P1 | — | **WP-P1** | — | OQ-13 |
| FR-600 | P1 | — | **WP-P1** | — | HITL DISAGREE napló előkészítés H-ban |
| FR-610 | Comp P0 HU | PARTIAL | **WP-L** | HU A.1.1; `text_hu_status` jelölés | nem LLM; lektorált HU később |
| FR-700 | Comp P0 | PARTIAL | WP-I | CI grep + `tests/test_fr_trace.py` (nincs openai/anthropic/langchain import) | a klinikai út a leletkészítéskor nem hívja a shadow motort |
| FR-710 | Comp P0 | PARTIAL | **WP-X** | determinisztikus HU; hash; 6. § (6) | AuditEvent a magyarázat-kérésről megvan (a create_report mellett) |

---

## 4. User story mátrix (§5.2)

| # | Persona | Terv | Status | Spec |
| --- | --- | --- | --- | --- |
| 1 | P1 riport egy művelettel | WP-U + K + R | PARTIAL (HTTP + HTML) | FR-240, 400-STATIC, 500 |
| 2 | P1 guideline-verzió | WP-T + F | PARTIAL | FR-310, 500 |
| 3 | P1 hiányzó gén | WP-R / V | PARTIAL | FR-210; 4 VCF gold + OC INDETERMINATE; HLA/UGT VCF `not_snv`, laboreredmény outside-call |
| 4 | P1 white-label + aláíró | WP-F + U | PARTIAL | SYN-ORG slot + signer_slot; logo fájl később |
| 5 | P1 újragenerálás | WP-P1 | DEFERRED | FR-510 |
| 6–10 | P2 felírási riasztás | WP-F2 | PARTIAL (cső + lakat) | FR-520; NG-07; élő suggestion pecsétig LOCK |
| 11–12 | P3 fenokonverzió HITL/F2 | WP-M + H | PARTIAL SYN | FR-410-LIVE; vak UI; nincs kitalált PM |
| 13 | P4 tanácsadás kapu | WP-C + U | PARTIAL | FR-100 HTTP + űrlap |
| 14 | P4 gén-hozzájárulás | WP-C | PARTIAL | scope + omit_from_patient |
| 15 | P5 visszavonás tanúsítvány | WP-C | PARTIAL | DeletionCertificate; 410 |
| 16 | P5 audit export | WP-Q | PARTIAL | CSV+JSON; hash-chain P1 |
| 17 | P6 FHIR/CDS | WP-F; WP-F2 | PARTIAL | STU3 Bundle; F1+ `E-ISO-002`; `pce_cds` lakat |
| 18 | P6 MDR határ | Outbound OQ-03 | PLANNED irat | REG-020/021 |
| 19 | nincs PGx explicit | WP-U / I | PLANNED | story 19 |
| 20 | csonka VCF | WP-V | PARTIAL | `E-VCF-001` prefix; gold később |
| 21 | CDS ne blokkoljon | WP-F2 fail-open | PARTIAL | E.2; FR-520; timeout → üres `cards` |

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
| ShadowInference | shadow | WP-M / H | PARTIAL |
| HitlReview | shadow | WP-H | PARTIAL |
| BuildFlag LIVE_CDS | mindkettő | WP-I | FULL false |
| `POST /v1/cases/{id}/files` | B.3.1 | WP-V | PARTIAL |
| `POST /v1/cases/{id}/outside-calls` | B.3.2 | WP-K | FULL (JSON+TSV+hibák) |
| `PUT /v1/cases/{id}/clinical-context` | B.3.3 | WP-K | FULL |
| `POST /v1/hl7/oru` | B.3.4 P1 | WP-P1 | DEFERRED |
| `POST /v1/shadow/events` | B.3.5 | WP-G / H | PARTIAL (202 + persist) |
| `GET /v1/cases/{id}/reports/{rid}` | B.4.1 | WP-F | FULL (kötelező mezők + tiltottak) |
| PDF oldalmeta | B.4.2 | WP-F / R | PARTIAL |
| FHIR STU3 Bundle | B.4.3 | WP-F | PARTIAL |
| CDS Hooks | B.4.4 | WP-F2 | PARTIAL (lakat; F1+ 404) |
| `GET /v1/encyclopedia` | B.4.5 P1 | WP-P1 | DEFERRED |
| `/v1/hitl/**` | B.4.6 | WP-H | PARTIAL (lista, vak, verdict, UI; klinikai processzus 403) |

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
| E-TIMEOUT-CDS | F2 | PARTIAL | felírás nem blokkol (`test_cds` timeout) |

---

## 7. NFR / REG

| ID | Terv | Megjegyzés |
| --- | --- | --- |
| NFR-010 | WP-V után mérés | F0 WES nélkül nem kapu |
| NFR-011 | WP-F2 | 2 s timeout tesztelt; p95 800 ms mérés hátravan |
| NFR-020 | üzem | nem F0 feature |
| NFR-030 | WP-K | EU tenancy; DPA = REG-050 |
| NFR-031 | SYN HTTP eltérés dokumentált | éles TLS 1.3 |
| NFR-032 | WP-Q | SYN szerepek; MFA éles |
| NFR-033 | WP-I | gitleaks CI |
| NFR-040 | WP-Q | = FR-120 |
| NFR-050 | P2 | DEFERRED |
| NFR-060 | WP-X + R | bitre azonos JSON |
| NFR-070 | CI | **NFR-070a** Class B mag; **NFR-070b** Class C javaslat A.4.1 — OQ-06 |
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
| CYP2D6-only, nincs DPWG/FDA | FR-400-STATIC | **PARTIAL** — 12 gén CPIC pair; F5/VKORC1 rec hiány **jelezve**; DPWG ClinPGx pin + FDA Table 2-2 kivonat a leleten (`dpwg_version` / `fda_table_version` nem null) |
| EDU null | FR-410-EDU, FR-610 | spec-OK null; HU jelölés a statements-en |
| Nincs 6. § (6) magyarázat | FR-710 | **PARTIAL** — determinisztikus HU |
| HITL váz, nincs motor | FR-400-LIVE, 410-LIVE, 440–450 | **PARTIAL** — `pce_shadow` + `pce_hitl`; SSRI NM→szegény **nincs**, a hiány a kártyán; PREPARE-12 élő párok gén-kulcson (F5/VKORC1 rec üres) |
| Nincs IAM | FR-470, E.4 | **PARTIAL** — SYN szerep-token |
| VCF gold ≥3 | FR-210 | **zárva** 4 SYN fájlra; 10 gén SNV-katalógus pinelve; HLA-B / UGT1A1\*28 `not_snv` |

**FR-410-EDU (forrásolt, nem kitalálás):** A CPIC `guideline.notesonusage` 2026-08-13-án üres volt a CYP2D6 rekordokon (S043). A spec: a lelet *tartalmazhat* EDU bekezdést. Ha nincs forrásolt szöveg → `phenoconversion_edu = null` **megfelel**, TC-EDU-001: null ≠ kitalált bekezdés; tiltott token CI marad. Hivatalos osztály-szöveg később WP-T + URL.

---

## 9. P06u ellenőrzés (2026-08-13)

| Szabály | Eredmény |
| --- | --- |
| (1) NOW-sorok PARTIAL vagy FULL | **27/27 PARTIAL**; **0 MISSING** |
| (2) DATAFLOW F1+ SYN végigjárható | **PASS** `test_ui_and_iso_and_walk` |
| (2b) DATAFLOW F1s HITL végigjárható | **PASS** `test_his_gateway_ingest_hitl_report_untouched` + HTTP vak walk |
| (3) érintett B.5 HTTP | **PASS** 001–005, 006, CALL, GONE, ISO; HITL operatív kódok a B.4.6-on |
| (4) `unsourced_claims == 0` | **PASS** F1+; árnyék: `functional_phenotype` üres, ha a tábla null |
| (5) FR-470 grepek | **PASS** (CI + IsolationTests; `pce_report` nem importál `pce_shadow` / `pce_cds`) |

F1+ WP-C/K/F/X/Q/U **PARTIAL-VERIFIED**. WP-M/H **PARTIAL-VERIFIED** (CYP2D6 + SSRI szelet; forrásolt null PM). Spec-t nem írunk.

---

## 10. P06w ellenőrzés (2026-08-13)

A user kérdése: van-e hivatalos NM→szegény metabolizáló tábla; a hiányt a termékben jelezni; PREPARE-12 CPIC; VCF gold; hatóanyag-kód a párosításhoz.

| Szabály | Eredmény |
| --- | --- |
| CPIC SSRI 2023 NM→szegény sor | **NINCS.** A kártya `forras_allapot.hianyzik` kiírja. Funkcionális szegény metabolizáló **nem** íródik. |
| FDA Table 2-2 | **VAN** erős gátló (paroxetin N06AB05, fluoxetin N06AB03). Nem mondja, hogy a beteg szegény metabolizáló. |
| CPIC opioid 2020 | **VAN** (erős gátló → aktivitási pont 0 → szegény metabolizáló), opioid szubsztrátra; a paroxetin-SSRI sorra **nem** alkalmazzuk. |
| PREPARE-12 CPIC pair_view | **12/12 letöltve** (S049). F5 és VKORC1 `recommendation_view` üres → a lelet `hianyzik` listája. |
| VCF gold ≥3 | **PASS** `tests/fixtures/vcf-gold-v0/` + `test_vcf_coverage.py` + klinikai path |
| ANON ATC5 | **202** (D-38: 7 karakteres hatóanyag-kód). DPO `max_atc_level=4` → 400. |
| Unittest | lásd P06x |

---

## 11. P06x ellenőrzés (2026-08-13)

A user öt pontja: forrás-letöltés; szegény címke tiltás; „a lelet olvas”; 5 vs 7 karakter; „allélhívó”.

| Szabály | Eredmény |
| --- | --- |
| CPIC API/PDF + FDA oldal, dátummal | **Letöltve és beépítve.** PDF/HTML: `docs/pce/Sources/official/` (2026-08-13). PREPARE-12 API JSON: `tests/fixtures/f1plus-v0/prepare12/`. Knowledge `on_disk`. A motor a pin-elt JSON-t olvassa, nem a PDF-et futáskor. |
| Funkcionális szegény címke tilos; hiány a kártyán | **Igen, a termékben.** `functional_phenotype=[]`; `irtunk_szegeny_metabolizalot=false`; HITL `forras_allapot` van/hiányzik a vak lépés után. |
| „A lelet olvassa a gyógyszerlistát” | **Értelmetlen mondat — javítva.** A PDF nem olvas. A lelet a gén publikált guideline-sorait **listázza**; `gyogyszerlista_a_leleten=false` + `megjegyzes_hu` a JSON/PDF-en. A renderernek nincs `medications` argumentuma. |
| 5 vs 7 karakteres kód | **7 karakteres hatóanyag-kód a default** (WHO ATC 5. szint). Spec A14/FR-461 D-38. ANON `N06AB05`/`N06AB10` → 202. Csoportkód (5 karakter) a párosítást szünetelteti. DPO durvíthat. |
| „Az allélhívó ki van kapcsolva” | **Magyarázat a leleten.** PharmCAT NamedAlleleMatcher = a program, amely VCF-ből csillag-allélt hívna. Ki: spec FR-300. Bekapcsolás: változáskezelés + REG-010, nem UI-kapcsoló. A diplotípust a partnerlabor adja. `diplotipus_forras_hu`. |
| Unittest | **94 OK** (P06x). P06y: lásd §12 |

---

## 12. P06y — J-1…J-6 (2026-08-13)

| Tétel | Eredmény |
| --- | --- |
| J-1 F-07 séma-zárás | B.4.1 allow-list; deny-list bővítve (`medications`, `clinical_context`, `hitl_*`, …). `_scan_forbidden` tok-szűkítés törölve. `create_report` **nem** tölti a gyógyszerlista-táblát. 7 negatív + 1 pozitív teszt. |
| J-6 R9↔kód | `tests/test_report.py` R9 backtick-nevek ⊆ `FORBIDDEN_B41_FIELDS`; CI lépés. |
| J-3 F-06 pheno-gold | `tests/fixtures/pheno-gold-v0/` N=32. Elvárt funkcionális fenotípus **üres**. G3 ≥90% **csak** itt. Nincs kitalált NM→szegény. |
| J-2 F-04 | A.4.1 tábla; NFR-070a/b; OQ-06 = osztály páronként. RA pecsét **nyitott**. |
| J-4 F-05 | FR-110: 26. § (1) határidő nélkül; GDPR Art. 12(3)/12(4)/17(1). **S055 LEZÁRVA** (EUR-Lex HTML+PDF). Két artefaktum + `E-DSR-OVERDUE`. |
| J-5 F-01 | §0 Owner / Validation / Due / Ha hamis. A14 k≥5 / 0,5% horgonya WP29 05/2014 + EDPB 01/2025, nem a DPIA. |
| Unittest | **108 OK** |

---

## 13. P06z — árazás (2026-08-13)

| Tétel | Eredmény |
| --- | --- |
| YouScript 365 USD | `[V]` WebFetch; urllib pin 403 |
| SMART Per User, Site-Based | `[V]` pin |
| Semmelweis 816.636.406 Ft | `[V]` GFI + KÉ 2020/58 pin — **HIS**, nem PGx |
| EKR ~88,3 M Ft | `[R]` — EKR body hátravan |
| Javasolt Ft-sáv | **Következtetés** `Sales/pricing.md`. Nincs a spec FR-ben listaárként. |
| Repo állapota | 5 modul (shadow+HITL egy cső); 12 official SHA-256 `ok`; **111** teszt. Nem 94, nem 7 pin. |

---

## 14. P06aa — G melléklet (2026-08-13)

| Tétel | Eredmény |
| --- | --- |
| S055 | **LEZÁRVA.** EUR-Lex HTML 809 035 byte; Art. 12(3)/12(4)/17(1) a HTML-ben. |
| FR-110 | Két artefaktum: `DeletionCertificate` + `DsrLetter`. `refuse_erasure` Art. 12(4). `E-DSR-OVERDUE`. |
| OQ-05/06/16 | Javaslat, **nem** DPO-/RA-/counsel-pecsét. Class I MDSW default; IIa-safe párlista fallback; k≥11 politika. A14 k≥5 marad. |
| F-14 | `[Yp]=0` 15 felíró alatt; `[Yc]` közép 240 e; `[Ysh]=0`. Mind `[ESTIMATE]`. |
| Pin | + GDPR HTML/PDF, EMA 0,09, MDCG 2021-24 → **16** official `ok: true`. Unittest **113 OK**. |

---

## 15. P06ab — S060 / S062 pin (2026-08-13)

| Tétel | Eredmény |
| --- | --- |
| S060 | **LEZÁRVA `[V]`.** Teljes PRCI `document.html`: „target cell size of 11 patients” + risk=0.09. Profiloldal külön pin. |
| S062 | **LEZÁRVA `[V]`.** DHCS DDG V2.2 (2022-12-06, 71 oldal): numerátor <11 vagy nevező <20 000. Élő DHCS Incapsula; pin Wayback `/web/2022/`. v3.0 nincs pinelve. **Nem** EU-jog. |
| OQ-16 / A14 | k≥11 **javaslat** a DPO-nak. A14 k≥5 / 0,5% `[ASSUMPTION]` **nem** DPO-pecsét. |
| Pin | Official **19** `ok: true`. Unittest **113 OK**. |

---

## 16. P06ac — F2 CDS cső lakattal (2026-08-14, D-44)

A G5 ellentmondás: a Sales „ki van kapcsolva, nem hiányzik”; a TRACE FR-520 LOCK volt, mert a `pce_clinical`-en 404. Feloldás: külön processzus, a cső megvan, a kimenet lakat.

| Tétel | Eredmény |
| --- | --- |
| F1+ processzus | `GET/POST /cds-services/` → 404 `E-ISO-002` (**változatlan**) |
| F2 processzus | `src/pce_cds/`, `python -m pce_cds` SYN :8092 |
| Repo flag | `LIVE_CDS is False`; `MATCHER_ON is False`; `IIA_SAFE_BLOCK is True` |
| Lock HTTP | discovery `enabled: false`; POST 200 `cards: []`; `X-PCE-LIVE-CDS: false` |
| ON út | csak teszt-paraméter `live_cds=True`; **nem** a repo konstans |
| Fail-open | timeout 2 s → üres `cards` |
| IIa-safe | G §2.4 **mechanizmus-család** (ATC5 + HU INN-variáns); info, nincs suggestion. Tramadol / tegafur / tioguanin / `klopidogrel` bent. Nem L01BC*/L01BB* catch-all. |
| SMART | stub `/.well-known/smart-configuration` |
| Izoláció | `pce_report` / `pce_clinical` nem importál `pce_cds`-t (CI + teszt) |
| OQ | 05 / 06 / 15 / 16 **nem** pecsét. A14 k≥5 / 0,5% változatlan |
| Unittest | **124 OK** (113 + 11 CDS) |
| FR-520 / FR-530 | **PARTIAL** (cső); élő Card / éles EHR = pecsét |

Bekapcsolás a fejlesztés végén: signed release `LIVE_CDS=true` (és szükség szerint `IIA_SAFE_BLOCK=false` OQ-06 után). Kikapcsolás: a konstans `false`. Nincs újraírás.

---

## 17. P06ae — ETAP 0 (2026-08-14, D-45)

A user ETAP 0 szállítást kért. A megelőző kör a „indulhat”-ot későbbi engedélynek olvasta — ez hiba volt (E-24). Ez a kör a kódot szállítja.

| Tétel | Eredmény |
| --- | --- |
| T5 DPWG + FDA a leleten | ClinPGx `guidelineAnnotation?source=DPWG` pin (113 annotáció, 2026-08-14). `dpwg_version` nem null. FDA Table 2-2 CYP2D6 strong extract a 2026-08-13 HTML-ből. Külön URL-ek; **nincs** szintetizált harmadik ajánlás. |
| FR-210 katalógus | 10 PREPARE-12 gén SNV pin (Ensembl POST GRCh38+GRCh37 + NCBI dbSNP). 4. SYN gold: `missing-cyp2c9-star3.vcf`. HLA-B és UGT1A1\*28 `not_snv` → `NOT_TESTED` (NCBI `snp_class=delins` rs8175347). Matcher ki. |
| WP-M élő párosítás | Kulcs `(gén, ATC5)`. CYP2C19 `*1/*1`/`*1/*2`/`*2/*2` CPIC diplotípus-API; clopidogrel `B01AC04` stratégia-kategória. CYP2D6+clopidogrel **nem** párosít. Nincs `dose_mg`, nincs kitalált funkcionális PM. |
| FR-461 monitor | `org_id` / `org_display` = `SYN-ORG-001`. Nincs kitalált kórháznév, nincs PII. |
| Flag | `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. OQ-05/06/15/16 **nem** pecsét. A14 k≥5 / 0,5% változatlan. |
| Unittest | **134 OK** (124 + ETAP 0) |
| Official pin | **26** `ok: true` (19 a 2026-08-13 körből + 7 ETAP 0). A MANIFEST `accessed` **2026-08-13** marad a régi sorokon. |

Ensembl egyedi GET `/variation/human/{rsid}` 2026-08-14-én HTTP 503; a POST `/variation/homo_sapiens` batch 200. NCBI refsnp/eutils független GRCh38 chrpos-ellenőrzés.

---

## 18. P06af — PREPARE-12 élő párok + laboreredmény-befogadás + VCF csillag-allél BE-út (2026-08-15)

A user: a maradék PREPARE-12 párokat **nem** ő hagyta ki; az ETAP 0 D-45 vágás volt. A rendszer **nem** végzi el a HLA-B / UGT1A1\*28 laborvizsgálatot — a laboreredményt befogadja, elemzi, felhasználja. „Nincs mit bekapcsolni” hamis volt: a BE-utat meg kell írni, a repo flag ki marad.

| Tétel | Eredmény |
| --- | --- |
| Élő párok | CYP2B6–efavirenz (J05AG03), CYP2C9–celecoxib (M01AH01, aktivitási pont 2.0/1.5 CONTINUE, 1.0/0.5/0.0 CONSIDER_DOSE_CHANGE), CYP3A5–tacrolimus, DPYD–fluorouracil, SLCO1B1–simvastatin, TPMT–azathioprine (NUDT15 No Result), HLA-B–abacavir, UGT1A1–atazanavir. Nincs `dose_mg`. F5/VKORC1 **nincs** kitalált pár (üres recommendation_view). |
| HLA-B / UGT1A1\*28 | Outside-call fixture + F1+ pair dump + élő párosítás. VCF `not_snv` → `NOT_TESTED`. Nincs kitalált HLA pontmutáció, nincs rs887829 \*28-helyettesítő. |
| VCF csillag-allél | `call_star_alleles(..., matcher_on=True)`: CYP2D6 \*4/\*4 CALLED a pin-elt definiáló pontmutációból; hiányzó hely INDETERMINATE, nem \*1. Repo `MATCHER_ON=false`. Nem a teljes PharmCAT NamedAlleleMatcher. |
| Flag | `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. OQ-05/06/15/16 **nem** pecsét. |
| Official pin | **41** `ok: true`. MANIFEST top-level `accessed` **2026-08-13**. Új sorok `accessed: 2026-08-15`. |
| Unittest | **158 OK** |

A fluorouracil / azathioprine / clopidogrel IIa-safe listán van: az árnyék-motor párosít, a CDS suggestion pecsétig blokkolt (`IIA_SAFE_BLOCK=true`).

---

## 19. P06ag — szoftver-KÉSZ: rec_view párok + warfarin-diagram + PharmCAT (2026-08-15)

A user: a flag ki **nem** azt jelenti, hogy a szoftver nincs megírva. Demózható, tesztelt, szállított; prod éles pecsét nélkül. A „ki adja / honnan” a gyártó pin, nem a labor.

| Tétel | Ki adja | Honnan | Szoftver |
| --- | --- | --- | --- |
| F5 élő pár | CPIC rec_view | `api.cpicpgx.org` F5=not.is.null → **0 sor** | Pipeline **megvan**: `CPIC_F5_SOURCE=off` (prod) / `mock` (lokális fixture) / `live` (API). Mock **nem** hivatalos CPIC ajánlás. Nincs kitalált élő pár a default táblán. |
| Warfarin | CPIC 2017 PDF 2. ábra | pin `cpic-warfarin-2017-28198005.pdf`; WHO B01AA03 | CYP2C9 **és** VKORC1 együtt; PM → CONSIDER_ALTERNATIVE; különben CONSIDER_DOSE_CHANGE; **nincs mg**. |
| Többi rec-táblás szer | CPIC recommendation_view + WHO ATC | `prepare12-rec-pairings.v0.json` + `whocc-atc-*.html` | `infer` stratégia-kategória, nincs mg. Index párok nem felülírva. |
| Csillag-allél | PharmGKB PharmCAT 3.4.0 all-jar | GitHub release; sha256 pin; jar `var/` gitignored | NamedAlleleMatcher + Phenotyper hívva `matcher_on=True`. Repo flag false. |

Official pin: **87** `ok: true`. MANIFEST top-level `accessed` **2026-08-13**. Unittest **165 OK**.

---

## 20. P06ah — F5 adat-agnosztikus ingest (2026-08-15)

A user: „Amíg a CPIC nem ad rec-sort, nincs mit párosítani” **nem** azt jelenti, hogy a fejlesztés az API-ra vár. A cső most a mock fixture-ön fut. Amikor a CPIC publikál, `CPIC_F5_SOURCE=live` — kódmódosítás nélkül.

| Tétel | Eredmény |
| --- | --- |
| Séma / DTO | `tests/fixtures/cpic_f5_recommendation.schema.json` + `validate_rec_view_row`. `lookupkey.F5` string vagy null. |
| Mock fixture | `tests/fixtures/cpic_f5_mock.json`: HET avoid / WT continue / null F5 skip. `mocked: true`. ATC példa G03AA07. Nincs mg. |
| DataProvider | `OffF5Provider` / `MockF5Provider` / `LiveF5Provider`. Env `CPIC_F5_SOURCE`. Prod default **off**. |
| Index párok | Mock nem írja felül a paroxetin / clopidogrel / egyéb index párokat. |
| F1+ lelet | F5 `guideline_row_count == 0`. Mock szöveg nem kerül a signed JSON-ra. |
| Warfarin *2/*3 | CYP2C9+VKORC1 → CONSIDER_ALTERNATIVE. Egy gén → nincs finding. |
| PharmCAT HTTP | `POST /v1/cases/{id}/files?matcher_on=true` gold VCF → CYP2D6 *4/*4 CALLED. Repo `MATCHER_ON=false`. |
| Flag | `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. OQ-k **nem** pecsét. |
| Unittest | **184 OK** |

---

## 21. P06ai — repo-konform hardening (2026-08-15, D-49)

A user: a klinikai mag stabil; a hiányzó enterprise-garanciákat **a meglévő stdlib + unittest + pinelt JSON** keretben kell bezárni. Nincs Pydantic, BeautifulSoup, pytest, külső coverage.

| Tétel | Eredmény |
| --- | --- |
| F5 | `F5Source` Enum; ismeretlen token `ValueError`; mock=live `validate_rec_view_row`; nem-dict sor `log.critical` + fail-fast; HOM fixture; CI `CPIC_F5_SOURCE != live`. |
| Rec / warfarin | SKIP `frozenset`; index `(gene, atc5)` felülírás `ValueError`; ATC-5 regex `^[A-Z][0-9]{2}[A-Z]{2}[0-9]{2}$`; warfarin deklaratív CYP2C9-mátrix. Hiányzó gén → üres `live_findings`. |
| PharmCAT | CI: Java 17 + `fetch_software_ready_pins.py --jar-only` a tesztek előtt; `PCE_PHARMCAT_OFFLINE=1` — `ensure_jar()` nem hív GitHubot. `assemble_b41` matcher_on=True: négy nem-üres verzió. Gold VCF: CYP2D6 \*4/\*4 **és** CYP2C9 \*4/\*4 (PharmCAT 3.4.0 translation, rs56165452). |
| Flag | `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. OQ-k **nem** pecsét. MANIFEST top-level `accessed` **2026-08-13**. |
| Unittest | **195 OK** |

---

## 22. P06aj — checklist-zárás stdlib keretben (2026-08-15, D-50)

A user checklist Pydantic / BeautifulSoup / pytest / 100% coverage-csomag / `MissingGeneticDataException` crash nélkül, a meglévő stacken.

| Tétel | Eredmény |
| --- | --- |
| F5 | `F5DataProvider` Protocol; fixture deepcopy (HET+HOM); kétszeres `apply_f5_source` nem duplikál; `config/production.env` = `off`; LIVE üres/hálózati hiba → nincs exception. |
| Warfarin | Mindkét gén guard. Hiány → `MISSING_GENETIC_DATA` státusz, **üres** `live_findings`, nincs klinikai crash. Mátrix: `*2/*3`+AA, `*3/*3`+GA, `*1/*1`+AA, `*1/*2`+GG. |
| HTML | stdlib `html.parser`. Csonka pin → `ValueError` / `exit 1`. Nincs BeautifulSoup. Index clopidogrel SKIP akkor is, ha valaki berakja az ATC szótárba. |
| PharmCAT | `matcher_on=False` nem hív `subprocess.run`. `shell=False`. Nincs `.first()` / `.fallback()`. `add_outside_call`. CYP2D6 `sv_determined=False`. |
| Flag | `LIVE_CDS=false`; `MATCHER_ON=false`. OQ **nem** pecsét. |
| Unittest | **211 OK** |

---

## 23. P06ak — M4 megfelelőség: IIa-safe mechanizmus + FR-id nyomonkövetés (2026-08-15, D-51)

Független BA-audit (annotációt mért, viselkedést a 12 Compliance P0 + `pce_cds` IIa-safe blokkon). S1 klinikai lyuk: tramadol és magyar INN (`klopidogrel`) kiesett. S2: 24/36 FR-id nem szerepelt tesztben. S3: FR-420 és FR-250 *más néven* megvoltak.

| Tétel | Eredmény |
| --- | --- |
| IIa-safe | `IiaSafeFamily` ötöd: DPYD-fluoropirimidin (FU / kapecitabin / tegafur), CYP2C19–clopidogrel, TPMT-tiopurin (+ tioguanin), CYP2D6-opioid (kodein **és** tramadol), HLA-B\*15:02 aromás antiepileptikum (N03AF + N03AB02/N03AB05). Magyar INN-variáns. WHO L01BC/L01BB **prefix nincs** (gemcitabin / fludarabin). Pin: S048/S049 + WHO L01BC03 (S075). |
| FR-420 | Létezik: `severity_means_replace_prescribed=false`, findings gén-kulccsal. Nem hiányzott — jelöletlen volt. |
| FR-250 | Létezik: 7 karakteres ATC a gatewayen. `E-MAP-001` katalógusban, F1+ riport **nem** emeli (nincs gyógyszerlista a leleten). HGVS/VRS **nem** külön hátralék: **előfeltétel `MATCHER_ON=true`.** |
| FR-id CI | Minden spec `#### FR-…` heading token a `tests/`-ben. P1/P2 (FR-230/430/480/510/540/600) **hiány** tesztelve, nem hamis FULL. |
| Flag | `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. OQ **nem** pecsét. MANIFEST `accessed` **2026-08-13**. Official pin **88** `ok`. |
| Unittest | **228 OK** |

---

## 24. P06al — elesett GTM + ZK rekord (2026-08-16, D-52)

BA deviancia: 2026-08-09 koncepció tíz eleme vs `main`. Két elemnek **nem** volt döntési sora: longevity 1. fázis (#8) és Zero-Knowledge / local-first (#9). A többi (LIVE_CDS lakat, NG-03, MATCHER_ON, NG-02/FR-430, NG-07, SKU-P, parking lot pharma) már rögzítve volt.

| Tétel | Eredmény |
| --- | --- |
| A16 | §0 feltevés: az eredeti sebességi 1. fázis **elesett**. v1.0 G4 már labor/klinika; v1.2 SKU-P intézmény = **több** pecsét. Longevity mint v1 vevő **ki**. Sales `sku-and-buyers.md` ugyanazt mondja. |
| A17 | ZK / local-first **nincs** `src/`-ben. Helyette FR-460 + A12 + A13. Visszavenni = DPIA, nem flag. |
| Nem pecsét | OQ-05/15/16 nyitott. `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. Nincs F-10 ebben a repóban. |
| Teszt | `FallenGtmRecordTests`: A16/A17 sor, sku-and-buyers, `src/` ZK-tilalom. Unittest **231 OK**. |

---

## 25. P06am — BA M4 újraellenőrzés: L01BC* + MANIFEST dátum + HGVS-kapu (2026-08-16, D-53)

A BA igazolta: a `L01BC*` / `L01BB*` prefix-catch-all **rossz**. WHO 4. szint anatómiai-terápiás taxonómia, nem PGx-mechanizmus. Pinelt ellenpélda (2026-08-16): citarabin L01BC01, gemcitabin L01BC05 a „Pyrimidine analogues” alatt; kladribin L01BB04, fludarabin L01BB05 a „Purine analogues” alatt — egyiknek sincs DPYD- vagy TPMT-mechanizmusa.

| Tétel | Eredmény |
| --- | --- |
| L01BC* / L01BB* | **Elvetve marad.** `IIA_SAFE_ATC_PREFIXES` nem tartalmazza. Teszt: 13 blokk + 6 kontroll + 7 HU név. |
| MANIFEST `accessed` | Top-level **2026-08-13** (első kör fagyasztása). Sorok: 2026-08-13 / 14 / 15 / 16 a *pin napja*. A „egységesen 2026-08-13” közlés **pontatlan** volt (E-29); a top-level zárolás szándékos. |
| WHO 5. szint | BA újraellenőrzéskor **58** hatóanyag-oldal (+ 1 structure). Most +4 ellenpélda → **62** hatóanyag + structure. Official pin **92** `ok`. |
| FR-250 HGVS/VRS | **HGVS/VRS előfeltétel: `MATCHER_ON=true`.** N3/V8. `src/`-ben 0 HGVS/VRS implementáció — helyes, amíg a matcher ki. |
| Flag / OQ | `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. OQ **nem** pecsét. |
| Unittest | **237 OK** |

---

## 26. P06an — COM(2025) 1023 F3-elágazás + OQ-05 Q4 (2026-08-16, D-54)

BA: a pivot indoka (hatályos Rule 11 alatt gyakorlatilag nincs Class I MDSW) iparági konszenzus; F3 18–36 hó egyezik ~24 hó NB-kommentárral; COM(2025) 1023 a premisszát később megváltoztathatja. A 2026-os terv **nem** a javaslatra épül.

| Tétel | Eredmény |
| --- | --- |
| A18 | 2026-os stratégia = **hatályos** Rule 11. COM = javaslat. F3 = döntési elágazás. Nem `LIVE_CDS` feloldás. |
| Q4 | OQ-05 counsel-brief: F1+ / L4-live a *javasolt* Rule 11 alatt + A.4.1. Q1–Q3 pecsét változatlan. |
| Pin | S077 COM PDF; S078 SWD; S079 Gleiss L4; S080 EUR-Lex HTML (olvasható Rule 11). Official **96** `ok`. Top-level `accessed` **2026-08-13**. |
| E-30 | MDCG 2024-7 **nem** Rule 11 Q&A; S065 marad B01AC04. |
| Nem `[V]` | 30% összesített teher; 2027 Q2 elfogadás; Have Your Say 03-18; NB 13–18 / 6–12 / 24 hó; G4 WTP. |
| Flag / OQ | `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. OQ **nem** pecsét. |
| Unittest | **241 OK** |

---

## 27. P06ao — OQ-05 teszt-jegyzőkönyv a unittest fából (2026-08-16, D-55)

A user két opciót adott: a 195→241 delta fókusza, vagy OQ-05 pecsét-jegyzőkönyv. A kettő nem verseng. A 46 új teszt a jegyzőkönyv tartalomjegyzéke. A generátor **nem** tölti a V. pecsétet.

| Tétel | Eredmény |
| --- | --- |
| 195→241 | +46. D-50 ops/F1s (F5 fail-open, warfarin státusz, PharmCAT circuit breaker). D-51 F2 IIa-safe + FR-id; FR-250/420/700 = III. D-52 A16/A17 rekord. D-53 L01BC = OQ-06; HGVS-kapu = III.4. D-54 Q4 pin, pecsét nélkül. |
| Generátor | `docs/pce/ProcessArtifacts/BuildScripts/generate_oq05_protocol.py` — AST + zárt evidenciatábla + mapped unittest. Stdlib. |
| Jegyzőkönyv | `OQ-05-TEST-PROTOCOL.md`. Státusz ELŐTERJESZTVE. Q1–Q3/III mapped OK. Q2 és Q4 szoftver:`partial`. |
| E-31 | Brief/G Q1 allow-list **45 → 47**. G §3.2 teszt-szám 124 → 250. |
| Flag / OQ | `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. OQ **nem** pecsét. |
| Unittest | **250 OK** |

---

## 28. P06ap — OQ-05 FELTÉTELLEL-tervezet + R-OPS (2026-08-16, D-56)

A user három V. utat adott (IGEN / FELTÉTELLEL / NEM) és két opciót (záradék-szöveg vs fail-open sprint). A V. pecsét Rule 11, nem szoftver-OQ. A checkbox **üres**.

| Tétel | Eredmény |
| --- | --- |
| IGEN a suite méretéből | **Elvetve.** Q1 szoftver:`partial`. IV.1 nyitva (gén-szintű terápiás szöveg lehet 11a). |
| NEM a fail-openből | **Elvetve.** R-OPS-01/02 shadow/CI ops, nem A.1 Rule 11. |
| FELTÉTELLEL-tervezet | `Outbound/OQ-05-feltetellel-tervezet.md`: három lakat + újra-nyitás; Q4 nem helyettesít; R-OPS dosszié IV. |
| D-56 | Fail-fast **nem** pecsét-előfeltétel. E-31 = 45→47, nem HGVS. |
| Flag / OQ | `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. OQ **nem** pecsét. |
| Unittest | **251 OK** |

---

## 29. P06aq — OQ-05 counsel-küldés citáció, nem REG-030 dosszié (2026-08-16, D-57)

A user a formális counsel-átadás előtt két utat adott: Class I MDSW (G §3.4) REG-dokumentáció áttekintése, vagy a FELTÉTELLEL-tervezet hivatkozásainak ellenőrzése. A V. pecsét Rule 11, nem szoftver-OQ. A checkbox **üres**.

| Tétel | Eredmény |
| --- | --- |
| Küldési kapu | Brief + melléklet-útvonalak + kategóriahiba-mentes záradék. **Nem** a teljes Class I technical file. |
| REG-010 | A melléklet — már a counsel-csomagban. |
| REG-030 | ISO 13485 / 62304 / 14971 QMS, F2-párhuzamos. **Nem** OQ-05 send-blocker. D.1 kezdeti, nem teljes dosszié. |
| E-32 | G §3.2 250 IGEN-érv → mapped **51** / Q3 **10**. Q1 „példa-lelet” → gold JSON, nem PDF. CI `IIA_SAFE_BLOCK`. |
| Flag / OQ | `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. OQ **nem** pecsét. |
| Unittest | **258 OK** |

---

## 30. P06ar — OQ-05 send-pack SHA-256 boríték (2026-08-16, D-58)

A user a kiküldéshez formális tartalomjegyzéket és SHA-256 listát kért (REG-010, gold JSON, D.1, tervezet). A V. pecsét Rule 11, nem szoftver-OQ. A checkbox **üres**.

| Tétel | Eredmény |
| --- | --- |
| Boríték | `Outbound/OQ-05-SEND-PACK.md`. 15 hashed fájl = brief VI. + a négy név. Saját hashét **nem** tartalmazza. |
| REG-030 | **Nincs** a hash-táblában. Nem küldési feltétel. |
| IIA_SAFE_BLOCK | IIa-safe pár-lakat a CI-ben. **Nem** COM(2025) 1023 mentesség. |
| Flag / OQ | `LIVE_CDS=false`; `MATCHER_ON=false`; `IIA_SAFE_BLOCK=true`. OQ **nem** pecsét. |
| Unittest | **261 OK** |

