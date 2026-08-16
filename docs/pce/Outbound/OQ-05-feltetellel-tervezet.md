# OQ-05 V. FELTÉTELLEL — gyártói záradék-tervezet

| | |
| --- | --- |
| **Iktató** | PCE-OUT-OQ-05-FELT / v1.2 |
| **Dátum** | 2026-08-16 |
| **Státusz** | TERVEZET a counsel kitöltéséhez. **Nem** pecsét. **Nem** counsel-állásfoglalás. |
| **Kapcsolt** | [OQ-05-counsel-brief.md](OQ-05-counsel-brief.md) V. szakasz (checkboxok **üresek**); [OQ-05-TEST-PROTOCOL.md](../ProcessArtifacts/OQ-05-TEST-PROTOCOL.md) |

Ez az irat a brief V. szakasz *kitöltési javaslatát* adja, ha a counsel a FELTÉTELLEL rubrikát választja. A gyártó **nem** jelöli be az IGEN / NEM / FELTÉTELLEL négyzetet. A F.6 sor ettől üres.

---

## 0. Kategória — mit dönt az V. pecsét, és mit nem

Az OQ-05 V. szakasz a **hatályos MDR Annex VIII Rule 11** szerinti minősítés: az A.1 F1+ kimenet MDSW-e, és ha igen, milyen osztály. Forrás: brief Q1–Q3; G §3; A.0 / A.1.

**Nem** az V. pecsét tárgya:

- a unittest-készlet mérete,
- a D-49 hardening gépelt OK-ja,
- az F5 live hálózat fail-open ága,
- a CI PharmCAT JAR HTTP letöltése a tesztek előtt.

Ezek szoftver-OQ / ops tények. A jegyzőkönyv Q1 szoftver-hatóköre **`partial`**: a teszt a gyógyszerlista-vakságot és a teljes tábla dumpot méri. Rule 11 vs 11c ettől még counsel. Q2 szoftver-hatóköre **`partial`**. Q3 szoftver-hatóköre **`yes`** (flag + izoláció) — 10 mapped teszt, nem a teljes suite.

A unittest-suite mérete **nem** IGEN pecsét. A két ops-kockázat **nem** NEM pecsét.

---

## 1. Amit a gyártó nem javasol bejelölni

**Feltétel nélküli IGEN.** A dosszié IV.1 pontja nyitva: gén-szintű, verziózott CPIC/DPWG/FDA *terápiás* szöveg lehet Rule 11a gyógyszerlista nélkül is. G §3.4 pecsétig: **Class I MDSW** technical file, ne „nem eszköz”. A unittest-suite mérete és az AST-lefedettség ezt a jogi küszöböt nem lépi át.

**NEM a fail-open / CI HTTP miatt.** Az F5 live `OSError → []` a shadow-úton van; prod `CPIC_F5_SOURCE=off`; a mock nem megy az aláírt leletre. A CI JAR-pin HTTP a tesztek *előtt* fut; a tesztfázis `PCE_PHARMCAT_OFFLINE=1`. Ezek nem az A.1 F1+ rendeltetés Rule 11 kérdései. Ha a counsel NEM-et jelöl, a gyártói default osztály **Rule 11a → IIa** (brief V.), nem „fail-open → elutasítás”.

---

## 2. Ha a counsel FELTÉTELLEL-t jelöl

A brief V. definíciója: FELTÉTELLEL = **IGEN** (nem MDSW) az alábbi feltételekkel. A feltételek a specbe / CI-be kerülnek, nem szóban maradnak.

Gyártói záradék-tervezet (a counsel átfogalmazhatja a saját sablonjába):

1. A jóváhagyás **csak** az A.1 F1+ statikus, aláírt laborleletre vonatkozik, a III. invariánsok folyamatos fennállása mellett (gyógyszerlista-vakság, nincs betegre szabott ha–akkor, FR-410-EDU, FR-490 aláírói kapu, FR-470 csatorna-izoláció, A.1.1 nyilatkozat mint rendeltetés-mondat, nem felelősségkizárás).
2. A repo compile-time lakatok a pecsét napján: `LIVE_CDS=false`, `MATCHER_ON=false`, `IIA_SAFE_BLOCK=true`. Bármelyik billentése **újra megnyitja** az OQ-05-öt és a REG-010-et. A `MATCHER_ON=true` útvonal (PharmCAT NamedAlleleMatcher, HGVS/VRS — D-53, **nem** E-31) külön minősítés.
3. A Q4 (COM(2025) 1023 javasolt Rule 11) **nem** helyettesíti a Q1–Q3 pecsétet, és **nem** billenti a lakatokat.
4. A két dokumentált ops-viselkedés (alább R-OPS-01, R-OPS-02) a dosszié IV. maradék kockázata. **Nem** a pecsét feltétele, és a fail-fast-re váltás **nem** pecsét-feloldás.

