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
| P05j | PREPARE + YouScript analógia iratokba | 2026-08-12 | 2026-08-12 | DONE | I-19 | OQ-15 §III; market-packs mátrix; OQ-05 IV.a; OQ-16 ClinLabomics-határ | E-14 |
| P06j | Plan-vs-content (I-19) | 2026-08-12 | 2026-08-12 | DONE | PREPARE/YouScript/Tandem/ClinLabomics | VC-14; OQ-k nyitva; nincs kitalált Ft | — |
| P05k | SKU-P ki-fizet + lakat driver | 2026-08-12 | 2026-08-12 | DONE | I-19 „hogyan épül be” | market-packs ki-fizet; OQ-03 default; OQ-15 HITL≠ADR | — |
| P10b | Pecsétekig megerősítés | 2026-08-12 | 2026-08-12 | DONE | User: van-e architektúra-feladat pecsétekig? | README pecsétekig tábla; F.6 + OQ-17; D-24 | — |
| P05l | FR-461 ticket-bontás | 2026-08-12 | 2026-08-12 | DONE | Explicit kérés: gateway csonkolás ticketek | `Engineering/FR-461-gateway-tickets.md`; OQ-16 nyitva | — |
| P10c | Ops kapuk a fagyasztott specből | 2026-08-12 | 2026-08-12 | DONE | User: kötött lánc, majd core-most / telephely-később | README G5 modell; Outbound gyártói vs telephelyi; D-26/27 | — |
| P05m | OQ-16 küldési csomag | 2026-08-12 | 2026-08-12 | DONE | User: első kimenő irat + név-helyettesítés | `OQ-16-kuldesi-csomag.md`; nevek nincsenek kitalálva | — |
| P05n | Gold V0 SYN fixture | 2026-08-12 | 2026-08-12 | DONE | User: JSON fixture + CPIC 0,5% szelet | `Engineering/fixtures/gold-v0/`; S040–S042 | — |
| P05o | Gold V0 TC-GW kiegészítés | 2026-08-12 | 2026-08-12 | DONE | User: SYN folytatás; 461-11 mind a 11 | k-cella, rarest `*3x2/*3x2`, CYP2C19 keep-6, monitor | — |
| P05p | Gateway SYN szim 461-01/02 | 2026-08-13 | 2026-08-13 | DONE | User: Python ATC4 + negyedév a Gold V0-n | `Engineering/gateway_sim/`; G1/G2/C2 üresen | — |
| P05q | Gateway SYN szim 460 + 461-03 | 2026-08-13 | 2026-08-13 | DONE | User: PII-strip + dózis-tiltás | `strip_pii_fr460`, `suppress_dose_fr461_03`; opák ID teszt | — |
| P05r | main-only + könyvtár-takarítás + gateway/F1+ kód | 2026-08-13 | 2026-08-13 | DONE | User: merge, csak main; nagytakarítás; prod-like terv | `src/pce_gateway/`; `src/pce_report/`; tag `archive/pre-cleanup-2026-08-13` | — |
| P06r | Spec vs delivery plan tételes P06 | 2026-08-13 | 2026-08-13 | DONE | User: hasonlítsd a speccel; dataflow+UX teljesség | `SPEC-PLAN-TRACE.md`; `DATAFLOW-AND-UX.md`; bővített `DELIVERY-PLAN.md` | — |
| P05s | Klinikai kapu + B.3/B.4 SYN (WP-C/K/F/X/Q/U) | 2026-08-13 | 2026-08-13 | DONE | P06r: FR-100 nélküli PDF = spec-sértés | `src/pce_clinical/`; `src/pce_ui/`; G12 GatewayEvent; 60 unittest | — |
| P06s | Plan-vs-content a klinikai láncra | 2026-08-13 | 2026-08-13 | DONE | TRACE NOW 21/27 PARTIAL; F1+ dataflow 8/8 | SPEC-PLAN-TRACE §1/§9 | — |
| P06t | Tételes válasz-dokumentum a user négy pontjára | 2026-08-13 | 2026-08-13 | DONE | User: nem látszott a válasz | `Engineering/VALASZ-SPEC-TERV.md` | — |
| P05u | Árnyék-motor + HITL store/UI (WP-M/H) | 2026-08-13 | 2026-08-13 | DONE | P06t: 5 F1s MISSING; tilos kitalált PM | `src/pce_shadow/`; `src/pce_hitl/`; `src/pce_ui/hitl.html`; S044–S047 | VC-15 |
| P06u | Plan-vs-content az F1s láncra | 2026-08-13 | 2026-08-13 | DONE | TRACE NOW 26/27 PARTIAL; F1s dataflow 5/5 | TRACE + DATAFLOW rescore; 78 unittest | — |
| P06v | Felesleges plusz doksi törlése | 2026-08-13 | 2026-08-13 | DONE | User: ne generálj új doksit mindenre | `VALASZ-SPEC-TERV.md` törölve; a TRACE/DELIVERY-PLAN/DATAFLOW marad | — |
| P05w | PREPARE-12 CPIC + VCF gold + forráshiány a termékben | 2026-08-13 | 2026-08-13 | DONE | User: van/nincs tábla; PM=szegény metabolizáló; hatóanyag-kód; teljes rendszer | `prepare12/` extract; `vcf-gold-v0/`; `forras_allapot`; PSEUDO ATC5 | VC-15 |
| P06w | Plan-vs-content a 6 user-pontra | 2026-08-13 | 2026-08-13 | DONE | TRACE/DELIVERY/DATAFLOW/registry; 89 unittest | SPEC-PLAN-TRACE §10 | — |
| P05x | Spec-validáció: 7 karakteres kód + hivatalos pin + lelet-szöveg | 2026-08-13 | 2026-08-13 | DONE | User 5 pont: forrás-letöltés; szegény címke; „lelet olvas”; 5 vs 7; allélhívó | `Sources/official/`; A14/FR-461 D-38; `gyogyszerlista_a_leleten`; `diplotipus_forras_hu` | E-18 |
| P06x | Plan-vs-content az 5 user-pontra | 2026-08-13 | 2026-08-13 | DONE | TRACE §11; official pin teszt | SPEC-PLAN-TRACE §11 | — |
| P05y | J-1…J-6 kapuk | 2026-08-13 | 2026-08-13 | DONE | User: kódszintű F-07 injekció + tételes lista | allow-list B.4.1; pheno-gold-v0 N=32; A.4.1; FR-110 Art. 12(3); §0 Owner/Due | E-19 |
| P05z | Árazás: megfigyelt vs következtetés | 2026-08-13 | 2026-08-13 | DONE | User: YouScript 365 USD; HIS-plafon; javasolt Ft-sáv | `Sales/pricing.md`; S056–S058; VC-16 | E-20 |
| P05aa | G melléklet: öt nyitott tétel | 2026-08-13 | 2026-08-13 | DONE | User PCE-G-v1.0 | `G-open-items.md`; S055 LEZÁRVA; DSR két artefaktum; OQ-05/06/16 javaslat pecsét nélkül | E-19 zárva (EUR-Lex 200) |
| P05ab | S060 Health Canada PRCI + S062 DHCS DDG V2.2 pin | 2026-08-13 | 2026-08-13 | DONE | User: PRCI guidance URL + DHCS-DDG-V2-2.pdf | S060/S062 **LEZÁRVA** `[V]`; k=11 HC primer; A14 k≥5 **nem** pecsét; DHCS élő Incapsula → Wayback | E-21 |
| P05ac | Magyar próza: szemantika/szintaxis | 2026-08-14 | 2026-08-14 | DONE | User: érthetetlen mondatok; független ágens | Névelő (a/az); ATC4 vs ATC5; két határidő; hiányzó igék; OQ-16 A1 ATC5; A14 változatlan | E-22 |
| P05ad | F2 CDS Hooks cső lakattal (G5) | 2026-08-14 | 2026-08-14 | DONE | User: G5 feloldás; fejlesztés végén ki/be; freeze ignorálva | `src/pce_cds/`; `cds.html`; TRACE FR-520 PARTIAL; Sales/Outbound/A–G | E-23 |
| P06ac | Plan-vs-content a F2 csőre | 2026-08-14 | 2026-08-14 | DONE | TRACE §16; 124 unittest | SPEC-PLAN-TRACE §16; WP-F2 | — |

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
| D-29 | P05n | SYN Gold V0 + CPIC freq | Synthea ATC mint primer / CPIC European szelet | **CPIC xlsx European**; 0,5% A14; GeT-RM ≠ freq; Synthea ≠ ATC default; opák ID | S040–S042 | user |
| D-30 | P05o | Freq-config bake | Teljes 4005-ös CYP2D6 lap / allowlist | **Allowlist** 34 CYP2D6 + 6 CYP2C19; ismeretlen = ritka; PharmGKB gén–gyógyszer TSV ≠ A14 | S040 | user |
| D-31 | P05p | OQ-16 név + SYN kód | G1/G2/C2 kitalálása / üres + 461-01/02 szim | **Üres** helyettesítés (A9). Szim csak ATC+idő; PII/k-cella később | A9; user | user |
| D-32 | P05q | 460+461-03 vs k-cella most | PII/dózis most / 461-04 váz | **PII+dózis most**; k-cella a 461-06 freq után (ticket-sorrend) | FR-461 sorrend; user | user |
| D-33 | P05r | Hol dolgozzunk + duplikátumok | Feature ágak / csak `main`; docs alatti szim | **Csak `main`**, ez a repo. Gold V0 → `tests/fixtures/`; kód → `src/`. Visszaállítás: tag. | User 2026-08-13 | user |
| D-34 | P06r | Delivery plan vs teljes spec | Részleges WP-G/R / tételes P06 + hiányzó L0–L6 WP | **36 FR mind nevesítve**; NOW 27/27 terv; kód 0 FULL. Render FR-100 után. EDU null megengedett forrás hiányában. | User 2026-08-13 | user |
| D-35 | P05s | Klinikai lánc a fagyasztott B szerint | Terv-only / SQLite+stdlib HTTP a B.3/B.4-re | **Kód**: `pce_clinical` + labor HTML; FR-100 CLI sem kerülhető; NFR-031 TLS SYN-en localhost (dokumentált eltérés) | P06r rés FR-100 | user |
| D-36 | P05u | NM + erős gátló → PM a shadowban | Kitalált PM / forrásolt null, amíg CPIC konszenzus nincs | **Null `functional_phenotype`**; FDA strong class ATC5-ön; ATC4 nem paroxetin; Table 2a csak stratégia-kategória | S046; B.6.2 „a tábla szerint”; user: pótold | user |
| D-37 | P05w | Hol a NM→szegény tábla; ATC pontosság | Kitalált SSRI NM→szegény / opioid tábla keverése / hiány jelzése | **Amit van, azt írjuk; ami nincs, azt jelezzük.** SSRI 2023: nincs sor. FDA: erős gátló. Opioid 2020: van szabály, de nem a paroxetin-SSRI példa. ANON marad ATC4 (spec). Párosítás: 7 karakteres hatóanyag-kód (PSEUDO+hozzájárulás). Nem „egy szer = egy beteg”. | S045–S050; user 6 pont | user |
| D-38 | P05x | Spec-validáció: 5 vs 7 karakteres kód | Fagyasztott A14 ATC4 / 7 karakteres hatóanyag-kód | **7 karakteres WHO hatóanyag-kód a default** (§10.2 (c)). A14/FR-450/460/461 javítva. DPO durvíthat; akkor párosítás szünetel. k≥5 és 0,5% marad. Nem betegazonosító. | S032; user 2026-08-13 | user |
| D-39 | P05y | J-1 vs J-3 sorrend; J-2 osztály | Csak J-1 / csak J-3 / mind a hat | **Mind a hat.** J-1 allow-list ma. J-3 pheno-gold **üres** funkcionális fenotípus (nincs kitalált NM→szegény). J-2 A.4.1 + NFR-070a/b, OQ-06 nyitott. Ár **nincs** a specben. | User 2026-08-13 kódszintű lista | user |
| D-40 | P05z | Ft-sáv a specben vs Sales | Listaár a specbe / csak Sales következtetés | **Sales/pricing.md.** A spec §11 kötés marad; a 6–35 M Ft **nem** megfigyelt listaár. DrugMap VC-10. EKR 88,3 M Ft nincs pinelve. | User 2026-08-13 árazás | user |
| D-41 | P05aa | G öt tétel pecsét vs javaslat | Pecsétek / csak javaslat + S055 pin | **S055 LEZÁRVA.** OQ-05/06/16 **nem** pecsét. (a) IIa-safe fallback 2026-10-31; Class I MDSW default; k≥11 javaslat A14 változatlan; 15 felíró alatt `[Yp]=0`. | User G v1.0 | user |
| D-42 | P05ab | S060/S062 pin vs A14 átírás | k=11 pecsét / pin + javaslat | **Pin.** S060 `[V]` cél-cella 11; S062 `[V]` 11 / 20 000 (Wayback; élő Incapsula). **Nem** EU-jog. A14 k≥5 / 0,5% `[ASSUMPTION]` **marad**. DHCS v3.0 nincs pinelve. | User PRCI + DDG URL | user |
| D-43 | P05ac | Próza javítás vs tényátírás | Újraírás / csak nyelv | **Csak nyelv.** Tények, pecsétek, A14 k≥5, Ft-sáv **nem** változtak. A.1 „az aktuális” a `statements.py`-ban is. | User: minden írás | user |
| D-44 | P05ad | F2 cső a dobozban vs 404 stub | Várni a pecsétet / megírni a csövet lakattal | **Cső megvan, kimenet lakat.** Külön `pce_cds` processzus. Repo `LIVE_CDS=false`. ON = signed flag, nem újraírás. Spec freeze §10.2 (c) user-kérés. OQ-k **nem** pecsét. | G5; FR-520; NG-07 | user |

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
| E-15 | P05q | Hallucinated PII / API mismatch | User-minta: „Kovács János” / TAJ 123456789; `entry.resourceType`; DSTU2 `doseQuantity` | Gold V0 opák ID; FHIR R4 `entry.resource` + `doseAndRate` | D-32 |
| E-16 | P05u | Hallucinated phenotype mapping | Spec AC „NM + erős gátló → PM/IM a tábla szerint” — CPIC 2023: konszenzus **nincs** | Switch: FDA class + sourced null; dummy PM = fail | VC-15; D-36 |
| E-17 | P05w | Jargon / information loss | PM betűszó magyarázat nélkül; „durvább kód” / „szer azonosítja a beteget”; extra doksi | Magyar van/hiányzik a kártyán; hatóanyag-kód a párosításhoz; TRACE/DELIVERY/DATAFLOW only | D-37 |
| E-18 | P05x | Jargon / spec mismatch | „A lelet olvassa a gyógyszerlistát”; „allélhívó ki”; fagyasztott 5 karakteres kód vs WHO 7 | Lelet-szöveg: guideline-lista, nem felírás-szűrés; PharmCAT NamedAlleleMatcher magyarázat; A14 D-38 | D-38 |
| E-19 | P05y | API / authority fetch | EUR-Lex GDPR HTML/PDF 202 empty body | Irish DPC CS2025 pin Art. 12(3)-ra; S055 hátravan | J-4 |
| E-19b | P05aa | API / authority fetch (E-19 zárás) | EUR-Lex 202 empty body **lejárt**: HTML 200, 809 035 byte | Pin HTML+PDF; Art. 12(3)/12(4)/17(1) a HTML-ből; S055 LEZÁRVA | D-41 |
| E-20 | P05z | Authority fetch | YouScript HTML urllib 403; EKR001266472024 karbantartási oldal | WebFetch 365 USD; SMART+Semmelweis pin; EKR összeg `[R]` | D-40 |
| E-21 | P05ab | Authority fetch | Élő `dhcs.ca.gov/.../DHCS-DDG-V2-2.pdf` Incapsula HTML (212 B), nem PDF. Wayback `/web/2023/` és `/web/2024/` 429. | Wayback `/web/2022/` a V2.2 PDF-et adta (1 709 986 B, 71 oldal, CreationDate 2023-02-17). v3.0 nincs pinelve. | D-42 |
| E-22 | P05ac | Incomplete verification | Első független próza-ellenőrzés FAIL: maradék névelő (aláírt / IIa / esélyhányados / első) és *analogia*. | Retry: célzott javítás; 2. scan FAIL (ige/FDA/US); 3. scan FAIL (Cardet / „akkor”); 4. scan **CLEAN**. Unittest 113 OK. | P05ac |
| E-23 | P05ad | Cross-reference / product mismatch | Sales G5: F2 bent van lakattal. TRACE FR-520 LOCK + „endpoint nincs”; OQ-15 „képtelen kártyát adni”; demó 403. | Switch: külön `pce_cds` processzus; F1+ 404 marad; lock = 200 üres `cards`. Outbound/Sales/TRACE javítva. Unittest 124 OK. | D-44 |

