# A vevő RA / jogásza — FAQ (SKU-C / SKU-L / SKU-H)

| | |
| --- | --- |
| **Iktató** | PCE-SALES-RAFAQ / v1.2 |
| **Címzett** | A vevő minőségirányítása, jogásza, DPO-ja |
| **Státusz** | Tájékoztató. **Nem** helyettesíti a saját counselüket. **Nem** az OQ-05 pecsét. |

A komoly klinika és labor **ezt** kérdezi, mielőtt aláír. A sales, aki ezt kikerüli, nem zár.

---

## 1. Ez orvostechnikai eszköz (MDSW)?

**Gyártói pozíció (kérés, nem pecsét):** az F1+ a labor által *már megállapított* diplotípus formázása és **gén-szintű**, verziózott, nyilvános irányelv-szöveg hozzárendelése. Nincs aktuális-gyógyszer párosítás, nincs felírási riasztás, nincs dózisszám. Aláíró: labororvos.

**Nyitott:** külső counsel (OQ-05). A génhez rendelt CPIC *terápiás* szöveg önmagában lehet Rule 11a. A szerződés **hatálybalépési feltétele** ez az állásfoglalás.

**Nem érv:** „az orvos dönt, tehát nem eszköz.” Az MDR-ben ez nem minősít ki.

---

## 2. Miért nincs CE-jel?

Ha OQ-05 = IGEN: a gyártó szerint nem MDSW, CE nem e termékre kell. Ha OQ-05 = NEM: nincs éles szoftvereladás CE nélkül; IIa pálya.

A leleten lévő nyilatkozat **nem** CE-helyettesítő és **nem** felelősségkizárás.

---

## 3. A klinika MDSW-üzemeltető lesz?

F1+ SKU-C-n: a klinika **laboratóriumi jelentést** használ, mint más leletet. Nem futtat felírási CDSS-t. SKU-H: a HIS megjeleníti a dokumentumot; a vendor REG-021 szerint nem az F1+ motor gyártója.

Ha a klinika **élő riasztást** kér a felírásnál: az F2, más szerződés, CE vagy in-house.

---

## 4. Ki hívja a genotípust? Ki ír alá?

A partnerlabor. A PCE nem hív allélt nyers adatból. Minden F1+ leletet labor-szakorvos ír alá. Aláírás nélküli „validált PDF” nincs.

---

## 5. 2008. évi XXI. törvény?

Mintavétel előtti tanácsadás: **6. § (2)**. Írásbeli beleegyezés: **8. §**. Vizsgálat: engedélyezett szolgáltató, **12. § (1)**. A szoftver **kapuz** (FR-100); a kötelezettség a szolgáltatóé. A gyártó nem B2C genetikai app.

---

## 6. GDPR / genetikai adat?

Adatkezelő: labor és/vagy klinika. Gyártó: adatfeldolgozó a DPA szerint. Éles TAJ a gyártó kutatási felhőjébe nem default. Shadow/HITL **külön** termék (OQ-16/15), nem ennek a v1 SKU-nak a része.

Visszavonás: 26. § megsemmisítés; a gyártó 72 órás SLA-t **feltételez** (A10), a törvény határidőt nem ad.

---

## 7. EESZT?

A v1 **nem** ír az EESZT-be. Modul engedélyezett medikai rendszerben. ISO 9001 / szoftver-QMS: 2026-09-30 kapu a fejlesztői jogálláshoz — státuszt kérdezzetek, ne feltételezzetek 13485-öt.

---

## 8. Felelősség, ha a lelet alapján rossz a terápia?

Terápia: kezelőorvos. Diplotípus: aláíró labororvos. Szoftverhiba (rossz tábla, rossz verzió, hamis NM callability nélkül): gyártó, a hatályos termékfelelősség szerint. Disclaimer ezt **nem** zárja ki.

---

## 9. Mit kaptok a dossziéból?

- A.1 / A.1.1 / A.1.2 (intended purpose + EDU szabályok)
- Outbound OQ-05 brief (a *kérés*, nem a válasz)
- FR-470: `LIVE_CDS=false` az F1+ buildben
- Ez a FAQ

Amit **nem** kaptok tőlünk pecsétként: a ti counselötök helyetti MDSW-minősítés.

---

## 10. Pilot vs éles

Pilot: szintetikus vagy labor-validációs eset, TAJ nélkül, fizetős is lehet. Éles beteglelet: §2 feltételek (OQ-05, REG-020, DPA).
