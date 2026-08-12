# Sales — Eladható ajánlati csomag (feltételezett OQ-válaszok)

| | |
| --- | --- |
| **Csomag** | PCE-SPEC-v1.2 Sales |
| **Dátum** | 2026-08-12 |
| **Státusz** | Kereskedelmi hipotézis — **küldhető tervezet**; nem counsel-pecsét, nem árlista |
| **Gyártó** | `[Gyártó neve]` (A9; név nincs kitalálva) |

A spec-írás fagyasztva van. Ez a mappa **nem** új MDSW-állásfoglalás. Azért készült, mert G4 (≥ 3 fizető partner) és a klinikai/labor értékesítés **nem várhat** arra, hogy a F.6 tábla magától megteljen: a vevőnek SKU, ajánlat, demóhatár és szerződési feltétel kell.

**Alapelv:** a külső OQ-kra a gyártó *kért* válaszát vesszük **eladási alapnak**, és minden vevői iraton ott van, hogy ez feltétel. Ha a counsel nemet mond, a SKU nem „eltűnik”, hanem IIa pályára megy — addig nincs CE-mentes szoftvereladás.

## Ki mit vesz (röviden)

| Vevő | v1-ben mit vesz | Mit **nem** vesz |
| --- | --- | --- |
| **Partnerlabor** | F1+ szoftver: white-label, aláírt PGx-lelet (SKU-L) | Saját genotípus-hívó motort (NG-01) |
| **Klinika / magánrendelő** | A labor **vizsgálatát + leletét** (SKU-C). A PCE a labor / HIS mögött van. | Felírás-pillanatú riasztást, dózisszámot, B2C VCF-uploadot |
| **HIS / medikai vendor** | Modullicenc + MDR-határvonal (SKU-H, REG-021) | Azt, hogy ők legyenek az MDSW-gyártók |
| **Kórház RA** | Opcionális F1s evaluation (SKU-S) — **nem** a v1 bevételi mag | Élő CDSS-t CE nélkül |

A klinikus fájdalma (P2: „a felírás pillanatában akarok figyelmeztetést”) **valódi**, és **F2/F3**. Ha ezt ígéred v1-ben, a komoly vevő RA-ja kiszúrja, a spec pedig NG-07. A v1 ígéret: a lelet **megvan, aláírt, verziózott, a HIS-ben / PDF-ben**, nem hónapokkal később egy betegfiókban.

Részletes mátrix: [sku-and-buyers.md](sku-and-buyers.md).

## Feltételezett OQ-válaszok (eladási alap)

| OQ | Hipotézis, amire az ajánlat épül | Ha a válasz ellenkező |
| --- | --- | --- |
| **OQ-05** | IGEN, az A.1.2 invariánsok mellett: F1+ **nem MDSW** | SKU-L szoftvereladás **szünetel**, amíg IIa/CE. Fizető design-partner / várólista megmarad. A kód nem kidobandó. |
| **OQ-03** | Van legalább **egy** aláíró partnerlabor (REG-020) | SKU-C **nincs**: a gyártó nem végez genetikai vizsgálatot (NG-03, 12. §). Klinikának nincs mit számlázni. |
| **OQ-16** | Anonim F1s default (FR-461) | SKU-S csak FR-115-tel. Nem a v1 bevételi mag. |
| **OQ-15** | Shadow = evaluation / QA, nem Art. 62 | SKU-S vizsgálatként, etikai engedéllyel — lassabb, nem a záró ajánlat. |
| **OQ-01** | ISO 9001 **folyamatban**, kapu 2026-09-30 | Közbeszerzés / nagy kórház IT blokkolhat; magánlabor kevésbé. |

Ezek **nem** F.6 aláírások. Minden ajánlatban: *„A szoftverlicenc hatálybalépésének feltétele az OQ-05 írásos counsel-állásfoglalás. Addig: fizetős pilot szintetikus / labor-kontrollált adatokon.”*

## Irattár (vevőnek küldhető)

| Fájl | Címzett | Mikor |
| --- | --- | --- |
| [sku-and-buyers.md](sku-and-buyers.md) | Belső sales + ügyvezetés | Pitch előtt kötelező |
| [lab-one-pager.md](lab-one-pager.md) | Labor-vezető (P1) | Első SKU — ez a fizető termék |
| [clinic-one-pager.md](clinic-one-pager.md) | Klinika-üzemeltető / orvosigazgató (P2, P5) | Második — ők a leletet veszik |
| [his-vendor-one-pager.md](his-vendor-one-pager.md) | Medikai szállító (P6) | Integrációs csatorna |
| [proposal-order.md](proposal-order.md) | Bármely vevő jog / beszerzés | Ajánlat + megrendelőlap |
| [demo-script.md](demo-script.md) | Sales / megoldástervező | Demó — tilos a felugró ablak |
| [msp-checklist.md](msp-checklist.md) | Termék + sales | Enélkül **ne** fogadj el klinikapénzt |
| [customer-ra-faq.md](customer-ra-faq.md) | A vevő RA / jogásza | Amit úgysem kérdeznek meg előre |

**Melléklet a vevő RA-jának** (nem ez a mappa): A.1 intended purpose, A.1.1 nyilatkozat, [OQ-05 brief](../Outbound/OQ-05-counsel-brief.md) másolat, FR-470 egy mondat.

## Sorrend, ha el akarod adni

1. **SKU-L** — első aláíró labor (Outbound OQ-03 term sheet kitöltve). Enélkül a klinika-pitch üres.
2. **MSP** — outside-call → aláírt PDF, A.1.1, FR-100 kapu, demó szintetikus eseten ([msp-checklist.md](msp-checklist.md)).
3. **SKU-C** — klinikának a *labor szolgáltatása*, nem a PCE mint CDSS.
4. **SKU-H** — HIS-vendor, ha a klinika „a saját rendszerében akarja látni”.
5. SKU-S / F2 **nem** az első számla.

G4 a specben: ≥ 3 fizető labor/klinikai partner. A „klinikai” itt a **leletet rendelő** intézmény, nem a CE-s CDSS-licenc.

## Ami szándékosan nincs itt

- Kitöltött Ft-ár, TAM, versenytárs-tábla
- „CE nélkül is CDSS, mert az orvos dönt”
- Gyártó- vagy labor-cégnév
- Aláírt DPA / ÁSZF (jogi sablon a counselé; itt szerep-váz van)
