# F melléklet — Gyártói döntési előterjesztés (v1 / F1s)

| | |
| --- | --- |
| **Dokumentum** | PCE-SPEC-v1.2 Appendix F |
| **Dátum** | 2026-08-12 |
| **Státusz** | Gyártói, belsőleg jóváhagyott **kérési csomag** a külső szereplőknek |
| **Nem** | Jogi vélemény, DPO-határozat, etikai engedély, aláírt labor-szerződés |

A gyártó (A9: a `genetics` repo tulajdonos szervezete; **név nincs kitalálva**) az alábbi álláspontot kéri jóváhagyni. Az OQ **akkor zárul**, ha a címzett aláírja / elutasítja / feltételekkel visszaadja. Ez a fájl nem helyettesíti azt.

**Küldhető iratok:** [Outbound/](Outbound/README.md) — OQ-k. [Sales/](Sales/README.md) — vevői ajánlat a *feltételezett* OQ-válaszokra (G4). A F.6 sor az Outbound aláírás után töltődik; a Sales ettől még mehet pilotként.

```
v1 / F1s blokkolók
        │
        ├── Szabályozás: OQ-05 counsel · OQ-15 RA/intézmény
        ├── Adatvédelem: OQ-16 DPO · A10/A15
        └── Operatív:     OQ-01 EESZT/ISO 9001 · OQ-03 L3 labor
```

---

## F.0 Hogyan olvasd a státuszt

| Státusz | Jelentés |
| --- | --- |
| **ELŐTERJESZTVE** | A gyártó kérése rögzítve; külső aláírás hiányzik |
| **BELSŐ IGEN** | Amit a gyártó magának eldönthet (erőforrás, tárgyalás indítása) |
| **LEZÁRVA** | Csak külső vagy ténybeli zárás után (itt: egyik OQ sem, kivéve OQ-02) |
| **SPEC FAGYASZTVA** | v1.2 iratírás lezárva (§10.2); OQ-k ettől még ELŐTERJESZTVE |

A disclaimer (A.1.1 / FR-490) **nem** felelősségkizárás és **nem** MDSW-kimenekülés.

---

## F.1 OQ-05 — Counsel (ELŐTERJESZTVE)

**Kérés:** hagyja jóvá, hogy az A.1 F1+ **nem MDSW** (MDR hatályán kívül), a lenti műszaki garanciák mellett.

**Garanciák, amiket a counsel a dossziéban talál:**

- A report-renderer futásidőben **nem** kap `MedicationEntry`-t (FR-400-STATIC, FR-410-EDU, FR-470 CI).
- Kimenet: a meghívott gén **teljes**, verziózott CPIC/DPWG/FDA táblája; nincs ha–akkor a beteg aktuális gyógyszerére.
- FR-490 / A.1.1 nyilatkozat **minden** F1+ PDF/FHIR oldalon. Ez tájékoztató / rendeltetés-mondat, nem termékfelelősség-kizárás.

**A gyártó által kért kimenet:** feltételes igen, a fenti garanciák + FR-490 folyamatos megléte mellett.

**Ami ezt nem zárja:** a counsel aláírása. Ha a válasz nem, az F1+ IIa pályára esik (REG-010 újra).

Csomag: A.1, A.1.1, A.1.2, FR-400-STATIC, FR-410-EDU, FR-470, REG-010, MDCG 2019-11 Rev.1.

**Küldendő irat:** [Outbound/OQ-05-counsel-brief.md](Outbound/OQ-05-counsel-brief.md) — Igen/Nem/Feltétellel; A.1 szó szerint; a pecsét nem előre „nem MDSW”.

---

## F.2 OQ-15 — RA + intézmény (ELŐTERJESZTVE)

**Kérés:** a shadow (F1s) **ne** minősüljön MDR Art. 62 klinikai vizsgálatnak, hanem klinikai értékelési / minőségbiztosítási adatgyűjtésnek.

**Érv (nem tény):** FR-450-BLIND — szekvenciális reviewer-vak; a motor kimenete az index-ellátásban rejtve; FR-470: nincs írás a klinikai UI-ra. A szoftver nem módosítja a kezelést.

**Függés:** az intézményi RA a gyártó szerint akkor fogadja el, ha az **OQ-16** (DPO) tisztázott. F1s nem indul OQ-16 nélkül.

**Ami ezt nem zárja:** etikai bizottság / hatósági bejelentés, ha a RA másképp dönt. REG-090 az első HIS-csatlakozás előtt.

