# Adatfolyam és felhasználói út (B.1 + §5)

| | |
| --- | --- |
| **Spec** | B.1, B.2, B.3, B.4, E.2, §5.1–5.2 |
| **Terv** | [DELIVERY-PLAN.md](DELIVERY-PLAN.md) |
| **Mérés** | [SPEC-PLAN-TRACE.md](SPEC-PLAN-TRACE.md) |

Két elkülönített út. Keverés a klinikai UI-n = NG-07/08. SYN-en mindkettő **ugyanazokkal** a B-szerződésekkel fut, élő HIS/TAJ nélkül.

## 1. Klinikai path (F1+) — laborlelet

```mermaid
flowchart TB
  subgraph actors [Szereplők]
    P4[P4 Tanácsadó]
    P1[P1 Labor aláíró]
    P5[P5 DPO]
    P2[P2 Klinikus - csak aláírt lelet]
  end
  subgraph l0 [L0 Identity]
    Org[Organization license_id]
    Sub[Subject pszeudonim]
    Case[Case DRAFT]
    Coun[CounsellingRecord]
    Cons[ConsentRecord]
    Samp[Sample collected_at]
  end
  subgraph l1 [L1 Ingest]
    OC[OutsideCall JSON vagy TSV]
    VCF[GenomicFile - opcionális]
  end
  subgraph l2l3 [L2-L3]
    Dip[Diplotype callability]
    Ph[Phenotype genotype_only]
  end
  subgraph l4 [L4-static]
    RS[RuleSetVersion]
    Tab[CPIC/DPWG/FDA gén-tábla]
    EDU[phenoconversion_edu vagy null]
  end
  subgraph l6 [L6 Delivery]
    Rep[Report immutable]
    PDF[PDF aláíró hellyel]
    FHIR[FHIR STU3 Bundle]
    JSON[GET reports JSON]
    Exp[Explanation FR-710]
  end
  P4 --> Coun
  P4 --> Cons
  P1 --> Org
  P1 --> OC
  Org --> Case
  Sub --> Case
  Coun --> Case
  Cons --> Case
  Samp --> Case
  Case -->|FR-100 kapu| OC
  OC --> Dip
  VCF -.->|matcher OFF| Dip
  Dip --> Ph
  Ph --> Tab
  RS --> Tab
  Tab --> Rep
  EDU --> Rep
  Rep --> PDF
  Rep --> FHIR
  Rep --> JSON
  Rep --> Exp
  PDF --> P2
  P5 --> Case
```

**Invariánsok**

- L4-static-nak **nincs** `MedicationEntry` / `medications` argumentuma. A lelet a gén guideline-tábláját listázza, nem a felírásból szűr.
- `functional_phenotype` / `live_findings` / `hitl_*` **nincs** a Report JSON-ban.
- Render **409** `E-CONSENT-001..005`, ha a kapu piros — a CLI sem kerülheti meg (FR-100: admin sem).
- Fail-closed a szivárgásra (nincs shadow a PDF-en). A HIS-t ez az út nem blokkolja (nincs HIS a klinikai pathen).

**SYN állapot (2026-08-13 P06u):** a 8 API-lépés HTTP-n zöld (`tests/test_clinical.py`). UI: `src/pce_ui/index.html`, `python -m pce_clinical --mode serve`.

**API sorrend (B.3 / B.4) — labor egy műveletsor**

1. `POST /v1/orgs` + `POST /v1/subjects` + `POST /v1/cases` → `DRAFT`
2. `POST /v1/cases/{id}/counselling` (occurred_at < sample.collected_at)
3. `POST /v1/cases/{id}/consent` (8. § scopes)
4. `POST /v1/cases/{id}/outside-calls` (vagy TSV)
5. `POST /v1/cases/{id}/reports` → kapu → JSON/PDF/FHIR; status `SIGNED` csak aláíró slot kitöltése után
6. `GET /v1/cases/{id}/reports/{rid}`
7. `GET /v1/cases/{id}/explanation` (FR-710)
8. Visszavonás: `POST /v1/subjects/{id}/withdraw` → riport URL `410` `E-GONE-010`

Opcionális: `PUT /v1/cases/{id}/clinical-context` **tárol** a kutatási úthoz. Az aláírt JSON/PDF **nem** ebből a listából készül (FR-220).

---

## 2. Shadow path (F1s) — HITL, nem klinikai kimenet

```mermaid
flowchart TB
  HIS[HIS/LIS recept lezárás vagy lelet aláírás]
  GW[Intézményi gateway FR-460/461]
  KC[Helyi k-cella SQLite]
  ING[POST /v1/shadow/events]
  SI[ShadowInference]
  HITL[HITL store - külön DB]
  UI[HITL UI hitl_reviewer]
  HIS -->|Subscription aszinkron| GW
  GW --> KC
  GW -->|202 fail-open| HIS
  GW --> ING
  ING -->|E-SHADOW-001/002| X[nincs store-írás]
  ING -->|E-SHADOW-003| KC
  ING -->|202 + payload| SI
  SI --> HITL
  HITL --> UI
  SI -.->|FR-470 tilos| R[F1+ Report]
```

**Invariánsok**

