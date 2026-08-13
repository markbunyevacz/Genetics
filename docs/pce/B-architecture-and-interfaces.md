# B melléklet — Architektúra, adatmodell, interfészek, SOUP

| | |
| --- | --- |
| **Dokumentum** | PCE-SPEC-v1.2 Appendix B |
| **Dátum** | 2026-08-12 |
| **Kapcsolat** | PCE-SPEC §6; A melléklet modulok; E melléklet shadow/HITL |

Két **elkülönített** adatút. A klinikai path F1+ leletet állít elő. A shadow path L4-live inferenciát ír a HITL store-ba. A kettő keverése a klinikai UI-n = NG-07/08, FR-470.

---

## B.1 Rendszerkontextus

Szereplők: partnerlabor (ISO 15189 / működési engedély), PCE (ez a szoftver), labor aláíró, felíró klinikus, genetikai tanácsadó, DPO, HITL reviewer (kutatási szerep), (F1s) HIS/LIS integrációs motor + intézményi gateway, (F2+) EHR / medikai rendszer, (F4) PRS-partner, (F4) EESZT a medikai vendoron keresztül.

A v1 labor-UI átmeneti (FR-530). Célállapot: adat az API-n, megjelenés az EHR-ben. F1+-ban az EHR-megjelenés **aláírt lelet / enciklopédia**, nem interruptive Card.

```
Klinikai path (F1+):
[Tanácsadó] → L0 Consent/Counselling
[Labor aláíró] → L1 OutsideCall | VCF
L0 → L1 → L2 → L3(outside) → L4-static → L6 Report
L6 → PDF, FHIR Bundle STU3, JSON
L4-static NEM olvassa a MedicationEntry-t (FR-220, FR-400-STATIC)
FR-410-EDU = statikus oktató bekezdés, nem FunctionalPhenotype

Shadow path (F1s) — külön IAM, külön store:
[HIS/LIS: recept lezárás | lelet aláírás]
        → FHIR Subscription
        → Gateway (intézmény zónája, FR-460)
        → L4-live (FR-400-LIVE + FR-410-LIVE)
        → HITL store → HITL UI (FR-450)
L6-report ──X── L4-live   (FR-470)

F2/F3 (csak CE / in-house után, LIVE_CDS):
L4-live → L6-cds (CDS Hooks, SMART)
L4/L6 → L7 audit/PMS
```

Tenancy: laboronként (vagy klinikánként) elkülönített adat; genetikai payload EU-régió (NFR-030). Re-ID kulcs külön KMS-ben (FR-130) — **klinikai** tenancy. Shadow default: irreverzibilis anonimizálás a gatewayen; a gyártónál **nincs** re-ID kulcs (A12).

`LIVE_CDS` compile-time **false** az F1+ buildben (FR-470).

---

## B.2 Entitások

Azonosítók: UUID. Genetikai tartalom a **klinikai** tenancyben pszeudonim `subject_id`-hez kötve.

### B.2.1 Klinikai tenancy

