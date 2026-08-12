# Precision Clinical Engine (PCE) — Termékspecifikáció és követelménylista

| | |
| --- | --- |
| **Dokumentum-ID** | PCE-SPEC-v1.1 |
| **Státusz** | Draft — review-ra kész |
| **Dátum** | 2026-08-12 |
| **Hatókör** | PGx clinical decision support platform, magyar/EU piac |
| **Előző** | PCE-SPEC-v1.0 (2026-08-09) — váz; ez a kanonikus |
| **Mellékletek** | [A](A-intended-purpose-and-modules.md) · [B](B-architecture-and-interfaces.md) · [C](C-eeszt-f0-checklist.md) · [D](D-risk-and-traceability.md) |
| **Következő gate** | P01 — independent build-readiness review; blokkoló: **OQ-05** |

Jelölések: `[V]` primerben verifikált · `[R]` egy forrás · `[C]` céges közlés · `[CORRECTED]` a v1.0-hoz képest javítva · `[ASSUMPTION]` · `[NEEDS VERIFICATION]`.

---

## 0. Hatóköri feltevések (explicit, nem validált)

Kérdés helyett rögzítve. Ha bármelyik hamis, a jelzett szakasz újraírandó.

| # | Feltevés | Ha hamis, érintett szakasz |
| --- | --- | --- |
| A1 | A v1 célja **bevételtermelő F1 réteg** 9 hónapon belül; a szabályozott CDSS (IIa) a v2 (F2/F3). Az F1 nem-MDSW státusz **OQ-05-től függ**, nem előfeltétel. | Teljes §6, §11, A melléklet |
| A2 | Nincs saját ISO 15189 / CLIA labor; a genotípus-hívás **partnerlabor felelőssége**. Az F1 default útvonal: **outside-call** (FR-240), nem nyers VCF→allélhívás. | FR-240, FR-300, REG-020, A melléklet L3 |
| A3 | Nincs jelenleg érvényes EESZT fejlesztői regisztráció. | §11, REG-040a, C melléklet |
| A4 | A PRS-motor **nem** saját fejlesztés, hanem beszállítói integráció (F4). | §6.5, NG-02, FR-430 |
| A5 | Első aktív-CDSS referencia egyetemi/klinikai partnernél, in-house kivétellel (F2). | REG-011, §11 F2 |
| A6 | Csapatméret v1-re: 2–3 fejlesztő + 1 QA/RA + 1 klinikai szakértő (részidős). Minimum, nem komfortos. | §11 |
| A7 | Elsődleges UI-nyelv magyar; a klinikai ajánlás-szöveg HU, ha szakmai lektor van, különben az angol eredeti. | FR-610 |
| A8 | EESZT-útvonal F1-ben: **modul** az engedélyezett medikai rendszerben, nem saját EESZT-csatlakozás (NG-05). A 2026-09-30 ISO 9001 akkor is F0, ha a vevő a vendor. | REG-040a, C melléklet |
| A9 | A gyártó a `genetics` repo tulajdonos szervezete. **Név ebben a dokumentumban nincs kitalálva.** | Fejléc, REG-031 |
| A10 | `[ASSUMPTION]` A hozzájárulás-visszavonás kaszkádjának **üzemi SLA-ja 72 óra**. A 2008/XXI. 26. § (1) határidőt nem ad. | FR-110 |

**Nem feltevés, hanem verifikált korlát:** a hazai jogi és EESZT-korlátok (§4) nem tárgyalhatók terméktervezéssel.

**Prioritás-szótár (write-spec + compliance):**

| Címke | Jelentés |
| --- | --- |
| **Product P0** | Nélküle az F1 labor white-label nem oldja meg a magproblémát |
| **Compliance P0** | Jogszabály / biztonság; **nem kapcsolható ki** |
| **P1** | Fast follow; a mag use case nélküle is működik |
| **P2** | Architekturális biztosíték; most nem épül |

---

## 1. Problem Statement

A gyógyszerelési döntés pillanatában a rendelkezésre álló genetikai információ nem hasznosul. A magyar magánegészségügyben egy farmakogenetikai vizsgálat 2026 augusztusában **499 000 Ft** listaáron szerepel (Genetix DrugMap, 140+ gyógyszer) `[R]` — I-01, 2026-08-09 lekérdezés, ebben a körben nem ismételve. A nemzetközi kiskereskedelmi sáv a brief szerint jellemzően 250–2000 USD, a többség 300–600 USD `[R]`. A felárat nem a szekvenálás, hanem a hiányzó, skálázható értelmezési infrastruktúra fizeti meg: a labor PDF-et ad, a PDF a beteg fiókjában landol, a felíró orvos hónapokkal később nem látja.

A nem-megoldás költsége: a hazai laborok és klinikák statikus riportot adnak el prémium áron, klinikai hatás nélkül; a nemzetközi PGx-CDSS szállítók EU-jelenléte szűk; az AI Act Annex I tervezési óra (`[NEEDS VERIFICATION]` 2028-08-02, lásd §4.4) után az utólagos megfelelés drágább, mint a beépített.

A differenciátor **nem** a VCF+PRS dashboard, hanem a **fenokonverzió**: a genotípus-alapú fenotípus mellett a aktuális gyógyszerlista (inhibitor/induktor) és a szervfunkció alapján jelzett funkcionális fenotípus. A v1 ezt minősítésként adja, dózisszám nélkül (FR-410).

---

## 2. Goals

Outcome-ok, nem output-ok.

| ID | Goal | Célérték | Mérés |
| --- | --- | --- | --- |
| **G1** | A partnerlabor PGx-riport előállítási ideje csökkenjen | Kézi/félautomata baseline → **p95 < 10 perc** outside-call-tól vagy VCF-től aláírásra kész riportig | Pipeline-telemetria, `ingest→report_ready` |
| **G2** | Az actionable találatok ne vesszenek el | A **PREPARE 12-génes** panel + aktuális CPIC/DPWG szerint actionable gén–gyógyszer párok **100%-a** megjelenik, 0 silent drop | Gold set (§9), minden release |
| **G3** | Fenokonverzió-detektálás mint differenciátor | Fenokonverzió-gyanús esetek **≥ 90% recall** a gold seten | Gold set, §9.2 |
| **G4** | Bevétel a szabályozott réteg előtt | **≥ 3 fizető labor/klinikai partner** és ≥ 1 dokumentált case study a v1 végéig | Aláírt szerződések |
| **G5** | A v2 (IIa) útvonal ne igényeljen újraírást | QMS-artefaktumok (ISO 13485 / IEC 62304 / ISO 14971) **a v1-gyel párhuzamosan** keletkeznek | RA gap-analysis, §8 REG-030 |

**Üzleti goal, amit nem a termék teljesít:** az MKIK-akkreditációhoz szükséges referenciák. G4 ezt szolgálja.

### 2.1 Success metrics (write-spec)

**Leading (napok–hetek):**

| Metrika | Success | Stretch | Módszer | Ablak |
| --- | --- | --- | --- | --- |
| Riport p95 átfutás | < 10 min | < 5 min | telemetria | első 30 nap / partner |
| Callability false-NORMAL | **0** | 0 | gold set FR-210 | minden release |
| Unsourced claim | **0** | 0 | CI `unsourced_claims` | minden release |
| Fenokonverzió recall | ≥ 90% | ≥ 95% | gold set | minden release |

