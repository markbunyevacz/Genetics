# PROCESS-HISTORY — PCE-SPEC-v1.2

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
| P01b | Source ingestion (hibrid) | 2026-08-12 | 2026-08-12 | DONE | I-10 hibrid-brief | Inventory + registry S023–S031 | — |
| P05b | Deliverable restart (v1.2) | 2026-08-12 | 2026-08-12 | DONE | I-10 + D-07 | PCE-SPEC-v1.2; A rewrite; B/D align; E új | — |
| P05c | OQ technical packages | 2026-08-12 | 2026-08-12 | DONE | I-11 | FR-410-EDU/461/450-BLIND; A10≠TTL; A14/A15 | E-08 |
| P06c | Plan-vs-content (OQ csomagok) | 2026-08-12 | 2026-08-12 | DONE | I-11 | D.3; VC-12; OQ-k nyitva | — |
| P05d | A10/A15 mátrix + v1 sign-off | 2026-08-12 | 2026-08-12 | DONE | I-12 | §0.1; E.5.1; §10.1; nem double-blind | — |
| P05e | Gyártói döntési előterjesztés | 2026-08-12 | 2026-08-12 | DONE | I-13 | F melléklet; OQ ELŐTERJESZTVE; FR-461 monitor | — |
| P05f | Outbound hivatalos iratok | 2026-08-12 | 2026-08-12 | DONE | I-14 | `docs/pce/Outbound/` öt irat + index | E-10, E-11 |
| P06f | Plan-vs-content (Outbound) | 2026-08-12 | 2026-08-12 | DONE | I-14 vs spec | Öt irat spec-hez igazítva; OQ-k nyitva | — |
| P10 | Spec-fagyasztás | 2026-08-12 | 2026-08-12 | DONE | I-15 | §10.2; F1+ mag DEV-NOW; OQ-k nyitva | — |
| P05g | Sales csomag (feltételezett OQ) | 2026-08-12 | 2026-08-12 | DONE | I-16 | `docs/pce/Sales/` (később I-17 felülírja a leletbolt-olvasatot) | E-12 |
| P05h | Sales korrekció: rendszerlicenc | 2026-08-12 | 2026-08-12 | DONE | I-17 | SKU-P; market-packs HU/EU/US; OQ-17 | E-12 |
| P01c | Source ingestion (CureMD PDF) | 2026-08-12 | 2026-08-12 | DONE | I-18 PDF arXiv:2603.14876v1 | Inventory I-18; S028 L5 „elolvasva”; S028-note | E-13 |
| P05i | S028 formális beillesztés + határ | 2026-08-12 | 2026-08-12 | DONE | I-18 + VC-13 | §9.5; FR-710 SHAP-tiltás v1-en; literature-boundary | E-13 |
| P06i | Plan-vs-content (S028) | 2026-08-12 | 2026-08-12 | DONE | Három kért használat vs PDF | G3 marad ≥90%; nincs „állami referenciák” fejezet | — |
| P05j | PREPARE + YouScript analogia iratokba | 2026-08-12 | 2026-08-12 | DONE | I-19 | OQ-15 §III; market-packs mátrix; OQ-05 IV.a; OQ-16 ClinLabomics-határ | E-14 |
| P06j | Plan-vs-content (I-19) | 2026-08-12 | 2026-08-12 | DONE | PREPARE/YouScript/Tandem/ClinLabomics | VC-14; OQ-k nyitva; nincs kitalált Ft | — |
| P05k | SKU-P ki-fizet + lakat driver | 2026-08-12 | 2026-08-12 | DONE | I-19 „hogyan épül be” | market-packs ki-fizet; OQ-03 default; OQ-15 HITL≠ADR | — |
| P10b | Pecsétekig megerősítés | 2026-08-12 | 2026-08-12 | DONE | User: van-e architektúra-feladat pecsétekig? | README pecsétekig tábla; F.6 + OQ-17; D-24 | — |
| P05l | FR-461 ticket-bontás | 2026-08-12 | 2026-08-12 | DONE | Explicit kérés: gateway csonkolás ticketek | `Engineering/FR-461-gateway-tickets.md`; OQ-16 nyitva | — |
| P10c | Ops kapuk a fagyasztott specből | 2026-08-12 | 2026-08-12 | DONE | User: kötött lánc, majd core-most / telephely-később | README G5 modell; Outbound gyártói vs telephelyi; D-26/27 | — |
| P05m | OQ-16 küldési csomag | 2026-08-12 | 2026-08-12 | DONE | User: első kimenő irat + név-helyettesítés | `OQ-16-kuldesi-csomag.md`; nevek nincsenek kitalálva | — |

