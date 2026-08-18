"""Coordinator plus two specialists. Lane choice is learned, not hardcoded forever."""

from __future__ import annotations

import json
from typing import Any

from sail.bus import InProcessBus
from sail.engine import ImprovementEngine, Interaction
from sail.envelope import Envelope, LANE_HUMAN, LANE_STRUCTURED, MessagePart, new_id
from sail.lanes import decode, encode
from sail.memory import VectorMemory
from sail.selector import LaneSelector

ANALYZER = "analyzer"
PLANNER = "planner"
COORDINATOR = "coordinator"

_ANALYZE_HINTS = ("analyz", "count", "signal", "metric", "number", "adat", "elemz")
_PLAN_HINTS = ("plan", "delegat", "design", "goal", "terv", "lépés", "lepes")


def classify_task(text: str) -> tuple[str, str]:
    """Return (task_kind, recipient). Heuristic only; memory can override recipient."""
    low = text.lower()
    if any(h in low for h in _ANALYZE_HINTS):
        return "analyze", ANALYZER
    if any(tok in low for tok in ("vector", "temperature", "cpu", "load")):
        return "signal", ANALYZER
    if any(h in low for h in _PLAN_HINTS):
        return "plan", PLANNER
    return "concept", PLANNER


def native_payload(task_kind: str, lane: str, text: str) -> Any:
    if lane == "express":
        # Compact numeric sketch of the request (length + char codes), not a model.
        codes = [float(len(text))]
        for ch in text[:7]:
            codes.append(float(ord(ch) % 97))
        return tuple(codes)
    if lane == "semantic":
        return text
    if lane == LANE_STRUCTURED:
        kind_concept = {"analyze": "measurement", "signal": "signal", "plan": "plan", "concept": "concept"}
        return {
            "goal": text,
            "concepts": [kind_concept.get(task_kind, "concept"), "task"],
            "relations": [{"src": "task", "dst": kind_concept.get(task_kind, "concept"), "type": "is"}],
        }
    return text


def _ok_reply(incoming: Envelope, sender: str, body: str) -> Envelope:
    return Envelope(
        role="agent",
        lane=LANE_HUMAN,
        parts=(MessagePart("text/plain", body),),
        sender=sender,
        recipient=incoming.sender,
        task_kind=incoming.task_kind,
        task_id=incoming.task_id,
        context_id=incoming.context_id,
        metadata=(("ok", "1"),),
    )


def _err_reply(incoming: Envelope, sender: str, body: str) -> Envelope:
    return Envelope(
        role="agent",
        lane=LANE_HUMAN,
        parts=(MessagePart("text/plain", body),),
        sender=sender,
        recipient=incoming.sender,
        task_kind=incoming.task_kind,
        task_id=incoming.task_id,
        context_id=incoming.context_id,
        metadata=(("ok", "0"),),
    )


class AnalyzerAgent:
    """Accepts express / semantic / structured; rejects unconstrained human for signals."""

    name = ANALYZER

    def handle(self, message: Envelope) -> Envelope:
        try:
            payload = decode(message.lane, message.primary())
        except (TypeError, ValueError, json.JSONDecodeError, KeyError):
            return _err_reply(message, self.name, "parse-failed")
        if message.lane == LANE_HUMAN:
            return _err_reply(message, self.name, "human-lane-rejected")
        return _ok_reply(message, self.name, f"analyzed:{message.lane}:{_brief(payload)}")


class PlannerAgent:
    """Needs a structured goal (or semantic concept). Human text is treated as ambiguous."""

    name = PLANNER

    def handle(self, message: Envelope) -> Envelope:
        try:
            payload = decode(message.lane, message.primary())
        except (TypeError, ValueError, json.JSONDecodeError, KeyError):
            return _err_reply(message, self.name, "parse-failed")
        if message.lane == LANE_HUMAN:
            return _err_reply(message, self.name, "human-lane-ambiguous")
        if message.lane == LANE_STRUCTURED:
            if not isinstance(payload, dict) or not payload.get("goal"):
                return _err_reply(message, self.name, "missing-goal")
        return _ok_reply(message, self.name, f"planned:{message.lane}:{_brief(payload)}")


def _brief(payload: Any) -> str:
    text = repr(payload)
    return text if len(text) <= 80 else text[:77] + "..."


class CoordinatorAgent:
    def __init__(
        self,
        bus: InProcessBus,
        selector: LaneSelector,
        memory: VectorMemory,
        engine: ImprovementEngine,
        *,
        explore: bool = True,
    ) -> None:
        self.bus = bus
        self.selector = selector
        self.memory = memory
        self.engine = engine
        self.explore = explore
        bus.register(COORDINATOR, self.handle)

    def handle(self, message: Envelope) -> Envelope:
        """Inbound user envelope: classify, pick lane, delegate, learn."""
        text = _user_text(message)
        return self.run(text, context_id=message.context_id, task_id=message.task_id)

    def run(self, text: str, *, context_id: str | None = None, task_id: str | None = None) -> Envelope:
        task_kind, recipient = classify_task(text)
        near = self.memory.nearest(text, k=1, success_only=True)
        if near and near[0][0] >= 0.55:
            recipient = near[0][1].recipient or recipient
            task_kind = near[0][1].task_kind or task_kind
        lane = self.selector.choose(task_kind, explore=self.explore)
        payload = native_payload(task_kind, lane, text)
        part = encode(lane, payload)
        outgoing = Envelope(
            role="user",
            lane=lane,
            parts=(part,),
            sender=COORDINATOR,
            recipient=recipient,
            task_kind=task_kind,
            task_id=task_id or new_id(),
            context_id=context_id or new_id(),
        )
        t0 = _now_ms()
        try:
            reply = self.bus.send(outgoing)
            parse_ok = True
        except Exception as exc:  # noqa: BLE001 — bus/handler failures become a failed interaction
            parse_ok = False
            reply = _err_reply(outgoing, recipient, f"bus:{type(exc).__name__}")
        elapsed = _now_ms() - t0
        success = reply.meta_dict().get("ok") == "1"
        self.engine.record(
            Interaction(
                task_kind=task_kind,
                lane=lane,
                payload=payload,
                text=text,
                recipient=recipient,
                success=success,
                parse_ok=parse_ok,
                bytes_len=_part_size(part),
                elapsed_ms=elapsed,
            )
        )
        return reply


def _user_text(message: Envelope) -> str:
    data = message.primary().data
    if isinstance(data, str):
        return data
    return repr(data)


def _part_size(part: MessagePart) -> int:
    data = part.data
    if isinstance(data, bytes):
        return len(data)
    if isinstance(data, str):
        return len(data.encode("utf-8"))
    return len(repr(data))


def _now_ms() -> float:
    import time

    return time.perf_counter() * 1000.0