**Lagging (hónapok):**

| Metrika | Success | Stretch | Módszer |
| --- | --- | --- | --- |
| Fizető partner | ≥ 3 | ≥ 5 | szerződés |
| Override-ráta actionable riasztáson (F2+) | < 40% | < 25% | FR-600 |
| Guideline-váltás utáni recall-kampány lefedettség | 100% érintett eset listázva | 100% + betegértesítés workflow | FR-510 |

---

## 3. Non-Goals

| ID | Nem célja a v1-nek | Miért |
| --- | --- | --- |
| **NG-01** | Saját genotípus-hívás nyers labor-adatból (FASTQ/IDAT/raw intensity) | Translational Software 510(k) bukásának mintája `[R]`. L3 a partnerlabor akkreditált köre. |
| **NG-02** | Saját PRS-motor fejlesztése és validálása | Telített, ISO 13485-es piac; validáció többkohorszos; magyar referencia-genom hiányában kalibrálni sem. |
| **NG-03** | Közvetlen betegoldali (B2C) VCF-feltöltés és riport | 2008/XXI. 12. § (1): vizsgálat csak engedélyezett szolgáltatónál. |
| **NG-04** | Onkológiai szomatikus variáns-interpretáció | Külön IVDR-domain. |
| **NG-05** | EESZT írási művelet (eRecept, eProfil rögzítés) | BM-engedélyezett medikai rendszer nélkül nem lehetséges. A v1 modul, nem helyettesítő. |
| **NG-06** | LLM-alapú szabad szöveges klinikai tanácsadás | Nem determinisztikus; IIa dossziét megölné. FR-700. |

---

## 4. Kötelező korlátok (verifikált, nem tárgyalható)

### 4.1 EU MDR / MDSW

- **MDCG 2019-11 Rev.1** (2025-06-17) `[V]`: a szoftvert a **intended purpose** alapján kell minősíteni; a prognózis/predikció a Rule 11 hatókörébe esik; **minden modult önállóan** kell minősíteni, a modulok közti függőségeket dokumentálni.
- Rule **11a**: információ diagnosztikai vagy terápiás döntéshez → **IIa**, kivéve ha a döntés halált / irreverzibilis romlást (III) vagy súlyos romlást / sebészi beavatkozást (IIb) okozhat.
- `[CORRECTED]` Az IMDRF-leképező tábla **nem** tartalmazza a Class I-et; ez **nem** jelenti, hogy Class I MDSW ne létezne. Rule **11c** („all other software”) Class I; a Rev.1 Annex IV új Class I példát adott. PGx-ajánlást / terápiás információt adó kimenet **11a → IIa default**.
- Az „a végső döntést az orvos hozza” érvelés az FDA 2022 CDS guidance logikája, az MDR-ben **nem** minősít ki.

Részlet: [A melléklet](A-intended-purpose-and-modules.md).

### 4.2 Magyar humángenetikai törvény — 2008. évi XXI. tv. `[V]`

| Téma | Joghely | Követelmény |
| --- | --- | --- |
| Mintavétel előtti tanácsadás | **6. § (2)** | Cél, előny/kockázat (elvégzés *és* elmaradás), következmények, tárolás, azonosíthatóság |
| Eredmény közlése | **6. § (4)** | Egyéniesített tájékoztatás genetikai tanácsadás keretében |
| Algoritmus-magyarázat | **6. § (6)** | Automatizált feldolgozás/kódolás: az érintettet kérelmére tájékoztatni kell az informatikai módszerről |
| Jog a nem-tudáshoz | **6. § (7)** | Az érintett lemondhat adatai megismeréséről; a nyilatkozat visszavonható |
| Írásbeli beleegyezés | **8. §** | Mintavétel előtt, tájékoztatáson alapuló, írásban |
| Engedélyezett szolgáltató | **12. § (1)** | Szakmai minimumfeltételek + működési engedély |
| Célhoz kötöttség | **13. § (1), 15. §** | Megelőzés/diagnózis/terápia/rehabilitáció/kutatás, egészségügyi érdek; célon túli vizsgálat ismételt beleegyezés |
| 30 éves nyilvántartás | **26. § (1)** | Minta, adat, eljárás, továbbítás; visszavonáskor — tájékoztatás után — minden genetikai nyilvántartás megsemmisítése |

`[CORRECTED]` A v1.0 FR-100 tévesen a 8. §-t citálta tanácsadás-kapuként.

### 4.3 EESZT `[V]` `[CORRECTED]`

- Csatlakozásra kizárólag a működtető (BM) által **engedélyezett** szoftver. A Szolgáltatóközpont (ESZFK) végzi a műszaki bevizsgálást (5/F. §).
- Fejlesztői regisztráció a Redmine-felületen; 4. melléklet gazdasági + tanúsítási feltételek.
- Már engedélyezett / korábban regisztrált fejlesztők: regisztráció **2025-10-31**-ig (lejárt). **4. melléklet 2. pont** (ISO 9001 vagy egyéb szoftverfejlesztési QMS) **2026-09-30**-ig. Elmulasztás → engedély visszavonható (9/C. §).
- `[CORRECTED]` Ez **nem** ISO 13485 és **nem** ISO 27001. Az ISO 13485 az MDR pálya (REG-030). Az ISO 27001 enterprise/biztonság (REG-070), nem az EESZT 9/C. § tárgya.

Részlet: [C melléklet](C-eeszt-f0-checklist.md).

### 4.4 AI Act

- **MDCG 2025-6 / AIB 2025-1** (2025-06-19) `[V]`: MDAI magas kockázatú az Art. 6(1) szerint, ha (i) biztonsági komponens vagy maga eszköz, **és** (ii) MDR/IVDR szerinti harmadik feles megfelelőségértékelés alá esik. Class I nem MDAI. In-house, intézményen belül, NB nélkül jellemzően nem magas kockázatú.
- Digital Omnibus: Annex III → 2027-12-02, Annex I → **2028-08-02** `[NEEDS VERIFICATION]` (I-01: Tanács 2026-06-29, EP 2026-06-16; OJ-közzététel ebben a körben nem letöltve). **Tervezési órának megtartjuk.**
- Art. 4 AI literacy **nem** halasztott; 2025-02-02 óta alkalmazandó `[R]`.

### 4.5 EHDS — (EU) 2025/327 `[V]`

- Másodlagos felhasználás a legtöbb kategóriára 2029-03-26; **humán genetikai és klinikai vizsgálati adatra** hatéves átmenet → **2031-03-26**.
- EHDS-alapú adatmonetizációra 2031 előtt nem lehet üzleti tervet építeni. Interoperabilitás *ma* tervezési NFR (NFR-050).

---

## 5. Personák és user story-k

### 5.1 Personák

| P | Persona | Kontextus | Fő fájdalom |
| --- | --- | --- | --- |
| **P1** | Labor-vezető / molekuláris genetikus | Panel- vagy WES-adatból riport | Kézi értelmezés, verzió nélküli sablon, CPIC-követés |
| **P2** | Felíró klinikus | 12 perc/beteg, gyógyszert ír | Nem látja a PGx-et a felírás pillanatában |
| **P3** | Klinikai farmakológus / gyógyszerész | Medication review | Fenokonverzió és DDI kézi összevetése |
| **P4** | Genetikai tanácsadó | 2008/XXI. kötelező konzultáció | Nincs strukturált tanácsadás- és hozzájárulás-eszköz |
| **P5** | Klinika-üzemeltető / DPO | Compliance | 30 év, visszavonás, audit |
| **P6** | Medikai rendszer szállító | Integrációs partner | Nem akar MDR-gyártóvá válni |

