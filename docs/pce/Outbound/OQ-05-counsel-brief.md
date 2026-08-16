# Counsel brief — Tényalapú jogi előterjesztés (OQ-05)

| | |
| --- | --- |
| **Iktató** | PCE-OUT-OQ-05 / v1.2 |
| **Dátum** | 2026-08-12 |
| **Státusz** | TERVEZET — küldhető; **nem** counsel-állásfoglalás |
| **Feladó** | `[Gyártó neve]` (A9; név a fejlécben töltendő) |
| **Címzett** | Külső jogi és szabályozási tanácsadó (Counsel) |
| **Tárgy** | Állásfoglalás-kérés: az F1+ modul védhető-e nem-MDSW-ként (MDR (EU) 2017/745) |
| **OQ** | OQ-05 — **ELŐTERJESZTVE**, a jelen irat **nem** zárja |

Tisztelt Counsel!

Kérjük, a csatolt v1.2 műszaki specifikáció és az alább **szó szerint** idézett rendeltetés alapján adjon írásos állásfoglalást. A gyártó *kéri* a nem-MDSW pozíciót; **nem** állítja, hogy az már jogerős vagy hatósági tény.

---

## 0. Kérdés (A.8, szűkített) + G Q1–Q4

> Védhető-e az A.1 F1+ pozíció, ha a kimenet a labor-diplotípushoz verziózott CPIC/DPWG/FDA **gén-szintű** szövegkivonatot rendel, **nincs** aktuális-gyógyszer párosítás, **nincs** fenokonverzió-alkalmazás, **nincs** CDS Hooks, és az aláíró a labor orvosa?

A G melléklet szerint a fenti egyetlen kérdés még túl tág. Kérjük **előbb** a három igen/nem kérdést a **hatályos** Rule 11-re (a pecsét marad Igen/Nem/Feltétellel a V. szakaszban). A **Q4** a COM(2025) 1023 *javaslat*; **nem** pecsételi Q1–Q3-at. A counsel egyszer nézi az anyagot.

| # | Kérdés | Melléklet |
| --- | --- | --- |
| **Q1** | Az a kimenet, amely a vizsgált génekre a **teljes, szűretlen**, verziózott guideline-táblát nyomtatja a diplotípus mellé, anélkül hogy ismerné a beteg gyógyszerlistáját — Rule 11 hatálya, vagy Rule 11c Class I? | `tests/test_report.py`; `src/pce_report/schema.py` (`ALLOWED_B41_TOP_LEVEL` = 47, `FORBIDDEN_B41_FIELDS` = 15); gold outside-call fixture `tests/fixtures/f1plus-v0/outside-call-cyp2d6-called.json` (**nem** aláírt PDF); gépelt jegyzőkönyv: `ProcessArtifacts/OQ-05-TEST-PROTOCOL.md` (**nem** pecsét) |
| **Q2** | Ha Rule 11 alatt áll: a beteg-specifikus szelekció hiánya elegendő-e az **IIa alatti** besoroláshoz? | ugyanaz |
| **Q3** | Ha Q1 = Class I: elegendő-e a CI-invariáns-készlet (`LIVE_CDS is False`; `MATCHER_ON is False`; `IIA_SAFE_BLOCK is True`; `! grep MedicationEntry src/pce_report`; `! grep pce_gateway.pipeline src/pce_report`) az MDCG Rev.1 dokumentált modulhatárhoz? A Q3-claim **10** unittest-id a jegyzőkönyvben, nem a teljes suite. | `.github/workflows/ci.yml`; `ProcessArtifacts/OQ-05-TEST-PROTOCOL.md` Q3 |
| **Q4** | Mi az F1+ (L4-static) és az L4-live besorolása a COM(2025) 1023 szerinti **javasolt** Rule 11 alatt (alapértelmezés Class I; critical / serious / non-serious)? Az A.4.1 páronkénti súlyossági tábla megfelel-e az ott javasolt eszkalációs logikának? | COM(2025) 1023 PDF (S077); EUR-Lex HTML (S080); A.4.1; G §2.4 / §7 |

Ha a válasz **Q1 = Rule 11 és Q2 = nem**, az F1+ klinikai kimenet IIa pályára esik (REG-010 újra; a forgalomba hozatalhoz Notified Body szükséges).

