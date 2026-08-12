# FR-461 — Gateway csonkolási ticketek (kódolási előkészítés)

| | |
| --- | --- |
| **Forrás** | PCE-SPEC-v1.2 FR-460 / FR-461; E.3 / E.3.1; B.2.2 / B.3.5 / B.5; OQ-16 I.1–I.4 |
| **Prioritás** | Compliance P0 az **F1s anonim** úton |
| **Adat** | **SYN** fixture. Valódi beteg / éles HIS **tilos** OQ-16 + OQ-15 pecsétig (§10.2) |
| **Nem zárja** | OQ-16. A14 küszöbök `[ASSUMPTION]`; a DPO felülírhatja. ClinLabomics **nem** k-bizonyíték. |

A gateway az **intézményi zónában** fut (FR-460). A PCE felhő defense-in-depth: ha a csonkolás elmarad, ingest elutasít, a HIS **fail-open** (E.2).

**Cella (implementálandó, E.3.1 / OQ-16 I.4):** `(fenotípus-osztály × ATC-szint × naptári negyedév)` a gateway **helyi** számlálóján. A nyers count **nem** megy a PCE-hez. FR-461 „gördülő ablak” = ez a negyedéves helyi ablak; **ne** találj ki 90 napos csúszó ablakot.

**Osztály-enum coarsenkor (FR-461):** `REDUCED` | `INCREASED` | `UNCERTAIN`. `diplotype_granularity = CLASS` (E.3.1).

WHO ATC `[V]` S032: ATC3 = 4 karakter (`N06A`); ATC4 = 5 (`N06AB`); ATC5 = 7 (`N06AB10`). Anonim default: max ATC4; ATC5 **tilos**.

---

## Epic 0 — FR-460 előfeltétel (TC-GW-001..008)

Csonkolás FR-461 nélkül nem szállítható: előbb le kell szedni a közvetlen azonosítókat (E.3 tábla).

| ID | Cím | Given / When / Then | Hibakód |
| --- | --- | --- | --- |
| **PCE-GW-460-01** | Gateway intézményi zóna + service-account | Given HIS esemény, When továbbítás, Then csak a gateway hív `POST /v1/shadow/events`; más caller → `E-SHADOW-002` | `E-SHADOW-002` |
| **PCE-GW-460-02** | Név / telecom / cím / TAJ törlése | Given `Patient.name` vagy `identifier` (TAJ), When ANON kimenet, Then mező hiányzik. Ha a PCE mégis megkapja → `E-SHADOW-001`, nincs HITL sor | `E-SHADOW-001` |
| **PCE-GW-460-03** | `Patient.id` ANON | Given ANON, When kimenet, Then új, nem visszavezethető UUID; **nincs** re-ID kulcs a gyártónál | `E-SHADOW-001` ha join-key szivárog |
| **PCE-GW-460-04** | Practitioner / osztály / username törlése | Given Practitioner vagy ward, When ANON kimenet, Then törölve | `E-SHADOW-001` |
| **PCE-GW-460-05** | Meta `source` / belső ID tisztítás | Given FHIR meta belső azonosítók, When kimenet, Then tisztítva (E.3) | `E-SHADOW-001` |
| **PCE-GW-460-06** | `birthDate` gatewayen max év | Given `Patient.birthDate`, When ANON, Then legfeljebb év; HITL kártyán születési év **nincs** (FR-450) | — |
| **PCE-GW-460-07** | Aszinkron 202, HIS fail-open | Given gateway vagy PCE hiba, When HIS receptlezárás, Then a HIS **nem** blokkol; 202 Accepted a shadow ingestnél (B.3.5) | — |
| **PCE-GW-460-08** | `GatewayEvent` séma | Given továbbított (vagy elnyomott) esemény, When persist, Then: `id`, `received_at`, `org_id`, `mode` (`ANON`\|`PSEUDO`), `payload_hash`, `atc_level`, `time_grain`, `diplotype_granularity`, `suppressed?` (B.2.2) | — |

PSEUDO út + FR-115: **ne** kódold élesre, amíg OQ-16 = NEM. SYN-en a `mode` flag létezzen; `ResearchConsent` hiány → `E-CONSENT-006` (B.3.5).

---

## Epic 1 — FR-461 transzformáció (TC-GW-010..020)

