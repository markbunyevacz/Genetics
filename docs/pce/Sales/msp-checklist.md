# MSP — Minimum, hogy rendszerlicencet számlázz

| | |
| --- | --- |
| **Iktató** | PCE-SALES-MSP / v1.2 |
| **Termék** | PCE **rendszer**, nem PDF-bolt |
| **Szabály** | Sandbox-díj mehet MSP előtt. Éles intézményi tenancy **nem**. |

---

## A. Üzleti

| # | Kész? | Tétel |
| --- | --- | --- |
| A1 | [ ] | Vevő = klinika / kórház / hálózat / HIS-vendor (SKU-P vagy H) |
| A2 | [ ] | Market pack kitöltve: `HU` / `EU` / `US` |
| A3 | [ ] | `[Yp]` platformár kitöltve |
| A4 | [ ] | Ajánlat modulmátrixa: F2/F3 **LOCK**; feloldás §8 |
| A5 | [ ] | Diplotípus-**forrás** megvan (vevő laborja vagy REG-020) — csatlakozó, nem az, hogy a labort kell megvenni |
| A6 | [ ] | DPA-szerep: kezelő = intézmény |
| A7 | [ ] | Demó a lakatot is mutatta |

---

## B. Rendszer (egy telepítés)

| # | Kész? | Tétel |
| --- | --- | --- |
| B1 | [ ] | Tenancy + `MARKET_PACK` |
| B2 | [ ] | F1+ út: ingest → lelet **vagy** LOCK + sandbox, OQ-05 szerint |
| B3 | [ ] | FR-210 callability a SYN gold seten |
| B4 | [ ] | FR-470: `LIVE_CDS=false`; F2 UI lakat; CDS endpoint nem él |
| B5 | [ ] | F1s store külön IAM-mel (akár üresen), nem a klinikai UI-ra ír |
| B6 | [ ] | FR-100, ha HU |
| B7 | [ ] | FR-700: nincs LLM a klinikai úton |
| B8 | [ ] | Matcher default ki |

A F2 **kód** az MSP része (G5). A F2 **élő kimenet** nem.

---

## C. Élesítés

| # | Kész? | Tétel |
| --- | --- | --- |
| C1 | [ ] | HU/EU: OQ-05 vagy IIa/CE a bekapcsolt F1+-hoz; US: OQ-17 a bekapcsolt klinikai kimenethez |
| C2 | [ ] | Labor-csatlakozó élesben |
| C3 | [ ] | DPA |
| C4 | [ ] | HU: OQ-01 státusz közölve |

---

## D. G4

Fizető: SKU-P / SKU-H aláírva. Nem fizető: labor, aki csak adatot ad; F2-ígéret szerződés nélkül.
