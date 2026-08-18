# SAIL — Self-improving Agent Interchange Language

Kísérleti, **PCE-től izolált** sandbox. Nem klinikai modul, nem orvostechnikai funkció, nem CDSS.

| | |
| --- | --- |
| Csomag | `src/sail/` |
| Teszt | `tests/test_sail_*.py` |
| Futtatás | `PYTHONPATH=src python3 -m sail` |
| Függőség | stdlib (Python 3.12+). Nincs OpenAI, nincs ACP SDK. |

## Mit csinál

Négy kommunikációs sáv, in-process ágens busz, empirikus sávválasztó, vektor-memória (SHA-256 hash-embedding, nem foundation-model), és egy mért önjavító lépés:

1. Napló: sáv, feladat-típus, parse/feladat-siker.
2. `LaneSelector`: `(task_kind, lane)` sikerráta, epsilon-greedy exploráció.
3. Sikeres minták a `VectorMemory`-ban; a koordinátor hasonló kérést a közeli sikeres címzetthez küldhet.
4. `ImprovementEngine.step()`: empirikusan legjobb sávok elfogadása, az utolsó ablak újrajátszása, revert ha a rolling success romlana.

Ágensek a demóban: `coordinator`, `analyzer`, `planner`.

## ACP → A2A

A BeeAI **Agent Communication Protocol (ACP) 2025-08-29-én beolvadt az A2A-ba**; a `i-am-bee/acp` repo archivált. Ez a prototípus **nem** ACP-kliens. Az envelope mezői A2A-szerűek (`role`, `parts`, `task_id`, `context_id`); a transport in-process. HTTP/JSON-RPC A2A SDK későbbi PR.

## PCE-izoláció

- `src/sail/` nem importál `pce_*` csomagot.
- `pce_*` nem importál `sail`-t.
- `LIVE_CDS`, matcher, F1+ renderer, Outbound/Sales iratok érintetlenek.
- A CI FR-470 deny-list (`openai` / `anthropic` / `langchain` a klinikai úton) nem vonatkozik erre a sandboxra, és a default SAIL ezeket nem is húzza be.

## Mit nem állítunk

- Nincs 1 ms / 50 ms SLA, nincs „heti 5%” teljesítménygarancia.
- Nincs Tesla-stílusú neurális állapotmegosztás két foundation model között.
- Nincs SEAL súlyfrissítés, kvantum-protokoll, blockchain ágensháló.
- A hash-embedding **nem** OpenAI `text-embedding-ada-002` helyettesítője; csak offline, determinisztikus vektor a nearest-neighbour memóriához.
- DSPy / külső LM **opcionális**. Alapút LLM nélkül megy. Extra: `pip install 'pce-gateway[sail-llm]'` (CI nem telepíti).

## Parancsok

```bash
PYTHONPATH=src python3 -m unittest tests.test_sail_lanes tests.test_sail_engine tests.test_sail_bus -v
PYTHONPATH=src python3 -m sail
```