Minden ticket ANON `mode`. Config default: A14. Nincs manuális k-override ANON úton (FR-461 utolsó AC).

### PCE-GW-461-01 — ATC csonkolás (default ATC4)

| | |
| --- | --- |
| **AC** | FR-461 ATC; E.3.1; OQ-16 I.3 |
| **TC** | TC-GW-010, TC-GW-011 |

- Given `MedicationRequest` ATC5 (`N06AB10`), When ANON gateway, Then kimenet max `N06AB` (5 karakter). `atc_level = 4`.
- Given config `ATC3`, When ugyanaz, Then `N06A` (4 karakter). `atc_level = 3`.
- Given ATC5 a PCE ingesten, When ANON, Then `E-SHADOW-001`, nincs HITL sor.
- Tilos: hatóanyag-szint (7 karakter) az ANON payloadban.

### PCE-GW-461-02 — Idő generalizáció (naptári negyedév)

| | |
| --- | --- |
| **AC** | FR-461 idő; OQ-16 I.2 |
| **TC** | TC-GW-012, TC-GW-013 |

- Given `MedicationRequest.authoredOn` nap/óra/perc, When ANON, Then `2026-Q3` formátumú naptári negyedév. `time_grain = QUARTER`. Nincs nap, óra, perc.
- Given pontos `authoredOn` a PCE ingesten, When ANON, Then `E-SHADOW-001`.
- DPO-szigorítás (év): config `time_grain = YEAR`; default **negyedév**.

### PCE-GW-461-03 — `doseQuantity` tiltás

| | |
| --- | --- |
| **AC** | FR-461 adagolás; E.3 `MedicationRequest`; OQ-16 I.1 |
| **TC** | TC-GW-014 |

- Given `doseQuantity` / `dose_mg`, When ANON kimenet, Then a mező **nincs**. v1 shadowban `dose_mg` tilos (B.2.2).
- Given adagolás a PCE ingesten, When ANON, Then `E-SHADOW-001`.

### PCE-GW-461-04 — k-cella: coarsen

| | |
| --- | --- |
| **AC** | FR-461 ritka diplotípus (a); E.3.1 drop vs coarsen |
| **TC** | TC-GW-015 |

- Given intézményi cella elemszáma **&lt; k** (default k = 5), When config `on_small_cell = COARSEN`, Then diplotípus helyett fenotípus-osztály (`REDUCED`\|`INCREASED`\|`UNCERTAIN`). `diplotype_granularity = CLASS`. `suppressed = false`.
- A helyi count **nem** szerepel a PCE payloadban.

### PCE-GW-461-05 — k-cella: drop (`E-SHADOW-003`)

| | |
| --- | --- |
| **AC** | FR-461 ritka diplotípus (b) |
| **TC** | TC-GW-016 |

- Given cella &lt; k, When config `on_small_cell = DROP`, Then **nincs** HITL sor. Gateway: aggregált számláló. PCE: ha a nyers rekord mégis megérkezik → `E-SHADOW-003` (HTTP 202, nincs store-írás).
- HIS fail-open.

### PCE-GW-461-06 — Ritka diplotípus gyakoriság (A14 0,5%)

| | |
| --- | --- |
| **AC** | FR-461 freq &lt; küszöb; OQ-16 I.4 |
| **TC** | TC-GW-017 |

- Given verziózott gyakoriság-config (SYN tábla; gnomAD/PharmGKB **nevét a DPIA adja**, itt ne hardkódold primer forrásnak), When populációs freq &lt; **0,5%**, Then coarsen **vagy** drop a config szerint.
- A 0,5% `[ASSUMPTION]` A14. Config-kulcs: `rare_diplotype_threshold`. DPO felülírhatja; kód ne égesse be konstansnak a hívási úton.

### PCE-GW-461-07 — Legritkább osztály: mindig drop

| | |
| --- | --- |
| **AC** | FR-461 A14 monitor utolsó mondat; F.3; OQ-16 B4 |
| **TC** | TC-GW-018 |

- Given a gyakoriság-tábla **legritkább** diplotípus-osztálya, When ANON, Then **drop** (`E-SHADOW-003`), akkor is, ha a G3 recall csökken (R-020).
- Nincs `on_small_cell = COARSEN` kivétel erre az osztályra. Nincs manuális override.

### PCE-GW-461-08 — Nincs k-küszöb override ANON úton