Amíg a pecsét hiányzik, a gyártó **Class I MDSW** technical file-lal halad (G §3.4), nem „nem eszköz”-ként. Ez nem előre pecsételi a nem-MDSW-t.

---

## I. Bevezetés és kontextus

A gyártó laboratóriumi informatikai modult (**F1+**) fejleszt partnerlaboratóriumok számára. A partnerlabor — mint a 2008. évi XXI. tv. 12. § (1) szerinti engedélyezett egészségügyi szolgáltató — **már megállapítja** a farmakogenetikai diplotípust. Az F1+ a diplotípus **strukturált, white-label** megjelenítését és a nyilvános, verziózott irányelv-szövegek **gén-szintű** hozzárendelését végzi.

Két további üzemmód **nem** tárgya ennek a kérésnek, de a dossziéban szerepel, hogy a counsel lássa a határt:

| Üzemmód | Klinikai kimenet a kezelőorvosnak? | MDSW-kérdés |
| --- | --- | --- |
| **F1+** (ez a kérés) | Aláírt laborlelet; statikus guideline-szöveg | OQ-05 |
| **F1s** Shadow | **Nem** — a kezelőorvos semmit nem lát | OQ-15 / OQ-16 |
| **F2/F3** | Élő CDSS a felírás pillanatában | Rule 11a → IIa; CE / in-house |

Az „F2 képesség F1 minőségben, mert az orvos dönt / disclaimer van a PDF-en” stratégia **elutasítva** (NG-07; A.0). Kérjük, ezt a counsel **ne** használja a nem-MDSW indoklásban.

Jogalap a minősítéshez: MDCG 2019-11 Rev.1 (2025-06-17); MDR Annex VIII Rule 11. A minősítés az **intended purpose**-ön áll. A hatóság a tényleges funkciót és hatást nézi, nem a disclaimer szövegét.

---

## II. Rendeltetési cél — A.1 szó szerint

A counsel a minősítést **erre** a szövegre adja, ne parafrázisra. Forrás: A melléklet A.1.

> A PCE F1+ a partnerlaboratórium — mint a 2008. évi XXI. tv. 12. § (1) szerinti engedélyezett egészségügyi szolgáltató — számára white-label **adminisztratív adatkezelő és riport-előállító** szoftver.
>
> Célja a külső partnerlaboratórium által **már validált** diplotípus-eredmények strukturált megjelenítése, valamint a nyilvánosan elérhető, **verziózott** nemzetközi farmakogenetikai irányelvek (CPIC, DPWG, FDA-címke) **szöveges kivonatainak** automatizált hozzárendelése a laboratóriumi jelentéshez.
>
> A szoftver **nem** végez egyedi betegre szabott klinikai értékelést az aktuális gyógyszerlista vagy szervfunkció alapján, **nem** javasol terápiát, **nem** számít dózist, **nem** jelenik meg a felírási workflow interruptive riasztásaként, és **nem** helyettesíti a képzett egészségügyi szakember független orvosi döntését. Az aláíró a labor orvosa.

**Szabad (F1+ klinikai kimenet):** diplotípus + callability a laborhívásból (FR-240); statikus, verziózott guideline-szöveg a **meghívott génhez** (nem a felírt gyógyszerhez kötött pop-up); enciklopédia-nézet a beteg aktuális receptjéhez **nem** párosítva; fenokonverzió **oktató** bekezdés a gyógyszerlista olvasása nélkül (FR-410-EDU); a génhez tartozó **teljes** publikált gyógyszer/osztály-tábla (FR-400-STATIC).

**Tilos (F1+ klinikai kimenet):** order-select / order-sign típusú, a most felírt szerre szabott csere/dózis-utasítás; `functional_phenotype` az aktuális gyógyszerlistából az aláírt leleten; `dose_mg`; a shadow-motor kimenetének megjelenítése a kezelőorvosnak.

---

## III. Klinikai invariánsok és technikai garanciák

Ezek a kódszintű / CI-szintű állítások a specben. A counsel ezeket **tényként** kapja a dossziéból; a jogi minősítés ettől még a counselé.

### 1. Gyógyszerlista-vakság (FR-400-STATIC, FR-410-EDU)

