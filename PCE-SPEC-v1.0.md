# Precision Clinical Engine (PCE) — Termékspecifikáció és követelménylista

|                    |                                                                  |
| ------------------ | ---------------------------------------------------------------- |
| **Dokumentum-ID**  | PCE-SPEC-v1.0                                                    |
| **Státusz**        | Draft — review-ra kész                                           |
| **Dátum**          | 2026-08-09                                                       |
| **Szerző**         | Agentize Kft.                                                    |
| **Hatókör**        | PGx clinical decision support platform, magyar/EU piac           |
| **Következő gate** | P01 — source coverage audit + independent build-readiness review |

---

## 0. Hatóköri feltevések (explicit, nem validált)

Kérdés helyett rögzítem. Ha bármelyik hamis, a jelzett szakasz újraírandó.

| #   | Feltevés                                                                                                  | Ha hamis, érintett szakasz |
| --- | --------------------------------------------------------------------------------------------------------- | -------------------------- |
| A1  | A v1 célja **bevételtermelő, nem-MDSW réteg** szállítása 9 hónapon belül; a szabályozott CDSS (IIa) a v2. | Teljes §6 prioritizálás    |
| A2  | Nincs saját CLIA/ISO 15189 labor; a genotípus-hívás **partnerlabor felelőssége**.                         | FR-300 blokk, REG-020      |
| A3  | Nincs jelenleg érvényes EESZT fejlesztői regisztráció.                                                    | §11 timeline, REG-040      |
| A4  | A PRS-motor **nem** saját fejlesztés, hanem beszállítói integráció.                                       | §6.5, NG-04                |
| A5  | Első referencia-implementáció egyetemi/klinikai partnernél, in-house kivétellel.                          | REG-011, §11 F2            |
| A6  | Csapatméret v1-re: 2–3 fejlesztő + 1 QA/RA + 1 klinikai szakértő (részidős).                              | §11 becslések              |
| A7  | Elsődleges nyelv a UI-ban magyar, a klinikai tartalom kétnyelvű (HU/EN).                                  | FR-610                     |

**Nem feltevés, hanem verifikált korlát:** a hazai jogi és EESZT-korlátok (§4) nem tárgyalhatók, nem kerülhetők meg terméktervezéssel.

---

## 1. Problem Statement

A gyógyszerelési döntés pillanatában a rendelkezésre álló genetikai információ nem hasznosul. A magyar magánegészségügyben egy farmakogenetikai vizsgálat 2026 augusztusában **499 000 Ft** listaáron kapható (Genetix DrugMap, 140+ gyógyszer), a nemzetközi kiskereskedelmi sáv teteje ennek negyede–fele (250–2000 USD, medián 300–600 USD). A felárat nem a szekvenálás, hanem a hiányzó, skálázható értelmezési infrastruktúra fizeti meg: a labor PDF-et ad, a PDF a beteg fiókjában landol, a felíró orvos hónapokkal később nem látja.

A probléma mérete kvantifikált. Egy 894 748 folyamatosan biztosított egyénen végzett elemzés szerint ±30 napos ablakkal a populáció **24,8%-a** volt kitéve potenciálisan interakcióba lépő gyógyszerpároknak, az interakciók többsége CYP2D6 vagy CYP2C19 érintettséggel; a szerzők következtetése, hogy a PGx-eredmények értelmezésekor elengedhetetlen a gyógyszer-indukált **fenokonverzió** figyelembevétele. EHR-alapú keresztmetszeti elemzésben a betegek 89,7%-ának volt legalább egy PGx-iránymutatással érintett gyógyszerrendelése, 23,1%-uknak négy vagy több actionable gyógyszerre; szimulációban 100 betegre 17 terápiamódosítás lett volna lehetséges, ha az eredmény rendelkezésre áll.

A nem-megoldás költsége: a hazai laborok és klinikák továbbra is statikus riportot adnak el prémium áron, klinikai hatás nélkül; a nemzetközi CDSS-szállítók (GenXys, OneOme, YouScript/Aranscia) EU-ban nincsenek jelen, de a belépésük idő kérdése, és az AI Act Annex I határidő (2028-08-02) után az utólagos megfelelés drágább lesz, mint a beépített.

---

## 2. Goals

Outcome-ok, nem output-ok. Mindegyik mellett a mérési módszer.

| ID     | Goal                                                   | Célérték                                                                                                  | Mérés                                                      |
| ------ | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| **G1** | A partnerlabor PGx-riport előállítási ideje csökkenjen | Kézi/félautomata baseline → **< 10 perc** VCF-től aláírásra kész riportig, 95. percentilis                | Pipeline-telemetria, `ingest→report_ready` timestamp-delta |
| **G2** | Az actionable találatok ne veszítsenek el a riportban  | A CPIC/DPWG szerint actionable gén-gyógyszer párok **100%-a** megjelenik a riportban, 0 silent drop       | Gold set regressziós teszt (§9), minden release-nél        |
| **G3** | Fenokonverzió-detektálás mint differenciátor működjön  | A fenokonverzió-gyanús esetek **≥ 90%-a** jelölve, a QA gold seten mért recall alapján                    | Gold set, §9.3                                             |
| **G4** | Bevétel a szabályozott réteg előtt                     | **≥ 3 fizető labor/klinikai partner** és ≥ 1 dokumentált case study a v1 végéig                           | Aláírt szerződések                                         |
| **G5** | A v2 (IIa) útvonal ne igényeljen újraírást             | A QMS-artefaktumok (ISO 13485 / IEC 62304 / ISO 14971) **a v1-gyel párhuzamosan** keletkeznek, nem utólag | RA gap-analysis checklist, §10                             |

**Üzleti goal, amit nem a termék teljesít:** az MKIK-akkreditációhoz szükséges 3 referencia + 1 case study. G4 ezt közvetlenül szolgálja — ez a v1 valódi stratégiai indoka.

---

## 3. Non-Goals

| ID        | Nem célja a v1-nek                                                   | Miért                                                                                                                                                                                 |
| --------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **NG-01** | Saját genotípus-hívás nyers labor-adatból (FASTQ/IDAT/raw intensity) | Ez volt a Translational Software 510(k)-bukásának pontos oka: nyers labor-adatból genotípus- és fenotípus-hívást végzett. Az L3 a partnerlabor akkreditált felelősségi köre.          |
| **NG-02** | Saját PRS-motor fejlesztése és validálása                            | Telített, ISO 13485-tanúsított, guideline-idézett piac (Allelica, Genomics plc). A validáció 3+ év többkohorszos munka; a magyar referencia-genom hiánya miatt kalibrálni sem tudjuk. |
| **NG-03** | Közvetlen betegoldali (B2C) VCF-feltöltés és riport                  | Jogi tiltás Magyarországon (§4.2), és a DTC-adatvagyon árazása bizonyítottan alacsony: a 23andMe 15M+ profilja 305 M USD-ért ment el csődeljárásban (≈20 USD/profil).                 |
| **NG-04** | Onkológiai szomatikus variáns-interpretáció                          | Külön szabályozási és tudásbázis-domain (IVDR-érintettség, companion diagnostics). Önálló kezdeményezés.                                                                              |
| **NG-05** | EESZT írási művelet (eRecept, eProfil rögzítés)                      | BM-engedélyezett medikai rendszer nélkül nem lehetséges. A v1 az engedélyezett rendszerek **modulja**, nem helyettesítője.                                                            |
| **NG-06** | LLM-alapú szabad szöveges klinikai tanácsadás                        | Nem determinisztikus, nem verifikálható, és a v2 IIa dossziéját megölné. Az LLM szerepe kizárólag §6.6 szerint korlátozott.                                                           |

