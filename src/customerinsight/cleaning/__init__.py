"""Cleaning subpackage for CustomerInsight AI.
Provides data cleaning utilities.
"""

# Re‑export core cleaning functions for backward compatibility
from .cleaning import (
    audit_data_quality,
    clean_canonical_transactions,
    CleaningSummary,
)

__all__ = [
    "audit_data_quality",
    "clean_canonical_transactions",
    "CleaningSummary",
]

