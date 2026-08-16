#!/usr/bin/env python3
"""OQ-05 counsel send-pack TOC + SHA-256. Not a seal.

Hashes the brief VI attachments plus the named handover files
(REG-010, gold fixture, D.1, FELTÉTELLEL tervezet). Does not hash
this envelope file. Does not fill the V. seal. Does not include
REG-030 QMS bytes.

Stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUT = ROOT / "docs" / "pce" / "Outbound" / "OQ-05-SEND-PACK.md"
DEFAULT_DATE = "2026-08-16"

SEAL_FORBIDDEN = (
    "OQ-05 LEZÁRVA",
    "OQ-05 pecsételve",
    "OQ-05 pecsételt",
    "**SEALED**",
    "100% hermetikus",
)


class PackItem(NamedTuple):
    pack_id: str
    relpath: str
    role: str
    note: str


# Formal handover bytes. Broader citation-existence paths (f5_rec, PharmCAT
# wrapper, pin-fetcher) stay in Oq05CounselSendPackTests — those are ops,
# not the Rule 11 envelope.
PACK_ITEMS: tuple[PackItem, ...] = (
    PackItem(
        "COVER",
        "docs/pce/Outbound/OQ-05-counsel-brief.md",
        "Fedélirat",
        "OQ-05 kérés. V. checkbox üres. Nem pecsét.",
    ),
    PackItem(
        "FELT",
        "docs/pce/Outbound/OQ-05-feltetellel-tervezet.md",
        "Záradék-tervezet",
        "FELTÉTELLEL kitöltési javaslat. Nem pecsét.",
    ),
    PackItem(
        "SPEC",
        "docs/pce/PCE-SPEC-v1.2.md",
        "Spec v1.2",
        "Fagyasztott követelmény. OQ-05 ELŐTERJESZTVE.",
    ),
    PackItem(
        "REG-010",
        "docs/pce/A-intended-purpose-and-modules.md",
        "REG-010",
        "A melléklet. Intended purpose, modulonként.",
    ),
    PackItem(
        "F1",
        "docs/pce/F-decision-package.md",
        "F.1",
        "Gyártói kérés, nem counsel-válasz.",
    ),
    PackItem(
        "G",
        "docs/pce/G-open-items.md",
        "G §3 + §7",
        "Javaslat a pecsételőnek. Nem pecsét.",
    ),
    PackItem(
        "D1",
        "docs/pce/D-risk-and-traceability.md",
        "D.1",
        "Kezdeti ISO 14971. Nem teljes dosszié.",
    ),
    PackItem(
        "PROTOCOL",
        "docs/pce/ProcessArtifacts/OQ-05-TEST-PROTOCOL.md",
        "Szoftver-evidencia",
        "Mapped 51 egyedi teszt; Q3 = 10. Nem pecsét.",
    ),
    PackItem(
        "REGISTRY",
        "docs/pce/ProcessArtifacts/SOURCE-REGISTRY.md",
        "Forráslista",
        "S004/S005 MDCG URL (PDF nincs a repóban). S077/S080 COM pin.",
    ),
    PackItem(
        "GOLD",
        "tests/fixtures/f1plus-v0/outside-call-cyp2d6-called.json",
        "Q1 gold",
        "SYN outside-call JSON. Nem aláírt PDF.",
    ),
    PackItem(
        "TEST-REPORT",
        "tests/test_report.py",
        "Q1 teszt",
        "Renderer / B.4.1 / izoláció.",
    ),
    PackItem(
        "SCHEMA",
        "src/pce_report/schema.py",
        "B.4.1",
        "ALLOWED_B41_TOP_LEVEL élő méret.",
    ),
    PackItem(
        "CI",
        ".github/workflows/ci.yml",
        "Q3 CI",
        "LIVE_CDS=false; MATCHER_ON=false; IIA_SAFE_BLOCK=true (IIa-safe pár-lakat, nem COM-mentesség).",
    ),
    PackItem(
        "S077",
        "docs/pce/Sources/official/com-2025-1023-act.pdf",
        "Q4 S077",
        "COM(2025) 1023 PDF. Javaslat, nem hatályos jog.",
    ),
    PackItem(
        "S080",
        "docs/pce/Sources/official/eur-lex-com-2025-1023.html",
        "Q4 S080",
        "EUR-Lex HTML. Javasolt Rule 11 olvasható szövege.",
    ),
)

EXCLUDED: tuple[tuple[str, str], ...] = (
    (
        "Ez a SEND-PACK irat",
        "Boríték. A saját SHA-256-ját nem tartalmazza; a git commit az irat byte-jaira vonatkozik.",
    ),
    (
        "MDCG 2019-11 Rev.1 PDF",
        "Nincs a repóban. Counsel saját példánya. S004/S005 URL a SOURCE-REGISTRY-ben.",
    ),
    (
        "MDCG 2024-7",
        "Nem melléklet. PAR-sablon, nem Rule 11 Q&A (E-30).",
    ),
    (
        "Aláírt példa-lelet PDF",
        "Nincs és nem készül. Q1 = gold JSON.",
    ),
    (
        "REG-030 QMS fájl",
        "ISO 13485 / IEC 62304 / ISO 14971, PMS, gyártói nyilatkozat, regisztráció. F2-párhuzamos. Nem küldési feltétel.",
    ),
    (
        "Gyártó cégneve",
        "A9; `[Gyártó neve]`; a küldő tölti küldéskor, nem a git.",
    ),
    (
        "OQ-05 V. pecsét",
        "Checkbox üres. Counsel tölti.",
    ),
)


class FileRecord(NamedTuple):
    item: PackItem
    size: int
    sha256: str


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def records() -> tuple[FileRecord, ...]:
    out: list[FileRecord] = []
    missing: list[str] = []
    for item in PACK_ITEMS:
        path = ROOT / item.relpath
        if not path.is_file():
            missing.append(item.relpath)
            continue
        blob = path.read_bytes()
        out.append(FileRecord(item, len(blob), sha256_bytes(blob)))
    if missing:
        raise SystemExit("send-pack path missing: " + ", ".join(missing))
    return tuple(out)


def pack_digest(recs: tuple[FileRecord, ...]) -> str:
    lines = "".join(f"{r.item.relpath} {r.sha256}\n" for r in recs)
    return sha256_bytes(lines.encode("utf-8"))


def render(date: str) -> str:
    recs = records()
    digest = pack_digest(recs)
    lines: list[str] = []
    a = lines.append
    a("# OQ-05 küldőcsomag — tartalomjegyzék és SHA-256")
    a("")
    a("| | |")
    a("| --- | --- |")
    a("| **Iktató** | PCE-OUT-OQ-05-SEND / v1.2 |")
    a(f"| **Dátum** | {date} |")
    a("| **Státusz** | **Átadás-átvételi boríték — nem pecsét.** Nem counsel-állásfoglalás. Nem CE. |")
    a("| **Algoritmus** | SHA-256, fájlbyte, bináris (nem kanonizált szöveg) |")
    a(f"| **Csomag-ujjlenyomat** | `{digest}` |")
    a("| **OQ-05 V.** | üres (IGEN / NEM / FELTÉTELLEL a counselé) |")
    a("")
    a("A csomag-ujjlenyomat a `relatív_út + szóköz + sha256 + soremelés` sorok SHA-256-ja, a lenti sorrendben. A boríték **saját** hashét **nem** tartalmazza.")
    a("")
    a("Ez **nem** tölti ki az OQ-05 V. pecsétet. REG-030 **nem** küldési feltétel. D.1 kezdeti 14971, nem teljes dosszié. A Q1 gold **nem** aláírt PDF. A mapped evidenciatábla **51** egyedi teszt, a Q3 **10**; a suite mérete **nem** IGEN.")
    a("")
    a("## 1. Tartalomjegyzék")
    a("")
    a("| # | ID | Szerep | Útvonal |")
    a("| --- | --- | --- | --- |")
    for i, rec in enumerate(recs, start=1):
        a(f"| {i} | **{rec.item.pack_id}** | {rec.item.role} | `{rec.item.relpath}` |")
    a("")
    a("## 2. SHA-256 lista")
    a("")
    a("| ID | Byte | SHA-256 | Megjegyzés |")
    a("| --- | ---: | --- | --- |")
    for rec in recs:
        a(
            f"| **{rec.item.pack_id}** | {rec.size} | `{rec.sha256}` | {rec.item.note} |"
        )
    a("")
    a("## 3. Ami szándékosan nincs a hash-táblában")
    a("")
    a("| Tétel | Indok |")
    a("| --- | --- |")
    for title, reason in EXCLUDED:
        a(f"| {title} | {reason} |")
    a("")
    a("## 4. Ellenőrzés")
    a("")
    a("```")
    a("PYTHONPATH=src python3 docs/pce/ProcessArtifacts/BuildScripts/generate_oq05_send_pack.py --write")
    a("PCE_PHARMCAT_OFFLINE=1 PYTHONPATH=src python3 -m unittest tests.test_oq05_protocol.Oq05CounselSendPackTests -v")
    a("```")
    a("")
    a("A committed `OQ-05-SEND-PACK.md` byte-ra egyezik a generátor kimenetével. Eltérés = a melléklet változott, a borítékot újra kell írni. Ez **nem** pecsét-feloldás.")
    a("")
    a("*Generálta: `docs/pce/ProcessArtifacts/BuildScripts/generate_oq05_send_pack.py`.*")
    a("")
    text = "\n".join(lines)
    for tok in SEAL_FORBIDDEN:
        if tok in text:
            raise SystemExit(f"send-pack would contain forbidden seal token: {tok!r}")
    return text


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--date", default=DEFAULT_DATE)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--write", action="store_true", help="overwrite the committed envelope")
    args = p.parse_args(argv)
    text = render(args.date)
    if args.write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        sys.stdout.write(f"wrote {args.out}\n")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