---

## 4. Kötelező korlátok (verifikált, nem tárgyalható)

### 4.1 EU MDR / MDSW

- **MDCG 2019-11 Rev.1** (2025-06-17): a prognózis- és predikciós szoftvert kifejezetten hatókörbe vonja, általában IIa vagy magasabb osztályban; minden modult önállóan kell minősíteni, a modulok közti függőségeket dokumentálni kell. Az MDCG osztályozó táblázatában a Class I meg sem jelenik.
- **Következmény:** az L4 (PGx-szabálymotor) és L5 (PRS) **IIa minimum → Notified Body**. Az „a végső döntést az orvos hozza" érvelés az FDA 2022-es CDS guidance logikája, az MDR-ben nem működik.

### 4.2 Magyar humángenetikai törvény — 2008. évi XXI. tv.

- Humángenetikai vizsgálat csak a szakmai minimumfeltételek szerint felszerelt, szakképzett személyi háttérrel és **működési engedéllyel rendelkező** szolgáltatónál végezhető.
- A mintavétel **előtt** genetikai tanácsadás keretében kell tájékoztatni az érintettet a vizsgálat céljáról, elvégzésének vagy elmaradásának előnyeiről és kockázatairól, a lehetséges eredmény következményeiről.
- A biobankban tárolt minden genetikai mintát és adatot **legalább 30 évig** nyilván kell tartani; a hozzájárulás visszavonásakor minden genetikai adatra vonatkozó nyilvántartást meg kell semmisíteni.
- Automatizált adatfeldolgozás, kódolás esetén az érintettet kérelmére **tájékoztatni kell az alkalmazott informatikai módszerről**.

> Ez az utolsó pont a legritkábban észrevett: magyar jogi alapon **algoritmus-magyarázhatósági kötelezettség** áll fenn, függetlenül az AI Act-től. Lásd FR-710.

### 4.3 EESZT

- EESZT-csatlakozásra kizárólag a BM által engedélyezett szoftver használható; a BM engedélyezi és ellenőrzi, és verzióváltáskor is folyamatosan teljesíteni kell az engedélyezési követelményeket.
- Fejlesztői regisztráció határideje **2025-10-31** volt (lejárt); az elvárt ISO-tanúsítás megszerzésének határideje **2026-09-30**. Regisztráció nélkül a Redmine-hozzáférés inaktiválásra kerül, és érvényes szoftverengedély is visszavonható.

### 4.4 AI Act

- **MDCG 2025-6 / AIB 2025-1** (2025-06-19): egy MDAI akkor magas kockázatú az AI Act 6(1) szerint, ha (i) biztonsági komponens vagy maga is orvostechnikai eszköz, **és** (ii) MDR/IVDR szerinti bejelentett szervezet általi harmadik feles megfelelőségértékelés alá esik. Class I eszközök nem MDAI. Az egészségügyi intézményen belül fejlesztett és kizárólag ott használt in-house MDAI jellemzően nem magas kockázatú, ha nincs bejelentett szervezet a folyamatban.
- **Digital Omnibus** (Tanács végső jóváhagyás 2026-06-29, EP 2026-06-16): Annex III → **2027-12-02**, Annex I → **2028-08-02**. Az alkalmazási dátumok már nem kötődnek a harmonizált szabványok elkészültéhez.
- **A PCE-re az Annex I / 2028-08-02 óra ketyeg.**

### 4.5 EHDS — (EU) 2025/327

- Hatályba lépés 2025-03-26. Másodlagos felhasználás a legtöbb kategóriára **2029-03-26**, humán genetikai és klinikai vizsgálati adatra hatéves átmenettel **2031-03-26**.
- **Következmény:** EHDS-alapú adatmonetizációra 2031 előtt nem lehet üzleti tervet építeni. Az EHDS-interoperabilitás viszont *ma* tervezési követelmény (NFR-050).

---

## 5. Personák és user story-k

### 5.1 Personák

| P      | Persona                                                                   | Kontextus                                     | Fő fájdalom                                                                             |
| ------ | ------------------------------------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------- |
| **P1** | **Labor-vezető / molekuláris genetikus** (SYNLAB, Neumann, Genoid típusú) | Panel- vagy WES-adatból riportot kell kiadnia | Kézi értelmezés, verziókövetés nélküli Word-sablon, CPIC-frissítések követése           |
| **P2** | **Felíró klinikus** (magánklinika, belgyógyász/kardiológus/psychiáter)    | 12 perc/beteg, gyógyszert ír fel              | Nem tudja, van-e PGx-eredmény; ha van, 40 oldalas PDF                                   |
| **P3** | **Klinikai farmakológus / gyógyszerész**                                  | Medication review, polypharmacy               | Fenokonverzió és DDI kézi összevetése                                                   |
| **P4** | **Genetikai tanácsadó**                                                   | 2008/XXI. szerinti kötelező konzultáció       | Nincs strukturált eszköz a tanácsadás dokumentálására és a hozzájárulás granularitására |
| **P5** | **Klinika-üzemeltető / adatvédelmi tisztviselő**                          | Compliance-felelősség                         | 30 éves megőrzés, visszavonás-kaszkád, auditálhatóság                                   |
| **P6** | **Medikai rendszer szállító** (EESZT-engedélyezett vendor)                | Integrációs partner, nem végfelhasználó       | Nem akar MDR-felelősséget átvenni                                                       |

### 5.2 User story-k prioritási sorrendben

**P1 — Labor**

1. Labor-vezetőként **egyetlen művelettel** akarok VCF-ből standardizált PGx-riportot előállítani, hogy ne kelljen kézzel értelmeznem CPIC-táblákat.
2. Labor-vezetőként látni akarom, **melyik guideline-verzió** alapján készült egy riport, hogy hat hónappal később rekonstruálni tudjam a döntést.
3. Labor-vezetőként azt akarom, hogy a rendszer **jelezze, ha a benyújtott VCF nem fedi le** a panel egy génjét, hogy ne adjak ki hamis „normál" eredményt.
4. Labor-vezetőként a riportot **saját arculatommal és aláíró orvosommal** akarom kiadni, hogy a saját szolgáltatásom része legyen.
5. Labor-vezetőként **újra akarom generálni** a régi riportokat új guideline-verzióval, hogy lássam, kit kell visszahívni.

**P2 — Klinikus**

6. Felíró klinikusként azt akarom, hogy a **felírás pillanatában** kapjak figyelmeztetést, ha a beteg genotípusa a tervezett gyógyszerrel ütközik — nem külön portálon bejelentkezve.
7. Felíró klinikusként **konkrét alternatívát** akarok látni, nem csak tiltást, hogy azonnal tudjak felírni valamit.
8. Felíró klinikusként **el akarom tudni utasítani** a figyelmeztetést indoklással, hogy a rendszer ne blokkolja a klinikai megítélésemet.
9. Felíró klinikusként a **hivatkozást** akarom látni (CPIC guideline, FDA címke), hogy magam ítélhessem meg az evidenciát.
10. Felíró klinikusként azt akarom, hogy **ne kapjak riasztást** olyan gén-gyógyszer párra, ami nem actionable, hogy ne szokjak le az elolvasásáról.

**P3 — Klinikai farmakológus**

