# E melléklet — Shadow-mode, HITL, anonimizáló gateway, kutatási hozzájárulás

| | |
| --- | --- |
| **Dokumentum** | PCE-SPEC-v1.2 Appendix E |
| **Dátum** | 2026-08-12 |
| **Kapcsolat** | A.2, FR-115, FR-440–FR-470, REG-090 |
| **Státusz** | Műszaki + GDPR váz; **nem** DPA, **nem** klinikai vizsgálati kérelem |

A shadow **nem** az F1+ klinikai termék. Külön adatút, külön IAM, külön store. Ha a kezelőorvos ellátásban látja, az F2.

---

## E.1 Üzleti kötés (nem TAM)

Az F1+ white-label statikus lelet a labor manuális szövegezését váltja ki — ez a fizető termék. A kórházi IT-nek az F1+ „okos lelet, nem élő riasztás” könnyebb belépő, mint a interruptive CDSS. Az F1s a **ugyanazon** integrációs csövön (Subscription → gateway) építi a későbbi F2 kapcsolót; a kapcsoló CE / in-house nélkül **nem** billenhet klinikai UI-ra (FR-470).

---

## E.2 Adatút

```
[ HIS / LIS : recept lezárás | lelet aláírás ]
        │
        ▼  FHIR Subscription / webhook (HTTPS)
[ Anonimizáló / álnevesítő Gateway ]
        │  kötelezően a kórház/labor hálózati zónájában (FR-460)
        ├─► Direct identifiers törölve vagy kód a intézmény KMS-ében
        └─► Observation (diplotípus) + MedicationRequest (ATC) + opcionális Observation (eGFR)
        │
        ▼  TLS 1.3, külön tenant
[ PCE Shadow CDSS ] ──► [ HITL store ]
        │
        X  nincs írás L6-report / CDS Card / SMART klinikai view felé
        │
        ▼
[ HITL UI ]  csak kutató / bizottsági szerep, nem a felíró napi UI
```

**Fail-closed a klinikai szivárgásra, fail-open a felírásra:** a shadow hibája nem blokkolja a HIS-t; a shadow kimenet hiánya nem jelenik meg „nincs PGx” kártyaként a felírónak (az F1+ lelet külön path).

---

## E.3 Gateway — FHIR csonkolás (FR-460)

A gateway **nem** a PCE felhőjében fut. Kimenet csak akkor hagyja el az intézményt, ha a checklist zöld.

| Erőforrás | F1s anonim út (A12 default) | F1s álnevesített út |
| --- | --- | --- |
| `Patient.name`, `telecom`, `address` | Törölve | Törölve |
| `Patient.identifier` (TAJ, személyi) | Törölve | Törölve |
| `Patient.id` | Új, nem visszavezethető UUID; **nincs** kulcs a PCE-nél | Intézményi pszeudonim; kulcs **csak** intézménynél |
| `Patient.birthDate` | Legfeljebb **év** | Legfeljebb év, hacsak a protokoll indokolja |
| `Patient.gender` | Megtartható | Megtartható |
| `Observation` PGx | kód + value (diplotípus); callability | u.a. |
| `MedicationRequest` | ATC / OGYÉI kód + adagolási struktúra, ha a protokoll kéri | u.a. |
| `Practitioner`, org, ward, username | Törölve | Törölve vagy intézményi kód |
| Meta `source`, `lastUpdated` belső ID-k | Tisztítva | Tisztítva |

Irreverzibilis anonimizálás: nincs olyan kulcs, amellyel a gyártó a gént a személyhez köthetné. Ha van kulcs az intézménynél → **álnevesítés**, GDPR személyes adat, FR-115 kötelező.

A 2008/XXI. 26. § szerinti 30 éves genetikai nyilvántartás az **intézmény / biobank** kötelezettsége. A gyártó shadow store-ja: kutatási cél, FR-115 szerinti törlés; nem helyettesíti a 30 éves intézményi naplót.

---

## E.4 HITL felület (FR-450)

- Szerep: `hitl_reviewer` ≠ `clinician` a felíró tenancyben. Ugyanaz a természetes személy lehet mindkettő, **más login / más app**.
- Esetkártya: diplotípus, (ál)anonim gyógyszerlista, motor-kimenet (`functional_phenotype`, javasolt stratégia-kategória, **nem** kötelező `dose_mg` a v1 shadowban), guideline-verzió.
- Válasz: `AGREE` \| `DISAGREE` \| `INSUFFICIENT_DATA` + kötelező kategória-indok.
- Időzítés: nem a vizit alatt; batch (pl. havi) vagy bizottsági ülés.
- G3 / clinical evaluation metrika: reviewer egyetértés a gold set + élő shadow mintán. Nem a felíró override-rátája (az F2 FR-600).

