# Precision Clinical Engine (PCE) — specifikációs csomag

| | |
| --- | --- |
| **Státusz** | Draft — review-ra kész |
| **Verzió** | v1.1 |
| **Dátum** | 2026-08-12 |
| **Nyelv** | magyar (követelmény-ID-k angolul) |
| **Repo** | [markbunyevacz/genetics](https://github.com/markbunyevacz/genetics) |

Ez a csomag a PCE farmakogenetikai (PGx) platform **követelménylistája és szoftverspecifikációja**. Write-spec PRD-struktúra, IEC 62304 / MDR technical file-ba vihető SRS-kiterjesztéssel. **Nem** jogi állásfoglalás, **nem** üzleti terv, **nem** implementáció.

## Olvasási sorrend

1. **[PCE-SPEC-v1.1.md](PCE-SPEC-v1.1.md)** — kanonikus PRD + SRS. Innen indulj.
2. **[A-intended-purpose-and-modules.md](A-intended-purpose-and-modules.md)** — F1 vs F2/F3 intended purpose, L0–L7 modul-minősítés. Az OQ-05 tényalapja, nem a válasza.
3. **[B-architecture-and-interfaces.md](B-architecture-and-interfaces.md)** — adatmodell, API/FHIR/VCF, hibakatalógus, SOUP, fenokonverzió.
4. **[C-eeszt-f0-checklist.md](C-eeszt-f0-checklist.md)** — 29/2022. 4. melléklet 1.1–1.9 + ISO 9001, 2026-09-30.
5. **[D-risk-and-traceability.md](D-risk-and-traceability.md)** — ISO 14971 kezdeti kockázat + FR→forrás→teszt→GSPR mátrix.

## Process artifacts

| Fájl | Tartalom |
| --- | --- |
| [ProcessArtifacts/SOURCE-INVENTORY.md](ProcessArtifacts/SOURCE-INVENTORY.md) | Felhasznált forrásdokumentumok |
| [ProcessArtifacts/SOURCE-REGISTRY.md](ProcessArtifacts/SOURCE-REGISTRY.md) | Külső források L1–L5 besorolással |
| [ProcessArtifacts/VALIDATED-CLAIMS.md](ProcessArtifacts/VALIDATED-CLAIMS.md) | Korrekciók a v1.0 vázlathoz képest |
| [ProcessArtifacts/PROCESS-HISTORY.md](ProcessArtifacts/PROCESS-HISTORY.md) | Fázis- és döntésnapló |
| [Sources/PCE-SPEC-v1.0.md](Sources/PCE-SPEC-v1.0.md) | Előző vázlat (nem kanonikus) |

## Gyártó

A gyártó neve ebben a csomagban **nincs kitalálva**. A9 feltevés: a gyártó a `genetics` repo tulajdonos szervezete. A README és a spec a repo-t azonosítja, nem egy fiktív Kft.-t.

## Ami szándékosan nincs itt

- OQ-05 jogi vélemény (külső counsel)
- Engineering ticket-bontás, gold-set annotációs SOP
- Saját PRS-motor, B2C VCF-upload, EESZT írás, onkológiai szomatikus panel
- TAM / piackutató-számok (5,7× szórás; nem SRS-anyag)

## Következő gate

P01 — source coverage audit + independent build-readiness review. A blokkoló üzleti kérdés: **OQ-05** (lásd spec §10 és A melléklet).