### 5.2 User story-k (prioritási sorrend)

**P1 — Labor**

1. Labor-vezetőként egy művelettel akarok a laborom által már megállapított diplotípusból (vagy lefedett VCF-ből) standardizált PGx-riportot, hogy ne kelljen kézzel CPIC-táblákat értelmeznem.
2. Labor-vezetőként látni akarom, melyik guideline-verzió alapján készült a riport, hogy hat hónappal később rekonstruálni tudjam.
3. Labor-vezetőként azt akarom, hogy a rendszer jelezze, ha a VCF nem fedi a panel egy génjét, hogy ne adjak ki hamis „normál” eredményt.
4. Labor-vezetőként a riportot saját arculatommal és aláíró orvosommal akarom kiadni, hogy a saját szolgáltatásom része legyen.
5. Labor-vezetőként újra akarom generálni a régi riportokat új guideline-verzióval, hogy lássam, kit kell visszahívni.

**P2 — Klinikus**

6. Felíró klinikusként a felírás pillanatában akarok figyelmeztetést, ha a beteg genotípusa a tervezett gyógyszerrel ütközik — nem külön portálon. *(F2; v1-ben P1)*
7. Felíró klinikusként konkrét, forrásolt alternatívát akarok látni, nem csak tiltást.
8. Felíró klinikusként el akarom tudni utasítani a figyelmeztetést indoklással, hogy a rendszer ne blokkolja a megítélésemet.
9. Felíró klinikusként a hivatkozást (CPIC/DPWG/FDA) akarom látni.
10. Felíró klinikusként nem akarok riasztást nem-actionable párra.

**P3 — Klinikai farmakológus**

11. Klinikai farmakológusként a beteg aktuális gyógyszerlistája alapján akarom látni a gyógyszer-indukált fenokonverziót, hogy ne NM-ként kezeljek egy funkcionálisan lassú metabolizálót.
12. Klinikai farmakológusként egy oldalon akarom látni a genotípust, a DDI-t és a szervfunkciós módosítókat.

**P4 — Genetikai tanácsadó**

13. Genetikai tanácsadóként azt akarom, hogy a rendszer ne engedjen riportot kiadni, amíg a mintavétel előtti tanácsadás és a 8. § szerinti beleegyezés nincs dokumentálva.
14. Genetikai tanácsadóként génenkénti/indikációnkénti hozzájárulást akarok rögzíteni, hogy a beteg élhessen a 6. § (7) szerinti nem-tudás jogával.

**P5 — Compliance**

15. DPO-ként a hozzájárulás visszavonása kaszkádolva töröljön minden genetikai adatot és nyilvántartást, és erről tanúsítvány készüljön.
16. DPO-ként exportálható audit trailt akarok minden genetikai adathozzáférésről.

**P6 — Integrációs partner**

17. Medikai szállítóként szabvány FHIR/CDS Hooks felületet akarok, hogy ne kelljen üzleti logikát építenem.
18. Medikai szállítóként írásban rögzített MDR-felelősségi határvonalat akarok.

**Edge**

19. Klinikusként, ha nincs PGx-adat, a rendszer ezt explicit mondja meg.
20. Labor-vezetőként hibás/csonka VCF esetén beszédes hibát akarok, ne részleges riportot.
21. Klinikusként, ha a CDS nem elérhető, a felírás ne blokkolódjon.

---

## 6. Funkcionális követelmények

Rétegek: L0 Identity & Consent · L1 Ingestion · L2 Normalization · L3 Genotype→Phenotype · L4 Knowledge & Rules · L5 PRS · L6 Delivery · L7 Observability. Minősítés: [A melléklet](A-intended-purpose-and-modules.md). Interfészek: [B melléklet](B-architecture-and-interfaces.md). Tesztek: [D melléklet](D-risk-and-traceability.md).

### 6.1 L0 — Identity & Consent

#### FR-100 · Genetikai tanácsadás- és beleegyezés-kapu — **Compliance P0**

A rendszer nem engedélyezi PGx-riport generálását olyan esethez, amelyhez nincs rögzítve (i) mintavétel **előtti** genetikai tanácsadás (6. § (2)) és (ii) 8. § szerinti írásbeli beleegyezés. A kapu azt is ellenőrzi, hogy a vizsgálatot végző partner **engedélyezett szolgáltató** (12. § (1)) — a PCE maga nem „végzi” a vizsgálatot B2C-ben (NG-03).

Acceptance criteria:

- [ ] Given egy eset, amelyhez nincs `counselling_record`, When a felhasználó riportgenerálást indít, Then elutasítás `E-CONSENT-001` kóddal és a **6. § (2)**-re hivatkozó magyar indoklással. `[CORRECTED]`
- [ ] Given nincs `consent_record` (8. §), When riportgenerálás indul, Then elutasítás `E-CONSENT-003` kóddal (8. §).
- [ ] Given `counselling_record.date` **későbbi**, mint `sample.collected_at`, When riportgenerálás indul, Then elutasítás `E-CONSENT-002` (tanácsadás a mintavétel előtt kötelező).
- [ ] Given érvényes tanácsadás + beleegyezés + engedélyezett `performing_org`, When riportgenerálás indul, Then a művelet folytatódik, és a riport metaadata tartalmazza a tanácsadó azonosítóját, a tanácsadás dátumát, a beleegyezés dátumát és a szolgáltató működési engedély-azonosítóját (ha megadott).
- [ ] A kapu **nem** kikapcsolható konfigurációval, sem admin szerepkörrel. Negatív teszt: admin sem tudja megkerülni.
- [ ] Given a 15. § szerinti célt meghaladó további génvizsgálat, When nincs ismételt beleegyezés, Then az extra gének nem kerülnek a riportba (`E-CONSENT-004`).

Technikai megjegyzés: v1 kézi rögzítés; v1.1 FHIR `Consent` + `Encounter`.

#### FR-110 · Granuláris, visszavonható hozzájárulás — **Compliance P0**

Hozzájárulás gén/génpanel és felhasználási cél szintjén; 6. § (7) nem-tudás joga.

- [ ] Given a beteg lemondott egy adott gén eredményének megismeréséről, When riport generálódik, Then az adott gén a **beteg-példányból** kimarad. A klinikus-példányban csak akkor jelenhet meg, ha a klinikus hozzáférése külön, konfigurált jogalapon engedélyezett — kódmódosítás nélkül.
- [ ] Given hozzájárulás-visszavonás, When rögzítésre kerül, Then a rendszer kaszkádolva töröl minden érintett genetikai adatot és nyilvántartási bejegyzést, és visszavonhatatlan törlési tanúsítványt állít ki. Az üzemi cél: **72 órán belül** `[ASSUMPTION]` A10. A törvényi minimum: megsemmisítés a 26. § (1) szerint, határidő nélkül.
- [ ] A kaszkád **derived** adatra is kiterjed: diplotípus, fenotípus, riportok, cache, PRS-eredmény (ha van).
- [ ] Negatív teszt: visszavonás után a korábbi riport URL **410 Gone**, nem 200 cache-ből.
- [ ] A 30 éves **audit** napló a törlés *eseményét* megőrzi személyazonosító genetikai tartalom nélkül (ki, mikor, milyen jogalapon, milyen objektum-azonosítók semmisültek meg) — a genetikai tartalom nem marad.

