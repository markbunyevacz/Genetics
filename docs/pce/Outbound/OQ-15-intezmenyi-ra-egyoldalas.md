# Intézményi RA egyoldalas — Klinikai értékelési kérelem (OQ-15)

| | |
| --- | --- |
| **Iktató** | PCE-OUT-OQ-15 / v1.2 |
| **Dátum** | 2026-08-12 |
| **Státusz** | TERVEZET — küldhető; **nem** etikai engedély, **nem** hatósági bejelentés |
| **Feladó** | `[Gyártó neve]` (A9; név a fejlécben töltendő) |
| **Címzett** | Partner intézmény orvosigazgatója / intézményi RA / etikai bizottság |
| **Intézmény** | `[Partner intézmény neve]` |
| **Tárgy** | Kérelem az F1s (Shadow Mode) adatgyűjtés jóváhagyására |
| **OQ** | OQ-15 — **ELŐTERJESZTVE**; függ **OQ-16**-tól |

Tisztelt Orvosigazgató / RA / Etikai Bizottság!

Kérjük annak elbírálását, hogy az F1s shadow futtatás az Önök intézményében **milyen** jogi dobozba esik, és ennek alapján a futtatás **megkezdhető-e**. A gyártó *érve* alább van. **Nem** állítjuk, hogy az MDR 62. cikke alóli mentesség hatósági tény.

**Függés:** a shadow adat a gatewayen át megy. Az OQ-16 (DPO: anonim vs FR-115) nélkül F1s HIS-csatlakozás **nem** indul (F.2).

---

## I. Mi fut, és mi *nem* fut a rutin ellátásban

A gyártó a későbbi F2/F3 PGx-CDSS motort (**L4-live**: beteg–gyógyszer párosítás, fenokonverzió-alkalmazás) **háttérben** futtatja. Ez **ugyanaz** a motor, amely CE / in-house után élő döntéstámogatás lesz. A shadow **klinikai értékelési adatgyűjtés** a jövőbeli MDSW-hez — nem „titkos CDSS az F1-ben”.

A kezelőorvos a napi ellátásban **ebből semmit nem lát**.

Fizikai / build-szintű retesz (**FR-470**): az éles F1+ / F1s klinikai buildben a `LIVE_CDS` flag **compile-time false**. A szoftver **képtelen** felugró ablakot, CDS Hooks kártyát vagy éles riasztást adni a felírás pillanatában. A shadow hibája a HIS-t **nem** blokkolja (fail-open a felírásra, fail-closed a klinikai szivárgásra).

Ha a shadow kimenet bármely klinikai képernyőre kerül, az üzemmód **F2**, az F1+ rendeltetés hamis, és ez a kérelem érvénytelen.

---

## II. FR-450-BLIND — szekvenciális, reviewer-vak folyamat

A háttérben gyűjtött adatok validálása **nem** a vizit alatt történik. Az intézmény kijelölt szakemberei (`hitl_reviewer`, külön app / külön login) utólag, batchben (pl. havi) végzik a felülvizsgálatot.

**Nem** kettős vak (double-blind): a motor kimenete a rendszerben megvan; a reviewer az 1. lépésben nem látja.

1. Az orvos megkapja az **anonimizált** (vagy a DPO szerinti álnevesített) esetet: gén + csonkolt gyógyszercsoport (ATC3/4) + negyedév. Nincs név, TAJ, életkor, orvosnév, osztály.
2. Az orvos **előbb** meghozza a saját független szakmai döntését, és rögzíti (`CONTINUE` / `ALTERNATIVE` / `DOSE_CHANGE` / `INSUFFICIENT`).
3. A rendszer **csak a mentés után** fedi fel, hogy a shadow motor mit javasolt volna; a reviewer `AGREE` / `DISAGREE`.

A két lépés időbélyege immutábilis. A HITL **nem** a felíró napi UI.

---

## III. Klinikai háttér — PREPARE (S008), nem PCE-RWE

Az F1s **nem** a PREPARE újrafuttatása. A Lancet-vizsgálat a *preemptív 12-génes panel + DPWG szerinti felírás* klinikai hasznát mérte hét EU-országban. A shadow a **helyi** L4-live motor concordanciáját és a későbbi F2/F3 clinical evaluation *inputját* gyűjti (G3, HITL). Magyarország **nincs** a hét országban.

**Számok a közleményből** `[V]` Swen et al., Lancet 2023;401:347–356; doi:10.1016/S0140-6736(22)01841-4; NCT03093818:

