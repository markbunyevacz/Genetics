# Demó-forgatókönyv — amit a vevő láthat (és amit nem)

| | |
| --- | --- |
| **Iktató** | PCE-SALES-DEMO / v1.2 |
| **Közönség** | Laborvezető, klinika-üzemeltető, HIS-vendor, *esetleg* a vevő RA-ja |
| **Adat** | **Csak** szintetikus eset (`SYN-001`…). Éles TAJ, valódi recept, élő HIS **tilos** a demóban, amíg OQ-16/15 és DPA nincs. |

A demó **eladja a leletet**. Ha felugró riasztást mutatsz, a v1 intended purpose hamis, a vevő RA-ja MDSW-nek néz, és a következő kérdés az: „hol a CE?”.

---

## 0. Nyitó mondat (30 mp, kötelező)

> „Ez nem döntéstámogató riasztás a felírásnál. A labor meghívja a diplotípust, a szoftver verziózott irányelv-táblát rendel hozzá, a labororvos aláír. A kezelőorvos a leletet kapja. Az élő CDSS külön, minősített termék.”

Ha a hallgató P2 („én figyelmeztetést akarok a gombnál”):

> „Az a F2, CE után, ugyanazon a csövön. Ma azt oldjuk meg, hogy a 499 ezres vizsgálat ne egy PDF legyen a beteg fiókjában.”

---

## 1. Forgatókönyv A — Labor (SKU-L), 12 perc

**Szereplők:** te + laborvezető. Képernyő: labor-UI.

| Perc | Lépés | Mutatni | Nem mutatni |
| --- | --- | --- | --- |
| 0–2 | Outside-call be: CYP2D6 \*1/\*1, callability OK, aláíró mező üres | FR-240 mezők | Nyers FASTQ, „mi hívtuk az allélt” |
| 2–5 | Generate: PDF white-label, **teljes** CYP2D6 CPIC tábla, verzió + URL | FR-400-STATIC | A beteg „jelenlegi” sertralinjára szűrt egy sor |
| 5–7 | Callability fail eset: hiányzó pozíció → `INDETERMINATE`, nem NM | FR-210 | „Normál, mert nincs variáns a fájlban” |
| 7–9 | EDU bekezdés: inhibitor-*osztályok* tankönyvileg | FR-410-EDU | „Mivel Ön paroxetint szed, PM” |
| 9–11 | Aláírás helye, A.1.1 a láblécben, kolofon: technológiai szállító | FR-490 | „A fejlesztő minden felelősséget kizár” |
| 11–12 | Guideline-verzió a metaadatban | FR-370 | Élő PharmCAT matcher mint default |

**Záró:** term sheet `[Y1]`/`[X]` — „minden leletet ti írtok alá”.

---

## 2. Forgatókönyv B — Klinika (SKU-C), 8 perc

**Szereplők:** orvosigazgató. Képernyő: **kész PDF** + (ha van) HIS-dokumentum nézet. Nem labor-admin.

| Perc | Lépés | Mutatni | Nem mutatni |
| --- | --- | --- | --- |
| 0–1 | Nyitó mondat (§0) | — | CDS Hooks kártya |
| 1–4 | Ugyanaz a SYN-001 PDF, klinikus szemmel: diplotípus, tábla, forrás | „ezt kapja az orvos” | Dózis-slider, „cseréld X-re” |
| 4–6 | Hol landol: HIS dokumentum / nyomtatás, nem beteg-email mint egyetlen csatorna | SKU-C ígéret | EESZT eProfil írás |
| 6–8 | Felelősség-tábla: labor aláír, orvos terápia | clinic-one-pager | „A szoftver megakadályozza a mellékhatást” |

**Ha kérik a riasztást:** 60 mp roadmap, **nincs** élő prototípus. „A motor megvan shadowban; a felíró nem látja, amíg nincs CE.” **Ne** mutasd a HITL kártyát úgy, mintha a vizit UI-ja lenne.

---

## 3. Forgatókönyv C — HIS-vendor (SKU-H), 10 perc

- FHIR Bundle (DiagnosticReport + Observation), sandbox.
- Enciklopédia: keresés „CYP2D6” → guideline lista, **nincs** nyitott MedicationRequest-hez kötött Card (FR-480).
- REG-021 egy slide: ti nem MDSW-gyártók.

---

## 4. Tiltott demó-elemek (CI a sales-re)

Ha bármelyik bekerül a hívásba, a demó **F2-t** adott el:

- `LIVE_CDS`, CDS Hooks, SMART interruptive
- „Ennél a betegnél a most felírt X-et Y-ra”
- `dose_mg`, `functional_phenotype` a **aláírt** PDF-en
- Shadow tipp a „kezelőorvos képernyőjén”
- Valódi beteg, TAJ, élő recept
- LLM-szöveg a leleten (FR-700)

---

## 5. Kiosztandó a hívás után

- A megfelelő one-pager (lab / clinic / HIS)
- Szintetikus minta-PDF (ha már van; különben „MSP után”)
- [proposal-order.md](proposal-order.md) pilot-sor
- [customer-ra-faq.md](customer-ra-faq.md), ha jogász is volt a hívásban
