# G melléklet — Az öt nyitott tétel kidolgozása

| | |
| --- | --- |
| **Dokumentum-ID** | PCE-G-v1.0 |
| **Dátum** | 2026-08-13 |
| **Bemenet** | PCE-SPEC-v1.2, A–F melléklet, `src/`, `tests/`, SOURCE-REGISTRY S001–S062 |
| **Célja** | Az OQ-05 / OQ-06 / OQ-16 / S055 / F-14 tételekhez **döntési javaslat és levezetés**. Ez a melléklet **nem** pecsételi le ezeket a tételeket. |
| **Státusz** | S055 / S060 / S062 **LEZÁRVA**. OQ-05 / OQ-06 / OQ-16 / F-14: javaslat a pecsételő felé. |

**Jelölés:** `[V]` verifikált primer forrásból (pin vagy ezen a napon olvasott) · `[S]` másodlagos forrás · `[I]` következtetés · `[E]` becslés · `[A]` feltevés

Ez a melléklet döntési javaslat és levezetés: **nem** zárja az OQ-05 / OQ-06 / OQ-16 pecsétjét, **nem** tartalmaz listaárat, és **nem** Rule 11 határozat.

A bemeneti vázlat 108 tesztet és S001–S055-öt említett. A G pecsét-napján (2026-08-13): unittest **113 OK**. 2026-08-14 (D-44, F2 cső): **124 OK**. 2026-08-14 (D-45, ETAP 0): **134 OK**. 2026-08-15 (D-46, PREPARE-12 ready): **158 OK**. 2026-08-15 (D-47, szoftver-KÉSZ): unittest **165 OK**. 2026-08-15 (D-48, F5 mock pipeline): unittest **184 OK**. A SOURCE-REGISTRY S074-ig tart (S060 és S062 **lezárva**; S063–S066 ETAP 0; S067–S069 2026-08-15 index párok; S070–S073 PharmCAT 3.4.0 + warfarin + rec_view; S074 F5 mock L5). Az F1+ allow-list **47** top-level kulcs (`ALLOWED_B41_TOP_LEVEL`, plusz `pharmvar_version` és `cpic_data_version`), deny-list **15** (`FORBIDDEN_B41_FIELDS`). A hivatalos forrás-pin **19** fájlnál `ok: true` (2026-08-13); ETAP 0 után **26**; index-pár kör után **41**; szoftver-KÉSZ után **87**.

---

# 1. S055 — GDPR Art. 12(3) primer forrás · **LEZÁRVA**

## 1.1 A szöveg

`[V]` EUR-Lex, CELEX 32016R0679, HTML pin: `Sources/official/eur-lex-gdpr-2016-679.html` (SHA-256 `887784eb…`, 809 035 byte, 2026-08-13). OJ-hivatkozás a HTML-ben: **OJ L 119**, **4.5.2016**. PDF pin is megvan (`eur-lex-gdpr-2016-679.pdf`); a PDF szövegkinyerése ebben a környezetben üres, ezért a cikkek a HTML-ből.

Art. 12(3) első mondata (tag-mentesített HTML, szó szerint):

> The controller shall provide information on action taken on a request under Articles 15 to 22 to the data subject without undue delay and in any event within one month of receipt of the request.

Folytatás a pinelt HTML-ben: a határidő **két további hónappal** meghosszabbítható a kérelmek összetettsége és száma alapján; a hosszabbításról az érintettet a kérelem beérkezésétől számított **egy hónapon belül** kell tájékoztatni, a késedelem indokaival együtt.

Art. 12(4): ha az adatkezelő nem intézkedik, **legkésőbb egy hónapon belül** tájékoztatnia kell az érintettet az okokról, valamint a panasz és a bírósági jogorvoslat lehetőségéről.

Art. 17(1) (`Right to erasure`): az érintettnek joga van a rá vonatkozó személyes adatok törléséhez **without undue delay**, és az adatkezelő köteles törölni **without undue delay**, ha a (a)–(f) indokok egyike fennáll.

## 1.2 Amit ez javít az FR-110-en — **két külön határidő, nem egy**

A spec korábbi megfogalmazása a magyar 26. § (1)-re igaz volt („határidő nélkül”), de a GDPR Art. 17(1) `without undue delay` fordulatát elhallgatta. Három rendelkezés fut párhuzamosan:

| Kötelezettség | Jogalap | Határidő |
| --- | --- | --- |
| A törlés **elvégzése** | GDPR Art. 17(1) `[V]` | „without undue delay” — **kvantifikálatlan, de nem hiányzó** |
| Az érintett **tájékoztatása** a megtett intézkedésről | GDPR Art. 12(3) `[V]` | **egy hónap** (+2 hónap, értesítéssel az első hónapon belül) |
| A genetikai nyilvántartás megsemmisítése visszavonáskor | 2008/XXI. 26. § (1) `[V]` S001 | **nincs határidő** |

`[I]` Kvantifikálatlan határidő nem azonos a határidő hiányával. Az A10 72 órás SLA a *törlés* üzemi célja; az Art. 12(3)/12(4) a *válaszlevél* határideje.

## 1.3 FR-110 kiegészítés — két artefaktum

**Új acceptance criterion (Compliance P0), a specbe beírva:**

- Hozzájárulás-visszavonás vagy Art. 17 törlési kérelem rögzítésekor a rendszer **két külön artefaktumot** állít elő: (a) törlési tanúsítvány a kaszkád lefutásáról (A10: 72 h), és (b) **érintetti válaszlevél** a megtett intézkedésről, kiállítási határidő: a kérelem beérkezésétől **egy hónap** (Art. 12(3)). A (b) akkor is kötelező, ha a törlés jogszerűen **megtagadásra** kerül (Art. 12(4)).
- Negatív teszt: 30 napnál régebbi, válaszlevél nélküli kérelem a compliance dashboardon `E-DSR-OVERDUE` riasztást ad.

**Miért nem elég a 72 órás SLA:** az A10 a *törlés* SLA-ja. Ha a törlést az FR-120 30 éves megőrzési kötelezettsége miatt **megtagadjuk**, a 72 órás törlési SLA **nem alkalmazandó** — de az Art. 12(4) szerinti válaszadási kötelezettség akkor is fennáll.

SYN (2026-08-13): `withdraw_subject` kiállítja mindkét artefaktumot; `refuse_erasure` csak a 12(4) levelet (a genetikai tartalom marad); `GET /v1/compliance/dsr` az `E-DSR-OVERDUE` riasztás.

## 1.4 S054 az FR-120 forrásoszlopában is

`[V]` Irish DPC Case Studies 2025, Case Study 12 (pin: `ie-dpc-case-studies-2025.pdf`, p. 20): foglalkozás-egészségügyi szolgáltató, egészségügyi adat törlési kérelme. A szolgáltató **megtagadta** Art. 9(2)(h) + az Orvosi Kamara vizsgálati jogköre miatt; a megőrzési politika **hét év** az utolsó kapcsolat után. A DPC: a megtagadásnak volt érvényes jogalapja. Ugyanakkor az Art. 12(3) **egy hónapos válasz** elmaradt — ez volt a jogsértés.

KEY TAKEAWAYS `[V]`: a törléshez való jog nem abszolút; a megőrzési kötelezettség megalapozhatja a megtagadást; **akkor is** válaszolni kell a kötelező határidőn belül.

`[I]` Ez ugyanaz a jogi minta, mint a PCE FR-120 (30 év) vs FR-110 (visszavonás) feszültsége. Az S054 ettől a naptól az **FR-120** forrásoszlopában is szerepel, nem csak az FR-110-ében.

---

# 2. OQ-06 — Osztály páronként · **javaslat az RA felé**

Ez a szakasz **nem** pecsételi az OQ-06-ot. Az A.4.1 tábla nyitott marad.

## 2.1 A jogszabályi teszt

`[V]` MDR Annex VIII Rule 11 (S020, spec §4.1): a diagnosztikai vagy terápiás döntéshez információt szolgáltató szoftver **IIa**, kivéve ha a döntés hatása:

- **halál vagy irreverzibilis egészségromlás** → **III**
- **súlyos egészségromlás vagy sebészi beavatkozás** → **IIb**

`[V]` MDCG 2021-24 (S061, pin `mdcg-2021-24-en.pdf`): a Rule 11 ábrán „death or irreversible deterioration of health” / „serious deterioration in health or surgical intervention”. Egy példa-sor: „III — death or an irreversible deterioration of a person's state of health”. A **„serious”** szót ez a példatár a III-ág halál/irreverzibilis fordulatához **nem** toldja be. Az MDCG 2019-11 Rev.1 (S005) „irreversible **serious** deterioration” betoldása ezért **nem** S061-en áll; az RA-nak a két MDCG-t együtt kell olvasnia.