#### FR-120 · 30 éves nyilvántartás — **Compliance P0** (hash-chain: **P1**)

Jogalap: 26. § (1). `[CORRECTED]` A hash-chain nem törvényi P0.

- [ ] Minden genetikai minta/adat felvétele, vizsgálata, tárolása, feldolgozása és továbbítása naplózott; a bejegyzés tartalmazza a minta típusát, mennyiségét (ha ismert), eredetét, rendeltetési célját és a kialakított genetikai adat *kategóriáját* (gén/diplotípus azonosító, nem nyers VCF a naplóban).
- [ ] A napló **legalább 30 évig** megőrződik, kivéve a 26. § (1) szerinti megsemmisítést.
- [ ] A napló **append-only**; utólagos módosítás elutasított. Negatív teszt: DB-szintű UPDATE a napló-táblán hibát ad. (**P0**)
- [ ] Strukturált export (CSV + JSON) hatósági ellenőrzésre. (**P0**)
- [ ] `[P1]` Kriptográfiai hash-chain a bejegyzéseken.

#### FR-130 · Beteg-azonosítás és pszeudonimizáció — **Compliance P0**

- [ ] A genetikai adat L2–L5-ben kizárólag pszeudonim azonosítóval szerepel; az újraazonosító kulcs külön, szigorúbb ACL-ű store-ban van (2008/XXI. kódkulcs-elkülönítés szellemében, 24. § / 25. §).
- [ ] Given L4 szabálykiértékelés, When a motor logol, Then a logban nincs név, TAJ, születési dátum. Negatív teszt: CI log-scanner PII-mintákra.

---

### 6.2 L1 — Ingestion

#### FR-200 · VCF befogadás — **Product P0**

A VCF-útvonal támogatott, de az F1 **default** a FR-240 outside-call. VCF akkor kell, ha a partner a nyers/variáns fájlt adja, és a callability (FR-210) ellenőrizendő.

- [ ] Támogatott: VCFv4.2 és 4.3, single- és multi-sample, GRCh37 és GRCh38, bgzip+tabix és plain.
- [ ] Given multi-sample VCF, When feltöltés, Then sample-enként szétválasztás; minden sample-hez külön eset kell (nincs automatikus beteg-tippelés).
- [ ] Given nem támogatott referencia vagy hiányzó `##reference`, When feltöltés, Then `E-VCF-003`, a hiányzó elem megnevezésével.
- [ ] Fájlméret-limit: 5 GB/fájl; e fölött chunked upload vagy `E-VCF-004`.
- [ ] Given csonka/parse-olhatatlan VCF, When feltöltés, Then beszédes hiba `E-VCF-001`, **nem** részleges riport (story 20).

#### FR-210 · Lefedettség-ellenőrzés (callability) — **Product P0**

**A klinikai P0 csúcs.** A hiányzó pozíció **nem** azonos a referencia-alléllal. Naiv missing-to-ref → hamis NM → ellentétes ajánlás → visszahívás.

- [ ] Given VCF, amelyben a panel egy génjének definiáló pozíciója nem vizsgált (nincs a VCF-ben, és nincs lefedő gVCF reference block), When feldolgozás, Then a gén státusza `INDETERMINATE`, **nem** `NORMAL`.
- [ ] Minden génhez explicit státusz: `CALLED` / `PARTIAL` / `INDETERMINATE` / `NOT_TESTED`.
- [ ] Given `INDETERMINATE` gén, When riport, Then az adott gén gyógyszerállítása **nem** pozitív állítás, hanem „nem meghatározható”.
- [ ] Negatív teszt: a gold setben ≥ 3 eset, ahol a missing-to-ref klinikailag ellentétes ajánlást adna; a rendszer `INDETERMINATE`.
- [ ] A PharmCAT `--absent-to-ref` és `--unspecified-to-ref` **nem** hívható vakon; esetenként, dokumentált indokkal, change-control alatt.

#### FR-220 · Klinikai kontextus (gyógyszerlista, labor) — kézi **Product P0** / FHIR **P1**

A fenokonverzió (FR-410) inputja. FHIR nem kell a mag use case-hez, ha van kézi bevitel.

- [ ] **P0** Kézi bevitel: aktuális gyógyszerlista (ATC vagy OGYÉI/PHARMINDEX azonosító) + opcionális eGFR/kreatinin, ALT/AST/bilirubin.
- [ ] **P0** Given nincs sem FHIR, sem kézi klinikai adat, When riport, Then a fenokonverzió- és szervfunkciós kimenet explicit „nem értékelhető — hiányzó klinikai adat”, nem hallgatólagos kihagyás. A riport `clinical_context = ABSENT`.
- [ ] **P1** FHIR R4 `Observation` (eGFR/kreatinin, ALT/AST/bilirubin, albumin), `MedicationRequest` / `MedicationStatement`.
- [ ] **P1** Given FHIR-forrás nem elérhető, When feldolgozás, Then fallback kézi bevitelre; a riport jelzi `clinical_context = MANUAL`.

#### FR-230 · HL7 v2 LRI — **P1**

- [ ] HL7 v2.5.1 LRI ORU^R01 fogadása genotípus-eredményhez; mapping a B melléklet szerint.

#### FR-240 · Külső genotípus/fenotípus (outside-call) — **Product P0**

Az F1 default útvonal. A partnerlabor **már meghívott** diplotípusa.

- [ ] Tab-delimited outside-call és strukturált API: `gene`, `diplotype`, `calling_lab`, `signing_physician`, `method`, `call_date`, opcionálisan `phenotype`, `callability`.
- [ ] Given outside-call és VCF-alapú hívás ütközik, When mindkettő elérhető, Then **nincs** automatikus választás: `W-CALL-010`, emberi döntés.
- [ ] Given outside-call `callability = INDETERMINATE` egy génre, When riport, Then ugyanaz a viselkedés, mint FR-210.

---

### 6.3 L2 — Normalization

#### FR-250 · Variáns- és terminológia-normalizálás — **Product P0**

- [ ] Variáns-reprezentáció HGVS és GA4GH VRS szerint, left-align + trim, ahol variáns bemenet van.
- [ ] Gyógyszer: ATC + hazai törzs (OGYÉI/PHARMINDEX) `[NEEDS VERIFICATION]` gépi licence (OQ-11). Labor: LOINC. Fenotípus: SNOMED CT vagy CPIC-terminológia.
- [ ] Given ismeretlen gyógyszerkód, When mapping, Then `NEEDS_MAPPING`, **nincs** csendes hiányos gyógyszerlistás riport (`E-MAP-001`).
- [ ] A mapping-táblák verziózottak; a verzió a riport metaadatában szerepel.

---

### 6.4 L3 — Genotype → Phenotype

#### FR-300 · PharmCAT-integráció — **Product P0** (VCF-útvonal); F1 default = FR-240

