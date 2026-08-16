# BuildScripts

Stdlib generator scripts. No pytest, Pydantic, or coverage packages.

| Script | Output | What it is not |
| --- | --- | --- |
| `generate_oq05_protocol.py` | `../OQ-05-TEST-PROTOCOL.md` | Not an OQ-05 seal. Not a counsel opinion. Not CE. |
| `generate_oq05_send_pack.py` | `../../Outbound/OQ-05-SEND-PACK.md` | Not an OQ-05 seal. Envelope SHA-256 list; does not hash itself. |

```
PYTHONPATH=src python3 docs/pce/ProcessArtifacts/BuildScripts/generate_oq05_protocol.py --write
PYTHONPATH=src python3 docs/pce/ProcessArtifacts/BuildScripts/generate_oq05_send_pack.py --write
```

`--write` overwrites the committed protocol. CI does not rewrite it; `tests/test_oq05_protocol.py` diffs the committed file against a fresh generate().
