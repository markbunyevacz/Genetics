# SKU — PCE rendszer (egy termék, piaci flag)

| | |
| --- | --- |
| **Iktató** | PCE-SALES-SKU / v1.2 |
| **Termék** | Precision Clinical Engine — **rendszerlicenc** |
| **Nem termék** | Laboratóriumi PGx-vizsgálat, B2C lelet, „PDF-bolt” |

A vevő (klinika, kórház, ellátóhálózat, HIS-vendor) a **PCE-t** veszi. F1+, F1s, F2, F3 **ugyanaz a szoftver**. A piac (HU / EU / US) és a minősítés azt dönti el, melyik modul **élő** a felírónak.

```
                    PCE rendszer (egy bináris / egy tenancy)
        ┌──────────────┬──────────────┬──────────────┬──────────────┐
        │  F1+         │  F1s         │  F2          │  F3          │
        │  lelet       │  shadow      │  élő CDSS    │  CE/FDA CDSS │
        │  L4-static   │  L4-live     │  in-house    │  forgalom    │
        └──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┘
               │              │              │              │
         market pack     market pack    LOCK amíg     LOCK amíg
         HU/EU/US        OQ-15/16       in-house/CE   CE / 510(k)
```

Labor / LIS / VCF = **bemenet**. REG-020 = csatlakozási szerződés, nem a SKU neve.

---

## SKU-P — Platform (ez az, amit eladsz)

| | |
| --- | --- |
| **Vevő** | Klinika, magánellátó, kórház, ellátóhálózat |
| **Mit kap** | PCE rendszer: adatmodell, consent-kapu, ingest, knowledge, lelet, shadow-cső, CDSS-cső, audit. HIS/LIS csatlakozás. Piaci csomag (HU/EU/US). |
| **Ár modell** | Éves platform + telephely / klinikus sáv (**B2B SaaS**). F2/F3 *aktiválás* `[Ya]`, ha a flag feloldódik — nem új termék. Placeholder: `[Yp]` / `[Yc]` |
| **Bemenet** | A vevő laborja (outside-call/VCF) vagy kijelölt partnerlabor. A gyártó **nem** számláz vizsgálatot. A labor **nem** viszonteladó. |
| **Labor díj** | Csak ha a labor *saját* white-label tenancyt kér: `[Yl]` a gyártónak (OQ-03). REG-020 csatlakozó = 0 szoftverdíj a labor felé. |
| **MDR / FDA** | A *bekapcsolt* modul intended purpose-e. Kikapcsolt F2 nem „titkos CDSS”. |

Ez G5: a v2 (élő CDSS) **nem** újraírt szoftver. Kapcsoló + dosszié.

---

## SKU-H — HIS-vendor (csatorna, ugyanaz a rendszer)

A medikai szállító a PCE-t **beágyazza**. REG-021: ki a gyártó. A vendor nem lesz MDSW-gyártó attól, hogy F1+ dokumentumot megjelenít. F2 feloldás után a gyártó marad a CDSS gyártója, ha a szerződés így szól.

Ár: éves platform + integráció `[Yh]` / `[Yi]`.

---

## Labor-csatlakozó (nem SKU)

| | |
| --- | --- |
| **Ki** | A vevő laborja vagy kijelölt partner |
| **Mit csinál** | Diplotípust hív, callability, ahol kell: aláír a saját QMS-e szerint |
| **Szerződés** | REG-020 / [lab-one-pager](lab-one-pager.md) — integráció |
| **Pénz** | A labor a *vizsgálatot* a klinikának számlázhatja (az ő üzlete). A PCE-t a **klinika** fizeti a gyártónak. |

NG-01: a PCE nem hív allélt FASTQ-ból. Ez nem teszi a labort a szoftver vevőjévé.

---

## Modulok — mi van a dobozban vs mi él

| Modul | A rendszerben | Élő a felírónak | Feloldás |
| --- | --- | --- | --- |
| **F1+** | Igen | Market pack szerint (HU/EU: OQ-05) | Counsel / IIa |
| **F1s** | Igen | Soha a felírónak (ez a lényeg) | OQ-15/16; HITL külön UI |
| **F2** | Igen, `LIVE_CDS` compile/license **false** | Csak in-house (REG-011) után, azon az intézményen | Intézményi RA + QMS |
| **F3** | Igen, ugyanaz a motor | Csak CE (EU) / FDA clearance (US) után | NB / FDA |
| **L5 PRS** | Interfész-stub | Nem | F4 |

„Maximum ki van kapcsolva” = ez a tábla. **Nem** = „az EU-s klinikán megy a riasztás, mert a kódban benne van”.

---

## Árazási kötés (spec §11, rendszerre olvasva)

| Sor | Modell | Mikor |
| --- | --- | --- |
| Platform (SKU-P) | Éves + telephely | Most |
| Klinikus-sáv | Per-clinician/hó | F2/F3 *aktiváláskor* (spec: L4-live) |
| HIS-vendor | Éves + integráció | SKU-H |
| Labor volumensáv | Opcionális, ha a labor *is* tenancyt kér | Integráció, nem a mag-SKU |

A 499 000 Ft-os kiskereskedelmi PGx-vizsgálat **nem** PCE-ár. Az a labor üzlete.

Sávos placeholder + javasolt Ft-következtetés (YouScript 365 USD/év lista **nem** HU ár): [pricing.md](pricing.md), [market-packs.md](market-packs.md). Analogia-határ: [competitor-analogs.md](competitor-analogs.md).

---

## G4

Fizetőnek számít: aláírt **rendszerlicenc** (klinika / kórház / hálózat / HIS-vendor). Nem számít: ingyenes demó, „majd ha CE”, labor amely csak adatot ad licenc nélkül.