A leletgeneráló renderer futásidőben **nem** kapja meg, nem olvassa és nem dolgozza fel a beteg aktuálisan szedett vagy felírt gyógyszereinek listáját (`MedicationEntry` nincs a report-renderer argumentumai között). Negatív teszt + CI call-graph.

### 2. Nincs betegre szabott „ha–akkor” (A.1.2)

A szoftver nem futtat egyedi döntési fát a beteg aktuális gyógyszerére. Ha a leleten egy adott gén (pl. CYP2D6) szerepel, a rendszer a hozzá tartozó **teljes**, változatlan, verziózott nemzetközi irányelv-táblázatot átemeli (mind az N sort), anélkül, hogy abból a betegre szabott, recepthez kötött következtetést vonna le. Tiltott tokenek a rendererben: „Ön” / „ennél a betegnél” / „a most felírt” (`E-EDU-001`).

### 3. FR-410-EDU — oktató bekezdések

A leleten megjelenő fenokonverziós vagy klinikai magyarázatok kizárólag **általános**, tankönyvi, guideline-azonosító + verzió + URL mellett közölt szövegek. Nem állítják, hogy *ez a beteg* jelenleg fenokonvertált. Nem tartalmaznak a beteg egyedi gyógyszer–gén interakciójára utaló egyedi megállapítást.

### 4. Aláírói felelősség (FR-490, REG-020)

A végtermékként létrejövő leletet a partnerlaboratórium szakorvosa ellenőrzi és írja alá. A szoftver nem ad ki automatizált, orvosi jóváhagyás nélküli validált leletet. Az F1+ default L3 útvonal: **outside-call** (a labor hívja a diplotípust); a PharmCAT matcher F1+ klinikai buildben **ki**.

### 5. Csatorna-izoláció (FR-470)

Az F1+ processzuson (`pce_clinical`) a `LIVE_CDS` flag **compile-time false**, és **nincs** CDS Hooks endpoint (404 `E-ISO-002`). A repo tartalmaz egy külön F2 processzust (`pce_cds`); a kimenet lakattal: POST 200 üres `cards`, nincs suggestion. Q3 CI-invariánsok változatlanok. A shadow-motor kimenete nem íródik a Report/PDF/FHIR entitásba.

### 6. Nyilatkozat a leleten (A.1.1) — **nem** felelősségkizárás

Minden F1+ PDF/FHIR oldal tartalmazza az A.1.1 sablont (counsel-véglegesítendő). Ez **tájékoztató / rendeltetés-mondat**. A „fejlesztő minden felelősséget kizár” formula **nincs** a sablonban: a termékfelelősség / MDR GSPR nem disclaimerezhető. A disclaimer **nem** minősít ki MDSW-ből (A.0).

A.1.1 jelenlegi szöveg (counsel töltheti a felelősségi bekezdést):

> Ez a lelet a partnerlaboratórium által megállapított diplotípus-eredmények, valamint a nyilvánosan elérhető nemzetközi farmakogenetikai irányelvek (CPIC, DPWG, FDA) aktuális, verziózott szövegkivonatainak automatizált párosításával készült.
>
> A jelentésben szereplő irányelv-szövegek általános, publikált tudományos források. A szoftver nem végez egyedi, a beteg aktuális gyógyszerlistájára vagy szervfunkciójára szabott klinikai értékelést, nem módosítja a laboratóriumi alapadatokat, és nem tesz javaslatot egyedi terápiára vagy konkrét gyógyszeradagolásra.
>
> Az információ nem helyettesíti a kezelőorvos vagy gyógyszerész független szakmai döntését. Terápiás módosítás kizárólag a kezelőorvos felelőssége, a beteg klinikai képének figyelembevételével.
>
> Aláíró orvos: \[laboratóriumi szakorvos neve és pecsétszáma\]

---

## IV. A gyártó által ismert maradék kockázat (nem elhallgatva)

A gyártó **nem** kéri, hogy a counsel ezt a kockázatot hallgassa el:

1. A génhez rendelt CPIC/DPWG/FDA **terápiás** szöveg (dózis-/csere-stratégia a *kategóriában*) önmagában lehet MDR Rule **11a** (információ, amelyet diagnosztikai vagy terápiás döntéshez használnak) → Class **IIa**, akkor is, ha nincs aktuális-gyógyszer szűrés.
2. A labororvos aláírása és az „Az orvos dönt” formula **nem** minősít ki (A.0).
3. Class I (Rule 11c) létezik, de a PGx terápiás információ **nem** 11c menekülés.

