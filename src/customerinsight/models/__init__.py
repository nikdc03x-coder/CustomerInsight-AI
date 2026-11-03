"""Models subpackage for CustomerInsight AI.

Contains predictive and clustering model implementations. The public API
remains available from the top‑level package via ``customerinsight``
re‑exports.
"""

from __future__ import annotations

# Re‑export symbols from the concrete implementation modules so that
# ``import customerinsight.models`` provides a flat namespace.
from .prediction import assess_predictive_eligibility, predict_customer_recurrence_and_clv
from .clustering import *  # noqa: F403,F401 – expose clustering utilities

__all__ = [
    "assess_predictive_eligibility",
    "predict_customer_recurrence_and_clv",
    # clustering exports are added dynamically via wildcard import
]

