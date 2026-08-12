# Vevő RA / jog — FAQ (rendszerlicenc)

| | |
| --- | --- |
| **Iktató** | PCE-SALES-RAFAQ / v1.2 |
| **Státusz** | Tájékoztató. Nem a ti counselötök. Nem OQ-05/17 pecsét. |

---

## 1. Mit veszünk? Leletet vagy eszközt?

**Rendszert.** F1+, F1s, F2, F3 egy szoftver. A szerződés a `[HU|EU|US]` csomag **bekapcsolt** moduljaira szól. A zárt F2/F3 a telepítésben lakattal van; klinikai használatuk tiltott.

---

## 2. Ha F2 bent van a kódban, az már MDSW-forgalmazás?

A gyártó álláspontja: **nem**, ha a klinikai UI-ra **nem** megy kimenet (`LIVE_CDS=false`, FR-470), és a rendeltetés a bekapcsolt modulé. A hatóság a *tényleges használatot* nézi. Ha a felíró riasztást kap, az F2, CE/in-house/FDA nélkül = tilos (NG-07). A lakat nem színház: admin nem billenti.

OQ-05 a **F1+** rétegre. F2/F3 külön intended purpose (A.3).

---

## 3. Miért nincs CE / 510(k) a teljes dobozon?

Mert a forgalomba hozott *funkció* a csomag ON modulja. A zárt CDSS-re nincs CE, amíg F3. US: OQ-17 nyitott; default F2/F3 LOCK.

---

## 4. US vs EU — átkapcsolható?

Nem egy checkbox. Új tenancy, új intended purpose. Az FDA 2022 CDS „az orvos le tudja vezetni” **nem** érvényes az MDR-ben. Az EU nem-MDSW **nem** érvényes automatikusan az FDA-nál.

---

## 5. Ki hívja a genotípust?

A vevő laborja. A PCE nem hív nyers adatból (NG-01). A labor integrációs partner, nem a szoftver kiskereskedelmi vevője.

---

## 6. 2008/XXI. (HU)?

6. § (2) tanácsadás, 8. § beleegyezés, 12. § szolgáltató. A rendszer kapuz. EU/US csomagban ez a kapu N/A; helyi jog `[NEEDS VERIFICATION]`.

---

## 7. GDPR / HIPAA?

Adatkezelő: az intézmény. Gyártó: feldolgozó. F1s külön DPIA (OQ-16). US: HIPAA BAA, OQ-17 mellett.

---

## 8. EESZT?

A rendszer **nem** ír eReceptet/eProfilt. HIS-modul.

---

## 9. Felelősség

Terápia: kezelőorvos. Diplotípus: labor. Bekapcsolt szoftverhibája: gyártó, disclaimer nem zárja ki. LOCK modul használata: szerződéses tiltás.

---

## 10. Pilot

Sandbox, SYN-adatok, F2 lakat látszik, nem él. Éles: megrendelőlap §3.

---

## 11. Van RWE / SOTA a PCE-re? (CureMD-cikk)

A CureMD/arXiv 2603.14876 **nem** a PCE bizonyítéka: US diagnózis CBC/CMP-ből, L5 preprint, Top-5 accuracy 83,10% **nem** a G3.

PGx-evidencia: **PREPARE** (Lancet 2023;401:347–356). Actionable DGI: 21,0% vs 27,7% klinikailag releváns ADR (grade 2–5, possible+), OR 0,70, **p = 0,0075**. Magyarország nincs a 7 országban. Ez a *panel + DPWG felírás* evidencája, **nem** a PCE saját RWE-je, **nem** ápolási nap.

Részlet: [literature-boundary.md](literature-boundary.md). YouScript/ActX: [competitor-analogs.md](competitor-analogs.md).
