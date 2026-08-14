"""F2 CDS Hooks pipe (FR-520). Separate process from pce_clinical / pce_report.

LIVE_CDS in this repo is False. The pipe exists; the prescriber path is off
until a signed release flips the compile-time flag. Tests pass live_cds= into
the hook handler; they do not mutate the constant.
"""

from pce_cds.cards import build_cards, live_discovery, lock_discovery
from pce_cds.policy import IIA_SAFE_BLOCK

__all__ = ["IIA_SAFE_BLOCK", "build_cards", "live_discovery", "lock_discovery"]
