# Term sheet — F1+ laboratóriumi L3 / outside-call (OQ-03)

| | |
| --- | --- |
| **Iktató** | PCE-OUT-OQ-03 / v1.2 |
| **Dátum** | 2026-08-12 |
| **Státusz** | TERVEZET — tárgyalási alap; **nem** szerződés, **nem** REG-020 aláírás |
| **Feladó** | `[Gyártó neve]` (A9; név a fejlécben töltendő) |
| **Címzett** | `[Partnerlaboratórium neve]` — üzleti vezetés / orvosigazgató |
| **Tárgy** | Term sheet — F1+ white-label lelet, outside-call, szakorvosi aláírás |
| **OQ** | OQ-03 — **ELŐTERJESZTVE**; labor név / ár / aláírt szerződés **nyitott** |

Tisztelt Partner!

Ez a lap a v1.2 spec **REG-020** határvonalának kereskedelmi vázlata. A szögletes zárójelek a tárgyalásé. Labornevet, Ft-összeget és SLA-órát a gyártó **nem** talál ki.

---

## 0. Mi *nem* ez a szolgáltatás (javítás a korábbi vázlathoz)

| Félreértés | Spec |
| --- | --- |
| Az L3 csak akkor kell, ha a szoftver „NG-01 riasztást” ad, és csak ezekért jár díj | **NG-01** = *non-goal*: a PCE **nem** hív genotípust nyers labor-adatból (FASTQ/IDAT). Nem riasztáskód. |
| A szoftver automatikusan „validált leletet” ad ki; a labororvos csak a kivételeket nézi | F1+ default: a labor **már** meghívta a diplotípust (**outside-call**, FR-240). A PCE formáz + statikus guideline-szöveg. **Minden** F1+ leletet a labor szakorvosa ír alá (FR-490). |
| PharmCAT / VCF-matcher az F1+ default | Matcher F1+ klinikai buildben **ki**. VCF-útvonal támogatott, de nem a default. |
| Darabár csak a manuális felülbírálatra | Spec árazási kötés: labor white-label = **fix havidíj + volumensáv**, nem per-patient CDS. A `[Y]` a tárgyalásé. |

A „kivétel” (INDETERMINATE callability, outside-call vs VCF ütközés `W-CALL-010`) **emberi döntés** — ez nem NG-01, és nem az egyetlen aláírandó eset.

---

## 1. A szolgáltatás tárgya

A **Partnerlaboratórium**:

1. Akkreditált / engedélyezett körében **megállapítja** a farmakogenetikai diplotípust / fenotípust (L3). A PCE ezt **outside-call** bemenetként fogadja (`gene`, `diplotype`, `calling_lab`, `signing_physician`, `method`, `call_date`, opcionálisan `phenotype`, `callability`).
2. Kijelölt szakorvosai **minden** F1+ white-label PDF/FHIR kimenetet ellenőriznek és **elektronikusan aláírnak**, mielőtt a lelet a megrendelő / HIS felé kimegy.
3. A PCE a partner arculatával készíti a leletet; a kolofonban a PCE **technológiai szállító**, nem aláíró (FR-500).

A **Gyártó**:

1. Szállítja az F1+ szoftvert (L0–L2 + L4-static + L6-report) a v1.2 intended purpose szerint.
2. **Nem** végez saját genotípus-hívást nyers adatból (NG-01).
3. **Nem** ad ki orvosi aláírás nélküli „validált” leletet.

A későbbi F1s shadow / F2 CDSS **nem** része ennek a term sheetnek, hacsak külön megállapodás nem születik.

---

## 2. Felelősségi körök (REG-020 mag)

| Tétel | Partnerlabor | Gyártó |
| --- | --- | --- |
| Diplotípus / fenotípus-hívás, módszer, callability | **Igen** — aláíró orvos | Nem |
| Statikus, verziózott CPIC/DPWG/FDA szövegkivonat helyessége a config szerint | A lelet **tartalmáért** az aláíró orvos a lelet kibocsátásakor | A szoftver a configot hiba nélkül rendereli; guideline-frissítés change-control (FR-370 / FR-510) |
| Klinikai / jogi felelősség a **aláírt lelet** tartalmáért | Az aláíró labororvos / a labor mint szolgáltató | Technológiai szállító; termékfelelősség a szoftverhibáért a hatályos jog szerint **nem** zárható ki disclaimerrel (A.1.1) |
| 2008/XXI. tanácsadás, beleegyezés, 12. § (1) engedély | A vizsgálatot végző szolgáltató | FR-100 kapu a szoftverben; nem helyettesíti a labor kötelezettségét |
| MDSW minősítés (OQ-05) | A labor a saját szolgáltatására | A szoftver gyártói pozíciója counsel előtt; ha OQ-05 NEM → IIa, a szerződés újratárgyalandó |

---

## 3. SLA (rendelkezésre állás és átfutási idő)

