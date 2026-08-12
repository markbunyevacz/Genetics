# SOURCE-INVENTORY — PCE-SPEC-v1.1

| | |
| --- | --- |
| **Fázis** | P01 (ingestion) |
| **Dátum** | 2026-08-12 |
| **Hatókör** | A v1.1 speccsomaghoz felhasznált források |

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

## Átfedés

- I-01 ⊂ I-02 strukturálva; I-01 joghelyei I-03/I-04/I-05 ellen ellenőrizve.
- I-06 és I-07 génlistája **nem azonos** (12 vs 14) — ez a v1.1 OQ-02 lezárása.
- I-02 üzleti/TAM/versenytárs anyaga **nem** került a SRS-be (deszkóp: üzleti dosszié ≠ követelmény).

## Metaadat-ellentmondások

| Tétel | I-01 / I-02 | Primer | Kezelés |
| --- | --- | --- | --- |
| EESZT ISO | „ISO-tanúsítás” / 13485-re utaló keverés | 4. melléklet 2.1 = ISO 9001 vagy szoftver-QMS | VALIDATED-CLAIMS VC-01 |
| PREPARE gének | 14-génes PGx-Passport mint design basis | Lancet: 12 gén, 50 variáns | VC-02 |
| FR-100 joghely | 8. § | tanácsadás = 6. § (2); beleegyezés = 8. §; szolgáltató = 12. § | VC-03 |
| Class I | „az MDCG táblázatában meg sem jelenik” | Rule 11c + Annex IV Class I példa | VC-04 |
