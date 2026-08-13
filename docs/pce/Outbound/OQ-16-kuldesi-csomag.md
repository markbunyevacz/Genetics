# OQ-16 — kiküldési csomag (első kimenő irat)

| | |
| --- | --- |
| **Iktató** | PCE-OUT-OQ-16-SEND / v1.2 |
| **Kanonikus kérdőív** | [OQ-16-dpo-dpia-kerdoiv.md](OQ-16-dpo-dpia-kerdoiv.md) — **ne írd át** |
| **Státusz** | Küldhető, ha a lenti **G1 + C2** ki van töltve. **Nem** DPIA, **nem** pecsét. |
| **Lánc** | Ez az **első** telephelyi / adatvédelmi irat. OQ-15 **nem** megy ki a válasz előtt. |

A kérdőív törzse zárolt. Ez a fájl a **boríték**: kitöltendő változók, tárgysor, mellékletlista. Gyártó- vagy labornevet a repo **nem** helyettesít be (A9; D-03). Az I-01 „Agentize Kft.” **tiltott**.

---

## 0. Mit *ne* helyettesíts

| Változó | OQ-16 törzsben? | Teendő |
| --- | --- | --- |
| `[Gyártó neve]` | Igen — **Feladó** | A **küldő** írja a borítékra és a kérdőív fejlécére küldéskor. Itt üresen marad. |
| `[Partnerlaboratórium neve]` | **Nincs.** Az OQ-03 mezője. | **Ne** írd az OQ-16-ba. A DPO-nak nem labor-term sheet kell. |
| `[X]`, `[Y1]`/`[Y2]`, Ft, SLA | Nincs | OQ-03. |
| DPO aláírás / F.6 | Üresen | A **címzett** tölti. |

OQ-16 D2: adatkezelő = intézmény/labor *szerep*, nem cégnév. Ha a telephely laborja még nincs megnevezve, a kérdőív akkor is kiküldhető a **DPO szervezetére**.

---

## 1. Küldés előtti kitöltőlap (kötelező)

A küldő tölti. Üresen **nem** megy ki.

| ID | Mező | Példa *formátum* (nem érték) | 16-A termék-DPO | 16-B telephely-DPO |
| --- | --- | --- | --- | --- |
| **G1** | Gyártó jogi neve | cégjegyzék szerinti név | kötelező | kötelező |
| **G2** | Gyártó kapcsolattartó + e-mail | természetes személy | kötelező | kötelező |
| **C2** | Címzett szervezet | DPO munkáltatója | gyártó **vagy** megbízott DPO-cég | **intézmény** (kórház/klinika) |
| **C1** | Címzett DPO neve, ha ismert | — | ha van | ha van; különben „DPO / DPIA munkacsoport” |
| **C2b** | Intézmény (HIS-adatkezelő), ha ≠ C2 | — | `nincs HIS — termék-DPIA` | = C2, vagy a labor, ha ő az adatkezelő |
| **H1** | Válaszhatáridő | naptári dátum | ajánlott | ajánlott |

**16-A** elhagyhatja a céget **most**, HIS-név nélkül: termék-szintű vélemény az A14/FR-461 kontrollokról. **Nem** nyit éles HIS-t.

**16-B** nyitja a HIS-kaput (OQ-15-tel együtt). C2 nélkül **tilos** 16-B-t küldeni.

A lánc „első irat” = 16-A *vagy* 16-B, attól függően, van-e nevesített intézmény. Hamis kórháznév **nincs**.

---

## 2. Fejléc a kérdőívre (küldéskor, másolat)

A gitben lévő `OQ-16-dpo-dpia-kerdoiv.md` Feladó-sora marad `[Gyártó neve]`. A **kimenő másolaton**:

```
Iktató:     PCE-OUT-OQ-16 / v1.2
Dátum:      [küldés napja]
Feladó:     [G1]
Címzett:    [C1], [C2]
Intézmény:  [C2b]     ← 16-A: „nincs HIS — termék-DPIA”
Tárgy:      F1s (Shadow Mode) gateway anonimizálási kontrollok — OQ-16
OQ:         ELŐTERJESZTVE; ez az irat nem zárja
```