A Partnerlaboratórium vállalja, hogy az aláírásra kész F1+ kimenet (PDF/FHIR) rendelkezésre állásától számított **`[X]` órán** belül a kijelölt szakorvos áttekinti a diplotípus-adatokat és a renderelt leletet, majd elektronikusan aláírja **vagy** indoklással visszautasítja (`INDETERMINATE` / `W-CALL-010` / szakmai ok).

| Mutató | Cél (tárgyalandó) |
| --- | --- |
| Aláírási átfutás p95 | `[X]` óra a `report_ready` eseménytől |
| Elérhetőség (munkanap / ügyelet) | `[munkanap 8–16 / egyéb]` |
| Ütköző hívás (`W-CALL-010`) | Nincs automatikus választás; emberi döntés ugyanabban az SLA-ban vagy `[X2]` óra |
| Gyártói pipeline p95 (outside-call → aláírásra kész) | Spec G1: **&lt; 10 perc** (szoftver, nem orvosi aláírás) |

---

## 4. Díjazás (kereskedelmi váz)

A spec kötése: **fix havidíj + volumensáv**, nem per-patient CDSS-licenc. A tárgyalás ettől eltérhet; a placeholder-ek kötelezően kitöltendők aláírás előtt.

**Gyártói default (nem pecsét):** a **kórház/klinika** fizeti a SKU-P-t a gyártónak. A labor **nem** viszonteladója a kórházi licencnek. Ha a labor *saját* white-label tenancyt kér (saját megrendelők, saját pecsét), a labor a gyártónak `[Y1]`/`[Y2]` (mátrix: `[Yl]`). Ha a labor csak a klinika tenancyjéhez csatlakozik (REG-020), szoftverdíj **nem** jár a labor felé — a vizsgálat díját a labor a klinikának számlázza.

| Tétel | Összeg | Megjegyzés |
| --- | --- | --- |
| Havidíj (platform / white-label tenancy) | `[Y1]` Ft + ÁFA / hó | Csak ha a labor *saját* tenancyt kér. Minimum volumen: `[N]` lelet/hó |
| Volumensáv (sávonként) | `[Y2]` Ft + ÁFA / aláírt lelet **vagy** sávos csomag | Csak **aláírt** F1+ lelet |
| Opcionális: INDETERMINATE / ütközés plusz munka | `[Y3]` Ft + ÁFA / eset | Nem „NG-01 díj” |
| F1s / HITL (ha egyáltalán) | Külön kutatási megállapodás | Nem a felíró licenc |
| Csatlakozó a klinika SKU-P-jéhez | 0 szoftverdíj a labor felé | REG-020; a klinika fizeti a `[Yp]`-t |

Automatikus, **aláírás nélküli** leletkimenet **nincs** — ezért „az automatikus lelet után díj nem jár” modell **nem** alkalmazható.

Ettől a defaulttól a felek eltérhetnek (pl. a gyártó fizet a labornak mint alvállalkozónak). A számlázási irány a REG-020-ban rögzítendő. **Viszonteladás** (a labor SKU-P-t ad el kórháznak) **nem** default és nem cél.

---

## 5. Függőségek és kilépés

- **OQ-05:** ha a counsel szerint az F1+ MDSW, a term sheet nem helyettesíti a CE-t; a felek 30 napon belül újratárgyalnak vagy felmondanak.
- White-label arculat, pecsétszám, FHIR `DocumentReference` aláírómező: a labor adja.
- Titoktartás / adatfeldolgozás: külön DPA; genetikai adat a 2008/XXI. szerint.
- Ez a lap **nem** kizárólagos; mindkét fél a végleges szerződésig szabadon tárgyal.

---

## 6. Aláírás (szándék, nem szerződés)

A lenti aláírás **tárgyalási szándék** / LOI-szint, hacsak a felek ki nem töltik: „ez REG-020 szerződés”.

- [ ] Tárgyalási szándék (LOI) — REG-020 szerződés `[dátum]`-ig
- [ ] Ez a lap a REG-020 szerződésnek minősül (csak ha mindkét jogi képviselő kifejezetten bejelöli)

| | Partnerlabor | Gyártó |
| --- | --- | --- |
| Név | .................................... | .................................... |
| Pozíció | .................................... | .................................... |
| Dátum | .................................... | .................................... |
| Aláírás | .................................... | .................................... |

**Kitöltendő a küldés előtt:** `[Partnerlaboratórium neve]`, `[X]`, `[Y1]`/`[Y2]`, számlázási irány.

**Mellékletek:** PCE-SPEC-v1.2 (FR-240, FR-490, FR-500, REG-020, NG-01, §11 árazási kötés); A.1; F.5.

*OQ-03 a labor nevének, az árnak és az aláírt REG-020-nak a rögzítéséig nyitott. Itt labornevet nem találunk ki.*
