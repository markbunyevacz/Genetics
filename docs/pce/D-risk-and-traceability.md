# D melléklet — Kockázat és traceability

| | |
| --- | --- |
| **Dokumentum** | PCE-SPEC-v1.2 Appendix D |
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
| **R-003** | CPIC vs DPWG ütközés, a szoftver „szintetizál” | Egyetlen „győztes” ajánlás | Nem létező, egyik forrásban sem szereplő tanács | 4 | 2 | 2 | 16 | **FR-400-STATIC** mindkét forrás; `unsourced_claims == 0` | Alacsony |
| **R-004** | LLM a klinikai úton | Szabad szöveg, hallucinált dózis | Nem reprodukálható, hamis ajánlás; 6. § (6) sérülés | 5 | 2 | 2 | 20 | **FR-700**, **FR-710**, **NFR-060**; CI call-graph | Tilos a klinikai path |
| **R-005** | Tanácsadás/beleegyezés megkerülése | Admin override, config flag | 2008/XXI. 6. § (2), 8. §, 12. § sérülés | 4 | 2 | 2 | 16 | **FR-100** nem kikapcsolható; negatív teszt adminra | — |
| **R-006** | Visszavonás után cache-elt riport | CDN/HTTP cache, 200 a 410 helyett | 26. § (1) megsemmisítés elmarad | 4 | 3 | 2 | 24 | **FR-110** 410 Gone; kaszkád derived-re + HITL store; A10 72 h SLA | Audit a törlésről |
| **R-007** | DPYD–fluoropirimidin: a statikus guideline-szöveget terápiás utasításnak olvassák | F1+ intended purpose vs felhasználói percepció | Súlyos toxicitás, ha a labor/klinikus a PDF-et „dózisnak” veszi | 5 | 2 | 3 | 30 | A.1 a PDF-en (**FR-490**); nincs `dose_mg`; nincs élő fenokonverzió a leleten; REG-020 aláíró; **OQ-05** | F3-on IIa + klinikai eval |
| **R-008** | Fenokonverzió hallgatólagos kihagyása a **shadow/F2** pathen | Nincs gyógyszerlista, a motor NM-et ad „késznek” | Funkcionális PM NM-ként kezelve a HITL/F2 kártyán | 4 | 3 | 2 | 24 | **FR-220** `clinical_context = ABSENT` a HITL/F2 kártyán; FR-410-LIVE nem értékelhető. F1+ leleten élő alkalmazás **tilos** (FR-410-EDU only) | — |
| **R-009** | Guideline-váltás (F5-eset) után régi riport él | Hardcoded génlista | Elavult, visszavont ajánlás | 4 | 3 | 2 | 24 | **FR-310**, **FR-510**; PharmCAT 2.11.0 mint bizonyíték | P1 a tömeges újragenerálás |
| **R-010** | CDS timeout blokkolja a felírást | Fail-closed | Gyógyszer elmarad, kár a késedelemből | 4 | 2 | 2 | 16 | **FR-520** fail-open 2 s; NFR-011; F1+ buildben CDS nincs kitéve | F2 |
| **R-011** | PII a motor-logban | Debug dump | GDPR Art. 9 + 2008/XXI. | 3 | 3 | 2 | 18 | **FR-130** CI PII-scanner | — |
| **R-012** | Multi-sample VCF rossz beteghez | Automatikus hozzárendelés | Rossz beteg riportja | 5 | 2 | 2 | 20 | **FR-200** nincs tippelés; E-VCF-002 | — |
| **R-013** | Gépi fordítás / LLM-fordítás klinikai szövegen | FR-610 megsértése | Hamis klinikai jelentés | 4 | 2 | 2 | 16 | **FR-610** + **FR-700**: nincs HU → EN eredeti jelöléssel | OQ-14 lektor |
| **R-014** | PRS európai kalibráció nem-európai alanyon | L5 F4, ancestry nélkül | Kockázat-túlbecslés | 4 | 3 | 3 | 36 | **FR-430** ancestry_calibration kötelező a szerződésben; v1-ben nincs L5 | F4 |
| **R-015** | „Regulatory bypass”: F2 kimenet F1 köntösben / disclaimer mint kimenekülés | „Az orvos dönt”; HITL a napi UI-n | Forgalomba hozatal CE nélkül, ha MDSW; betegkár + hatósági leállítás | 5 | 3 | 2 | 30 | **NG-07/08**; A.0; **FR-470**; FR-490 **nem** minősít ki; OQ-05 nyitva | S=5 → v1 előtt CI izoláció |
| **R-016** | Shadow inferencia szivárog a kezelőorvos klinikai UI-jára | Közös store, rossz RBAC, `LIVE_CDS` runtime true | Az A.1 rendeltetés hamis → F2/MDSW; NG-08 | 5 | 3 | 2 | 30 | **FR-470** CI call-graph; `E-ISO-001`; compile-time flag; E.8 | G6 = 0 szivárgás |
| **R-017** | Anonimizáló gateway a gyártó felhőjében fut | PII (TAJ, név) elhagyja az intézményt | GDPR Art. 9; 2008/XXI.; DPA sérülés | 4 | 3 | 2 | 24 | **FR-460**; `E-SHADOW-001`; gateway intézményi zóna | REG-091 |
| **R-018** | Shadow = rejtett klinikai vizsgálat Art. 62 nélkül | „Csak analitika” címke valós ellátási eseményen | Jogellenes vizsgálat; etikai/hatósági szankció | 4 | 3 | 3 | 36 | **REG-090**; **OQ-15** az első HIS-csatlakozás **előtt**; E.7 | Counsel dönt |
| **R-019** | Re-identifikáció diplotípus + ritka ATC kombinációból | „Anonim” shadow 7 karakteres kóddal / pontos idővel | GDPR személyes adat; FR-115 megkerülve | 4 | 3 | 2 | 24 | **FR-461**; 7 karakteres kód default (D-38); negyedév; ritka-elnyomás; k≥5 (A14); finomabb ATC → kisebb k-cella (R-020, elfogadott ár); **OQ-16** | DPO |
| **R-020** | ATC/diplotípus coarsening rontja a shadow validációt | DPO ATC3-at vagy CLASS-only diplotípust kér | G3 recall/precision a gold set alatt; F2 dosszié gyengül | 3 | 3 | 2 | 18 | Config-szint napló; G3 küszöb; ha ATC3, a phenoconversion gold set **ATC3-kompatibilis** subset | A14 vs G3 |
| **R-021** | F1+ EDU ha–akkor / med-lista szűrés | Renderer a beteg receptjére szabja a CPIC sort | OQ-05 összeomlik; Rule 11a | 5 | 2 | 2 | 20 | **FR-410-EDU**, **FR-400-STATIC** teljes tábla; `E-EDU-001`; A.1.2 | OQ-05 nyitva |