## 4. File timeline

| Fájl | Létrehozva | Módosítva | Státusz |
| --- | --- | --- | --- |
| docs/pce/README.md | P00/P05 | P05ad (D-44 F2 cső) | v1.2; G5 cső lakattal |
| docs/pce/PCE-SPEC-v1.2.md | P05b (git mv) | P05ad (D-44 FR-520/530) | v1.2; ATC-klauzula §10.2 (c); F2 cső |
| docs/pce/A-intended-purpose-and-modules.md | P05 | P05ad | DRAFT v1.2; L6-cds lakat |
| docs/pce/B-architecture-and-interfaces.md | P05 | P05ad (B.4.4 `pce_cds`) | DRAFT v1.2 |
| docs/pce/C-eeszt-f0-checklist.md | P05 | P05f (C.4 Outbound linkek) | DRAFT v1.2 |
| docs/pce/D-risk-and-traceability.md | P05 | P05ad (R-010 / FR-520) | DRAFT v1.2 |
| docs/pce/E-shadow-hitl.md | P05b | P05ad (E.8 `pce_cds`) | DRAFT v1.2 |
| docs/pce/F-decision-package.md | P05e | P05ad (D-44 nem pecsét) | DRAFT v1.2; OQ-k ELŐTERJESZTVE |
| docs/pce/Outbound/* | P05f | P05ad (OQ-05/15 cső vs 404) | TERVEZET; 16 első kimenő; A9 |
| docs/pce/Sales/* | P05g | P05ad (demó üres cards) | TERVEZET rendszerlicenc |
| docs/pce/Sources/S028-* | P01c | P05i | L5 jegyzet + PDF |
| docs/pce/ProcessArtifacts/* | P01–P06 | P05ad (D-44, E-23) | DRAFT |
| docs/pce/Engineering/* | P05l | P06ac (WP-F2, TRACE §16) | SYN ticketek; P06 mátrix; kód `src/` |
| src/pce_shadow/ | P05u | P05w | F1s élő párosítás; forráshiány magyarul |
| src/pce_hitl/ | P05u | P05w | vak ellenőrző API + `hitl.sqlite` |
| src/pce_ui/hitl.html | P05u | P05w | van/hiányzik lista a vak lépés után |
| src/pce_clinical/coverage.py | P05w | P05x | FR-210; diplotípus-forrás magyarul |
| docs/pce/G-open-items.md | P05aa | P05ad (124 teszt; kill-switch kód) | Javaslat, nem pecsét; S055/S060/S062 LEZÁRVA |
| docs/pce/Sources/official/ | P05x | P05ab | + GDPR HTML/PDF; EMA 0,09; MDCG 2021-24; HC PRCI; DHCS DDG V2.2 (19 `ok`) |
| tests/fixtures/pheno-gold-v0/ | P05y | P05y | N=32; G3 nevező |
| src/pce_report/schema.py | P05r | P05y | B.4.1 allow-list |
| tests/fixtures/f1plus-v0/prepare12/ | P05w | P05w | 12 gén CPIC pin |
| tests/fixtures/vcf-gold-v0/ | P05w | P05w | 3 SYN missing-to-ref |
| docs/pce/Sales/pricing.md | P05z | P05aa | `[Yp]=0` 15 felíró alatt; `[Y*]` ESTIMATE |
| docs/pce/Sources/market/ | P05z | P05z | SMART + Semmelweis/KÉ pin |
| src/pce_cds/ | P05ad | P05ad | F2 CDS Hooks cső; repo `LIVE_CDS=false` |
| src/pce_ui/cds.html | P05ad | P05ad | F2 lakat-UI |
| tests/test_cds.py | P05ad | P05ad | lock / ON paraméter / timeout / IIa-safe / izoláció |
