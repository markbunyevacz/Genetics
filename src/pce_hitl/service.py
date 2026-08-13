"""HITL cards, reviewer-blind step, verdict (B.4.6, E.4)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from pce_hitl.errors import HitlError
from pce_hitl.pii import pii_hits
from pce_hitl.store import HitlStore
from pce_shadow.engine import infer

BLIND_ON = True
FORBIDDEN_CARD_KEYS = (
    "name",
    "taj",
    "age",
    "birth",
    "birthDate",
    "birth_year",
    "ward",
    "physician",
    "Practitioner",
    "patient",
)
PII_SCAN_FIELDS = ("case_display_id", "gene", "phenotype_display", "config_id")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def opaque_display_id(material: str) -> str:
    return hashlib.sha256(material.encode("utf-8")).hexdigest().upper()[:5]


def _card_medications(meds: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for med in meds:
        code = med.get("code")
        if isinstance(code, str):
            out.append({"code": code, "system": str(med.get("system") or "http://www.whocc.no/atc")})
    return out


def _phenotype_display(body: dict[str, Any]) -> str | None:
    if body.get("diplotype_granularity") == "CLASS":
        cls = body.get("phenotype_class")
        return f"CLASS:{cls}" if cls else "CLASS"
    dips = body.get("diplotypes") or []
    if dips:
        gene = dips[0].get("gene")
        star = dips[0].get("diplotype")
        if gene and star:
            return f"{gene} {star}"
        return star
    rows = body.get("genotype_phenotype") or []
    if rows and rows[0].get("genotype_phenotype"):
        return str(rows[0]["genotype_phenotype"])
    return None


def _primary_gene(body: dict[str, Any]) -> str | None:
    dips = body.get("diplotypes") or []
    if dips and isinstance(dips[0].get("gene"), str):
        return dips[0]["gene"]
    rows = body.get("genotype_phenotype") or []
    if rows and isinstance(rows[0].get("gene"), str):
        return rows[0]["gene"]
    return None


def _motor_category(body: dict[str, Any]) -> str | None:
    findings = body.get("live_findings") or []
    if findings and isinstance(findings[0], dict):
        cat = findings[0].get("strategy_category")
        return str(cat) if cat else None
    if body.get("clinical_context") == "ABSENT":
        return "NOT_EVALUABLE"
    return None


def persist_inference(store: HitlStore, payload: dict[str, Any]) -> dict[str, Any]:
    body = infer(payload)
    material = body.get("payload_hash") or json.dumps(
        {"d": body.get("diplotypes"), "m": body.get("medications")},
        sort_keys=True,
        default=str,
    )
    display = opaque_display_id(str(material))
    rec = {
        "id": body["id"],
        "gateway_event_id": body.get("gateway_event_id"),
        "case_display_id": display,
        "config_id": body["config_id"],
        "gene": _primary_gene(body),
        "phenotype_display": _phenotype_display(body),
        "medications": _card_medications(body.get("medications") or []),
        "clinical_context": body["clinical_context"],
        "body": body,
        "created_at": _now(),
    }
    store.insert_inference(rec)
    return rec


class HitlService:
    def __init__(self, store: HitlStore, *, blind_on: bool = BLIND_ON) -> None:
        self.store = store
        self.blind_on = blind_on

    def list_cards(self) -> list[dict[str, Any]]:
        rows = self.store.query(
            "SELECT id, case_display_id, config_id, gene, phenotype_display, "
            "medications_json, clinical_context, created_at FROM shadow_inference "
            "ORDER BY created_at"
        )
        cards = []
        for row in rows:
            card = {
                "id": row["id"],
                "case_display_id": row["case_display_id"],
                "gene": row["gene"],
                "phenotype_display": row["phenotype_display"],
                "medications": json.loads(row["medications_json"]),
                "config_id": row["config_id"],
                "clinical_context": row["clinical_context"],
                "created_at": row["created_at"],
                "blind_required": self.blind_on,
            }
            _assert_card_clean(card)
            cards.append(card)
        return cards

    def get_card(self, inference_id: str, *, reveal_motor: bool = False) -> dict[str, Any]:
        row = self.store.one("SELECT * FROM shadow_inference WHERE id = ?", (inference_id,))
        if row is None:
            raise HitlError("E-HITL-NOTFOUND", http=404, message_hu="Nincs ilyen inferencia.")
        blind = self.store.one("SELECT * FROM hitl_blind WHERE inference_id = ?", (inference_id,))
        review = self.store.one("SELECT * FROM hitl_review WHERE inference_id = ?", (inference_id,))
        body = json.loads(row["body_json"])
        card = {
            "id": row["id"],
            "case_display_id": row["case_display_id"],
            "gene": row["gene"],
            "phenotype_display": row["phenotype_display"],
            "medications": json.loads(row["medications_json"]),
            "config_id": row["config_id"],
            "clinical_context": row["clinical_context"],
            "created_at": row["created_at"],
            "blind_required": self.blind_on,
            "blind_complete": blind is not None,
            "review_complete": review is not None,
        }
        show_motor = (not self.blind_on) or reveal_motor or blind is not None
        if show_motor:
            card["motor_category"] = _motor_category(body)
            card["live_findings"] = body.get("live_findings") or []
            card["phenoconversion"] = body.get("phenoconversion")
            card["organ_flags"] = body.get("organ_flags") or []
            card["genotype_phenotype"] = body.get("genotype_phenotype")
            card["functional_phenotype"] = body.get("functional_phenotype") or []
        if blind is not None:
            card["blind_decision"] = {
                "choice": blind["choice"],
                "reviewer_id": blind["reviewer_id"],
                "at": blind["at"],
            }
        if review is not None:
            card["verdict"] = {
                "verdict": review["verdict"],
                "reason_code": review["reason_code"],
                "at": review["at"],
            }
        _assert_card_clean(card)
        return card

    def record_blind(self, inference_id: str, choice: str, reviewer_id: str) -> dict[str, Any]:
        allowed = {"CONTINUE", "ALTERNATIVE", "DOSE_CHANGE", "INSUFFICIENT"}
        if choice not in allowed:
            raise HitlError("E-HITL-BLIND", http=400, message_hu="Érvénytelen vak döntés.")
        self.get_card(inference_id)
        existing = self.store.one("SELECT inference_id FROM hitl_blind WHERE inference_id = ?", (inference_id,))
        if existing is not None:
            raise HitlError(
                "E-HITL-IMMUTABLE",
                http=409,
                message_hu="A vak döntés immutábilis.",
            )
        self.store.execute(
            "INSERT INTO hitl_blind (inference_id, choice, reviewer_id, at) VALUES (?, ?, ?, ?)",
            (inference_id, choice, reviewer_id, _now()),
        )
        return self.get_card(inference_id, reveal_motor=True)

    def record_review(
        self,
        inference_id: str,
        verdict: str,
        reason_code: str,
        reviewer_id: str,
        note: str | None = None,
    ) -> dict[str, Any]:
        allowed = {"AGREE", "DISAGREE", "INSUFFICIENT_DATA"}
        if verdict not in allowed:
            raise HitlError("E-HITL-VERDICT", http=400, message_hu="Érvénytelen verdict.")
        if not (reason_code or "").strip():
            raise HitlError("E-HITL-REASON", http=400, message_hu="A reason_code kötelező.")
        if self.blind_on:
            blind = self.store.one("SELECT inference_id FROM hitl_blind WHERE inference_id = ?", (inference_id,))
            if blind is None:
                raise HitlError(
                    "E-HITL-BLIND",
                    http=409,
                    message_hu="Először a vak lépést kell rögzíteni.",
                )
        if note:
            hits = pii_hits(note)
            if hits:
                raise HitlError(
                    "E-HITL-PII",
                    http=400,
                    message_hu="A szabad szöveg személyes adatot tartalmazhat.",
                    extra={"hits": hits},
                )
        existing = self.store.one("SELECT inference_id FROM hitl_review WHERE inference_id = ?", (inference_id,))
        if existing is not None:
            raise HitlError("E-HITL-IMMUTABLE", http=409, message_hu="A verdict immutábilis.")
        self.store.execute(
            """
            INSERT INTO hitl_review (inference_id, verdict, reason_code, note, reviewer_id, at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (inference_id, verdict, reason_code.strip(), note, reviewer_id, _now()),
        )
        return self.get_card(inference_id, reveal_motor=True)


def _assert_card_clean(card: dict[str, Any]) -> None:
    dumped = json.dumps(card, default=str)
    for token in ("SYN-NAME", "SYN-TAJ", "dose_mg", "doseQuantity"):
        if token in dumped:
            raise HitlError("E-HITL-PII", http=500, message_hu="A kártya PII-t vagy dózist szivárogtat.")
    for key in FORBIDDEN_CARD_KEYS:
        if key in card:
            raise HitlError("E-HITL-PII", http=500, message_hu="Tiltott kártyamező.")
    for field in PII_SCAN_FIELDS:
        val = card.get(field)
        if isinstance(val, str) and pii_hits(val):
            raise HitlError("E-HITL-PII", http=500, message_hu="A kártya PII-t tartalmaz.")
