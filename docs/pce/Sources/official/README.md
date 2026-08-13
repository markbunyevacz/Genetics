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
| `whocc-atc-n06ab10.html` | WHO: N06AB10 = escitalopram | 2026-08-13 |
| `whocc-atc-c01ba01.html` | WHO: C01BA01 = quinidine | 2026-08-13 |
| `edpb-guidelines-01-2025-pseudonymisation.pdf` | EDPB 01/2025 álnevesítés | 2026-08-13 |
| `wp29-opinion-05-2014-wp216-anonymisation.pdf` | WP29 05/2014 k-anonimitás (technika, nem k=5) | 2026-08-13 |
| `ie-dpc-case-studies-2025.pdf` | Irish DPC: Art. 12(3) egy hónap | 2026-08-13 |
| `eur-lex-gdpr-2016-679.html` | GDPR Art. 12(3)/12(4)/17(1) primer | 2026-08-13 |
| `eur-lex-gdpr-2016-679.pdf` | GDPR OJ PDF (szövegkinyerés üres; a HTML a primer) | 2026-08-13 |
| `ema-anonymisation-report-form-instructions.pdf` | EMA/HC risk=0,09 (Policy 0070 / PRCI) | 2026-08-13 |
| `mdcg-2021-24-en.pdf` | MDCG Rule 11 osztályozási példatár | 2026-08-13 |

A PREPARE-12 gén `pair_view` / `recommendation_view` JSON: `tests/fixtures/f1plus-v0/prepare12/` (CPIC API, 2026-08-13).

A motor futáskor **nem** parse-olja a PDF-et. A pin-elt JSON extractet olvassa. A PDF/HTML itt van, hogy a forrás ne csak URL legyen.

Újraletöltés: `python3 docs/pce/Sources/official/fetch_official_sources.py`