`[V]` MDCG 2019-11 Rev.1 (S005): modulonkénti értékelés; egy adminisztratív platformba ágyazott orvosi modul **csak azt a modult** vonja az eszköz-rezsimbe, **feltéve, hogy a határok és a függőségek dokumentáltak.**

`[I]` A PCE CI-invariánsok (`LIVE_CDS is False`, zárt 45 kulcsos allow-list, 15-elemű deny-list, `! grep MedicationEntry src/pce_report`, `! grep pce_gateway.pipeline src/pce_report`) **pontosan ez a dokumentáció**, és gépileg ellenőrzött. Ez nem pecsételi az osztályt.

## 2.2 A kritikus megkülönböztetés: F1+ statikus ≠ L4-live

| | F1+ statikus (`FR-400-STATIC`) | L4-live (`FR-400-LIVE`) |
| --- | --- | --- |
| Kimenet | **Mind az N** guideline-sor a vizsgált génekre | A beteg gyógyszerlistájára **szűrt** lista |
| Tudja-e, mit szed a beteg? | **Nem** (`medications_applied_to_recommendations: false`) | Igen |
| Legrosszabb döntés a kimenet **önmagában** | Nincs — nem mondja meg, melyik sor releváns | Konkrét szer folytatása/elhagyása |

`[I]` **Ez a különbség dönti el az osztályt, nem a gén.** A statikus kimenet funkcionálisan a CPIC-tábla kinyomtatása a beteg genotípusa mellé. A live kimenet terápiás állásfoglalás.

## 2.3 Páronkénti javaslat az **L4-live** útra

A „legrosszabb kimenet” **nem** pecsételt CPIC-halálállítás. A D.1 csak a DPYD–fluoropirimidinre ír S=5 „súlyos toxicitás”-t, **nem** „halál”-t. A többi pár D.1-ben nincs sor; a spec `[NEEDS VERIFICATION]` az RA felé. Az alábbi Rule 11 oszlop **gyártói javaslat** `[I]`, nem forrásolt klinikai kimenet.

| Pár | Ami a repóban van | Rule 11 javaslat `[I]` | 62304 javaslat |
| --- | --- | --- | --- |
| **DPYD – 5-FU / kapecitabin** | R-007 S=5 „súlyos toxicitás”; CPIC pair_view A | **III** — mert a saját D.1 S=5 + Rule 11a III-ág együtt IIa-ként nem védhető live-ban | **C** |
| **CYP2C19 – clopidogrel** | PREPARE-12 pair_view; D.1-ben nincs pár-sor | **III** javaslat; RA dönt. Az MDCG „serious” betoldása (S005 vs S061) **nem** pecsételi ki a III alól | **C** |
| **CYP2D6 – kodein** | CPIC opioid 2020 PDF pin (S048); D.1-ben nincs „halál” | **III** javaslat; a guideline pinelt, a III-ág az RA-é | **C** |
| **HLA-B\*15:02 – karbamazepin** | CPIC pair_view A (`carbamazepine`); D.1-ben nincs kimenet | **III** javaslat | **C** |
| **TPMT / NUDT15 – tiopurin** | TPMT a PREPARE-12-n; NUDT15 **nincs** a v1 default panelen | **IIb–III**, RA dönt | **C** |
| Minden más PREPARE-12 pár | Dóziseltérés, monitorozás, terápiás kudarc — D.1-ben nincs S=5 | **IIa** (default) | **B** |

## 2.4 Stratégiai következtetés

`[I]` **Az F3 „IIa CE” cél a fenti öt párra live-ban nem védhető.** Aki a Notified Body elé IIa-ként viszi be a DPYD–fluoropirimidin live párosítást, azt vissza fogják küldeni — és a saját D.1 kockázati regisztere (S=5) lesz ellene a bizonyíték.

Két út van:

**(a) IIa-safe párlista az első live kiadáshoz.** Az L4-live indul, de a fenti öt pár **kikapcsolva** marad; a rendszer ezekre statikus szöveget ad (F1+ viselkedés) és explicit „ehhez a párhoz élő párosítás nem elérhető, konzultáljon klinikai farmakológussal” jelzést. Osztály: **IIa**. 62304: **B**. A timeline tartható.

