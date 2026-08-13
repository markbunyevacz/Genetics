# Precision Clinical Engine (PCE) — Termékspecifikáció és követelménylista

| | |
| --- | --- |
| **Dokumentum-ID** | PCE-SPEC-v1.2 |
| **Státusz** | **v1.2 FAGYASZTVA** — spec-írás lezárva a külső OQ-kig; F1+ mag fejleszthető (§10.2) |
| **Dátum** | 2026-08-12 |
| **Hatókör** | PGx platform, magyar/EU piac; F1+ statikus lelet + F1s shadow HITL + F2/F3 CDSS |
| **Előző** | PCE-SPEC-v1.1 — F1 passzív L4 + élő fenokonverzió a leleten; v1.2 ezt szűkíti |
| **Mellékletek** | [A](A-intended-purpose-and-modules.md) · [B](B-architecture-and-interfaces.md) · [C](C-eeszt-f0-checklist.md) · [D](D-risk-and-traceability.md) · [E](E-shadow-hitl.md) · [F](F-decision-package.md) · [Outbound](Outbound/README.md) · [Sales](Sales/README.md) |
| **Következő gate** | Párhuzamos: (1) F.6 külső aláírás · (2) F1+ mag fejlesztés §10.2 szerint |

Jelölések: `[V]` primerben verifikált · `[R]` egy forrás · `[C]` céges közlés · `[CORRECTED]` a v1.0-hoz képest javítva · `[ASSUMPTION]` · `[NEEDS VERIFICATION]`.

---

## 0. Hatóköri feltevések (explicit, nem validált)

Kérdés helyett rögzítve. Ha bármelyik hamis, a jelzett szakasz újraírandó. Owner / Validation / Due az Outbound + F.6 útvonalból; természetes személy **nincs kitalálva**.

| # | Feltevés | Owner | Validation | Due | Ha hamis, érintett szakasz |
| --- | --- | --- | --- | --- | --- |
| A1 | A v1 klinikai termék **F1+**: statikus, verziózott guideline-társítás aláírt laborleleten. Az élő CDSS (F2/F3) CE/in-house után. A nem-MDSW státusz **OQ-05-től függ**. Az F2/F3 kimenet F1 köntösben **tilos** (NG-07). | Counsel (OQ-05) | OQ-05 pecsét | v1 klinikai release előtt | §3, §6, §11, A, E |
| A2 | Nincs saját ISO 15189 / CLIA labor; a genotípus-hívás **partnerlabor felelőssége**. Az F1 default útvonal: **outside-call** (FR-240), nem nyers VCF→allélhívás. | Üzlet + partnerlabor (OQ-03) | OQ-03 / REG-020 | Első partner előtt | FR-240, FR-300, REG-020, A melléklet L3 |
| A3 | Nincs jelenleg érvényes EESZT fejlesztői regisztráció. | `eeszt_iso_owner` (OQ-01) | OQ-01; C melléklet | ISO 9001 kapu: **2026-09-30** | §11, REG-040a, C melléklet |
| A4 | A PRS-motor **nem** saját fejlesztés, hanem beszállítói integráció (F4). | Üzlet (OQ-10) | OQ-10 | F4 | §6.5, NG-02, FR-430 |
| A5 | Első aktív-CDSS referencia egyetemi/klinikai partnernél, in-house kivétellel (F2). | Intézményi RA (REG-011) | F2 szerződés | F2 indulás | REG-011, §11 F2 |
| A6 | Csapatméret v1-re: 2–3 fejlesztő + 1 QA/RA + 1 klinikai szakértő (részidős). Minimum, nem komfortos. | Ügyvezetés | Belső (F.4/F.5) | v1 | §11 |
| A7 | Elsődleges UI-nyelv magyar; a klinikai ajánlás-szöveg HU, ha szakmai lektor van, különben az angol eredeti. | Klinikai szakértő (OQ-14) | OQ-14 | FR-610 lektor | FR-610 |
| A8 | EESZT-útvonal F1-ben: **modul** az engedélyezett medikai rendszerben, nem saját EESZT-csatlakozás (NG-05). A 2026-09-30 ISO 9001 akkor is F0, ha a vevő a vendor. | `eeszt_iso_owner` | C melléklet; OQ-01 | **2026-09-30** | REG-040a, C melléklet |
| A9 | A gyártó a `genetics` repo tulajdonos szervezete. **Név ebben a dokumentumban nincs kitalálva.** | Ügyvezetés | Küldéskor, Outbound | Küldéskor | Fejléc, REG-031 |
| A10 | `[ASSUMPTION]` A **klinikai** hozzájárulás-visszavonás kaszkádjának üzemi SLA-ja **72 óra** (FR-110). A 2008/XXI. 26. § (1) határidőt nem ad. A GDPR Art. 12(3) a kérelemre **válasz** határideje (egy hónap, +2 összetett esetben). Az A10 ennél szigorúbb. **Nem** a shadow store alapértelmezett TTL-je. Visszavonáskor a álnevesített HITL-rekord: törlés **vagy** irreverzibilis anonimizálás 72 h-n belül. | DPO + klinikai ops (OQ-16 C1) | OQ-16 C1; Irish DPC Case Studies 2025 Case Study 12 (Art. 12(3) egy hónap). EUR-Lex primer letöltése **hátravan**. | v1 előtt (FR-110) | FR-110; E.5.1 |
| A11 | A v1.2 kanonikus szabályozási stratégia a **legális hibrid** (A.0–A.2): F1+ statikus lelet; F1s shadow HITL a kezelőorvos nélkül; F2/F3 csak minősítés után. | Counsel + RA (OQ-05) | OQ-05 | v1 előtt | A, E, FR-440–470 |
| A12 | Shadow default: **irreverzibilis anonimizálás** a intézményi gatewayen. Álnevesítés + FR-115 csak ha longitudinális követés kell. | DPO (OQ-16 A1) | OQ-16 A1 | F1s HIS előtt | E.5, FR-460 |
| A13 | `[ASSUMPTION]` A gateway ritka gén–gyógyszer kombinációt elnyom (FR-461) vagy az álnevesített utat választják (re-ID). | DPO (OQ-16) | OQ-16; WP29 05/2014 (k-anonimitás *technika*, nem küszöb); EDPB 01/2025 (álnevesített adat személyes adat marad, Rec. 26) | F1s HIS előtt | E.3.1, OQ-16 |
| A14 | `[ASSUMPTION]` **7 karakteres kód validálva 2026-08-13 (D-38, §10.2 (c)).** Default hatóanyag-kód: WHO ATC **5. szint, 7 karakter** (pl. N06AB05 paroxetin, N06AB10 eszcitaloprám). A 5 karakteres csoportkód (4. szint, pl. N06AB) a párosításhoz **nem elég**. Ritka diplotípus küszöb **0,5%** és k-anonymity **k ≥ 5** intézményi cellán: **nem** a DPIA-ból jön (a DPIA nem létezik → körkörös). Külső horgony: WP29 05/2014 (k-anonimitás: legalább k másik; a nagyobb k erősebb, **k=5 nincs előírva**); EDPB 01/2025 (álnevesítés ≠ anonimitás). A számokat a DPO választja (OQ-16 III.B1–B4). A DPO **durvíthat** (ATC4 / ATC3 / nagyobb k) — akkor a gén–hatóanyag párosítás **szünetel**. A 7 karakteres kód **nem** azt jelenti, hogy egy szer azonosítja a beteget. | DPO (OQ-16 III.B1–B4) | D-38 (7 karakter) **DONE**; B1/B3 pecsét **nyitott** | OQ-16 pecsét / F1s HIS előtt | FR-461; OQ-16 |
| A15 | A shadow/HITL validációs esetek megőrzése a **klinikai értékelési / vizsgálati protokoll** szerint (hónapok–évek, havi HITL). Feltétel: a rekord **már anonim** (OQ-16/A12) **vagy** van érvényes FR-115. **Nem** 72 órás puffer. | RA + DPO (OQ-15, OQ-16 C2) | OQ-15; OQ-16 C2 | F1s protokoll | E.5.1; FR-440 |

