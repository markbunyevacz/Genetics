# DPO / DPIA kérdőív — Adatvédelmi kontrollcsomag (OQ-16)

| | |
| --- | --- |
| **Iktató** | PCE-OUT-OQ-16 / v1.2 |
| **Dátum** | 2026-08-12 |
| **Státusz** | TERVEZET — küldhető; **nem** DPIA, **nem** DPO-határozat |
| **Feladó** | `[Gyártó neve]` (A9; név a fejlécben töltendő) |
| **Címzett** | Adatvédelmi tisztviselő (DPO) / DPIA munkacsoport |
| **Tárgy** | Az F1s (Shadow Mode) gateway anonimizálási kontrolljainak jóváhagyása |
| **OQ** | OQ-16 — **ELŐTERJESZTVE**, a jelen irat **nem** zárja |

Tisztelt DPO / DPIA munkacsoport!

Kérjük, a csatolt E melléklet (E.3, E.3.1, E.5, E.5.1) és a FR-461 követelmények alapján döntse el, hogy az F1s **default** út jogilag **anonim** adatfolyam-e, vagy álnevesített út + FR-115 (kutatási hozzájárulás) kötelező.

A gyártó kérése: **anonim default** a lenti kontrollok mellett, A14 küszöb **monitorozásával** akkor is, ha ez rontja a G3 metrikát (R-020).

---

## 0. Két hozzájárulás — ne keverjük

| Kapu | Jog | Shadow anonim út | Shadow álnevesített út |
| --- | --- | --- | --- |
| **FR-100** klinikai | 2008/XXI. 6. § (2) tanácsadás + 8. § beleegyezés + 12. § (1) szolgáltató | **Mindig kell** a PGx-vizsgálathoz / F1+ lelethez | **Mindig kell** |
| **FR-115** kutatási | GDPR 6(1)(a) + 9(2) (vagy a counsel által választott 9(2) pont) a shadow/HITL-re | **Csak ha** a DPO szerint a kimenet mégis személyes adat | **Kötelező** |

Az 1. döntési pont **nem** azt kérdezi, hogy a mintavételkor elhagyható-e a klinikai genetikai beleegyezés. **Nem hagyható el.** Az 1. pont csak a shadow-tárba menő, gateway utáni adatra vonatkozik.

Adatkezelő (váz, E.5): labor/kórház. Gyártó: adatfeldolgozó a DPA szerint, hacsak a counsel mást nem mond a saját kutatási adatbázisra.

---

## I. Alkalmazott technikai kontrollok (FR-461, E.3.1)

Az intézményi (kórházi/labor) zónán belül elhelyezkedő **Gateway** (FR-460) az alábbi transzformációkat hajtja végre a külső shadow-tárba való továbbítás **előtt**. A PCE felhő **nem** kap TAJ-t / nevet. Anonim úton **nincs** re-ID kulcs a gyártónál.

### I.1 Személyazonosítók

| Mező | Anonim út |
| --- | --- |
| Név, telecom, lakcím | Törölve |
| TAJ, személyi, egyéb `Patient.identifier` | Törölve |
| `Patient.id` | Új, nem visszavezethető UUID; **nincs** kulcs a PCE-nél |
| Practitioner, osztály, orvosnév | Törölve |
| Adagolás (`doseQuantity`) | **Nem** megy ki |

### I.2 Időbélyeg-generalizálás

A felírási / vizsgálati időpontok (`MedicationRequest.authoredOn` és hasonló) kizárólag naptári **év/negyedév** szintre (pl. `2026-Q3`) butítva kerülnek továbbításra. Nincs nap, óra, perc.

`Patient.birthDate`: a gatewayen legfeljebb **év**; a HITL kártyán születési év **nem** jelenik meg (FR-450).

### I.3 ATC-kód csonkolás