R-001 RPN 30, de **S = 5** → v1 előtt kötelező kontroll (FR-210 P0). R-002 RPN 45 → P0 jelzés + INDETERMINATE. R-015/R-016/R-021 S = 5 → FR-470 + EDU CI a v1 klinikai release előtt.

**F-04 / J-2:** R-007 S=5 + NFR-070 Class B + F3 IIa + Rule 11a (halál/irreverzibilis → III) **ellentmondás**. Páronkénti tábla: A.4.1. NFR-070a Class B a magra; NFR-070b Class C javaslat az L4-live DPYD (és a táblában felsorolt) párokra. Osztály: OQ-06, nem e sor.

R-008 v1.1-ben a aláírt lelet NM-jét védte. v1.2: élő fenokonverzió **nincs** a leleten; a kockázat a shadow/F2 kártyára és a F1+ EDU félreolvasására (R-007) marad.

---

## D.2 Traceability mátrix

Minden funkcionális, NFR és REG sor. TC-azonosítók a gold set / CI nevei; a tesztkód a 62304 verification-ben készül.

### Funkcionális

| Req | Pri | Forrás | AC / TC | GSPR / egyéb | Fázis |
| --- | --- | --- | --- | --- | --- |
| FR-100 | Comp P0 | 2008/XXI. 6. § (2), 8. §, 12. § (1), 15. § | TC-CONSENT-001..006 | GSPR 14.1; 23 | F1+ |
| FR-110 | Comp P0 | 6. § (7), 26. § (1); A10; GDPR Art. 12(3)/12(4), 17(1); S054, **S055** | TC-CONSENT-010..014; DSR levél; `E-DSR-OVERDUE` | GDPR 12(3), 12(4), 17; GSPR 14 | F1+ |
| FR-115 | Comp P0 ha ≠ anonim | GDPR 6(1)(a), 9(2)(a); E.6 | TC-CONSENT-020..023; E-CONSENT-006 | GDPR 9 | F1s |
| FR-120 | Comp P0 | 26. § (1); **S054** (megtagadás analogia) | TC-AUDIT-001..006 | GSPR 17.2 | F1+ |
| FR-120 hash-chain | P1 | Tervezés, nem tv. | TC-AUDIT-007 | — | F2 |
| FR-130 | Comp P0 | 24–25. § szelleme; GDPR | TC-PII-001..003 | GSPR 14; GDPR 32 | F1+ |
| FR-200 | Prod P0 | I-02 L1; B.3.1 | TC-VCF-001..008 | GSPR 17.1 | F1+ |
| FR-210 | Prod P0 | Klinikai kockázat; PharmCAT preprocessor; R-001 | TC-CALL-001..012 | ISO 14971 RC-003; GSPR 17.1 | F1+ |
| FR-220 kézi | Prod P0 F1s/F2 | FR-410-LIVE input; **nem** F1+ L4 | TC-CLIN-001..004 | GSPR 14 | F1s |
| FR-220 FHIR | P1 | FHIR R4; E.3 | TC-CLIN-010..012 | — | F1s |
| FR-230 | P1 | HL7 v2.5.1 LRI | TC-LRI-001..003 | — | F2 |
| FR-240 | Prod P0 | NG-01; YouScript-minta `[R]` | TC-OUT-001..006 | REG-020 | F1+ |
| FR-250 | Prod P0 | HGVS, VRS, ATC | TC-MAP-001..005 | GSPR 17.1 | F1+ |
| FR-300 | Prod P0 (VCF path) | PharmCAT; A.4 L3 | TC-PCAT-001..008 | SOUP; 62304 | F1+ opcionális |
| FR-310 | Prod P0 | PREPARE 12; PGx-Passport 14; PharmCAT 2.11.0 | TC-CONF-001..005 | 62304 §6 change control | F1+ |
| FR-400-STATIC | Prod P0 | CPIC/DPWG/FDA; A.1 | TC-RULE-001..040 | GSPR 17.1, 23; OQ-05 | F1+ |
| FR-400-LIVE | P0 F1s/F2 | u.a.; **tilos F1+ leleten** | TC-RULE-050..055 | Rule 11a ha klinikai UI | F1s / F2 |
| FR-410-EDU | Prod P0 | A.1.2 oktató bekezdés | TC-EDU-001..010 | OQ-05 csomag | F1+ |
| FR-410-LIVE | Prod P0 F1s/F2 | I-02 fenokonverzió; R-008 | TC-PHENO-001..015 | Clinical eval; **nem** F1+ lelet | F1s / F2 |
| FR-420 | Prod P0 | Alert fatigue; A.1 vs A.3 | TC-ALRT-001..004 | GSPR 5, 14 | F1+ / F2 |
| FR-430 | P2 | Kullo 2026; eMERGE 2024 | TC-PRS-IFACE-001 (contract test) | Rule 11a predikció | F4 |
| FR-440 | Prod P0 F1s | A.2; E.2 | TC-SHDW-001..006 | REG-090 | F1s |
| FR-450 | Prod P0 F1s | E.4 | TC-HITL-001..005 | G3 | F1s |
| FR-450-BLIND | P1 F1s | E.4.1; OQ-15 | TC-HITL-010..014 | Art. 62 érv, nem döntés | F1s |
| FR-460 | Comp P0 F1s | E.3; R-017 | TC-GW-001..008; E-SHADOW-001 | GDPR 32 | F1s |
| FR-461 | Comp P0 F1s anonim | E.3.1; R-019/020; A14 | TC-GW-010..020; E-SHADOW-003 | OQ-16 csomag | F1s |
| FR-470 | Comp P0 | A.0; NG-07/08; R-015/016 | TC-ISO-001..008 | Rule 11a kikerülés tilalma | F1+ |
| FR-480 | P1 | A.1 enciklopédia | TC-ENC-001..003 | OQ-05 | F1+ |
| FR-490 | Comp P0 | A.1.1; R-007 | TC-RPT-DISC-001..003 | GSPR 23; **nem** MDSW-kimenekülés | F1+ |
| FR-500 | Prod P0 | Genomics Reporting STU3 | TC-RPT-001..010 | GSPR 23 | F1+ |
| FR-510 | P1 | FR-310; R-009 | TC-RPT-020..023 | 62304 §6 | F1.1 |
| FR-520 | P0 F2; **tilos F1+** | Dolin 2018; R-010 | TC-CDS-001..006 | GSPR 14 (fail-open) | F2 |
| FR-530 | P1 F2; F1+ csak FR-480 | SMART on FHIR | TC-SMART-001..003 | — | F2 |
| FR-540 | P1 | 6. § (4); OQ-13 | TC-PT-001..003 | GSPR 23 | F2 |
| FR-600 | P1 | PMS/PMCF | TC-PMS-001..004 | MDR PMS; AI Act 72 | F2 |
| FR-610 | Comp P0 / P1 UI | A7 | TC-I18N-001..004 | GSPR 23; R-013 | F1+ |
| FR-700 | Comp P0 | AI Act; R-004 | TC-LLM-NEG-001..003 | AI Act 9, 15 | F1+ |
| FR-710 | Comp P0 | 6. § (6) | TC-EXPLAIN-001..004 | AI Act 13; GSPR 23 | F1+ |