**Nem feltevés, hanem verifikált korlát:** a hazai jogi és EESZT-korlátok (§4) nem tárgyalhatók terméktervezéssel.

### 0.1 A10 vs A15 — változáskezelés (nem keverendő)

| | A10 | A15 |
| --- | --- | --- |
| **Mi** | Hozzájárulás-**visszavonás** kaszkád SLA | HITL/shadow **megőrzés** a protokoll alatt |
| **Mikor** | A beteg (klinikai 8. § és/vagy FR-115) visszavon | Amíg a protokoll és a jogalap él |
| **Mit csinál a rendszer 72 h-n belül** | Klinikai genetikai tartalom megsemmisítése (26. §). Álnevesített HITL-sor: **törlés** *vagy* irreverzibilis anonimizálás (kulcs az intézménynél törlődik; PCE-nél nincs re-ID). | Semmit a 72 h miatt. A rekord marad, ha anonim (OQ-16) vagy FR-115 érvényes. |
| **Mit nem** | Nem a HITL tár alapértelmezett élettartama. Nem „minden shadow 72 h után elvész”. | Nem mentesít a visszavonási kaszkád alól. |

VC-12: az „A10 = 72 órás shadow-puffer” olvasat **hibás**. A havi review A15-öt igényel.

---

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

A v1 **fizető** termék a **PCE rendszer** (klinika/intézmény licenceli). A white-label lelet az F1+ *modul*, nem a SKU. A fenokonverzió F1s-ben mérhető, F2/F3-on él — a kód a dobozban van, a felírói kimenet flag mögött (G5, FR-470). Az „F2 képesség F1 minőségben, mert az orvos dönt” **elutasítva** (A.0, NG-07): bent van ≠ be van kapcsolva.

---

## 2. Goals

Outcome-ok, nem output-ok.

| ID | Goal | Célérték | Mérés |
| --- | --- | --- | --- |
| **G1** | A partnerlabor PGx-riport előállítási ideje csökkenjen | Kézi/félautomata baseline → **p95 < 10 perc** outside-call-tól vagy VCF-től aláírásra kész riportig | Pipeline-telemetria, `ingest→report_ready` |
| **G2** | Az actionable találatok ne vesszenek el | A **PREPARE 12-génes** panel + aktuális CPIC/DPWG szerint actionable gén–gyógyszer párok **100%-a** megjelenik, 0 silent drop | Gold set (§9), minden release |
| **G3** | Fenokonverzió-motor készen áll az F2-re | **pheno-gold-v0**-n **≥ 90% recall**; a **aláírt F1+ leleten 0** élő fenokonverzió-alkalmazás. **Nem** a CureMD Top-5 83,10% (S028, VC-13). **Nem** a vcf-gold és **nem** az f1plus-gold. N=32 SYN: a 90% pontbecslés N<100 mellett széles CI — partnerlabor-eset nélkül nem populációs paraméter. | Gold set §9.1 pheno-gold; FR-470 CI |
| **G4** | Bevétel a szabályozott réteg előtt | **≥ 3 fizető rendszerlicenc** (klinika / intézmény / HIS-vendor) | Aláírt SKU-P/H |
| **G5** | A v2 (IIa) útvonal ne igényeljen újraírást | QMS + ugyanaz a L4-live motor shadowban, mint F3-on; klinikai UI-kapcsoló külön | REG-030; FR-470 flag |
| **G6** | Nincs szabályozási bypass | 0 shadow/CDSS inferencia a klinikai pathen F1+ buildben | FR-470 CI |

**Üzleti goal, amit nem a termék teljesít:** az MKIK-akkreditációhoz szükséges referenciák. G4 ezt szolgálja.

### 2.1 Success metrics (write-spec)

**Leading (napok–hetek):**

| Metrika | Success | Stretch | Módszer | Ablak |
| --- | --- | --- | --- | --- |
| Riport p95 átfutás | < 10 min | < 5 min | telemetria | első 30 nap / partner |
| Callability false-NORMAL | **0** | 0 | gold set FR-210 | minden release |
| Unsourced claim | **0** | 0 | CI `unsourced_claims` | minden release |
| Fenokonverzió recall (shadow) | ≥ 90% | ≥ 95% | **pheno-gold-v0** FR-410-LIVE | minden release |
| Shadow szivárgás a leletre | **0** | 0 | FR-470 CI | minden release |

**Lagging (hónapok):**

| Metrika | Success | Stretch | Módszer |
| --- | --- | --- | --- |
| Fizető rendszerlicenc (SKU-P/H) | ≥ 3 | ≥ 5 | szerződés |
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
| **NG-07** | F2/F3 élő kimenet F1 intended purpose alatt („az orvos dönt” / disclaimer-kiskapu) | MDR Rule 11a; nincs FDA enforcement discretion. A.0. |
| **NG-08** | Shadow/HITL inferencia megjelenítése a kezelőorvos ellátási UI-ján | Az A.1 rendeltetést hamissá tenné; azonnal F2. |

---

## 4. Kötelező korlátok (verifikált, nem tárgyalható)

### 4.1 EU MDR / MDSW

- **MDCG 2019-11 Rev.1** (2025-06-17) `[V]`: a szoftvert a **intended purpose** alapján kell minősíteni; a prognózis/predikció a Rule 11 hatókörébe esik; **minden modult önállóan** kell minősíteni, a modulok közti függőségeket dokumentálni.
- Rule **11a**: információ diagnosztikai vagy terápiás döntéshez → **IIa**, kivéve ha a döntés halált / irreverzibilis romlást (III) vagy súlyos romlást / sebészi beavatkozást (IIb) okozhat.
- `[CORRECTED]` Az IMDRF-leképező tábla **nem** tartalmazza a Class I-et; ez **nem** jelenti, hogy Class I MDSW ne létezne. Rule **11c** („all other software”) Class I; a Rev.1 Annex IV új Class I példát adott. PGx-ajánlást / terápiás információt adó kimenet **11a → IIa default**.
- Az „a végső döntést az orvos hozza” érvelés az FDA 2022 CDS guidance logikája, az MDR-ben **nem** minősít ki. **NG-07.**

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

6. Felíró klinikusként a felírás pillanatában akarok figyelmeztetést, ha a beteg genotípusa a tervezett gyógyszerrel ütközik — nem külön portálon. *(F2/F3; F1+-ban tilos — NG-07)*
7. Felíró klinikusként F2-n konkrét, forrásolt alternatívát akarok látni, nem csak tiltást.
8. Felíró klinikusként el akarom tudni utasítani a figyelmeztetést indoklással, hogy a rendszer ne blokkolja a megítélésemet.
9. Felíró klinikusként a hivatkozást (CPIC/DPWG/FDA) akarom látni.
10. Felíró klinikusként nem akarok riasztást nem-actionable párra.

**P3 — Klinikai farmakológus**

11. Klinikai farmakológusként a HITL/F2 felületen a beteg aktuális gyógyszerlistája alapján akarom látni a fenokonverziót. *(F1+ leleten csak FR-410-EDU)*
12. Klinikai farmakológusként F2-n egy oldalon akarom látni a genotípust, a DDI-t és a szervfunkciós módosítókat.

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

