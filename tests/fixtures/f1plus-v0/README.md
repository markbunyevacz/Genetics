# F1+ Gold V0 (outside-call + official CPIC tables)

Not the §13 clinical gold-set SOP. Opaque IDs only. A gyártó tölti a CPIC API-t (`extract_cpic_prepare12_tables.py`), nem a labor.

| File | What |
| --- | --- |
| `outside-call-cyp2d6-called.json` | FR-240 CALLED `*1/*2` |
| `outside-call-cyp2d6-indeterminate.json` | FR-210 INDETERMINATE — no NORMAL claim |
| `cyp2d6-cpic-pair-view.v0.json` | CPIC `pair_view` CYP2D6 (korábbi szelet) |
| `cyp2d6-cpic-recommendation-view.v0.json` | CPIC `recommendation_view` CYP2D6 |
| `prepare12/` | Mind a 12 PREPARE gén pair + recommendation pin, 2026-08-13. F5/VKORC1 rec üres → a lelet jelzi. |
| `dpwg-prepare12-index.v0.json` | ClinPGx DPWG annotation index a 12 génre (2026-08-14). Nem keverve a CPIC sorral. |
| `fda-ddi-table-2-2-cyp2d6-strong.v0.json` | FDA Table 2-2 CYP2D6 strong index kivonat a 2026-08-13 HTML-ből. |
| `static-guideline-pins.v0.json` | `dpwg_version` / `fda_table_version` pecsét a lelethez. |
| `extract_cpic_prepare12_tables.py` | Újragenerálja a 12 gén JSON-t a nyilvános API-ról |

Do not invent `drugrecommendation` text. Do not filter pairs by a medication list. If a gene has no recommendation_view rows, say so — do not write dosing text.
