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

Az F1+ white-label statikus lelet a labor manuális szövegezését váltja ki — ez a fizető termék. A kórházi IT-nek az F1+ „okos lelet, nem élő riasztás” könnyebb belépő, mint az interruptive CDSS. Az F1s az **ugyanazon** integrációs csövön (Subscription → gateway) építi a későbbi F2 kapcsolót; a `pce_cds` cső a dobozban van. A kapcsoló CE / in-house nélkül **nem** billenhet klinikai UI-ra (FR-470, `LIVE_CDS=false`).

---

## E.2 Adatút

```
[ HIS / LIS : recept lezárás | lelet aláírás ]
        │
        ▼  FHIR Subscription / webhook (HTTPS)
[ Anonimizáló / álnevesítő Gateway ]
        │  kötelezően a kórház/labor hálózati zónájában (FR-460)
        ├─► Direct identifiers törölve vagy kód az intézmény KMS-ében
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
| `Observation` PGx | kód + **coarsened** value (FR-461); callability | nyers diplotípus a DPIA szerint |
| `MedicationRequest` | ATC **5. szint, 7 karakter** (hatóanyag-kód); **nincs** doseQuantity; `authoredOn` → negyedév | DPO durvíthat ATC4/ATC3-ra; akkor párosítás szünetel |
| `Practitioner`, org, ward, username | Törölve | Törölve vagy intézményi kód |
| Meta `source`, `lastUpdated` belső ID-k | Tisztítva | Tisztítva |

Irreverzibilis anonimizálás: nincs olyan kulcs, amellyel a gyártó a gént a személyhez köthetné. Ha van kulcs az intézménynél → **álnevesítés**, GDPR személyes adat, FR-115 kötelező.

A 2008/XXI. 26. § szerinti 30 éves genetikai nyilvántartás az **intézmény / biobank** kötelezettsége. A gyártó shadow store-ja: kutatási cél, FR-115 szerinti törlés; nem helyettesíti a 30 éves intézményi naplót. Megőrzés: **A15** (protokoll), nem A10.

### E.3.1 FR-461 — aggregáció az anonim úton (OQ-16 csomag)

A DPO/DPIA **előtt** ez a default. Ha a DPIA szerint így is személyes adat → A12 hamis, álnevesített út + FR-115.

WHO ATC szintek `[V]` (S032): 1. anatómiai (1 betű) → 2. terápiás (3 karakter, pl. N06) → 3. farmakológiai (4 karakter, pl. N06A) → 4. kémiai alcsoport (5 karakter, pl. N06AB) → 5. hatóanyag (7 karakter, pl. N06AB10).

| Kontroll | Default (A14) | Ha a DPO szigorít | Ár a G3 metrikának |
| --- | --- | --- | --- |
| ATC | **5. szint, 7 karakter** (hatóanyag) | 4. vagy 3. szint | FR-410-LIVE nem különbözteti a paroxetint más SSRI-től, ha csak N06AB / N06A megy ki (R-020) |
| Diplotípus | nyers, ha a cella ≥ k és freq ≥ küszöb | csak fenotípus-osztály / drop | ritka allél recall csökken |
| Idő | naptári negyedév | év | longitudinális összekötés nehezebb (álnevesített úton kell) |
| k | ≥ 5 intézményi cella | nagyobb k | több drop (`E-SHADOW-003`) |

**Ritka diplotípus:** küszöb 0,5% `[ASSUMPTION]` A14; a gyakoriság-tábla verziózott config (gnomAD / PharmGKB — a DPIA megnevezi). Intézményi cella: (fenotípus-osztály × ATC-szint × negyedév) count a gateway **helyi** statisztikáján; a nyers count **nem** megy a PCE-hez.

**Drop vs coarsen:** a gateway configja. Drop: a HIS fail-open, a HITL nem kap sort. Coarsen: `diplotype_granularity = CLASS`.

---

## E.4 HITL felület (FR-450)

```
[ Belépés: hitl_reviewer, külön app ]
        │
        ▼
[ Esetlista — opák ID, pl. A87F3 ]
        │  látszik: gén + (coarsened) diplotípus/osztály + hatóanyag-kód (7 karakter) + negyedév
        │  nem látszik: név, kor, intézmény, orvos
        ▼
[ FR-450-BLIND 1: reviewer saját strukturált döntése, motor tipp rejtve ]
        │
        ▼
[ FR-450-BLIND 2: motor kategória felvillan → AGREE / DISAGREE / INSUFFICIENT_DATA ]
        │
        ▼
