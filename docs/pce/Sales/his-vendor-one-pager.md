# HIS / medikai vendor egyoldalas — F1+ modul (SKU-H)

| | |
| --- | --- |
| **Feladó** | `[Gyártó neve]` |
| **Címzett** | `[Medikai rendszer / HIS vendor neve]` — termék + jog |
| **Tárgy** | PGx-lelet modul az engedélyezett medikai rendszerben — ti nem lesztek MDSW-gyártók |
| **Státusz** | Ajánlati egyoldalas. REG-021 határvonal. |

Tisztelt Partner!

A klinikai vevőitek PGx-leletet akarnak **a saját HIS-ükben**, nem egy külön portálon. Nem akarnak — és ti sem akartok — orvostechnikai szoftver-gyártóvá válni egy felírási riasztás miatt.

Az F1+ modul: a partnerlabor aláírt leletének megjelenítése + opcionális **enciklopédia** (génre / hatóanyagra keresés, verziózott guideline). **Nincs** CDS Hooks `order-sign` kártya. **Nincs** EESZT írás (eRecept, eProfil).

---

## Mit kaptok

- FHIR / dokumentum-interfész a leletre (Genomics Reporting IG STU3, R4).
- White-label a labor felé; a HIS a saját UX-ében jeleníti meg.
- Írásos MDR-határ (REG-021): **gyártó = `[Gyártó neve]`** az F1+ motorra; **ti** a medikai rendszer gyártói / forgalmazói maradtok a saját engedélyetek szerint.
- Ugyanaz a cső később F2-re (CE után) — a `LIVE_CDS` kapcsoló a mi release-ünk, nem a ti konfigotok.

## Mit nem kaptok v1-ben

- Interruptive CDSS, dózis-suggestion, SMART-on-FHIR felírási riasztás.
- Nyílt EESZT FHIR API-t vagy BM szoftverengedélyt tőlünk (NG-05; F1 = modul).
- Azt a jogi állítást, hogy „az orvos rákattint, tehát nem eszköz”.

## Ár (kitöltendő)

| Tétel | Összeg |
| --- | --- |
| Éves platform | `[Yh]` Ft + ÁFA / év |
| Integráció (egyszeri) | `[Yi]` Ft + ÁFA |
| Tenant / labor | a SKU-L szerint, nem a vendor árrése helyett |

## Hatály

REG-021 + OQ-05 feltétel. Pilot: sandbox, szintetikus Bundle, nincs éles TAJ.

---

| | |
| --- | --- |
| Kapcsolat | `[név, e-mail, telefon]` |
| Melléklet | A.1; B melléklet interfész-váz; REG-021 sablon-pontok a proposal-orderben |
