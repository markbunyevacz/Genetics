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

## 0. Kérdés (A.8, szűkített)

> Védhető-e az A.1 F1+ pozíció, ha a kimenet a labor-diplotípushoz verziózott CPIC/DPWG/FDA **gén-szintű** szövegkivonatot rendel, **nincs** aktuális-gyógyszer párosítás, **nincs** fenokonverzió-alkalmazás, **nincs** CDS Hooks, és az aláíró a labor orvosa?

Ha a válasz **nem**, az F1+ klinikai kimenet IIa pályára esik (REG-010 újra; Notified Body a forgalomba hozatalhoz).

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
> A szoftver **nem** végez egyedi betegre szabott klinikai értékelést a aktuális gyógyszerlista vagy szervfunkció alapján, **nem** javasol terápiát, **nem** számít dózist, **nem** jelenik meg a felírási workflow interruptive riasztásaként, és **nem** helyettesíti a képzett egészségügyi szakember független orvosi döntését. Az aláíró a labor orvosa.

**Szabad (F1+ klinikai kimenet):** diplotípus + callability a laborhívásból (FR-240); statikus, verziózott guideline-szöveg a **meghívott génhez** (nem a felírt gyógyszerhez kötött pop-up); enciklopédia-nézet a beteg aktuális receptjéhez **nem** párosítva; fenokonverzió **oktató** bekezdés a gyógyszerlista olvasása nélkül (FR-410-EDU); a génhez tartozó **teljes** publikált gyógyszer/osztály-tábla (FR-400-STATIC).

**Tilos (F1+ klinikai kimenet):** order-select / order-sign típusú, a most felírt szerre szabott csere/dózis-utasítás; `functional_phenotype` az aktuális gyógyszerlistából a aláírt leleten; `dose_mg`; a shadow-motor kimenetének megjelenítése a kezelőorvosnak.

---

## III. Klinikai invariánsok és technikai garanciák

Ezek a kódszintű / CI-szintű állítások a specben. A counsel ezeket **tényként** kapja a dossziéból; a jogi minősítés ettől még a counselé.

### 1. Gyógyszerlista-vakság (FR-400-STATIC, FR-410-EDU)

A leletgeneráló renderer futásidőben **nem** kapja meg, nem olvassa és nem dolgozza fel a beteg aktuálisan szedett vagy felírt gyógyszereinek listáját (`MedicationEntry` nincs a report-renderer argumentumai között). Negatív teszt + CI call-graph.

### 2. Nincs betegre szabott „ha–akkor” (A.1.2)

A szoftver nem futtat egyedi döntési fát a beteg aktuális gyógyszerére. Ha a leleten egy adott gén (pl. CYP2D6) szerepel, a rendszer a hozzá tartozó **teljes**, változatlan, verziózott nemzetközi irányelv-táblázatot átemeli (mind az N sor), anélkül, hogy abból a betegre szabott, recepthez kötött következtetést vonna le. Tiltott tokenek a rendererben: „Ön” / „ennél a betegnél” / „a most felírt” (`E-EDU-001`).

### 3. FR-410-EDU — oktató bekezdések

A leleten megjelenő fenokonverziós vagy klinikai magyarázatok kizárólag **általános**, tankönyvi, guideline-azonosító + verzió + URL mellett közölt szövegek. Nem állítják, hogy *ez a beteg* jelenleg fenokonvertált. Nem tartalmaznak a beteg egyedi gyógyszer–gén interakciójára utaló egyedi megállapítást.

### 4. Aláírói felelősség (FR-490, REG-020)

A végtermékként létrejövő leletet a partnerlaboratórium szakorvosa ellenőrzi és írja alá. A szoftver nem ad ki automatizált, orvosi jóváhagyás nélküli validált leletet. Az F1+ default L3 útvonal: **outside-call** (a labor hívja a diplotípust); a PharmCAT matcher F1+ klinikai buildben **ki**.

### 5. Csatorna-izoláció (FR-470)

Az F1+ buildben a `LIVE_CDS` flag **compile-time false**. Nincs CDS Hooks endpoint. A shadow-motor kimenete nem íródik a Report/PDF/FHIR entitásba.

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
2. A labororvos aláírása és a „az orvos dönt” formula **nem** minősít ki (A.0).
3. Class I (Rule 11c) létezik, de a PGx terápiás információ **nem** 11c menekülés.

A hibrid (F1+ statikus társítás) a v1.1-hez képest **szűkít** (kivette az élő fenokonverziót és a gyógyszerlista-alapú kiemelést). **Nem** szünteti meg az OQ-05-öt.

---

## V. Kért kimenet

Kérjük a három közül **egyet** megjelölni. Ha Feltétellel: a feltételek a specbe kerülnek (FR/CI), nem szóbeli.

### Döntés

- [ ] **IGEN** — az A.1 F1+, a III. invariánsok folyamatos fennállása mellett, a counsel megítélése szerint **nem** valósít meg MDSW-t; Notified Body a forgalomba hozatalhoz **nem** szükséges *ebből a minősítésből*. (Egyéb kötelezettségek — GDPR, 2008/XXI., termékfelelősség — ettől függetlenek.)
- [ ] **NEM** — az F1+ MDSW; a counsel szerinti osztály: _______________ (gyártói default, ha MDSW: Rule 11a → IIa). Forgalomba hozatal: CE / Notified Body a counsel által megjelölt eljárás szerint.
- [ ] **FELTÉTELLEL** — IGEN, az alábbi feltételekkel (kötelező kitölteni):

Feltételek:

1. .................................................................................................
2. .................................................................................................
3. .................................................................................................

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

**Mellékletek:** PCE-SPEC-v1.2; A melléklet; F.1; MDCG 2019-11 Rev.1 (a counsel saját példánya).

*Ez az irat gyártói kérés. Nem helyettesíti a counsel független vizsgálatát. OQ-05 a F.6 sor kitöltéséig nyitott.*