| Entitás | Kötelező mezők | Megjegyzés |
| --- | --- | --- |
| **Organization** | `id`, `name`, `license_id?`, `role` (lab \| clinic \| vendor) | 12. § (1) a lab szerepre |
| **Subject** | `id` (pszeudonim), `reid_key_ref` | Re-ID külön store; **nincs** a shadow store-ban |
| **Case** | `id`, `subject_id`, `org_id`, `status`, `config_id` | Status: `DRAFT` … `SIGNED` \| `NEEDS_MAPPING` \| `BLOCKED_CONSENT` |
| **CounsellingRecord** | `id`, `case_id`, `counsellor_id`, `occurred_at`, `pre_sampling` | FR-100; `occurred_at` < sample |
| **ConsentRecord** | `id`, `case_id`, `granted_at`, `scopes[]` (gene \| purpose), `withdrawn_at?` | FR-110; 8. § |
| **Sample** | `id`, `case_id`, `collected_at`, `type`, `quantity?`, `origin` | 26. § napló |
| **GenomicFile** | `id`, `case_id`, `format` (VCF42 \| VCF43), `reference` (GRCh37 \| GRCh38), `sha256`, `size` | FR-200 |
| **OutsideCall** | `id`, `case_id`, `gene`, `diplotype`, `calling_lab`, `signing_physician`, `method`, `call_date`, `phenotype?`, `callability?` | FR-240 |
| **Diplotype** | `case_id`, `gene`, `diplotype`, `source` (OUTSIDE \| PHARMCAT), `callability` | CALLED \| PARTIAL \| INDETERMINATE \| NOT_TESTED |
| **Phenotype** | `case_id`, `gene`, `genotype_phenotype`, `activity_score?` | Soha nem overwriteeli a fenokonverzió |
| **MedicationEntry** | `case_id`, `code_system`, `code`, `name`, `source` (MANUAL \| FHIR) | FR-220; F1+ leleten **nem** L4-bemenet |
| **LabObservation** | `case_id`, `loinc`, `value`, `unit`, `effective_at` | eGFR, ALT, …; F1+ leleten nem L4-bemenet |
| **RuleSetVersion** | `id`, `genes[]`, `rules_hash`, `cpic_ver`, `dpwg_ver`, `fda_ver`, `pheno_ver` | FR-310 |
| **Report** | `id`, `case_id`, `version`, `parent_report_id?`, `formats[]`, `signer_slot`, `immutable` | FR-500/510; **nincs** `functional_phenotype` F1+-on |
| **AuditEvent** | `id`, `ts`, `actor`, `action`, `object_type`, `object_id`, `legal_basis`, `prev_hash?` | FR-120; hash P1 |
| **Explanation** | `id`, `case_id`, `report_id`, `body_hu`, `hash` | FR-710; determinisztikus |
| **DeletionCertificate** | `id`, `subject_id`, `issued_at`, `objects_destroyed[]` | FR-110 (a); genetikai tartalom nélkül |
| **DsrRequest** | `id`, `subject_id`, `received_at`, `kind` (withdraw \| erasure \| erasure_refused), `response_issued_at?`, `letter_json?` | FR-110 (b); Art. 12(3)/12(4) |
| **DsrLetter** | a `letter_json`; `action_taken` erased \| refused | Nincs diplotípus / VCF |

`callability` enum: `CALLED` | `PARTIAL` | `INDETERMINATE` | `NOT_TESTED`.

`clinical_context` enum a **HITL kártyán** (F1s) és F2-n: `ABSENT` | `MANUAL` | `FHIR`. Az F1+ Report mezője: `medications_applied_to_recommendations: false` (FR-220).

**FunctionalPhenotype nem klinikai Report-entitás F1+-on.** Csak shadow/F2 (B.2.2).

### B.2.2 Shadow / HITL tenancy (FR-440–460)

Külön adatbázis, külön IAM. A klinikai `clinician` szerep **nem** olvassa.

| Entitás | Kötelező mezők | Megjegyzés |
| --- | --- | --- |
| **GatewayEvent** | `id`, `received_at`, `org_id`, `mode` (ANON \| PSEUDO), `payload_hash`, `atc_level`, `time_grain`, `diplotype_granularity`, `suppressed?` | FR-460/461; PII nélküli bundle |
| **ResearchConsent** | `id`, `pseudo_id?`, `granted_at`, `withdrawn_at?` | FR-115; csak álnevesített út; anonim úton nincs |
| **ShadowInference** | `id`, `gateway_event_id`, `config_id`, `diplotypes[]`, `medications[]` (ATC≤4), `functional_phenotype[]`, `live_findings[]`, `clinical_context` | FR-400-LIVE + FR-410-LIVE; **soha** nem FK a Report-ra |
| **HitlReview** | `id`, `inference_id`, `reviewer_id`, `blind_decision?`, `verdict` (AGREE \| DISAGREE \| INSUFFICIENT_DATA), `reason_code`, `reviewed_at` | FR-450 / FR-450-BLIND |
| **BuildFlag** | `LIVE_CDS` | Compile-time; F1+ = `false` |

`live_findings[]` stratégia-kategória (pl. `CONSIDER_ALTERNATIVE`); v1 shadowban **nincs** `dose_mg`.

---

## B.3 Ingest szerződések

