# Precision Clinical Engine (PCE) — specifikációs csomag

| | |
| --- | --- |
| **Státusz** | **v1.2 FAGYASZTVA** — spec-írás lezárva; F1+ mag + Sales csomag indulhat |
| **Verzió** | v1.2 |
| **Dátum** | 2026-08-12 |
| **Nyelv** | magyar (követelmény-ID-k angolul) |
| **Repo** | [markbunyevacz/genetics](https://github.com/markbunyevacz/genetics) |

Ez a csomag a PCE farmakogenetikai (PGx) platform **követelménylistája és szoftverspecifikációja**. Write-spec PRD-struktúra, IEC 62304 / MDR technical file-ba vihető SRS-kiterjesztéssel. **Nem** jogi állásfoglalás, **nem** üzleti terv, **nem** implementáció.

v1.2 a **legális hibrid**: F1+ statikus, verziózott guideline-társítás aláírt laborleleten; F1s shadow HITL a kezelőorvos nélkül; élő F2/F3 CDSS csak minősítés után. Az „F2 képesség F1 minőségben, mert az orvos dönt” útvonal **elutasítva** (NG-07).

A v1 / F1s **éles ON moduljához** a gyártói kérés kész ([F](F-decision-package.md), [Outbound](Outbound/README.md)); a pecsét hiányzik. A **spec-írás lezárva**. A **PCE rendszer** (kód + [Sales](Sales/README.md) SKU-P) ettől függetlenül indul: F2/F3 a dobozban, klinikai UI **zárva**.

## Olvasási sorrend

1. **[PCE-SPEC-v1.2.md](PCE-SPEC-v1.2.md)** — kanonikus PRD + SRS. Innen indulj.
2. **[A-intended-purpose-and-modules.md](A-intended-purpose-and-modules.md)** — F1+ / F1s / F2 intended purpose, L0–L7 modul-minősítés, A.0 bypass elutasítás. Az OQ-05 tényalapja, nem a válasza.
3. **[B-architecture-and-interfaces.md](B-architecture-and-interfaces.md)** — két path (klinikai vs shadow), adatmodell, API/FHIR/VCF, hibakatalógus, SOUP, fenokonverzió EDU/LIVE.
4. **[C-eeszt-f0-checklist.md](C-eeszt-f0-checklist.md)** — 29/2022. 4. melléklet 1.1–1.9 + ISO 9001, 2026-09-30.
5. **[D-risk-and-traceability.md](D-risk-and-traceability.md)** — ISO 14971 kezdeti kockázat (R-015–R-019) + FR→forrás→teszt→GSPR mátrix.
6. **[E-shadow-hitl.md](E-shadow-hitl.md)** — shadow pipeline, intézményi gateway, HITL UI, GDPR két út, REG-090 / OQ-15.
7. **[F-decision-package.md](F-decision-package.md)** — gyártói előterjesztés a v1 blokkolókra. **Nem** külső aláírás.
8. **[Outbound/](Outbound/README.md)** — címzett-kész irattervezetek (counsel, DPO, intézményi RA, L3 term sheet, ISO/EESZT owner). Küldhető; **nem** aláírt állásfoglalás.
9. **[Sales/](Sales/README.md)** — **rendszerlicenc** (SKU-P). F1–F3 egy bináris; HU/EU/US flag. Klinika a vevő. Labor = csatlakozó. F2 bent van, lakattal. Nem leletbolt.

## Process artifacts

| Fájl | Tartalom |
| --- | --- |
| [ProcessArtifacts/SOURCE-INVENTORY.md](ProcessArtifacts/SOURCE-INVENTORY.md) | Felhasznált forrásdokumentumok |
| [ProcessArtifacts/SOURCE-REGISTRY.md](ProcessArtifacts/SOURCE-REGISTRY.md) | Külső források L1–L5 besorolással |
| [ProcessArtifacts/VALIDATED-CLAIMS.md](ProcessArtifacts/VALIDATED-CLAIMS.md) | Korrekciók a v1.0 vázlathoz + VC-11 REFUTED + VC-13/14 |
| [ProcessArtifacts/PROCESS-HISTORY.md](ProcessArtifacts/PROCESS-HISTORY.md) | Fázis- és döntésnapló |
| [Sources/PCE-SPEC-v1.0.md](Sources/PCE-SPEC-v1.0.md) | Előző vázlat (nem kanonikus) |
| [Sources/S028-curemd-hybrid-cdss-note.md](Sources/S028-curemd-hybrid-cdss-note.md) | CureMD/arXiv 2603.14876 — L5; **nem** PGx-SOTA, **nem** G3 |
| [Sales/literature-boundary.md](Sales/literature-boundary.md) | S028 **nem** csatolható PCE-RWE-ként a licenchez |

## Gyártó

A gyártó neve ebben a csomagban **nincs kitalálva**. A9 feltevés: a gyártó a `genetics` repo tulajdonos szervezete. A README és a spec a repo-t azonosítja, nem egy fiktív Kft.-t.

## Ami szándékosan nincs itt

- OQ-05 / OQ-15 jogi vélemény (külső counsel)
- Engineering ticket-bontás, gold-set annotációs SOP
- Saját PRS-motor, B2C VCF-upload, EESZT írás, onkológiai szomatikus panel
- TAM / piackutató-számok (5,7× szórás; nem SRS-anyag)
- Kitöltött F.6 aláírások, gyártónévvel/labor-névvel kitöltött Outbound/Sales iratok, aláírt DPIA, etikai engedély, REG-020 szerződés, kitöltött Ft-ár

## Következő gate

**Spec:** fagyasztva. **Termék:** PCE rendszer (F1–F3, flag). **Vevő:** klinika/intézmény. **Éles F2:** CE / in-house / OQ-17, nem sales-kapcsoló.
