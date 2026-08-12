# A melléklet — Intended purpose és modul-minősítés

| | |
| --- | --- |
| **Dokumentum** | PCE-SPEC-v1.1 Appendix A |
| **Dátum** | 2026-08-12 |
| **Jogalap** | MDCG 2019-11 Rev.1 (2025-06-17); MDR Annex VIII Rule 11 |
| **Státusz** | Tényalap OQ-05-höz — **nem** jogi állásfoglalás |

A MDCG Rev.1 szerint a minősítés és az osztályozás az **intended purpose**-ön áll vagy dől. A gyártónak minden modult önállóan kell minősítenie, a határokat és a függőségeket dokumentálnia, és a felhasználónak egyértelműen közölnie, mely modul MDSW.

Ez a melléklet két, **egymást kizáró** szándéknyilatkozatot rögzít. Egyszerre mindkettő nem lehet igaz ugyanarra a kiadott szoftververzióra.

---

## A.1 F1 intended purpose — laboratóriumi riport-előállítás

**Rendeltetés (tervezet, counsel előtt):**

A PCE F1 a partnerlaboratórium — mint a 2008. évi XXI. tv. 12. § (1) szerinti engedélyezett egészségügyi szolgáltató — számára white-label **riport-előállító** szoftver. A bemenet a labor aláíró orvosa által **már megállapított** diplotípus (és opcionálisan fenotípus) + a beteg aktuális gyógyszerlistája és szervfunkciós adatai. A kimenet verziózott CPIC / DPWG / FDA-címke **szövegének** a diplotípushoz rendelése, callability-jelöléssel, fenokonverzió-minősítéssel (nem dózisszámmal), PDF és FHIR formában. Az aláíró a labor orvosa. A szoftver **nem** ad utasítást a felírásra, **nem** jelenik meg a felírási workflow interruptive riasztásaként, **nem** számít dózist.

**Amit szándékosan nem állít:**

- diagnózis, prognózis, predikció, kezelés vagy annak enyhítése mint a szoftver saját orvosi célja;
- „a rendszer javasolja a gyógyszert / dózist”;
- order-sign / order-select CDS;
- nyers labor-adatból (FASTQ, IDAT, intensity) genotípus-hívás.

**MDSW-indoklás (gyártói, nem tanácsadói):** L0–L2 adminisztráció, tárolás, kommunikáció, adatátalakítás. L3 a labor felelőssége (outside-call). L4 a v1-ben „irodalmi szöveg hozzárendelése aláírásra”, nem terápiás döntéstámogatás. Ez a mondat **OQ-05 tárgya**. Ha a counsel szerint a gyógyszerajánlás-szöveg önmagában Rule 11a, az F1 intended purpose érvénytelen, és az F1 build F3-ba esik.

**Konfigurációs tilalom F1-ben:**

- FR-300 `NamedAlleleMatcher` default **OFF**. Bekapcsolás = intended purpose változás = REG-010 újra.
- FR-520/530 **OFF**.
- FR-410 kimenet: `functional_phenotype` minősítés, `dose_mg` mező tilos.
- FR-430 PRS: nincs hívás.

---

## A.2 F2/F3 intended purpose — PGx-CDSS

**Rendeltetés (tervezet):**

A PCE F2/F3 farmakogenetikai **klinikai döntéstámogató** szoftver. A felírás vagy medication review pillanatában a beteg diplotípusa, aktuális gyógyszerlistája és szervfunkciója alapján információt szolgáltat, amelyet a klinikus **terápiás döntéshez** használ: actionable gén–gyógyszer interakció, forrásolt alternatíva, fenokonverzió-minősítés. Kimenet: CDS Hooks Card (`order-select` / `order-sign`) és/vagy SMART on FHIR nézet az EHR-en belül.

**Minősítés:** MDSW. **Osztály:** Rule **11a → IIa** default (információ terápiás döntéshez). IIb/III akkor, ha a döntés hatása a Rule 11a kivételekbe esik — PGx-dózis/alternatíva jellemzően IIa, de a DPYD–fluoropirimidin típusú, életveszélyes toxicitású párok **külön kockázatelemzést** igényelnek (D melléklet R-007). Nem Class I.

**F2 vs F3:** F2 in-house, egy intézmény, REG-011. F3 CE-jelölt, Notified Body, piaci forgalomba hozatal.

---

## A.3 L0–L7 modul-minősítési mátrix

MDCG Rev.1: a nem-MDSW modul interfészét akkor is dokumentálni kell, ha az MDSW rá támaszkodik. A host UI (EHR) nem MDSW attól, hogy MDSW-t futtat — de a gyártó a host interfészt usability/clinical performance részeként értékeli.

