# B melléklet — Architektúra, adatmodell, interfészek, SOUP

| | |
| --- | --- |
| **Dokumentum** | PCE-SPEC-v1.1 Appendix B |
| **Dátum** | 2026-08-12 |
| **Kapcsolat** | PCE-SPEC §6; A melléklet modulok |

---

## B.1 Rendszerkontextus

Szereplők: partnerlabor (ISO 15189 / működési engedély), PCE (ez a szoftver), felíró klinikus, genetikai tanácsadó, DPO, (F2+) EHR / medikai rendszer, (F4) PRS-partner, (F4) EESZT a medikai vendoron keresztül.

A v1 labor-UI átmeneti (FR-530). Célállapot: adat az API-n, megjelenés az EHR-ben.

```
[Tanácsadó] → L0 Consent/Counselling
[Labor aláíró] → L1 OutsideCall | VCF
[Klinikus / HIS] → L1 Medication + Observation (kézi P0 / FHIR P1)
L0 → L1 → L2 → L3 → L4 → L6 Report
                 └──────────┘ fenokonverzió input
L6 → PDF, FHIR Bundle STU3, JSON
L6 (F2) → CDS Hooks, SMART
L4/L6 → L7 audit/PMS
```

Tenancy: laboronként (vagy klinikánként) elkülönített adat; genetikai payload EU-régió (NFR-030). Re-ID kulcs külön KMS-ben (FR-130).

---

## B.2 Entitások

Azonosítók: UUID. Genetikai tartalom pszeudonim `subject_id`-hez kötve.

| Entitás | Kötelező mezők | Megjegyzés |
| --- | --- | --- |
| **Organization** | `id`, `name`, `license_id?`, `role` (lab \| clinic \| vendor) | 12. § (1) a lab szerepre |
| **Subject** | `id` (pszeudonim), `reid_key_ref` | Re-ID külön store |
| **Case** | `id`, `subject_id`, `org_id`, `status`, `config_id` | Status: `DRAFT` … `SIGNED` \| `NEEDS_MAPPING` \| `BLOCKED_CONSENT` |
| **CounsellingRecord** | `id`, `case_id`, `counsellor_id`, `occurred_at`, `pre_sampling` | FR-100; `occurred_at` < sample |
| **ConsentRecord** | `id`, `case_id`, `granted_at`, `scopes[]` (gene \| purpose), `withdrawn_at?` | FR-110; 8. § |
| **Sample** | `id`, `case_id`, `collected_at`, `type`, `quantity?`, `origin` | 26. § napló |
| **GenomicFile** | `id`, `case_id`, `format` (VCF42 \| VCF43), `reference` (GRCh37 \| GRCh38), `sha256`, `size` | FR-200 |
| **OutsideCall** | `id`, `case_id`, `gene`, `diplotype`, `calling_lab`, `signing_physician`, `method`, `call_date`, `phenotype?`, `callability?` | FR-240 |
| **Diplotype** | `case_id`, `gene`, `diplotype`, `source` (OUTSIDE \| PHARMCAT), `callability` | CALLED \| PARTIAL \| INDETERMINATE \| NOT_TESTED |
| **Phenotype** | `case_id`, `gene`, `genotype_phenotype`, `activity_score?` | Soha nem overwriteeli a fenokonverzió |
| **FunctionalPhenotype** | `case_id`, `gene`, `functional_phenotype`, `reason[]` (drug \| organ) | FR-410; mellett, nem helyett |
| **MedicationEntry** | `case_id`, `code_system`, `code`, `name`, `source` (MANUAL \| FHIR) | FR-220 |
| **LabObservation** | `case_id`, `loinc`, `value`, `unit`, `effective_at` | eGFR, ALT, … |
| **RuleSetVersion** | `id`, `genes[]`, `rules_hash`, `cpic_ver`, `dpwg_ver`, `fda_ver`, `pheno_ver` | FR-310 |
| **Report** | `id`, `case_id`, `version`, `parent_report_id?`, `formats[]`, `signer_slot`, `immutable` | FR-500/510 |
| **AuditEvent** | `id`, `ts`, `actor`, `action`, `object_type`, `object_id`, `legal_basis`, `prev_hash?` | FR-120; hash P1 |
| **Explanation** | `id`, `case_id`, `report_id`, `body_hu`, `hash` | FR-710; determinisztikus |
| **DeletionCertificate** | `id`, `subject_id`, `issued_at`, `objects_destroyed[]` | FR-110; genetikai tartalom nélkül |