Anonim úton **tilos** az ATC **5. szint** (7 karakter, hatóanyag, pl. N06AB10). Default maximum: ATC **4. szint** (5 karakter, pl. N06AB — szelektív szerotonin-visszavétel gátlók). Forrás: WHO ATC struktúra (S032).

A DPO szigoríthat ATC3-ra (4 karakter, pl. N06A). Ár: a shadow motor nem különbözteti a paroxetint más SSRI-től (R-020).

### I.4 k-anonymity / ritka kombináció (A13, A14)

Intézményi cella: (fenotípus-osztály × ATC-szint × negyedév) a gateway **helyi** statisztikáján; a nyers count **nem** megy a PCE-hez.

- Ha a cella elemszáma **&lt; k**, a Gateway a rekordot automatikusan magasabb osztályra aggregálja (coarsen) **vagy** teljesen eldobja (`E-SHADOW-003`).
- Default **k ≥ 5** (A14). A felhasználói vázlat „k < 5” megfogalmazása ugyanaz a küszöb: az elemszám nem éri el az 5-öt.
- Ritka diplotípus: populációs gyakoriság &lt; **0,5%** `[ASSUMPTION]` A14 → coarsen vagy drop. A gyakoriság-tábla verziózott config (gnomAD / PharmGKB — a DPIA megnevezi).
- A legritkább diplotípus-osztály default **drop**, akkor is, ha a G3 recall csökken. Nincs manuális k-küszöb override az F1s anonim úton.
- A gateway `E-SHADOW-003` drop-arányt és a k-cella eloszlást aggregáltan (nem PII) jelenti a DPO-nak legalább **negyedévente**.

---

## II. Re-identifikációs forgatókönyvek és védelem

### Forgatókönyv A — Ritka kombinációk

Egy ritka diplotípus és egy specifikus ATC4 csoport egybeesése szűk intézményi környezetben azonosíthatja a beteget.

**Védelem (A13 / FR-461):** cella &lt; k → coarsen vagy drop. A DPO szigoríthat (nagyobb k, ATC3, csak fenotípus-osztály).

### Forgatókönyv B — Hosszú távú követés

A havi HITL review miatt az adatok az **A15** protokoll szerint hónapokig–évekig tárolódhatnak a HITL tárban. **A15 nem 72 órás puffer** (VC-12).

**Feltétel:** a rekord **már anonim** (jelen OQ-16 IGEN) **vagy** van érvényes FR-115.

### Forgatókönyv C — Hozzájárulás-visszavonás (A10, nem TTL)

**A10** a klinikai / kutatási hozzájárulás **visszavonási** kaszkádja (FR-110), nem a shadow alapértelmezett élettartama. A 26. § (1) megsemmisítést ír elő határidő nélkül; a **72 óra** gyártói SLA `[ASSUMPTION]`.

| Esemény | Klinikai tenancy | Álnevesített HITL | Már anonim HITL (nincs kulcs) |
| --- | --- | --- | --- |
| Visszavonás | 72 h: genetikai tartalom megsemmisítése | 72 h: **törlés vagy** irreverzibilis anonimizálás | Klinikai tenancy törlése; HITL-sor a DPIA szerint maradhat (nincs join) |

Álnevesített, visszavont sort az A15 **nem** tart meg.

---

## III. DPO döntési pontok

Minden sor kötelező. NEM esetén a „akkor” oszlop életbe lép.

### A. Anonimitás és hozzájárulás

**A1.** Elegendő-e az ATC4 csonkolás, a negyedéves idő, a k ≥ 5 elnyomás és a ritka-diplotípus drop ahhoz, hogy a gateway **utáni** adatfolyamot jogilag **anonim** útnak tekintsük (GDPR személyes adat **nem**)?

- [ ] IGEN
- [ ] NEM — ekkor álnevesített út + **FR-115** kötelező; A12 hamis
- [ ] FELTÉTELLEL: .................................................................................................