11. Klinikai farmakológusként azt akarom, hogy a rendszer **a beteg aktuális gyógyszerlistája alapján** jelezze a gyógyszer-indukált fenokonverziót, hogy ne „normál metabolizálóként" kezeljek egy funkcionálisan lassú metabolizálót.
12. Klinikai farmakológusként medication review-hoz **egy oldalon** akarom látni a genotípust, a DDI-t és a szervfunkciós módosítókat.

**P4 — Genetikai tanácsadó**

13. Genetikai tanácsadóként azt akarom, hogy a rendszer **ne engedjen riportot kiadni**, amíg a mintavétel előtti tanácsadás nincs dokumentálva, hogy ne sértsük a 2008/XXI. tv.-t.
14. Genetikai tanácsadóként **génenkénti/indikációnkénti hozzájárulást** akarok rögzíteni, hogy a beteg lemondhasson egyes eredmények megismeréséről.

**P5 — Compliance**

15. Adatvédelmi tisztviselőként azt akarom, hogy a hozzájárulás visszavonása **kaszkádolva** töröljön minden genetikai adatot és nyilvántartást, hogy teljesítsük a törvényi kötelezettséget.
16. Adatvédelmi tisztviselőként **exportálható audit trailt** akarok minden genetikai adathozzáférésről, hogy hatósági ellenőrzésen bemutatható legyen.

**P6 — Integrációs partner**

17. Medikai rendszer szállítóként **szabvány FHIR/CDS Hooks felületet** akarok, hogy ne kelljen a saját termékembe üzleti logikát építenem.
18. Medikai rendszer szállítóként **írásban rögzített MDR-felelősségi határvonalat** akarok, hogy ne váljak akaratlanul gyártóvá.

**Edge case story-k**

19. Klinikusként azt akarom, hogy ha **nincs PGx-adat** a betegről, a rendszer ezt explicit mondja meg, ne hallgasson.
20. Labor-vezetőként azt akarom, hogy **hibás/csonka VCF** esetén beszédes hibát kapjak, ne részleges riportot.
21. Klinikusként azt akarom, hogy ha a rendszer **nem elérhető**, a felírás ne blokkolódjon.

---

## 6. Funkcionális követelmények

Prioritás: **P0** = nélküle nem szállítható · **P1** = fast follow · **P2** = architekturális biztosíték, most nem épül.

Réteg-hivatkozás: L0–L7 az architektúra szerint (L0 Identity&Consent, L1 Ingestion, L2 Normalization, L3 Genotype→Phenotype, L4 Knowledge&Rules, L5 PRS, L6 Delivery, L7 Observability).

---

### 6.1 L0 — Identity & Consent

#### FR-100 · Genetikai tanácsadás előfeltétel-kapu — **P0**

A rendszer nem engedélyezi PGx-riport generálását olyan esethez, amelyhez nincs rögzítve mintavétel előtti genetikai tanácsadás.

Acceptance criteria:

- [ ] Given egy eset, amelyhez nincs `counselling_record`, When a felhasználó riportgenerálást indít, Then a művelet elutasításra kerül `E-CONSENT-001` kóddal és a 2008/XXI. tv. 8. §-ra hivatkozó magyar nyelvű indoklással.
- [ ] Given egy `counselling_record`, amelynek dátuma **későbbi** a mintavétel dátumánál, When riportgenerálás indul, Then elutasítás `E-CONSENT-002` kóddal (a tanácsadás a mintavétel előtt kötelező).
- [ ] Given érvényes tanácsadási rekord, When riportgenerálás indul, Then a művelet folytatódik és a riport metaadatában szerepel a tanácsadó azonosítója és a tanácsadás dátuma.
- [ ] A kapu **nem** kikapcsolható konfigurációval, sem admin szerepkörrel. Negatív teszt: admin sem tudja megkerülni.

Technikai megjegyzés: a tanácsadási rekord bevihető kézzel (v1) vagy FHIR `Consent` + `Encounter` referenciából (v1.1).

#### FR-110 · Granuláris, visszavonható hozzájárulás — **P0**

Hozzájárulás rögzítése és kezelése gén/génpanel és felhasználási cél szintjén.

- [ ] Given a beteg lemondott egy adott gén eredményének megismeréséről, When riport generálódik, Then az adott gén eredménye a beteg-példányból kimarad, de a klinikus-példányban (ha a klinikus hozzáférése külön engedélyezett) megjelenhet — a szeparáció konfigurációval, nem kódmódosítással állítható.
- [ ] Given egy hozzájárulás-visszavonás, When a visszavonás rögzítésre kerül, Then a rendszer **72 órán belül** kaszkádolva töröl minden érintett genetikai adatot és nyilvántartási bejegyzést, és a törlésről visszavonhatatlan tanúsítványt állít ki.
- [ ] A visszavonási kaszkád **derived** adatra is kiterjed: diplotípus, fenotípus, generált riportok, cache-elt PRS-eredmények.
- [ ] Negatív teszt: a visszavonás után a korábbi riport URL 410 Gone-t ad, nem 200-at cache-ből.

#### FR-120 · 30 éves nyilvántartás — **P0**

- [ ] Minden genetikai minta/adat felvétele, vizsgálata, tárolása, feldolgozása és továbbítása naplózott, a naplóbejegyzés tartalmazza a minta típusát, mennyiségét, eredetét, rendeltetési célját és a kialakított genetikai adatot.
- [ ] A napló **legalább 30 évig** megőrződik, kivéve visszavonás esetén.
- [ ] A napló append-only, kriptográfiailag láncolt (hash-chain), utólag nem módosítható. Negatív teszt: DB-szintű UPDATE megkísérlése bejegyzésen hibát ad.
- [ ] A napló strukturált formában (CSV + JSON) exportálható hatósági ellenőrzésre.

#### FR-130 · Beteg-azonosítás és pszeudonimizáció — **P0**

- [ ] A genetikai adat a feldolgozó rétegekben (L2–L5) kizárólag pszeudonim azonosítóval szerepel; az újraazonosító kulcs külön, szigorúbb hozzáférési kontroll alatt tárolt store-ban van.
- [ ] Given L4 szabálykiértékelés, When a motor logol, Then a logban nem szerepel közvetlenül azonosító adat (név, TAJ, születési dátum). Negatív teszt: log-scanner CI-lépés PII-mintákra.

---

### 6.2 L1 — Ingestion

#### FR-200 · VCF befogadás — **P0**

- [ ] Támogatott: VCFv4.2 és 4.3, single-sample és multi-sample, GRCh37 és GRCh38, bgzip+tabix indexelt és plain.
- [ ] Given multi-sample VCF, When feltöltés történik, Then a rendszer sample-enként szétválasztja és minden sample-hez külön esetet igényel (nem tippel beteg-hozzárendelést).
- [ ] Given nem támogatott referencia-genom vagy hiányzó `##reference` header, When feltöltés történik, Then elutasítás `E-VCF-003` kóddal, a hiányzó elem megnevezésével.
- [ ] Fájlméret-limit: 5 GB/fájl (WGS gVCF fejtér). E fölött chunked upload.

#### FR-210 · Lefedettség-ellenőrzés (callability) — **P0**

**Ez a legkritikusabb egyetlen követelmény a teljes specben.** A hiányzó pozíció nem azonos a referencia-alléllal.

