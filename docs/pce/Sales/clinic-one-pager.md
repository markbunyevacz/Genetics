# Klinikai egyoldalas — PCE rendszer (SKU-P)

| | |
| --- | --- |
| **Feladó** | `[Gyártó neve]` |
| **Címzett** | `[Klinika / kórház / hálózat]` — orvosigazgató / IT / üzemeltetés |
| **Tárgy** | Farmakogenetikai **rendszer** a HIS-ben — F1+ / F1s / F2 / F3 egy platformon |
| **Csomag** | `[HU | EU | US]` |
| **Státusz** | Ajánlat. A bekapcsolt modulok a piaci csomag szerint. F2/F3 klinikai UI alapból **zárt**. |

Tisztelt Partner!

A PCE **szoftverrendszer**, nem laborlelet-szolgáltatás. Ti licencelitek a motort. A genotípust a **ti laborotok** (vagy a kijelölt partnerlabor) adja; a vizsgálat díja az ő számlájuk. A rendszer F1-től F3-ig **egy** kódbázis: ami ma nem minősített, az **ki van kapcsolva**, nem hiányzik.

---

## Ami a dobozban van

| Réteg | Mit csinál | Most ezen a telephelyen |
| --- | --- | --- |
| **F1+** | Diplotípus → verziózott CPIC/DPWG/FDA lelet, callability, aláíróhely, HIS-dokumentum | `[ON / LOCK]` — HU/EU: OQ-05 |
| **F1s** | Ugyanaz a döntéstámogató motor **árnyékban**; a felíró nem látja; HITL utólag | `[ON / LOCK]` — DPO/RA |
| **F2** | Élő CDSS a felírás pillanatában, intézményen belül | **LOCK** — in-house dosszié után |
| **F3** | Ugyanaz a CDSS forgalomba hozatalra | **LOCK** — CE (EU) / FDA (US) után |

A lakat **szándékos**. Átminősítés után signed release, nem „bekapcsoljuk configból”. Részlet: [market-packs.md](market-packs.md).

---

## Amit ti adtok a rendszernek

- HIS / LIS csatlakozás (FHIR vagy a vendorotok).
- Labor-forrás: outside-call vagy VCF — **nem** a PCE hív allélt nyers adatból.
- 2008/XXI. tanácsadás és beleegyezés, ha HU csomag (a szoftver kapuz).
- Adatkezelői szerep; a gyártó feldolgozó.

---

## Amit nem ígérünk a zárás napján

- Hogy hétfőn élő riasztás megy a receptre, mert „a kódban benne van”.
- Hogy a gyártó elvégzi a genetikai vizsgálatot.
- EESZT eRecept/eProfil írást (HU).
- FDA-kiskaput az európai telephelyre.

---

## Ár (kitöltendő)

| Tétel | Összeg |
| --- | --- |
| Platform, `[HU\|EU\|US]` csomag | `[Yp]` / év |
| Telephely / klinikus sáv | `[Yc]` |
| Indítás / HIS-illesztés | `[Y0]` egyszeri |
| F2/F3 aktiválás (ha a flag feloldódik) | `[Ya]` — külön záradék |

Pilot: sandbox, szintetikus vagy labor-kontrollált eset, `[Yp_pilot]`, `[T]` hét, éles TAJ nélkül.

---

| | |
| --- | --- |
| Kapcsolat | `[név, e-mail, telefon]` |
| Melléklet | market-packs; RA-FAQ; minta-UI (F2 = lakat) |

*Nem CE-jel. Nem FDA-clearance. A zárt modul a rendszer része, klinikai használata tiltott.*