**A2.** Ha A1 = IGEN: megerősíti-e, hogy ez **nem** mentesít a klinikai FR-100 (6. § (2) / 8. §) alól a PGx-vizsgálatnál / F1+ leletnél?

- [ ] IGEN (FR-100 marad)
- [ ] NEM — indoklás kötelező (a gyártó specje szerint ez nem védhető): .................................................................................................

**A3.** Jóváhagyja-e, hogy A1 = IGEN esetén a shadow mintavételekor **külön** kutatási (FR-115) hozzájárulás **nem** kell?

- [ ] IGEN
- [ ] NEM — FR-115 akkor is kell

### B. Küszöbök

**B1.** Elfogadja-e a default **k ≥ 5** intézményi cellát?

- [ ] IGEN
- [ ] NEM — előírt k = ________

**B2.** Elfogadja-e az ATC **4. szint** maximumot, ATC5 tiltással?

- [ ] IGEN
- [ ] NEM — előírt max: ATC3 / ATC2 / egyéb: ________

**B3.** Elfogadja-e a 0,5%-os ritka-diplotípus küszöböt mint A14 feltevést, a DPIA-ban megnevezendő gyakoriság-táblával?

- [ ] IGEN
- [ ] NEM — küszöb / forrás: ________

**B4.** Jóváhagyja-e, hogy a legritkább osztályok **drop**ja G3 rovására is kötelező, és a k-küszöbnek nincs manuális override-ja anonim úton?

- [ ] IGEN
- [ ] NEM — feltétel: .................................................................................................

### C. Megőrzés és visszavonás

**C1.** Jóváhagyja-e az A10 szerinti **72 órás** visszavonási SLA-t a klinikai tenancyre és az álnevesített HITL-re (törlés **vagy** irreverzibilis anonimizálás)?

- [ ] IGEN
- [ ] NEM — előírt SLA: ________ (a 26. § (1) határidő nélküli megsemmisítés ettől független)

**C2.** Jóváhagyja-e az A15 szerinti protokoll-megőrzést (hónapok–évek, havi HITL) **csak** már anonim vagy érvényes FR-115-ös sorokra?

- [ ] IGEN
- [ ] NEM — feltétel: .................................................................................................

**C3.** Már anonim HITL-sor (nincs join-key): a klinikai visszavonás után a HITL-sor a DPIA szerint **maradhat**?

- [ ] IGEN
- [ ] NEM — törlendő a HITL is

### D. Szerepek és üzemeltetés

**D1.** A Gateway kötelezően az **intézményi** hálózati zónában fut (FR-460). Elfogadja?

- [ ] IGEN
- [ ] NEM

**D2.** Adatkezelő = intézmény/labor; gyártó = adatfeldolgozó a DPA szerint. Elfogadja, vagy a saját shadow-tárra a gyártó (közös) adatkezelő?

- [ ] Feldolgozó (gyártói váz)
- [ ] (Közös) adatkezelő — indoklás: .................................................................................................

**D3.** `Patient.gender` megtartható az anonim úton?

- [ ] IGEN
- [ ] NEM — törlendő

**D4.** Negyedéves aggregált drop/k-riport a DPO-nak (nem PII). Elfogadja?

- [ ] IGEN
- [ ] NEM — gyakoriság: ________

---

## IV. Aláírás

A DPIA külön dokumentum; ez a kérdőív a DPIA **inputja**. OQ-16 a F.6 sor kitöltéséig nyitott. F1s HIS-csatlakozás OQ-16 nélkül **nem** indul.

| | |
| --- | --- |
| DPO neve | .................................... |
| Szervezet | .................................... |
| Dátum | .................................... |
| Aláírás | .................................... |

**Mellékletek:** PCE-SPEC-v1.2 (FR-115, FR-460, FR-461, A10/A15 §0.1); E melléklet; F.3; WHO ATC struktúra (S032).

*Ha A1 = NEM, a gyártó az álnevesített utat és az E.6 FR-115 sablont viszi — nem „titkos anonimizálás”.*