Rétegek: L0 Identity & Consent · L1 Ingestion · L2 Normalization · L3 Genotype→Phenotype · L4 Knowledge & Rules · L5 PRS · L6 Delivery · L7 Observability. Minősítés: [A](A-intended-purpose-and-modules.md). Interfészek: [B](B-architecture-and-interfaces.md). Shadow/HITL: [E](E-shadow-hitl.md). Tesztek: [D](D-risk-and-traceability.md).

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
- [ ] Given hozzájárulás-visszavonás, When rögzítésre kerül, Then a rendszer kaszkádolva töröl minden érintett genetikai adatot és nyilvántartási bejegyzést, és visszavonhatatlan törlési tanúsítványt állít ki. Az üzemi cél: **72 órán belül** `[ASSUMPTION]` A10. A 2008/XXI. 26. § (1) nem ad határidőt; a GDPR Art. 12(3) szerint a törlési kérelemre legkésőbb egy hónapon belül kell **reagálni** (összetett esetben +2 hónap, értesítéssel az első hónapon belül). Az A10 72 órás SLA ennél szigorúbb. Forrás: Irish DPC Case Studies 2025, Case Study 12 (lekérdezve 2026-08-13, pin: `Sources/official/ie-dpc-case-studies-2025.pdf`). EUR-Lex (EU) 2016/679 primer letöltése **hátravan**.
- [ ] A kaszkád **derived** adatra is kiterjed: diplotípus, fenotípus, riportok, cache, PRS-eredmény (ha van).
- [ ] **HITL/shadow (A10 vs A15):** álnevesített rekord 72 h-n belül vagy (a) törlődik, vagy (b) irreverzibilisen anonimizálódik (nincs kulcs a PCE-nél, intézményi kulcs megsemmisül). Már anonim HITL-sor (nincs join-key): a klinikai tenancy törlése a 26. § tárgya; a HITL-sor a DPIA szerint maradhat A15 alatt. Nem „minden shadow 72 h TTL”.
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

#### FR-115 · Kutatási / shadow hozzájárulás (álnevesített út) — **Compliance P0 ha A12 ≠ anonim**

Külön a 6. § (2)/8. § klinikai kaputól. Sablon: E.6.

- [ ] Given álnevesített shadow-út, When nincs `research_consent` a case-hez, Then a gateway **nem** küld csomagot a PCE shadow store-ba (`E-CONSENT-006`).
- [ ] Given anonim út (A12 default) és a DPIA szerint a kimenet nem személyes adat, When shadow fut, Then FR-115 nem blokkol — a klinikai FR-100 továbbra is igen.
- [ ] A kutatási hozzájárulás visszavonása: álnevesített HITL-rekord 72 h-n belül törlődik **vagy** irreverzibilisen anonimizálódik (A10); A15 nem tartja meg álnevesített, visszavont sort.

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

#### FR-220 · Klinikai kontextus (gyógyszerlista, labor) — **P0 a shadow/F2 pathen**; F1+ leleten **nem L4-bemenet**

Az F1+ aláírt lelet **nem** párosítja a aktuális gyógyszerlistát a diplotípushoz (A.1). A lista a **F1s/F2** L4-live inputja.

- [ ] **P0 F1s/F2** Kézi vagy FHIR gyógyszerlista (ATC / OGYÉI) + opcionális eGFR, ALT/AST/bilirubin.
- [ ] **P0 F1+** A Report `medications_applied_to_recommendations: false`.
- [ ] **P0 F1s** Given nincs gyógyszerlista a shadowban, Then `clinical_context = ABSENT` a HITL kártyán, nem hallgatólagos NM.
- [ ] **P1** FHIR R4 `Observation` / `MedicationRequest` a gatewayen (E.3).
- [ ] Given F1+ riport és a case-hez van gyógyszerlista, When PDF/JSON készül, Then **nincs** `functional_phenotype` és nincs ATC-szűrt riasztás (FR-470).

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

> L4 **két üzemmód**. L4-static = F1+ klinikai kimenet. L4-live = F1s shadow vagy F2/F3. Keverésük a klinikai UI-n = NG-07.

#### FR-400-STATIC · Gén → verziózott guideline-szöveg — **Product P0 (F1+)**

- [ ] CPIC, ClinPGx-annotált DPWG és FDA-címke **szövegkivonat** a meghívott **génhez**, diplotípus/fenotípus-kategória szerint, ahogy a publikált táblázatban szerepel.
- [ ] A társítás **nem** a HIS-ben éppen felírt gyógyszerhez kötött riasztás.
- [ ] Given a génhez a guideline-ban N gyógyszer/osztály-sor van, When F1+ riport, Then **mind az N sor** megjelenik — **nincs** szűrés a beteg `MedicationEntry` listájára (A.1.2).
- [ ] Given azonos génre eltérő CPIC és DPWG, When riport, Then **mindkettő** forrásmegjelöléssel; nincs szintetizált harmadik ajánlás.
- [ ] Minden kivonat: forrás, verzió, evidencia-szint, URL.
- [ ] `assert unsourced_claims == 0`.
- [ ] Nincs `dose_mg`, nincs „csökkentsd 50%-kal ennél a betegnél”.
- [ ] Negatív teszt: a report-renderer nem kap `MedicationEntry`-t argumentumként.

#### FR-400-LIVE · Beteg–gyógyszer párosítás — **P0 shadow / P0 F2** ; **tilos F1+ leleten**

- [ ] Diplotípus + aktuális `MedicationEntry` → actionable finding lista.
- [ ] F1s: csak HITL store (FR-440). F2: CDS Card (FR-520).
- [ ] Negatív teszt F1+ build: a report-renderer nem hívja FR-400-LIVE-ot.

#### FR-410-EDU · Fenokonverzió oktató szöveg — **Product P0 (F1+)**

OQ-05 counsel-csomag része (A.1.2). **Nem** zárja le az OQ-05-öt.

- [ ] A lelet tartalmazhat **általános**, verziózott bekezdést: mely inhibitor/induktor *osztályok* a szakirodalom/guideline szerint módosíthatják a funkcionális fenotípust.
- [ ] A bekezdés **nem** állítja, hogy *ez a beteg* jelenleg fenokonvertált, és **nem** olvassa a `MedicationEntry` listát.
- [ ] **Ha–akkor tiltás:** nincs olyan mondat, amely a beteg konkrét gyógyszerét a génjéhez köti (pl. „mivel Ön X-et kap, váltson Y-ra”).
- [ ] **Tankönyvi forma:** statikus enciklopédia-kivonat; kötelező guideline-azonosító + verzió + URL. Példa-szerkezet: „A CPIC v[n] szerint a CYP2D6 ultragyors metabolizáló *kategóriában* a [gyógyszercsoport] alkalmazásakor [publikált stratégia]. Részletes útmutató: [URL].”
- [ ] **Kombinációs tilalom:** az F1+ renderer nem futtat olyan függvényt, amelynek bemenete egyszerre diplotípus **és** a case gyógyszerlistája. CI call-graph.
- [ ] Gold set: ≥ 5 tiltott „ha–akkor” minta → a renderer elutasítja / nem generálja.

#### FR-410-LIVE · Fenokonverzió-alkalmazás — **Product P0 (F1s/F2)** ; **tilos F1+ leleten**

A tudományos differenciátor. G3 a shadow gold seten.

- [ ] Aktuális gyógyszerlista → `functional_phenotype` a `genotype_phenotype` **mellett**, soha nem fölötte.
- [ ] Given CYP2D6 NM + erős CYP2D6-inhibitor (paroxetin, fluoxetin), When shadow/F2, Then `genotype_phenotype = NM`, `functional_phenotype = PM` vagy `IM` a tábla szerint.
- [ ] Nincs `dose_mg` a v1 shadowban (stratégia-kategória megengedett: pl. `CONSIDER_ALTERNATIVE`).
- [ ] Given hiányzó gyógyszerlista a shadowban, Then `clinical_context = ABSENT`, nem hallgatólagos NM.
- [ ] Szervfunkció (eGFR < 30 stb.): `reason: organ` flag, nem számított dózis.

#### FR-420 · Kiemelés — **Product P0 F1+-ban guideline-struktúra** / **F2-n alert**

- [ ] **F1+:** a lelet génenként / guideline-táblázat szerint tagolt; `CRITICAL` **nem** jelenti „most cseréld a felírt szert”.
- [ ] **F2:** csak actionable pár a interruptive cardon; nem-actionable függelék.
- [ ] Given 40 gén–gyógyszer pár az F2 motorban, When Card, Then a `CRITICAL`+`WARNING` a card címe, részlet a linkben.

