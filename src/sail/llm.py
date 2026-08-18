"""Optional DSPy hook. Not imported by the default SAIL path or CI."""

from __future__ import annotations


def require_dspy():
    try:
        import dspy  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "SAIL LLM extra is not installed. "
            "Default SAIL is stdlib-only; optional extra: dspy (see docs/sail/README.md)"
        ) from exc
    import dspy

    return dspy