A hibrid (F1+ statikus társítás) a v1.1-hez képest **szűkít** (kivette az élő fenokonverziót és a gyógyszerlista-alapú kiemelést). **Nem** szünteti meg az OQ-05-öt.

### IV.a Szomszédos L4 blogok — nem lezárt pecsét

A gyártó kapott vendor-blog hivatkozásokat (Tandem Health, 2026-06-24; punktum.net; mdxcro.com; IntuitionLabs a Tandem cikkben). **L4.** Nem Notified Body határozat.

Amit ezek **összhangban** mondanak a spec A.0 / NG-07-tel (a primer továbbra is **MDCG 2019-11 Rev.1 + MDR Rule 11**, S004/S005/S020):

- Az „AI asszisztens” / „csak tájékoztató” címke **nem** minősít ki, ha a kimenet klinikai döntést támogat.
- A puszta tárolás/megjelenítés vs. a döntést *befolyásoló* kimenet az MDCG kérdése.

Amit **nem** szabad belőlük kiolvasni (VC-14):

- Hogy a FR-400-STATIC gyógyszerlista-vakság **bizonyítottan** nem-MDSW. A dosszié IV.1 pontja nyitva: gén-szintű CPIC/DPWG/FDA *terápiás* szöveg lehet Rule 11a gyógyszerlista nélkül is.
- Hogy a Translational Software lab-API „bizonyítja” az F1+ EU-s biztonságát. A TSI 510(k) **elutasítás** (US, `[R]`) ellenkező irányú tanulság a betegre szabott riportokra.

Kérjük a counsel-t, a minősítést a **MDCG/MDR primerre** és az A.1 szövegre adja, ne ezekre a blogokra.

---

## IV.b Q4 — javasolt Rule 11 (COM(2025) 1023), nem hatályos jog

A Q1–Q3 a **hatályos** MDR Annex VIII Rule 11 + MDCG 2019-11 Rev.1. A Q4 **külön**: a Bizottság 2025-12-16-i javaslata (COM(2025) 1023 final). Nem alkalmazandó, amíg a Hivatalos Lap + Art. 5 (20 nap + 6 hónap). A 2026-os tanúsítási terv **nem** erre épül (A18).

Kérjük a Q4-et **ugyanabban az ülésben**, mert a counsel egyszer nézi a dossziét.

A javasolt 6.3 Rule 11 szó szerint (S080, EUR-Lex HTML; a pinelt PDF pypdf-fel nem adja ki a „Rule 11” stringet):

> Software which is intended to generate an output that confers a clinical benefit and is used for diagnosis, treatment, prevention, monitoring, prediction, prognosis, compensation or alleviation of a disease or condition is classified as **class I**, unless the output is intended for a disease or condition:
> – in a **critical situation** … death or an irreversible deterioration … → **class III**;
> – in a **serious situation** … or to drive clinical management in a critical situation → **class IIb**;
> – in a **non-serious situation**, or to drive clinical management in a serious situation or to inform clinical management in a critical or serious situation → **class IIa**.

Az A.4.1 tábla (DPYD S=5, CYP2C19–clopidogrel, kodein, HLA-B\*15:02, tiopurin) a dosszié inputja az OQ-06-hoz **és** ehhez a Q4-hez. Nem pecsét.

**Nem** kérjük, hogy a Q4 válasz feloldja a `LIVE_CDS` / `MATCHER_ON` / `IIA_SAFE_BLOCK` lakatot.

---

## V. Kért kimenet

Kérjük a három közül **egyet** megjelölni **Q1–Q3-ra**. Ha Feltétellel: a feltételek a specbe kerülnek (FR/CI), nem szóbeli. A **Q4** válasz külön bekezdés; **nem** helyettesíti a lenti pecsétet.

Gyártói kitöltési javaslat (a négyzetek **üresek** maradnak): [OQ-05-feltetellel-tervezet.md](OQ-05-feltetellel-tervezet.md). A unittest-suite mérete **nem** IGEN. Az F5 fail-open és a CI JAR HTTP **nem** NEM. Pecsétig Class I MDSW dosszié (G §3.4).

### Döntés