Ha a partner VCF-et ad és a PCE futtatja a `NamedAlleleMatcher`-t, az F1 nem-MDSW állítás **gyengül** (A melléklet, OQ-05). A követelmény ettől még specifikált, mert a VCF-útvonal létezik.

- [ ] PharmCAT `NamedAlleleMatcher` és `Phenotyper` hívása a VCF-útvonalon; pipeline-verzió, PharmVar allél-definíció, CPIC adatverzió a riport metaadatában.
- [ ] Given phased VCF, When hívás, Then a fázis felhasználásra kerül; unphased esetben ambiguitás jelölése, nincs önkényes választás.
- [ ] Given CYP2D6, When hívás, Then jelzés, ha structural variant (del/dup/hybrid) a bemenetből nem meghatározható.
- [ ] MPL 2.0: származékos módosítások közzétételi kötelezettsége dokumentált; a PharmCAT által hívott programok licencei külön (REG-080, B SOUP).
- [ ] Az F1 **ajánlott** konfiguráció: PharmCAT matcher **ki**, outside-call **be**. A matcher bekapcsolása change-control + REG-010 újraértékelés.

#### FR-310 · Génlista mint verziózott konfiguráció — **Product P0**

`[CORRECTED]` OQ-02 **lezárva**.

**Klinikai evidencia-alap (PREPARE, Lancet 2023)** — 50 germline variáns, **12 gén** a vizsgálat indulásakor: CYP2B6, CYP2C9, CYP2C19, CYP2D6, CYP3A5, DPYD, F5, HLA-B, SLCO1B1, TPMT, UGT1A1, VKORC1. A panel a vizsgálat alatt változhatott (DPWG-frissítés).

**Konfigurációs bővítmény (PGx-Passport, CPT 2019)** — 58 variáns, **14 gén**: a fenti + **HLA-A**, **NUDT15**.

A v1 default gene set = PREPARE 12, `config_id = pgx-prepare-12@<version>`. HLA-A és NUDT15 opcionális, külön config-verzió.

- [ ] A génlista, variáns-definíciók és szabálybázis **külső, verziózott konfiguráció**, nem kódkonstans.
- [ ] Bizonyíték: PharmCAT 2.11.0 eltávolította az F5-öt, mert a DPWG visszavonta az F5–szisztémás hormonális kontraceptívum ajánlást `[V]`. A génlista **nem stabil**.
- [ ] Given konfigurációváltás, When aktiválás, Then change-control rekord (ki, mit, mikor, forrás) és a korábbi riportok érintettsége listázható (FR-510).

---

### 6.5 L4 / L5 — Knowledge, Rules, PRS

> L4/L5 **MDSW IIa**, ha a kimenet terápiás/diagnosztikai döntéshez ad információt (Rule 11a). Az F1 intended purpose (A melléklet) ezt szűkíti: passzív, aláíró orvos, nincs order-sign, nincs dózisszám. **OQ-05** dönti el, védhető-e. Ha nem, F1 = F3.

#### FR-400 · Szabálymotor — **Product P0 (passzív)** / **P1 (aktív CDSS)**

- [ ] **P0** CPIC, ClinPGx-annotált DPWG és ClinPGx-annotált FDA-címke ajánlások kiértékelése diplotípus alapján; kimenet a riportban, nem a felírási workflow-ban.
- [ ] Given azonos gén–gyógyszer párra eltérő CPIC és DPWG, When kiértékelés, Then **mindkettő** forrásmegjelöléssel; a rendszer **nem** szintetizál harmadik ajánlást.
- [ ] Minden kimeneti állítás mellett: forrás, guideline-verzió, evidencia-szint, mély link.
- [ ] Negatív teszt: `assert unsourced_claims == 0` CI-ben.
- [ ] **P1** Ugyanez a motor CDS Hooks Card-ként (FR-520).

#### FR-410 · Fenokonverzió-modul — **Product P0** *(differenciátor)*

- [ ] A beteg aktuális gyógyszerlistája alapján a rendszer detektálja a CYP-inhibitor/induktor együttadást, és jelzi a genotípus-alapútól eltérő **funkcionális** fenotípust.
- [ ] Given CYP2D6 NM genotípus + erős CYP2D6-inhibitor (paroxetin, fluoxetin) egyidejű szedése, When kiértékelés, Then `genotype_phenotype = NM`, `functional_phenotype = PM` vagy `IM` (a szabálybázis szerint), a különbség explicit.
- [ ] A fenokonverzió **soha nem írja felül** a genotípus-fenotípust.
- [ ] Given eGFR < 30 vagy dokumentáltan emelkedett bilirubin, When kiértékelés, Then jelzés: PGx mellett szervfunkciós módosítás is indokolt **lehet** — nem dózisszám.
- [ ] A kimenet **minősítés, nem dózisszám**. Konkrét mg-ajánlás v1-ben tilos.
- [ ] A fenokonverzió-szabálybázis verziózott, mint FR-310.

#### FR-420 · Alert-relevancia szűrés — **Product P0**

F1-ben „riasztás” = a riport első oldalának kiemelése, nem interruptive EHR-alert.

- [ ] Csak actionable gén–gyógyszer pár kerül a kiemelésbe; a nem-actionable a függelékbe.
- [ ] Kategóriák: `CRITICAL` (alternatíva a forrás szerint), `WARNING` (monitorozás), `INFO` (nincs teendő).
- [ ] Given 40 gén–gyógyszer pár, When riport, Then a `CRITICAL` + `WARNING` a első oldalon, részletek mögötte.

#### FR-430 · PRS interfész — **P2** (nem épül)

- [ ] Interfész definiált: `POST /prs/score` → `{score, percentile, absolute_risk, ancestry_calibration, provider, model_version}` — stub, nincs implementáció.
- [ ] Beszállítói minimum: ISO 13485, dokumentált ancestry-kalibráció, eMERGE-típusú klinikai pipeline.
- [ ] Indoklás: Kullo et al., Nat Rev Genet 2026;27:246–263 `[V]`; portabilitási / túlbecslési irodalom. Magyar referencia-genom hiányában saját modell nem kalibrálható.

---

### 6.6 L6 — Delivery

#### FR-500 · Riport-generálás — **Product P0**

- [ ] Kimenet: PDF (aláírásra kész), FHIR Bundle (Genomics Reporting IG), strukturált JSON.
- [ ] FHIR: IG **v3.0.0 STU3**, FHIR R4; mapping-réteg STU4-re (`GenomicStudy`, új operations) — szállít STU3-on.
- [ ] PDF minden oldalán: guideline-verziók, pipeline-verzió, callability-összefoglaló, aláíró orvos helye, intended purpose egy mondatban (F1 vs F2).
- [ ] Given white-label partner, When riport, Then partner arculata és aláírója; PCE a kolofonban mint technológiai szállító.

#### FR-510 · Riport-újragenerálás guideline-frissítéskor — **P1**

- [ ] Given új CPIC/DPWG verzió, When admin újraértékelést indít, Then a rendszer listázza azokat az eseteket, ahol az ajánlás **megváltozott**, riportonkénti deltával.
- [ ] Az eredeti riport immutábilis; új verzió jön létre.

#### FR-520 · CDS Hooks — **P1** (F2-ben Product P0)

