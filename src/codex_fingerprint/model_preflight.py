"""Pure helpers for checking and temporarily extending account model mappings."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def mapping_supports(mapping: dict[str, str] | None, model: str) -> bool:
    """Return whether a non empty mapping admits an exact model or a simple wildcard."""
    if not mapping:
        return True  # empty mapping means passthrough/allow all at the platform layer
    if model in mapping:
        return True
    for pattern in mapping:
        if pattern.endswith("*") and model.startswith(pattern[:-1]):
            return True
    return False


def with_identity_mapping(mapping: dict[str, str] | None, model: str) -> dict[str, str]:
    """Return a complete copy with an identity entry, leaving the input untouched."""
    result = deepcopy(mapping or {})
    result[model] = model
    return result


def classify_404(error: str | None) -> str:
    """Tag known platform routing errors for reports before calling them upstream failures."""
    text = (error or "").lower()
    if "not supported by any configured account" in text:
        return "platform_account_mapping"
    if "not available for this group" in text:
        return "platform_group_allowlist"
    return "unknown_404"