Ha a counsel a FELTÉTELLEL helyett NEM-et (MDSW) jelöl: a fenti 2–3. pont a *modulhatár* dokumentációja marad, nem nem-MDSW feltétel.

---

## 3. R-OPS-01 — F5 live fail-open

| | |
| --- | --- |
| **Hol** | `LiveF5Provider.rows()`; teszt: `test_f5_live_network_error_skips_without_exception` |
| **Viselkedés** | Hálózati `OSError` → `log.exception` + `return []`. Nem fail-fast. |
| **Szándék** | Üzemeltetési döntés. Ismeretlen env-token `ValueError`. Üres env → `DISABLED`. Prod: `CPIC_F5_SOURCE=off` (`config/production.env`). |
| **F1+ lelet** | A mock/live F5 rec-sor **nem** megy az aláírt leletre. |
| **OQ-05 viszony** | Shadow/F1s ops. **Nem** Q1–Q3 döntő. Fail-fast-re váltás termékdöntés (D-56: **nem** pecsét-előfeltétel). |

## 4. R-OPS-02 — CI JAR HTTP a tesztek előtt

| | |
| --- | --- |
| **Hol** | `.github/workflows/ci.yml`: `fetch_software_ready_pins.py --jar-only`, majd `PCE_PHARMCAT_OFFLINE=1` unittest |
| **Viselkedés** | A CI job induláskor pinelt PharmCAT JAR-t tölt GitHub release-ről. A tesztfázisban `ensure_jar()` nem tölt le; hiányzó/hibás checksum → `PharmcatError`. `--jar-only` a `merge_manifest` előtt kilép. |
| **Szándék** | A hermetikus zárás a **teszt**, nem a teljes job. MANIFEST top-level `accessed` **2026-08-13**. |
| **OQ-05 viszony** | Matcher default ki (`MATCHER_ON=false`). **Nem** Q1–Q3 döntő. A JAR-pin air-gap kiterjesztése a teljes jobra külön CI-döntés, nem pecsét-feloldás. |

**E-31** (2026-08-16): az OQ-05 brief/G Q1 `ALLOWED_B41_TOP_LEVEL` **45 → 47** (`schema.py`). Ez **nem** outside-call, **nem** HGVS, **nem** laborcsatorna-validáció.

---

## 5. Pecsétig gyártói default (változatlan)

G §3.4 `[A]`: Class I MDSW technical file, amíg a counsel nem pecsétel. Nem „nem eszköz”. Q4 nem pecsét. Flagok false.

---

## 6. Counsel-küldés vs Class I MDSW dosszié

A formális átadás kapuja **nem** a REG-030 teljes QMS (ISO 13485 / IEC 62304 / ISO 14971 fájl, PMS, gyártói nyilatkozat, EUDAMED-regisztráció). Az a teher G §3.4 szerint pecsétig *párhuzamos* F2-pálya. D.1 **kezdeti** 14971 nyilvántartás, **nem** teljes dosszié (`D-risk-and-traceability.md`). REG-010 = A melléklet, már a counsel-csomagban.

A küldés kapuja: a brief melléklet-útvonalai léteznek; a V. checkbox üres; a kategóriahibák nincsenek a záradékban (suite méret ≠ IGEN; F5 fail-open / CI JAR HTTP ≠ NEM; E-31 ≠ HGVS). Gép: `test_oq05_protocol.Oq05CounselSendPackTests.test_outbound_listed_paths_exist` (a testosztály a citációkat méri, **nem** pecsétel). REG-030 **nem** küldési feltétel. Átadás-átvétel SHA-256: [OQ-05-SEND-PACK.md](OQ-05-SEND-PACK.md) (boríték, **nem** pecsét; a saját hashét nem tartalmazza).

*Ez az irat gyártói kitöltési javaslat. A brief V. checkboxai és a VI. aláírás a counselé.*
