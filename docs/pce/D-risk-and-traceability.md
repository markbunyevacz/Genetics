# D melléklet — Kockázat és traceability

| | |
| --- | --- |
| **Dokumentum** | PCE-SPEC-v1.1 Appendix D |
| **Dátum** | 2026-08-12 |
| **Szabvány** | ISO 14971 (kezdeti nyilvántartás, **nem** teljes dosszié); IEC 62304; MDR Annex I GSPR |

A teljes ISO 14971 fájl a QMS-ben (REG-030) készül. Itt a spec-ből következő, **már azonosított** veszélyek és a rájuk kötött követelmények. Új veszély a fejlesztés során → új sor, nem csendes javítás (IR-08).

Súlyosság / előfordulás / detektálhatóság: 1–5. RPN = S×O×D. Küszöb: RPN ≥ 40 vagy S = 5 → kötelező kockázatcsökkentés a v1 előtt.

---

## D.1 Kezdeti kockázati nyilvántartás

| ID | Veszély | Okozó szituáció | Ártalom | S | O | D | RPN | Kockázatcsökkentés (req) | Maradék |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **R-001** | Hiányzó VCF-pozíció = referencia (missing-to-ref) | Naiv default; `--absent-to-ref` vakon | Hamis NM → ellentétes gyógyszerajánlás | 5 | 3 | 2 | 30 | **FR-210**; gold set ≥3 ellentétes eset; PharmCAT flag dokumentált; CI 100% callability | S marad 5; O/D csökken. **RC-003** |
| **R-002** | CYP2D6 SV (del/dup/hybrid) nem detektált | WES/panel nem fedi a szerkezetet | Rossz aktivitás-score, rossz dózis-*szöveg* | 5 | 3 | 3 | 45 | **FR-300** SV-jelzés; `INDETERMINATE` ha nem hívható; outside-call a labor módszerét viszi | Labor módszer (REG-020) |
| **R-003** | CPIC vs DPWG ütközés, a szoftver „szintetizál” | Egyetlen „győztes” ajánlás | Nem létező, egyik forrásban sem szereplő tanács | 4 | 2 | 2 | 16 | **FR-400** mindkét forrás; `unsourced_claims == 0` | Alacsony |
| **R-004** | LLM a klinikai úton | Szabad szöveg, hallucinált dózis | Nem reprodukálható, hamis ajánlás; 6. § (6) sérülés | 5 | 2 | 2 | 20 | **FR-700**, **FR-710**, **NFR-060**; CI call-graph | Tilos a klinikai path |
| **R-005** | Tanácsadás/beleegyezés megkerülése | Admin override, config flag | 2008/XXI. 6. § (2), 8. §, 12. § sérülés | 4 | 2 | 2 | 16 | **FR-100** nem kikapcsolható; negatív teszt adminra | — |
| **R-006** | Visszavonás után cache-elt riport | CDN/HTTP cache, 200 a 410 helyett | 26. § (1) megsemmisítés elmarad | 4 | 3 | 2 | 24 | **FR-110** 410 Gone; kaszkád derived-re; A10 72 h SLA | Audit a törlésről |
| **R-007** | DPYD–fluoropirimidin: a passzív riportot terápiás utasításnak olvassák | F1 intended purpose vs felhasználói percepció | Súlyos toxicitás, ha a labor/klinikus a PDF-et „dózisnak” veszi | 5 | 2 | 3 | 30 | A.1 intended purpose a PDF-en (FR-500); nincs `dose_mg` (FR-410); REG-020 aláíró; OQ-05 | F3-on IIa + klinikai eval |
| **R-008** | Fenokonverzió hallgatólagos kihagyása | Nincs gyógyszerlista, a riport NM-et ad „késznek” | Funkcionális PM NM-ként kezelve | 4 | 3 | 2 | 24 | **FR-220** `clinical_context = ABSENT` explicit; FR-410 nem értékelhető | — |
| **R-009** | Guideline-váltás (F5-eset) után régi riport él | Hardcoded génlista | Elavult, visszavont ajánlás | 4 | 3 | 2 | 24 | **FR-310**, **FR-510**; PharmCAT 2.11.0 mint bizonyíték | P1 a tömeges újragenerálás |
| **R-010** | CDS timeout blokkolja a felírást | Fail-closed | Gyógyszer elmarad, kár a késedelemből | 4 | 2 | 2 | 16 | **FR-520** fail-open 2 s; NFR-011 | F2 |
| **R-011** | PII a motor-logban | Debug dump | GDPR Art. 9 + 2008/XXI. | 3 | 3 | 2 | 18 | **FR-130** CI PII-scanner | — |
| **R-012** | Multi-sample VCF rossz beteghez | Automatikus hozzárendelés | Rossz beteg riportja | 5 | 2 | 2 | 20 | **FR-200** nincs tippelés; E-VCF-002 | — |
| **R-013** | Gépi fordítás / LLM-fordítás klinikai szövegen | FR-610 megsértése | Hamis klinikai jelentés | 4 | 2 | 2 | 16 | **FR-610** + **FR-700**: nincs HU → EN eredeti jelöléssel | OQ-14 lektor |
| **R-014** | PRS európai kalibráció nem-európai alanyon | L5 F4, ancestry nélkül | Kockázat-túlbecslés | 4 | 3 | 3 | 36 | **FR-430** ancestry_calibration kötelező a szerződésben; v1-ben nincs L5 | F4 |

