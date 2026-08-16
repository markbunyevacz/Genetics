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
| `health-canada-prci-guidance.html` | Health Canada PRCI profiloldal (S060) | 2026-08-13 |
| `health-canada-prci-guidance-document.html` | Health Canada PRCI teljes útmutató: risk=0.09 **és** cél-cella 11 (S060) | 2026-08-13 |
| `dhcs-ddg-v2-2.pdf` | DHCS DDG V2.2 (2022-12-06): numerátor <11 vagy nevező <20 000 (S062). Wayback-pin; élő DHCS Incapsula. v3.0 nincs pinelve. | 2026-08-13 |
| `clinpgx-dpwg-guideline-annotations-2026-08-14.json` | ClinPGx DPWG guidelineAnnotation lista (113 rekord) | 2026-08-14 |
| `knmp-farmacogenetica-2026-08-14.html` | KNMP farmakogenetika landing (DPWG kiadó); gén-tábla nem ebből | 2026-08-14 |
| `cpic-api-diplotype-cyp2c19-nm-im-pm.json` | CPIC CYP2C19 `*1/*1` NM, `*1/*2` IM, `*2/*2` PM | 2026-08-14 |
| `whocc-atc-b01ac04.html` | WHO: B01AC04 = clopidogrel | 2026-08-14 |
| `ensembl-prepare12-defining-snvs-2026-08-14.json` | Ensembl POST GRCh38+GRCh37 definiáló SNV-k | 2026-08-14 |
| `ncbi-dbsnp-prepare12-defining-snvs-2026-08-14.json` | NCBI eutils dbSNP (rs8175347 = delins) | 2026-08-14 |
| `ncbi-refsnp-prepare12-defining-snvs-2026-08-14.json` | NCBI refsnp slim GRCh38.p14 HGVS | 2026-08-14 |

A PREPARE-12 gén `pair_view` / `recommendation_view` JSON: `tests/fixtures/f1plus-v0/prepare12/` (CPIC API, 2026-08-13).

A motor futáskor **nem** parse-olja a PDF-et. A pinelt JSON-kivonatot olvassa. A PDF/HTML itt van, hogy a forrás ne csak URL legyen.

A többi WHO 5. szintű hatóanyag-oldal a `MANIFEST.json`-ban van, nem ebben a táblában. IIa-safe **ellenpélda** (2026-08-16, S076): `whocc-atc-l01bc01.html` citarabin, `whocc-atc-l01bc05.html` gemcitabin, `whocc-atc-l01bb04.html` kladribin, `whocc-atc-l01bb05.html` fludarabin.

**MANIFEST `accessed`:** a top-level mező **2026-08-13** marad (az első kör fagyasztása). A sorok a *saját* pin napjukat viselik (`2026-08-13` / `14` / `15` / `16`). Ez szándékos, nem egységesítés.

Újraletöltés: `python3 docs/pce/Sources/official/fetch_official_sources.py` (2026-08-13 kör). ETAP 0 pin: `python3 docs/pce/Sources/official/fetch_etap0_pins.py` — a MANIFEST `accessed` mezőjét a régi sorokon **nem** írja felül. A `--jar-only` **nem** hív `merge_manifest`-et.