- [ ] Given egy VCF, amelyben a panel egy génjének egy vagy több definiáló pozíciója **nem** vizsgált (nem szerepel, és nincs gVCF reference block, amely lefedi), When feldolgozás történik, Then az adott gén státusza `INDETERMINATE`, **nem** `NORMAL`.
- [ ] A riport minden génhez explicit callability-státuszt közöl: `CALLED` / `PARTIAL` / `INDETERMINATE` / `NOT_TESTED`.
- [ ] Given `INDETERMINATE` gén, When riport generálódik, Then az adott génhez tartozó gyógyszerajánlások **nem** jelennek meg pozitív állításként, hanem „nem meghatározható" jelöléssel.
- [ ] Negatív teszt: a gold setben szerepel legalább 3 eset, ahol a naiv missing-to-reference feltevés klinikailag ellentétes ajánlást adna; ezeket a rendszernek `INDETERMINATE`-ként kell jelölnie.

Technikai megjegyzés: a PharmCAT preprocessor `--absent-to-ref` és `--unspecified-to-ref` funkciói **nem** hívhatók vakon; a viselkedést esetenként, dokumentált indokkal kell beállítani.

#### FR-220 · Laboreredmény- és gyógyszerlista-behúzás — **P0**

- [ ] FHIR R4 `Observation` (eGFR/kreatinin, ALT/AST/bilirubin, albumin), `MedicationRequest` / `MedicationStatement` fogadása.
- [ ] Given FHIR-forrás nem elérhető, When eset feldolgozódik, Then a rendszer kézi bevitelt engedélyez, és a riport jelzi, hogy a klinikai kontextus kézi bevitelű.
- [ ] Given nincs sem FHIR, sem kézi klinikai adat, When riport generálódik, Then a fenokonverzió- és szervfunkciós modul kimenete explicit „nem értékelhető — hiányzó klinikai adat", nem hallgatólagos kihagyás.

#### FR-230 · HL7 v2 LRI laborüzenet — **P1**

- [ ] HL7 v2.5.1 LRI ORU^R01 fogadása genotípus-eredményhez.

#### FR-240 · Külső genotípus/fenotípus bevitel — **P0**

A NG-01 (nincs saját nyers hívás) miatt kritikus: a partnerlabor által **már meghívott** diplotípus közvetlen befogadása.

- [ ] Tab-delimited outside-call fájl és strukturált API-endpoint fogadása diplotípusra (`gene`, `diplotype`, `calling_lab`, `signing_physician`, `method`, `call_date`).
- [ ] Given outside call és VCF-alapú hívás ütközik, When mindkettő elérhető, Then a rendszer **nem választ automatikusan**: konfliktust jelez `W-CALL-010`-nel és emberi döntést kér.

---

### 6.3 L2 — Normalization

#### FR-250 · Variáns- és terminológia-normalizálás — **P0**

- [ ] Variáns-reprezentáció HGVS és GA4GH VRS szerint normalizált, left-align + trim.
- [ ] Gyógyszer-kódolás ATC + a hazai törzs (OGYÉI/PHARMINDEX) azonosítójára mappelve; laborparaméter LOINC; fenotípus SNOMED CT vagy CPIC-terminológia.
- [ ] Given ismeretlen gyógyszerkód, When mappelés fut, Then az eset `NEEDS_MAPPING` állapotba kerül és nem generál riportot csendben hiányos gyógyszerlistával.
- [ ] A mapping-táblák verziózottak és a riportban a verzió szerepel.

---

### 6.4 L3 — Genotype → Phenotype

#### FR-300 · PharmCAT-integráció — **P0**

- [ ] PharmCAT `NamedAlleleMatcher` és `Phenotyper` modulok hívása; a pipeline verziója, a PharmVar allél-definíció verziója és a CPIC adatverzió a riport metaadatában rögzített.
- [ ] Given fázisolt (phased) VCF, When hívás történik, Then a fázisinformáció felhasználásra kerül; unphased esetben a rendszer ambiguitást jelöl, nem választ önkényesen.
- [ ] Given CYP2D6, When hívás történik, Then a rendszer jelzi, ha structural variant (deletion/duplication/hybrid) nem meghatározható a bemenetből — a CYP2D6 a legnagyobb klinikai hatású és a legnehezebben hívható gén.
- [ ] Licenc-megfelelés: a PharmCAT MPL 2.0 alatt van; a származékos módosítások közzétételi kötelezettsége dokumentált, és a PharmCAT által hívott egyéb programok licencei külön ellenőrzöttek.

#### FR-310 · Génlista mint verziózott konfiguráció — **P0**

A design basis a **PGx-Passport**: 58 germline variáns allél 14 génben — CYP2B6, CYP2C9, CYP2C19, CYP2D6, CYP3A5, DPYD, F5, HLA-A, HLA-B, NUDT15, SLCO1B1, TPMT, UGT1A1, VKORC1 (van der Wouden et al., CPT 2019). A PREPARE-t a Lancet „12-gene panel"-ként publikálta; a két lista nem azonos, az eltérést a P01 gate-en primer forrásból tisztázni kell (§10 OQ-02).

- [ ] A génlista, a variáns-definíciók és a szabálybázis **külső, verziózott konfiguráció**, nem kódba írt konstans.
- [ ] Bizonyíték a követelmény szükségességére: a DPWG visszavonta az F5 – szisztémás hormonális kontraceptívum ajánlását, ezért az F5 kikerült a PharmCAT-ből. A génlista **nem stabil**.
- [ ] Given konfigurációváltás, When új verzió aktiválódik, Then a változás change-control rekordot generál (ki, mit, mikor, milyen forrás alapján), és a korábbi riportok érintettsége listázható.

---

### 6.5 L4 / L5 — Knowledge, Rules, PRS

> **Ez a réteg MDSW IIa.** A v1-ben kizárólag „laboratóriumi riport-előállítás az aláíró orvos felelősségével" rendeltetéssel szállítható, aktív, felírás-pillanatú riasztás nélkül. Az aktív CDSS a v2.

#### FR-400 · Szabálymotor — **P0 (passzív) / P1 (aktív)**

- [ ] CPIC, ClinPGx-annotált DPWG és ClinPGx-annotált FDA-címke ajánlások kiértékelése diplotípus alapján.
- [ ] Given azonos gén-gyógyszer párra eltérő CPIC és DPWG ajánlás, When kiértékelés fut, Then **mindkettő** megjelenik forrásmegjelöléssel; a rendszer nem szintetizál harmadik, egyik forrásban sem szereplő ajánlást.
- [ ] Minden kimeneti állítás mellett gépi hivatkozás: forrás (CPIC/DPWG/FDA), guideline-verzió, evidencia-szint, mély link.
- [ ] Negatív teszt: nincs olyan riport-állítás, amelyhez ne tartozna forráshivatkozás. CI-ellenőrzés: `assert unsourced_claims == 0`.

#### FR-410 · Fenokonverzió-modul — **P0** *(a fő differenciátor)*

- [ ] A beteg aktuális gyógyszerlistája alapján a rendszer detektálja a CYP-inhibitor/induktor együttadást, és jelzi a genotípus-alapú fenotípustól eltérő **funkcionális** fenotípust.
- [ ] Given CYP2D6 normál metabolizáló genotípus + erős CYP2D6-inhibitor (pl. paroxetin, fluoxetin) egyidejű szedése, When kiértékelés fut, Then a kimenet `genotype_phenotype = NM`, `functional_phenotype = PM/IM`, és a különbség explicit jelölt.
- [ ] A fenokonverzió-kimenet **soha nem írja felül** a genotípus-alapú fenotípust, hanem mellette áll — visszamenőleges rekonstruálhatóság miatt.
- [ ] Given szervfunkciós eltérés (eGFR < 30, emelkedett bilirubin), When kiértékelés fut, Then a rendszer jelzi az érintett gyógyszereknél, hogy a PGx-ajánlás mellett szervfunkciós dózismódosítás is indokolt lehet.
- [ ] A modul kimenete **minősítés, nem dózisszám**. Konkrét dózist a v1 nem javasol (MDR-osztály-tartás).