`callability` enum: `CALLED` | `PARTIAL` | `INDETERMINATE` | `NOT_TESTED`.

`clinical_context` enum a riporton: `ABSENT` | `MANUAL` | `FHIR`.

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

P0: JSON `{ medications: [{code_system, code, name}], observations: [{loinc, value, unit, effective_at}] }`.

P1: FHIR R4 Bundle (`MedicationRequest` | `MedicationStatement`, `Observation`). Profile: nem saját IG v1-ben; validáció R4 + kötelező kódolás.

### B.3.4 HL7 v2 LRI — **P1**

`POST /v1/hl7/oru` — `ORU^R01`, v2.5.1. Mapping: OBR/OBX → OutsideCall. Részletes szegmens-tábla a P1 ticketben; v1 nem szállítja.

---

## B.4 Kimeneti szerződések

### B.4.1 JSON riport — `GET /v1/cases/{case_id}/reports/{report_id}`

Kötelező top-level:

```
report_id, case_id, version, config_id,
pipeline_version, pharmcat_version?,
cpic_version, dpwg_version, fda_table_version,
callability_summary: {gene: status},
genes: [{gene, diplotype, genotype_phenotype, functional_phenotype, callability}],
findings: [{gene, drug, atc, severity, statements: [{source, version, evidence, url, text_en, text_hu?}], unsourced: false}],
clinical_context, counselling: {id, at, counsellor_id},
intended_purpose_clause,  // F1 vagy F2 mondat
white_label: {org, signer_slot}
```

Minden `statements[]` elemnek van `source` + `url`. CI: `unsourced == 0`.

### B.4.2 PDF

Oldalanként: config/pipeline verzió, callability-összefoglaló, aláíró hely, intended purpose egy mondat, kolofon (PCE mint tech szállító). White-label: partner logo + név.

### B.4.3 FHIR Genomics Reporting IG STU3

