# Ajánlat és megrendelőlap — PCE **rendszerlicenc**

| | |
| --- | --- |
| **Iktató** | PCE-SALES-ORD / v1.2 |
| **Státusz** | Tervezet — nem ÁSZF, nem DPA |
| **Feladó** | `[Gyártó neve]` |
| **Címzett** | `[Vevő — klinika / kórház / hálózat / HIS-vendor]` |
| **Market pack** | `[HU | EU | US]` |
| **Ajánlat érvényes** | `[dátum]`-ig (alap: 30 nap) |

A Vevő a **Precision Clinical Engine rendszert** rendeli (F1+ · F1s · F2 · F3 egy szoftver). Nem PGx-vizsgálatot, nem lelet-előfizetést.

---

## 1. Tárgy

- [ ] **SKU-P** — Intézményi rendszerlicenc (alap)
- [ ] **SKU-H** — HIS-vendor beágyazás (REG-021)

Labor: csatlakozó, nem ez a megrendelés tárgya. Csatolt REG-020: `[van / folyamatban / a Vevő laborja]`.

**Nem tárgy, amíg a flag LOCK:** élő felírási CDSS a klinikai UI-n, EESZT írás, B2C VCF-upload, saját allélhívás.

---

## 2. Modulmátrix (ez a telephely)

A nem ON sorok a szoftver **részei**, klinikai használatuk tiltott. Feloldás: §8.

| Modul | Ezen a megrendelésen |
| --- | --- |
| F1+ lelet / L4-static | `[ON / LOCK]` |
| F1s shadow + HITL | `[ON / LOCK]` |
| F2 élő CDSS (in-house) | **LOCK** |
| F3 élő CDSS (CE/FDA) | **LOCK** |
| `LIVE_CDS` | **false** |

Market pack szabály: [market-packs.md](market-packs.md).

---

## 3. Hatálybalépés

**Éles betegadat** és a platformlicenc akkor él, ha:

1. A `[HU|EU|US]` csomag szerinti külső feltétel: HU/EU F1+ ON-hoz OQ-05 *vagy* IIa/CE; US-hez OQ-17. Addig: fizetős sandbox.
2. Diplotípus-forrás csatlakoztatva (Vevő laborja / REG-020).
3. DPA: adatkezelő = Vevő (és/vagy labor); gyártó = feldolgozó.
4. HU csomag: FR-100 kapu; OQ-01 státusz közölve.

**Pilot:** szintetikus vagy labor-validációs eset, TAJ nélkül, `[Yp_pilot]`, `[T]` hét. A F2 UI lakattal **mutatható**, nem üzemeltethető.

---

## 4. Díjak

| Tétel | Összeg |
| --- | --- |
| Platform `[HU\|EU\|US]` | `[Yp]` / év |
| Telephely / klinikus sáv | `[Yc]` |
| Indítás / HIS | `[Y0]` egyszeri |
| SKU-H integráció (ha jelölve) | `[Yi]` |
| F2/F3 aktiválás (később, §8) | `[Ya]` |
| Pilot | `[Yp_pilot]` |

Sávok magyarázata: [market-packs.md](market-packs.md) árazási mátrix. A YouScript 365 USD/év **nem** ennek a táblának az ára.

---

## 5. SLA (bekapcsolt modulokra)

| Mutató | Cél |
| --- | --- |
| Ingest → F1+ aláírásra kész p95 | &lt; 10 perc (szoftver) |
| Rendelkezésre állás | `[99,x %]` |
| Élő CDSS késleltetés (csak ha F2 ON) | fail-open: a felírás nem blokkolódik |
| Shadow hiba | nem jelenik meg a felírónak |

---

## 6. Felelősség

| Tétel | Vevő / kezelőorvos | Labor | Gyártó |
| --- | --- | --- | --- |
| Terápia | Igen | Nem | Nem |
| Diplotípus-hívás | — | Igen | Nem |
| Bekapcsolt szoftverhibája | — | — | Hatályos termékfelelősség; nincs „minden kizárva” |
| LOCK modul klinikai használata | Tiltott; a Vevő nem kapcsolhatja | — | Nem ad signed `LIVE_CDS=true`-t feltétel nélkül |

---

## 7. Adat

HU: 2008/XXI. kapu. Shadow csak ha F1s ON és OQ-16/15. Nincs B2C feltöltés.

---

## 8. Feloldás (átminősítés)

F2/F3 ON csak: (a) írásos aktiválási megrendelés `[Ya]`, (b) HU/EU: CE vagy in-house (REG-011) / US: OQ-17 szerinti FDA-út, (c) gyártó signed release, A.3 intended purpose, (d) `LIVE_CDS=true` ettől a buildtől. Admin-config **nem** elég.

---

## 9. Aláírás

- [ ] Pilot (sandbox, F2 LOCK)
- [ ] Éles SKU-P, §2–3 szerint

| | Vevő | Gyártó |
| --- | --- | --- |
| Név / pozíció | | |
| Market pack | `[HU\|EU\|US]` | |
| Dátum / aláírás | | |
