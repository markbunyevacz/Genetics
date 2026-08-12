# Gold V0 — SYN FHIR fixture (TC-GW, nem G3 SOP)

| | |
| --- | --- |
| **Ticket** | PCE-GW-461-11 |
| **Adat** | Szintetikus. Opák ID-k. **Nincs** valós TAJ, **nincs** valós név. |
| **Küszöb** | A14 `rare_diplotype_threshold = 0.005` `[ASSUMPTION]`. DPO felülírhatja. |
| **Frekvencia** | CPIC/ClinPGx **diplotípus** tábla, biogeográfiai oszlop **European**, letöltve 2026-08-12. |

Ez **nem** a §13 klinikai gold-set SOP. Nem OQ-16 pecsét. Nem k-anonimitás-bizonyíték.

## Mit *ne* keverj

| Forrás | Szabad | Tilos |
| --- | --- | --- |
| **CPIC frequency xlsx** | A14 0,5% összevetés; `frequency-config.v0.json` | A táblát „magyar allélfrekvenciának” nevezni. HU nincs CPIC-csoport; SYN default = **European** oszlop `[ASSUMPTION]`. |
| **CDC GeT-RM** | Konszenzusos *diplotípus-szöveg* labor-QC-hez (363 minta, 34 gén) | Populációs gyakoriság / k ≥ 5 teszt. GeT-RM **nem** A14 forrás. |
| **Synthea** | FHIR R4 életút, `Patient` / `MedicationRequest` a PII-strip és idő tesztjéhez | „Synthea ATC-t ad.” A Synthea gyógyszerkódja jellemzően **RxNorm**; az ATC-t a Gold V0 **explicit** WHO kóddal viszi (`N06AB10`). |
| **SMART sample patients** | Statikus FHIR demó | PCE-RWE; HIS-pecsét |

CPIC letöltés (élő `current/` URL, 2026-08-12):

- CYP2D6 frequency: https://files.cpicpgx.org/data/report/current/frequency/CYP2D6_frequency_table.xlsx
- CYP2C19 frequency: https://files.cpicpgx.org/data/report/current/frequency/CYP2C19_frequency_table.xlsx
- CYP2D6 diplotype–phenotype: https://files.cpicpgx.org/data/report/current/diplotype_phenotype/CYP2D6_Diplotype_Phenotype_Table.xlsx
- Index: https://www.clinpgx.org/page/cyp2d6RefMaterials
- GeT-RM: https://www.cdc.gov/lab-quality/php/get-rm/reference-materials.html
- WHO ATC: https://www.whocc.no/atc/structure_and_principles/

A CPIC **Diplotype frequency** lap Hardy–Weinberg becslés az allélgyakoriságokból (a xlsx *Methods and Caveats* füle). CYP2D6 change log a fájlban: **2024-10-17**.

## Három azonnali TC-GW eset

| Fájl | Teszt | Bemenet | Elvárt |
| --- | --- | --- | --- |
| [gw-v0-01-normal-his-in.json](gw-v0-01-normal-his-in.json) | TC-GW-010..014, PII-strip | CYP2D6 `*1/*2` (European **0.10565814** ≥ 0,5%); ATC5 `N06AB10`; nap-idő; `doseQuantity`; opák PII | [gw-v0-01-normal-gateway-out.json](gw-v0-01-normal-gateway-out.json): PII/dózis nincs; `N06AB`; `2026-Q3`; diplotípus **RAW** |
| [gw-v0-02-rare-diplotype-his-in.json](gw-v0-02-rare-diplotype-his-in.json) | TC-GW-017 | CYP2D6 `*6/*6` (European **0.00012537414** &lt; 0,5%); ATC4 már a HIS-ben | [gw-v0-02-rare-expected.json](gw-v0-02-rare-expected.json): default **drop** `E-SHADOW-003`; coarsen → `REDUCED` (PM) ha `on_rare=COARSEN` |
| [gw-v0-03-atc5-pce-ingest.json](gw-v0-03-atc5-pce-ingest.json) | TC-GW-011 | Gateway *kihagyva*: ATC5 eléri a PCE-t | [gw-v0-03-atc5-expected.json](gw-v0-03-atc5-expected.json): `E-SHADOW-001`, nincs HITL |

A `*1/*2` CPIC coded summary: **CYP2D6 Normal Metabolizer** (AS 2.0). A `*6/*6`: **Poor Metabolizer** (AS 0.0).

## Frekvencia-config (0,5%)

[frequency-config.v0.json](frequency-config.v0.json) — **nem** a hívási út konstansa. `rare_diplotype_threshold` config-kulcs.

- **Keep (RAW engedélyezett):** a CYP2D6 European diplotípusok, ahol freq ≥ 0,005. A 2026-08-12-es xlsx-ben **34** ilyen sor (leggyakoribb: `*1/*2` = 0.10565814).
- **Rare (coarsen/drop):** minden más a teljes CPIC táblában, plusz a fixture `*6/*6`.
- **Rarest drop (PCE-GW-461-07):** a betöltött tábla *adott biogeográfiai oszlopában* a **legkisebb pozitív** freq. A Gold V0 nem választ 0.0-s (nem megfigyelt) allélt „legritkábbnak”.

A teljes 4005 CYP2D6 diplotípus-sor **nincs** a gitben. Frissítés: töltsd le a `current/` xlsx-et, futtasd: `python3 extract_cpic_frequency_slice.py`.

## Következő (nem ebben a csomagban)

- Cella count 4 / k=5 COARSEN és DROP (TC-GW-015/016) — ugyanaz a bundle, `meta.cell_count` fixture-rel.
- Negyedéves monitor aggregátum (TC-GW-020).
- Synthea-skálázás RxNorm→ATC map után.
- GeT-RM Coriell-minta ID-k a L3 matcher goldhoz (nem A14).