#### FR-430 · PRS interfész — **P2** (nem épül)

- [ ] Interfész definiált: `POST /prs/score` → `{score, percentile, absolute_risk, ancestry_calibration, provider, model_version}` — stub, nincs implementáció.
- [ ] Beszállítói minimum: ISO 13485, dokumentált ancestry-kalibráció, eMERGE-típusú klinikai pipeline.
- [ ] Indoklás: Kullo et al., Nat Rev Genet 2026;27:246–263 `[V]`; portabilitási / túlbecslési irodalom. Magyar referencia-genom hiányában saját modell nem kalibrálható.

#### FR-440 · Shadow CDSS futtatás — **Product P0 (F1s)**

- [ ] HIS/LIS esemény (lelet aláírás vagy recept lezárás) → aszinkron feldolgozás; a HIS **nem** vár a válaszra.
- [ ] A motor FR-400-LIVE + FR-410-LIVE kimenete csak a HITL store-ba íródik.
- [ ] A kimenet tartalmazza a `config_id` / guideline-verziókat (reprodukálhatóság).

#### FR-450 · HITL review UI — **Product P0 (F1s)**

- [ ] Szerep `hitl_reviewer` elválasztva a felíró `clinician` tenancytől (E.4).
- [ ] Kártya (anonim út): opák `case_display_id` (pl. `A87F3`); gén; coarsened diplotípus/fenotípus-osztály; **hatóanyag-kód** (WHO ATC 5. szint, 7 karakter; ha a DPO durvított, csoportkód + párosítás szünetel); guideline-verzió. **Nincs** név, TAJ, életkor, születési év, intézményi/osztály-azonosító, orvosnév. Motor-kategória: csak FR-450-BLIND 2. lépése után, vagy ha a vak mód ki van kapcsolva.
- [ ] Válasz: `AGREE` / `DISAGREE` / `INSUFFICIENT_DATA` + kötelező `reason_code`; szabad szöveg opcionális, PII-scanner a mentéskor.
- [ ] Nem a vizit alatt; batch vagy bizottság.
- [ ] **P1 (OQ-15 csomag):** vak mód (FR-450-BLIND, E.4.1) default **be** az első intézményi protokollban, amíg OQ-15 el nem dől.

#### FR-450-BLIND · Vak HITL (szekvenciális, reviewer-vak) — **P1 (F1s)**

**Nem** kettős vak (double-blind): a motor kimenete ismert a rendszernek; csak a reviewer nem látja az 1. lépésben.

- [ ] 1. lépés: a reviewer **nem** látja a motor tippjét; strukturált saját döntést rögzít (`CONTINUE` / `ALTERNATIVE` / `DOSE_CHANGE` / `INSUFFICIENT`).
- [ ] 2. lépés: a rendszer megmutatja a motor kategóriáját; a reviewer `AGREE`/`DISAGREE`.
- [ ] A két lépés időbélyege és a vak döntés immutábilis. Ez **nem** zárja le az OQ-15-öt.

#### FR-460 · Intézményi anonimizáló gateway — **Compliance P0 (F1s)**

- [ ] A gateway a kórház/labor zónájában fut; a PCE felhő **nem** kap TAJ/nevet (E.3).
- [ ] Anonim út: nincs re-ID kulcs a gyártónál. Álnevesített út: kulcs csak az adatkezelőnél + FR-115.
- [ ] FR-461 aggregáció **a továbbítás előtt** fut; a PCE shadow ingest TAJ-t / dózist / pontos timestampet / ritka nyers diplotípust `E-SHADOW-001` / `E-SHADOW-003` szerint elutasít. A **7 karakteres hatóanyag-kód default elfogadott** (D-38). Ha a DPO `max_atc_level < 5`, a finomabb kód `E-SHADOW-001`.

#### FR-461 · Re-ID kontroll (k-anonymity / aggregáció) — **Compliance P0 (F1s anonim út)**

OQ-16 technikai csomag. **Nem** zárja le az OQ-16-ot. Küszöbök: A14, a DPO felülírhatja.

- [ ] **Hatóanyag-kód (WHO ATC 5. szint, 7 karakter):** default **megtartva** (pl. N06AB05, N06AB10). A csoportkód (4. szint, 5 karakter, pl. N06AB) a párosításhoz elégtelen. A DPO durvíthat ATC4/ATC3-ra; akkor a gátló-állítás szünetel (R-020). INN/márkanév az ANON payloadban **nem** megy ki, csak a kód. A 7 karakteres kód **nem** betegazonosító.
- [ ] **Idő generalizáció:** `MedicationRequest.authoredOn` → naptári **negyedév** (pl. `2026-Q3`); nincs nap, óra, perc. `Patient.birthDate` a HITL kártyán nem jelenik meg.
- [ ] **Ritka diplotípus:** ha a konfigurált populációs gyakoriság < A14 küszöb **vagy** az intézményi (gén-osztály × ATC-szint) cella elemszáma a gördülő ablakban < `k`, Then a gateway vagy (a) fenotípus-*osztályt* küld diplotípus helyett (`REDUCED` / `INCREASED` / `UNCERTAIN`), vagy (b) a rekordot **kihagyja** (`E-SHADOW-003`, csak számláló log).
- [ ] Adagolási struktúra (doseQuantity) anonim pathen **nem** megy ki.
- [ ] Álnevesített út: FR-461 enyhíthető a DPIA szerint; FR-115 kötelező.
- [ ] **A14 monitor (DPO-feltétel, F.3):** a gateway `E-SHADOW-003` drop-arányt és a k-cella eloszlást aggregáltan (nem PII) jelenti a DPO-nak legalább negyedévente. A legritkább diplotípus-osztály default **drop**, akkor is, ha a G3 recall csökken (R-020). Nincs manuális override a k-küszöbre F1s anonim úton.

#### FR-470 · Csatorna-izoláció — **Compliance P0**

G6. E.8 invariánsok.

- [ ] F1+ Report/PDF/FHIR nem tartalmaz shadow mezőt.
- [ ] B.4.1 **zárt** top-level kulcskészlet (allow-list). Tiltott: `functional_phenotype`, `shadow_recommendation`, `dose_mg`, `live_findings`, `medications`, `medication_entries`, `MedicationEntry`, `medicationRequest`, `MedicationRequest`, `medicationStatement`, `clinical_context`, `hitl_review`, `hitl_verdict`, bármely `hitl_*`. Ismeretlen top-level kulcs = `RendererConfigError`.
- [ ] CI: `pce_report` forrásában nincs `medication_entry` / `MedicationEntry` folytonos sztring; a DELIVERY-PLAN R9 backtick-nevek ⊆ séma deny-list.
- [ ] `clinician` klinikai API-n `/shadow/**` és `/hitl/**` → 403/404.
- [ ] `LIVE_CDS` compile-time false az F1+ buildben.
- [ ] CI call-graph: report-renderer nem olvassa a shadow kimeneti táblát.
- [ ] `create_report` **nem** tölti a gyógyszerlista-táblát. A lista a klinikai store-ban maradhat (FR-220); a F1+ renderernek nincs `medications` argumentuma.

#### FR-480 · Enciklopédia-nézet — **P1**

- [ ] Az orvos génre / hatóanyagra keres; a rendszer verziózott CPIC/DPWG/FDA szöveget listáz.
- [ ] Given a HIS-ben nyitott `MedicationRequest`, When enciklopédia, Then **nincs** automatikus „ehhez a recepthez ez a riasztás” Card (az F2).
- [ ] A keresés naplózott, de nem döntéstámogató kimenet.

#### FR-490 · Intended purpose + nyilatkozat a leleten — **Compliance P0**

- [ ] Minden F1+ PDF/FHIR tartalmazza az A.1 mondatot és az A.1.1 sablont (counsel-véglegesítve).
- [ ] A nyilatkozat **nem** kapcsolja ki FR-100-at és **nem** minősít ki MDSW-ből.

