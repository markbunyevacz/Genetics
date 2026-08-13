# Gateway SYN sim — FR-460 + PCE-GW-461-01..03

| | |
| --- | --- |
| **Ticket** | FR-460 PII; PCE-GW-461-01 ATC4; 461-02 negyedév; 461-03 dózis |
| **Adat** | [Gold V0](../fixtures/gold-v0/README.md) |
| **Nem** | k-cella (461-04/05), ritka drop (461-06/07), élő HIS, `LIVE_CDS` |

Stdlib Python. A default CLI **GatewayEvent** kimenete nem tartalmaz `Patient` mezőt, `doseQuantity`-t, TAJ-t vagy nevet. A nem + születési év csak `--with-local` mellett jelenik meg (`local_counter`), és **nem** megy a PCE-re.

FHIR R4: `Bundle.entry[].resource`. A dózis a Gold V0-ban `dosageInstruction[].doseAndRate[].doseQuantity` (nem DSTU2 `doseQuantity` az instructionen). A szim mindkét utat törli.

## Futtatás

```bash
cd docs/pce/Engineering/gateway_sim

python3 pce_gw_transform.py -i ../fixtures/gold-v0/gw-v0-01-normal-his-in.json
# N06AB, 2026-Q3, display null, nincs Patient, nincs dózis

python3 pce_gw_transform.py --with-local -i ../fixtures/gold-v0/gw-v0-01-normal-his-in.json
# + local_counter.birth_year=1980 (intézményi számláló)

python3 pce_gw_transform.py --mode ingest -i ../fixtures/gold-v0/gw-v0-03-atc5-pce-ingest.json
python3 pce_gw_transform.py --mode ingest -i ../fixtures/gold-v0/gw-v0-08-taj-pce-ingest.json
python3 pce_gw_transform.py --mode ingest -i ../fixtures/gold-v0/gw-v0-09-day-pce-ingest.json

python3 -m unittest test_pce_gw_transform.py
```

Következő ticket-sorrend: **461-06** freq-allowlist, utána **461-04/05** k-cella (a cella fenotípus-osztályt használ).