- [ ] `order-select` és `order-sign`; válasz `Card`, `suggestion` az alternatívára, `link` az evidenciára.
- [ ] Given a szolgáltatás > 2 s alatt nem válaszol, Then a felírás **nem blokkolódik** (fail-open). Klinikai biztonság, nem perf-preferencia.
- [ ] Given nincs PGx-adat, When hook, Then explicit „nincs elérhető PGx-eredmény” card, nem üres válasz.

#### FR-530 · SMART on FHIR — **P1**

- [ ] EHR-launch context (`patient`, `encounter`, `user`); a nézet a felírási workflow-ba illeszkedik, nem önálló portál.
- [ ] A v1 webes labor-UI **átmeneti**, nem végállapot.

#### FR-540 · Beteg-példány riport — **P1**

- [ ] Laikus nyelvű változat: genotípus-információ + „beszéljen kezelőorvosával”; **nincs** dózis- vagy terápiajavaslat.
- [ ] OQ-13: kiadható-e anélkül, hogy 6. § (4) szerinti tanácsadásnak minősülne — jogi, nem engineering.

---

### 6.7 L7 — Observability & Governance

#### FR-600 · Alert-fatigue és override telemetria — **P1**

F1-ben a „riasztás” riport-kiemelés; az override F2-n értelmes. P1, hogy a séma meglegyen a PMS/PMCF-hez.

- [ ] Minden kiemelés/riasztás megjelenítése, elfogadása, elutasítása naplózott; elutasítás kötelező indoklás-kategóriával.
- [ ] Override-ráta gén–gyógyszer szinten aggregálható; > 80% automatikus review-lista.
- [ ] Az adat PMS/PMCF input a v2 dossziéhoz.

#### FR-610 · Nyelv — **Compliance P0** (klinikai szöveg) / **P1** (teljes EN UI)

- [ ] **P0** UI magyar. Beteg-riport magyar (ha FR-540 készül).
- [ ] **P0** Klinikai ajánlás: szakmai lektorált magyar, **és** az eredeti angol forrásszöveg elérhető.
- [ ] **P0** Given nincs lektorált magyar, When riport, Then az angol eredeti jelenik meg jelöléssel — **nem** gépi fordítás, **nem** LLM-fordítás (FR-700).
- [ ] **P1** Teljes angol UI a nem-magyar klinikusnak.

#### FR-700 · LLM-használat korlátozása — **Compliance P0**

- [ ] LLM kizárólag (a) előre jóváhagyott sablonkészletből olvashatósági átfogalmazásra, és (b) belső dokumentum-keresésre.
- [ ] Az LLM **nem** generál gyógyszerajánlást, fenotípus-hívást, dózist vagy kockázati számot. Negatív teszt: klinikai kimeneti útvonalon nincs LLM-hívás; CI call-graph.
- [ ] Indoklás: AI Act Annex I + nem-determinisztikus komponens a IIa dossziéban; 6. § (6) reprodukálható magyarázatot követel (FR-710).

#### FR-710 · Algoritmus-magyarázat kérésre — **Compliance P0**

Jogalap: **6. § (6)** `[V]`.

- [ ] Given beteg vagy képviselője magyarázatot kér, When a kérés rögzített, Then esetspecifikus, laikus nyelvű magyarázat: mely gének, milyen diplotípus, melyik guideline-verzió, melyik szabály, callability.
- [ ] A magyarázat **determinisztikus**: ugyanaz az eset + ugyanaz a config → bitre azonos magyarázat (NFR-060).
- [ ] A magyarázat **nem** LLM-generált.

---

## 7. Nem-funkcionális követelmények

| ID | Követelmény | Célérték | Ellenőrzés | Pri |
| --- | --- | --- | --- | --- |
| **NFR-010** | Pipeline-átfutás (ingest → riport) | p95 < 10 min, p99 < 25 min WES-re | Load teszt | P0 |
| **NFR-011** | CDS Hooks válaszidő | p95 < 800 ms, hard timeout 2 s, fail-open | Szintetikus monitor | P1 (F2: P0) |
| **NFR-020** | Rendelkezésre állás | 99,5% H–P 7–20 CET; CDS fail-open miatt nem klinikai-kritikus F1-ben | SLO | P0 |
| **NFR-030** | Adat-lokalizáció | Genetikai adat EU-ban tárolt és feldolgozott; alvállalkozói lánc dokumentált | DPA audit | P0 |
| **NFR-031** | Titkosítás | At-rest AES-256, in-transit TLS 1.3; genetikai payload rétegzett; re-ID kulcs külön KMS | Pentest | P0 |
| **NFR-032** | Hozzáférés | RBAC + MFA minden genetikai adatot látó szerepre; least privilege; break-glass naplózva | Access review / negyedév | P0 |
| **NFR-033** | Titokkezelés | Nincs secret a repóban; gitleaks + Semgrep CI; kulcsrotáció ≤ 90 nap | CI | P0 |
| **NFR-040** | Auditálhatóság | Minden genetikai adathozzáférés: ki, mit, mikor, jogalap; append-only | FR-120 | P0 |
| **NFR-050** | EHDS-készültség | Adatmodell leképezhető EHDS/MyHealth@EU felé; nem implementált, nem kizárt | Architecture review | P2 |
| **NFR-060** | Reprodukálhatóság | Adott bemenet + config-verzió → bitre azonos kimenet | CI determinizmus | P0 |
| **NFR-070** | Kódminőség / 62304 | Software safety class **B** (feltétel: klinikai kár lehetséges rossz ajánlásnál); unit+integráció ≥ 80%, klinikai útvonal 100% | CI | P0 |
| **NFR-080** | DR | RPO ≤ 1 h, RTO ≤ 8 h; 30 éves nyilvántartás külön immutábilis archívumban | Éves DR-teszt | P0 |
| **NFR-090** | Skálázás | 10 000 eset/hó lineáris költség; PharmCAT izolált worker | Kapacitásteszt | P1 |

---

## 8. Szabályozási és compliance követelmények

| ID | Követelmény | Pri | Határidő |
| --- | --- | --- | --- |
| **REG-010** | Intended purpose írásban, modulonként, MDCG 2019-11 Rev.1 szerint. Két változat: F1 vs F2/F3 — [A melléklet](A-intended-purpose-and-modules.md). Az F1 nem-MDSW **indoklás**, nem tény, amíg OQ-05. | Compliance P0 | v1 előtt |
| **REG-011** | F2 in-house: intézményen belül, kizárólag ott; NB nincs a megfelelőségértékelésben; feltételek dokumentálva | Compliance P0 | F2 indulás |
| **REG-020** | Írásos határvonal a partnerlaborral: diplotípus/fenotípus-hívás a labor aláíró orvosáé | Compliance P0 | Első partner előtt |
| **REG-021** | Írásos határvonal a medikai szállítóval: ki a gyártó, ki a distributor | Compliance P0 | Első integráció előtt |
| **REG-030** | ISO 13485 QMS, IEC 62304, ISO 14971 — **v1-gyel párhuzamosan**, nem utólag. **Nem** az EESZT 2026-09-30 tárgya. | Compliance P0 | F2-vel párhuzamosan |
| **REG-031** | PRRC (MDR Art. 15) kijelölve; mikrovállalkozásnál külső PRRC a rendelet feltételei szerint | Compliance P0 | F2 |
| **REG-040a** | EESZT fejlesztői regisztráció (5/F. §) + **4. melléklet 2.1 ISO 9001 vagy egyéb szoftver-QMS** `[CORRECTED]` | Compliance P0 | **ISO 9001: 2026-09-30** |
| **REG-040b** | Saját EESZT-csatlakozás / BM szoftverengedély — **nem F1 cél** (NG-05, A8). F4. | P2 | F4 |
| **REG-050** | GDPR Art. 9 jogalap; DPIA genetikai adatra; DPO | Compliance P0 | v1 előtt |
| **REG-060** | AI Act gap Art. 9–15, 17, 72; AI-követelmények az MDR fájlba **integrálva, nem duplikálva** (MDCG 2025-6) | P1 | 2027 Q4 |
| **REG-061** | AI literacy Art. 4 — 2025-02-02 óta | Compliance P0 | Azonnal |
| **REG-070** | ISO/IEC 27001 (opcionálisan 42001) — enterprise / biztonság, **nem** EESZT 9/C. § `[CORRECTED]` | P1 | enterprise előtt |
| **REG-080** | SPDX SBOM; PharmCAT MPL 2.0 + hívott programok licencei külön | Compliance P0 | v1 előtt |

