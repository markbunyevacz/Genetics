# Gateway SYN sim — PCE-GW-461-01 / 461-02

| | |
| --- | --- |
| **Ticket** | PCE-GW-461-01 (ATC4), PCE-GW-461-02 (naptári negyedév) |
| **Adat** | [Gold V0](../fixtures/gold-v0/README.md) |
| **Nem** | FR-460 PII-strip, FR-461-03 dózis, k-cella, ritka drop, élő HIS, `LIVE_CDS` |

Stdlib Python. A CLI **nem** írja ki a `Patient` erőforrást (PII ne szivárogjon a szim kimenetén).

## Futtatás

```bash
cd docs/pce/Engineering/gateway_sim

# HIS-zóna: ATC5 → ATC4, nap → 2026-Q3
python3 pce_gw_transform.py -i ../fixtures/gold-v0/gw-v0-01-normal-his-in.json

# DPO-szigorítás: ATC3
python3 pce_gw_transform.py -i ../fixtures/gold-v0/gw-v0-01-normal-his-in.json --atc-level 3

# PCE ingest védelem (ATC5 → E-SHADOW-001, exit 2)
python3 pce_gw_transform.py --mode ingest -i ../fixtures/gold-v0/gw-v0-03-atc5-pce-ingest.json

# Nap-szintű authoredOn a PCE-n
python3 pce_gw_transform.py --mode ingest -i ../fixtures/gold-v0/gw-v0-09-day-pce-ingest.json

python3 -m unittest test_pce_gw_transform.py
```

WHO ATC (S032): ATC3 = 4 karakter (`N06A`); ATC4 = 5 (`N06AB`); ATC5 = 7 (`N06AB10`). Hatóanyag-display (`escitalopram`) csonkolás után **null** — ez nem WHO-szótár.
