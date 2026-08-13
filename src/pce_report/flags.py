"""F1+ clinical renderer flags. Matcher stays off. No live CDS on this path."""

# FR-300 / FR-470. Do not set True in this package.
MATCHER_ON: bool = False

# Renderer must never import or call the shadow matcher.
LIVE_CDS: bool = False