**(b) L4-live teljes párlistával → Class III.** Notified Body III-as útvonal, MDR Art. 62 klinikai vizsgálat valószínű, **+18–24 hónap** `[E]` és nagyságrenddel nagyobb dosszié.

**Javaslat: (a).** Ez termékdöntés, amely a szabályozási döntést de-riszkeli. A kikapcsolt öt pár nem üres hely: ezek adják a szakmai hitelt, ha a lelet **megmondja, hogy tudja, hogy nem tudja.**

`LIVE_CDS` a repóban **false**. Az (a) kill-switch **megvan** (`src/pce_cds/policy.py`, `IIA_SAFE_BLOCK=true`). Az (a) az *első live kiadás* termékdöntése; a pecsét a flaget billenti, nem a csövet írja újra.

## 2.5 Amit az RA-nak el kell döntenie (és amit ez a melléklet nem dönt el)

1. A TPMT/NUDT15 IIb vagy III?
2. Az MDCG 2019-11 „irreversible **serious**” betoldása mentesíti-e a CYP2C19–clopidogrel párt a III alól, szemben az S061 „death or an irreversible deterioration” szövegezéssel?
3. Elfogadja-e a Notified Body az (a) opció „kikapcsolt pár” konstrukcióját, vagy az intended purpose-ban a pár puszta említése is behúzza az osztályt?

`[A]` Ha az RA **2026-10-31-ig** nem dönt, a fejlesztés az **(a)** opció szerint halad — mert az (a) az (b)-be bármikor felfejleszthető, fordítva nem.

---

# 3. OQ-05 — Az F1+ nem-MDSW pozíció · **javaslat a counsel felé**

Ez a szakasz **nem** pecsételi az OQ-05-öt. Az OQ-05 **ELŐTERJESZTVE** marad.

## 3.1 Amit a v1.2 jól kérdez, és amit rosszul

Az OQ-05 jelenlegi kérdése (A.8): védhető-e a nem-MDSW, ha a kimenet gén-szintű guideline-szöveget tartalmaz gyógyszerlista nélkül. `[I]` Ez még mindig tágabb, mint a kód tényleges kimenete. A counsel „gyógyszerajánlást tartalmaz-e?” olvasatra **nemmel** fog válaszolni.

A helyes, szűk, eldönthető kérdés:

> **Az a szoftverkimenet, amely a vizsgált génekre a teljes, szűretlen, verziózott guideline-táblát nyomtatja ki a beteg diplotípusa mellé — anélkül, hogy ismerné vagy feldolgozná a beteg gyógyszerlistáját — a Rule 11 értelmében „információ, amelyet diagnosztikai vagy terápiás döntéshez használnak”, vagy referenciaanyag?**

## 3.2 Az érvek, mindkét irányban

**Nem-MDSW / Rule 11c Class I mellett:**

1. `[I]` **Nincs beteg-specifikus szelekció.** Két azonos genotípusú beteg azonos leletet kap, akkor is, ha az egyik semmit nem szed, a másik tízféle szert.
2. `[V]` **A modulhatár gépileg bizonyított.** Zárt allow-list 45 kulcsra, 15-elemű deny-list nested kulcson is, `LIVE_CDS is False` CI-assert, öt izolációs grep (MedicationEntry, medication_entry, pce_gateway.pipeline, pce_shadow, pce_cds a `pce_report`/`pce_clinical` ellen), **124** zöld teszt. MDCG 2019-11 Rev.1 a modulonkénti értékeléshez dokumentált határokat követel. A `pce_cds` a dobozban van; az F1+ processzuson a CDS továbbra is 404.
3. `[V]` Az aláíró a labor orvosa (FR-490); a `dose_mg` tiltott token.

**IIa mellett:**

1. `[S]` A Rule 11a küszöb tág: nehéz olyan klinikai szöveget elképzelni, amit *soha* nem használnak döntéshez. (Bristows-típusú kommentár **nincs** pinelve ebben a repóban — L4, nem S-szám.)
2. `[V]` Az MDCG Rev.1 után a Class I MDSW sáv keskeny, de **nem üres**: Rule 11c létezik; Rev.1 Annex IV új Class I példát adott (VC-04, **nem** VC-03).
3. `[I]` Az „az orvos dönt” érv az FDA 2022-es CDS guidance logikája, nem az MDR-é. Erre nem szabad építeni (NG-07, VC-11).

