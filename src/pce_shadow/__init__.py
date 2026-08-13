"""F1s live pairing + phenoconversion. Not imported by pce_report (FR-470)."""

from pce_shadow.engine import infer
from pce_shadow.table import KnowledgeTable, default_table

__all__ = ["KnowledgeTable", "default_table", "infer"]
