# A melléklet — Intended purpose, modul-minősítés, legális hibrid

| | |
| --- | --- |
| **Dokumentum** | PCE-SPEC-v1.2 Appendix A |
| **Dátum** | 2026-08-12 |
| **Jogalap** | MDCG 2019-11 Rev.1 (2025-06-17); MDR Annex VIII Rule 11 |
| **Státusz** | Tényalap OQ-05-höz — **nem** jogi állásfoglalás |

A MDCG Rev.1 szerint a minősítés és az osztályozás az **intended purpose**-ön áll vagy dől. A gyártónak minden modult önállóan kell minősítenie. A hatóság a termék **tényleges funkcióját és hatását** nézi, nem a disclaimer szövegét.

Ez a melléklet **három**, egymást követő (nem egyszerre élő klinikai) üzemmódot rögzít. Ugyanarra a kiadott *klinikai* szoftververzióra nem lehet F1+ és F2 intended purpose.

```
[ F1+  Okos laborriport ] ──► [ F1s  Shadow HITL ] ──► [ F2 in-house / F3 CE IIa ]
  statikus CPIC/FDA/DPWG         algoritmus fut,            élő felírás-pillanatú CDSS
  társítás, aláíró = labor       kezelőorvos NEM látja      Rule 11a
```

---

## A.0 Elutasított stratégia — „Regulatory Bypass”

**Elutasítva (NG-07).** Az F2/F3 kimenet (betegre szabott, aktuális gyógyszerhez kötött terápiás javaslat, interruptive riasztás, dózisszám) **nem** szállítható F1 köntösben azzal a védelemmel, hogy „a végső gombot az orvos nyomja meg” / „HITL majd igazolja”.

| Állítás | EU MDR valóság `[V]` Rule 11a |
| --- | --- |
| „Az orvos dönt, tehát nem eszköz” | Ha a szoftver információt ad, amelyet diagnosztikai vagy **terápiás döntéshez** használnak, az **IIa** (kivéve 11a felminősítés). Az orvos gombja nem minősít ki. |
| FDA 2022 CDS „az orvos le tudja vezetni a nyers adatból” | Az MDR-ben **nincs** FDA-típusú enforcement discretion. |
| Disclaimer a PDF alján | Nem változtatja meg a rendeltetést. A hatóság a hatást nézi. |
| Élő F2-kimenet + „később CE-zünk” | Forgalomba hozatal / használatba vétel CE nélkül, ha MDSW. |

A HITL **nem** mentesít, ha a kezelőorvos a napi ellátásban látja a gép javaslatát. A HITL a **shadow** üzemre van fenntartva (A.2, E melléklet).

---

## A.1 F1+ intended purpose — statikus tudástársítás (klinikai kimenet)

**Rendeltetés (tervezet, counsel előtt):**

A PCE F1+ a partnerlaboratórium — mint a 2008. évi XXI. tv. 12. § (1) szerinti engedélyezett egészségügyi szolgáltató — számára white-label **adminisztratív adatkezelő és riport-előállító** szoftver.

Célja a külső partnerlaboratórium által **már validált** diplotípus-eredmények strukturált megjelenítése, valamint a nyilvánosan elérhető, **verziózott** nemzetközi farmakogenetikai irányelvek (CPIC, DPWG, FDA-címke) **szöveges kivonatainak** automatizált hozzárendelése a laboratóriumi jelentéshez.

A szoftver **nem** végez egyedi betegre szabott klinikai értékelést a aktuális gyógyszerlista vagy szervfunkció alapján, **nem** javasol terápiát, **nem** számít dózist, **nem** jelenik meg a felírási workflow interruptive riasztásaként, és **nem** helyettesíti a képzett egészségügyi szakember független orvosi döntését. Az aláíró a labor orvosa.

**Szabad (F1+ klinikai kimenet):**

- Diplotípus + callability a laborhívásból (FR-240).
- Statikus, verziózott guideline-szöveg a **meghívott génhez** (nem a felírt gyógyszerhez kötött pop-up): pl. „A beteg CYP2D6 diplotípusa a labor szerint \*1/\*1 (NM). A CPIC vX szerint a CYP2D6 NM státuszhoz tartozó gyógyszer–stratégia párok a következők: [táblázat, forrás, URL].”
- Enciklopédia-nézet (FR-480): az orvos a génre kattint, a szoftver kilistázza a hivatalos útmutatókat; a beteg aktuális receptjéhez **nem** párosít proaktívan.
- Fenokonverzió **oktató** bekezdés: általános, guideline-ból vett lista (mely inhibitorok *általában* módosíthatnak), **anélkül**, hogy a rendszer a beteg aktuális gyógyszerlistájára alkalmazná (FR-410-EDU, A.1.2).
- A génhez tartozó **teljes** publikált gyógyszer/osztály-tábla, nem a beteg aktuális receptjére szűrve (FR-400-STATIC).

**Tilos (F1+ klinikai kimenet) — ez már F2/F3 vagy shadow:**

