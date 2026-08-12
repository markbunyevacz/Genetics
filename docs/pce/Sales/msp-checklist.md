# MSP — Minimum eladható termék (enélkül ne fogadj klinikapénzt)

| | |
| --- | --- |
| **Iktató** | PCE-SALES-MSP / v1.2 |
| **Kapcsolat** | §10.2 F1+ mag; G4 |
| **Szabály** | Pilot-díj **szintetikus** adatokon mehet MSP előtt is. **Éles** SKU-C / beteglelet **nem**. |

Az MSP a **eladható F1+**, nem a teljes SRS. A spec P0-jai közül azok, amelyek nélkül a vevő nem kapja meg, amit a one-pager ígér.

---

## A. Üzleti kapu (ember, nem kód)

| # | Kész? | Tétel | Nélküle |
| --- | --- | --- | --- |
| A1 | [ ] | `[Gyártó neve]` kitöltve a one-pagereken | Nincs kiállítható ajánlat |
| A2 | [ ] | Legalább egy labor **névvel** a term sheeten (OQ-03) | SKU-C üres — a klinika nem vehet vizsgálatot tőled (12. §) |
| A3 | [ ] | `[Y1]` / `[Y2]` / `[X]` kitöltve a labornak | Nincs számla |
| A4 | [ ] | Ajánlat §2 (OQ-05 mint feltétel) benne van | MDSW-t hazudsz vagy eladhatatlanul bizonytalan |
| A5 | [ ] | DPA-szerep rögzítve (kezelő vs feldolgozó) | A klinika DPO-ja megállítja |
| A6 | [ ] | Demó-forgatókönyv betartva (nincs felugró) | A következő hívás a vevő RA-jával elveszett |

A2 a kemény: **klinikának eladni labor nélkül = B2C genetikai vizsgálat**, ami NG-03.

---

## B. Szoftver kapu (F1+ mag)

| # | Kész? | FR | Elfogadás a vevő előtt |
| --- | --- | --- | --- |
| B1 | [ ] | FR-240 | Egy SYN-eset outside-call → riport |
| B2 | [ ] | FR-210 | Egy SYN-eset missing-to-ref → `INDETERMINATE`, nem NM |
| B3 | [ ] | FR-400-STATIC | CYP2D6 (vagy egy PREPARE-gén) **teljes** tábla, MedicationEntry nélkül |
| B4 | [ ] | FR-410-EDU | Oktató bekezdés; tiltott token („Ön”, „a most felírt”) nincs |
| B5 | [ ] | FR-490 / A.1.1 | Minden PDF-oldalon a nyilatkozat + aláíró hely |
| B6 | [ ] | FR-500 | White-label logo placeholder; FHIR Bundle *vagy* PDF (PDF a minimum a labornak) |
| B7 | [ ] | FR-100 | Consent hiányában nincs riport (`E-CONSENT-001/003`) — a demóban is |
| B8 | [ ] | FR-470 | `LIVE_CDS=false`; a demó buildben nincs CDS endpoint |
| B9 | [ ] | FR-310 | Default panel = PREPARE 12, verziózott config |
| B10 | [ ] | FR-700 | Nincs LLM a lelet szövegén |

Matcher (FR-300) **ki**. VCF-útvonal P1 a *eladáshoz*; az első labor outside-call-lal is tud venni.

---

## C. Élesítés (pénz + betegadat)

| # | Kész? | Tétel |
| --- | --- | --- |
| C1 | [ ] | OQ-05 írásban **vagy** a szerződés csak pilot (proposal §2) |
| C2 | [ ] | REG-020 aláírva a névvel bíró labarral |
| C3 | [ ] | DPA aláírva |
| C4 | [ ] | ISO 9001 státusz közölve (folyamatban is elég magánlabor-pilotra; 2026-09-30 a kapu) |
| C5 | [ ] | Éles tenancy a labor/HIS zónájában; TAJ nem a gyártó „shadow” felhőjében |

SKU-S (shadow) **nem** MSP. Ne tedd az első számlára.

---

## D. G4 számolás

Fizető partnernek számít:

- Aláírt SKU-L (labor) — **igen**
- Aláírt SKU-H (vendor) — **igen**
- Klinika, aki a labortól rendel leletet, és a labor PCE-t használ — **igen**, ha a lánc dokumentált (SKU-C + REG-020)
- Ingyenes demó, LOI aláírás nélkül, „majd CE után” handshake — **nem**

Cél: ≥ 3. Az első **mindig** labor.
