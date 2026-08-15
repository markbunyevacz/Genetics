# Árazás — megfigyelt tény vs következtetés

| | |
| --- | --- |
| **Iktató** | PCE-SALES-PRX / v1.2 |
| **Dátum** | 2026-08-13 |
| **Szabály** | A Ft-sáv **következtetés**, nem megfigyelt PCE-listaár. A spec FR-katalógusába **nincs** bemásolva. |
| **Nem** | Kitalált ágyszám-tarifa; YouScript 365 USD mint HU lista; DrugMap mint verifikált PCE-ár |

A vevő **rendszert** licencel (SKU-P). A labor a vizsgálatot számlázhatja; az nem PCE-ár.

---

## 1. Három mondat

Egyetlen **publikus** közvetlen versenytárs-ár létezik: YouScript provider-előfizetés **365 USD / év** (youscript.com, 2026-08-13 WebFetch: `$365.00`). A SMART Health IT katalógus Licensing & Pricing: **Per User, Site-Based** (pin: `Sources/market/smart-youscript-2026-08-13.html`). GenXys, OneOme, ActX, Coriell: nyilvános listaár **nincs** ebben a körben — contact-sales.

A magyar **plafont** odaítélt közbeszerzés adja, nem PGx-modul-ár. Semmelweis / T-Systems MedSolution keret **816.636.406 Ft nettó** (KÉ 2020/58; Semmelweis GFI 2020-04-07 pin). Zala Vármegyei Szent Rafael / Asseco MedWorkS karbantartás: a kutatás **~88,3 M Ft / 12 hó, két kórház**, hivatkozás **EKR001266472024**. Az EKR-portál ebben a környezetben karbantartási oldalt adott — az összeg **nincs** SHA-256 pinelve.

A javasolt PCE-sávok **mind következtetések**. Egy PGx-modul a fenti HIS-ügyletek **töredéke**. **15 felíró alatt nincs platform-alapdíj** (G §5.2). A publikálandó szám **egy**: a klinikus-ülőhely közepe. A `[Yp]` ajánlatkérés-alapú.

---

## 2. Megfigyelt (pin vagy ezen a napon olvasott)

| Tétel | Érték | Státusz | Forrás |
| --- | --- | --- | --- |
| YouScript 1 éves provider-megújítás | **365 USD** | `[V]` WebFetch 2026-08-13 (`$365.00`). urllib pin **403** | S033; `Sources/market/MANIFEST.json` YOUSCRIPT-PROVIDER-1Y `ok: false` |
| YouScript licencforma | Per User, Site-Based | `[V]` SMART pin | S034 |
| Semmelweis MedSolution keret | **816.636.406 Ft** nettó; 36 hó (2020-05-01–2023-05-01) | `[V]` Semmelweis GFI + eGov KÉ 2020/58 pin | S056, S057 |
| DrugMap 499 000 Ft | laborvizsgálat-lista, 2026-08-09 | **UNVERIFIABLE** ebben a repo-körben (VC-10) | S017 |
| EKR001266472024 ~88,3 M Ft / 12 hó | MedWorkS karbantartás, két kórház (kutatás) | `[R]` — EKR body **hátravan** | S058 |

A 816,6 M Ft a kutatás kerekítése a pinelt **816.636.406 Ft**-ra.

---

## 3. Javasolt sáv (következtetés, nem megfigyelt ár)

Kitöltés: a megrendelőlapon marad `[Yp]` / `[Yc]` / … — ez a tábla a **tárgyalási sáv**, nem ÁSZF.

| Sor | Sáv | Mire támaszkodik | Jelölés |
| --- | --- | --- | --- |
| Klinikus / év `[Yc]` | **120–480 e Ft**, közép **240 e Ft** | YouScript 365 USD; a kutatás ≈ **115 e Ft** átváltást használ (MNB közép **nincs** pinelve). Felső sáv: nagyobb funkció-terjedelem | alsó: analógia; Ft: `[ESTIMATE]` FX |
| Platform / tenancy / év `[Yp]` | **0 Ft 15 felíró alatt**; **6–35 M Ft** felette | HIS-plafon 40%-a `[I]`; megfizethetőség. A 0–35 M Ft listaárként hiteltelen — ajánlatkérés | `[ESTIMATE]` |
| További telephely / év `[Ys]` | **2–8 M Ft** | site-based analógia (SMART, ár nélkül) | `[ESTIMATE]` |
| HIS-integráció, egyszeri `[Yi]` | a licenc **20–50%-a** | egészségügyi IT norma, nem megfigyelt PCE-tétel | `[ESTIMATE]` |
| Labor white-label tenancy `[Yl]` | **4–25 M Ft/év** | per-report komponenssel; nem viszonteladás | `[ESTIMATE]` |
| F2/F3 aktiválási felár `[Ya]` | **+15–40%** | csak CE / in-house után (FR-470) | `[ESTIMATE]` |
| HIS-vendor `[Yh]` | `[Yp]` + `[Yi]`, marzs **20–30%** | `[E]` | `[ESTIMATE]` |
| Shadow/kutatási tenancy `[Ysh]` | **0 Ft** | G3 validáció; nem termék. Ne számlázd. | `[I]` |