### B.3.1 VCF — `POST /v1/cases/{case_id}/files`

- Content-Type: `application/octet-stream` vagy `multipart/form-data`
- Elfogadott: VCFv4.2, VCFv4.3; `.vcf`, `.vcf.gz` + `.tbi`
- Header: `##fileformat`, `##reference` ∈ {GRCh37, GRCh38, hg19, hg38 és kanonikus aliasok}
- Multi-sample: nem merge; `E-VCF-002` ha sample-hozzárendelés hiányzik
- Max 5 GB; felette `E-VCF-004` vagy chunked (`Upload-Offset`)

### B.3.2 Outside-call — `POST /v1/cases/{case_id}/outside-calls`

JSON tömb vagy TSV (`gene`, `diplotype`, `calling_lab`, `signing_physician`, `method`, `call_date`, `phenotype?`, `callability?`).

TSV elválasztó: tab. UTF-8. Üres diplotípus → `E-CALL-001`.

Konfliktus VCF-hívással: `W-CALL-010`, case status `NEEDS_RESOLUTION`.

### B.3.3 Klinikai kontextus — `PUT /v1/cases/{case_id}/clinical-context`

P0 a **shadow/F2** pathen. F1+ lelet **nem** használja L4-bemenetként (FR-220).

P0: JSON `{ medications: [{code_system, code, name}], observations: [{loinc, value, unit, effective_at}] }`.

P1: FHIR R4 Bundle (`MedicationRequest` | `MedicationStatement`, `Observation`). Profile: nem saját IG v1-ben; validáció R4 + kötelező kódolás.

F1+ report-renderer: a lista tárolható a case-en (labor workflow). Az aláírt JSON/PDF a meghívott gén publikált guideline-sorait listázza; **nem** a beteg aktuális felírásaiból szűrt figyelmeztetés. `functional_phenotype` nincs a leleten.

### B.3.4 HL7 v2 LRI — **P1**

`POST /v1/hl7/oru` — `ORU^R01`, v2.5.1. Mapping: OBR/OBX → OutsideCall. Részletes szegmens-tábla a P1 ticketben; v1 nem szállítja.

### B.3.5 Shadow ingest — FHIR Subscription (F1s)

A HIS/LIS **nem** a PCE klinikai API-ját hívja szinkron. Esemény → intézményi gateway → `POST /v1/shadow/events` (csak gateway service-account).

- A PCE **nem** fogad nyers `Patient.name` / TAJ csomagot. Ha a bundle identifier-t tartalmaz, `E-SHADOW-001`, a rekord **nem** kerül a HITL store-ba.
- Álnevesített út: hiányzó `ResearchConsent` → `E-CONSENT-006`, nincs továbbítás.
- Aszinkron: 202 Accepted; a HIS fail-open (E.2).
- Csonkolási szabály: E.3 + E.3.1 (FR-461). Default: 7 karakteres hatóanyag-kód. Pontos `authoredOn` / TAJ / k-alatti cella → `E-SHADOW-001` vagy `E-SHADOW-003`.

---

## B.4 Kimeneti szerződések

### B.4.1 JSON riport — `GET /v1/cases/{case_id}/reports/{report_id}`

F1+ kötelező top-level:

```
report_id, case_id, version, config_id,
pipeline_version, pharmcat_version?,
cpic_version, dpwg_version, fda_table_version,
callability_summary: {gene: status},
genes: [{gene, diplotype, genotype_phenotype, callability}],
findings: [{gene, drug_class_or_table_row, atc?, severity,
            statements: [{source, version, evidence, url, text_en, text_hu?}],
            unsourced: false}],
medications_applied_to_recommendations: false,
phenoconversion_edu: {text, source, version} | null,
counselling: {id, at, counsellor_id},
intended_purpose_clause,   // A.1 mondat
disclaimer_clause,         // A.1.1, FR-490
white_label: {org, signer_slot}
```

