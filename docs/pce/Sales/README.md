# Sales — PCE rendszerlicenc (piaci csomagok)

| | |
| --- | --- |
| **Csomag** | PCE-SPEC-v1.2 Sales |
| **Dátum** | 2026-08-13 (árazási sáv: [pricing.md](pricing.md)) |
| **Státusz** | Kereskedelmi hipotézis — küldhető; nem counsel-pecsét |
| **Gyártó** | `[Gyártó neve]` (A9; név nincs kitalálva) |
| **Termék** | **PCE rendszer** (egy szoftver: F1+ · F1s · F2 · F3). Nem laborlelet-kereskedelem. |

A vevő **rendszert** vesz: farmakogenetikai motor + lelet + shadow + (később) élő CDSS **egy** platformon. A HU / EU / US csomag ugyanazt a kódot viszi; a különbség a **licencelt / bekapcsolt** modul, nem egy másik termék.

A labor **csatlakozó** (outside-call / VCF / LIS). A gyártó nem ad el PGx-vizsgálatot és nem B2C leletbolt (NG-03).

**NG-07 változatlan:** a kikapcsolt F2 **benne van** a rendszerben (G5). **Bekapcsolni** élő felírói UI-n csak az adott piac minősítése után szabad. „Bent van, majd CE-zünk, addig is megy a riasztás” = forgalomba hozatal, ha MDSW.

## Mit vesz a klinika

| Kap | Nem kap (amíg a flag zárva) |
| --- | --- |
| PCE platformlicenc, HIS/LIS csatlakozás | Másik szoftvert F2-höz — ugyanaz a rendszer |
| F1+ (lelet, statikus guideline) — ha a piaci csomag engedi | Élő order-sign riasztást HU/EU-ban CE / in-house nélkül |
| F1s (shadow) — ha OQ-15/16 és a csomag engedi | Azt, hogy a gyártó hívja a genotípust (NG-01) |
| F2/F3 **a binárisban**, zárral + átminősítési úttal | FDA CDS-kiskaput az MDR alá (nincs ilyen) |

Piaci flag-tábla: [market-packs.md](market-packs.md). Vevőtérkép: [sku-and-buyers.md](sku-and-buyers.md).

## Feltételezett OQ-k (eladási alap, nem lezárt pecsét)

| OQ | Hipotézis | Ha ellenkező |
| --- | --- | --- |
| **OQ-05** | F1+ bekapcsolható HU/EU-ban nem-MDSW-ként *vagy* a rendszer IIa-ként megy, F1+ akkor is a bekapcsolt réteg | F1+ flag IIa/CE-ig zárva a *klinikai* kimenetre; a kód megmarad; fizetős sandbox |
| **OQ-03** | Van labor-**csatlakozó** (REG-020) — integráció, nem a SKU | A rendszernek kell diplotípus-forrás; a klinika saját laborját kötjük. Nincs forrás → nincs mit futtatni. Nem azt jelenti, hogy a labor legyen a szoftver vevője. |
| **OQ-16 / 15** | F1s bekapcsolható evaluationként | F1s flag zárva; F2 attól még a roadmap |
| **OQ-01** | ISO 9001 folyamatban (HU) | HU közbeszerzés / EESZT-fejlesztői jogállás kockázat; EU/US csomag nem ettől él |
| **OQ-17** (US) | US counsel + 510(k)/De Novo / CDS-minősítés **nyitott** | US csomagban F2 **zárva**, amíg ez nincs. Nem FDA-blog alapján kapcsoljuk. |

Licencmondat: *„A PCE rendszerlicenc a `[HU|EU|US]` csomagot adja. Az F2/F3 klinikai UI a csomagban zárt; feloldás: change-control + az adott piac minősítése. Addig a motor shadowban / sandboxban futhat, a felíró nem kap élő kártyát.”*

## Irattár

| Fájl | Ki olvassa |
| --- | --- |
| [sku-and-buyers.md](sku-and-buyers.md) | Sales — **SKU-P rendszer**, nem leletbolt |
| [market-packs.md](market-packs.md) | Sales + RA — HU / EU / US flag + árazási mátrix minta (`[Y*]`) |
| [clinic-one-pager.md](clinic-one-pager.md) | Klinika / kórház — **ők a vevők** |
| [lab-one-pager.md](lab-one-pager.md) | Labor mint **integrációs partner** |
| [his-vendor-one-pager.md](his-vendor-one-pager.md) | HIS-csatorna |
| [proposal-order.md](proposal-order.md) | Rendszerlicenc + modulmátrix |
| [demo-script.md](demo-script.md) | Teljes rendszer demó; F2 lakat |
| [msp-checklist.md](msp-checklist.md) | Enélkül ne számlázz éles tenancyt |
| [customer-ra-faq.md](customer-ra-faq.md) | Vevő jog / RA |
| [literature-boundary.md](literature-boundary.md) | PREPARE/S028/YouScript **határ**; ne csatold RWE/pecsétként |
| [competitor-analogs.md](competitor-analogs.md) | YouScript / ActX / TSI — struktúra, nem árlista |
| [pricing.md](pricing.md) | Megfigyelt YouScript 365 USD + HIS-plafon; javasolt Ft-sáv = **következtetés** |

## Sorrend

1. Klinika / kórház / hálózat — **SKU-P** (rendszer).
2. Market pack: HU vagy EU vagy US.
3. Labor-csatlakozó a vevő laborjához (REG-020), nem „eladjuk a leletet”.
4. MSP: rendszer feláll, F1+ (vagy sandbox) megy, F2 zárt, demó a lakatot is mutatja.
5. F1s / F2 feloldás = külön aktiválási záradék, nem „majd bekapcsoljuk hétfőn”.

G4: ≥ 3 **fizető rendszerlicenc** (klinika / intézmény / vendor), nem három eladott PDF.