[ reason_code (+ opcionális szöveg, PII-scan) → HITL store / clinical evaluation input ]
```

- Szerep: `hitl_reviewer` ≠ `clinician` a felíró tenancyben. Ugyanaz a természetes személy lehet mindkettő, **más login / más app**.
- Nem a vizit alatt; batch (pl. havi) vagy bizottsági ülés → A15 megőrzés.
- G3 metrika: vak döntés vs motor (ha BLIND be), különben AGREE-ráta. Nem a felíró override-rátája (az F2 FR-600).

### E.4.1 Vak mód és OQ-15

Szekvenciális, **reviewer-vak** eljárás. **Nem** kettős vak (double-blind): a motor kimenete a rendszerben megvan; a reviewer az 1. lépésben nem látja.

A vak HITL **támogató bizonyíték** arra, hogy a reviewer nem a napi ellátásban, nem a gép élő tanácsára gyógyít. **Nem** Art. 62-mentesség.

Az érv, amit a RA/intézmény OQ-15-höz vihet (és a counsel elvethet): az L4-live kimenet nem befolyásolja az index-kezelést, mert a kezelőorvos nem látja, és a HITL utólagos. Az MDR Art. 62 hatóköre ettől még nyitott — REG-090 az első csatlakozás **előtt**.

---

## E.5 Két GDPR-út (A12)

| Út | Mikor | Jogalap (váz) | Beteg hozzájárulás a shadowhoz |
| --- | --- | --- | --- |
| **Anonim** (default) | Nincs longitudinális követés | Anonim adat ≠ GDPR személyes adat, *ha* az anonimizálás tényleges | Nem (a klinikai 2008/XXI. hozzájárulás ettől még kell a vizsgálathoz) |
| **Álnevesített** | 6 hónapos kimenet összekötése kell | GDPR 6(1)(a) + 9(2)(a) *vagy* más 9(2) jogalap a counsel szerint | **FR-115** igen; kulcs az adatkezelőnél |

Adatkezelő: labor/kórház. Gyártó: adatfeldolgozó a DPA szerint, hacsak a counsel mást nem mond a saját kutatási adatbázisra. DPIA: REG-050 kiterjesztése a shadowra **élesítés előtt**.

„Tiszta anonimizálás után szabadon tanítjuk a modellt” — csak akkor, ha az anonimizálás **visszafordíthatatlan**. Genetikai + ritka gyógyszerkombináció re-identifikálhat; FR-461 + DPIA. `[ASSUMPTION]` A13/A14.

**A10 ≠ shadow TTL.** Lásd spec §0.1.

### E.5.1 Visszavonás vs megőrzés

| Esemény | Klinikai tenancy | Álnevesített HITL | Már anonim HITL (nincs kulcs) |
| --- | --- | --- | --- |
| Protokoll fut, hozzájárulás él | 26. § nyilvántartás | A15, FR-115 | A15, ha a DPIA szerint nem személyes adat |
| Klinikai vagy kutatási hozzájárulás **visszavonva** | 72 h megsemmisítés (A10, FR-110) | 72 h: törlés **vagy** irreverzibilis anonimizálás | Klinikai tenancy törlése; HITL-sor a DPIA szerint maradhat (nincs join) |

A15 feltétel: OQ-16 anonim út *vagy* érvényes FR-115. Álnevesített, visszavont sort A15 **nem** tart meg.

---

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

A shadow motor **ugyanaz** az L4-live, amely F3-on MDSW lesz. Valós ellátási eseményen futtatni a jövőbeli eszköz klinikai hasznának bizonyítására:

- lehet **klinikai értékelés** adatgyűjtése, vagy
- lehet **klinikai vizsgálat** (MDR Art. 62+), etikai engedéllyel és hatósági bejelentéssel,

attól függően, hogy a szoftver „használatba vétele” / beavatkozás-e. **OQ-15:** külső RA/counsel + a partner intézmény kutatási igazgatósága **az első shadow-csatlakozás előtt**. Ez a dokumentum nem dönt.

In-house F2 (A.7) más jogi doboz, mint a gyártó felhőjében futó shadow.

**SOTA az F1s / clinical evaluation dossziéhoz:** PREPARE (S008), PGx-Passport (S009), CPIC (S030), MDCG/MDR. A CureMD labor→ICD preprint (S028, L5, n=593 055, Top-5 acc. 83,10%) **nem** állami/hatósági SOTA és **nem** G3-küszöb. Szabad *irodalmi* mellékletként: [S028-note](Sources/S028-curemd-hybrid-cdss-note.md). VC-13.

---

## E.8 Tesztelendő invariánsok (FR-470)

- [ ] Given shadow motor kimenet, When L6-report generálódik, Then a Report JSON/PDF/FHIR **nem** tartalmaz `functional_phenotype`, `shadow_recommendation`, `dose_mg`.
- [ ] Given `clinician` szerep, When a klinikai API-t hívja, Then 404/403 a `/shadow/**` és `/hitl/**` útvonalakra.
- [ ] CI: a report-renderer **nem** függ a shadow-writer kimeneti táblájától, és **nem** importálja a `pce_cds`-t. A `pce_clinical` processzuson a CDS 404 (`E-ISO-002`). A `pce_cds` a shadow *motort* hívhatja, ha `LIVE_CDS=true`; a HITL store-ból **nem** ír a Reportba. Fordítva megengedett: a shadow olvashatja a klinikai diplotípust.
- [ ] Feature flag `LIVE_CDS=true` csak signed release-ben, REG-010 F2/F3 intended purpose mellett; a repo compile-time **false**. A cső (`pce_cds`) ettől még a dobozban van.
- [ ] Anonim ingest: nap-szintű `authoredOn` / TAJ / dózis → elutasítva. 7 karakteres hatóanyag-kód **elfogadott**, hacsak a DPO nem durvít.
- [ ] F1+ renderer: `MedicationEntry` nincs a call-graphben; tiltott token → `E-EDU-001`.