**Tilos F1+ JSON-ban (allow-list + deny-list):** a top-level kulcskészlet zárt (`ALLOWED_B41_TOP_LEVEL`). Tiltott mezők, nested is: `functional_phenotype`, `shadow_recommendation`, `dose_mg`, `live_findings`, `medications`, `medication_entries`, `medication_entry`, `MedicationEntry`, `medicationRequest`, `MedicationRequest`, `medicationStatement`, `MedicationStatement`, `clinical_context`, `hitl_review`, `hitl_verdict`, bármely `hitl_*`. Ismeretlen top-level kulcs = hiba. A `medications_applied_to_recommendations: false` **megengedett** (nem gyógyszerlista).

Minden `statements[]` elemnek van `source` + `url`. CI: `unsourced == 0`.

`findings` F1+-on a **génhez** tartozó guideline-tábla sorai (FR-400-STATIC), nem a HIS aktuális `MedicationRequest` párosítása.

### B.4.2 PDF

Oldalanként: config/pipeline verzió, callability-összefoglaló, aláíró hely, A.1 intended purpose, A.1.1 nyilatkozat (FR-490), kolofon (PCE mint tech szállító). White-label: partner logo + név.

Nincs interruptive „csökkentsd a dózist” box. FR-410-EDU ha van: külön, „általános tájékoztató” címkével.

### B.4.3 FHIR Genomics Reporting IG STU3

