# Piaci csomagok — HU / EU / US (flag, nem három termék)

| | |
| --- | --- |
| **Iktató** | PCE-SALES-MKT / v1.2 |
| **Szabály** | Egy kódbázis. `MARKET_PACK` + modul-licencek. Feloldás = change-control + minősítés, nem hotfix. |
| **Nem** | FDA CDS guidance átmásolása az MDR alá. US-pecsét nélkül F2-t US-ben sem kapcsolunk. |

A vevő azt kéri: „működő F1, F1s, F2, F3”. A válasz: **a rendszer ez**. Amit a szerződés ad: melyik flag **true** ezen a telephelyen.

---

## Flag-mátrix (default)

Jelölés: **ON** = a modul a rendeltetése szerint fut. **LOCK** = a kód megvan, klinikai UI / élő kimenet tiltva (FR-470). **N/A** = a piac joga nem ezt a kaput kéri.

| Modul / kapu | **HU** | **EU** (nem HU) | **US** |
| --- | --- | --- | --- |
| F1+ L4-static lelet | ON, ha OQ-05 IGEN; különben LOCK→IIa | u.a. (MDR) | ON csak US counsel szerint; default LOCK, amíg OQ-17 |
| F1s shadow + HITL | LOCK→ON OQ-15+16 után | u.a. (GDPR/DPIA a helyi DPO) | US IRB / HIPAA + US counsel; default LOCK |
| F2 élő CDSS (in-house) | LOCK; ON csak REG-011 + intézmény | LOCK; ON csak MDR in-house a *telepítő* tagállamban | LOCK; US in-house **nem** MDR-in-house. OQ-17 |
| F3 élő CDSS forgalom | LOCK; ON CE IIa után | LOCK; ON CE IIa után | LOCK; ON 510(k) / De Novo / más FDA út után |
| `LIVE_CDS` | compile/license **false** amíg F2/F3 ON | u.a. | u.a. |
| FR-100 2008/XXI kapu | **ON** (kötelező) | N/A mint HU tv.; helyi genetikai jog `[NEEDS VERIFICATION]` | CLIA-lab + HIPAA; nem 2008/XXI |
| EESZT írás | **OFF** (NG-05) | N/A | N/A |
| ISO 9001 2026-09-30 | HU fejlesztői jogállás (OQ-01) | Nem 9/C. §; ISO 13485 F2/F3-hoz | QSR / QMSR a device-pályán |
| LLM a klinikai úton | OFF (FR-700) | OFF | OFF |
| Saját genotípus-hívás | OFF (NG-01) | OFF | OFF (YouScript/TSI 510(k) minta) |

A HU csomag **EU + magyar kapuk**. Nem külön motor.

---

## Mit jelent a „kikapcsolt funkcionalitás”

1. A F2/F3 **képernyő és API** a telepítésben látszik **lakattal** (licenc + build flag). A vevő látja, hogy a rendszer teljes.
2. A L4-live motor F1s-ben futhat (felíró **nem** látja), ha a shadow csomag ON.
3. Admin **nem** billentheti `LIVE_CDS=true`-ra configgal. Csak signed release + REG-010/011 / FDA clearance (FR-470).
4. Piaci csomagváltás (HU→US tenancy) **nem** egy checkbox a klinikának. Új tenancy, új intended purpose, új dosszié.

---

## Átminősítés (feloldási záradék)

| Lépés | HU / EU | US |
| --- | --- | --- |
| 1 | F1s gold set (G3) | u.a. + US klinikai adat, ha az FDA kéri |
| 2 | ISO 13485 + 62304 + 14971 (REG-030) | QMSR + 62304 |
| 3 | F2: in-house dokumentáció **vagy** F3: NB, CE | 510(k) / De Novo / egyéb — **OQ-17** |
| 4 | `LIVE_CDS=true` signed build, A.3 intended purpose | US intended use a 510(k) szerint |
| 5 | Szerződés: modulaktiválási díj `[Ya]` | u.a. |

Amíg 4 nincs: a sales **nem** mondja, hogy „jövő héten bekapcsoljuk a riasztást”.

---

## OQ-17 — US (nyitott, nem blokkolja a HU/EU licencet)

Kérdés a **US counselnek**, nem az EU OQ-05-nek:

> A PCE **ugyanazon** bináris F2/F3 kimenete (beteg–gyógyszer, felírás-pillanat) eszköz-e az FD&C Act / 2022 CDS guidance szerint, és milyen premarket út kell? A genotípus-hívás **kint** marad (NG-01).

