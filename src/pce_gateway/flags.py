"""Compile-time feature flags. F1+ / HU-EU-US LOCK tenancy."""

# FR-470. Do not set True in this package. The F2 pipe (`pce_cds`) exists;
# this flag is the lock. Flip only in a signed release after CE / in-house / [Ya].
LIVE_CDS: bool = False