| Modul | Tartalom | F1 intended purpose | MDSW? | Osztály (ha MDSW) | Felelős | Függőségek |
| --- | --- | --- | --- | --- | --- | --- |
| **L0** Identity & Consent | Azonosítás, 6. § (2)/8. § kapu, granuláris consent, 30 éves napló, visszavonás | Adminisztráció, jogi kapu | **Nem** | — | PCE | — |
| **L1** Ingestion | VCF/gVCF, outside-call, (P1) FHIR/HL7 | Tárolás / kommunikáció | **Nem** | — | PCE fogad, labor küld | L0 kapu |
| **L2** Normalization | HGVS/VRS, ATC/LOINC/SNOMED mapping | Adatátalakítás | **Nem** | — | PCE | L1 |
| **L3** Genotype→Phenotype | PharmCAT matcher/phenotyper **vagy** outside-call echo | F1: labor hívása, PCE csak befogad. VCF-matcher = határ. | **Határ** | Ha a PCE hív nyers/variáns adatból diplotípust: MDSW-kockázat (OQ-05) | **Labor** (F1 default); PCE csak ha matcher ON | L2; SOUP PharmCAT |
| **L4** Knowledge & Rules | CPIC/DPWG/FDA szabálybázis, fenokonverzió, szervfunkció-flag | F1: szöveghozzárendelés aláírásra. F2/F3: terápiás információ. | **Igen, ha 11a** | **IIa** default | PCE | L3 diplotípus; L1 gyógyszerlista |
| **L5** PRS | Partner score → percentilis / abszolút kockázat | F1: nincs. F4: prediktív. | **Igen** | **IIa** (predikció/prognózis) | Partner gyártó + PCE mint integrator | L1 genom; ancestry |
| **L6** Delivery | PDF/FHIR riport; CDS Hooks; SMART | F1: riport = L4 kiterjesztése. F2: CDS = L4 kiterjesztése. | L4-gyel együtt | L4 osztálya | PCE; EHR host nem MDSW | L4, (L5) |
| **L7** Observability | Override, PMS/PMCF, drift | Post-market / AI Act Art. 12/72 | Nem önálló MDSW | — | PCE | L4/L6 események |

### L3 határ — YouScript vs Translational Software

A brief és a v1.0 szerint a Translational Software 510(k) azon bukott, hogy nyers labor-adatból genotípus- és fenotípus-hívást végzett; a YouScript laborriportból (már jóváhagyott hívás) indult. `[R]` — egy szaklap-forrás, I-01.

**F1 default:** FR-240 outside-call. A PCE nem állítja, hogy ő hívta a diplotípust.

**Ha FR-300 matcher ON:** a PCE VCF-ből allélt/diplotípust állít elő. Ez a MDCG döntési fán közelebb van az MDSW-hez, még akkor is, ha a labor orvosa aláír. **Bekapcsolás = OQ-05 újra + REG-010.**

---

## A.4 Modul-függőségek (dokumentálandó a technical file-ban)

```
L0 ──► L1 ──► L2 ──► L3 ──► L4 ──► L6
              │              ▲
              │              │
              └──────────────┘  (gyógyszerlista, Observation → fenokonverzió)
Partnerlabor ──► L1 (outside-call | VCF)
L5 (F4) ─ ─ ► L6
L4/L6 ──► L7
EHR host UI ──► L6 (SMART / CDS Hooks); a host nem MDSW, az interfész igen, értékelendő
```

A gyártó közli a felhasználóval:

1. mely modulok alkotják a terméket;
2. mely modulok esnek MDR/IVDR vagy más jog (EHDS, 2008/XXI.) alá;
3. hogy a labor aláírása mit fed és mit nem (REG-020).

---

## A.5 Class I — mit állítunk és mit nem

`[CORRECTED]` VC-04.

- Az MDCG Rev.1 IMDRF-táblája: „This table does not take into account MDSW which is Class I.”
- Rule 11c: minden egyéb MDSW Class I.
- Rev.1 Annex IV: új Class I példa.

**Következtetés, amit ez a melléklet levon:** Class I MDSW **létezik**, de a PGx-ajánlást / terápiás információt adó szoftver **nem** 11c. A „Class I-re menekülés” F2/F3-ra nem stratégia. Az F1 menekülés **nem-MDSW** (admin/riport), nem Class I.

---

## A.6 In-house (F2) — feltételek, nem kiskapu

REG-011. Az in-house (MDR Art. 5(5) szellemében, egészségügyi intézmény) **nem** mentesít a 2008/XXI. alól, **nem** mentesít a GDPR alól, és csak akkor kerüli el a magas kockázatú AI-t (MDCG 2025-6), ha nincs NB a megfelelőségértékelésben **és** a szoftver kizárólag az intézményben fut.

Ha az in-house eszköz kikerül az intézményből (más kórház, SaaS, white-label laborhálózat), az F2 intended purpose megszűnik → F3.

---

## A.7 OQ-05 — a kérdés, amit ez a dokumentum *nem* válaszol meg

> Védhető-e az A.1 F1 pozíció az MDCG 2019-11 Rev.1 alatt, ha a PDF/FHIR kimenet CPIC/DPWG/FDA gyógyszerajánlás-szöveget tartalmaz, az aláíró pedig a partnerlabor orvosa, és nincs CDS Hooks?

A counsel brief **nem** ennek a csomagnak a része. A counselnek adandó csomag: A.1 szöveg, A.3 mátrix, FR-400/410/500, REG-010/020, MDCG Rev.1 modules fejezet (S005).