| Tétel | Érték |
| --- | --- |
| Design | Nyílt, multicentrikus, klaszter-randomizált crossover |
| Helyszín | 18 kórház, 9 közösségi egészségügyi központ, 28 patika; AT, GR, IT, NL, SI, ES, UK |
| Enrollált | **6944** / 41 696 alkalmas (3342 beavatkozás, 3602 kontroll) |
| Panel | 50 germline variáns, **12 gén** (köztük CYP2D6, CYP2C19, DPYD) |
| Actionable DGI az index-gyógyszerre | **1558** beteg (második gatekeeping) |
| Primer kimenet | Klinikailag releváns ADR 12 héten: Liverpool definite/probable/**possible** + CTCAE **grade 2–5** |
| Actionable kar | **152/725 (21,0%)** vs **231/833 (27,7%)**; OR **0,70** (0,54–0,91); **p = 0,0075** |
| Teljes kezelt | 628/2923 (21,5%) vs 934/3270 (28,6%); OR 0,70; p < 0,0001 |

A „30%” az OR 0,70 (relatív esélycsökkenés), **nem** abszolút 30 százalékpont, **nem** p = 0,0034, **nem** „súlyos ADR” mint egyetlen címke.

**Kötelező forráskritika a címzett felé:** open-label; a hatás jelentős része grade 2; a Lancet levelei (Curtis; Rogers et al.; Van der Linden; Peñas-LLedó & LLerena) a haszon mértékét vitatják. A primer kimenet **nem** halálozás és **nem** ápolási nap. A PCE F1s **nem** méri újra a Lancet ADR-arányt, hacsak a helyi protokoll ADR-kimenetet is gyűjt — a v1.2 spec ezt **nem** írja elő.

**Mit indokol ez a kérelemben:** (1) az F2/F3 *későbbi* élesítésnek van független, peer-reviewed PGx-evidenciája (panel + guideline-vezérelt felírás); (2) az F1s a helyi motor HITL-validációja ehhez a dossziéhoz, a felíró nélkül. **Nem** indokolja, hogy a shadow Art. 62 alól mentes, és **nem** a PCE saját RWE-je.

---

## IV. Gyártói érv — és ami *nem* dőlt el

**Érv (nem tény):** mivel a szoftver kimeneteit az ellátó orvos nem látja, a szoftver **zéró hatást** gyakorol az *index* páciens kezelésére a felírás pillanatában. Az eljárás ezért a gyártó szerint közelebb áll az MDR Annex XIV szerinti **klinikai értékelési adatgyűjtéshez** és belső minőségbiztosításhoz, mint az MDR 62. cikke szerinti, emberen végzett klinikai vizsgálathoz.

**Ami nyitva marad (E.7, REG-090):**

- Az MDR 62. cikk hatóköre ettől még a **címzett** döntése. A „nincs hatás az index-kezelésre” **nem** automatikus mentesség.
- A shadow motor valós ellátási eseményen fut, a jövőbeli eszköz klinikai hasznának bizonyítására — ez lehet evaluation **vagy** vizsgálat (etikai engedély + hatósági bejelentés).
- In-house F2 (intézményen belüli élő CDSS) **más** jogi doboz, mint a gyártó felhőjében futó shadow. Ez a kérelem a **shadowról** szól, nem F2 élesítésről.

Kérjük a címzettet, hogy a lenti három közül válasszon — ne hagyja üresen a „nem vizsgálat” állítást aláírás nélkül.

---

## V. Döntés

- [ ] **JÓVÁHAGYVA mint klinikai értékelési / QA adatgyűjtés** — a shadow futtatás megkezdhető a csatolt protokoll és az OQ-16 DPO-döntés szerint; a címzett megítélése szerint **nem** MDR Art. 62 klinikai vizsgálat. (A címzett saját RA-eljárása szerint dokumentálandó.)
- [ ] **TOVÁBBÍTVA** etikai bizottsághoz / hatósági bejelentéshez mint **klinikai vizsgálat** (Art. 62+) — a shadow **nem** indul a vizsgálat engedélye nélkül.
- [ ] **ELUTASÍTVA** — indoklás: .................................................................................................
- [ ] **FELTÉTELLEL** — feltételek:

1. .................................................................................................
2. OQ-16 (DPO) státusz a jóváhagyáskor: IGEN anonim / FR-115 kötelező / folyamatban (a nem illő **húzandó**).

---

## VI. Aláírás

| | |
| --- | --- |
| Név | .................................... |
| Pozíció (orvosigazgató / RA / etikai bizottság elnöke) | .................................... |
| Intézmény | `[Partner intézmény neve]` |
| Dátum | .................................... |
| Aláírás / pecsét | .................................... |

**Mellékletek:** PCE-SPEC-v1.2 (FR-440, FR-450, FR-450-BLIND, FR-470, REG-090, §9.4); A.2; E.4, E.4.1, E.7; F.2; OQ-16 kérdőív (másolat vagy DPO-válasz); Swen et al., Lancet 2023;401:347–356 (S008) — a címzett saját példánya / PubMed 36739136.

*REG-090: az első HIS-csatlakozás előtt. Ez az egyoldalas kérelem, nem a vizsgálat teljes protokollja.*
