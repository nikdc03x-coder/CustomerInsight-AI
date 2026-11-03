"""Compatibility wrapper for legacy imports.

The older code path expects ``customerinsight.analytics.analytics`` to
expose the core analytics functions. After the refactor the actual
implementations live in ``customerinsight.analytics`` (the package)
and its sub‑modules. This file re‑exports those symbols so existing
imports continue to work.
"""

# Direct imports from implementation modules – avoid circular imports.
# NOTE: If any of these symbols move to a different module, update the import path here.
from .rfm import calculate_rfm
from .revenue import (
    get_revenue_kpis,
    get_revenue_trend,
    get_revenue_by_country,
    get_top_customers,
)
from .segmentation import (
    segment_customers,
    compare_segments,
)

# Market‑basket analysis lives in the ``products`` sub‑package
from ..products import run_market_basket_analysis

__all__ = [
    "calculate_rfm",
    "get_revenue_kpis",
    "get_revenue_trend",
    "get_revenue_by_country",
    "get_top_customers",
    "segment_customers",
    "compare_segments",
    "run_market_basket_analysis",
]

