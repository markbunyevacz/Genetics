# Engineering

| | |
| --- | --- |
| **Státusz** | v1.2 spec **FAGYASZTVA**; kód a `main`-en |
| **Nem** | Új FR, OQ-lezárás, intended purpose, DPIA, élő HIS, `LIVE_CDS=true` |

| Fájl | Hatókör |
| --- | --- |
| [DELIVERY-PLAN.md](DELIVERY-PLAN.md) | Megvalósítási csomagok; B-szerződés + Given/When/Then |
| [SPEC-PLAN-TRACE.md](SPEC-PLAN-TRACE.md) | Spec ↔ terv P06 státusztábla (36 FR, story, API, hiba) |
| [DATAFLOW-AND-UX.md](DATAFLOW-AND-UX.md) | F1+ / F1s adatfolyam + persona UX |
| [CLEANUP.md](CLEANUP.md) | Könyvtár-takarítás + `archive/pre-cleanup-2026-08-13` visszaállítás |
| [FR-461-gateway-tickets.md](FR-461-gateway-tickets.md) | Ticket-bontás |
| [../../../src/pce_gateway/](../../../src/pce_gateway/) | Intézményi ANON gateway (Gold V0) |
| [../../../src/pce_clinical/](../../../src/pce_clinical/) | F1+ klinikai kapu + B.3/B.4 |
| [../../../src/pce_report/](../../../src/pce_report/) | F1+ renderer (CPIC API szelet, matcher OFF) |
| [../../../src/pce_shadow/](../../../src/pce_shadow/) | F1s élő párosítás (nem a leleten) |
| [../../../src/pce_hitl/](../../../src/pce_hitl/) | Ellenőrző tár + vak API |
| [../../../src/pce_ui/](../../../src/pce_ui/) | Labor HTML + HITL HTML |
| [../../../tests/fixtures/gold-v0/](../../../tests/fixtures/gold-v0/README.md) | Gold V0 gateway csomag |
| [../../../tests/fixtures/f1plus-v0/](../../../tests/fixtures/f1plus-v0/README.md) | F1+ outside-call + CPIC tábla |
| [../../../tests/fixtures/shadow-v0/](../../../tests/fixtures/shadow-v0/README.md) | CYP2D6 tudás-pin (FDA/CPIC/WHO) |

A `gateway_sim/` és `fixtures/` alatti README csak átirányítás.
