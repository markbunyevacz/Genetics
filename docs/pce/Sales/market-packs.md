# Piaci csomagok — HU / EU / US (flag, nem három termék)

| | |
| --- | --- |
| **Iktató** | PCE-SALES-MKT / v1.2 |
| **Szabály** | Egy kódbázis. `MARKET_PACK` + modul-licencek. Feloldás = change-control + minősítés, nem hotfix. |
| **Nem** | FDA CDS guidance átmásolása az MDR alá. US-pecsét nélkül F2-t US-ben sem kapcsolunk. |

A vevő azt kéri: „működő F1, F1s, F2, F3”. A válasz: **a rendszer ez**. Amit a szerződés ad: melyik flag **true** ezen a telephelyen.

---

## Flag-mátrix (default)

Jelölés: **ON** = a modul a rendeltetése szerint fut. **LOCK** = a kód megvan, klinikai UI / élő kimenet tiltva (FR-470). **N/A** = a piac joga nem ezt a kaput kéri.

| Modul / kapu | **HU** | **EU** (nem HU) | **US** |
| --- | --- | --- | --- |
| F1+ L4-static lelet | ON, ha OQ-05 IGEN; különben LOCK→IIa | u.a. (MDR) | ON csak US counsel szerint; default LOCK, amíg OQ-17 |
| F1s shadow + HITL | LOCK→ON OQ-15+16 után | u.a. (GDPR/DPIA a helyi DPO) | US IRB / HIPAA + US counsel; default LOCK |
| F2 élő CDSS (in-house) | LOCK; ON csak REG-011 + intézmény | LOCK; ON csak MDR in-house a *telepítő* tagállamban | LOCK; US in-house **nem** MDR-in-house. OQ-17 |
| F3 élő CDSS forgalom | LOCK; ON CE IIa után | LOCK; ON CE IIa után | LOCK; ON 510(k) / De Novo / más FDA út után |
| `LIVE_CDS` | compile/license **false** amíg F2/F3 ON | u.a. | u.a. |
| FR-100 2008/XXI kapu | **ON** (kötelező) | N/A mint HU tv.; helyi genetikai jog `[NEEDS VERIFICATION]` | CLIA-lab + HIPAA; nem 2008/XXI |
| EESZT írás | **OFF** (NG-05) | N/A | N/A |
| ISO 9001 2026-09-30 | HU fejlesztői jogállás (OQ-01) | Nem 9/C. §; ISO 13485 F2/F3-hoz | QSR / QMSR a device-pályán |
| LLM a klinikai úton | OFF (FR-700) | OFF | OFF |
| Saját genotípus-hívás | OFF (NG-01) | OFF | OFF (YouScript/TSI 510(k) minta) |

A HU csomag **EU + magyar kapuk**. Nem külön motor.

---

## Mit jelent a „kikapcsolt funkcionalitás”

1. A F2/F3 **képernyő és API** a telepítésben látszik **lakattal** (licenc + build flag). A vevő látja, hogy a rendszer teljes.
2. A L4-live motor F1s-ben futhat (felíró **nem** látja), ha a shadow csomag ON.
3. Admin **nem** billentheti `LIVE_CDS=true`-ra configgal. Csak signed release + REG-010/011 / FDA clearance (FR-470).
4. Piaci csomagváltás (HU→US tenancy) **nem** egy checkbox a klinikának. Új tenancy, új intended purpose, új dosszié.

---

## Átminősítés (feloldási záradék)

| Lépés | HU / EU | US |
| --- | --- | --- |
| 1 | F1s gold set (G3) | u.a. + US klinikai adat, ha az FDA kéri |
| 2 | ISO 13485 + 62304 + 14971 (REG-030) | QMSR + 62304 |
| 3 | F2: in-house dokumentáció **vagy** F3: NB, CE | 510(k) / De Novo / egyéb — **OQ-17** |
| 4 | `LIVE_CDS=true` signed build, A.3 intended purpose | US intended use a 510(k) szerint |
| 5 | Szerződés: modulaktiválási díj `[Ya]` | u.a. |

Amíg 4 nincs: a sales **nem** mondja, hogy „jövő héten bekapcsoljuk a riasztást”.

---

## OQ-17 — US (nyitott, nem blokkolja a HU/EU licencet)

Kérdés a **US counselnek**, nem az EU OQ-05-nek:

> A PCE **ugyanazon** bináris F2/F3 kimenete (beteg–gyógyszer, felírás-pillanat) eszköz-e az FD&C Act / 2022 CDS guidance szerint, és milyen premarket út kell? A genotípus-hívás **kint** marad (NG-01).

**Tilos:** EU-s nem-MDSW (OQ-05) átvitele US-re, vagy US CDS „az orvos le tudja vezetni” átvitele MDR-re.

Státusz: **NYITOTT**. A US market pack F2/F3 default **LOCK**.

---

## Szerződési egy mondat

> A Vevő a PCE rendszert a `[HU|EU|US]` csomagban licenceli. A nem ON modulok a szoftver részét képezik, klinikai használatuk tiltott. Feloldás írásos aktiválással, a gyártó signed release-ével és az adott piac szabályozási feltételének teljesülésével.
