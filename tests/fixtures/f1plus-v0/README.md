# F1+ Gold V0 (outside-call + official CPIC tables)

Not the §13 clinical gold-set SOP. Opaque IDs only. A gyártó tölti a CPIC API-t (`extract_cpic_prepare12_tables.py`), nem a labor.

| File | What |
| --- | --- |
| `outside-call-cyp2d6-called.json` | FR-240 CALLED `*1/*2` |
| `outside-call-cyp2d6-indeterminate.json` | FR-210 INDETERMINATE — no NORMAL claim |
| `cyp2d6-cpic-pair-view.v0.json` | CPIC `pair_view` CYP2D6 (korábbi szelet) |
| `cyp2d6-cpic-recommendation-view.v0.json` | CPIC `recommendation_view` CYP2D6 |
| `prepare12/` | Mind a 12 PREPARE gén pair + recommendation pin, 2026-08-13. F5/VKORC1 rec üres → a lelet jelzi. |
| `extract_cpic_prepare12_tables.py` | Újragenerálja a 12 gén JSON-t a nyilvános API-ról |

Do not invent `drugrecommendation` text. Do not filter pairs by a medication list. If a gene has no recommendation_view rows, say so — do not write dosing text.
