# Genetics — Precision Clinical Engine

Spec (frozen v1.2): **[docs/pce/README.md](docs/pce/README.md)**

Work only on **`main`**. `LIVE_CDS` and the F1+ matcher are compile-time **false**.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m pce_gateway -i tests/fixtures/gold-v0/gw-v0-01-normal-his-in.json --seed-cell 4
PYTHONPATH=src python3 -m pce_clinical --mode serve --port 8090
PYTHONPATH=src python3 -m pce_hitl --port 8091
pip install reportlab
PYTHONPATH=src python3 -m pce_report -i tests/fixtures/f1plus-v0/outside-call-cyp2d6-called.json --pdf-out /tmp/f1plus.pdf --json-out /tmp/f1plus.json
```

Delivery queue: [docs/pce/Engineering/DELIVERY-PLAN.md](docs/pce/Engineering/DELIVERY-PLAN.md). Spec coverage: [SPEC-PLAN-TRACE.md](docs/pce/Engineering/SPEC-PLAN-TRACE.md). Dataflow/UX: [DATAFLOW-AND-UX.md](docs/pce/Engineering/DATAFLOW-AND-UX.md).  
2026-08-13 tree cleanup rollback: [docs/pce/Engineering/CLEANUP.md](docs/pce/Engineering/CLEANUP.md).

