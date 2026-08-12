# Precision Clinical Engine (PCE) — specifikációs csomag

| | |
| --- | --- |
| **Státusz** | Draft — review-ra kész |
| **Verzió** | v1.2 |
| **Dátum** | 2026-08-12 |
| **Nyelv** | magyar (követelmény-ID-k angolul) |
| **Repo** | [markbunyevacz/genetics](https://github.com/markbunyevacz/genetics) |

Ez a csomag a PCE farmakogenetikai (PGx) platform **követelménylistája és szoftverspecifikációja**. Write-spec PRD-struktúra, IEC 62304 / MDR technical file-ba vihető SRS-kiterjesztéssel. **Nem** jogi állásfoglalás, **nem** üzleti terv, **nem** implementáció.

v1.2 a **legális hibrid**: F1+ statikus, verziózott guideline-társítás aláírt laborleleten; F1s shadow HITL a kezelőorvos nélkül; élő F2/F3 CDSS csak minősítés után. Az „F2 képesség F1 minőségben, mert az orvos dönt” útvonal **elutasítva** (NG-07).

A v1 / F1s induláshoz **külső állásfoglalás** kell (spec §10.1): counsel (OQ-05), intézmény+RA (OQ-15), DPO (OQ-16), plusz OQ-01 és OQ-03.

## Olvasási sorrend

1. **[PCE-SPEC-v1.2.md](PCE-SPEC-v1.2.md)** — kanonikus PRD + SRS. Innen indulj.
2. **[A-intended-purpose-and-modules.md](A-intended-purpose-and-modules.md)** — F1+ / F1s / F2 intended purpose, L0–L7 modul-minősítés, A.0 bypass elutasítás. Az OQ-05 tényalapja, nem a válasza.
3. **[B-architecture-and-interfaces.md](B-architecture-and-interfaces.md)** — két path (klinikai vs shadow), adatmodell, API/FHIR/VCF, hibakatalógus, SOUP, fenokonverzió EDU/LIVE.
4. **[C-eeszt-f0-checklist.md](C-eeszt-f0-checklist.md)** — 29/2022. 4. melléklet 1.1–1.9 + ISO 9001, 2026-09-30.
5. **[D-risk-and-traceability.md](D-risk-and-traceability.md)** — ISO 14971 kezdeti kockázat (R-015–R-019) + FR→forrás→teszt→GSPR mátrix.
6. **[E-shadow-hitl.md](E-shadow-hitl.md)** — shadow pipeline, intézményi gateway, HITL UI, GDPR két út, kutatási hozzájárulás váz, REG-090 / OQ-15.

## Process artifacts

| Fájl | Tartalom |
| --- | --- |
| [ProcessArtifacts/SOURCE-INVENTORY.md](ProcessArtifacts/SOURCE-INVENTORY.md) | Felhasznált forrásdokumentumok |
| [ProcessArtifacts/SOURCE-REGISTRY.md](ProcessArtifacts/SOURCE-REGISTRY.md) | Külső források L1–L5 besorolással |
| [ProcessArtifacts/VALIDATED-CLAIMS.md](ProcessArtifacts/VALIDATED-CLAIMS.md) | Korrekciók a v1.0 vázlathoz + VC-11 REFUTED |
| [ProcessArtifacts/PROCESS-HISTORY.md](ProcessArtifacts/PROCESS-HISTORY.md) | Fázis- és döntésnapló |
| [Sources/PCE-SPEC-v1.0.md](Sources/PCE-SPEC-v1.0.md) | Előző vázlat (nem kanonikus) |

## Gyártó

A gyártó neve ebben a csomagban **nincs kitalálva**. A9 feltevés: a gyártó a `genetics` repo tulajdonos szervezete. A README és a spec a repo-t azonosítja, nem egy fiktív Kft.-t.

## Ami szándékosan nincs itt

- OQ-05 / OQ-15 jogi vélemény (külső counsel)
- Engineering ticket-bontás, gold-set annotációs SOP
- Saját PRS-motor, B2C VCF-upload, EESZT írás, onkológiai szomatikus panel
- TAM / piackutató-számok (5,7× szórás; nem SRS-anyag)
- DPA, DPIA, etikai kérelem végleges szövege (E melléklet váz)

## Következő gate

P01 — source coverage audit. v1 gate: **§10.1** külső állásfoglalás (OQ-05, OQ-15, OQ-16, OQ-01, OQ-03). A technikai csomag megvan, a döntés nincs.
