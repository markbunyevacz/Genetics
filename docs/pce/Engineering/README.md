# Engineering

| | |
| --- | --- |
| **Státusz** | v1.2 spec **FAGYASZTVA**; kód a `main`-en |
| **Nem** | Új FR, OQ-lezárás, intended purpose, DPIA, élő HIS, `LIVE_CDS=true` |

| Fájl | Hatókör |
| --- | --- |
| [DELIVERY-PLAN.md](DELIVERY-PLAN.md) | WP-G gateway → WP-R F1+ lelet → WP-H HITL |
| [CLEANUP.md](CLEANUP.md) | Könyvtár-takarítás + `archive/pre-cleanup-2026-08-13` visszaállítás |
| [FR-461-gateway-tickets.md](FR-461-gateway-tickets.md) | Ticket-bontás |
| [../../../src/pce_gateway/](../../../src/pce_gateway/) | Intézményi ANON gateway (Gold V0) |
| [../../../src/pce_report/](../../../src/pce_report/) | F1+ renderer (CPIC API szelet, matcher OFF) |
| [../../../tests/fixtures/gold-v0/](../../../tests/fixtures/gold-v0/README.md) | Gold V0 gateway csomag |
| [../../../tests/fixtures/f1plus-v0/](../../../tests/fixtures/f1plus-v0/README.md) | F1+ outside-call + CPIC tábla |

A `gateway_sim/` és `fixtures/` alatti README csak átirányítás.