Bundle: `DiagnosticReport` + `Observation` (genotípus, fenotípus, implied) a [hl7.org/fhir/uv/genomics-reporting](http://hl7.org/fhir/uv/genomics-reporting) STU3 szerint. Mapping-réteg elválasztva a STU4 `GenomicStudy` / operations felé (FR-500). Nem implementálunk STU4 operations-t v1-ben.

### B.4.4 CDS Hooks — P1

`POST /cds-services/pgx-order-sign` és `.../pgx-order-select`.

Timeout: 2000 ms hard; a **hívó** fail-open. Ha a PCE > 2 s, a Card elmaradhat — a felírás nem blokkol. Nincs PGx-adat: info Card, nem üres 200.

---

## B.5 Hibakatalógus

| Kód | HTTP | Mikor | Felhasználói szöveg (HU, elv) |
| --- | --- | --- | --- |
| `E-CONSENT-001` | 409 | Nincs tanácsadás | Mintavétel előtti genetikai tanácsadás hiányzik (2008/XXI. 6. § (2)). |
| `E-CONSENT-002` | 409 | Tanácsadás a mintavétel után | A tanácsadásnak a mintavétel előtt kell történnie (6. § (2)). |
| `E-CONSENT-003` | 409 | Nincs 8. § beleegyezés | Írásbeli beleegyezés hiányzik (8. §). |
| `E-CONSENT-004` | 409 | Célon túli gén, nincs ismételt beleegyezés | 15. § |
| `E-CONSENT-005` | 409 | Nincs engedélyezett performing_org | 12. § (1) |
| `E-VCF-001` | 400 | Parse hiba / csonka fájl | A VCF nem olvasható; részleges riport nem készül. |
| `E-VCF-002` | 400 | Multi-sample hozzárendelés hiány | Sample-enként külön eset kell. |
| `E-VCF-003` | 400 | Hiányzó/nem támogatott `##reference` | A referencia-genom hiányzik vagy nem GRCh37/38. |
| `E-VCF-004` | 413 | > 5 GB | |
| `E-CALL-001` | 400 | Üres diplotípus outside-callban | |
| `W-CALL-010` | 409 | Outside-call vs VCF konfliktus | Automatikus választás nincs; emberi döntés. |
| `E-MAP-001` | 409 | `NEEDS_MAPPING` | Ismeretlen gyógyszerkód; a riport nem megy ki hiányos listával. |
| `E-CALLABILITY` | — | génszintű, nem feltétlen HTTP | `INDETERMINATE` a riportban, nem error a case-en, ha más gének CALLED |
| `E-TIMEOUT-CDS` | — | CDS > 2 s | Hívó fail-open; PCE logolja |
| `E-GONE-010` | 410 | Visszavont / törölt riport | FR-110 |

Figyelmeztetés (`W-*`) nem csendes siker. A kliensnek meg kell jelenítenie.

---

## B.6 Fenokonverzió viselkedés

Input: `Phenotype.genotype_phenotype` + `MedicationEntry[]` + opcionális `LabObservation[]`.

Szabálybázis: verziózott inhibitor/induktor tábla (CYP2D6, CYP2C19, CYP3A4/5, …) — **külső config**, mint FR-310. A v1 minimum: erős CYP2D6-inhibitorok (legalább paroxetin, fluoxetin) → NM genotípus mellett funkcionális PM/IM a tábla szerint.

Invariánsok:

1. `genotype_phenotype` immutábilis a fenokonverzió után.
2. `functional_phenotype` csak akkor íródik, ha van klinikai kontextus; különben a riport `clinical_context = ABSENT` és a modul „nem értékelhető”.
3. Nincs `dose_mg`, nincs „csökkentsd X mg-ra”.
4. Szervfunkció: eGFR < 30 vagy a config szerinti bilirubin-küszöb → `reason: organ` flag, nem számított dózis.
5. Determinisztikus (NFR-060).

Gold set: ≥ 90% recall, ≥ 75% precision (PCE-SPEC §9.2).

---

## B.7 SOUP és tudásbázis

IEC 62304 SOUP = szoftver, amelyet nem a gyártó fejlesztett a 62304 szerint, de a termékben van.

| Komponens | Licenc | Szerep | SOUP? | Kontroll |
| --- | --- | --- | --- | --- |
| PharmCAT (NamedAlleleMatcher, Phenotyper, Reporter) | MPL 2.0 | L3 VCF-útvonal | **Igen** | Verzió pin, SBOM, changelog review (F5-eset), derivátum közzététel |
| PharmCAT által hívott programok (pl. matching libraries) | **eltérhet** | L3 | **Igen, külön** | REG-080 tételes lista minden release-nél |
| CPIC guidelines | Közzétett guideline | L4 tartalom | Nem SOUP — **tudásbázis** | Verzió, change-control, FR-510 |
| DPWG / ClinPGx annotáció | Közzétett | L4 | Tudásbázis | Ugyanaz |
| FDA PGx table / labels | Közzétett | L4 | Tudásbázis | Ugyanaz |
| FHIR R4 + Genomics Reporting IG STU3 | HL7 | L6 | SOUP (spec+lib, ha van ref. impl.) | Verzió pin |
| CDS Hooks spec | HL7 | L6 P1 | Spec | — |

SBOM: SPDX, CI-ben. MPL 2.0 copyleft a módosított PharmCAT fájlokra: közzétételi eljárás dokumentálva a QMS-ben, nem „majd később”.

---

## B.8 Biztonsági minimum (NFR-031–033)

- TLS 1.3 in transit; AES-256 at rest; genetikai blob külön kulccsal, mint a re-ID.
- Nincs secret a gitben (gitleaks).
- MFA + RBAC: szerepek `counsellor`, `lab_signer`, `lab_tech`, `clinician`, `dpo`, `admin`. `admin` **nem** írja felül FR-100-at.
- Break-glass: időzített, naplózott, DPO-értesítés.

Részletes threat model a QMS-ben (F2); ez a melléklet nem ISO 27001 SOA.
