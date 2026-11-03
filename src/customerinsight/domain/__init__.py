"""Domain package for CustomerInsight AI.

Exports schema utilities and related domain objects. Keeping the definitions
in a dedicated namespace clarifies the separation between data contracts
and higher‑level services.
"""

from __future__ import annotations

# Re‑export symbols from the existing ``schema`` module so that external
# imports continue to work (e.g. ``from customerinsight.domain import CANONICAL_FIELDS``).
from ..schema import (
    CANONICAL_FIELDS,
    detect_column_mappings,
    coerce_canonical_types,
    assess_capabilities,
)

__all__ = [
    "CANONICAL_FIELDS",
    "detect_column_mappings",
    "coerce_canonical_types",
    "assess_capabilities",
]

