"""B.5 clinical error codes. Messages are the spec HU text, not paraphrases."""
from __future__ import annotations

from typing import Any

# B.5 catalogue — HTTP + HU user text (principle column).
B5: dict[str, tuple[int, str]] = {
    "E-CONSENT-001": (
        409,
        "Mintavétel előtti genetikai tanácsadás hiányzik (2008/XXI. 6. § (2)).",
    ),
    "E-CONSENT-002": (
        409,
        "A tanácsadásnak a mintavétel előtt kell történnie (6. § (2)).",
    ),
    "E-CONSENT-003": (409, "Írásbeli beleegyezés hiányzik (8. §)."),
    "E-CONSENT-004": (409, "Célon túli gén, nincs ismételt beleegyezés (15. §)."),
    "E-CONSENT-005": (409, "Nincs engedélyezett performing_org (12. § (1))."),
    "E-CONSENT-006": (
        409,
        "Álnevesített shadow, nincs kutatási hozzájárulás (FR-115).",
    ),
    "E-VCF-001": (400, "A VCF nem olvasható; részleges riport nem készül."),
    "E-VCF-002": (400, "Sample-enként külön eset kell."),
    "E-VCF-003": (400, "A referencia-genom hiányzik vagy nem GRCh37/38."),
    "E-VCF-004": (413, "A VCF nagyobb, mint 5 GB."),
    "E-CALL-001": (400, "Üres diplotípus outside-callban."),
    "W-CALL-010": (
        409,
        "Outside-call vs VCF konfliktus. Automatikus választás nincs; emberi döntés.",
    ),
    "E-MAP-001": (409, "Ismeretlen gyógyszerkód; a riport nem megy ki hiányos listával."),
    "E-GONE-010": (410, "Visszavont / törölt riport (FR-110)."),
    "E-ISO-001": (403, "A clinician szerep nem olvassa a HITL/shadow utat (FR-470)."),
    "E-ISO-002": (404, "CDS endpoint nincs az F1+ buildben (LIVE_CDS=false)."),
    "E-EDU-001": (422, "F1+ renderer tiltott ha–akkor / „Ön” token (FR-410-EDU)."),
    "E-AUDIT-001": (409, "Az AuditEvent napló append-only; utólagos módosítás elutasított."),
}


class ClinicalError(Exception):
    def __init__(
        self,
        code: str,
        *,
        extra: dict[str, Any] | None = None,
        http: int | None = None,
        message_hu: str | None = None,
    ) -> None:
        spec_http, spec_hu = B5.get(code, (400, code))
        self.code = code
        self.http = http if http is not None else spec_http
        self.message_hu = message_hu if message_hu is not None else spec_hu
        self.extra = extra or {}
        super().__init__(self.code)

    def as_dict(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "error": self.code,
            "http": self.http,
            "message_hu": self.message_hu,
        }
        body.update(self.extra)
        return body