## 3.3 Javasolt counsel-kérdés formátum

Három **igen/nem** kérdés, mindegyikhez a kód mint melléklet. A pecsét továbbra is Igen / Nem / Feltétellel (OQ-05 V. szakasz).

| # | Kérdés | Melléklet |
| --- | --- | --- |
| **Q1** | A §3.1 szerinti kimenet Rule 11 hatálya alatt áll, vagy Rule 11c Class I? | `tests/test_report.py`, `schema.py` allow-list, példa-lelet |
| **Q2** | Ha Rule 11 alatt áll: a beteg-specifikus szelekció hiánya elegendő-e az **IIa alatti** besoroláshoz? | ugyanaz |
| **Q3** | Ha a válasz Q1-re „Class I”: elegendő-e a jelenlegi CI-invariáns-készlet az MDCG Rev.1 „dokumentált határok és függőségek” követelményéhez? | `.github/workflows/ci.yml` |

## 3.4 A biztonságos alapértelmezés, amíg nincs pecsét

`[I]` **Haladj úgy, mintha Class I MDSW volna — ne úgy, mintha nem lenne eszköz.**

Indoklás:

- Class I esetén **nincs Notified Body**, tehát az MDCG 2025-6 szerint **nem** magas kockázatú AI-rendszer. Az AI Act 2028-08-02-i tervezési határidő ettől a Class I pozíciótól **nem** indul el (VC-09: a dátum `[NEEDS VERIFICATION]`).
- A Class I terhe: technical file, ISO 14971, PMS, gyártói nyilatkozat, regisztráció. `[E]` Ez **3–5 hónap** munka egy meglévő QMS mellett; D.1, A melléklet, teszt-lefedettség **már** a repóban van.
- Ha a counsel utóbb IIa-t mond, a Class I dosszié **beszámít** az IIa dossziéba. Ha „nem eszköz”-ként haladtok és a counsel IIa-t mond, nulláról kezditek.

Ez a legolcsóbb visszafordítható pozíció. **Nem** dönti el az OQ-05-öt, és **nem** írja felül az A.6 elemzést (élő PGx-terápia nem 11c).

---

# 4. OQ-16 — k és a ritka-diplotípus küszöb · **javaslat a DPO felé**

Ez a szakasz **nem** pecsételi az OQ-16-ot. Az A14 `k ≥ 5` és a 0,5% **marad `[ASSUMPTION]`**, amíg a DPO nem pecsétel.

## 4.1 Amit a kutatás hozott — és ami megdönti a k≥5 *indokolatlanságát*

| Forrás | Küszöb | Kontextus | Pin |
| --- | --- | --- | --- |
| `[V]` **EMA** űrlap-utasítás | **9%** re-azonosítási kockázat (**risk = 0,09**) | Policy 0070 / PRCI közös mondat | S059 `ema-anonymisation-report-form-instructions.pdf` p. 7/11 |
| `[V]` **Health Canada PRCI** teljes útmutató | **risk=0,09** **és** cél-cellaméret **11 beteg** | Klinikai adat publikálás | S060 `health-canada-prci-guidance-document.html`: *„Adopting a risk threshold of risk=0.09 equates to a target cell size of 11 patients.”* Ugyanott: *„Health Canada encourages adopting a 9% re-identification risk threshold (risk=0.09).”* Profiloldal: S060-profil. |
| `[V]` **WP29 05/2014** | k-anonimitás technika; **k értéket nem ír elő** | EU útmutató | S053 |
| `[V]` **EDPB 01/2025** | álnevesített adat személyes adat marad | EU útmutató | S052 |
| `[V]` **California DHCS DDG V2.2** | numerátor **< 11** egyén **vagy** nevező **< 20 000** | US állami egészségügyi aggregátum-közlés | S062 `dhcs-ddg-v2-2.pdf` (2022-12-06, 71 oldal). Élő dhcs.ca.gov 2026-08-13 Incapsula HTML; pin: Wayback. A DHCS oldal most **v3.0**-t jelöl utódnak — v3.0 **nincs** pinelve. |
| `[S]` El Emam irodalmi áttekintés | publikált cellaméret-küszöbök **3–30** között | Általános | **nincs pin** |
| `[S]` HHS | **nincs univerzális számküszöb** a „very small” fogalomra | HIPAA expert determination | **nincs pin** |