- Order-select / order-sign: „Ennél a betegnél a most felírt X-et Y-ra cseréld / a dózist 50%-kal csökkentsd.”
- `functional_phenotype` a **aktuális** gyógyszerlistából a aláírt leleten (FR-410-LIVE).
- `dose_mg`, „optimális dózis”, „mellékhatás megelőzése a szoftver által”.
- A shadow-motor kimenetének megjelenítése a kezelőorvosnak.

**❌ Tiltott intended purpose példa:** „A szoftver célja a farmakogenetikai adatok elemzése a betegre szabott optimális gyógyszerdózis meghatározása és a mellékhatások megelőzése érdekében.”

**MDSW-indoklás (gyártói, nem tanácsadói):** L0–L2 adminisztráció. L3 = labor. L4 F1+-ban **könyvtári társítás** (gén → publikált szöveg), nem a felírás pillanatának döntéstámogatása. **OQ-05 továbbra is nyitott:** a génhez rendelt CPIC terápiás szöveg önmagában lehet Rule 11a. A hibrid **szűkíti** a v1.1 F1-et (kivette a élő fenokonverziót és a gyógyszerlista-alapú kiemelést a klinikai kimenetből); nem szünteti meg az OQ-05-öt.

**Konfigurációs tilalom F1+ klinikai buildben:**

- FR-300 matcher default **OFF**.
- FR-410-LIVE, FR-520, FR-530 interruptive path **OFF**.
- FR-430 PRS: nincs hívás.
- Shadow kimenet soha nem íródik a Report entitásba (FR-470).

### A.1.1 Jogi nyilatkozat sablon (lelet / FHIR `DocumentReference.description`)

Counsel-review tárgy. **Nem** minősít ki MDSW-ből.

> Ez a lelet a partnerlaboratórium által megállapított diplotípus-eredmények, valamint a nyilvánosan elérhető nemzetközi farmakogenetikai irányelvek (CPIC, DPWG, FDA) aktuális, verziózott szövegkivonatainak automatizált párosításával készült.
>
> A jelentésben szereplő irányelv-szövegek általános, publikált tudományos források. A szoftver nem végez egyedi, a beteg aktuális gyógyszerlistájára vagy szervfunkciójára szabott klinikai értékelést, nem módosítja a laboratóriumi alapadatokat, és nem tesz javaslatot egyedi terápiára vagy konkrét gyógyszeradagolásra.
>
> Az információ nem helyettesíti a kezelőorvos vagy gyógyszerész független szakmai döntését. Terápiás módosítás kizárólag a kezelőorvos felelőssége, a beteg klinikai képének figyelembevételével.
>
> Aláíró orvos: \[laboratóriumi szakorvos neve és pecsétszáma\]

A „fejlesztő minden felelősséget kizár” formula **nincs** a sablonban: a termékfelelősség / MDR GSPR nem disclaimerezhető el; a counsel tölti ki a felelősségi bekezdést.

### A.1.2 FR-410-EDU / FR-400-STATIC — OQ-05 technikai csomag

**Nem** jogi igazolás. A counsel ezt a csomagot kapja. OQ-05 nyitott marad: a gén-szintű CPIC terápiás szöveg önmagában lehet Rule 11a.

| Szabály | Tilos | Szabad |
| --- | --- | --- |
| Ha–akkor | „Mivel Ön [gyógyszer]-t kap, a CYP2D6 miatt váltson [Y]-ra / csökkentse a dózist.” | Nincs beteg-gyógyszer kötés. |
| Tankönyv | Szabadon generált, forrás nélküli tanács | Verziózott guideline-kivonat + URL, mint enciklopédia. |
| Kombináció | Diplotípus **és** aktuális gyógyszerlista egy függvényben | A lelet a gén **összes** CPIC/DPWG/FDA sorát mutatja, a recepttől függetlenül. |
| Fenokonverzió | `functional_phenotype` ebből a betegből | Osztály-szintű oktató bekezdés (FR-410-EDU). |

Példa-szerkezet (nem végleges klinikai szöveg; lektor: OQ-14):

> A CPIC nemzetközi irányelvei alapján a CYP2D6 ultragyors metabolizáló *kategóriában* a triciklikus antidepresszánsok alkalmazásakor fokozott metabolizáció és a hatás elmaradása *a guideline szerint* várható. Az irányelv ilyen *kategóriában* alternatív terápiát vagy dózismódosítást tárgyal. Részletes útmutató: CPIC Guideline [azonosító] v[n], [URL].

A „Ön” / „ennél a betegnél” / „a most felírt” formulák a F1+ rendererben **tiltott tokenek** (CI).

---

## A.2 F1s — Shadow HITL (nem klinikai kimenet)

**Rendeltetés:** a CDSS-motor (FR-410-LIVE, beteg–gyógyszer párosítás, opcionális dózis-*jelölt*) **háttérben** fut, zárt kutatási/validációs tárba ír. A kezelőorvos az ellátásban **ebből semmit nem lát**. A HITL egy külön, kutatási UI-n vagy szakértői bizottságban történik, utólag: „A motor szerint itt stratégia-váltás lett volna. Egyetért?” (igen/nem + indok).

