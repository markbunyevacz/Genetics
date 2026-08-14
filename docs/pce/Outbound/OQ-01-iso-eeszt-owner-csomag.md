# ISO 9001 / EESZT F0 owner-csomag (OQ-01)

| | |
| --- | --- |
| **Iktató** | PCE-OUT-OQ-01 / v1.2 |
| **Dátum** | 2026-08-12 |
| **Státusz** | Belső feladatlista — **BELSŐ IGEN** a folyamat indítására; a regisztráció *ténye* nyitott |
| **Címzett** | Ügyvezetés / belső minőségirányítási (RA) vezető |
| **Owner szerep** | `eeszt_iso_owner` (természetes személy a QMS-ben; **itt nincs kitalálva**) |
| **Szigorú kapuőr** | **2026-09-30** — 29/2022. 4. melléklet **2. pont** (9/C. §) |
| **OQ** | OQ-01 — **ELŐTERJESZTVE**; C-000 tény nélkül nem zárható |

Ez a csomag a C melléklet C.4 teendőit **végrehajtható** belső irattá alakítja. Nem BM-engedélykérelem, nem Redmine-feltöltés.

---

## 0. Mi *nem* a feladat (javítás a korábbi vázlathoz)

| Félreértés | Spec (VC-01, NG-05, A8) |
| --- | --- |
| „EESZT fejlesztői regisztráció = aszinkron FHIR + SSL tanúsítvány az éles adatközpontba” | Az EESZT **nem** nyílt FHIR API. **NG-05:** nincs EESZT *írás* (eRecept, eProfil). F1 = **modul** engedélyezett medikai vendor felé, nem saját EESZT-csatlakozó (REG-040b = F4). |
| A 2026-09-30 = ISO 13485 / ISO 27001 | **4. melléklet 2.1** = **ISO 9001** *vagy* **egyéb szoftverfejlesztési területen alkalmazott auditált QMS**. ISO 13485 az MDR/F2 pálya (REG-030). ISO 27001 enterprise (REG-070), nem a 9/C. § tárgya. |
| „ISO 9001 megújítás” | Lehet, hogy **nincs** érvényes tanúsítvány. Ekkor **megszerzés**, nem megújítás. |
| A 2025-10-31 még előttünk van | **Lejárt.** 9/C. § (1): a már engedélyezett / korábban regisztrált fejlesztők a 5/F. § regisztrációt **2025. október 31-ig** kötelesek voltak elvégezni. Kérdés: van-e **most** aktív ESZFK Redmine regisztráció? (C-000) |
| F1-ben a PCE saját EESZT-csatlakozó, ezért a checklist N/A | A8: a 2026-09-30 ISO 9001 **akkor is F0**, ha a vevő a medikai vendor. A fejlesztői jogállás a *fejlesztőre* vonatkozik. |

**Regisztráció hol:** Szolgáltatóközpont (ESZFK) **Redmine** (29/2022. 5/F. §). Portál: https://e-egeszsegugy.gov.hu/fejlesztoknek

**Saját BM szoftverengedély / műszaki bevizsgálás:** nem F1 cél. C.3 (3. melléklet) F1-ben nem töltendő.

---

## 1. Kapuőr és naptár

| Dátum | Esemény | Állapot 2026-08-12-én |
| --- | --- | --- |
| 2025-10-31 | EESZT fejlesztői regisztráció (9/C. §) | **Lejárt** — C-000 kitöltendő *most* |
| **2026-09-30** | 4. melléklet 2.1 ISO 9001 / szoftver-QMS | **~7 hét** — F0 kritikus út |
| F1+ éles | OQ-05 + REG-020 + FR-100 | Külön kapu; ez a csomag nem helyettesíti |

Ha 2026-09-30-ig nincs 2.1 tanúsítvány, a 9/C. § szerint az engedély **visszavonásra kerül** (ahol van engedély). Modulszállítónál is fennáll a későbbi saját belépés és a Redmine-kockázat.

---

## 2. Feladatlista (C.4 + C-000–C-201)

Minden sor: státusz `NINCS INDÍTVA` / `FOLYAMATBAN` / `KÉSZ` / `N/A`. Bizonyíték = dátum + dokumentumazonosító.

### Task 0 — Owner kijelölése (azonnal)

| | |
| --- | --- |
| Leírás | Az ügyvezetés kijelöli az `eeszt_iso_owner` természetes személyt a QMS-ben. Név **itt nem kitalált**. |
| Felelős | Ügyvezetés |
| Kimenet | Név, beosztás, helyettes; F.4 / F.6 |
| Státusz | |
| Név (kitöltendő) | .................................... |

### Task 1 — EESZT fejlesztői jogállás ténye (C-000–C-002)

| | |
| --- | --- |
| Leírás | **Nem** FHIR-csatlakozás. Annak megállapítása, van-e **aktív ESZFK Redmine** fejlesztői regisztráció *most*. Ha nincs: a portál szerinti **új** belépés. Döntés: saját EESZT-gyártó (REG-040b, F4) vs **modulszállító** engedélyezett vendor felé (A8). |
| Felelős | `eeszt_iso_owner` + ügyvezetés |
| Kimenet | C-000 IGEN/NEM + bizonyíték (Redmine ID / elutasítás / inaktiválás); C-002 döntés |
| Státusz | |