**Nem futtatott:** P04 work-package gate (a plan rögzítette a hatókört); P07 (P06 után, ha gap); P08 translation; P09 fusion. G0–G6 user-gate-ek a cloud-agent plan-jóváhagyással helyettesítve (A1–A13 explicit feltevés).

## 2. Decision log

| ID | Fázis | Döntés | Opciók | Választás | Indok | User |
| --- | --- | --- | --- | --- | --- | --- |
| D-01 | P00 | Nyelv | HU / EN / bilingual spec | HU, ID-k EN | A felhasználó és az I-01 magyar | implicit |
| D-02 | P00 | Hatókör | PRD only / PRD+SRS / +tickets +counsel | PRD+SRS + A–D; nincs ticket, nincs counsel | Plan; write-spec §5 follow-up külön kör | plan approve |
| D-03 | P00 | Gyártónév | Agentize Kft. (I-01) / kitalálni / repo-tulajdonos | Repo-tulajdonos, név nélkül (A9) | IR-01: nem kitalálunk jogi entitást | plan |
| D-04 | P05 | F1 default L3 | PharmCAT VCF-en / outside-call | Outside-call default; VCF+PharmCAT kockázatként dokumentálva | YouScript-minta; OQ-05 gyengülés | plan |
| D-05 | P05 | Üzleti TAM/versenytárs | Be / ki | Ki a SRS-ből | Plan: nem SRS | plan |
| D-06 | P02 | OQ-02 | Nyitva hagyni / lezárni primerrel | Lezárni: 12 vs 14 | Lancet + CPT 2019 | — |
| D-07 | P05b | F2-in-F1 „bypass” | Élő CDSS F1 köntösben + HITL / elutasítás + hibrid | **Elutasítva** (NG-07); F1+ static + F1s shadow + F2 CE után | I-10 + MDR Rule 11a; nincs FDA kiskapu | user brief |
| D-08 | P05b | Fenokonverzió a leleten | Élő (v1.1) / csak EDU / teljesen ki | FR-410-EDU a leleten; FR-410-LIVE shadow/F2 | Beteg-gyógyszer párosítás = Rule 11a | I-10 |
| D-09 | P05b | Shadow GDPR | Anonim / álnevesített | Default anonim (A12); FR-115 ha longitudinális | I-10 két út; A13 re-ID | I-10 |
| D-10 | P05b | Disclaimer „minden felelősség kizárva” | Be / ki | **Ki** a sablonból | Termékfelelősség / GSPR nem disclaimerezhető | I-10 korrekció A.1.1 |
| D-11 | P05c | A10 mint F1s 72 h TTL | Átvenni / elvetni | **Elvetve** (VC-12); A15 = protokoll-megőrzés | Havi HITL ellentmond a 72 h puffernek; A10 = FR-110 | I-11 |
| D-12 | P05c | OQ-05/15/16 lezárása a technikai csomaggal | Lezárni / nyitva + csomag | **Nyitva**; csomag = FR-410-EDU, FR-461, FR-450-BLIND | Nem jogi vélemény | I-11 |
| D-13 | P05c | Anonim ATC max szint | ATC5 / ATC4 / ATC3 | Default **ATC4**; ATC5 tilos; ATC3 DPO | WHO szintek S032; G3 tradeoff R-020 | I-11 |
| D-14 | P05d | Visszavonáskor HITL | Mindig töröl / töröl vagy anonimizál | **Törlés vagy irreverzibilis anonimizálás** 72 h (A10); A15 csak anonim vagy FR-115 | I-12 változáskezelés | I-12 |
| D-15 | P05e | OQ-k lezárása gyártói kéréssel | Lezárni / előterjeszteni | **ELŐTERJESZTVE** (F); külső aláírás kell | Nem hamisítunk counsel/DPO pecsétet | I-13 |
| D-16 | P05e | Disclaimer mint MDSW-kimenekülés | Felelősségkizárás / A.1.1 | **A.1.1 marad**; nem felelősségkizárás | FR-490; A.0 | I-13 |
| D-17 | P05f | I-14 vázlatok szó szerint? | Átmásolni / spec szerint javítani | **Javítva**: A.1 verbatim; FR-100≠FR-115; Art. 62 kérelem; L3≠NG-01; EESZT≠FHIR | IR-01, VC-01, NG-01, NG-05 | I-14 |
| D-18 | P10 | Spec-szakasz a külső OQ alatt | Tovább írni / fagyasztani + kód | **Fagyasztva**; F1+ mag indul; OQ-k ELŐTERJESZTVE | I-15; F.6 ≠ git-stop | I-15 |
| D-19 | P05g | Eladás a pecsét előtt | Várni F.6-ra / készíteni a SKU-t hipotézisen | Sales csomag (I-16: klinika=lelet — **I-17 felülírja**) | G4 | I-16 |
| D-20 | P05h | Mit adunk el? | Laborlelet / **rendszer** F1–F3 flaggel | **SKU-P**; labor csatlakozó; HU/EU/US; F2 LOCK≠hiány | I-17; NG-07; G5 | I-17 |
| D-21 | P05i | S028 beépítés | Állami SOTA + G3=83,1% + SHAP-FR + RWE / L5 jegyzet + határ | **L5 jegyzet**; G3 ≥90% marad; SHAP nem v1 FR; RWE tiltott; **nincs** „állami referenciák” fejezet | VC-13; IR-01 | I-18 |
| D-22 | P05j | PREPARE/YouScript iratba | Szó szerinti user-számok / primer Lancet + publikus YouScript lista | **Primer**: p=0,0075; 365 USD lista; Tandem nem pecsét; ClinLabomics nem k | VC-14 | I-19 |
| D-23 | P05k | Ki fizet + lakat driver | Labor viszonteladó / SKU-P SaaS + `[Yl]` opcionális | Klinika fizeti SKU-P-t; labor nem viszonteladó; lakat előbb NG-07, aztán `[Ya]` | I-19 finomítás | I-19 |
| D-24 | P10b | Iratírás pecsétekig | Tovább spec / fagyasztva + F1+ mag | **Megerősítve** §10.2; OQ-k nyitva; nincs `v1.2-Core-Specification.md`; nincs új architektúra-fejezet | README pecsétekig; B melléklet | user |
| D-25 | P05l | FR-461 ticketek a fagyasztott specből | Spec-módosítás / engineering bontás | **Engineering/**; SYN only; A14 assumption; nem OQ-16 pecsét | FR-461; E.3.1; TC-GW-010..020 | user |
| D-26 | P10c | Küldési lánc | Párhuzamos OQ-15 / kötött 16→15→05→03→01 | **Kötött küldés**; HIS továbbra is 15+16 pecsét; FR-115 ≠ FR-100; ISO ≠ megújítás | §10.2 fallback; OQ-16 I.0 | user |
| D-27 | P10c | Core most vs irat a megrendelőkor | Minden OQ most / minden OQ a vevőkor | **G5:** egy bináris SYN-en. Gyártói OQ-05/01 most. Telephelyi 16→15→03 nevesített megrendelőkor. Flag = telepítés. | SKU-P; user | user |
| D-28 | P05m | OQ-16 küldési boríték | Nevek beírása a gitbe / boríték + A9 | **Boríték**; G1/C2 a küldőé; labor ≠ OQ-16; 16-A termék-DPO most, 16-B HIS-DPO névvel | A9; user OQ-16 első irat | user |

## 3. Error log

| ID | Fázis | Típus | Leírás | Escalation | Resolution |
| --- | --- | --- | --- | --- | --- |
| E-01 | P02 | Hallucinated / unsourced legal cite | I-01 FR-100 8. §-t használt tanácsadásra | Retry: primer törvény | VC-03 |
| E-02 | P02 | Hallucinated / conflated standard | EESZT ISO = 13485 keverés | Retry: 4. melléklet | VC-01 |
| E-03 | P02 | Scope / overclaim | Class I „meg sem jelenik” | Retry: MDCG PDF | VC-04 |
| E-04 | P03 | Silent verification risk | Digital Omnibus OJ nem fetch-elve | Mark [NEEDS VERIFICATION] | VC-09; dátum tervezési órának marad |
| E-05 | P00 | Tool | Notion MCP needsAuth | Skip Notion; git repo | docs/pce/ |
| E-06 | P05b | Scope / regulatory bypass | v1.1 F1 tartalmazott élő fenokonverziót a leleten — I-10 szerint ez F2-hatás | Restart P05: szűkítés F1+-ra; shadow külön | D-07, D-08; VC-11 |
| E-07 | P01b | Authority | I-10 [1]–[7] blog/preprint mint Rule 11a bizonyíték | Nem L1-ként használni | S023–S029 L4/L5; primer S004/S020 |
| E-08 | P05c | Cross-reference breakage / assumption mix-up | I-11 A10-et F1s 72 h puffernek olvasta | Retry: A10 eredeti jelentés + A15 | VC-12 |
| E-09 | P05d | Terminology | I-12 „double-blind validation” | Szekvenciális reviewer-vak; a motor nem vak | FR-450-BLIND; E.4.1 |
| E-10 | P05f | Scope / overclaim | I-14 OQ-05 pecsét előre „nem MDSW”; OQ-15 Art. 62 mint tény | Igen/Nem/Feltétellel; kérelem nem határozat | Outbound OQ-05/15 |
| E-11 | P05f | Cross-reference / spec mismatch | I-14 L3 = NG-01 riasztás + csak kivétel díjazva; OQ-01 = EESZT FHIR/SSL | NG-01 = non-goal; minden lelet aláírás; Redmine + ISO 9001 2.1 | Outbound OQ-03/01 |
| E-12 | P05g | Scope / product mismatch | I-16 sales a klinikának leletet adott el | Retry: SKU-P rendszer; market packs | I-17; D-20 |
| E-13 | P01c/P05i | Scope / overclaim | I-18: S028 = F1s állami SOTA; Top-5 83,1% = G3/R-020; SHAP = F2 mag; PCE-RWE | Primer PDF; CORRECTED nem silent drop | VC-13; D-21; §9.5 |
| E-14 | P05j | Hallucinated / wrong cite | I-19: PREPARE p=0,0034; PMC7195220 mint YouScript; ClinLabomics mint k-anon; Tandem mint OQ-05 pecsét; TSI mint F1+ siker; ágyszám-ár | Primer Lancet + vendor oldalak; CORRECTED | VC-14; D-22 |

## 4. File timeline

| Fájl | Létrehozva | Módosítva | Státusz |
| --- | --- | --- | --- |
| docs/pce/README.md | P00/P05 | P10c (G5 core-most; gyártói vs telephelyi OQ) | v1.2 FAGYASZTVA |
| docs/pce/PCE-SPEC-v1.2.md | P05b (git mv) | P05j (§9.4 PREPARE p=0,0075) | v1.2 FAGYASZTVA; S028+PREPARE határ |
| docs/pce/A-intended-purpose-and-modules.md | P05 | P05i (A.3 SHAP≠FR-710) | DRAFT v1.2 |
| docs/pce/B-architecture-and-interfaces.md | P05 | P05c | DRAFT v1.2 |
| docs/pce/C-eeszt-f0-checklist.md | P05 | P05f (C.4 Outbound linkek) | DRAFT v1.2 |
| docs/pce/D-risk-and-traceability.md | P05 | P06j (VC-14) | DRAFT v1.2 |
| docs/pce/E-shadow-hitl.md | P05b | P05i (E.7 SOTA-határ) | DRAFT v1.2 |
| docs/pce/F-decision-package.md | P05e | P10b (F.6 + OQ-17) | DRAFT v1.2; OQ-k ELŐTERJESZTVE |
| docs/pce/Outbound/* | P05f | P05m (OQ-16 küldési boríték) | TERVEZET; 16 első kimenő; A9 |
| docs/pce/Sales/* | P05g | P05j (mátrix + competitor-analogs) | TERVEZET rendszerlicenc |
| docs/pce/Sources/S028-* | P01c | P05i | L5 jegyzet + PDF |
| docs/pce/ProcessArtifacts/* | P01–P06 | P05l (I-20, D-25) | DRAFT |
| docs/pce/Engineering/* | P05l | P05l | SYN ticketek; nem spec |