---

## 9. Validációs és teszt-stratégia

### 9.1 Gold set

Nélküle G2/G3 nem mérhető, a v2 dosszié nem védhető.

- **Méret:** minimum 200 eset. 60 szintetikus (edge), 100 nyilvános referencia (GeT-RM / AMP diplotípusok), 40 deidentifikált partnerlabor-eset.
- **Kötelező edge:** hiányzó pozíció (FR-210), CYP2D6 SV, unphased ambiguitás, CPIC–DPWG ütközés, fenokonverzió, `INDETERMINATE` + actionable gyógyszer, visszavont hozzájárulás, csonka VCF, F5 config-on/off.
- **Ground truth:** két független annotátor (klinikai farmakológus + molekuláris genetikus); döntőbíró egyet nem értéskor. Cohen's κ **≥ 0,80**; ez alatt az annotációs útmutató újraírandó, nem a küszöb.
- **Verzió:** DVC; minden release-hez rögzített gold set verzió.

### 9.2 Metrikák és küszöbök

| Mérés | Küszöb | Megjegyzés |
| --- | --- | --- |
| Diplotípus-egyezés referencia-anyagokon (outside-call echo / matcher) | **100%** | Determinisztikus |
| Actionable ajánlás recall (PREPARE 12 + aktuális CPIC/DPWG) | **100%** (0 FN) | G2 |
| Callability-jelölés | **100%** | FR-210 |
| Fenokonverzió recall | **≥ 90%** | G3 |
| Fenokonverzió precision | **≥ 75%** | FP = „nézd meg” |
| Forrás nélküli állítás | **0** | FR-400 CI |

### 9.3 Regressziós kapu

- [ ] Minden guideline-verzió-váltás után a teljes gold set újrafut; delta-riport release-review tárgy.
- [ ] Given bármely metrika küszöb alatt, When release, Then CI blokkol. **Nincs** manuális override.

### 9.4 Klinikai evidencia a v2 dossziéhoz

**PREPARE** (Swen et al., Lancet 2023;401:347–356) `[V]`: nyílt, multicentrikus, kontrollált, klaszter-randomizált crossover; 12-génes panel; 18 kórház, 9 közösségi egészségügyi központ, 28 közösségi gyógyszertár; 7 ország (AT, GR, IT, NL, SI, ES, UK) — **Magyarország nincs benne**. 50 germline variáns 12 génben a startnál. 6944 beteg 41 696 alkalmasból; 6495 (93,5%) enrolláltnál actionable variáns; genotípus-vezérelt kar vs standard: klinikailag releváns ADR csökkenés (a közlemény ~30% OR-csökkenést közöl az actionable alcsoportban).

**Forráskritika (kötelező a dossziéban):** a csökkenés elsősorban grade 2 ADR, „possible to probable” adjudikáció; a Lancet legalább négy kritikai levelet közölt (Curtis; Rogers et al.; Van der Linden; Peñas-LLedó & LLerena). A Notified Body ezt megtalálja.

A 12 vs 14 eltérés **nem** nyitott kérdés: lásd FR-310.

---

## 10. Open Questions

### Blokkoló (v1 indulás előtt)

| ID | Kérdés | Kinek | Státusz |
| --- | --- | --- | --- |
| **OQ-01** | Van érvényes EESZT fejlesztői regisztráció? A 4. melléklet 1.1–1.9 + 2.1 teljesíthető-e 2026-09-30-ig? | Ügyvezetés / RA | **Teendő**, nem spekuláció → [C melléklet](C-eeszt-f0-checklist.md) |
| **OQ-02** | PREPARE 12 vs PGx-Passport 14 | Klinikai | **LEZÁRVA** (FR-310, VC-02) |
| **OQ-03** | Melyik partnerlabor vállalja az L3 aláírói felelősséget, milyen áron? | Üzletfejlesztés | Nyitott |
| **OQ-04** | Magyar Genom Program / BBMRI HU csomópont: partner vagy versenytárs? | Ügyvezetés | Nyitott; hungen.hu nem datált |
| **OQ-05** | Védhető-e a „nem-MDSW riport-előállító” pozíció MDCG 2019-11 Rev.1 alatt, ha a kimenet gyógyszerajánlás-*szöveget* tartalmaz, és az aláíró a labor orvosa? **Legnagyobb egyetlen kockázat.** | **Külső jogi tanácsadó** | Nyitott. Ez a dokumentum **nem** állásfoglalás. Tényalap: A melléklet. |
| **OQ-06** | ISO 13485 tanúsító és Notified Body; HU/EU NB átfutás | RA | Nyitott |

### Nem-blokkoló

| ID | Kérdés | Kinek |
| --- | --- | --- |
| **OQ-10** | PRS-beszállító (Allelica vagy más), árazás, EU-adatlokalizáció | Üzlet, F4-ig |
| **OQ-11** | OGYÉI/PHARMINDEX gépi elérés és licenc | Engineering |
| **OQ-12** | Genomics Reporting IG STU3 → STU4 időzítés | Engineering |
| **OQ-13** | FR-540 beteg-riport 6. § (4) tanácsadásnak minősül-e? | Jogi |
| **OQ-14** | Magyar klinikai ajánlás-fordítás szakmai lektora | Klinikai szakértő |

**Döntés, nem kérdés:** a v1 **nem** tartalmaz aktív, felírás-pillanatú riasztást. Ha mégis, az MDSW, és a §11 F1 oszlop érvénytelen.

---

## 11. Timeline és fázisolás

### Kemény határidők

| Dátum | Esemény | Forrás |
| --- | --- | --- |
| **2025-10-31** | EESZT fejlesztői regisztráció (lejárt) | 29/2022. 9/C. § `[V]` |
| **2026-09-30** | 4. melléklet 2. pont — ISO 9001 / szoftver-QMS | 9/C. § `[V]` |
| **2027-12-02** | AI Act Annex III `[NEEDS VERIFICATION]` | Digital Omnibus / I-01 |
| **2028-08-02** | AI Act Annex I — tervezési óra `[NEEDS VERIFICATION]` | I-01 |
| **2029-03-26** | EHDS másodlagos (nem-genetikai) | (EU) 2025/327 |
| **2031-03-26** | EHDS másodlagos — humán genetikai adat | (EU) 2025/327 |

