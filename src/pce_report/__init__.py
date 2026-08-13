"""F1+ signed-lab renderer (FR-210 / FR-400-STATIC / FR-490 / FR-500). Matcher OFF."""

from pce_report.flags import LIVE_CDS, MATCHER_ON
from pce_report.guidelines import GuidelineTable
from pce_report.render import render_f1plus

__all__ = ["LIVE_CDS", "MATCHER_ON", "GuidelineTable", "render_f1plus"]
