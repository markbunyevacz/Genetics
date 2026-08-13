# F1+ Gold V0 (outside-call + official CPIC tables)

Not the §13 clinical gold-set SOP. Opaque IDs only.

| File | What |
| --- | --- |
| `outside-call-cyp2d6-called.json` | FR-240 CALLED `*1/*2` |
| `outside-call-cyp2d6-indeterminate.json` | FR-210 INDETERMINATE — no NORMAL claim |
| `cyp2d6-cpic-pair-view.v0.json` | CPIC `pair_view` CYP2D6, accessed 2026-08-13 |
| `cyp2d6-cpic-recommendation-view.v0.json` | CPIC `recommendation_view` where lookupkey contains CYP2D6 |
| `extract_cpic_cyp2d6_tables.py` | Regenerates the two CPIC JSON files from the API |

Do not invent `drugrecommendation` text. Do not filter pairs by a medication list.
