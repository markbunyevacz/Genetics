# PROCESS-HISTORY — PCE-SPEC-v1.1

LIVE-UPDATE. Hibák nem kerülnek felülírásra.

## 1. Phase log

| Fázis | Név | Kezdés | Zárás | Státusz | Input | Output | Hibák |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P00 | Bootstrap | 2026-08-12 | 2026-08-12 | DONE | User request (write-spec, teljes követelménylista); I-01 vázlat | Domain: MedTech / PGx-CDSS / HU+EU; scaffold `docs/pce/` | — |
| P01 | Source ingestion | 2026-08-12 | 2026-08-12 | DONE | I-01–I-09 | SOURCE-INVENTORY, SOURCE-REGISTRY | — |
| P02 | Critical review | 2026-08-12 | 2026-08-12 | DONE | Inventory + primer fetch | VALIDATED-CLAIMS VC-01–VC-10 | VC-01/02/03/04/05/06 |
| P03 | Claim validation | 2026-08-12 | 2026-08-12 | DONE | CQ a P02-ből | VCT | VC-09, VC-10 UNVERIFIABLE |
| P05 | Deliverable generation | 2026-08-12 | 2026-08-12 | DONE | Plan + VCT | PCE-SPEC-v1.1 + A–D mellékletek | — |
| P06 | Plan-vs-content | 2026-08-12 | 2026-08-12 | DONE | Plan checklist | README + ez a napló | — |

**Nem futtatott:** P04 work-package gate (a plan rögzítette a hatókört); P07 (P06 után, ha gap); P08 translation; P09 fusion. G0–G6 user-gate-ek a cloud-agent plan-jóváhagyással helyettesítve (A1–A10 explicit feltevés).

## 2. Decision log

| ID | Fázis | Döntés | Opciók | Választás | Indok | User |
| --- | --- | --- | --- | --- | --- | --- |
| D-01 | P00 | Nyelv | HU / EN / bilingual spec | HU, ID-k EN | A felhasználó és az I-01 magyar | implicit |
| D-02 | P00 | Hatókör | PRD only / PRD+SRS / +tickets +counsel | PRD+SRS + A–D; nincs ticket, nincs counsel | Plan; write-spec §5 follow-up külön kör | plan approve |
| D-03 | P00 | Gyártónév | Agentize Kft. (I-01) / kitalálni / repo-tulajdonos | Repo-tulajdonos, név nélkül (A9) | IR-01: nem kitalálunk jogi entitást | plan |
| D-04 | P05 | F1 default L3 | PharmCAT VCF-en / outside-call | Outside-call default; VCF+PharmCAT kockázatként dokumentálva | YouScript-minta; OQ-05 gyengülés | plan |
| D-05 | P05 | Üzleti TAM/versenytárs | Be / ki | Ki a SRS-ből | Plan: nem SRS | plan |
| D-06 | P02 | OQ-02 | Nyitva hagyni / lezárni primerrel | Lezárni: 12 vs 14 | Lancet + CPT 2019 | — |

## 3. Error log

| ID | Fázis | Típus | Leírás | Escalation | Resolution |
| --- | --- | --- | --- | --- | --- |
| E-01 | P02 | Hallucinated / unsourced legal cite | I-01 FR-100 8. §-t használt tanácsadásra | Retry: primer törvény | VC-03 |
| E-02 | P02 | Hallucinated / conflated standard | EESZT ISO = 13485 keverés | Retry: 4. melléklet | VC-01 |
| E-03 | P02 | Scope / overclaim | Class I „meg sem jelenik” | Retry: MDCG PDF | VC-04 |
| E-04 | P03 | Silent verification risk | Digital Omnibus OJ nem fetch-elve | Mark [NEEDS VERIFICATION] | VC-09; dátum tervezési órának marad |
| E-05 | P00 | Tool | Notion MCP needsAuth | Skip Notion; git repo | docs/pce/ |

## 4. File timeline

| Fájl | Létrehozva | Módosítva | Státusz |
| --- | --- | --- | --- |
| docs/pce/README.md | P00/P05 | P06 | DRAFT |
| docs/pce/PCE-SPEC-v1.1.md | P05 | P06 | DRAFT |
| docs/pce/A-intended-purpose-and-modules.md | P05 | — | DRAFT |
| docs/pce/B-architecture-and-interfaces.md | P05 | — | DRAFT |
| docs/pce/C-eeszt-f0-checklist.md | P05 | — | DRAFT |
| docs/pce/D-risk-and-traceability.md | P05 | — | DRAFT |
| docs/pce/ProcessArtifacts/* | P01–P06 | live | DRAFT |