**Tilos:** EU-s nem-MDSW (OQ-05) átvitele US-re, vagy US CDS „az orvos le tudja vezetni” átvitele MDR-re.

Státusz: **NYITOTT**. A US market pack F2/F3 default **LOCK**.

---

## Szerződési egy mondat

> A Vevő a PCE rendszert a `[HU|EU|US]` csomagban licenceli. A nem ON modulok a szoftver részét képezik, klinikai használatuk tiltott. Feloldás írásos aktiválással, a gyártó signed release-ével és az adott piac szabályozási feltételének teljesülésével.

---

## Ki fizet (B2B SaaS, nem viszonteladás)

YouScript/ActX *struktúra*-analogia: az intézmény a szoftvert fizeti; a labor genotípust ad. Publikus YouScript-tarifa: Per User / Site-Based + 365 USD/év lista. **Ágyszám-sávos enterprise árlista nincs nyilvánosan** — a PCE ezért nem másol kitalált ágyszám-táblát.

| Pénzmozgás | Ki → kinek | Mit fedez | Nem |
| --- | --- | --- | --- |
| **SKU-P** | Klinika / hálózat → gyártó | Platform, HIS-cső, F1+ (ha ON), F1s (ha ON), zárt F2/F3 kód | PGx-vizsgálat darabára |
| **Opcionális labor-tenancy** `[Yl]` | Partnerlabor → gyártó | Saját white-label render + aláíróhely (OQ-03) | A kórházi SKU-P viszonteladása |
| **REG-020 csatlakozó** | Integráció, díj 0 vagy a klinika viszi | Outside-call / VCF a *klinika* tenancyjére | A labor nem lesz PCE-viszonteladó |
| **Vizsgálat** | Labor → klinika (a labor árlistája) | A genotípus-hívás | Nem PCE-SKU |
| **F2/F3 `[Ya]`** | Klinika → gyártó | Élő CDS feloldás | CE/in-house/OQ-17 **előtt** tilos |

A licencmondat a megrendelőlapon: *„A Vevő a PCE platform prediktív és munkafolyamat-képességét licenceli (B2B SaaS). A partnerlabor nem viszonteladó. White-label tenancy külön `[Yl]`, OQ-03.”*

---

## Lakat mint sales-driver (FR-470) — előbb retesz, aztán `[Ya]`

A HU/EU v1 buildben a `LIVE_CDS` **compile-time false**. A demóban a F2/F3 képernyő **látszik, nem kattintható**.

| Szabad mondani | Tilos mondani |
| --- | --- |
| A vevő látja a teljes F1–F3 döntési fát; az élesítés gombja CE / in-house + licencmódosítás `[Ya]` | „YouScript-lakat”; „hétfőn kapcsoljuk”; ActX-szerű élő riasztás ma |
| Az ActX *klinikai* gatingje (villan, ha releváns szer) az **F2 viselkedés** analogiája, feloldás után | Hogy az ActX compile-time MDR-reteszt használ; hogy PDF→CDSS történetük primer |
| A lakat **először** Rule 11a védvonal (NG-07) | Hogy a lakat *csak* up-sell, ezért CE előtt is mehet a kártya |

„Bent van, addig is megy a riasztás” = forgalomba hozatal, ha MDSW. A `[Ya]` **nem** nyitja a lakatoz CE nélkül.

---

## Piaci analógia (SKU-P, nem pecsét)

A kórház/hálózat **szoftverlicencet** vesz; a labor diplotípust szállít. Ez a PCE SKU-P + outside-call. A lenti termékek **US/vendor** analogiák, nem EU-MDR precedens és nem a mi árlistánk.

