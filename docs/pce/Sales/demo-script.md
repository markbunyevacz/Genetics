# Demó — a **rendszer** (F1–F3), piaci lakatokkal

| | |
| --- | --- |
| **Iktató** | PCE-SALES-DEMO / v1.2 |
| **Közönség** | Klinika / kórház IT+orvosigazgató; opcionálisan labor mint csatlakozó |
| **Adat** | Csak `SYN-…`. Éles TAJ tilos. |
| **Cél** | Eladni a **platformot**, nem egy PDF-et. Megmutatni, hogy F2/F3 *benne van*, és *zárva* van. |

---

## 0. Nyitó (45 mp)

> „Ez egy farmakogenetikai rendszer: lelet, árnyék-validáció és élő döntéstámogatás **egy** szoftverben. A `[HU|EU|US]` csomagban ma az F1+[ / F1s] él. Az F2/F3 a felírónak zárva, amíg az adott piac minősítése megvan — nem azért, mert hiányzik, hanem mert a riasztás bekapcsolása forgalomba hozatal.”

Ha azt mondják, „nekünk a YouScript kell, most”:

> „A motor megvan. A felírási kártya ugyanazon a csövön kapcsol. Ma lakattal mutatom. CE / in-house / FDA nélkül nem kapcsolom, mert az a ti RA-toknak és nekünk is Rule 11a / eszköz.”

---

## 1. Forgatókönyv — 20 perc, klinika a vevő

| Perc | Mit mutatsz | Mondat | Tilos |
| --- | --- | --- | --- |
| 0–2 | Nyitó + market pack slide (HU/EU/US tábla) | „Egy bináris, három csomag” | „US-ben ez nem eszköz, ezért EU-ban is mehet” |
| 2–7 | F1+: SYN-001 outside-call → lelet, teljes gén-tábla, callability fail eset | „A labor *csatlakozik*, ti licencelitek a rendszert” | „Mi eladjuk a 499 ezres vizsgálatot” |
| 7–11 | F1s: HITL kártya **kutatási UI**, reviewer-vak; felírói képernyőn üres | „A motor fut, a vizit nem látja” | Shadow tipp a vizit-UI-n |
| 11–16 | F2 képernyő **lakattal**: CDS-kártya mock, `LIVE_CDS=false` badge | „Ez a feloldott állapot *után*. Ma nem kattintható élesre.” | Éles order-sign a demó-HIS-ben |
| 16–18 | Feloldási út: CE / in-house / OQ-17 | „Szerződés §8, nem config” | Dátumígéret („Q4-ben biztos CE”) |
| 18–20 | Ár: platform `[Yp]`, aktiválás `[Ya]` később | Rendszerlicenc | Labor listaár mint PCE-ár |

Labor a teremben: 3 perc csatlakozó (outside-call mezők), nem „vegyétek meg ti a terméket”.

---

## 2. HIS-vendor (10 perc)

Ugyanaz a rendszer, beágyazva. REG-021. Enciklopédia ON lehet F1+-szal. CDS Hooks endpoint a demóban **403/lakat**.

---

## 3. Tiltott

- `LIVE_CDS=true` HU/EU/US demó-tenancyen, amíg a pack LOCK
- „Bent van, kapcsoljuk, a CE majd utolér”
- Gyártó mint genetikai labor
- LLM-lelet
- Valódi beteg

A lakat **eladási eszköz**: a vevő látja a teljes F1–F3-at. A lakat nélküli F2-demó EU-ban MDSW-forgalmazásnak *néz ki*.
