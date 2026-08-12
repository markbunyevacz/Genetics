# C melléklet — EESZT F0 checklist

| | |
| --- | --- |
| **Dokumentum** | PCE-SPEC-v1.2 Appendix C |
| **Dátum** | 2026-08-12 |
| **Jogalap** | 29/2022. (I. 31.) Korm. rendelet 5/F. §, 5/G. §, 9/C. §, **4. melléklet**; 294/2025. (IX. 25.) Korm. rendelet |
| **Portál** | https://e-egeszsegugy.gov.hu/fejlesztoknek `[V]` |

`[CORRECTED]` VC-01: a 2026-09-30 határidő a 4. melléklet **2. pontja** (ISO 9001 vagy egyéb szoftverfejlesztési QMS), **nem** ISO 13485, **nem** ISO 27001.

A1/A8: F1-ben a PCE **nem** saját EESZT-csatlakozó (NG-05). A checklist akkor is F0, ha a vevő az engedélyezett medikai vendor: a fejlesztői jogállás és a 9/C. § a *fejlesztőre* vonatkozik, és a 2026-09-30 utáni Redmine / engedély-kockázat az F4 utat zárja.

---

## C.1 Folyamat (5/F. §)

1. Fejlesztő **regisztráció** a Szolgáltatóközpont (ESZFK) Redmine-felületén.
2. A regisztráció feltétele: a 4. melléklet gazdasági + tanúsítási követelményeinek igazolása.
3. **Műszaki bevizsgálás** → támogató vélemény.
4. A **működtető** (BM) az Eüak. 35/B. § (5) szerint **engedélyezi** az EESZT-csatlakozásra használható informatikai rendszert.
5. Verzióváltás / műszaki átalakítás: a megfelelés **folyamatos**; a Szolgáltatóközpont figyelemmel kíséri (5/G. §). Hiányosság → javítási felhívás → engedély-visszavonás.

**9/C. § (1)** `[V]`: a 294/2025. hatálybalépésekor már engedélyezett, illetve korábban regisztrált fejlesztők a 5/F. § (1) szerinti regisztrációt **2025. október 31-ig** kötelesek elvégezni, azzal, hogy a **4. melléklet 2. pontjának** való megfelelést **2026. szeptember 30-ig** kötelesek biztosítani. Elmulasztás → az engedély visszavonásra kerül.

A 2025-10-31 **lejárt**. OQ-01: van-e érvényes regisztráció *most*? Ha nincs, a Redmine inaktiválás / új belépés a portál aktuális eljárása szerint — ezt a checklist 0. sora rögzíti, nem találgatja.

---

## C.2 4. melléklet — tesztelhető checklist

Forrás: 294/2025. (IX. 25.) 2. melléklete = 29/2022. 4. melléklete `[V]`.

Állapot: `IGEN` / `NEM` / `N/A` + bizonyíték (dátum, dokumentum). Üresen hagyva kitöltésre.

### 0. Jogállás

| ID | Követelmény | I/N/NA | Bizonyíték |
| --- | --- | --- | --- |
| C-000 | Van aktív ESZFK Redmine fejlesztői regisztráció? | | |
| C-001 | Ha C-000 = NEM: a portál szerinti **új** fejlesztői belépés elindítva? | | |
| C-002 | A szervezet EESZT-csatlakozó szoftver **gyártója/fejlesztője** akar lenni (REG-040b), vagy csak **modulszállító** engedélyezett vendor felé (A8)? | | |

Ha C-002 = csak modulszállító: a 4. melléklet akkor is releváns, ha később saját engedély kell; F1-ben REG-040b P2. A 2.1 ISO 9001 ettől még ésszerű F0 (vállalati QMS + későbbi belépés), de **nem** keverendő az MDR ISO 13485-tel.

### 1. Gazdasági követelmények