---

### 6.6 L6 — Delivery

#### FR-500 · Riport-generálás — **Product P0**

- [ ] Kimenet: PDF (aláírásra kész), FHIR Bundle (Genomics Reporting IG), strukturált JSON.
- [ ] FHIR: IG **v3.0.0 STU3**, FHIR R4; mapping-réteg STU4-re (`GenomicStudy`, új operations) — szállít STU3-on.
- [ ] PDF minden oldalán: guideline-verziók, pipeline-verzió, callability-összefoglaló, aláíró orvos helye, **F1+ intended purpose** (A.1) + FR-490 nyilatkozat. F2 buildben a mondat az A.3 CDSS rendeltetés.
- [ ] Given white-label partner, When riport, Then partner arculata és aláírója; PCE a kolofonban mint technológiai szállító.

#### FR-510 · Riport-újragenerálás guideline-frissítéskor — **P1**

- [ ] Given új CPIC/DPWG verzió, When admin újraértékelést indít, Then a rendszer listázza azokat az eseteket, ahol az ajánlás **megváltozott**, riportonkénti deltával.
- [ ] Az eredeti riport immutábilis; új verzió jön létre.

#### FR-520 · CDS Hooks — **tilos F1+**; **Product P0 F2/F3**

- [ ] F1+ buildben a CDS endpoint nincs kitéve (FR-470).
- [ ] F2: `order-select` / `order-sign`; `Card` + `suggestion` + evidencia-`link`.
- [ ] Given a szolgáltatás > 2 s, Then a felírás **nem blokkolódik** (fail-open).
- [ ] Given nincs PGx-adat F2-n, When hook, Then explicit „nincs elérhető PGx-eredmény” card.

#### FR-530 · SMART on FHIR — **P1 F2**; F1+-ban csak enciklopédia (FR-480)

- [ ] F2: EHR-launch a felírási workflow-ban, interruptive CDSS a A.3 szerint.
- [ ] F1+: ha van SMART, az **csak** FR-480 (kereső), nem a nyitott recepthez párosított riasztás.
- [ ] A v1 labor-UI átmeneti.

#### FR-540 · Beteg-példány riport — **P1**

- [ ] Laikus nyelvű változat: genotípus-információ + „beszéljen kezelőorvosával”; **nincs** dózis- vagy terápiajavaslat.
- [ ] OQ-13: kiadható-e anélkül, hogy 6. § (4) szerinti tanácsadásnak minősülne — jogi, nem engineering.

---

### 6.7 L7 — Observability & Governance

#### FR-600 · Alert-fatigue és override telemetria — **P1**

F1+-ban nincs interruptive riasztás. Az override F2-n és a HITL `DISAGREE` F1s-en értelmes. P1 a séma.

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
- [ ] A v1 PGx-szabályút magyarázata **nem** SHAP / feature-attribution. SHAP csak P2 jelölt, *ha* később külön ML komponens kerül a rendszerbe (nem LLM — FR-700; nem v1 core). S028 módszertani analógia, nem FR. §9.5.

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
| **NFR-070a** | Kódminőség / 62304 — F1+ mag | Software safety class **B** a L0–L3, L4-static, L6-report útra (consent-kapu, statikus társítás, PDF/FHIR). Unit+integráció ≥ 80%, klinikai útvonal 100% | CI | P0 |
| **NFR-070b** | Kódminőség / 62304 — élő párosítás | Software safety class **C** **javaslat** (RA: OQ-06) az L4-live / F1s–F2–F3 útra a A.4.1 párokra, mert rossz élő ajánlásnál súlyos klinikai kár lehetséges (R-007 S=5). Amíg az RA nem választ, az F3 gyártói default **IIa** (A.3) **nem** zárja a Class C vs Rule 11a III kérdést. | OQ-06; coverage az L4-live-ra F1s-től | P0 F1s/F2 |
| **NFR-080** | DR | RPO ≤ 1 h, RTO ≤ 8 h; 30 éves nyilvántartás külön immutábilis archívumban | Éves DR-teszt | P0 |
| **NFR-090** | Skálázás | 10 000 eset/hó lineáris költség; PharmCAT izolált worker | Kapacitásteszt | P1 |

---

## 8. Szabályozási és compliance követelmények

| ID | Követelmény | Pri | Határidő |
| --- | --- | --- | --- |
| **REG-010** | Intended purpose írásban, modulonként, MDCG 2019-11 Rev.1 szerint. Három üzemmód: F1+ / F1s / F2–F3 — [A melléklet](A-intended-purpose-and-modules.md). Az F1+ nem-MDSW **indoklás**, nem tény, amíg OQ-05. | Compliance P0 | v1 előtt |
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
| **REG-090** | F1s shadow: clinical evaluation vs clinical investigation (MDR Art. 62) eldöntve **az első élő HIS-csatlakozás előtt**; protokoll + etikai út, ha vizsgálat | Compliance P0 | F1s előtt |
| **REG-091** | DPA: intézmény = adatkezelő, gyártó = feldolgozó a shadowra (hacsak counsel mást nem mond); DPIA kiterjesztve a shadowra | Compliance P0 | F1s előtt |

---

## 9. Validációs és teszt-stratégia

### 9.1 Gold set

Nélküle G2/G3 nem mérhető, a v2 dosszié nem védhető. **Három külön halmaz**, saját N-nel és ground truth-szal:

| Halmaz | N (jelen) | Ground truth | Mit mér | Küszöb |
| --- | --- | --- | --- | --- |
| **vcf-gold** | 3 SYN missing-to-ref (CYP2D6\*4, CYP2C19\*2, DPYD\*2A) | Ensembl/dbSNP pozíció (S050) | Callability / FR-210 | 100% INDETERMINATE, 0 hamis NM |
| **f1plus-gold** | PREPARE-12 CPIC pair/rec extract + GeT-RM tervezett 100 | CPIC API pin; CDC GeT-RM a 100-ra **még nincs** a repóban | Guideline-társítás (G2) | actionable recall **100%** a pin-elt táblán |
| **pheno-gold** | **32** SYN (`tests/fixtures/pheno-gold-v0/`) | FDA DDI 1-2 / 2-2, CPIC SSRI 2023, WHO ATC — pin 2026-08-13 | Fenokonverzió viselkedés (G3) | **≥90% csak itt**. Elvárt funkcionális fenotípus: **üres**, ha nincs hivatalos NM→szegény sor |

- **Kötelező edge** (szétosztva): hiányzó pozíció (vcf-gold), CYP2D6 SV, unphased ambiguitás, CPIC–DPWG ütközés, fenokonverzió (pheno-gold), `INDETERMINATE` + actionable gyógyszer, visszavont hozzájárulás, csonka VCF, F5 config-on/off.
- **60 szintetikus guideline-sor** az f1plus/szabálytáblából **nem** G3 nevező (körkörös recall).
- **Ground truth annotátor:** két független annotátor a partnerlabor-esetre (klinikai farmakológus + molekuláris genetikus); döntőbíró egyet nem értéskor. Cohen's κ **≥ 0,80**. A pheno-gold SYN N=32-n a G3 **pontbecslés**; N<100 mellett a 90% CI széles — partnerlabor-eset nélkül nem populációs paraméter.
- **Verzió:** DVC; minden release-hez rögzített gold set verzió.

### 9.2 Metrikák és küszöbök

| Mérés | Küszöb | Megjegyzés |
| --- | --- | --- |
| Diplotípus-egyezés referencia-anyagokon (outside-call echo / matcher) | **100%** | Determinisztikus |
| Actionable ajánlás recall (PREPARE 12 + aktuális CPIC/DPWG) | **100%** (0 FN) | G2 |
| Callability-jelölés | **100%** | FR-210 |
| Fenokonverzió recall | **≥ 90%** | G3. **Csak pheno-gold.** **Nem** S028 Top-5 accuracy 83,10%. |
| Fenokonverzió precision | **≥ 75%** | FP = „nézd meg” |
| Forrás nélküli állítás | **0** | FR-400 CI |