### Fázisok

| Fázis | Idő | Tartalom | Kimenet | MDR |
| --- | --- | --- | --- | --- |
| **F0** | 0–3 hó | C melléklet checklist; OQ-05 counsel; partnerlabor LOI; gold set v0 (60 szintetikus) | Jogi tisztánlátás + 1 LOI | — |
| **F1** | 3–9 hó | L0–L2 + FR-240 + passzív L4 riport + FR-410. FR-300 matcher **ki**, hacsak OQ-05 engedi. | Fizető labor-partner | Nem MDSW **csak ha** OQ-05 igen |
| **F2** | 6–18 hó | In-house aktív CDSS (FR-520/530); ISO 13485 + 62304 + 14971 | Case study + referenciák | In-house (REG-011) |
| **F3** | 18–36 hó | IIa CE L4-re; AI Act a technikai fájlban | CE-jelölt CDSS | **IIa** |
| **F4** | 36+ hó | L5 partner; EESZT-modul; EHDS-készültség | Enterprise platform | IIa |

**Kritikus út:** OQ-05 → F1 hatókör. Ha a gyógyszerajánlás-szöveget tartalmazó riport is MDSW, F1 összeomlik F3-ba.

### Kompetencia (SFIA)

| Szerep | Szint | Miért |
| --- | --- | --- |
| Solution Architect | L5 | Több szabályozási domain |
| RA / QA | L5 | ISO 13485 Management Representative |
| PRRC | Jogszabályi | MDR Art. 15; nem korlátlanul outsource |
| Senior Backend | L4 | IEC 62304 Class B |
| QA / Test | L4 | Gold set, IAA, regresszió |
| Klinikai farmakológus / genetikus | Szakvizsga | Ground truth, lektorálás |

Egyik sem opcionális. A6 a minimum.

### Árazási kötés a követelményekre (nem TAM)

A brief árazási modellje **követelmény-kötés**, nem megfigyelt ár:

| Sáv | Modell | Spec-kötés |
| --- | --- | --- |
| Labor white-label (L0–L3 + passzív L4) | Fix havidíj + volumensáv | F1; nem per-patient (a preemptív tesztelést büntetné) |
| Klinikai CDSS (L4 aktív) | Per-clinician/hó | F2/F3; FR-520 |
| PRS (L5) | Per-report, partner-átárazás | FR-430; nem saját motor |
| Enterprise / EHR-vendor | Éves platform + integrációs egyszeri | P6; REG-021 |

---

## 12. Traceability

A teljes mátrix: [D melléklet](D-risk-and-traceability.md).

Váz:

| Req ID | Forrás | Teszteset | MDR/AI Act |
| --- | --- | --- | --- |
| FR-100 | 2008/XXI. 6. § (2), 8. §, 12. § (1) | TC-CONSENT-001..006 | GSPR 14.1 |
| FR-110 | 6. § (7), 26. § (1) | TC-CONSENT-010..014 | GDPR Art. 17; GSPR 14 |
| FR-120 | 26. § (1) | TC-AUDIT-001..006 | GSPR 17.2 |
| FR-210 | Klinikai kockázat + PharmCAT preprocessor | TC-CALL-001..012 | ISO 14971 RC-003 |
| FR-310 | PREPARE; PGx-Passport; PharmCAT 2.11.0 | TC-CONF-001..005 | IEC 62304 §6 |
| FR-400 | CPIC / DPWG / FDA | TC-RULE-001..040 | GSPR 17.1 |
| FR-410 | Fenokonverzió-irodalom (I-02) | TC-PHENO-001..015 | Clinical evaluation |
| FR-700 | MDCG 2025-6; AI Act 6(1) | TC-LLM-NEG-001..003 | AI Act Art. 9, 15 |
| FR-710 | 6. § (6) | TC-EXPLAIN-001..004 | AI Act Art. 13; GSPR 23 |

---

## 13. Parking lot

- Onkológiai szomatikus panel (IVDR)
- HLA hiperszenzitivitás kiterjesztés (HLA-B\*57:01, \*15:02 túl)
- Magyar referencia-genom allélfrekvencia-korrekció (Semmelweis projekttől függ)
- Gyógyszertári medication review (PREPARE 28 patika — validált use case, nem v1)
- Pharma kohorsz-toborzás (EHDS 2031+)
- Biztosítói prevenciós modul
- Engineering ticket-bontás, gold-set annotációs SOP, OQ-05 counsel brief (write-spec §5 follow-up)

---

## 14. Forrásjegyzék

A teljes registry: [SOURCE-REGISTRY](ProcessArtifacts/SOURCE-REGISTRY.md). Korrekciók: [VALIDATED-CLAIMS](ProcessArtifacts/VALIDATED-CLAIMS.md).

**Szabályozás**

1. `[V]` 2008. évi XXI. törvény — njt.jog.gov.hu / net.jogtar.hu
2. `[V]` MDCG 2019-11 Rev.1 (2025-06-17) — health.ec.europa.eu
3. `[V]` MDCG 2025-6 / AIB 2025-1 (2025-06-19)
4. `[V]` (EU) 2025/327 EHDS
5. `[NEEDS VERIFICATION]` Digital Omnibus AI dátumok (I-01)
6. `[V]` 29/2022. (I. 31.) Korm. r.; 294/2025. (IX. 25.) Korm. r. 4. melléklet; e-egeszsegugy.gov.hu/fejlesztoknek

**Klinikai**

7. `[V]` Swen et al. Lancet 2023;401:347–356 (PREPARE) + kritikai levelek
8. `[V]` van der Wouden et al. CPT 2019;106:866–873 (PGx-Passport)
9. `[V]` Kullo et al. Nat Rev Genet 2026;27:246–263
10. `[V]` eMERGE, Nat Med 2024, doi:10.1038/s41591-024-02796-z

**Technológia**

11. `[V]` PharmCAT changelog 2.11.0 (F5 removal) — pharmcat.clinpgx.org/changelog
12. `[V]` HL7 FHIR Genomics Reporting IG v3.0.0
13. `[V]` Dolin et al. Methods Inf Med 2018;57:e115–e123

**Piac**

14. `[R]` genetix.hu/arak — I-01, 2026-08-09; ebben a körben nem ismételve

---

## 15. Amit ez a spec nem tud

- **Nem** OQ-05 jogi vélemény. A teljes F1 fázis ezen áll vagy dől.
- **Nem** ellenőrizte a 2026-os ACC/AHA irányelv szövegét (Allelica PR, `[C]`, ki van hagyva).
- **Nem** ismételte a Genetix ár-scrape-et (VC-10).
- **Nem** talált (és nem is keresett OPTEN-ben) magyar/CEE PGx-CDSS versenytársat — ez üzleti dosszié, nem SRS.
- **Nem** állít TAM-ot. A szekunder piackutatók 5,7× szórása szándékosan nincs a dokumentumban.

---

*PCE-SPEC-v1.1. A v1.0 váz korrekciói: VC-01–VC-06. OQ-02 lezárva. Következő: OQ-05 külső counsel; C melléklet F0 végrehajtás.*