### NFR

| Req | Pri | Forrás | Ellenőrzés | GSPR / egyéb |
| --- | --- | --- | --- | --- |
| NFR-010 | P0 | G1 | Load teszt | GSPR 17 |
| NFR-011 | P1 (F2: P0) | FR-520 | Szintetikus monitor | R-010 |
| NFR-020 | P0 | Üzem | SLO | — |
| NFR-030 | P0 | GDPR; EHDS irány | DPA | GDPR 44+ |
| NFR-031 | P0 | GDPR 32 | Pentest | GSPR 17.2 |
| NFR-032 | P0 | 2008/XXI.; GDPR | Access review | GSPR 14 |
| NFR-033 | P0 | Biztonsági baseline | CI gitleaks | — |
| NFR-040 | P0 | FR-120 | TC-AUDIT | GSPR 17.2 |
| NFR-050 | P2 | (EU) 2025/327 | Architecture review | EHDS 2031 |
| NFR-060 | P0 | FR-710; 62304 | CI determinizmus | GSPR 17.1 |
| NFR-070a | P0 | IEC 62304 Class B — F1+ mag | Coverage CI | 62304 |
| NFR-070b | P0 F1s/F2 | IEC 62304 Class C **javaslat** — A.4.1 L4-live | OQ-06 | 62304 |
| NFR-080 | P0 | 26. § 30 év | Éves DR | GSPR 17.2 |
| NFR-090 | P1 | Kapacitás | Load | — |