| ID | 4. mell. | Követelmény | I/N/NA | Bizonyíték |
| --- | --- | --- | --- | --- |
| C-101 | 1.1 | Gt. esetén az utolsó lezárt üzleti év beszámolója közzétéve a Cégszolgálatnál | | |
| C-102 | 1.2 | Gt.: az utolsó két év mérlege alapján a saját tőke **legalább 1 évben nem negatív** | | |
| C-103 | 1.3 | Civil szervezet: OBH-nál az utolsó lezárt év beszámolója közzétéve | | |
| C-104 | 1.4 | Civil: utolsó két év, saját tőke legalább 1 évben nem negatív | | |
| C-105 | 1.5 | NAV köztartozásmentes adatbázis **vagy** 30 napnál nem régebbi NAV igazolás (nincs nyilvántartott tartozás, nincs végrehajtásra/visszatartásra átadott köztartozás) | | |
| C-106 | 1.6 | Nincs végelszámolás, kényszertörlés; nincs közzétett csődeljárást elrendelő végzés; nincs jogerős felszámolás | | |
| C-107 | 1.7 | A tevékenység nincs felfüggesztve | | |
| C-108 | 1.8 | A gt. tevékenységei között **TEÁOR’25 62, 63** ágazat **vagy 58.2** alágazat szerepel | | |
| C-109 | 1.9 | Vezető tisztségviselő nyilatkozata: a szervezet gazdasági/szakmai tevékenységével kapcsolatban bűncselekmény az elmúlt 3 évben jogerős ítéletben nem nyert megállapítást | | |

1.1–1.2 **vagy** 1.3–1.4 a szervezet formája szerint. Egyéni vállalkozó: a melléklet szövege gt./civil fókuszú — ha a gyártó ev., `[NEEDS VERIFICATION]` a Szolgáltatóközpontnál, ne találgassunk.

### 2. Tanúsítás

| ID | 4. mell. | Követelmény | I/N/NA | Bizonyíték | Határidő |
| --- | --- | --- | --- | --- | --- |
| C-201 | **2.1** | **ISO 9001** vagy **egyéb szoftverfejlesztési területen alkalmazott auditált minőségirányítási rendszer** tanúsítványa | | Tanúsítvány száma, tanúsító, érvényesség | **2026-09-30** (9/C. §) |

Elfogadható „egyéb”: a rendelet nem sorolja fel. Gyakorlati jelöltek (nem kimerítő, nem jogi tanács): ISO 9001; szoftverfejlesztésre auditált QMS. **ISO 13485 önmagában** orvostechnikai QMS — a 2.1 szöveg „szoftverfejlesztési területen alkalmazott”; a 13485 *lehet* érv, de a 9/C. § betűje a 2.1. Ha csak 13485 van 9001 nélkül, **kérdezd a Szolgáltatóközpontot** (OQ-01 bővítmény), ne feltételezd.

**Nem** 2.1: ISO 27001, ISO 42001, ISO 15189. Ezek REG-070 / labor.

---

## C.3 3. melléklet — felhasználási terület (ha saját csatlakozás)

Csak REG-040b / F4. A 3. melléklet (294/2025. 1. melléklete) kategóriái, amelyek a PCE-re *később* relevánsak lehetnek:

- 1.4 Diagnosztika; 2.9 Laboratóriumi diagnosztikai tevékenység; 2.11 Egyéb diagnosztikai; 2.6/2.7 szakellátás
- 3.2 Nem közfinanszírozott (magán) — a brief szerint a NEAK preventív PGx-et nem finanszírozza `[R]`
- 4.2 Felhő; 5.1 saját infra vagy 5.2 több szervezet, elkülönített adatkezelés

F1-ben **nem** töltendő. Itt van, hogy F4-en ne kelljen keresni.

---

## C.4 F0 teendők (0–3 hónap, PCE-SPEC §11)

| # | Teendő | Owner | Kimenet |
| --- | --- | --- | --- |
| 1 | C-000–C-002 kitöltése | Ügyvezetés | OQ-01 tény |
| 2 | C-101–C-109 bizonyíték mappa | Pénzügy / jog | 4. mell. 1. pont |
| 3 | ISO 9001 (vagy elfogadott szoftver-QMS) gap + tanúsító | RA | C-201, 2026-09-30 |
| 4 | Döntés: saját EESZT-engedély vs vendor-modul (A8) | Ügyvezetés | REG-040b igen/nem |
| 5 | OQ-05 counsel (párhuzamos, A.1 szűkített szöveg) | Külső jog | F1+ MDSW igen/nem |
| 6 | OQ-15: shadow = Art. 62 vizsgálat-e (ha F1s a F0-ban indul) | RA + intézmény | REG-090 döntés |

A 2026-09-30 **kb. 7 hét** 2026-08-12-től. ISO 9001 nulláról ebben az ablakban szűk — ha nincs tanúsítvány, ez az F0 egyetlen kritikus útja, nem a kód.

---

## C.5 Ami szándékosan nincs ebben a mellékletben

- FHIR API az EESZT-hez (nincs nyílt FHIR; NG-05).
- BM szoftverengedély-kérelem sablonja (Redmine-dokumentáció, nem publikus ebben a körben).
- Az engedélyezett medikai rendszerek BM-táblázata (folyamatosan frissül; P6 célfiók, nem spec-kód).
