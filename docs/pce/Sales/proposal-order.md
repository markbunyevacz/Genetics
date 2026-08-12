# Ajánlat és megrendelőlap (SKU-L / SKU-C / SKU-H)

| | |
| --- | --- |
| **Iktató** | PCE-SALES-ORD / v1.2 |
| **Státusz** | Tervezet — **nem** ÁSZF, **nem** DPA |
| **Feladó** | `[Gyártó neve]` |
| **Címzett** | `[Vevő neve]` |
| **Ajánlat érvényes** | `[dátum]`-ig (alap: 30 nap) |

Ez a lap a v1.2 spec kereskedelmi kötése. A szögletes zárójelek a küldőé. Jogi véglegesítés: counsel.

---

## 1. Tárgy

A Vevő a lenti SKU-t rendeli. A gyártó a PCE F1+ szoftvert / modult szállítja a [A.1 rendeltetés](../A-intended-purpose-and-modules.md) szerint.

**Nem tárgy:** élő klinikai döntéstámogatás (F2/F3), EESZT írás, B2C VCF-upload, saját genotípus-hívás.

Jelölj **egyet** (vagy L+H együtt, ha a vendor a labort is kiszolgálja):

- [ ] **SKU-L** — Labor white-label szoftverlicenc
- [ ] **SKU-C** — Klinika: PGx-lelet *szolgáltatás* partnerlaboron keresztül (a szoftvert a labor licenceli; ez a lap a klinika–labor–gyártó háromszöget rögzíti)
- [ ] **SKU-H** — HIS / medikai vendor modullicenc

---

## 2. Hatálybalépési feltételek (kötelező)

A **éles betegadat** és a **fizetős szoftverlicenc** (SKU-L / SKU-H) akkor lép hatályba, ha:

1. **OQ-05:** írásos counsel-állásfoglalás az F1+ A.1 rendeltetésről (IGEN vagy FELTÉTELLEL, a feltételek a szerződésbe emelve). Ha NEM (MDSW): a felek 30 napon belül IIa/CE ütemtervre térnek, vagy a Vevő eláll — a már megfizetett pilot nem jár vissza, ha a pilot teljesült.
2. **SKU-L / SKU-C:** van REG-020 / aláíró labor (`[Partnerlabor]`). SKU-C labor nélkül **érvénytelen**.
3. **Adat:** DPA aláírva. Adatkezelő = `[labor/klinika]`; adatfeldolgozó = `[Gyártó neve]`, hacsak a counsel mást nem ír.
4. **ISO / EESZT:** a gyártó C-201 (ISO 9001 vagy egyéb szoftver-QMS) státusza a Vevővel közölve. 2026-09-30 kapuőr. Hiány **nem** automatikus érvénytelenség magánlabor-SKU-n, de a Vevő 14 napos elállást kap, ha a kapu elvész.

**Pilot (éles hatály előtt):** zárt környezet, szintetikus vagy a labor saját validációs esetei, `[Yp]` Ft + ÁFA, `[T]` hét, éles TAJ **nincs**.

---

## 3. Szolgáltatás és SLA

| Mutató | Cél |
| --- | --- |
| Szoftver: outside-call → aláírásra kész PDF/FHIR p95 | &lt; 10 perc (G1) |
| Labororvosi aláírás (SKU-L, a labor vállalja) | `[X]` óra |
| Rendelkezésre állás (szoftver) | `[99,x %]` munkaidőben; a felírás **nem** blokkolódik ettől a terméktől (nincs élő CDS) |
| Guideline-váltás | FR-510 lista az érintett esetekről (P1; ha a csomagban van) |

---

## 4. Díjak (kitöltendő)

| SKU | Tétel | Összeg | Időszak |
| --- | --- | --- | --- |
| L | Indítás / arculat | `[Y0]` Ft + ÁFA | egyszeri |
| L | Havidíj | `[Y1]` Ft + ÁFA | / hó, `[N]` lelet benne |
| L | Volumensáv | `[Y2]` Ft + ÁFA | / aláírt lelet vagy sáv |
| C | Klinika → labor vizsgálat | a labor díjszabása | nem PCE-ár |
| H | Éves platform | `[Yh]` Ft + ÁFA | / év |
| H | Integráció | `[Yi]` Ft + ÁFA | egyszeri |
| — | Pilot | `[Yp]` Ft + ÁFA | `[T]` hét |

Fizetés: `[munkanap]` nap, számla. Éves SKU-H: `[előre / negyedévente]`.

---

## 5. Felelősségi határ (rövid)

| Tétel | Labor | Klinika | Gyártó | HIS-vendor |
| --- | --- | --- | --- | --- |
| Diplotípus-hívás | Igen | Nem | Nem | Nem |
| Lelet aláírása | Igen | Nem | Nem | Nem |
| Terápia | Nem | Kezelőorvos | Nem | Nem |
| Renderer / guideline-config hiba | — | — | Szoftverhiba a hatályos jog szerint | — |
| HIS-megjelenítés | — | — | Interfész-szerződés | Saját medikai rendszer |

A.1.1 a leleten. **Nincs** „minden felelősség kizárva” klauzula.

REG-021 (SKU-H): a vendor nem MDSW-gyártó az F1+ motorra.

---

## 6. Adat

- Nincs B2C feltöltés.
- Éles genetikai adat csak FR-100 kapu után.
- F1s / shadow **nem** része ennek a megrendelésnek, hacsak SKU-S külön nem keltezve (OQ-15/16).
- Feldolgozói utasítás: a gyártó a lelet előállításához szükséges adatot kezeli; TAJ a gyártó shadow-felhőjébe F1+-on **nem** a default (klinikai tenancy a labor/HIS zónájában — B melléklet).

---

## 7. Roadmap-mondat (nem teljesítési kötelezettség)

Az élő felírási riasztás (F2) **nem** e szerződés tárgya. A felek tudomásul veszik, hogy ugyanaz az integrációs cső később minősített CDSS-re kapcsolható; ehhez külön szerződés és CE / in-house kell.

---

## 8. Aláírás

- [ ] Pilot megrendelés (éles feltétel §2 nélkül, TAJ nélkül)
- [ ] Éles SKU, §2 feltételekkel

| | Vevő | Gyártó |
| --- | --- | --- |
| Név / pozíció | | |
| Dátum | | |
| Aláírás | | |

**SKU-C:** a partnerlabor képviselője is aláír, vagy csatolt REG-020.

| Partnerlabor | Név | Dátum | Aláírás |
| --- | --- | --- | --- |
| `[Partnerlabor]` | | | |