R-001 RPN 30, de **S = 5** → v1 előtt kötelező kontroll (FR-210 P0). R-002 RPN 45 → P0 jelzés + INDETERMINATE.

---

## D.2 Traceability mátrix

Minden funkcionális, NFR és REG sor. TC-azonosítók a gold set / CI nevei; a tesztkód a 62304 verification-ben készül.

### Funkcionális

| Req | Pri | Forrás | AC / TC | GSPR / egyéb | Fázis |
| --- | --- | --- | --- | --- | --- |
| FR-100 | Comp P0 | 2008/XXI. 6. § (2), 8. §, 12. § (1), 15. § | TC-CONSENT-001..006 | GSPR 14.1; 23 (címke/utasítás a hibaüzenetben) | F1 |
| FR-110 | Comp P0 | 6. § (7), 26. § (1); A10 | TC-CONSENT-010..014 | GDPR 17; GSPR 14 | F1 |
| FR-120 | Comp P0 | 26. § (1) | TC-AUDIT-001..006 | GSPR 17.2 | F1 |
| FR-120 hash-chain | P1 | Tervezés, nem tv. | TC-AUDIT-007 | — | F2 |
| FR-130 | Comp P0 | 24–25. § szelleme; GDPR | TC-PII-001..003 | GSPR 14; GDPR 32 | F1 |
| FR-200 | Prod P0 | I-02 L1; B.3.1 | TC-VCF-001..008 | GSPR 17.1 | F1 |
| FR-210 | Prod P0 | Klinikai kockázat; PharmCAT preprocessor; R-001 | TC-CALL-001..012 | ISO 14971 RC-003; GSPR 17.1 | F1 |
| FR-220 kézi | Prod P0 | FR-410 input | TC-CLIN-001..004 | GSPR 14 | F1 |
| FR-220 FHIR | P1 | FHIR R4 | TC-CLIN-010..012 | — | F1.1 |
| FR-230 | P1 | HL7 v2.5.1 LRI | TC-LRI-001..003 | — | F2 |
| FR-240 | Prod P0 | NG-01; YouScript-minta `[R]` | TC-OUT-001..006 | REG-020 | F1 |
| FR-250 | Prod P0 | HGVS, VRS, ATC | TC-MAP-001..005 | GSPR 17.1 | F1 |
| FR-300 | Prod P0 (VCF path) | PharmCAT; A.3 L3 | TC-PCAT-001..008 | SOUP; 62304 | F1 opcionális |
| FR-310 | Prod P0 | PREPARE 12; PGx-Passport 14; PharmCAT 2.11.0 | TC-CONF-001..005 | 62304 §6 change control | F1 |
| FR-400 passzív | Prod P0 | CPIC/DPWG/FDA | TC-RULE-001..040 | GSPR 17.1, 23 | F1 |
| FR-400 aktív | P1 | u.a. | TC-RULE-050..055 | Rule 11a | F2 |
| FR-410 | Prod P0 | I-02 fenokonverzió; R-008 | TC-PHENO-001..015 | Clinical eval | F1 |
| FR-420 | Prod P0 | Alert fatigue | TC-ALRT-001..004 | GSPR 5, 14 | F1 |
| FR-430 | P2 | Kullo 2026; eMERGE 2024 | TC-PRS-IFACE-001 (contract test) | Rule 11a predikció | F4 |
| FR-500 | Prod P0 | Genomics Reporting STU3 | TC-RPT-001..010 | GSPR 23 | F1 |
| FR-510 | P1 | FR-310; R-009 | TC-RPT-020..023 | 62304 §6 | F1.1 |
| FR-520 | P1 | Dolin 2018; R-010 | TC-CDS-001..006 | GSPR 14 (fail-open) | F2 |
| FR-530 | P1 | SMART on FHIR | TC-SMART-001..003 | — | F2 |
| FR-540 | P1 | 6. § (4); OQ-13 | TC-PT-001..003 | GSPR 23 | F2 |
| FR-600 | P1 | PMS/PMCF | TC-PMS-001..004 | MDR PMS; AI Act 72 | F2 |
| FR-610 | Comp P0 / P1 UI | A7 | TC-I18N-001..004 | GSPR 23; R-013 | F1 |
| FR-700 | Comp P0 | AI Act; R-004 | TC-LLM-NEG-001..003 | AI Act 9, 15 | F1 |
| FR-710 | Comp P0 | 6. § (6) | TC-EXPLAIN-001..004 | AI Act 13; GSPR 23 | F1 |

