# SOURCE-INVENTORY — PCE-SPEC-v1.2

| | |
| --- | --- |
| **Fázis** | P01 (ingestion) + P01b (v1.2 hibrid-brief) |
| **Dátum** | 2026-08-12 |
| **Hatókör** | A v1.2 speccsomaghoz felhasznált források |

## Bemeneti dokumentumok

| ID | Fájl / forrás | Formátum | Nyelv | Szerep | Szavak (kb.) |
| --- | --- | --- | --- | --- | --- |
| I-01 | PCE-SPEC-v1.0 (feltöltött vázlat, 2026-08-09); másolat: `docs/pce/Sources/PCE-SPEC-v1.0.md` | md | HU | Előző PRD-váz; **nem** kanonikus | ~6 500 |
| I-02 | Felhasználói brief: MDCG / 2008/XXI / EESZT / EHDS korrekciók + L0–L7 architektúra + versenytársak + árazás | md (chat) | HU | Termékstratégiai input; üzleti részek deszkópolva | n/a |
| I-03 | 2008. évi XXI. törvény (njt / net.jogtar) | HTML | HU | Humángenetikai jog | primer |
| I-04 | 29/2022. (I. 31.) Korm. rendelet + 294/2025. (IX. 25.) Korm. rendelet 4. melléklet | HTML | HU | EESZT fejlesztői követelmények | primer |
| I-05 | MDCG 2019-11 Rev.1 (2025-06-17), health.ec.europa.eu | PDF | EN | MDSW minősítés/osztályozás | primer |
| I-06 | Swen et al., Lancet 2023;401:347–356 (PREPARE) | PDF/HTML | EN | Klinikai evidencia | primer |
| I-07 | van der Wouden et al., Clin Pharmacol Ther 2019;106:866–873 (PGx-Passport) | HTML | EN | 14-génes panel | primer |
| I-08 | PharmCAT changelog (F5 removal, v2.11.0) | HTML | EN | Change-control bizonyíték | primer |
| I-09 | e-egeszsegugy.gov.hu/fejlesztoknek | HTML | HU | EESZT fejlesztői portál | primer |
| I-10 | Felhasználói hibrid-brief: F2/F3 képesség F1 minőségben; „regulatory bypass” elemzés; shadow/HITL/GDPR/FHIR váz | md (chat) | HU | v1.2 termék- és szabályozási input; blog-URL-ek L4/L5 | n/a |
| I-11 | OQ technikai csomag: FR-461 gateway, FR-410-EDU szabályok, vak HITL; A10 félreolvasás (72 h mint shadow TTL) | md (chat) | HU | v1.2 finomhangolás; A10 **nem** átvéve TTL-ként | n/a |
| I-12 | Változáskezelés A10/A15; OQ-csomagok véglegesítése; „double-blind” megfogalmazás | md (chat) | HU | A10 = visszavonás 72 h (törlés vagy anonimizálás); A15 = protokoll-megőrzés; vak ≠ kettős vak | n/a |
| I-13 | Gyártói döntési csomag a v1 blokkolókra (counsel/DPO/RA/ügyvezetés/üzlet kérései) | md (chat) | HU | F melléklet; OQ nem zárva; disclaimer ≠ felelősségkizárás | n/a |
| I-14 | Öt küldhető hivatalos irat vázlata (counsel, DPO, intézményi RA, L3 term sheet, ISO/EESZT owner) | md (chat) | HU | Outbound/; vázlat hibák javítva (NG-01, EESZT FHIR, Art. 62 mint tény, FR-100 keverés) | n/a |
| I-15 | Spec-szakasz lezárása vs fejlesztés indítása a külső OQ-k alatt | md (chat) | HU | §10.2 fagyasztás; F1+ mag kód igen; OQ-k nyitva | n/a |
| I-16 | Eladás klinikáknak a külső OQ-k feltételezésével | md (chat) | HU | Sales/; SKU-L/C/H; klinika=lelet nem CDSS; OQ mint hatályfeltétel | n/a |

## Átfedés

- I-01 ⊂ I-02 strukturálva; I-01 joghelyei I-03/I-04/I-05 ellen ellenőrizve.
- I-06 és I-07 génlistája **nem azonos** (12 vs 14) — ez a v1.1 OQ-02 lezárása.
- I-02 üzleti/TAM/versenytárs anyaga **nem** került a SRS-be (deszkóp: üzleti dosszié ≠ követelmény).
- I-11 az OQ-05/15/16 **technikai** csomagja; az OQ-kat nem zárja. I-11 A10=shadow-TTL állítása **elvetve** (VC-12).
- I-12 A10-et visszavonási kaszkádra szűkíti; vak ≠ kettős vak.
- I-13 gyártói kérés a címzetteknek; F.6 üresen marad külső aláírásig.
- I-14 az I-13 kéréseit címzett-kész irattá alakítja; a vázlat **nem** szó szerinti, ahol a spec mást mond (Outbound/README javítótábla).
- I-15 a spec-írást fagyasztja; a F1+ mag kódot elválasztja a F.6 forgalmazási kaputól.
- I-16: a vevőnek SKU kell a pecsét előtt; a klinika nem F2-t vesz. OQ-k ettől még nyitva.

## Metaadat-ellentmondások

| Tétel | I-01 / I-02 / I-10 | Primer | Kezelés |
| --- | --- | --- | --- |
| EESZT ISO | „ISO-tanúsítás” / 13485-re utaló keverés | 4. melléklet 2.1 = ISO 9001 vagy szoftver-QMS | VALIDATED-CLAIMS VC-01 |
| PREPARE gének | 14-génes PGx-Passport mint design basis | Lancet: 12 gén, 50 variáns | VC-02 |
| FR-100 joghely | 8. § | tanácsadás = 6. § (2); beleegyezés = 8. §; szolgáltató = 12. § | VC-03 |
| Class I | „az MDCG táblázatában meg sem jelenik” | Rule 11c + Annex IV Class I példa | VC-04 |
| „Az orvos dönt” kimenekülés | I-10 elemzi és elutasítja az EU-ban | MDR Rule 11a; MDCG Rev.1 intended purpose | VC-11 REFUTED |