---

## E.5 Két GDPR-út (A12)

| Út | Mikor | Jogalap (váz) | Beteg hozzájárulás a shadowhoz |
| --- | --- | --- | --- |
| **Anonim** (default) | Nincs longitudinális követés | Anonim adat ≠ GDPR személyes adat, *ha* a anonimizálás tényleges | Nem (a klinikai 2008/XXI. hozzájárulás ettől még kell a vizsgálathoz) |
| **Álnevesített** | 6 hónapos kimenet összekötése kell | GDPR 6(1)(a) + 9(2)(a) *vagy* más 9(2) jogalap a counsel szerint | **FR-115** igen; kulcs az adatkezelőnél |

Adatkezelő: labor/kórház. Gyártó: adatfeldolgozó a DPA szerint, hacsak a counsel mást nem mond a saját kutatási adatbázisra. DPIA: REG-050 kiterjesztése a shadowra **élesítés előtt**.

„Tiszta anonimizálás után szabadon tanítjuk a modellt” — csak akkor, ha a anonimizálás **visszafordíthatatlan**. Genetikai + ritka gyógyszerkombináció re-identifikálhat; a DPIA-nak ezt kezelnie kell (k-anonymity / ritka kombináció elnyomása). `[ASSUMPTION]` A13: a gateway ritka-kombináció szűrőt alkalmaz, vagy az álnevesített utat választják.

---

## E.6 Kutatási hozzájárulás váz (álnevesített út) — FR-115

Külön a 6. § (2) / 8. § klinikai beleegyezéstől. Counsel tölti ki; a gyártó neve nem kitalált (A9).

**Cím:** Páciens hozzájárulás — egészségügyi és genetikai adatok kutatási / algoritmus-validációs célú, álnevesített kezeléséhez.

1. **Cél:** a farmakogenetikai vizsgálat adatkezelője \[Partnerlabor/Kórház\] együttműködik a \[gyártó, A9\] fejlesztővel a gyógyszer–gén párosító algoritmusok pontosságának értékelésére (shadow / HITL). Az algoritmus kimenete **nem** része a kezelésnek.
2. **Álnevesítés:** név, TAJ, cím, pontos születési dátum nem kerül a fejlesztőhöz. Kód; a kulcsot kizárólag az adatkezelő őrzi.
3. **Jogalap és idő:** GDPR 6(1)(a), 9(2)(a) (vagy a counsel által választott 9(2) pont); tárolás a protokoll szerint, max \[X\] év.
4. **Jogok:** tájékoztatás, törlés, korlátozás, hozzájárulás visszavonása. Visszavonás után a kód alapján a shadow rekord törlendő (FR-110 kaszkád a HITL store-ra is).
5. **Nyilatkozat:** a tájékoztatást megértettem; önként hozzájárulok az álnevesített diplotípus és gyógyszerlista kutatási/validációs felhasználásához.

Aláírás: páciens / törvényes képviselő; dátum; adatfelvevő.

---

## E.7 REG-090 / OQ-15 — klinikai vizsgálat vs „csak analitika”

A shadow motor **ugyanaz** a L4-live, amely F3-on MDSW lesz. Valós ellátási eseményen futtatni a jövőbeli eszköz klinikai hasznának bizonyítására:

- lehet **klinikai értékelés** adatgyűjtése, vagy
- lehet **klinikai vizsgálat** (MDR Art. 62+), etikai engedéllyel és hatósági bejelentéssel,

attól függően, hogy a szoftver „használatba vétele” / beavatkozás-e. **OQ-15:** külső RA/counsel + a partner intézmény kutatási igazgatósága **a első shadow-csatlakozás előtt**. Ez a dokumentum nem dönt.

In-house F2 (A.7) más jogi doboz, mint a gyártó felhőjében futó shadow.

---

## E.8 Tesztelendő invariánsok (FR-470)

- [ ] Given shadow motor kimenet, When L6-report generálódik, Then a Report JSON/PDF/FHIR **nem** tartalmaz `functional_phenotype`, `shadow_recommendation`, `dose_mg`.
- [ ] Given `clinician` szerep, When a klinikai API-t hívja, Then 404/403 a `/shadow/**` és `/hitl/**` útvonalakra.
- [ ] CI: call-graph a report-renderer és a cds-hooks modul **nem** függ a shadow-writer kimeneti táblájától (csak fordítva tilos; a shadow olvashatja a diplotípust).
- [ ] Feature flag `LIVE_CDS=true` csak signed release-ben, REG-010 F2/F3 intended purpose mellett; F1+ buildben a flag compile-time false.