#### FR-420 · Alert-relevancia szűrés — **P0**

- [ ] A rendszer csak actionable gén-gyógyszer párra generál riasztást; a nem-actionable eredmény a riport függelékébe kerül, nem riasztásba.
- [ ] Riasztás-kategóriák: `CRITICAL` (alternatíva javasolt), `WARNING` (monitorozás javasolt), `INFO` (nincs teendő).
- [ ] Given egy eset 40 gén-gyógyszer párral, When riport generálódik, Then a `CRITICAL` + `WARNING` riasztások száma a riport első oldalán, a részletek mögötte.

#### FR-430 · PRS — **P2 (nem épül a v1-ben)**

Architekturális biztosíték. A v1 úgy tervezendő, hogy a PRS beszállító beköthető legyen újraírás nélkül.

- [ ] Az L5 interfész definiált (`POST /prs/score` → `{score, percentile, absolute_risk, ancestry_calibration, provider, model_version}`), de nincs implementáció.
- [ ] A szerződéses követelmény a leendő beszállítóra: ISO 13485, dokumentált ancestry-kalibráció, és az eMERGE-típusú klinikai implementációs pipeline megléte (score transfer klinikai laborba, teljesítmény-validáció és -verifikáció).
- [ ] A P2 státusz indoklása a dokumentumban rögzített: a PRS-ek szuboptimális precizitása, rossz populációk közti átvihetősége és a klinikusok/betegek körében alacsony fogalmi ismertsége (Kullo et al., Nat Rev Genet 2026;27:246–263), valamint hogy a PRS-ek nem európai eredetű populációkban túlbecsülik a kockázatot, a legnagyobb túlbecsléssel afrikai populációkban.

---

### 6.6 L6 — Delivery

#### FR-500 · Riport-generálás — **P0**

- [ ] Kimeneti formátumok: PDF (aláírásra kész), FHIR Bundle a Genomics Reporting IG szerint, és strukturált JSON.
- [ ] A FHIR-kimenet a Genomics Reporting IG **v3.0.0 (STU3)**, FHIR R4 alapon készül; a v4.0.0 (STU4) ballot új operations-készletet és `GenomicStudy` támogatást hoz, ezért az implementáció verzió-agnosztikus mapping-réteget használ.
- [ ] A PDF-riport minden oldalán szerepel: guideline-verziók, pipeline-verzió, callability-összefoglaló, aláíró orvos helye.
- [ ] Given white-label partner, When riport generálódik, Then a partner arculata és aláírója jelenik meg, a PCE mint technológiai szállító a kolofonban.

#### FR-510 · Riport-újragenerálás guideline-frissítéskor — **P1**

- [ ] Given új CPIC/DPWG verzió aktiválása, When az admin újraértékelést indít, Then a rendszer listázza azokat a korábbi eseteket, ahol az ajánlás **megváltozott**, és riportonként jelzi a delta-t.
- [ ] Az újragenerálás nem írja felül az eredeti riportot; új verzió jön létre, az eredeti immutábilis marad.

#### FR-520 · CDS Hooks szolgáltatás — **P1** *(v2-ben P0)*

- [ ] `order-select` és `order-sign` hook implementáció; a válasz `Card` objektumként adja a riasztást, `suggestion`-nel az alternatívára és `link`-kel az evidenciára.
- [ ] Given a CDS szolgáltatás > 2 s alatt nem válaszol, When a hívó rendszer timeout-ol, Then a felírás **nem blokkolódik** (fail-open). Ez klinikai biztonsági követelmény, nem teljesítmény-preferencia.
- [ ] Given nincs PGx-adat a betegről, When hook meghívódik, Then a válasz explicit „nincs elérhető PGx-eredmény" card, nem üres válasz.

#### FR-530 · SMART on FHIR alkalmazás — **P1**

- [ ] EHR-launch context (`patient`, `encounter`, `user`) fogadása; a nézet a felírási workflow-ba illeszkedő, nem önálló portál.

> Tervezési indoklás: a felhasználói kutatás szerint a farmakogenetikai adatot a meglévő EHR-en belül kell megjeleníteni, nem külön portálon, és a felírási workflow-ban, nem statikusan tárolt diszkrét eredményként; ehhez szétcsatolt, szabvány-alapú architektúra kell, amely API-kkal elválasztja az adatot az alkalmazástól. A v1 önálló webes felülete **átmeneti**, nem végállapot.

#### FR-540 · Beteg-példány riport — **P1**

- [ ] Külön, laikus nyelvű riport-változat, amely nem tartalmaz dózis- vagy terápiajavaslatot, csak a genotípus-információt és a „beszéljen kezelőorvosával" instrukciót.

---

### 6.7 L7 — Observability & Governance

#### FR-600 · Alert-fatigue és override telemetria — **P0**

- [ ] Minden riasztás megjelenítése, elfogadása és elutasítása naplózott, az elutasítás kötelező indoklás-kategóriával.
- [ ] Az override-ráta gén-gyógyszer pár szinten aggregálható; a > 80% override-rátájú szabály automatikusan review-listára kerül.
- [ ] Ez az adat egyben a PMS/PMCF (post-market surveillance) input a v2 MDR-dossziéhoz.

#### FR-610 · Kétnyelvű klinikai tartalom — **P0**

- [ ] UI és beteg-riport magyar; a klinikai ajánlás-szöveg magyar **és** az eredeti angol forrásszöveg is elérhető.
- [ ] Given magyar fordítás egy új guideline-ajánláshoz nem áll rendelkezésre, When riport generálódik, Then az angol eredeti jelenik meg jelöléssel — **nem** gépi fordítás.

#### FR-700 · LLM-használat korlátozása — **P0**

- [ ] LLM kizárólag (a) riport-szöveg olvashatósági átfogalmazására **előre jóváhagyott sablonkészletből**, és (b) belső dokumentum-keresésre használható.
- [ ] Az LLM **nem** generál gyógyszerajánlást, fenotípus-hívást, dózist vagy kockázati számot. Negatív teszt: a klinikai kimeneti útvonalon nincs LLM-hívás; CI-ellenőrzés a call graph-on.
- [ ] Indoklás: az AI Act Annex I magas kockázatú út (2028-08-02) mellett a nem-determinisztikus komponens a IIa dossziét megnehezíti; és ha GPAI modellre épülünk, downstream provider-ként a device-szintű kötelezettségek akkor is ránk hárulnak, míg a modell-szintű GPAI kötelezettségek a modell szolgáltatójára.

#### FR-710 · Algoritmus-magyarázat kérésre — **P0**

Jogi alap: a 2008. évi XXI. tv. szerint automatizált adatfeldolgozás, kódolás esetén az érintettet kérelmére tájékoztatni kell az alkalmazott informatikai módszerről.

- [ ] Given beteg vagy képviselője magyarázatot kér, When a kérés rögzítésre kerül, Then a rendszer esetspecifikus, laikus nyelvű magyarázatot generál: mely gének, milyen diplotípus, melyik guideline, milyen szabály vezetett a kimenethez.
- [ ] A magyarázat determinisztikus és reprodukálható: ugyanaz az eset ugyanazt a magyarázatot adja.