**G3 ≠ R-020 ≠ S028.** R-020 = ATC/diplotípus-csonkolás vs G3 a shadow gold seten. A CureMD Table 2 Top-5 **83,10%** más feladat (ICD-csoport, US primer ellátás), más metrika (Top-N accuracy). Nem küszöb, nem matematikai referencia. VC-13.

### 9.3 Regressziós kapu

- [ ] Minden guideline-verzió-váltás után a teljes gold set újrafut; delta-riport release-review tárgy.
- [ ] Given bármely metrika küszöb alatt, When release, Then CI blokkol. **Nincs** manuális override.

### 9.4 Klinikai evidencia a v2 dossziéhoz

**PREPARE** (Swen et al., Lancet 2023;401:347–356; NCT03093818) `[V]`: nyílt, multicentrikus, kontrollált, klaszter-randomizált crossover; 12-génes panel; 18 kórház, 9 közösségi egészségügyi központ, 28 közösségi gyógyszertár; 7 ország (AT, GR, IT, NL, SI, ES, UK) — **Magyarország nincs benne**. 50 germline variáns 12 génben a startnál. 41 696 alkalmasból **6944** enrollált (3342 genotípus-vezérelt, 3602 standard). 6495 (93,5%) enrolláltnál legalább egy actionable variáns; az index-gyógyszerre actionable DGI: **1558** (25,2% a második gatekeeping-elemzésben).