| ID | Kérdés | I / N / NA | Bizonyíték |
| --- | --- | --- | --- |
| C-000 | Van aktív ESZFK Redmine fejlesztői regisztráció? | | |
| C-001 | Ha C-000 = NEM: új fejlesztői belépés elindítva? | | |
| C-002 | Saját csatlakozó gyártó, vagy modulszállító vendor felé? | | |

### Task 2 — 4. melléklet 1. pont, gazdasági (C-101–C-109)

| | |
| --- | --- |
| Leírás | Gt. vagy civil forma szerint: közzétett beszámoló, saját tőke, NAV köztartozásmentesség, nincs csőd/felszámolás, TEÁOR’25 62/63 vagy 58.2, vezető tisztségviselői nyilatkozat. Részletek: C melléklet C.2. |
| Felelős | Pénzügy / jog |
| Kimenet | Bizonyíték-mappa; C-101–C-109 kitöltve |
| Határidő | A Redmine / 2.1 audit előtt; **nem** később, mint 2026-09-30 |
| Státusz | |

### Task 3 — ISO 9001:2015 (vagy egyéb auditált szoftver-QMS) — C-201

| | |
| --- | --- |
| Leírás | Gap-elemzés **azonnal**. Tanúsító kiválasztása. A MIR fedje a **szoftverfejlesztést** (és ésszerűen az egészségügyi adatfeldolgozást). Érvényesség **legalább 2026-09-30-ig** — ha nincs cert, megszerezni eddig. **Nem** ISO 13485-csere; a 13485 F2-n külön (REG-030). Ha csak 13485 van 9001 nélkül: **kérdezni a Szolgáltatóközpontot**, ne feltételezni. |
| Felelős | RA / minőségirányítási vezető + `eeszt_iso_owner`; külső QMS-tanácsadó bevonható |
| Kimenet | Tanúsítvány száma, tanúsító, érvényesség; C-201 |
| Határidő | **2026-09-30** (kemény) |
| Státusz | |

Van-e *most* ISO 9001 tanúsítvány?

- [ ] IGEN — szám: ________ tanúsító: ________ érvényes: ________
- [ ] NEM — gap + tanúsító indul: `[dátum]`

### Task 4 — Saját EESZT-engedély vs vendor-modul (A8)

| | |
| --- | --- |
| Leírás | F1 döntés: **nem** saját BM-engedély kell (REG-040b: P2 / F4). A 2.1 szerinti ISO ettől még F0 kapu. |
| Felelős | Ügyvezetés |
| Kimenet | Írásos döntés: modulszállító / később saját csatlakozó |
| Státusz | |

### Task 5–8 — Külső OQ-k (ez a csomag csak indítja)

A tényleges iratok: `docs/pce/Outbound/`. Az owner **nem** írja alá a counsel/DPO/RA/labor helyett.

| # | OQ | Irat | Owner teendő |
| --- | --- | --- | --- |
| 5 | OQ-05 | [OQ-05-counsel-brief.md](OQ-05-counsel-brief.md) | Counselnek kiküldeni; F.6 |
| 6 | OQ-16 | [OQ-16-dpo-dpia-kerdoiv.md](OQ-16-dpo-dpia-kerdoiv.md) | DPO; F1s előfeltétel |
| 7 | OQ-15 | [OQ-15-intezmenyi-ra-egyoldalas.md](OQ-15-intezmenyi-ra-egyoldalas.md) | Intézmény, OQ-16 után |
| 8 | OQ-03 | [OQ-03-l3-term-sheet.md](OQ-03-l3-term-sheet.md) | Üzleti tulajdonos; a labor neve a specben nincs megnevezve |

---

## 3. Belső döntés (már rögzítve, F.4)

Az ügyvezetés / RA **elindítja** az ISO 9001 gap + tanúsítói folyamatot és kijelöli az `eeszt_iso_owner` szerepet. Ez **BELSŐ IGEN** a folyamatról.

**Nyitva marad:** C-000 tény; a tanúsítvány megszerzése; F.6.

---

## 4. Owner visszaigazolás

- [ ] Task 0: `eeszt_iso_owner` kijelölve
- [ ] Task 1: C-000 kitöltve
- [ ] Task 3: tanúsító / gap elindítva
- [ ] Tudomásul veszem: 2026-09-30 = 4. melléklet **2.1**, nem 13485, nem FHIR-EESZT

| | |
| --- | --- |
| `eeszt_iso_owner` neve | .................................... |
| Ügyvezető / RA vezető | .................................... |
| Dátum | .................................... |
| Aláírás | .................................... |

**Mellékletek:** [C melléklet](../C-eeszt-f0-checklist.md) (teljes C-101–C-201 tábla); F.4; 29/2022. 4. melléklet / 294/2025. 9/C. §; https://e-egeszsegugy.gov.hu/fejlesztoknek

*OQ-01 a C-000 tény és a 2.1 tanúsítvány nélkül nem zárható. Ez a lista nem helyettesíti a Redmine-feltöltést.*
