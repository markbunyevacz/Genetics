# Hivatalos forrás-másolatok (dátummal rögzítve)

A gyártó (ez a repo) tölti le. Nem a labor és nem a kórház feladata.

| Fájl | Mi | Accessed |
| --- | --- | --- |
| `cpic-ssri-2023-37032427.pdf` | CPIC SSRI guideline PDF | 2026-08-13 |
| `cpic-opioid-2020-33387367.pdf` | CPIC opioid guideline PDF | 2026-08-13 |
| `fda-ddi-table-substrates-inhibitors-inducers-2026-08-13.html` | FDA DDI tábla (2-2. tábla: fluoxetin, paroxetin = erős CYP2D6 index-gátló) | 2026-08-13 |
| `whocc-atc-n06ab05.html` | WHO: N06AB05 = paroxetine | 2026-08-13 |
| `whocc-atc-n06ab03.html` | WHO: N06AB03 = fluoxetine | 2026-08-13 |
| `whocc-atc-structure-and-principles.html` | WHO: 5. szint = hatóanyag (7 karakter) | 2026-08-13 |
| `cpic-api-diplotype-cyp2d6-nm-pm.json` | CPIC API: `*1/*1`, `*1/*2` Normal Metabolizer; `*4/*4` Poor Metabolizer | 2026-08-13 |

A PREPARE-12 gén `pair_view` / `recommendation_view` JSON: `tests/fixtures/f1plus-v0/prepare12/` (CPIC API, 2026-08-13).

A motor futáskor **nem** parse-olja a PDF-et. A pin-elt JSON extractet olvassa. A PDF/HTML itt van, hogy a forrás ne csak URL legyen.

Újraletöltés: `python3 docs/pce/Sources/official/fetch_official_sources.py`