### REG

| Req | Pri | Forrás | Artefaktum | Határidő |
| --- | --- | --- | --- | --- |
| REG-010 | Comp P0 | MDCG 2019-11 Rev.1 | A melléklet (F1+ / F1s / F2) | v1 előtt |
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
| REG-090 | Comp P0 | MDR Art. 62; E.7; R-018 | OQ-15 döntés + protokoll | F1s előtt |
| REG-091 | Comp P0 | GDPR; E.5; R-017 | DPA + shadow DPIA | F1s előtt |

---

## D.3 Plan-vs-content (P06) — forráskorrekciók és v1.2 hibrid

| Plan tétel | Hol van a deliverable-ben |
| --- | --- |
| VC-01 EESZT ISO 9001 ≠ 13485 | PCE-SPEC §4.3, §8 REG-040a/070; C melléklet C-201; VALIDATED-CLAIMS |
| VC-02 PREPARE 12 vs Passport 14; OQ-02 lezárva | FR-310; §9.4; §10 OQ-02 LEZÁRVA |
| VC-03 joghelyek 6. § (2), 8. §, 12. § | §4.2 tábla; FR-100 AC |
| VC-04 Class I létezik, PGx nem 11c | §4.1; A.6 |
| VC-05 72 h = A10 assumption; S055 Art. 12(3) pin; két artefaktum | §0 A10; FR-110; G §1 |
| VC-06 hash-chain P1 | FR-120 |
| VC-11 „az orvos dönt” kimenekülés | A.0; NG-07; FR-470; VALIDATED-CLAIMS REFUTED |
| VC-12 A10 ≠ F1s 72 h puffer | §0.1; E.5.1; VALIDATED-CLAIMS |
| FR-410-EDU ha–akkor / teljes gén-tábla | A.1.2; FR-400-STATIC; FR-410-EDU |
| Gateway ATC4 / k-anonymity / negyedév | E.3.1; FR-461 |
| Vak HITL | E.4.1; FR-450-BLIND |
| Product vs Compliance P0 szétválasztás | §0 szótár; minden FR címke |
| F1+ / F1s / F2 intended purpose | A.1, A.2, A.3 |
| L0–L7 mátrix (L4-static vs L4-live) | A.4 |
| Outside-call default, matcher kockázat | A.4 L3; FR-240; FR-300 |
| Adatmodell, API, hibakatalógus, SOUP, két path | B melléklet |
| Shadow, gateway, HITL, consent váz | E melléklet |
| EESZT 1.1–1.9 + 2.1 | C melléklet |
| ISO 14971 kezdeti + teljes mátrix | ez a dokumentum |
| Gyártói előterjesztés, nem aláírás | F melléklet; OQ státusz ELŐTERJESZTVE |
| Címzett-kész irattervezetek | Outbound/ (OQ-05/16/15/03/01); nem pecsét |
| Spec-fagyasztás + F1+ mag DEV | §10.2; D-18; OQ-k nyitva |
| Eladható ajánlat, feltételezett OQ | Sales/; **SKU-P rendszer**; HU/EU/US flag; F2 LOCK |
| VC-13 S028 ≠ PGx-SOTA / G3 / PCE-RWE | §9.5; G3 ≥90% marad; FR-710 nem SHAP; [S028-note](Sources/S028-curemd-hybrid-cdss-note.md); [literature-boundary](Sales/literature-boundary.md) |
| VC-14 PREPARE/YouScript/Tandem/ClinLabomics | OQ-15 §III (p=0,0075); market-packs mátrix; OQ-05 IV.a; OQ-16 I.4; [competitor-analogs](Sales/competitor-analogs.md) |
| VC-16 Ft-sáv = következtetés | [Sales/pricing.md](Sales/pricing.md); YouScript 365 USD ≠ HU lista; HIS-plafon pin |

**P06 eredmény (v1.2 + Sales SKU-P + S028 + I-19 + árazás):** a vevő **rendszert** licencel. PREPARE számok a Lancetből, nem user-p=0,0034. YouScript 365 USD lista ≠ HU ár. A 6–35 M Ft **következtetés**. Tandem/ClinLabomics nem pecsét. OQ-k + OQ-17 nyitva.
