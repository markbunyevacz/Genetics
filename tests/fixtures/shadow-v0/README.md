# Shadow / HITL SYN gold (F1s)

Pinned extracts for the research path. **Not** the signed F1+ lab PDF.

| Fájl | Tartalom |
| --- | --- |
| `cyp2d6-knowledge.v0.json` | CPIC diplotípus CYP2D6 (*1/*1, *1/*2, *4/*4) + CYP2C19 (*1/*1 NM, *1/*2 IM, *2/*2 PM); FDA erős CYP2D6-gátló; CPIC 2023 Table 2a; CYP2C19–clopidogrel (`B01AC04`) stratégia-kategória. Párosítás `(gén, ATC5)` kulcsú. **Nincs** SSRI NM→szegény sor. |
| `pseudo-atc5-paroxetine-pce-ingest.json` | 7 karakteres paroxetin-kód. ANON default **elfogadja** (D-38). |

A **fenokonverziós nevező** külön: `tests/fixtures/pheno-gold-v0/` (N=32). A G3 ≥90% **csak** ott. Ez a mappa továbbra is a tudástábla pin, nem a G3 nevező.

Letöltve: 2026-08-13 (CYP2D6/SSRI) és 2026-08-14 (CYP2C19/clopidogrel). Spec: FR-400-LIVE, FR-410-LIVE, B.6.2.
