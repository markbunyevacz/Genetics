# SKU és vevők — mit lehet eladni v1-ben

| | |
| --- | --- |
| **Iktató** | PCE-SALES-SKU / v1.2 |
| **Státusz** | Belső sales-térkép; a one-pagerek ebből készültek |
| **Hipotézis** | OQ-05 IGEN feltétellel; OQ-03 legalább egy labor |

A P2 klinikus **felírás-pillanatú riasztást** akar. Az a termék F2, Rule 11a, CE vagy in-house. **Ma nem eladható** anélkül, hogy a vevő (vagy a hatóság) MDSW-gyártónak nézne. A v1 eladható termék a **lelet-infrastruktúra**.

```
[ Klinika rendel PGx-vizsgálatot ]
        │  SKU-C: a klinika a LABORT fizeti
        ▼
[ Partnerlabor hívja a diplotípust + aláír ]
        │  SKU-L: a labor a PCE-t fizeti
        ▼
[ PCE F1+ white-label PDF/FHIR ]
        │
        ├─► PDF a klinikusnak / betegnek
        └─► HIS-modul (SKU-H), ha a vendor beépíti
```

---

## SKU-L — Labor white-label (v1 bevételi mag)

| | |
| --- | --- |
| **Vevő** | Engedélyezett genetikai / molekuláris labor (2008/XXI. 12. § (1)) |
| **Mit kap** | Outside-call → aláírásra kész PDF + FHIR; saját arculat; verziózott CPIC/DPWG/FDA gén-tábla; callability; FR-100 kapu |
| **Ár modell** | Havidíj + volumensáv (spec §11). Placeholder: `[Y1]` / `[Y2]` |
| **Szerződés** | [OQ-03 term sheet](../Outbound/OQ-03-l3-term-sheet.md) → REG-020 |
| **MDR** | Hipotézis: nem MDSW (OQ-05). Feltétel a licencben. |
| **Nélküle** | Nincs aláíró, nincs klinikai lelet, SKU-C halott |

Ez G1-et adja el: p95 &lt; 10 perc a kézi CPIC-másolás helyett.

---

## SKU-C — Klinika / magánellátó (lelet, nem szoftver)

| | |
| --- | --- |
| **Vevő** | Magánklinika, szakrendelő, kórházi osztály — **PGx-vizsgálatot rendel** |
| **Mit kap** | Aláírt farmakogenetikai lelet a partnerlaboron keresztül; a lelet a dokumentációban / HIS-ben; oktató guideline-szöveg a génhez; **nincs** felugró ablak a felíráskor |
| **Kitől számláz** | Alapeset: a **labor** számláz a klinikának (vizsgálat + lelet). A gyártó a labort számlázza (SKU-L). Kivétel: a gyártó a klinika HIS-vendorán át SKU-H-t ad — akkor sem CDSS-licenc. |
| **Ár modell** | A labor saját PGx-árazása (a piacon `[R]` 499 000 Ft lista egy versenytársnál — **nem** a PCE ára). A PCE nem B2C. |
| **MDR** | A klinika **nem** MDSW-üzemeltető F1+-on. A lelet laboratóriumi jelentés. |
| **Tilos a pitchben** | „Csökkenti a dózist”; „megakadályozza a mellékhatást a szoftver”; „ugyanaz, mint a YouScript / CDSS, csak olcsóbb” |

A klinika **azért** veszi meg, mert:

1. A lelet **gyorsabb** és **nyomon követhető** (guideline-verzió).
2. Az aláíró labororvos a saját szakorvosa / partnere — felelősség tiszta.
3. Ugyanaz a cső később F2-re kapcsolható (G5), **amikor** CE / in-house megvan — ez roadmap, nem v1 feature.

---

## SKU-H — HIS / medikai vendor

| | |
| --- | --- |
| **Vevő** | Engedélyezett medikai rendszer szállítója (P6) |
| **Mit kap** | F1+ modul: lelet megjelenítés + opcionális enciklopédia (FR-480). Írásos határ: ki a gyártó (REG-021). Nincs EESZT írás (NG-05). |
| **Ár modell** | Éves platform + integrációs egyszeri |
| **MDR** | A vendor **nem** akar MDSW-gyártó lenni — ezért F1+ statikus lelet, nem CDS Hooks. |
| **F2** | Ugyanaz a cső; a kapcsoló a gyártóé, CE után. |

---

## SKU-S — Shadow / HITL (nem v1 mag)

Kórházi kutatási / QA megállapodás. OQ-15 + OQ-16. **Nem** a klinikus-licenc. Ne ezzel nyiss sales hívást. Akkor vedd elő, ha a vevő a *későbbi* CDSS-t kérdezi: „ezen a csövön mérjük, a felíró nem látja”.

---

## SKU-F2 — Élő CDSS (nem v1)

Per-clinician / hó. **Csak** CE vagy in-house (REG-011) után. A sales **nem** ígér dátumot, amíg REG-030 / OQ-06 nincs. Roadmap-mondat: *„A v1 leletcsőre épül; az élő riasztás külön minősítés.”*

---

## Mi kell ahhoz, hogy a klinika *tényleg* vegyen

| # | Feltétel | Miért |
| --- | --- | --- |
| 1 | Aláíró labor (SKU-L) | 12. §; NG-03 |
| 2 | MSP működik (PDF + aláírás + disclaimer) | Nincs demó → nincs szerződés |
| 3 | Őszinte „nem CDSS” mondat | A vevő RA-ja ezt kérdezi elsőnek |
| 4 | OQ-05 mint **hatálybalépési feltétel** vagy fizetős pilot | Nem hazudsz MDSW-státuszt |
| 5 | DPA-szerep: adatkezelő = labor/klinika; gyártó = feldolgozó | P5 DPO |
| 6 | Ár a labor felé kitöltve (`[Y1]`/`[Y2]`) | G4 |

A 499 000 Ft-os kiskereskedelmi PGx-ár **nem** a tiéd. A tiéd a labor **ideje és a guideline-követés**. A klinika akkor fizet, ha a labor emiatt gyorsabb / megbízhatóbb leletet ad, vagy ha a HIS-ben megjelenik a lelet anélkül, hogy a vendor MDSW-t venne a nyakába.