---

## 7. Nem-funkcionális követelmények

| ID          | Követelmény                     | Célérték                                                                                                                           | Ellenőrzés                 |
| ----------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| **NFR-010** | Pipeline-átfutás (VCF → riport) | p95 < 10 min, p99 < 25 min WES-re                                                                                                  | Load teszt                 |
| **NFR-011** | CDS Hooks válaszidő             | p95 < 800 ms, hard timeout 2 s, fail-open                                                                                          | Szintetikus monitor        |
| **NFR-020** | Rendelkezésre állás             | 99,5% üzleti időben (H–P 7–20 CET); a CDS Hooks fail-open miatt nem klinikai-kritikus                                              | SLO dashboard              |
| **NFR-030** | Adat-lokalizáció                | Genetikai adat EU-ban tárolt és feldolgozott; alvállalkozói lánc dokumentált                                                       | DPA audit                  |
| **NFR-031** | Titkosítás                      | At-rest AES-256, in-transit TLS 1.3; a genetikai payload rétegzett titkosítású, az újraazonosító kulcs külön KMS-ben               | Pentest                    |
| **NFR-032** | Hozzáférés                      | RBAC + kötelező MFA minden genetikai adatot látó szerepre; least privilege; break-glass eljárás naplózva                           | Access review negyedévente |
| **NFR-033** | Titokkezelés                    | Nincs secret a repóban; gitleaks + Semgrep CI gate; kulcsrotáció ≤ 90 nap                                                          | CI gate                    |
| **NFR-040** | Auditálhatóság                  | Minden genetikai adathozzáférés naplózott (ki, mit, mikor, milyen jogalapon), append-only                                          | FR-120 teszt               |
| **NFR-050** | EHDS-készültség                 | Az adatmodell EHDS/MyHealth@EU-kompatibilis leképezhető; nem implementált, de nem is kizárt                                        | Architecture review        |
| **NFR-060** | Reprodukálhatóság               | Adott bemenet + adott konfigurációverzió → bitre azonos kimenet                                                                    | Determinizmus-teszt CI-ben |
| **NFR-070** | Kódminőség                      | IEC 62304 szerinti software safety classification (várhatóan Class B); unit + integrációs coverage ≥ 80% a klinikai útvonalon 100% | CI                         |
| **NFR-080** | Katasztrófa-visszaállítás       | RPO ≤ 1 h, RTO ≤ 8 h; a 30 éves nyilvántartás külön, immutábilis archívumban                                                       | DR-teszt évente            |
| **NFR-090** | Skálázás                        | 10 000 eset/hó lineáris költséggel; a PharmCAT-futtatás izolált, horizontálisan skálázható worker                                  | Kapacitásteszt             |

---

## 8. Szabályozási és compliance követelmények

| ID          | Követelmény                                                                                                                                                                                       | Prioritás | Határidő                |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ----------------------- |
| **REG-010** | A v1 rendeltetése (`intended purpose`) írásban rögzített, és a nem-MDSW státusz indoklása dokumentált az MDCG 2019-11 Rev.1 döntési fája alapján, modulonként                                     | **P0**    | v1 előtt                |
| **REG-011** | Az F2 referencia-implementáció in-house eszközként fut az egészségügyi intézményen belül; a kivétel feltételei (nincs bejelentett szervezet a megfelelőségértékelésben) dokumentáltan teljesülnek | **P0**    | F2 indulás              |
| **REG-020** | Írásos felelősségi határvonal a partnerlaborral: a genotípus/fenotípus-hívás a labor aláíró orvosának felelőssége                                                                                 | **P0**    | Első partner előtt      |
| **REG-021** | Írásos felelősségi határvonal az integrációs partnerrel (medikai rendszer szállító): ki a gyártó, ki a distributor                                                                                | **P0**    | Első integráció előtt   |
| **REG-030** | ISO 13485 QMS felépítése, IEC 62304 szoftver-életciklus, ISO 14971 risk management — **a v1-gyel párhuzamosan**, nem utólag                                                                       | **P0**    | F2-vel párhuzamosan     |
| **REG-031** | Person Responsible for Regulatory Compliance (MDR Art. 15) kijelölve; mikrovállalkozásnál külső PRRC igénybe vehető, de a feltételek dokumentáltan teljesülnek                                    | **P0**    | F2                      |
| **REG-040** | EESZT fejlesztői regisztráció + ISO-tanúsítás                                                                                                                                                     | **P0**    | **ISO: 2026-09-30**     |
| **REG-050** | GDPR Art. 9 jogalap dokumentálva; DPIA elvégezve genetikai adatkezelésre; adatvédelmi tisztviselő kijelölve                                                                                       | **P0**    | v1 előtt                |
| **REG-060** | AI Act gap-analysis Art. 9–15, 17, 72 ellen; az AI-specifikus követelmények az MDR technikai fájlba **integrálva, nem duplikálva** (MDCG 2025-6 ajánlása szerint)                                 | **P1**    | 2027 Q4                 |
| **REG-061** | AI literacy (AI Act Art. 4) — ez a kötelezettség **nem** került elhalasztásra a Digital Omnibusszal, 2025-02-02 óta alkalmazandó                                                                  | **P0**    | Azonnal                 |
| **REG-070** | ISO/IEC 27001 (és opcionálisan 42001) — az EESZT ISO-követelmény és az enterprise beszerzés miatt                                                                                                 | **P1**    | 2026-09-30-hoz igazítva |
| **REG-080** | Nyílt forráskódú licenc-inventár (SPDX SBOM); a PharmCAT MPL 2.0 és a hívott programok licenceinek külön ellenőrzése, mert azok más licenc alá tartozhatnak                                       | **P0**    | v1 előtt                |

---

## 9. Validációs és teszt-stratégia

### 9.1 Gold set

Nélküle a §2 goal-ok nem mérhetők és a v2 dosszié nem védhető.

- **Méret:** minimum 200 eset. Összetétel: 60 szintetikus (edge case-ekre tervezett), 100 nyilvános referencia (GeT-RM / AMP referencia-anyagok diplotípusai), 40 valós, deidentifikált partnerlabor-eset.
- **Kötelező edge case-ek:** hiányzó pozíció (FR-210), CYP2D6 structural variant, unphased ambiguitás, CPIC–DPWG ütközés, fenokonverzió, `INDETERMINATE` gén actionable gyógyszerrel, visszavont hozzájárulás, csonka VCF.
- **Ground truth:** két független annotátor (klinikai farmakológus + molekuláris genetikus), egyet nem értés esetén harmadik döntőbíró. Egyetértés mérése Cohen's kappa; **elfogadási küszöb κ ≥ 0,80**, ez alatt az annotációs útmutató újraírandó, nem a küszöb leszállítandó.
- **Verziókövetés:** a gold set DVC-vel verziózott, minden release-hez rögzített gold set verzió tartozik.

### 9.2 Metrikák és küszöbök

