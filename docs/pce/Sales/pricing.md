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

A javasolt PCE-sáv **mindegyik következtetés**. Egy PGx-modul a fenti HIS-ügyletek **töredéke**.

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
| Platform / tenancy / év | **6–35 M Ft** | HIS-plafon töredéke; magánellátói tűrőképesség | `[ASSUMPTION]` következtetés |
| Klinikus / év | **120–480 e Ft** | YouScript 365 USD; a kutatás ≈ **115 e Ft** átváltást használ (MNB közép **nincs** pinelve). Felső sáv: nagyobb funkció-terjedelem | alsó: analogia; Ft: `[ASSUMPTION]` FX |
| További telephely / év | **2–8 M Ft** | site-based analogia (SMART, ár nélkül) | `[ASSUMPTION]` |
| HIS-integráció, egyszeri | a licenc **20–50%-a** | egészségügyi IT norma, nem megfigyelt PCE-tétel | `[ASSUMPTION]` |
| Labor white-label tenancy | **4–25 M Ft/év** | per-report komponenssel; `[Yl]`, nem viszonteladás | `[ASSUMPTION]` |
| F2/F3 aktiválási felár | **+15–40%** | csak CE / in-house után (`[Ya]`; FR-470) | `[ASSUMPTION]` |

**Tilos mondani:** „a PCE listaára 6–35 M Ft”; „365 USD = a HU klinikus-díj”; „a DrugMap 499 e Ft a mi árunk”.

### Orvosigazgatói érv (nem PCE-árlista)

Ha a DrugMap teszt **499 000 Ft** (VC-10, egy forrás) áll, a klinikus-sáv **alja** (120 e Ft/év) annak **kb. negyede**. Ez összehasonlítás egy laborvizsgálat-árral, nem SKU-P számla.

---

## 4. Ami a sáv mögött a repóban van (nem feltételezés)

Öt futó modul (a `pce_shadow` és a `pce_hitl` egy validációs cső):

| Csomag | A kódban | Ami *nincs* túlállítva |
| --- | --- | --- |
| `pce_clinical` | Hozzájárulás-kapu (FR-100), append-only audit (`prev_hash`, UPDATE/DELETE tiltva), FR-710 magyarázat | A **30 éves** megőrzés spec FR-120; a SYN SQLite nem időzít 30 évet |
| `pce_report` | Verziózott **CPIC** pair/recommendation (PREPARE-12 pin), callability, PDF, FHIR STU3 Bundle; F1+ matcher **ki** | A disclaimer **DPWG**-t említ; `dpwg_version` a JSON-ban **null** — hivatalos DPWG-tábla a leleten TRACE szerint hátravan |
| `pce_gateway` | Intézményi anonimizálás, k-cella, 7 karakteres hatóanyag-kód default | Éles HIS pecsétig tilos |
| `pce_shadow` + `pce_hitl` | Élő párosítás árnyékban; vak HITL (human-in-the-loop) UI; nincs kitalált szegény metabolizáló | A felíró **nem** látja (NG-07) |
| `pce_ui` | Labor / klinikai / HITL HTML a fenti API-kra | Nem EESZT-kliens |

Hivatalos klinikai pin: `docs/pce/Sources/official/MANIFEST.json` — **12** fájl `ok: true`, SHA-256-tal (2026-08-13). A motor a pin-elt JSON extractet olvassa, nem a PDF-et futáskor.

Teszt: `PYTHONPATH=src python3 -m unittest discover -s tests -v` → **111 OK** (2026-08-13, árazási pin-tesztekkel). A J-1…J-6 merge 108 volt; ez a csomag három market-tesztet ad. Nem 94.

`LIVE_CDS = false`. `MATCHER_ON = false`. Bent van ≠ be van kapcsolva.

---

## 5. Hogyan használd

| Mondd | Ne mondd |
| --- | --- |
| Egy publikus PGx-szoftver lista: 365 USD/év / provider | „Minden versenytárs ennyi” |
| A kórházi HIS százmilliós–milliárdos keret; a PGx-modul töredék | „A Semmelweis 816 M Ft-ot fizetett PGx-ért” |
| Javasolt sáv 6–35 M Ft/év tenancy, tárgyalásra | „Ez a listaárunk” |
| A klinikus-sáv alja egy DrugMap-teszt negyede, *ha* az a 499 e Ft áll | „A DrugMap-ot mi verifikáltuk” |

Megrendelőlap: [proposal-order.md](proposal-order.md). Flag: [market-packs.md](market-packs.md). Analogia-határ: [competitor-analogs.md](competitor-analogs.md).