`[V]` A Health Canada **nem** hagyja a 11-et levezetésnek: a 0,09-et **szó szerint** 11 fős cél-cellára fordítja. Az EMA S059 csak a 0,09-et mondja; a k=11 a kanadai primerben áll.

`[I]` Ez **nem** EU-s k-előírás (WP29 továbbra sem ad számot). A k≥5 ezért a publikált egészségügyi *cellaméret-precedens* (HC 11, DHCS 11) **alatt** van. Nem jogsértés, de a DPO-nak indokolnia kell, miért nem ezt a precedenst alkalmazza.

## 4.2 A 0,5% küszöb: feltevésből levezetéssé

`[I]` A jelenlegi 0,5% önkényes szám. Levezethető.

Ha az intézménynek **N** F1s-be bevont betege van, és egy diplotípus populációs gyakorisága **f**, akkor a várható cellaméret **N · f**. A k-követelmény teljesüléséhez:

```
N · f ≥ k        ⟹        f ≥ k / N
```

| Intézményi N | k = 5 → min. f | k = 11 → min. f |
| --- | --- | --- |
| 500 | 1,00% | 2,20% |
| 1 000 | 0,50% | 1,10% |
| 2 200 | 0,23% | **0,50%** |
| 5 000 | 0,10% | 0,22% |
| 10 000 | 0,05% | 0,11% |

`[I]` **A 0,5% pontosan akkor helyes, ha k = 11 és N ≈ 2 200.** Kisebb intézménynél túl megengedő, nagyobbnál fölöslegesen szigorú.

## 4.3 Javaslat a DPO-nak

**Ne fix számot kérj tőle. Kérj politikát.** Az A14 pecsétig **nem** íródik át.

| Paraméter | Javaslat `[A]` a DPO felé | Indoklás |
| --- | --- | --- |
| **k** | **k ≥ 11** a `diplotípus × ATC5` cellára; **k ≥ 5** abszolút padló minden más cellára | S060 cél-cella 11 `[V]`; S059 0,09 `[V]`; padló = mai A14 |
| **Ritka-diplotípus küszöb** | **Számított:** `f_min = k / N_intézmény`, negyedévente újraszámolva | Megszünteti az önkényes 0,5%-ot |
| **Nevező-minimum** | Egyetlen aggregátum sem publikálható **N < 20 000** nevezővel | S062 DHCS DDG V2.2 `[V]` — **nem** EU-norma; a DPO elvetheti |
| **Ha `N · f < k`** | **Drop**, nem durvítás — a durvítás ATC-szinten a párosítást öli meg (R-020) | E.3.1 |
| **Felülvizsgálat** | A `f_min` az intézményi N változásakor újraszámol; a gateway a `frequency-config.v0.json`-ból olvassa | FR-461 |

## 4.4 A kompromisszum, amit ki kell mondani

`[I]` k = 11 mellett a G3 ≥90% recall **el fog esni** kis intézménynél. Egy 1 000 fős F1s-kohorszban k=11 azt jelenti, hogy csak az **1,1% feletti** gyakoriságú diplotípusok mérhetők.

**Ez nem hiba, hanem a mérés valós felbontása.** A helyes reakció nem a k csökkentése, hanem:

- a G3 küszöb **rétegzése**: „≥90% recall a mérhető cellákon; a nem mérhető cellák aránya külön jelentendő”,
- vagy **több intézmény** bevonása, hogy N nőjön.

Az FR-461 monitor már negyedévente jelenti a drop-arányt a DPO-nak (spec A14 / OQ-16 I.4). Ezt ki kell egészíteni a **„nem mérhető cella” aránnyal**, mert az a G3 valódi korlátja.

---

# 5. F-14 — Árazási sáv · **levezetés, nem lista**

Kanonikus fájl: [Sales/pricing.md](Sales/pricing.md). A spec FR-katalógusába **nincs** Ft-listaár.

## 5.1 Horgonyok

