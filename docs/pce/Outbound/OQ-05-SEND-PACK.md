# OQ-05 küldőcsomag — tartalomjegyzék és SHA-256

| | |
| --- | --- |
| **Iktató** | PCE-OUT-OQ-05-SEND / v1.2 |
| **Dátum** | 2026-08-16 |
| **Státusz** | **Átadás-átvételi boríték — nem pecsét.** Nem counsel-állásfoglalás. Nem CE. |
| **Algoritmus** | SHA-256, fájlbyte, bináris (nem kanonizált szöveg) |
| **Csomag-ujjlenyomat** | `bdb78b8a9c573fb6363da10f6e2db0d822352cb32778970676875458ee0990c6` |
| **OQ-05 V.** | üres (IGEN / NEM / FELTÉTELLEL a counselé) |

A csomag-ujjlenyomat a `relatív_út + szóköz + sha256 + soremelés` sorok SHA-256-ja, a lenti sorrendben. A boríték **saját** hashét **nem** tartalmazza.

Ez **nem** tölti ki az OQ-05 V. pecsétet. REG-030 **nem** küldési feltétel. D.1 kezdeti 14971, nem teljes dosszié. A Q1 gold **nem** aláírt PDF. A mapped evidenciatábla **51** egyedi teszt, a Q3 **10**; a suite mérete **nem** IGEN.

## 1. Tartalomjegyzék

| # | ID | Szerep | Útvonal |
| --- | --- | --- | --- |
| 1 | **COVER** | Fedélirat | `docs/pce/Outbound/OQ-05-counsel-brief.md` |
| 2 | **FELT** | Záradék-tervezet | `docs/pce/Outbound/OQ-05-feltetellel-tervezet.md` |
| 3 | **SPEC** | Spec v1.2 | `docs/pce/PCE-SPEC-v1.2.md` |
| 4 | **REG-010** | REG-010 | `docs/pce/A-intended-purpose-and-modules.md` |
| 5 | **F1** | F.1 | `docs/pce/F-decision-package.md` |
| 6 | **G** | G §3 + §7 | `docs/pce/G-open-items.md` |
| 7 | **D1** | D.1 | `docs/pce/D-risk-and-traceability.md` |
| 8 | **PROTOCOL** | Szoftver-evidencia | `docs/pce/ProcessArtifacts/OQ-05-TEST-PROTOCOL.md` |
| 9 | **REGISTRY** | Forráslista | `docs/pce/ProcessArtifacts/SOURCE-REGISTRY.md` |
| 10 | **GOLD** | Q1 gold | `tests/fixtures/f1plus-v0/outside-call-cyp2d6-called.json` |
| 11 | **TEST-REPORT** | Q1 teszt | `tests/test_report.py` |
| 12 | **SCHEMA** | B.4.1 | `src/pce_report/schema.py` |
| 13 | **CI** | Q3 CI | `.github/workflows/ci.yml` |
| 14 | **S077** | Q4 S077 | `docs/pce/Sources/official/com-2025-1023-act.pdf` |
| 15 | **S080** | Q4 S080 | `docs/pce/Sources/official/eur-lex-com-2025-1023.html` |

## 2. SHA-256 lista

