"""FR-500 PDF from a rendered F1+ JSON report. Embeds a system TTF for Hungarian."""
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


def _font_path() -> Path:
    for p in FONT_CANDIDATES:
        if p.is_file():
            return p
    raise FileNotFoundError(
        "No Hungarian-capable TTF found. Install fonts-dejavu-core (DejaVuSans.ttf)."
    )


def write_pdf(report: dict[str, Any], dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(_font_path())))
    c = canvas.Canvas(str(dest), pagesize=A4)
    width, height = A4
    x0, y = 40, height - 40
    c.setFont(FONT_NAME, 11)

    def line(text: str, size: int = 9) -> None:
        nonlocal y
        c.setFont(FONT_NAME, size)
        max_chars = 108 if size <= 9 else 90
        remaining = text.replace("\t", " ")
        while remaining:
            chunk, remaining = remaining[:max_chars], remaining[max_chars:]
            if y < 50:
                c.showPage()
                y = height - 40
                c.setFont(FONT_NAME, size)
            c.drawString(x0, y, chunk)
            y -= size + 3

    case = report["case"]
    line("Precision Clinical Engine — F1+ report", 12)
    line(f"config_id {report['config_id']}  matcher_on={report['matcher_on']}  LIVE_CDS={report['live_cds']}")
    line(f"medications_applied_to_recommendations={report['medications_applied_to_recommendations']}")
    line("")
    line("A.1 intended purpose", 11)
    for para in report["a1_intended_purpose"].split("\n"):
        line(para)
    line("")
    line("A.1.1 disclaimer", 11)
    for para in report["a11_disclaimer"].split("\n"):
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
    c.save()
    return dest
