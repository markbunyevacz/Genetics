# S028 — CureMD hibrid CDSS preprint: mit állít, mire *nem* használható

| | |
| --- | --- |
| **Forrás** | Maqsood MH, Sajid M, Ahmed K, Shahid MU, Farooq M. *A Hybrid AI and Rule-Based Decision Support System for Disease Diagnosis and Management Using Labs.* CureMD Research. arXiv:2603.14876v1 [cs.AI], 2026-03-16. |
| **Példány** | [CureMD-Hybrid-CDSS-arXiv-2603.14876v1.pdf](CureMD-Hybrid-CDSS-arXiv-2603.14876v1.pdf) |
| **Authority** | **L5** (arXiv preprint; gyártói kutatócsoport: CureMD, New York). Nem peer-reviewed folyóirat ebben a körben. **Nem** L1 hatósági/állami SOTA. |
| **Registry** | S028 |
| **Státusz** | Primerben elolvasva 2026-08-12. A három javasolt PCE-felhasználás **határolva** (VC-13). |

Ez a jegyzet a felhasználói kérésre adott **formális beillesztés**. Nem „Klinikai háttér és állami referenciák” fejezet: az a cím erre a forrásra hamis lenne.

---

## 1. Amit a cikk *tényleg* vizsgál `[V]` a PDF-ből

**Rendeltetés:** rutin laborból (CBC, CMP, lipid, májpanel) + kor/nem → **valószínű diagnózis-csoport** (ICD-10), majd szabályalapú megerősítés. Assistive CDSS a diagnózishoz, US primer ellátás.

| Állítás | A PDF-ben | Oldal / hely |
| --- | --- | --- |
| Mintanagyság | **593 055** beteg (nem „kb. 600 000” mint egyetlen szám) | Absztrakt; §3 |
| Helyszín | **547** US primary care; HIPAA de-identifikált CureMD EHR | Absztrakt; §3 |
| Időablak | Labor 2000–2023; a diagnózis előtti **1 év** | §3.1 |
| Szabálymotor | **59** állapot; guideline-ból kinyert szabály → ICD-10 | §4.1 |
| ML | XGBoost **multi-class**; 37 ICD-10 → **11** csoport; hiányzó érték imputálás nélkül | §4.2; kimenet §2 |
| Top-N pontosság (teszt 20%) | Top-1 **31,18%**; Top-5 **83,10%**; Top-11 99,6% | Table 2 |
| „80% küszöb” | A szerzők a Top-5-öt **trade-offnak** nevezik (80% elérése) | §5.1 |
| SHAP | Mean SHAP + egyedi beteg SHAP; T2DM példa az appendixben | §2 kimenet 3; §6; Fig. 7–9 |
| Limitáció (szerzők) | Csak labor; nincs vital, anamnézis, tünet | Limitations |
| Jövő (szerzők) | Gyógyszer / eljárás ajánlás — **nincs** a közölt rendszerben | Future work |

**Table 1 adatminőség:** a PDF „Dyslipidemia **E55**” / „Vitamin D Deficiency **E78**” sorai az ICD-10 szokásos kódolásával **felcseréltek** (E55 = D-vitamin / rachitis; E78 = lipoproteinzavar). A számokat ettől a jegyzettől **nem** viszi a PCE gold set. `[V]` Table 1, p. 5.

**Top-1 = 31,18%:** a Top-5 83,10% **nem** „a modell 83%-ban helyes diagnózist ad”, hanem: az igaz diagnózis-csoport az **öt** legvalószínűbb között van.

---

## 2. PCE-határ (miért nem „tökéletes beépítés”)

| PCE (v1.2) | S028 |
| --- | --- |
| Farmakogenetika: diplotípus → CPIC/DPWG/FDA | Diagnózis: CBC/CMP → ICD-10 csoport |
| G3 = fenokonverzió **recall ≥ 90%** PGx gold seten | Top-5 **accuracy 83,10%** 11 betegségcsoporton |
| R-020 = ATC-csonkolás vs G3 | Nem metrika-definíció |
| F1s = PGx L4-live shadow, felíró nem látja | Diagnosztikai likely-diagnosis a klinikusnak |
| Magyarázat F1+/F2 szabályúton: FR-710 (guideline, verzió, URL) | SHAP egy **XGBoost** modellre |
| Klinikai evidencia v2-höz: PREPARE (S008), PGx-Passport (S009), CPIC (S030) | CureMD saját EHR, US, nem PGx |

A két intended purpose **nem** ugyanaz. Az S028 **nem** igazolja a PCE motorját, **nem** MDR Annex XIV SOTA a PGx-CDSS-re, **nem** „állami referencia”.

---

## 3. A három kért felhasználás — döntés

### 3.1 F1s klinikai értékelési dosszié

| Kérés | Döntés |
| --- | --- |
| „Hatósági SOTA / állami hivatkozás” | **Tiltott.** L5 preprint, vendor. SOTA a PGx-re: S008/S009/S030 + MDCG. |
| „XGBoost a laboron = elfogadott irány, tehát a PCE F1s is” | **Csak analógia**, nem bizonyíték. Más feladat, más kimenet. |
| „83,1% = G3 / R-020 matematikai referencia” | **Tiltott.** Más metrika, más küszöb, más populáció. G3 marad **≥ 90% recall** (§9.2). |

**Szabad a dosszié *irodalmi* mellékletében (nem SOTA-tábla):** „Hibrid szabály+ML CDSS létezik labor-diagnosztikában (S028, L5); a PCE F1s ettől függetlenül PGx-szabály + HITL gold set.”

### 3.2 F2/F3 lakat — SHAP

A PCE F2 magja **szabály + fenokonverzió-tábla**, nem XGBoost-diagnózis. A bekapcsolt magyarázat: **FR-710** (determinisztikus, nem LLM, nem SHAP).

**Szabad, lakat alatt, P2:** *ha* később külön ML komponens kerül a rendszerbe (nem LLM — FR-700; nem v1 PGx-core), akkor feature-attribution (SHAP-osztály) **jelölt** magyarázó réteg, S028-cal mint *módszertani* analógia. Ez **nem** a v1 FR, **nem** G3-küszöb.

### 3.3 Sales / RWE melléklet a licenchez

**Tiltott** PCE-RWE-ként: a cikk nem a PCE-t, nem PGx-et, nem EU klinikát mér. „A rutin labor csökkenti a diagnosztikai tévedést” **a CureMD rendszerükre** vonatkozik, nem a SKU-P-re.

**Szabad**, ha a vevő a *hibrid CDSS* irodalmat kéri: ez a jegyzet + PDF, **L5** pecséttel, „nem a mi klinikai értékelésünk”.

---

## 4. PCE klinikai háttér — ami *igen* L1/L2

| ID | Forrás | Szerep |
| --- | --- | --- |
| S008 | PREPARE, Lancet 2023 | PGx klinikai evidencia (HU nincs a 7 országban) |
| S009 | PGx-Passport, CPT 2019 | 14 vs 12 gén |
| S030 | CPIC | F1+ / F2 szabályszöveg |
| S004/S005/S020 | MDCG / MDR | Minősítés, nem ez a preprint |

S028 **nem** kerül ezek mellé a SOTA-sorba.