- HIS **nem** vár a PCE-re (E.2 fail-open).
- `clinician` → `/v1/hitl/**` = `E-ISO-001`.
- ShadowInference **soha** nem FK a Report-ra.
- F1+ JSON: zárt B.4.1 kulcskészlet; `medications` / `clinical_context` / `hitl_*` reject. A lelet-összeállítás **nem** tölti a gyógyszerlista-táblát.
- ANON: nincs ResearchConsent kapu. PSEUDO: `E-CONSENT-006`.
- Vak mód: 1. lépés motor nélkül; 2. lépés AGREE/DISAGREE.

**HITL kártya (anonim):** `case_display_id`, gén, CLASS vagy RAW a FR-461 szerint, **hatóanyag-kód** (WHO ATC 5. szint, 7 karakter; ha a DPO durvított: csoportkód), `config_id`. Nincs név, TAJ, születési év, orvosnév. Vak lépés után: `forras_allapot` (mi van / mi hiányzik magyarul).

**SYN állapot (2026-08-13 P06x):** a 5 lépés járható. Motor: `src/pce_shadow/`. Tár: `var/hitl.sqlite`. Képernyő: `src/pce_ui/hitl.html`, `python -m pce_hitl`. 7 karakteres paroxetin (`N06AB05`): gén szerinti normál metabolizáló megmarad, funkcionális szegény metabolizáló üres, a hiány ki van írva. 5 karakteres csoportkód (`N06AB`): párosítás szünetel.

---

## 3. Persona UX (SYN, pecsétig)

Minden képernyő a B API-t hívja. Nincs kitalált kórháznév; org = `SYN-ORG-001`.

| Persona | Képernyő / CLI | Happy path | Hibás path | Spec story |
| --- | --- | --- | --- | --- |
| **P4 Tanácsadó** | WP-U: tanácsadás + beleegyezés űrlap | dátum a mintavétel előtt; gén-scope pipák | későbbi dátum → `E-CONSENT-002` HU | 13, 14 |
| **P1 Labor** | WP-U: eset, outside-call feltöltés, előnézet, aláírás | kapu zöld → PDF + JSON + FHIR | kapu piros → nincs PDF; INDETERMINATE gén nem NORMAL | 1–4, 20 |
| **P2 Klinikus** | **nincs** vizit-UI F1+-on | megkapja az aláírt PDF-et / FHIR-t a laborból | nem lát HITL-t, nem kap CDS Cardet | 6–10 LOCK; 9 forrás a PDF-en |
| **P3 Farmakológus** | HITL UI (nem napi vizit) | vak lépés, majd motor | `clinical_context=ABSENT` ha nincs lista | 11–12 |
| **P5 DPO** | audit export, törlési tanúsítvány, A14 monitor | CSV/JSON 30 éves séma; gateway quarterly_report | PII a monitorban = regresszió | 15, 16 |
| **P6 Vendor** | FHIR Bundle + írásos határ (OQ-03) | STU3 DiagnosticReport | CDS endpoint 404 | 17, 18 |
| **HIS** | nem UI | 202, recept lezárul | gateway hiba is 202 a HIS felé | 21 |

**F2/F3 UX** (nem SYN-cél most): order-select Card, fail-open 2 s, „nincs PGx” info Card — WP-P1/F2, `LIVE_CDS` false.

---

## 4. Csatorna-izoláció (ellenőrizhető UX)

| Teszt | Elvárt |
| --- | --- |
| Labor PDF-ben `live_findings` / `functional_phenotype` | nincs |
| `Authorization: clinician` + `GET /v1/hitl/inferences` | 403/404 `E-ISO-001` |
| `GET /cds-services/pgx-order-sign` F1+ build | 404 `E-ISO-002` |
| Renderer kwargs `medications` | `RendererConfigError` |
| Gateway export `SYN-TAJ` / `doseQuantity` / INN (`escitalopram`) | nincs (a **kód** `N06AB10` van) |

---

## 5. Teljes út — SYN gold (nincs zsákutca)

**F1+ klinikai út (WP-C+K+R+F+U+V) — járható**

1. Tanácsadó rögzít SYN counselling + consent (`SYN-MD-001` pecsétszám-hely, nem kitalált orvosnév a gitben: placeholder slot).
2. Labor feltölt `outside-call-cyp2d6-called.json`, **vagy** VCF-et (hiányzó definiáló pozíció → `INDETERMINATE`, nem NORMAL).
3. Kapu enged; report `config_id=pgx-prepare-12@v0`; a meghívott gén CPIC pair sorai (12 gén pin, F5/VKORC1 rec hiány jelezve); A.1.1 minden PDF oldalon.
4. Klinikus a PDF-et kapja — nincs belépése a HITL-re (`E-ISO-001`). A PDF a gén guideline-sorait listázza; nem a beteg aktuális felírásaiból szűrt figyelmeztetés.
5. INDETERMINATE: nincs NORMAL claim.
6. Visszavonás: riport URL `410` `E-GONE-010`.

**F1s kutatási út (WP-G+M+H) — járható**

1. Fixture HIS bundle → gateway → k-cella → `POST /v1/shadow/events`.
2. ANON 7 karakteres kód → 202 (párosítás, ha a kód hatóanyag). TAJ → 400. HIS ettől függetlenül „lezárt”. 5 karakteres csoportkód → HITL sor, párosítás szünetel.
3. Továbbított esemény → ShadowInference a **hitl.sqlite**-ban.
4. Reviewer 1. lépés vak; 2. lépés verdict + `forras_allapot` (van/hiányzik).
5. Report store üres marad ettől az eseménytől.