**Tilos mondani:** „a PCE listaára 6–35 M Ft”; „365 USD = a HU klinikus-díj”; „a DrugMap 499 e Ft a mi árunk”; „Medicover 29,1 mrd Ft” (nincs pin).

Levezetés: [G §5](../G-open-items.md). Mind a nyolc `[Y*]` **nem** megfigyelt PCE-tranzakció. Az első három aláírt szerződés után újraszámolni.

### Orvosigazgatói érv (nem PCE-árlista)

Ha a DrugMap teszt **499 000 Ft** (VC-10, egy forrás) áll, a klinikus-sáv **alja** (120 e Ft/év) annak **kb. negyede**. Ez összehasonlítás egy laborvizsgálat-árral, nem SKU-P számla.

---

## 4. Ami a sáv mögött a repóban van (nem feltételezés)

Öt futó modul (a `pce_shadow` és a `pce_hitl` egy validációs cső):

| Csomag | A kódban | Ami *nincs* túlállítva |
| --- | --- | --- |
| `pce_clinical` | Hozzájárulás-kapu (FR-100), append-only audit (`prev_hash`, UPDATE/DELETE tiltva), FR-710 magyarázat | A **30 éves** megőrzés spec FR-120; a SYN SQLite nem időzít 30 évet |
| `pce_report` | Verziózott **CPIC** pair/recommendation (PREPARE-12 pin), callability, PDF, FHIR STU3 Bundle; F1+ matcher **ki**; `dpwg_version` + `fda_table_version` a B.4.1 JSON-on (ClinPGx DPWG pin + FDA Table 2-2 kivonat, külön URL, nincs szintetizált harmadik) | DPWG teljes HTML tábla nem a findings-ben (index + pin); lektorált HU DPWG-szöveg |
| `pce_gateway` | Intézményi anonimizálás, k-cella, 7 karakteres hatóanyag-kód default | Éles HIS pecsétig tilos |
| `pce_shadow` + `pce_hitl` | Élő párosítás árnyékban; vak HITL (human-in-the-loop) UI; nincs kitalált szegény metabolizáló | A felíró **nem** látja (NG-07) |
| `pce_cds` | F2 CDS Hooks cső (order-sign / order-select + SMART stub); repo `LIVE_CDS=false` → üres `cards` | Signed `LIVE_CDS=true` pecsét nélkül tilos |
| `pce_ui` | Labor / klinikai / HITL HTML + F2 lakat-UI (`cds.html`) a fenti API-kra | Nem EESZT-kliens |

Hivatalos klinikai pin: `docs/pce/Sources/official/MANIFEST.json` — **19** fájl `ok: true` a 2026-08-13 körben, SHA-256-tal, beleértve GDPR Art. 12 HTML/PDF, EMA 0,09 űrlap-utasítás, MDCG 2021-24, Health Canada PRCI (cél-cella 11), DHCS DDG V2.2 (Wayback). 2026-08-14 ETAP 0: **26** `ok: true` (+ DPWG ClinPGx, Ensembl POST, NCBI dbSNP, CYP2C19 diplotípus, WHO B01AC04, KNMP landing). 2026-08-15: **41** `ok: true` (+ PREPARE-12 diplotípus-API és WHO ATC a maradék élő párokhoz). A motor a pin-elt JSON extractet olvassa, nem a PDF-et futáskor.

Teszt: `PYTHONPATH=src python3 -m unittest discover -s tests -v` → **113 OK** (2026-08-13, G DSR + pin tesztekkel). A J-1…J-6 merge 108 volt; az árazási csomag 111; ez a G két DSR-tesztet ad. Nem 94. 2026-08-14 (D-44, `pce_cds`): **124 OK**. 2026-08-14 (D-45, ETAP 0): **134 OK**. 2026-08-15 (D-46): **158 OK**.

`LIVE_CDS = false`. `MATCHER_ON = false`. Bent van ≠ be van kapcsolva.

---

## 5. Hogyan használd

| Mondd | Ne mondd |
| --- | --- |
| Egy publikus PGx-szoftver lista: 365 USD/év / provider | „Minden versenytárs ennyi” |
| A kórházi HIS százmilliós–milliárdos keret; a PGx-modul töredék | „A Semmelweis 816 M Ft-ot fizetett PGx-ért” |
| Javasolt sáv 6–35 M Ft/év tenancy, tárgyalásra | „Ez a listaárunk” |
| A klinikus-sáv alja egy DrugMap-teszt negyede, *ha* az a 499 e Ft áll | „A DrugMap-ot mi verifikáltuk” |

Megrendelőlap: [proposal-order.md](proposal-order.md). Flag: [market-packs.md](market-packs.md). Analógia-határ: [competitor-analogs.md](competitor-analogs.md).