| Analóg | Amit *igazol* `[V]` / `[R]` | Amit *nem* igazol |
| --- | --- | --- |
| **YouScript** | EHR-be ágyazott élő PGx-CDS (Epic/Cerner, SMART on FHIR). Katalógus: **Per User, Site-Based**. Nyilvános kiskereskedelmi megújítás: **365 USD / év / provider** (youscript.com, 2026-08-12). GenomeWeb (2014): más labor genotípusa is betölthető — outside-call analógia `[R]`. | Enterprise ágyszám-tarifa (nincs publikus tábla). Compile-time `LIVE_CDS` lakat. 39%/71% kórházi csökkenés (céges közlés, registryből kihagyva). A PMC 7195220 **nem** YouScript-cikk (polifarmácia-review). |
| **ActX** | Ma: labor-PDF riport **és** order-entry riasztás, ha van genomprofil és releváns gyógyszer (actx.com). A „villan, ha releváns szer” = **klinikai** gating (F2 viselkedés). | Hogy PDF-leletként *indultak*, majd CDSS-sé alakultak `[NEEDS VERIFICATION]`. Hogy a PCE FR-470 lakat = az ő modelljük. Az ActX élő riasztás **F2**, HU/EU-ban CE/in-house nélkül tilos (NG-07). |
| **Translational Software** | Lab-facing knowledge/API + white-label riport létezett. A 510(k) **elutasítás** után a US szolgáltatást leállították (GenomeWeb `[R]`): a FDA a betegre szabott, CPIC-alapú riportot nem fogadta el „könyvtárnak”. | Hogy az F1+ „önmagában hatalmas, biztonságos B2B piac”. Ellenkezőleg: **NG-01** (ne hívjunk diplotípust) és az OQ-05 maradék kockázat (gén-szintű terápiás szöveg lehet Rule 11a). |

A demó **lakatja** (FR-470) először **szabályozási** retesz, másodszor látható F2/F3 upgrade-út. Nem YouScript-feature-másolat. „Bent van, addig is megy a riasztás” = forgalomba hozatal, ha MDSW.

Részlet: [competitor-analogs.md](competitor-analogs.md). Irodalmi határ: [literature-boundary.md](literature-boundary.md).

---

## Árazási mátrix minta

A YouScript **publikus** sémája: egyéni provider-előfizetés (365 USD/év) + intézményi „site-based” (ár nélkül). A javasolt **Ft-sáv** [pricing.md](pricing.md) — **következtetés**, nem megfigyelt PCE-listaár. A megrendelőlapon a `[Y*]` marad (proposal-order §4). **Nincs** kitalált ágyszám-tarifa.

| Sáv | Ki fizet | PCE sor | YouScript/ActX analog (nyilvános) | Placeholder | Mikor számlázható élesen |
| --- | --- | --- | --- | --- | --- |
| **A. Platform** | Klinika / hálózat (SKU-P) | Éves intézményi licenc, market pack HU/EU/US | SMART: Site-Based; enterprise quote nem publikus | `[Yp]` — sáv **6–35 M Ft**/év (következtetés) | MSP + DPA + diplotípus-forrás. F1+ ON: OQ-05 *vagy* IIa/CE |
| **B. Klinikus-sáv** | Ugyanaz a vevő | Per-clinician / év (vagy /hó × 12) | YouScript provider **365 USD/év** lista (US, 1 fiók, nem EHR-enterprise) | `[Yc]` — sáv **120–480 e Ft**/év (következtetés) | Ugyanaz. Nem a 365 USD átvétele |
| **C. Telephely** | Ugyanaz | Extra site | Site-Based (ár nélkül) | `[Ys]` — sáv **2–8 M Ft**/év (következtetés) | Ugyanaz |
| **D. Indítás / HIS** | Vevő vagy SKU-H | Egyszeri integráció | Nincs publikus YouScript-tétel | `[Y0]` / `[Yi]` — a licenc **20–50%-a** (norma, `[ASSUMPTION]`) | Szerződés |
| **E. F1s shadow** | Vevő, ha a pack ON | A platform része vagy külön sor | Nincs YouScript-ár | `[Ysh]` vagy 0 (benne van) | OQ-15 + OQ-16 |
| **F. F2/F3 aktiválás** | Vevő | Előfizetés / aktiválási díj a **feloldott** élő CDS-re | ActX: élő order-alert a fizetett klinikai réteg (vendor). YouScript: az élő CDS *a* termék | `[Ya]` — **+15–40%** (következtetés), csak pecsét után | **Csak** CE / in-house / OQ-17 után. Nem demó-kapcsoló |
| **G. Labor tenancy** | Csak ha a labor *is* white-label tenancyt kér | Opcionális havidíj + volumensáv | ActX lab PDF reporting (vendor). TSI volt lab-API | `[Yl]` — sáv **4–25 M Ft**/év (következtetés) | REG-020. **Nem** viszonteladás. A mag-SKU a klinika |

**Tilos a mátrixban:** ágyszám-sáv kitalált árral; „a labor fizeti a platformot, a kórház ingyen kapja”; YouScript 365 USD mint HU listaár; a 6–35 M Ft mint *listaár*; F2 díj CE előtt. Részlet: [pricing.md](pricing.md).

G4: aláírt **rendszerlicenc** (A+B/C), nem három PDF.