Ez **klinikai értékelési / vizsgálati** tevékenység, nem „titkos CDSS az F1-ben”. Lásd E melléklet, REG-090, OQ-15.

Ha a shadow kimenet bármely klinikai képernyőre kerül, az üzemmód **F2**, és az A.1 intended purpose hamis.

---

## A.3 F2/F3 intended purpose — PGx-CDSS (élő)

**Rendeltetés (tervezet):** farmakogenetikai klinikai döntéstámogatás. A felírás vagy medication review pillanatában a diplotípus + aktuális gyógyszerlista + szervfunkció alapján információ, amelyet a klinikus **terápiás döntéshez** használ. Kimenet: CDS Hooks Card és/vagy SMART on FHIR.

**Minősítés:** MDSW. **Osztály:** Rule **11a → IIa** default. DPYD–fluoropirimidin: D melléklet R-007. Nem Class I. Nem FDA CDS-kiskapu.

**F2 vs F3:** F2 in-house (REG-011). F3 CE, Notified Body, piaci forgalomba hozatal. Az F1s HITL-adatok a clinical evaluation inputjai, nem helyettesítik a CE-t.

**Lakat alatti magyarázat (HU/EU: F2/F3 UI zárva, amíg CE/in-house):** a bekapcsolt magyarázat **FR-710** — gén, diplotípus, guideline-verzió, szabály, callability; determinisztikus, nem LLM. **Nem** SHAP a v1 PGx-magra. SHAP (S028 analógia) csak P2 jelölt, ha később külön ML komponens kerül a rendszerbe. §9.5; VC-13.

---

## A.4 L0–L7 modul-minősítési mátrix

| Modul | Tartalom | F1+ klinikai | F1s shadow | F2/F3 | MDSW? |
| --- | --- | --- | --- | --- | --- |
| **L0** | Consent, 30 év, kutatási hozzájárulás (FR-115) | Admin | Admin + research consent | Admin | Nem |
| **L1** | VCF, outside-call, FHIR | Tárolás | + Subscription a gatewayen át | Tárolás | Nem |
| **L2** | Normalizálás | Adatátalakítás | u.a. | u.a. | Nem |
| **L3** | Matcher vs outside-call | Labor; matcher OFF | u.a. | Határ, ha matcher ON | Határ |
| **L4-static** | Gén → verziózott guideline-szöveg | **Be** | — | Be (plusz élő) | OQ-05 |
| **L4-live** | Gyógyszerlista → functional phenotype, order-alert | **Ki** | **Be**, klinikai UI-ra **nem** | **Be**, klinikai UI-ra **igen** | IIa ha klinikai UI |
| **L5** | PRS | Ki | Ki | F4 | IIa |
| **L6-report** | PDF/FHIR aláírt lelet | Be | Nem ír shadowot a leletbe | Be | L4-static-cal |
| **L6-cds** | CDS Hooks / SMART interruptive | Ki | Ki | Be | IIa |
| **L6-hitl** | Kutatási review UI | Ki | Be | PMS | Nem klinikai eszköz-UI |
| **L7** | Audit, PMS | Be | Shadow log elkülönítve | Be | Nem önálló MDSW |

### L3 határ

F1+ default: FR-240 outside-call. FR-300 matcher ON = OQ-05 + REG-010 újra.

---

## A.5 Modul-függőségek

```
Klinikai path (F1+):
  L0 ──► L1 ──► L2 ──► L3(outside) ──► L4-static ──► L6-report
  (gyógyszerlista NEM bemenet az L4-static-hoz)

Shadow path (F1s) — külön store, külön IAM:
  [HIS esemény] ──► [Gateway a intézmény zónájában] ──► L4-live ──► HITL DB
  L6-report ──X── L4-live   (FR-470 tiltott él)

F2/F3: L4-live ──► L6-cds  (kapcsoló csak CE / in-house után)
```

---

## A.6 Class I

`[CORRECTED]` VC-04. Class I létezik (11c). PGx élő terápiás információ **nem** 11c. F1+ menekülés = **nem-MDSW könyvtári társítás** (OQ-05), nem Class I.

---

## A.7 In-house (F2)

REG-011. Nem mentesít 2008/XXI. és GDPR alól. Intézményen kívül = F3.

---

## A.8 OQ-05 — szűkített kérdés

> Védhető-e az A.1 F1+ pozíció, ha a kimenet a labor-diplotípushoz verziózott CPIC/DPWG/FDA **gén-szintű** szövegkivonatot rendel, **nincs** aktuális-gyógyszer párosítás, **nincs** fenokonverzió-alkalmazás, **nincs** CDS Hooks, és az aláíró a labor orvosa?

A v1.1 kérdés tágabb volt (gyógyszerajánlás-szöveg általában). A v1.2 szűkít. A válasz továbbra is **külső counsel**. Csomag: A.1, A.1.1, **A.1.2**, A.4, FR-400-STATIC, FR-410-EDU, FR-470, REG-010, MDCG Rev.1.