### NFR

| Req | Pri | Forrás | Ellenőrzés | GSPR / egyéb |
| --- | --- | --- | --- | --- |
| NFR-010 | P0 | G1 | Load teszt | GSPR 17 |
| NFR-011 | P1 | FR-520 | Szintetikus monitor | R-010 |
| NFR-020 | P0 | Üzem | SLO | — |
| NFR-030 | P0 | GDPR; EHDS irány | DPA | GDPR 44+ |
| NFR-031 | P0 | GDPR 32 | Pentest | GSPR 17.2 |
| NFR-032 | P0 | 2008/XXI.; GDPR | Access review | GSPR 14 |
| NFR-033 | P0 | Biztonsági baseline | CI gitleaks | — |
| NFR-040 | P0 | FR-120 | TC-AUDIT | GSPR 17.2 |
| NFR-050 | P2 | (EU) 2025/327 | Architecture review | EHDS 2031 |
| NFR-060 | P0 | FR-710; 62304 | CI determinizmus | GSPR 17.1 |
| NFR-070 | P0 | IEC 62304 Class B | Coverage CI | 62304 |
| NFR-080 | P0 | 26. § 30 év | Éves DR | GSPR 17.2 |
| NFR-090 | P1 | Kapacitás | Load | — |

### REG

| Req | Pri | Forrás | Artefaktum | Határidő |
| --- | --- | --- | --- | --- |
| REG-010 | Comp P0 | MDCG 2019-11 Rev.1 | A melléklet | v1 előtt |
| REG-011 | Comp P0 | MDR Art. 5(5) szelleme; MDCG 2025-6 | F2 szerződés | F2 |
| REG-020 | Comp P0 | NG-01; 12. § | Labor-szerződés | Első partner |
| REG-021 | Comp P0 | MDCG modules / gyártó def. | Vendor-szerződés | Első integráció |
| REG-030 | Comp P0 | ISO 13485, 62304, 14971 | QMS | F2 párhuzamos |
| REG-031 | Comp P0 | MDR Art. 15 | PRRC kijelölés | F2 |
| REG-040a | Comp P0 | 29/2022. 4. mell. 2.1, 9/C. § | C melléklet C-201 | **2026-09-30** |
| REG-040b | P2 | Eüak. 35/B. § | BM engedély | F4 |
| REG-050 | Comp P0 | GDPR Art. 9, 35 | DPIA, DPO | v1 előtt |
| REG-060 | P1 | AI Act; MDCG 2025-6 | Gap-analysis a technikai fájlban | 2027 Q4 |
| REG-061 | Comp P0 | AI Act Art. 4 | Képzési napló | Azonnal |
| REG-070 | P1 | ISO 27001 | Tanúsítvány | enterprise |
| REG-080 | Comp P0 | MPL 2.0; 62304 SOUP | SPDX SBOM | v1 előtt |

---

## D.3 Plan-vs-content (P06) — forráskorrekciók

| Plan tétel | Hol van a deliverable-ben |
| --- | --- |
| VC-01 EESZT ISO 9001 ≠ 13485 | PCE-SPEC §4.3, §8 REG-040a/070; C melléklet C-201; VALIDATED-CLAIMS |
| VC-02 PREPARE 12 vs Passport 14; OQ-02 lezárva | FR-310; §9.4; §10 OQ-02 LEZÁRVA |
| VC-03 joghelyek 6. § (2), 8. §, 12. § | §4.2 tábla; FR-100 AC |
| VC-04 Class I létezik, PGx nem 11c | §4.1; A.5 |
| VC-05 72 h = A10 assumption | §0 A10; FR-110 |
| VC-06 hash-chain P1 | FR-120 |
| Product vs Compliance P0 szétválasztás | §0 szótár; minden FR címke |
| F1 vs F2/F3 intended purpose | A.1, A.2 |
| L0–L7 mátrix | A.3 |
| Outside-call default, matcher kockázat | A.3 L3; FR-240; FR-300 |
| Adatmodell, API, hibakatalógus, SOUP, fenokonverzió | B melléklet |
| EESZT 1.1–1.9 + 2.1 | C melléklet |
| ISO 14971 kezdeti + teljes mátrix | ez a dokumentum |
| Nincs TAM, nincs ticket, nincs counsel | PCE-SPEC §15; README |

**P06 eredmény:** a plan checklist tételei a csomagban megvannak. Maradék gap szándékos: OQ-05 válasza, gold-set SOP, engineering ticketek.
