"""FR-530 SMART on FHIR stub. Launch is not interruptive while LIVE_CDS is false."""
from __future__ import annotations

from typing import Any


def smart_configuration(*, live_cds: bool) -> dict[str, Any]:
    if not live_cds:
        return {
            "live_cds": False,
            "capabilities": [],
            "message_hu": (
                "SMART launch zárva. A felírási workflow-ban nincs interruptive CDSS, "
                "amíg a signed release LIVE_CDS=true."
            ),
        }
    return {
        "live_cds": True,
        "capabilities": ["launch-ehr", "client-confidential-symmetric", "context-ehr-patient"],
        "grant_types_supported": ["authorization_code"],
        "message_hu": "SMART stub SYN-en. Éles EHR-launch pecsét + signed release után.",
    }
