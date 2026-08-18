# AGENTS.md

## Cursor Cloud specific instructions

Precision Clinical Engine (PCE) — a pharmacogenomics platform. It is almost pure
Python 3.12 standard library; the only third-party runtime dependency is
`reportlab` (PDF rendering). Everything runs with `PYTHONPATH=src`. Standard
commands live in `README.md`; the notes below are the non-obvious caveats.

### Services / entry points

All servers are `http.server`-based, bind to `127.0.0.1`, and print their bound
address on startup. Auth is a plain role name passed as the `Authorization`
header (e.g. `lab_signer`, `counsellor`, `dpo`, `clinician`, `hitl_reviewer`,
`admin`) — not real tokens (NFR-032).

- `pce_clinical` (`--mode serve --port 8090`): clinical B.3/B.4 REST API + the
  primary browser UI at `/` (`src/pce_ui/index.html`). SQLite at `var/clinical.sqlite`.
- `pce_hitl` (`--port 8091`): human-in-the-loop review API + UI. SQLite at `var/hitl.sqlite`.
- `pce_cds` (`--port 8092`): SMART-on-FHIR CDS Hooks. Locked off (`LIVE_CDS=false`);
  discovery lists services as `enabled: false` and hooks return `{"cards": []}`.
- `pce_gateway`: institutional ANON gateway. CLI transform/ingest, or
  `--mode serve --port 8080` (requires `--account`/`PCE_GW_ACCOUNT`).
- `sail`: standalone self-improving multi-agent engine demo, `python3 -m sail`.

### Testing caveats

- Run tests with `PCE_PHARMCAT_OFFLINE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v`.
- A handful of tests require the PharmCAT jar to physically exist at
  `var/pharmcat/pharmcat-3.4.0-all.jar` even in offline mode. It is gitignored;
  the update script fetches it via
  `python3 docs/pce/Sources/official/fetch_software_ready_pins.py --jar-only`
  (idempotent, verifies sha256). Without it, 6 tests error/fail on a missing jar.
- There is no linter (ruff/flake8/black). "Lint" in CI (`.github/workflows/ci.yml`)
  is a set of freeze/isolation grep + assert checks; run those steps to reproduce.
- Keep `LIVE_CDS`, `MATCHER_ON`, and `CPIC_F5_SOURCE=off` frozen — CI asserts them.

### Non-obvious gotchas

- The `README.md` `pce_report -i <outside-call> --pdf-out ...` example is stale:
  the F1+ renderer now enforces FR-100 and rejects outside-call files that try to
  bypass the consent gate. To produce a report/PDF, drive the full clinical flow
  (org → subject → case → counselling → consent → outside-calls → reports) through
  the `pce_clinical` server/service, then `GET .../reports/<id>/pdf`. The clinical
  UI "Szervezet + alany + eset + tanácsadás + beleegyezés" button bootstraps all of it.
- HITL review cards are produced by the gateway ingest path, not the clinical
  server. Run `pce_gateway --mode ingest -i <pce-ingest.json> --account local` to
  write an inference into `var/hitl.sqlite`, which the running `pce_hitl` server
  then serves at `/v1/hitl/inferences`.
- PDF rendering needs a Hungarian-capable TTF; `DejaVuSans.ttf` from
  `fonts-dejavu-core` is preinstalled on the base image, so no font install is needed.
