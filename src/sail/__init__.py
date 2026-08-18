"""SAIL: Self-improving Agent Interchange Language (experimental sandbox).

Isolated from PCE clinical modules. Stdlib-only by default. Not a medical
device component, not an ACP implementation (ACP merged into A2A in 2025).
"""

from sail.envelope import Envelope, MessagePart
from sail.lanes import LANES, decode, encode
from sail.memory import VectorMemory, embed
from sail.selector import LaneSelector
from sail.engine import ImprovementEngine, Interaction
from sail.bus import InProcessBus
from sail.agents import AnalyzerAgent, CoordinatorAgent, PlannerAgent

__all__ = [
    "AnalyzerAgent",
    "CoordinatorAgent",
    "Envelope",
    "ImprovementEngine",
    "InProcessBus",
    "Interaction",
    "LANES",
    "LaneSelector",
    "MessagePart",
    "PlannerAgent",
    "VectorMemory",
    "decode",
    "embed",
    "encode",
]