| | |
| --- | --- |
| **AC** | FR-461 „Nincs manuális override a k-küszögre F1s anonim úton” |
| **TC** | TC-GW-019 |

- Given `mode = ANON`, When admin/API `k`-t csökkentene 5 alá, Then elutasítva. Növelés (DPO-szigorítás) config-release-szel megengedett, runtime „kapcsoló” nem.
- `mode = PSEUDO`: FR-461 enyhítés csak DPIA + FR-115 után (OQ-16 NEM ág). SYN-en tesztelhető; élesben pecsétig zárva.

### PCE-GW-461-09 — PCE ingest defense-in-depth

| | |
| --- | --- |
| **AC** | FR-460 utolsó AC; B.3.5; B.5 |
| **TC** | TC-GW-011, TC-GW-013, TC-GW-016 |

A PCE **nem bízik** a gatewayben.

| Bemenet | Kód | HITL |
| --- | --- | --- |
| `Patient.name` / TAJ / identifier | `E-SHADOW-001` (400) | nem |
| ATC5 (7 karakter) | `E-SHADOW-001` | nem |
| Nap-szintű `authoredOn` | `E-SHADOW-001` | nem |
| Nyers ritka diplotípus / k-alatti sejt | `E-SHADOW-003` (202) | nem; számláló |
| Nem gateway service-account | `E-SHADOW-002` (403) | nem |

### PCE-GW-461-10 — A14 monitor (DPO, negyedévente)

| | |
| --- | --- |
| **AC** | FR-461 A14 monitor; OQ-16 I.4 |
| **TC** | TC-GW-020 |

- Given ANON forgalom, When naptári negyedév zárul, Then aggregált (nem PII) ripor: `E-SHADOW-003` drop-arány + k-cella eloszlás.
- Tilos a riporben: név, TAJ, nyers diplotípus, pontos idő, `Patient.id`.
- G3 vs drop: a monitor **nem** kapcsolja ki a dropot, ha a recall esik (R-020).

### PCE-GW-461-11 — SYN fixture csomag (gold v0, nem annotációs SOP)

| | |
| --- | --- |
| **AC** | §10.2 F1s kód fixture-ön; D.2 TC-GW-010..020 |
| **TC** | a fenti TC-k mind |

Minimum SYN esetek (kitalált PII **nincs**; opák ID-k):

1. ATC5 → ATC4 csonkolás (`N06AB10` → `N06AB`).
2. ATC5 leak a PCE-re → `E-SHADOW-001`.
3. `authoredOn` nap → `YYYY-Qn`.
4. `doseQuantity` jelen van a HIS mockban → kimenetben nincs.
5. Cella count 4, k = 5, COARSEN → `CLASS`.
6. Cella count 4, k = 5, DROP → nincs HITL sor, számláló +1.
7. Freq &lt; 0,5% → coarsen vagy drop a fixture-config szerint.
8. Legritkább osztály → mindig drop.
9. ANON k-csökkentés kísérlet → elutasítva.
10. TAJ a bundle-ben → `E-SHADOW-001`.
11. Negyedéves monitor JSON: csak aggregátum.

Ez **nem** a §13 gold-set annotációs SOP (klinikai G3). Az a parking lot.

---

## Sorrend

```
PCE-GW-460-01..08  →  461-01 ATC  →  461-02 idő  →  461-03 dózis
        →  461-06 freq-config  →  461-04/05 k-cella  →  461-07 rarest drop
        →  461-08 no override  →  461-09 ingest reject  →  461-10 monitor
        →  461-11 SYN fixture (párhuzamosan az első ticketektől)
```

CI: report-renderer **nem** olvassa a shadow kimenetet (FR-470). Ez a sáv nem billenti `LIVE_CDS=true`-ra.

---

## Expliciten tilos ebben a sávban

- Éles HIS / valódi betegrekord (OQ-15 + OQ-16).
- ClinLabomics vagy k ≥ 5 mint **bizonyított** anonimitás.
- YouScript / PREPARE mint OQ-16 pecsét.
- `LIVE_CDS=true`; CDS a felírónak; shadow a vizit-UI-n.
- Új FR / új küszöb kitalálása. Ha a DPO más k-t vagy ATC3-at ír elő, az F.6 + config-release, nem csendes default-csere.