Partnerlabor **nincs** ebben a fejlécben.

---

## 3. Levél (másolható)

**Tárgy:** PCE F1s / OQ-16 — gateway anonimitás (ATC4, k ≥ 5, ritka drop) — döntési kérés

```
Tisztelt [C1 / DPO / DPIA munkacsoport]!

Cégünk, a [G1], a Precision Clinical Engine (PCE) F1s (Shadow Mode)
adatútjához kér állásfoglalást. Ez az OQ-16 kérdőív: DPIA-input,
nem DPIA, nem hatósági határozat.

Kérjük A1–D4 minden sorának kitöltését (IGEN / NEM / FELTÉTELLEL).

Gyártói kérés: a gateway utáni adatfolyam legyen jogilag anonim
(ATC max 4. szint, idő = naptári negyedév, k ≥ 5, ritka diplotípus
drop), A14 küszöb monitorozásával akkor is, ha ez rontja a G3-at.

Két hozzájárulás nem keverendő:
- FR-100 (2008/XXI. 6. § (2) / 8. §) a mintavételnél mindig kell.
- FR-115 csak akkor kötelező, ha A1 = NEM (álnevesített út).

A k ≥ 5 és a 0,5% A14 feltevés, nem ClinLabomics-tétel.
Kérjük, a választ [H1]-ig juttassák el [G2] részére.

Tisztelettel,
[G2]
[G1]
```

**Tilos a levélben:** „nem MDSW”; PREPARE/YouScript mint pecsét; „a shadow anonim, ezért nincs betegi beleegyezés”; kitalált kórház/labor; élő CDS / vizit-UI.

---

## 4. Mellékletek (egy csomag)

Sorrend a csatolmányban:

1. Ez a boríték (kitöltött G1–C2b) — belső; a DPO-nak opcionális
2. [OQ-16-dpo-dpia-kerdoiv.md](OQ-16-dpo-dpia-kerdoiv.md) — **kötelező** (fejléc: G1)
3. [PCE-SPEC-v1.2.md](../PCE-SPEC-v1.2.md) — FR-115, FR-460, FR-461, §0.1 A10/A15
4. [E melléklet](../E-shadow-hitl.md) — E.3, E.3.1, E.5, E.5.1 (E.6 csak ha A1 várhatóan NEM)
5. [F.3](../F-decision-package.md) — gyártói kérés, nem válasz
6. WHO ATC szintek: https://www.whocc.no/atc/structure_and_principles/ (S032)

**Ne csatold:** ClinLabomics; CureMD/S028; Sales ármátrix; OQ-03 term sheet; OQ-15 (az a következő irat).

---

## 5. Küldési checklist

- [ ] G1 kitöltve a kimenő másolaton (nem Agentize, nem kitalált Kft.)
- [ ] C2 kitöltve; 16-B-nél intézményi név **valódi**
- [ ] Partnerlabor **nincs** az OQ-16-on
- [ ] A1–D4 üresen a címzettnek (ne pipáld ki helyette)
- [ ] IV. aláíró-sor üres
- [ ] Melléklet 2–6 csatolva
- [ ] Levélben nincs „nem MDSW” / PREPARE-RWE
- [ ] F.6 OQ-16 sora a gyártónál üresen marad a válaszig
- [ ] OQ-15 **hold** a pecsétig

---

## 6. Válasz után

| A1 | Következő |
| --- | --- |
| IGEN / FELTÉTELLEL (A14 monitor) | OQ-15 kiküldhető a **ugyanazon** intézménynek. HIS: 16 **és** 15 pecsét. |
| NEM | Gateway megmarad; `PSEUDO` + FR-115. OQ-15-ön jelezni: FR-115 kötelező. FR-100 marad. |

16-A pecsét **nem** helyettesíti a 16-B-t: éles HIS-hez a *telepítő* intézmény DPO-ja kell.
