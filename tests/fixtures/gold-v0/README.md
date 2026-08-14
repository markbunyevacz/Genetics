# Gold V0 — SYN FHIR fixture (TC-GW, nem G3 SOP)

| | |
| --- | --- |
| **Ticket** | PCE-GW-461-11 |
| **Adat** | Szintetikus. Opák ID-k. **Nincs** valós TAJ, **nincs** valós név. |
| **Küszöb** | A14 `rare_diplotype_threshold = 0.005` `[ASSUMPTION]`. DPO felülírhatja. |
| **Frekvencia** | CPIC/ClinPGx **diplotípus** tábla, biogeográfiai oszlop **European**, letöltve 2026-08-12. |
| **Index** | [index.json](index.json) |

Ez **nem** a §13 klinikai gold-set SOP. Nem OQ-16 pecsét. Nem k-anonimitás-bizonyíték.

## Mit *ne* keverj

| Forrás | Szabad | Tilos |
| --- | --- | --- |
| **CPIC frequency xlsx** | A14 0,5% összevetés; `frequency-config.v0.json` | A táblát „magyar allélfrekvenciának” nevezni. HU nincs CPIC-csoport; SYN default = **European** oszlop `[ASSUMPTION]`. |
| **PharmGKB gén–gyógyszer TSV** | Matcher / FR-400 később | A 0,5%-os A14 szabály **nem** ebből épül. E.3.1: a produkciós freq-forrást a DPIA nevezi meg. |
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

A CPIC **Diplotype frequency** lap Hardy–Weinberg becslés az allélgyakoriságokból (a xlsx *Methods and Caveats* füle). CYP2D6 change log a fájlban: **2024-10-17**. CYP2C19 change log: **2022-03-11**.

## Mit égess a configba (0,5% szabály)

[frequency-config.v0.json](frequency-config.v0.json) — **nem** a hívási út konstansa. `rare_diplotype_threshold` config-kulcs.

**Allowlist, nem denylist.** A gitbe az European HW diplotípusok mennek, ahol freq ≥ 0,005. Ami nincs a listán (ismeretlen hívás, ritka, 0.0), az A14 szerint coarsen/drop. A teljes CYP2D6 lap **4005** numerikus European sort tartalmaz; ebből **34** keep, **1001** pozitív &lt; 0,5%, **2970** nulla. A 3971 nem-keep sort **ne** tedd a gitbe.

| Gén | Keep (RAW engedélyezett) | Fixture ritka | Legritkább pozitív a teljes lapon (mindig drop) |
| --- | --- | --- | --- |
| CYP2D6 | **34** sor; leggyakoribb `*1/*2` = **0.105658144** | `*6/*6` = **0.00012537414** | `*3x2/*3x2` = **9.999999e-09** |
| CYP2C19 | **6** sor: `*1/*1`, `*1/*17`, `*1/*2`, `*2/*17`, `*17/*17`, `*2/*2` | — | nem Gold V0 HIS-bemenet |

CYP2C19 keep (European, 2026-08-12 xlsx):

| Diplotípus | Freq |
| --- | --- |
| `*1/*1` | 0.39080182 |
| `*1/*17` | 0.2693592 |
| `*1/*2` | 0.18361284 |
| `*2/*17` | 0.06327735 |
| `*17/*17` | 0.04641379 |
| `*2/*2` | 0.021566989 |

Frissítés: töltsd le a `current/` xlsx-eket, futtasd: `python3 extract_cpic_frequency_slice.py CYP2D6_frequency_table.xlsx CYP2C19_frequency_table.xlsx`.

## TC-GW esetek (PCE-GW-461-11 mind a 11)

| Fájl | Teszt | Bemenet | Elvárt |
| --- | --- | --- | --- |
| [gw-v0-01-normal-his-in.json](gw-v0-01-normal-his-in.json) | TC-GW-010..014 | CYP2D6 `*1/*2` (≥ 0,5%); ATC5 `N06AB10`; nap-idő; `doseQuantity`; opák PII | [gw-v0-01-normal-gateway-out.json](gw-v0-01-normal-gateway-out.json): nincs `patient` / dózis / INN; **`N06AB10`** (7 karakter); `2026-Q3`; **RAW** |
| [gw-v0-02-rare-diplotype-his-in.json](gw-v0-02-rare-diplotype-his-in.json) | TC-GW-017 | `*6/*6` (&lt; 0,5%) | [gw-v0-02-rare-expected.json](gw-v0-02-rare-expected.json): default **drop** `E-SHADOW-003`; coarsen → `REDUCED` ha `on_rare=COARSEN` |
| [gw-v0-03-atc5-pce-ingest.json](gw-v0-03-atc5-pce-ingest.json) | TC-GW-011 | Gateway *kihagyva*: 7 karakteres kód a PCE-n | [gw-v0-03-atc5-expected.json](gw-v0-03-atc5-expected.json): **202** (D-38). DPO `max_atc_level=4` → `E-SHADOW-001` |
| [gw-v0-04-small-cell-his-in.json](gw-v0-04-small-cell-his-in.json) | TC-GW-015 | `*4/*4` (freq **0.034168635** ≥ 0,5%, PM → `REDUCED`); cella **4**, k = 5 | [gw-v0-04-coarsen-expected.json](gw-v0-04-coarsen-expected.json): `CLASS` / `REDUCED`; count **nincs** a payloadban |
| ugyanaz a HIS-in | TC-GW-016 | `on_small_cell=DROP` | [gw-v0-05-drop-expected.json](gw-v0-05-drop-expected.json): nincs HITL, `E-SHADOW-003` |
| [gw-v0-06-rarest-his-in.json](gw-v0-06-rarest-his-in.json) | TC-GW-018 | `*3x2/*3x2` | [gw-v0-06-rarest-expected.json](gw-v0-06-rarest-expected.json): **mindig drop**, akkor is ha `on_rare=COARSEN` és a cella ≥ k |
| [gw-v0-07-k-override-reject.json](gw-v0-07-k-override-reject.json) | TC-GW-019 | ANON `k=3` | elutasítva; nagyobb k csak config-release |
| [gw-v0-08-taj-pce-ingest.json](gw-v0-08-taj-pce-ingest.json) | TC-GW-010 ingest | `Patient.identifier` a PCE-n | [gw-v0-08-taj-expected.json](gw-v0-08-taj-expected.json): `E-SHADOW-001` |
| [gw-v0-09-day-pce-ingest.json](gw-v0-09-day-pce-ingest.json) | TC-GW-013 ingest | nap-szintű `authoredOn` a PCE-n | [gw-v0-09-day-expected.json](gw-v0-09-day-expected.json): `E-SHADOW-001` |
| [gw-v0-10-quarterly-monitor.json](gw-v0-10-quarterly-monitor.json) | TC-GW-020 | — | csak aggregátum; nincs nyers diplotípus / TAJ / nap |

A `*1/*2` CPIC coded summary: **CYP2D6 Normal Metabolizer** (AS 2.0). A `*4/*4`, `*6/*6`, `*3x2/*3x2`: **Poor Metabolizer** (AS 0.0) → coarsen osztály `REDUCED`.

A k-cella fixture szándékosan **nem** ritka diplotípus: a 0,5% szabály és a k ≥ 5 szabály külön tesztelhető.

## Következő (nem ebben a csomagban)

- Synthea-skálázás RxNorm→ATC map után.
- GeT-RM Coriell-minta ID-k a L3 matcher goldhoz (nem A14).
- §13 klinikai gold-set annotációs SOP (G3).
