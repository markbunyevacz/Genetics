"""FR-710 deterministic HU explanation. No LLM, no SHAP (NFR-060)."""
from __future__ import annotations

import hashlib
from typing import Any

from pce_report.statements import A1_INTENDED_PURPOSE

TEMPLATE = (
    "A 2008. évi XXI. tv. 6. § (6) szerinti magyarázat.\n"
    "config_id={config_id}\n"
    "case_id={case_id}\n"
    "callability={callability}\n"
    "gének:\n{genes_block}\n"
    "A lelet A.1 szerinti célja: {a1_first}\n"
    "A szoftver nem javasol terápiát, nem számít dózist, és nem helyettesíti "
    "a képzett egészségügyi szakember döntését.\n"
    "Guideline-forrás URL-ek:\n{urls}\n"
)


def _first_sentence(text: str) -> str:
    part = text.strip().split("\n", 1)[0].strip()
    return part


def build_explanation(report: dict[str, Any]) -> dict[str, str]:
    genes = report.get("genes") or []
    lines: list[str] = []
    urls: list[str] = []
    for g in genes:
        lines.append(
            f"- {g.get('gene')} diplotípus={g.get('diplotype')} "
            f"callability={g.get('callability')}"
        )
    for finding in report.get("findings") or []:
        for stmt in finding.get("statements") or []:
            url = stmt.get("url")
            if isinstance(url, str) and url not in urls:
                urls.append(url)
    body = TEMPLATE.format(
        config_id=report["config_id"],
        case_id=report["case_id"],
        callability=report.get("callability_summary"),
        genes_block="\n".join(lines) if lines else "- (nincs gén a beteg-példányon)",
        a1_first=_first_sentence(A1_INTENDED_PURPOSE),
        urls="\n".join(urls) if urls else "(nincs URL)",
    )
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return {"body_hu": body, "hash": digest}
