# Cleanup manifest — 2026-08-13

Rollback point (full tree before this cleanup):

```bash
git checkout archive/pre-cleanup-2026-08-13
```

Single-path restore examples:

```bash
# Root duplicate v1.0 spec (identical to Sources copy)
git checkout archive/pre-cleanup-2026-08-13 -- PCE-SPEC-v1.0.md

# Old docs-folder Python sim + tests
git checkout archive/pre-cleanup-2026-08-13 -- docs/pce/Engineering/gateway_sim

# Fixtures as they lived under docs/
git checkout archive/pre-cleanup-2026-08-13 -- docs/pce/Engineering/fixtures/gold-v0
```

The tag is on `main` after PR #2 merge (`88d4b7a` parent). Feature branches `cursor/pce-ops-gates-3690` and `cursor/pce-spec-3690` were deleted after merge; their commits remain on `main` and in the tag.

## What moved or was removed

| Action | From | To / why |
| --- | --- | --- |
| Deleted duplicate | `/PCE-SPEC-v1.0.md` | Identical to `docs/pce/Sources/PCE-SPEC-v1.0.md` (byte-for-byte). Canonical product spec is `docs/pce/PCE-SPEC-v1.2.md`. |
| Moved | `docs/pce/Engineering/fixtures/gold-v0/` | `tests/fixtures/gold-v0/` — one Gold V0 pack, used by tests and the gateway. |
| Moved | `docs/pce/Engineering/gateway_sim/pce_gw_transform.py` | `src/pce_gateway/transform.py` |
| Removed | `docs/pce/Engineering/gateway_sim/test_pce_gw_transform.py` | Replaced by `tests/test_transform.py` + `tests/test_pipeline.py` |
| Redirect stubs | `docs/pce/Engineering/gateway_sim/README.md`, `docs/pce/Engineering/fixtures/README.md` | Pointers only, no second copy of fixtures or code |

Not deleted (unique, still in use): Outbound OQ drafts, Sales pack, A–F appendices, ProcessArtifacts, S028 PDF + note, v1.2 spec.

## Checks after cleanup

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
test ! -e PCE-SPEC-v1.0.md
test -f docs/pce/Sources/PCE-SPEC-v1.0.md
test -f tests/fixtures/gold-v0/frequency-config.v0.json
test -f src/pce_gateway/pipeline.py
test -f src/pce_report/render.py
test ! -e docs/pce/Engineering/fixtures/gold-v0
test ! -e docs/pce/Engineering/gateway_sim/pce_gw_transform.py
```