| Mérés                                     | Küszöb                      | Megjegyzés                                               |
| ----------------------------------------- | --------------------------- | -------------------------------------------------------- |
| Diplotípus-egyezés a referencia-anyagokon | **100%**                    | Ez nem statisztikai, hanem determinisztikus követelmény  |
| Actionable ajánlás recall                 | **100%** (0 false negative) | G2; a false negative klinikai kár                        |
| Callability-jelölés helyessége            | **100%**                    | FR-210; a legfontosabb egyetlen teszt                    |
| Fenokonverzió recall                      | **≥ 90%**                   | G3                                                       |
| Fenokonverzió precision                   | **≥ 75%**                   | Alacsonyabb, mert a false positive itt „nézd meg" típusú |
| Forrás nélküli állítás                    | **0**                       | FR-400 CI-gate                                           |

### 9.3 Regressziós kapu

- [ ] Minden guideline-verzió-váltás után a teljes gold set újrafut; a delta-riport kötelező review-tárgy a release előtt.
- [ ] Given a gold seten bármely metrika a küszöb alá esik, When release-t próbálnak indítani, Then a CI blokkol. Nincs manuális override.

### 9.4 Klinikai evidencia-hivatkozás a v2 dossziéhoz

A klinikai evaluáció alapja a PREPARE: nyílt, multicentrikus, kontrollált, klaszter-randomizált crossover implementációs vizsgálat 12-génes PGx-panellel, 18 kórházban, 9 közösségi egészségügyi központban és 28 közösségi gyógyszertárban, 7 európai országban (Ausztria, Görögország, Olaszország, Hollandia, Szlovénia, Spanyolország, UK); a genotípus-vezérelt kezelés szignifikánsan csökkentette a klinikailag releváns ADR-ek előfordulását, és megvalósítható volt eltérő európai ellátásszervezési környezetekben. 6944 beteg 41 696 alkalmasból, 6495 (93,5%) enrolláltnál actionable variánssal; ~30%-os csökkenés az ADR esélyhányadosában.

**Forráskritika kötelező része a dossziénak:** a csökkenés elsősorban grade 2 ADR-ekből származott, döntően „possible to probable" adjudikált oksági kapcsolattal, és a Lancet legalább négy kritikai levelet közölt (Curtis; Rogers et al.; Van der Linden; Peñas-LLedó & LLerena). A Notified Body ezt meg fogja találni — jobb, ha mi hozzuk be.

---

## 10. Open Questions

### Blokkoló (v1 indulás előtt megválaszolandó)

| ID        | Kérdés                                                                                                                                                                                                                                   | Kinek                         |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| **OQ-01** | Van érvényes EESZT fejlesztői regisztrációnk? Ha nincs, a 2026-09-30-i ISO-határidő teljesíthető-e?                                                                                                                                      | Ügyvezetés / RA               |
| **OQ-02** | A PREPARE „12-gene panel" és a PGx-Passport 14-génes listája közti eltérés pontosan mi? Primer forrás: Lancet 2023;401:347–356 supplementary + van der Wouden CPT 2019                                                                   | Klinikai szakértő             |
| **OQ-03** | Melyik partnerlabor vállalja az L3 aláírói felelősségét, és milyen áron? Ez a NG-01 architektúra alapfeltétele                                                                                                                           | Üzletfejlesztés               |
| **OQ-04** | A Magyar Genom Program / BBMRI Magyar Csomópont federált adatmegosztási projektje partner vagy versenytárs? A hungen.hu tartalma nem datált; a legfrissebb megerősített adatpont a 2025. áprilisi NKFIH-rendezvény                       | Ügyvezetés                    |
| **OQ-05** | Jogi állásfoglalás: „nem-MDSW riport-előállító eszköz" pozíció védhető-e az MDCG 2019-11 Rev.1 alatt, ha a kimenet gyógyszerajánlást tartalmaz — akkor is, ha az aláíró a labor orvosa? **Ez a legnagyobb egyetlen kockázat a specben.** | Külső jogi tanácsadó (nem én) |
| **OQ-06** | ISO 13485 tanúsító és Notified Body kiválasztása — a magyar/EU NB-kapacitás jelenlegi átfutása?                                                                                                                                          | RA                            |

### Nem-blokkoló (implementáció közben rendezhető)

| ID        | Kérdés                                                                                                                                       | Kinek                  |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **OQ-10** | PRS-beszállító: Allelica vagy alternatíva? Árazás és EU-adatlokalizáció?                                                                     | Üzletfejlesztés, F4-ig |
| **OQ-11** | A hazai gyógyszertörzs (OGYÉI) gépi elérhetősége és licence az ATC-mappeléshez?                                                              | Engineering            |
| **OQ-12** | Genomics Reporting IG STU3 → STU4 migráció időzítése?                                                                                        | Engineering            |
| **OQ-13** | A beteg-példány riport (FR-540) jogilag kiadható-e a 2008/XXI. tv. tanácsadási kötelezettsége mellett anélkül, hogy tanácsadásnak minősülne? | Jogi                   |
| **OQ-14** | Magyar klinikai ajánlás-fordítás: ki a felelős szakmai lektor?                                                                               | Klinikai szakértő      |

**Amire nem kérdés kell, hanem döntés:** hogy a v1 tényleg nem tartalmaz aktív, felírás-pillanatú riasztást. Ha igen, akkor az MDSW, és a teljes §11 timeline érvénytelen.

---

## 11. Timeline és fázisolás

### Kemény határidők

| Dátum          | Esemény                                             | Forrás               |
| -------------- | --------------------------------------------------- | -------------------- |
| **2026-09-30** | EESZT fejlesztői ISO-tanúsítás határideje           | e-egeszsegugy.gov.hu |
| **2027-12-02** | AI Act Annex III magas kockázatú kötelezettségek    | Digital Omnibus      |
| **2028-08-02** | **AI Act Annex I** — ez a mi óránk                  | Digital Omnibus      |
| **2029-03-26** | EHDS másodlagos felhasználás (nem-genetikai)        | (EU) 2025/327        |
| **2031-03-26** | EHDS másodlagos felhasználás — humán genetikai adat | (EU) 2025/327        |

### Fázisok

| Fázis  | Idő      | Tartalom                                                                                                                       | Kimenet                                           | MDR                            |
| ------ | -------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------- | ------------------------------ |
| **F0** | 0–3 hó   | EESZT jogállás rendezése, OQ-01/03/05 megválaszolása, partnerlabor-szerződés, gold set v0 (60 szintetikus eset)                | Jogi tisztánlátás + 1 aláírt LOI                  | —                              |
| **F1** | 3–9 hó   | L0–L3 + passzív L4 riport. FR-100/110/120/130, 200/210/220/240, 250, 300/310, 400/410/420, 500, 600/610/700/710                | Fizető labor-partner, bevétel                     | Nem MDSW (REG-010 indoklással) |
| **F2** | 6–18 hó  | In-house implementáció egyetemi partnernél; aktív CDSS (FR-520/530) in-house kivétellel; ISO 13485 + IEC 62304 + ISO 14971 QMS | Case study + 3 referencia → **MKIK-akkreditáció** | In-house kivétel (REG-011)     |
| **F3** | 18–36 hó | IIa CE-jelölés az L4-re; AI Act Art. 9–15/17/72 integrálva a technikai fájlba                                                  | CE-jelölt CDSS                                    | **IIa**                        |
| **F4** | 36+ hó   | L5 PRS beszállítói integrációval; EESZT-modul; EHDS-készültség                                                                 | Enterprise-képes platform                         | IIa                            |

**Kritikus út:** OQ-05 (jogi állásfoglalás) → F1 hatókör. Ha a válasz az, hogy a gyógyszerajánlást tartalmazó riport is MDSW, akkor F1 összeomlik F3-ba, és a timeline 18 hónapról 36-ra nő. **Ezt a kérdést az első két hétben kell feltenni, nem a hatodik hónapban.**

