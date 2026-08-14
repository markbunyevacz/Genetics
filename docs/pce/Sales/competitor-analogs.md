# Sales — YouScript / ActX / TSI analógia (határolva)

| | |
| --- | --- |
| **Iktató** | PCE-SALES-CMP / v1.2 |
| **Szabály** | Piaci *struktúra*-analógia. Nem árlista, nem MDR-pecsét, nem PCE-RWE. |
| **Dátum** | 2026-08-12 |

A vevő **SKU-P** rendszert licencel. A labor **csatlakozó**. Az alábbi három US-termék ezt a *szétválasztást* vagy a *lakat/élő CDS* lépcsőt világítja meg — a túlállítások VC-14.

---

## YouScript (Precision Medicine / Genelex)

**Ami áll:** élő, EHR-be ágyazott PGx/DDI döntéstámogatás (Epic, Cerner; SMART on FHIR). A SMART Health IT katalógus **Licensing & Pricing: Per User, Site-Based**. A gyártó webshopja **365 USD / 1 év** provider-megújítást listáz (2026-08-12). GenomeWeb (2014): Epic-integráció; a YouScript akkor is futtatható, ha a genotípus *más* laborból jön — ez az outside-call analógia `[R]`.

**Ami nem áll:**

- A PMC **7195220** (Valdes et al., *Crit Rev Clin Lab Sci*) polifarmácia-review. **Nem** említi a YouScriptot. Ne csatold YouScript-bizonyítékként.
- Publikus **ágyszám**-tarifa: nincs. Enterprise = sales quote.
- 39% / 71% kórházi csökkenés: céges közlés, a registry **szándékosan** kihagyta.
- A PCE FR-470 compile-time lakat **nem** YouScript-feature.

---

## ActX (Genomic Decision Support)

**Ami áll (vendor, L3):** laboroknak konfigurálható PGx **PDF**; egészségügyi rendszereknek Epic order-entry **riasztás**, ha van genomprofil és a felírt szerre van találat. NorthShore/Epic példa: Healthcare IT News `[R]`.

**Ami nem áll:** a „kezdetben statikus PDF, aztán CDSS” céges történet ebben a körben **nincs primer forrás** (`[NEEDS VERIFICATION]`). A releváns-szerre villanó riasztás **F2-viselkedés**, nem a HU/EU market-pack lakat. Élő ActX-szerű kártya CE nélkül = NG-07.

---

## Translational Software (PGx knowledge / API)

**Ami áll `[R]` (GenomeWeb):** lab-facing portal/API, diplotípus + guideline-szöveg, white-label riport. A 510(k) **nem** ment át; a cég az US PGx-szolgáltatást leállította. Az FDA a betegre szabott, CPIC-alapú riportot nem fogadta el puszta könyvtárnak; a diplotípus-hívás is kérdés volt.

**PCE-tanulság:** NG-01 (ne hívjunk allélt). OQ-05 maradék: gén-szintű CPIC/DPWG/FDA *terápiás* szöveg az F1+ leleten továbbra is lehet Rule 11a. TSI **nem** bizonyítja, hogy az F1+ „biztonságos, hatalmas B2B piac”.

---

## Hogyan használd a demóban

| Mondd | Ne mondd |
| --- | --- |
| A kórház a szoftvert fizeti; a labor adatot ad (YouScript/ActX csatorna) | „Ők EU-ban nem-MDSW-ként mennek, tehát mi is” |
| A lakat: előbb CE/in-house, aztán `[Ya]` | „YouScript-lakat; hétfőn kapcsoljuk” |
| PREPARE a *PGx panel* evidenciája (§9.4) | „A PCE 30%-kal csökkenti az ADR-t”; „életet ment / ápolási nap” a Lancetből |
| A kórház SKU-P-t fizet; a labor opcionális `[Yl]` | „A labor viszonteladja a PCE-t”; ágyszám-tarifa mint tény |

---

## GenXys / OneOme / Coriell

Nyilvános **USD/Ft listaár** ebben a körben **nincs**. A vendor oldalak demót / contact-sales-t kérnek (kutatás + OneOme/GenXys nyilvános „contact us” szövegek). **Nem** PCE-ár.

YouScript + PREPARE **nem** zárja le az OQ-05 / 15 / 16 / 17-et és nem pecsételi a nem-MDSW-t. Ft-sáv: [pricing.md](pricing.md).