- [ ] **IGEN** — az A.1 F1+, a III. invariánsok folyamatos fennállása mellett, a counsel megítélése szerint **nem** valósít meg MDSW-t; Notified Body a forgalomba hozatalhoz **nem** szükséges *ebből a minősítésből*. (Egyéb kötelezettségek — GDPR, 2008/XXI., termékfelelősség — ettől függetlenek.)
- [ ] **NEM** — az F1+ MDSW; a counsel szerinti osztály: _______________ (gyártói default, ha MDSW: Rule 11a → IIa). Forgalomba hozatal: CE / Notified Body a counsel által megjelölt eljárás szerint.
- [ ] **FELTÉTELLEL** — IGEN, az alábbi feltételekkel (kötelező kitölteni):

Feltételek:

1. .................................................................................................
2. .................................................................................................
3. .................................................................................................

### Q4 — javasolt Rule 11 (nem a V. pecsét)

- F1+ (L4-static) a COM(2025) 1023 szerinti javasolt Rule 11 alatt: _______________
- L4-live ugyanott: _______________
- Az A.4.1 tábla megfelel-e a critical / serious / non-serious eszkalációnak? Igen / Nem / Feltétellel: _______________

### A gyártó által kért (nem előre aláírt) nyilatkozat-szöveg

Az alábbi szöveg **csak akkor** használható, ha a fenti döntés IGEN vagy a Feltétel teljesült. A counsel saját céges sablonját is elfogadjuk.

> ÁLLÁSFOGLALÁS
>
> Alulírott, mint jogi és szabályozási tanácsadó, a PCE-SPEC-v1.2-ben bemutatott F1+ rendeltetés (A.1) és működési invariánsok (különösen a gyógyszerlista-vakság, a betegre szabott ha–akkor logika hiánya, a FR-410-EDU oktató jelleg, a FR-470 izoláció és a labororvosi aláírás) alapján kijelentem, hogy az F1+ modul — a jelen állásfoglalásban rögzített feltételek mellett — **nem** valósít meg az MDR értelmében vett orvostechnikai szoftver (MDSW) funkciót, így annak piacra hozatala **ebből a minősítésből** nem engedélyköteles a Notified Body részéről.
>
> Fenntartás: a gén-szintű, verziózott CPIC/DPWG/FDA terápiás szöveg Rule 11a kockázatát a dosszié IV. pontja szerint mérlegeltem. A leleti A.1.1 nyilatkozat nem MDSW-kimenekülés és nem termékfelelősség-kizárás.

---

## VI. Aláírás

| | |
| --- | --- |
| Counsel neve / kamarai azonosító | .................................... |
| Cég / iroda | .................................... |
| Dátum | .................................... |
| Aláírás / pecsét | .................................... |
| Mellékelt dosszié verziója | PCE-SPEC-v1.2 + A melléklet (A.0, A.1, A.1.1, A.1.2, A.4, A.8) |

**Mellékletek:** PCE-SPEC-v1.2; A melléklet (REG-010); F.1; G §3 + §7; MDCG 2019-11 Rev.1 (a counsel saját példánya; a repo S004/S005 URL-t pinel, PDF-et **nem**); COM(2025) 1023 final PDF + EUR-Lex HTML (S077/S080); `tests/test_report.py`; `src/pce_report/schema.py`; `.github/workflows/ci.yml`; gold outside-call fixture `tests/fixtures/f1plus-v0/outside-call-cyp2d6-called.json` (**nem** aláírt PDF); `docs/pce/ProcessArtifacts/OQ-05-TEST-PROTOCOL.md` (gépelt szoftver-evidencia, **nem** pecsét); `docs/pce/Outbound/OQ-05-feltetellel-tervezet.md` (gyártói záradék-tervezet, **nem** pecsét). A D melléklet **kezdeti** ISO 14971 nyilvántartás, **nem** teljes dosszié; REG-030 **nem** küldési feltétel. Tandem/punktum/mdxcro **nem** a minősítés primer forrása. **MDCG 2024-7 nem melléklet** — az a PAR-sablon (NB-kijelölés), nem Rule 11 Q&A (E-30).

*Ez az irat gyártói kérés. Nem helyettesíti a counsel független vizsgálatát. OQ-05 a F.6 sor kitöltéséig nyitott.*
