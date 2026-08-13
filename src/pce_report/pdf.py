"""FR-500 / B.4.2 PDF. Every page: config, callability, signer, A.1, A.1.1, colophon."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
)
FONT_NAME = "PCESans"
HEADER_H = 78
FOOTER_H = 36


def _font_path() -> Path:
    for p in FONT_CANDIDATES:
        if p.is_file():
            return p
    raise FileNotFoundError(
        "No Hungarian-capable TTF found. Install fonts-dejavu-core (DejaVuSans.ttf)."
    )


def _clip(text: str, n: int) -> str:
    text = text.replace("\n", " ").strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def write_pdf(report: dict[str, Any], dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(_font_path())))
    c = canvas.Canvas(str(dest), pagesize=A4)
    width, height = A4
    page_no = 1
    y = height - HEADER_H - 8
    x0 = 40

    a1 = report.get("a1_intended_purpose") or report.get("intended_purpose_clause") or ""
    a11 = report.get("a11_disclaimer") or report.get("disclaimer_clause") or ""
    call = report.get("callability_summary") or {
        report.get("case", {}).get("gene"): report.get("case", {}).get("callability")
    }
    signer = (report.get("white_label") or {}).get("signer_slot") or "SYN-MD-001"
    colophon = (report.get("white_label") or {}).get("colophon") or (
        "Precision Clinical Engine — technológiai szállító"
    )
    cfg = report.get("config_id", "")
    pipe = report.get("pipeline_version") or "pce-report"

    def chrome() -> None:
        c.setFont(FONT_NAME, 7)
        top = height - 14
        c.drawString(x0, top, _clip(f"{cfg} | {pipe} | page {page_no}", 110))
        c.drawString(x0, top - 11, _clip(f"callability {call} | aláíró hely: {signer}", 110))
        c.drawString(x0, top - 22, _clip("A.1: " + a1, 110))
        c.drawString(x0, top - 33, _clip("A.1.1: " + a11, 110))
        c.drawString(x0, top - 44, _clip(colophon, 110))
        c.line(x0, height - HEADER_H + 6, width - 40, height - HEADER_H + 6)
        c.drawString(x0, 22, _clip(f"{cfg} | {call} | {signer} | {colophon} | {page_no}", 110))
        c.line(x0, FOOTER_H, width - 40, FOOTER_H)

    def new_page() -> None:
        nonlocal page_no, y
        chrome()
        c.showPage()
        page_no += 1
        y = height - HEADER_H - 8
        chrome()

    def line(text: str, size: int = 9) -> None:
        nonlocal y
        c.setFont(FONT_NAME, size)
        max_chars = 108 if size <= 9 else 90
        remaining = text.replace("\t", " ")
        if remaining == "":
            remaining = " "
        while remaining:
            chunk, remaining = remaining[:max_chars], remaining[max_chars:]
            if y < FOOTER_H + 14:
                new_page()
                c.setFont(FONT_NAME, size)
            c.drawString(x0, y, chunk)
            y -= size + 3

    chrome()
    case = report["case"]
    line("Precision Clinical Engine — F1+ report", 12)
    line(f"config_id {cfg}  matcher_on={report.get('matcher_on')}  LIVE_CDS={report.get('live_cds')}")
    line(f"medications_applied_to_recommendations={report.get('medications_applied_to_recommendations')}")
    line(f"gyogyszerlista_a_leleten={report.get('gyogyszerlista_a_leleten')}")
    if report.get("megjegyzes_hu"):
        line(str(report["megjegyzes_hu"]))
    if report.get("diplotipus_forras_hu"):
        line(str(report["diplotipus_forras_hu"]))
    if report.get("report_id"):
        line(f"report_id={report['report_id']} case_id={report.get('case_id')}")
    if report.get("counselling"):
        line(f"counselling={report['counselling']} license={report.get('performing_org_license_id')}")
    line("")
    line("A.1 intended purpose", 11)
    for para in a1.split("\n"):
        line(para)
    line("")
    line("A.1.1 disclaimer", 11)
    for para in a11.split("\n"):
        line(para)
    line("")
    line("Outside-call", 11)
    line(
        f"id={case.get('case_display_id')} gene={case['gene']} "
        f"diplotype={case.get('diplotype')} callability={case['callability']} "
        f"positive_drug_assertion={case['positive_drug_assertion']}"
    )
    if case.get("fr210"):
        line(str(case["fr210"]))
    line("")
    line(f"CPIC pair_view ({report['pair_count']} rows) — FR-400-STATIC, no medication filter", 11)
    for p in report["pairs"]:
        line(
            f"{p['drugname']} | {p['cpiclevel']} | {p['usedforrecommendation']} | {p['guidelineurl']}"
        )
    line("")
    line(
        f"CPIC recommendation_view ({report['guideline_row_count']} rows) — full gene table",
        11,
    )
    for rec in report["guideline_rows"]:
        lk = rec.get("lookupkey")
        line(
            f"{rec.get('drugname')} | {lk} | {rec.get('classification')} | "
            f"{rec.get('drugrecommendation')} | {rec.get('guidelineurl')}"
        )
    line("")
    line(f"unsourced_claims={report['unsourced_claims']}")
    line(str(report.get("edu_note") or ""))
    chrome()
    c.save()
    return dest