| Horgony | Érték | Típus |
| --- | --- | --- |
| YouScript provider-előfizetés | **365 USD/fő/év** | `[V]` S033; urllib pin 403, WebFetch 2026-08-13 |
| YouScript licencforma | Per User, Site-Based | `[V]` S034 SMART pin |
| Semmelweis / T-Systems, MedSolution keret | **816.636.406 Ft** nettó | `[V]` S056, S057 — **teljes HIS**, nem PGx |
| Zala Szent Rafael + Keszthely / Asseco, MedWorkS karbantartás | **~88,3 M Ft / 12 hó, 2 kórház** | `[R]` S058 — EKR body **nincs** pinelve |
| Genetix DrugMap | **499 000 Ft** | **UNVERIFIABLE** VC-10 |
| SYNLAB MyPGx / Medicare Zrt. árbevétel / HU magán EBITDA / EUR/HUF · USD/HUF | — | **nincs pin** ebben a repóban; **nem** `[V]` |

A vázlat 115 000 Ft YouScript-átváltása **nincs** MNB-pinelve; a pricing.md ezt `[ASSUMPTION]` FX-ként viszi.

## 5.2 Levezetés `[E]` / `[I]`

**Klinikus-ülőhely `[Yc]`.** A YouScript 365 USD a padló-analógia. Két ellentétes korrekció: a magyar fizetőképesség (lefelé), a PCE funkció-terjedelme — öt modul, consent-kapu, 30 éves audit, callability, magyarázat-generátor (felfelé). `[E]` Ezek nagyjából kioltják egymást.

> **`[Yc]` = 120 000 – 480 000 Ft / felíró / év, közép 240 000 Ft.** `[E]`
> Érvelés a vevő felé, *ha* a DrugMap 499 e Ft áll (VC-10): **240 e Ft/év ≈ egy DrugMap-vizsgálat fele.** Ez összehasonlítás, nem PCE-ár.

**Platform-alapdíj `[Yp]`.** Tipikus B2B SaaS alapdíj–ülőhely arány kis telephelyen 1–2× `[E]`.

| Telephely | Ülőhely-bevétel (240 e Ft-tal) | Platform-alap `[Yp]` |
| --- | --- | --- |
| 20 felíró | 4,8 M Ft | **6–10 M Ft** |
| 50 felíró | 12 M Ft | **10–18 M Ft** |
| 100+ felíró | 24 M Ft+ | **15–35 M Ft** |

**Felső korlát:** a Zala-ügylet `[R]` 88,3 M Ft/év két kórházra ⇒ ~44 M Ft/kórház **teljes HIS**-karbantartásra. `[I]` Egy szakmodul, amely ennek több mint 2/3-át kéri, elveszti a beszerzést. A Semmelweis-keret `[V]` 816,6 M Ft **36 hónapra** — nem éves PGx-plafon.

> **Szabály `[I]`:** `[Yp]` ≤ a telephely teljes HIS-költésének 40%-a, ha a HIS-költés ismert. Ez adja a 35 M Ft plafont mint **tárgyalási** tetőt, nem mint listaárat.

**Megfizethetőségi ellenpróba** (a vázlat Medicover/EBITDA számai **nincsenek pinelve** — a következtetés a sáv *alakjára* áll, a 29,1 mrd Ft-ra nem):

> `[I]` **Kritikus javítás: ~15 felíró alatt nincs platform-alapdíj. Csak ülőhely.** E nélkül a Sales-csomag alsó sávja eladhatatlan, és pont a Phase-1 célcsoportot zárja ki.

## 5.3 A `[Y*]` placeholderek feloldva — mind `[ESTIMATE]`

| Placeholder | Érték | Alap |
| --- | --- | --- |
| `[Yc]` klinikus/év | **120–480 e Ft**, közép 240 e | YouScript analógia + teszt-ár arány `[E]` |
| `[Yp]` platform/év | **0 Ft < 15 felírónál**; 6–35 M Ft felette | HIS-plafon 40%-a `[I]` + megfizethetőség |
| `[Ys]` további telephely/év | **2–8 M Ft** | site-based analógia `[E]` |
| `[Y0]` / `[Yi]` integráció, egyszeri | **az első éves díj 20–50%-a** | egészségügyi IT norma `[S]` |
| `[Yl]` labor white-label tenancy/év | **4–25 M Ft** + per-report komponens | OQ-03 függvénye `[E]` |
| `[Ya]` F2/F3 aktiválási felár | **+15–40%** az alapon | meglévő vevő alsó, új logó felső `[E]` |
| `[Yh]` HIS-vendor | `[Yp]` + `[Yi]`, viszonteladói marzs **20–30%** | `[E]` |
| `[Ysh]` shadow/kutatási tenancy | **0 Ft** | Ez a gyártó saját validációs igénye (G3). Nem termék. Ne számlázd. |

