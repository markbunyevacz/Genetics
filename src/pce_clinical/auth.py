"""SYN IAM roles (E.4). Tokens are the role name; not production MFA (NFR-032)."""
from __future__ import annotations

from pce_clinical.errors import ClinicalError

ROLES = frozenset(
    {"counsellor", "lab_signer", "clinician", "hitl_reviewer", "dpo", "gateway", "admin"}
)

# FR-100: admin is a role, not a bypass.
WRITE_CASE = frozenset({"lab_signer", "admin"})
WRITE_CONSENT = frozenset({"counsellor", "lab_signer", "admin"})
READ_REPORT = frozenset({"lab_signer", "counsellor", "dpo", "admin", "clinician"})
WRITE_REPORT = frozenset({"lab_signer", "admin"})
DPO = frozenset({"dpo", "admin"})
HITL = frozenset({"hitl_reviewer", "dpo"})


def parse_role(authorization: str | None) -> str:
    if not authorization:
        return "anonymous"
    raw = authorization.strip()
    if raw.lower().startswith("bearer "):
        raw = raw[7:].strip()
    if raw in ROLES:
        return raw
    return "anonymous"


def require_role(authorization: str | None, allowed: frozenset[str]) -> str:
    role = parse_role(authorization)
    if role not in allowed:
        raise ClinicalError("E-ISO-001", http=403, extra={"role": role})
    return role