Bundle: `DiagnosticReport` + `Observation` (genotípus, **genotípus-fenotípus**) a [hl7.org/fhir/uv/genomics-reporting](http://hl7.org/fhir/uv/genomics-reporting) STU3 szerint. Mapping-réteg elválasztva a STU4 `GenomicStudy` / operations felé (FR-500). Nem implementálunk STU4 operations-t v1-ben.

F1+: **nincs** implied `functional_phenotype` Observation a aktuális gyógyszerlistából. `DocumentReference.description` = FR-490 sablon.

### B.4.4 CDS Hooks — **nincs F1+ buildben**; P0 F2

`POST /cds-services/pgx-order-sign` és `.../pgx-order-select`.

F1+ artifact: az endpoint **nincs** kitéve (404, FR-470). F2: timeout 2000 ms hard; a **hívó** fail-open. Nincs PGx-adat: info Card, nem üres 200.

### B.4.5 Enciklopédia — `GET /v1/encyclopedia` (FR-480, P1)

Query: gén és/vagy hatóanyag. Válasz: verziózott guideline-szövegek. **Nincs** `case_id` kötelező; ha a kliens küld `MedicationRequest` id-t, a szerver **nem** állít elő order-sign Cardet.

### B.4.6 HITL API — `/v1/hitl/**` (FR-450)

Külön process (`pce_hitl`). Csak `hitl_reviewer` (és DPO/admin a törléshez). `clinician` → 403/404 (`E-ISO-001`).

`GET /v1/hitl/inferences` — batch kártyák (opák ID, ATC≤4, nincs PII). `POST /v1/hitl/inferences/{id}/blind` — vak döntés. `POST /v1/hitl/inferences/{id}/reviews` — verdict a motor felfedése után.

### B.4.7 Érintetti kérelem (FR-110) — DPO

| Út | Mikor |
| --- | --- |
| `POST /v1/subjects/{id}/withdraw` | 26. § (1) kaszkád + tanúsítvány **és** Art. 12(3) válaszlevél |
| `POST /v1/subjects/{id}/refuse-erasure` | FR-120 megtagadás; genetika marad; Art. 12(4) levél |
| `GET /v1/compliance/dsr` | 30 napnál régebbi levél nélküli kérelem → `E-DSR-OVERDUE` |

---

## B.5 Hibakatalógus

| Kód | HTTP | Mikor | Felhasználói szöveg (HU, elv) |
| --- | --- | --- | --- |
| `E-CONSENT-001` | 409 | Nincs tanácsadás | Mintavétel előtti genetikai tanácsadás hiányzik (2008/XXI. 6. § (2)). |
| `E-CONSENT-002` | 409 | Tanácsadás a mintavétel után | A tanácsadásnak a mintavétel előtt kell történnie (6. § (2)). |
| `E-CONSENT-003` | 409 | Nincs 8. § beleegyezés | Írásbeli beleegyezés hiányzik (8. §). |
| `E-CONSENT-004` | 409 | Célon túli gén, nincs ismételt beleegyezés | 15. § |
| `E-CONSENT-005` | 409 | Nincs engedélyezett performing_org | 12. § (1) |
| `E-CONSENT-006` | 409 | Álnevesített shadow, nincs kutatási hozzájárulás | FR-115; a csomag nem megy a HITL store-ba. |
| `E-VCF-001` | 400 | Parse hiba / csonka fájl | A VCF nem olvasható; részleges riport nem készül. |
| `E-VCF-002` | 400 | Multi-sample hozzárendelés hiány | Sample-enként külön eset kell. |
| `E-VCF-003` | 400 | Hiányzó/nem támogatott `##reference` | A referencia-genom hiányzik vagy nem GRCh37/38. |
| `E-VCF-004` | 413 | > 5 GB | |
| `E-CALL-001` | 400 | Üres diplotípus outside-callban | |
| `W-CALL-010` | 409 | Outside-call vs VCF konfliktus | Automatikus választás nincs; emberi döntés. |
| `E-MAP-001` | 409 | `NEEDS_MAPPING` | Ismeretlen gyógyszerkód; a riport nem megy ki hiányos listával. |
| `E-CALLABILITY` | — | génszintű, nem feltétlen HTTP | `INDETERMINATE` a riportban, nem error a case-en, ha más gének CALLED |
| `E-TIMEOUT-CDS` | — | CDS > 2 s | Hívó fail-open; PCE logolja. **F2 only.** |
| `E-GONE-010` | 410 | Visszavont / törölt riport | FR-110 |
| `E-DSR-OVERDUE` | 200 (riasztás) | 30 napnál régebbi érintetti kérelem válaszlevél nélkül | FR-110 Art. 12(3)/12(4) |
| `E-AUDIT-001` | 409 | Audit UPDATE/DELETE | FR-120 append-only |
| `E-SHADOW-001` | 400 | Gateway kimenet PII-t vagy ATC5-öt / nap-szintű időt tartalmaz | A shadow ingest elutasít; a HIS nem blokkol. |
| `E-SHADOW-002` | 403 | Shadow hívás nem a gateway service-accounttól | |
| `E-SHADOW-003` | 202 | Rekord FR-461 miatt elnyomva (k / ritka diplotípus) | Nincs HITL sor; csak aggregált számláló. |
| `E-ISO-001` | 403/404 | `clinician` a `/shadow/**` vagy `/hitl/**` úton | FR-470 |
| `E-ISO-002` | 404 | CDS endpoint F1+ buildben | `LIVE_CDS=false` |
| `E-EDU-001` | 422 | F1+ renderer tiltott ha–akkor / „Ön” token | FR-410-EDU |

Figyelmeztetés (`W-*`) nem csendes siker. A kliensnek meg kell jelenítenie.

---

## B.6 Fenokonverzió viselkedés

Két üzemmód. Keverésük a aláírt leleten = NG-07.

### B.6.1 FR-410-EDU (F1+ lelet)

Statikus, verziózott bekezdés a guideline/irodalom szerint: mely inhibitor/induktor *osztályok* módosíthatják a funkcionális fenotípust. **Nem** olvassa a `MedicationEntry` listát. **Nem** ír `FunctionalPhenotype` sort. Nem állítja, hogy *ez a beteg* jelenleg fenokonvertált.

Invariánsok (A.1.2): nincs ha–akkor a beteg gyógyszerére; nincs kombinált diplotípus+med-lista hívás; a gén teljes guideline-táblája kimegy. Tiltott tokenek: „Ön”, „ennél a betegnél”, „a most felírt”. `E-EDU-001`.

### B.6.2 FR-410-LIVE (F1s shadow / F2 klinikai UI)

Input: `Phenotype.genotype_phenotype` + `MedicationEntry[]` + opcionális `LabObservation[]`.

Szabálybázis: verziózott inhibitor/induktor tábla (CYP2D6, CYP2C19, CYP3A4/5, …) — **külső config**, mint FR-310. A v1 minimum: erős CYP2D6-inhibitorok (legalább paroxetin, fluoxetin) → NM genotípus mellett funkcionális PM/IM a tábla szerint.

Invariánsok:

1. `genotype_phenotype` immutábilis a fenokonverzió után.
2. `functional_phenotype` csak akkor íródik, ha van klinikai kontextus; különben a HITL/F2 kártya `clinical_context = ABSENT` és a modul „nem értékelhető”.
3. Nincs `dose_mg` a v1 shadowban; stratégia-kategória megengedett.
4. Szervfunkció: eGFR < 30 vagy a config szerinti bilirubin-küszöb → `reason: organ` flag, nem számított dózis.
5. Determinisztikus (NFR-060).
6. F1+ report-renderer **nem** hívja ezt a modult (FR-470 CI).

Gold set: ≥ 90% recall, ≥ 75% precision a **shadow** mintán (PCE-SPEC §9.2, G3). Az aláírt F1+ leleten élő alkalmazás = **0**.

---

## B.7 SOUP és tudásbázis

IEC 62304 SOUP = szoftver, amelyet nem a gyártó fejlesztett a 62304 szerint, de a termékben van.

| Komponens | Licenc | Szerep | SOUP? | Kontroll |
| --- | --- | --- | --- | --- |
| PharmCAT (NamedAlleleMatcher, Phenotyper, Reporter) | MPL 2.0 | L3 VCF-útvonal | **Igen** | Verzió pin, SBOM, changelog review (F5-eset), derivátum közzététel |
| PharmCAT által hívott programok (pl. matching libraries) | **eltérhet** | L3 | **Igen, külön** | REG-080 tételes lista minden release-nél |
| CPIC guidelines | Közzétett guideline | L4-static / L4-live tartalom | Nem SOUP — **tudásbázis** | Verzió, change-control, FR-510 |
| DPWG / ClinPGx annotáció | Közzétett | L4 | Tudásbázis | Ugyanaz |
| FDA PGx table / labels | Közzétett | L4 | Tudásbázis | Ugyanaz |
| FHIR R4 + Genomics Reporting IG STU3 | HL7 | L6 | SOUP (spec+lib, ha van ref. impl.) | Verzió pin |
| FHIR Subscription / webhook kliens | HL7 / lib | L1 F1s | SOUP ha lib | Verzió pin; csak gateway→PCE |
| CDS Hooks spec | HL7 | L6 F2 | Spec | F1+ buildben nincs runtime |

SBOM: SPDX, CI-ben. MPL 2.0 copyleft a módosított PharmCAT fájlokra: közzétételi eljárás dokumentálva a QMS-ben, nem „majd később”.

A gateway **intézményi** komponens: a partner SOUP/QMS-e, nem a PCE klinikai release-e; a PCE a csonkolt bundle szerződést (E.3) teszteli.

---

## B.8 Biztonsági minimum (NFR-031–033)

- TLS 1.3 in transit; AES-256 at rest; genetikai blob külön kulccsal, mint a re-ID (klinikai tenancy).
- Shadow store: külön titkosítási kulcs; nincs join-key a klinikai `Subject.reid_key_ref`-hez.
- Nincs secret a gitben (gitleaks).
- MFA + RBAC: szerepek `counsellor`, `lab_signer`, `lab_tech`, `clinician`, `hitl_reviewer`, `dpo`, `admin`. `admin` **nem** írja felül FR-100-at. `clinician` ≠ `hitl_reviewer` (FR-450).
- Break-glass: időzített, naplózott, DPO-értesítés.
- Gateway: intézményi zóna; a PCE felhő PII-t elutasít (`E-SHADOW-001`).

Részletes threat model a QMS-ben (F2); ez a melléklet nem ISO 27001 SOA.

---

## B.9 Csatorna-izoláció (FR-470) — architektúra-teszt

CI / call-graph (E.8):

1. A report-renderer modul **nem** függ a shadow-writer kimeneti táblájától.
2. F1+ build: `LIVE_CDS=false`; CDS router nincs a binaryben vagy 404.
3. Integrációs teszt: adott `ShadowInference` mellett a Report JSON schema rejecteli a tiltott mezőket.
4. IAM teszt: `clinician` token → `/v1/hitl/**` = `E-ISO-001`.
