# Engineering — implementációs ticketek (nem spec)

| | |
| --- | --- |
| **Státusz** | v1.2 spec **FAGYASZTVA**; ezek a ticketek a zárolt FR-ek bontása |
| **Nem** | Új FR, OQ-lezárás, intended purpose, DPIA, élő HIS |

A spec-írás nem folytatódik. A ticketek **szintetikus** fixture-ön kódolhatók (§10.2). Éles intézményi adat: OQ-16 + OQ-15 pecsét.

| Fájl | Hatókör | Teszt-sáv |
| --- | --- | --- |
| [FR-461-gateway-tickets.md](FR-461-gateway-tickets.md) | Gateway csonkolás / k-anonimitás / ritka drop | TC-GW-010..020; előfeltétel TC-GW-001..008 |
| [fixtures/gold-v0/](fixtures/gold-v0/README.md) | SYN FHIR + CPIC European freq-szelet (A14 0,5%) | gw-v0-01..10; **nem** G3 SOP |
| [gateway_sim/](gateway_sim/README.md) | FR-460 PII + PCE-GW-461-01..03 (ATC, idő, dózis) | Gold V0; stdlib; nem élő HIS |

Gold-set annotációs SOP továbbra is §13 parking lot (nem ebben a mappában).