## 5.4 Szerződéses paraméterek `[S]`

Támogatás/karbantartás: a licencdíj **15–22%**-a évente. Éves emelés **3–8%**. Futamidő **3–5 év**. Nem megfigyelt PCE-szerződés.

## 5.5 Amit ki kell mondani a Sales-csomagban

`[I]` **Mind a nyolc érték `[ESTIMATE]`, egyetlen sem megfigyelt PCE-tranzakció.** Tárgyalási horgony, nem piactisztító ár. Az első három aláírt szerződés után újra kell számolni — akkor lesz `[V]`.

`[I]` A publikálandó szám **egy**: a klinikus-ülőhely. A platform-alapdíj maradjon ajánlatkérés-alapú, mert a 0-tól 35 M Ft-ig terjedő sáv listaárként hiteltelen.

---

# 6. Összefoglaló — mi zárult, mi vár kire

| Tétel | Státusz | Kire vár | Ha nem érkezik döntés |
| --- | --- | --- | --- |
| **S055** | **LEZÁRVA** `[V]` | — | FR-110 kiegészítés a §1.3 szerint, két artefaktum — **kódban megvan** |
| **OQ-06** | Javaslat kész | RA | `[A]` 2026-10-31-ig: **(a) IIa-safe párlista**, az öt magas pár live-ban kikapcsolva |
| **OQ-05** | Javaslat kész | Counsel | `[A]` **Class I MDSW**-ként haladni — a legolcsóbb visszafordítható pozíció |
| **S060** | **LEZÁRVA** `[V]` | — | Health Canada PRCI: risk=0,09 **és** cél-cella 11 |
| **S062** | **LEZÁRVA** `[V]` | — | DHCS DDG V2.2: numerátor <11 vagy nevező <20 000. Nem EU-norma. |
| **OQ-16** | Javaslat kész | DPO | S060/S062 `[V]` háttér. A14 k≥5 / 0,5 % `[ASSUMPTION]` **változatlan**. |
| **F-14** | Levezetve `[E]` | Ügyvezetés | Publikáld a `[Yc]` 240 e Ft-ot; `[Yp]` ajánlatkérésre; **15 felíró alatt nincs alapdíj** |

## 6.1 A három legfontosabb következtetés

1. **Az F3 „IIa” cél az öt magas kockázatú páron live-ban nem védhető** (§2.4). A megoldás termékdöntés, nem jogi: IIa-safe párlista.
2. **A k≥5 az egészségügyi cellaméret-precedens alatt van.** A Health Canada PRCI `[V]` 11 fős cél-cellát mond a 0,09 mellé (S060). A DHCS DDG V2.2 `[V]` 11-es numerátort és 20 000-es nevezőt (S062). A 0,5% matematikailag levezethető (§4.2), de eljárásilag továbbra is `[ASSUMPTION]`, amíg a DPO nem pecsétel; az A14 ezért **nem** változik.
3. **A jelenlegi árszerkezet kizárja a Phase-1 célcsoportot** (§5.2). 15 felíró alatt platform-alapdíj nélkül kell menni.

## 6.2 Amit nem ellenőriztem / hátravan

- A DHCS **v3.0** (a nyilvános reporting-oldal szerint a V2.2 utóda) **nincs** pinelve.
- A HU magánegészségügyi EBITDA-marzs és a Medicover/Medicare árbevétel **nincs** pinelve.
- Egyetlen `[Y*]` érték sem megfigyelt PCE-tranzakció.
- A DPYD „letális”, CYP2C19 stent-trombózis, CYP2D6 gyermekhalál, HLA-B\*15:02 SJS/TEN halál **nincs** a D.1-ben; az OQ-06 III-javaslat `[I]`, nem `[V]` klinikai kimenet.
- MDCG 2025-6 / AI Act Class I ↔ magas kockázatú AI: a §3.4 állítás `[I]` a meglévő spec-olvasaton; a 2025-6 PDF **nincs** újrapinelve ebben a körben.