### Kompetencia-igény (SFIA-leképezés)

| Szerep                            | SFIA szint            | Miért ez a szint                                           |
| --------------------------------- | --------------------- | ---------------------------------------------------------- |
| Solution Architect                | **L5**                | Több szabályozási domain egyidejű architekturális kezelése |
| Regulatory Affairs / QA           | **L5**                | ISO 13485 Management Representative, MDR technikai fájl    |
| PRRC (MDR Art. 15)                | Jogszabályi képesítés | Nem SFIA-kérdés; nem korlátlanul outsourcelhető            |
| Senior Backend Engineer           | **L4**                | IEC 62304 Class B szoftver-életciklus                      |
| QA / Test Engineer                | **L4**                | Gold set, IAA, regressziós kapu                            |
| Klinikai farmakológus / genetikus | Szakvizsga            | Ground truth annotáció, szakmai lektorálás                 |

Ezek közül **egyik sem opcionális**. A6 feltevés (2–3 fejlesztő + 1 QA/RA + 1 klinikai részidős) a minimum, nem a komfortos.

---

## 12. Traceability matrix (váz)

A P01 gate-en kitöltendő. Minden sor: követelmény → forrás → teszt → MDR technikai fájl szakasz.

| Req ID | Forrás                                                        | Teszteset           | MDR/AI Act szakasz            |
| ------ | ------------------------------------------------------------- | ------------------- | ----------------------------- |
| FR-100 | 2008. évi XXI. tv. 8. §                                       | TC-CONSENT-001..004 | GSPR 14.1, technikai fájl 3.2 |
| FR-120 | 2008. évi XXI. tv. 26. § (1)                                  | TC-AUDIT-001..006   | GSPR 17.2                     |
| FR-210 | PharmCAT preprocessor dokumentáció + klinikai kockázatelemzés | TC-CALL-001..012    | ISO 14971 risk control RC-003 |
| FR-310 | van der Wouden, CPT 2019; PharmCAT changelog (F5 removal)     | TC-CONF-001..005    | IEC 62304 §6 change control   |
| FR-400 | CPIC / DPWG / FDA labels                                      | TC-RULE-001..040    | GSPR 17.1                     |
| FR-410 | Fenokonverzió-irodalom (§1)                                   | TC-PHENO-001..015   | Clinical evaluation §4        |
| FR-700 | MDCG 2025-6; AI Act Art. 6(1)                                 | TC-LLM-NEG-001..003 | AI Act Art. 9, 15             |
| FR-710 | 2008. évi XXI. tv. automatizált feldolgozás                   | TC-EXPLAIN-001..004 | AI Act Art. 13; GSPR 23       |

---

## 13. Parking lot

Jó ötletek, amelyek nincsenek hatókörben, de itt tároljuk, hogy ne szivárogjanak vissza:

- Onkológiai szomatikus panel-interpretáció (külön IVDR-domain)
- HLA-alapú hiperszenzitivitás-modul kiterjesztése (HLA-B*57:01, *15:02 túl)
- Magyar referencia-genom alapú allélfrekvencia-korrekció — **stratégiailag értékes**, de a Semmelweis referencia-genom projekt kimenetétől függ
- Gyógyszertári integráció (medication review a patikában — a PREPARE 28 közösségi gyógyszertárat vont be, tehát validált use case)
- Pharma-oldali kohorsz-toborzás genotípus alapján (EHDS 2031 után)
- Biztosítói prevenciós modul

---

## 14. Forrásjegyzék

Primer és hivatalos források. A `[V]` verifikált, `[R]` részben verifikált (egy forrás), `[C]` céges közlés.

**Szabályozás**

1. `[V]` 2008. évi XXI. törvény a humángenetikai adatok védelméről — njt.hu / net.jogtar.hu
2. `[V]` MDCG 2019-11 Rev.1 (2025-06-17), Guidance on Qualification and Classification of Software — health.ec.europa.eu
3. `[V]` MDCG 2025-6 / AIB 2025-1 (2025-06-19), Interplay between MDR/IVDR and AIA — health.ec.europa.eu
4. `[V]` Regulation (EU) 2025/327 (EHDS), OJ L 2025/327, 2025-03-05
5. `[V]` Digital Omnibus on AI — Council final approval 2026-06-29, EP endorsement 2026-06-16
6. `[V]` EESZT fejlesztői követelmények — e-egeszsegugy.gov.hu/fejlesztoknek; 39/2016. (XII. 21.) EMMI r.; 29/2022. (I. 31.) Korm. r.

**Klinikai evidencia**
7. `[V]` Swen JJ et al. Lancet 2023;401:347–356 (PREPARE) + kritikai levelek: Lancet 2023;401:1850–1851, 401:320–321
8. `[V]` van der Wouden CH et al. Clin Pharmacol Ther 2019;106:866–873 (PGx-Passport)
9. `[V]` Kullo IJ et al. Nat Rev Genet 2026;27:246–263 (PRS clinical use)
10. `[V]` eMERGE, Nat Med 2024, doi:10.1038/s41591-024-02796-z (10 PRS klinikai implementáció)
11. `[V]` Clinical implementation of PRS, Eur J Hum Genet 2025, doi:10.1038/s41431-025-01931-9 (ancestry túlbecslés)
12. `[V]` McDermott et al. Br J Clin Pharmacol 2025, doi:10.1002/bcp.70109 (NHS PGx)

**Technológia**
13. `[V]` PharmCAT — pharmcat.clinpgx.org, MPL 2.0; changelog (F5 removal)
14. `[V]` HL7 FHIR Genomics Reporting IG v3.0.0 (STU3) / v4.0.0-ballot — hl7.org/fhir/uv/genomics-reporting
15. `[V]` Dolin RH, Boxwala A, Shalaby J. Methods Inf Med 2018;57:e115–e123 (FHIR + CDS Hooks PGx service)
16. `[V]` Newsom KJ et al. Front Pharmacol 2024;15:1458095 (Epic Genomic Module)

**Piac**
17. `[V]` genetix.hu/arak — magyar árlista, lekérdezve 2026-08-09
18. `[R]` Precision Medicine Online, 2023-10-12 — Translational Software 510(k) bukás és megszűnés
19. `[V]` Nature Biotechnology 2025, doi:10.1038/s41587-025-02683-z (23andMe anatómia)
20. `[C]` Allelica sajtóközlemények 2026-03-16, 2026-04-07 — ISO 13485, ACC/AHA idézés, PROACT 3

---

## 15. Amit ez a spec nem tud

- **Nem ellenőriztem** a 2026-os ACC/AHA irányelv szövegét; a PRS-idézés céges PR-ból származik.
- **Nem találtam** publikus árat egyetlen PGx-CDSS szállítótól sem — mind „contact sales". Az árazási javaslatok analógián alapulnak, nem megfigyelt adaton.
- **Nem találtam** magyar vagy CEE-székhelyű PGx-CDSS versenytársat. Ez lehet valós rés, de lehet a keresés hiánya; céginformációs (TEÁOR 6201/7211) szűrés kellene a megerősítéshez.
- **Nem tudom** és nem is állítom, hogy az OQ-05 jogi kérdésre a válasz igen. A teljes F1 fázis ezen áll vagy dől.

---

*A dokumentum a P00 gate kimenete. A P01 (source coverage audit) és a P02 (independent build-readiness review) még nem futott le.*
