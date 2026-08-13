"""Compile-time feature flags. F1+ / HU-EU-US LOCK tenancy."""

# FR-470. Do not set True in this package. F2 live CDS is a later binary flag
# after CE / in-house / [Ya] — not a runtime toggle here.
LIVE_CDS: bool = False