Elsődleges kimenet (12 hét): *klinikailag releváns* ADR = Liverpool causality definite/probable/**possible** **és** NCI-CTCAE **grade 2–5** (nem „súlyos” mint egyetlen címke). Actionable alcsoport: **152/725 (21,0%)** vs **231/833 (27,7%)**; OR **0,70** (95% CI 0,54–0,91); **p = 0,0075** (nem 0,0034). Teljes kezelt populáció: 628/2923 (21,5%) vs 934/3270 (28,6%); OR 0,70; p < 0,0001. A ~30% a **esélyhányados** csökkenése (1−0,70), nem abszolút kockázatcsökkenés (6,7 százalékpont az actionable karon).

**Forráskritika (kötelező a dossziéban):** a hatás elsősorban grade 2; open-label; a Lancet kritikai leveleket közölt (Curtis; Rogers et al.; Van der Linden; Peñas-LLedó & LLerena). A primer kimenet **nem** halálozás és **nem** ápolási nap. A vizsgálat DPWG-vezérelt felírást mért, **nem** a PCE szoftvert. A Notified Body ezt megtalálja. VC-14.

A 12 vs 14 eltérés **nem** nyitott kérdés: lásd FR-310.

### 9.5 Szomszédos CDSS-irodalom (nem PGx-SOTA, nem állami referencia)

**Nincs** „Klinikai háttér és állami referenciák” fejezet. Az a cím L1/L2 hatósági vagy PGx-SOTA forrásnak járna. Az alábbi preprint **L5**.

**S028** `[V]` a PDF-ből: Maqsood et al., CureMD Research, *A Hybrid AI and Rule-Based Decision Support System for Disease Diagnosis and Management Using Labs*, arXiv:2603.14876v1, 2026-03-16. Példány: [Sources/](Sources/CureMD-Hybrid-CDSS-arXiv-2603.14876v1.pdf). Formális jegyzet: [S028-note](Sources/S028-curemd-hybrid-cdss-note.md).

| A PDF állítása | Érték | PCE-használat |
| --- | --- | --- |
| Mintanagyság | **593 055** beteg, **547** US primary care | Nem PCE-kohorsz |
| Szabály + ML | 59 állapot; XGBoost 37 ICD-10 → 11 csoport | Analógia: hibrid CDSS létezik. Nem PGx-motor. |
| Top-N accuracy (teszt 20%) | Top-1 **31,18%**; Top-5 **83,10%**; Top-11 99,6% | **Tiltott** G3/R-020 küszöbnek |
| Szerzői olvasat | Top-5 ≈ 80% **trade-off**, nem „a modell 83%-ban helyes” | Ugyanígy tilos sales-RWE-ként |
| SHAP | Az *ő* XGBoostjukra (T2DM appendix) | Nem FR-710; P2 ha később ML komponens |
| Limitáció (szerzők) | Csak labor; nincs vital/anamnézis/tünet | Más intended purpose, mint a PCE |

**F1s klinikai értékelés SOTA-sora:** PREPARE (S008), PGx-Passport (S009), CPIC (S030), MDCG/MDR. S028 **irodalmi melléklet** lehet („hibrid szabály+ML CDSS labor-diagnosztikában”), **nem** Annex XIV SOTA, **nem** állami/hatósági hivatkozás.

**Sales:** a cikket **ne** csatold a licenchez PCE-RWE-ként. [literature-boundary](Sales/literature-boundary.md).

---

## 10. Open Questions

### Blokkoló (v1 indulás előtt)

| ID | Kérdés | Kinek | Státusz |
| --- | --- | --- | --- |
| **OQ-01** | Van érvényes EESZT fejlesztői regisztráció? A 4. melléklet 1.1–1.9 + 2.1 teljesíthető-e 2026-09-30-ig? | Ügyvezetés / RA | **ELŐTERJESZTVE** (F.4): owner szerep + audit azonnal. A regisztráció *ténye* nyitott → C melléklet |
| **OQ-02** | PREPARE 12 vs PGx-Passport 14 | Klinikai | **LEZÁRVA** (FR-310, VC-02) |
| **OQ-03** | Melyik partnerlabor vállalja az L3 aláírói felelősséget, milyen áron? | Üzletfejlesztés | **ELŐTERJESZTVE** (F.5). Tárgyalás indul; havidíj + volumensáv. Labor neve / aláírt szerződés nyitott. |
| **OQ-04** | Magyar Genom Program / BBMRI HU csomópont: partner vagy versenytárs? | Ügyvezetés | Nyitott; hungen.hu nem datált |
| **OQ-05** | Védhető-e az **A.1 F1+** nem-MDSW-ként? | **Külső counsel** | **ELŐTERJESZTVE** (F.1). Gyártói kérés: feltételes nem-MDSW a A.1.2 + FR-490 mellett. **Nem** counsel-aláírás. |
| **OQ-06** | **Osztály páronként** (A.4.1): Rule 11 IIa / IIb / III és IEC 62304 B / C a DPYD–fluoropirimidin, CYP2C19–clopidogrel, TPMT/NUDT15–tiopurin, CYP2D6–kodein, HLA-B\*15:02–karbamazepin párokra. **Nem** először „melyik Notified Body”. NB csak a választott osztály után. | RA | Nyitott; A.4.1 tábla a dosszié inputja |
| **OQ-15** | Shadow = Art. 62 vizsgálat vagy evaluation? | RA + intézmény | **ELŐTERJESZTVE** (F.2). Gyártói kérés: nem Art. 62, reviewer-vak evaluation. Függ OQ-16-tól. **Nem** RA-határozat. |
| **OQ-16** | Anonim shadow elég-e, vagy FR-115? | DPO | **ELŐTERJESZTVE** (F.3). Gyártói kérés: anonim default + A14 monitor/drop G3 rovására is. **Nem** DPIA. |

### Nem-blokkoló

| ID | Kérdés | Kinek |
| --- | --- | --- |
| **OQ-10** | PRS-beszállító (Allelica vagy más), árazás, EU-adatlokalizáció | Üzlet, F4-ig |
| **OQ-11** | OGYÉI/PHARMINDEX gépi elérés és licenc | Engineering |
| **OQ-12** | Genomics Reporting IG STU3 → STU4 időzítés | Engineering |
| **OQ-13** | FR-540 beteg-riport 6. § (4) tanácsadásnak minősül-e? | Jogi |
| **OQ-14** | Magyar klinikai ajánlás-fordítás szakmai lektora | Klinikai szakértő |
| **OQ-17** | US: ugyanazon bináris F2/F3 kimenete eszköz-e (510(k) / De Novo / 2022 CDS guidance), NG-01 mellett? Nem az OQ-05 átvitele. US pack F2/F3 default LOCK. | US counsel |

**Döntés, nem kérdés:** a v1 klinikai kimenet **nem** tartalmaz aktív, felírás-pillanatú riasztást, élő fenokonverzió-alkalmazást, és **nem** mutatja a shadowot a kezelőorvosnak. Ha mégis, az F2/MDSW, és az F1+ oszlop érvénytelen (NG-07/08).

**F1+ ≠ lezárt nem-MDSW.** Az A.1 pozíció *indoklás* OQ-05-ig. A FR-410-EDU szabályok a pozíciót *szűkítik*, nem igazolják.

### 10.1 v1 / F1s — külső állásfoglalás (a technikai csomag után)

A csomagok és a **gyártói kérés** a [F mellékletben](F-decision-package.md) vannak. A **küldhető iratok** az [Outbound](Outbound/README.md) mappában. A **klinikai / forgalmazási** mérföldkő **nem** indul a F.6 aláíró-sor nélkül. A **spec-írás** és a **F1+ mag kód** ettől elválik — §10.2.

| Ki | Mit dönt | Csomag, amit kap | Blokkolja |
| --- | --- | --- | --- |
| Külső counsel | OQ-05 | F.1 + A + [OQ-05 brief](Outbound/OQ-05-counsel-brief.md) | F1+ nem-MDSW forgalmazás |
| RA + intézmény | OQ-15 | F.2 + E.4.1 + [OQ-15 kérelem](Outbound/OQ-15-intezmenyi-ra-egyoldalas.md) | F1s HIS-csatlakozás |
| DPO | OQ-16 | F.3 + E.3.1 + [OQ-16 kérdőív](Outbound/OQ-16-dpo-dpia-kerdoiv.md) | Anonim vs FR-115 |
| Ügyvezetés / RA | OQ-01 | F.4 + C + [OQ-01 owner](Outbound/OQ-01-iso-eeszt-owner-csomag.md) | 2026-09-30 kapu |
| Üzlet | OQ-03 | F.5 + term sheet | Labor-**csatlakozó** (nem a mag-SKU) |
| US counsel | OQ-17 | [market-packs](Sales/market-packs.md) | US F2/F3 feloldás |

### 10.2 Spec-fagyasztás és fejlesztési start (2026-08-12)

**Döntés (D-18):** a v1.2 **követelmény- és iratíró szakasz lezárva**, amíg a külső állásfoglalások (F.6) meg nem érkeznek. A spec ettől a naptól **fagyasztott**: új FR/OQ/intended-purpose csak (a) beérkezett OQ-válasz, (b) P0 klinikai biztonsági hiba (pl. FR-210), vagy (c) explicit új felhasználói kérés esetén.

**2026-08-13 (D-38, §10.2 (c)):** A14 / FR-450 / FR-460 / FR-461 ATC-klauzula javítva: default **7 karakteres hatóanyag-kód**. A többi FR változatlan. Az OQ-16 pecsét ettől **nem** zárul.

Az OQ-05 / OQ-15 / OQ-16 / OQ-01 / OQ-03 / OQ-17 **nem** zárulnak le. ELŐTERJESZTVE / NYITOTT maradnak.

A fejlesztés **elindulhat** a lenti határon. „F.6 nélkül nem indul a mérföldkő” = nincs **éles betegadat, HIS-csatlakozás, nem-MDSW forgalmazás**. Nem azt jelenti, hogy a git üresen marad.

| Sáv | Indul most? | Tartalom | Vár F.6-ra? |
| --- | --- | --- | --- |
| **Spec / Outbound** | **Lezárva** (fagyasztva) | v1.2 + A–F + öt küldendő irat | Igen a *válaszra*; a *küldés* azonnal |
| **F1+ mag (kód)** | **Igen** | L0–L2, FR-240 outside-call, FR-210 callability, FR-310 PREPARE-12 config, FR-400-STATIC, FR-410-EDU, FR-490, FR-500 PDF/FHIR, FR-470 `LIVE_CDS=false`, FR-700 (nincs LLM a klinikai úton). Matcher **ki**. Gold set v0: missing-to-ref + tiltott EDU tokenek. | Nem a kódra. Igen a **nem-MDSW piaci** állításra (OQ-05). |
| **F1s kód fixture-ön** | **Igen, zárt** | FR-440/450/450-BLIND/460/461/410-LIVE **szintetikus** adatokon, külön store, külön IAM. Nincs éles HIS, nincs valódi betegrekord. | Igen az **éles** HIS-csatlakozásra (OQ-15 + OQ-16). |
| **ISO 9001 / Redmine** | **Igen** (F.4 BELSŐ IGEN) | C-000 tény, C-201 tanúsító; 2026-09-30 kapuőr | A tanúsítvány *ténye* nyitott; a folyamat nem vár counselre |
| **Labor LOI** | **Igen** (F.5 BELSŐ IGEN) | [OQ-03 term sheet](Outbound/OQ-03-l3-term-sheet.md) kitöltve, név nélkül a specben | Igen az aláírt REG-020-ra |
| **Értékesítés (G4)** | **Igen, hipotézisen** | [Sales/](Sales/README.md): **SKU-P rendszerlicenc** klinikának/kórháznak; F1–F3 egy bináris; HU/EU/US flag; F2/F3 LOCK amíg minősítés. Labor = csatlakozó, nem a termék. | Éles ON modul: piaci OQ (05/15/16/17). `LIVE_CDS=true` nem sales-flag. |
| **F2/F3 / `LIVE_CDS=true`** | **Nem** | Interruptive CDSS, élő fenokonverzió a klinikai UI-n | CE / in-house (REG-011) + NG-07 |

**Tilos a fagyasztás alatt kódolni / szállítani:**

- `LIVE_CDS=true` F1+ / HU-EU-US **LOCK** tenancyen; CDS Hooks a felírónak; shadow kimenet a klinikai UI-ra (NG-07/08, FR-470). A F2 **kód** a rendszer része (G5); az élő kimenet nem.
- F1+ renderer, amely `MedicationEntry`-t olvas, vagy ha–akkor / receptre szűrt CPIC sort ad (R-021).
- Valódi intézményi adat a shadow tárba OQ-16 + OQ-15 nélkül.
- „Nem MDSW / nincs NB” állítás a counsel aláírása előtt.
- PharmCAT matcher bekapcsolása F1+ klinikai úton (OQ-05 + REG-010 újra).

Ha OQ-05 = **NEM**, a már megírt F1+ mag **nem dobandó**: IIa / CE pályára megy (REG-010), a statikus renderer megmarad. Ha OQ-16 = **NEM**, a gateway kód megmarad, az út álnevesített + FR-115.

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
| **F0** | 0–3 hó | Spec fagyasztva. Outbound; ISO 9001; **SKU-P sales** (klinika veszi a rendszert); F1+ mag + F2 kód lakattal; F.6. | Rendszerlicenc-ajánlat + MSP | — |
| **F1+** | 3–9 hó | L0–L2 + FR-240 + FR-400-STATIC + FR-410-EDU + FR-490. Matcher **ki**. FR-410-LIVE **ki a leletről**. | Fizető labor, white-label lelet | Nem MDSW **csak ha** OQ-05 igen |
| **F1s** | F1+-szal párhuzamosan | Gateway (FR-460), shadow (FR-440), HITL (FR-450), izoláció (FR-470); REG-090/091 | G3 metrika, clinical evaluation input | Nem klinikai kimenet; OQ-15 |
| **F2** | 6–18 hó | In-house élő CDSS (FR-520/530, FR-410-LIVE a klinikai UI-n); ISO 13485 + 62304 + 14971 | Case study | In-house (REG-011) |
| **F3** | 18–36 hó | IIa CE; `LIVE_CDS` kapcsoló a már kiépített csövön | CE-jelölt CDSS | **IIa** |
| **F4** | 36+ hó | L5 partner; EESZT-modul; EHDS | Enterprise | IIa |

**Kritikus út:** OQ-05 → F1+ *forgalmazási* hatókör (nem a renderer-kód). OQ-15 → F1s *éles* HIS. A „kapcsoló átbillentése” F3-on **csak** CE/in-house után (FR-470). A F1+ mag kód F0-ban indul (§10.2).

### Kompetencia (SFIA)

| Szerep | Szint | Miért |
| --- | --- | --- |
| Solution Architect | L5 | Több szabályozási domain |
| RA / QA | L5 | ISO 13485 Management Representative |
| PRRC | Jogszabályi | MDR Art. 15; nem korlátlanul outsource |
| Senior Backend | L4 | IEC 62304 NFR-070a Class B (F1+ mag); NFR-070b Class C javaslat L4-live (OQ-06) |
| QA / Test | L4 | Gold set, IAA, regresszió |
| Klinikai farmakológus / genetikus | Szakvizsga | Ground truth, lektorálás |

Egyik sem opcionális. A6 a minimum.

### Árazási kötés a követelményekre (nem TAM)

A brief árazási modellje **követelmény-kötés**, nem megfigyelt ár. Javasolt Ft-sáv (következtetés, nem listaár): [Sales/pricing.md](Sales/pricing.md).

| Sáv | Modell | Spec-kötés |
| --- | --- | --- |
| Labor white-label (F1+ modul) | Opcionális tenancy, ha a labor *is* licencel | FR-400-STATIC; **nem** a mag-SKU |
| Platform (SKU-P) | Éves + telephely / klinikus | A klinika veszi a **rendszert**; F2/F3 aktiválás külön |
| Shadow/HITL (F1s) | A licenc része, ha a pack ON | FR-440–450 |
| Klinikai CDSS (L4-live) | Per-clinician/hó **aktiváláskor** | **Csak** F2/F3 ON; FR-520 |
| PRS (L5) | Per-report, partner-átárazás | FR-430 |
| Enterprise / EHR-vendor | Éves platform + integrációs egyszeri | P6; a F3 kapcsoló ugyanazon a csövön |

---

## 12. Traceability

A teljes mátrix: [D melléklet](D-risk-and-traceability.md).

Váz:

| Req ID | Forrás | Teszteset | MDR/AI Act |
| --- | --- | --- | --- |
| FR-100 | 2008/XXI. 6. § (2), 8. §, 12. § (1) | TC-CONSENT-001..006 | GSPR 14.1 |
| FR-110 | 6. § (7), 26. § (1); GDPR Art. 12(3) | TC-CONSENT-010..014 | GDPR Art. 12(3), 17; GSPR 14 |
| FR-120 | 26. § (1) | TC-AUDIT-001..006 | GSPR 17.2 |
| FR-210 | Klinikai kockázat + PharmCAT preprocessor | TC-CALL-001..012 | ISO 14971 RC-003 |
| FR-310 | PREPARE; PGx-Passport; PharmCAT 2.11.0 | TC-CONF-001..005 | IEC 62304 §6 |
| FR-400-STATIC | CPIC / DPWG / FDA | TC-RULE-001..040 | GSPR 17.1; OQ-05 |
| FR-410-LIVE | Fenokonverzió-irodalom | TC-PHENO-001..015 | Clinical eval; **nem** F1+ lelet |
| FR-470 | A.0 / NG-07 | TC-ISO-001..008 | Rule 11a kikerülés tilalma |
| FR-410-EDU | A.1.2 | TC-EDU-001..010 | OQ-05 csomag, nem válasz |
| FR-461 | E.3.1; A14 | TC-GW-010..020 | OQ-16 csomag, nem válasz |
| FR-450-BLIND | E.4.1 | TC-HITL-010..014 | OQ-15 támogató design |
| FR-700 | MDCG 2025-6; AI Act 6(1) | TC-LLM-NEG-001..003 | AI Act Art. 9, 15 |
| FR-710 | 6. § (6) | TC-EXPLAIN-001..004 | AI Act Art. 13; GSPR 23 |

---

## 13. Parking lot

- Onkológiai szomatikus panel (IVDR)
- HLA hiperszenzitivitás kiterjesztés (HLA-B\*57:01, \*15:02 túl)
- Magyar referencia-genom allélfrekvencia-korrekció (Semmelweis projekttől függ)
- Gyógyszertári medication review (PREPARE 28 patika — validált use case, nem v1)
- Feature-attribution (SHAP-osztály) **csak** ha később külön ML komponens kerül a rendszerbe (nem LLM; nem v1 PGx-core). S028 analógia. Nem G3.
- Pharma kohorsz-toborzás (EHDS 2031+)
- Biztosítói prevenciós modul
- Engineering ticket-bontás és gold-set annotációs SOP — **következő munka**, nem spec-feladat (§10.2)

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

**Klinikai (PGx-SOTA)**

7. `[V]` Swen et al. Lancet 2023;401:347–356 (PREPARE) + kritikai levelek — 21,0% vs 27,7%, OR 0,70, p=0,0075 (actionable DGI)
8. `[V]` van der Wouden et al. CPT 2019;106:866–873 (PGx-Passport)
9. `[V]` Kullo et al. Nat Rev Genet 2026;27:246–263
10. `[V]` eMERGE, Nat Med 2024, doi:10.1038/s41591-024-02796-z

**Szomszédos CDSS (nem PGx-SOTA, L5)**

10a. `[V]` Maqsood et al., arXiv:2603.14876v1 — n=593 055; Top-5 acc. 83,10%; **nem** G3, **nem** PCE-RWE. [S028-note](Sources/S028-curemd-hybrid-cdss-note.md).

**Technológia**

11. `[V]` PharmCAT changelog 2.11.0 (F5 removal) — pharmcat.clinpgx.org/changelog
12. `[V]` HL7 FHIR Genomics Reporting IG v3.0.0
13. `[V]` Dolin et al. Methods Inf Med 2018;57:e115–e123

**Piac**

14. `[R]` genetix.hu/arak — I-01, 2026-08-09; ebben a körben nem ismételve

---

## 15. Amit ez a spec nem tud

- **Nem** kitöltött F.6. A [Sales](Sales/README.md) **rendszerlicenc** (SKU-P); F2 a dobozban lakattal. Nem pecsét. OQ-17 (US) nyitott.
- **Nem** OQ-15 döntés. A „nincs hatása a kezelésre → nem Art. 62” *érv*, nem hatósági tény.
- **Nem** OQ-16 DPIA-döntés. A FR-461 kontrollok a DPO inputjai.
- **Nem** DPA, DPIA vagy etikai kérelem — E melléklet váz.
- A10 **nem** F1s 72 órás puffer. Visszavonáskor 72 h kaszkád (törlés vagy irreverzibilis anonimizálás). Megőrzés: A15. §0.1.
- A felhasználói hibrid-brief [1]–[7] hivatkozásai (meddeviceguide, monterail, arxiv 2603.14876, stb.) **L4/L5**; a Rule 11a állítás a MDCG/MDR primerre támaszkodik `[V]`, nem ezekre a blogokra.
- **S028** (CureMD hybrid CDSS) **elolvasva.** Nem F1s SOTA, nem G3/R-020 küszöb, nem PCE-RWE, nem „állami referencia” (VC-13). Nincs ilyen című fejezet. §9.5.
- **Nem** FDA CDS guidance mélyelemzés. MDR-ben nincs equivalent discretion. US út = OQ-17, default LOCK.

---

*PCE-SPEC-v1.2 FAGYASZTVA (§10.2). OQ-k ELŐTERJESZTVE. F1+ mag fejleszthető. Disclaimer ≠ felelősségkizárás.*