Csomag: E.4.1, E.7, FR-450-BLIND, FR-470.

**Küldendő irat:** [Outbound/OQ-15-intezmenyi-ra-egyoldalas.md](Outbound/OQ-15-intezmenyi-ra-egyoldalas.md) — kérelem, nem Art. 62-mentesség mint tény.

---

## F.3 OQ-16 — DPO (ELŐTERJESZTVE)

**Kérés:** az F1s default út legyen **anonim** (FR-115 nélkül), FR-461 + E.3.1 mellett.

**Garanciák:**

- Gateway intézményi zónában; ATC max 4. szint; idő = negyedév; k &lt; 5 vagy ritka diplotípus → drop vagy osztály (FR-461).
- A10: visszavonáskor 72 h törlés **vagy** irreverzibilis anonimizálás. A15 csak már anonim (vagy FR-115-ös) sorra.

**A gyártó által várt DPO-feltétel (előre beépítve):** A14 küszöb **monitorozása** és a legritkább diplotípusok automatikus dropja akkor is, ha ez rontja a G3-at (R-020). → FR-461 utolsó AC.

**Ami ezt nem zárja:** aláírt DPIA. Ha a DPO szerint a profil így is személyes adat → A12 hamis, FR-115 kötelező.

**Küldendő irat:** [Outbound/OQ-16-dpo-dpia-kerdoiv.md](Outbound/OQ-16-dpo-dpia-kerdoiv.md) — anonim út **nem** kapcsolja ki FR-100-at.

---

## F.4 OQ-01 — Ügyvezetés / RA (BELSŐ IGEN a folyamatról)

**Belső döntés:** a 2026-09-30 ISO 9001 / 4. melléklet 2. pont **v1 kapuőr** (A8: akkor is, ha a vevő a medikai vendor). Dedikált owner szerep: `eeszt_iso_owner` (természetes személy a QMS-ben, **itt nincs kitalálva**). ISO 9001 gap + tanúsító **azonnal** indul; külső QMS-tanácsadó bevonható.

**Ami nyitva marad:** van-e *most* érvényes EESZT fejlesztői regisztráció (C-000); a tanúsítvány megszerzése tény.

C melléklet C.4.

**Belső irat:** [Outbound/OQ-01-iso-eeszt-owner-csomag.md](Outbound/OQ-01-iso-eeszt-owner-csomag.md) — Redmine + 2.1 ISO 9001; **nem** EESZT FHIR.

---

## F.5 OQ-03 — Üzlet (BELSŐ IGEN a tárgyalás indítására)

**Belső döntés:** hivatalos tárgyalás az **első** partnerlaborral L3 outside-call + **minden** F1+ lelet aláírására. Kereskedelmi váz: havidíj + volumensáv (spec §11); a darabár opcionális sáv, nem „csak kivétel”. A szerződésben: aláírási SLA.

**Ami nyitva marad:** a labor **neve**, az ár, az aláírt REG-020. Itt labornevet **nem** találunk ki.

**Küldendő irat:** [Outbound/OQ-03-l3-term-sheet.md](Outbound/OQ-03-l3-term-sheet.md) — minden F1+ lelet aláírása; NG-01 ≠ riasztáskód; havidíj + volumensáv.

**Vevői pár:** [Sales/lab-one-pager.md](Sales/lab-one-pager.md) + [Sales/proposal-order.md](Sales/proposal-order.md). Klinikának: [Sales/clinic-one-pager.md](Sales/clinic-one-pager.md) — ők a leletet veszik, nem a CDSS-t. Enélkül G4 üres.

---

## F.6 Aláíró-sor (külső; üresen)

| OQ | Címzett | Dátum | Igen / Nem / Feltétellel | Feltétel |
| --- | --- | --- | --- | --- |
| OQ-05 | Counsel | | | |
| OQ-15 | Intézményi RA / kutatási igazgatóság | | | |
| OQ-16 | DPO | | | |
| OQ-01 | `eeszt_iso_owner` + tanúsító státusz | | | |
| OQ-03 | Partnerlabor (REG-020) | | | |

A sor kitöltése a címzett **Outbound** iratán történik, nem ebben a mellékletben.

A spec-írás **fagyasztva** (§10.2). A F1+ mag és a [Sales](Sales/README.md) **nem** várja ezt a táblát; az éles HIS és a nem-MDSW *licenc* igen. Pilot (szintetikus) a Sales ajánlat §2 szerint mehet.