| ID | Byte | SHA-256 | Megjegyzés |
| --- | ---: | --- | --- |
| **COVER** | 17785 | `28ec0c87efd274dd0f9880a004cc9cd9b27e2f0645fea687867e2fae220a7298` | OQ-05 kérés. V. checkbox üres. Nem pecsét. |
| **FELT** | 6392 | `011f59f88b889b8afc755b543abf4939dc7e81f4e2f8df7749f16a30ea182b23` | FELTÉTELLEL kitöltési javaslat. Nem pecsét. |
| **SPEC** | 85160 | `e59145d91e8cb6231d5dbedee4fbd3a1a4058bba1343c8ea4623ee288d589353` | Fagyasztott követelmény. OQ-05 ELŐTERJESZTVE. |
| **REG-010** | 17032 | `407ae1cece322d42e274362e59e94e93a3cfe48f047f7c4d7fa71adc918db358` | A melléklet. Intended purpose, modulonként. |
| **F1** | 7766 | `bac7ebc8f4b17462d4d1629214dcac8aeabef07cc4c70b3f9a31916a7e88333a` | Gyártói kérés, nem counsel-válasz. |
| **G** | 33883 | `9783e540839495b4eb11cfbb1156e0914d5bd46d57b4f6596030b6ebe16d747f` | Javaslat a pecsételőnek. Nem pecsét. |
| **D1** | 16095 | `15dd8328f95648e919922ee50618b6514a4d74ab69facd7e826a02034a8c2a3c` | Kezdeti ISO 14971. Nem teljes dosszié. |
| **PROTOCOL** | 41030 | `3099708c55bbb804a2b54186a642c2a18c5e7d0d1f18646f4aeeeb328c3a6043` | Mapped 51 egyedi teszt; Q3 = 10. Nem pecsét. |
| **REGISTRY** | 23989 | `a28ce242207be88b4e71a9d3ca5892e38759bc4a80136cb79e4a18f970391332` | S004/S005 MDCG URL (PDF nincs a repóban). S077/S080 COM pin. |
| **GOLD** | 283 | `3dc1bd4cb391dee13918f19317fd791a9ac9885e3163cdb60e42a5bfbc48d891` | SYN outside-call JSON. Nem aláírt PDF. |
| **TEST-REPORT** | 12321 | `593ac8dac2d6101c5fce4210a5020314ca103894d89c14d5cc429903788379a4` | Renderer / B.4.1 / izoláció. |
| **SCHEMA** | 13453 | `8a6ff4020a404564e6f838d10b282b2420f8c14cf6c8616bb66ad2756db35e07` | ALLOWED_B41_TOP_LEVEL élő méret. |
| **CI** | 2656 | `4e2797667a62205fb142307e2c1080503cb323bab5517ba85a74bb34a2e16a97` | LIVE_CDS=false; MATCHER_ON=false; IIA_SAFE_BLOCK=true (IIa-safe pár-lakat, nem COM-mentesség). |
| **S077** | 1237906 | `62ee670667c08070416cc20ebb2d7a7d33f843dbc8b70220284471f70b1d926c` | COM(2025) 1023 PDF. Javaslat, nem hatályos jog. |
| **S080** | 1218733 | `cf091819888148a4b7a92b0419b72fb9b9ba0807d6f949ea6727b6d80fd592ee` | EUR-Lex HTML. Javasolt Rule 11 olvasható szövege. |

## 3. Ami szándékosan nincs a hash-táblában

| Tétel | Indok |
| --- | --- |
| Ez a SEND-PACK irat | Boríték. A saját SHA-256-ját nem tartalmazza; a git commit az irat byte-jaira vonatkozik. |
| MDCG 2019-11 Rev.1 PDF | Nincs a repóban. Counsel saját példánya. S004/S005 URL a SOURCE-REGISTRY-ben. |
| MDCG 2024-7 | Nem melléklet. PAR-sablon, nem Rule 11 Q&A (E-30). |
| Aláírt példa-lelet PDF | Nincs és nem készül. Q1 = gold JSON. |
| REG-030 QMS fájl | ISO 13485 / IEC 62304 / ISO 14971, PMS, gyártói nyilatkozat, regisztráció. F2-párhuzamos. Nem küldési feltétel. |
| Gyártó cégneve | A9; `[Gyártó neve]`; a küldő tölti küldéskor, nem a git. |
| OQ-05 V. pecsét | Checkbox üres. Counsel tölti. |

## 4. Ellenőrzés

```
PYTHONPATH=src python3 docs/pce/ProcessArtifacts/BuildScripts/generate_oq05_send_pack.py --write
PCE_PHARMCAT_OFFLINE=1 PYTHONPATH=src python3 -m unittest tests.test_oq05_protocol.Oq05CounselSendPackTests -v
```

A committed `OQ-05-SEND-PACK.md` byte-ra egyezik a generátor kimenetével. Eltérés = a melléklet változott, a borítékot újra kell írni. Ez **nem** pecsét-feloldás.

*Generálta: `docs/pce/ProcessArtifacts/BuildScripts/generate_oq05_send_pack.py`.*
