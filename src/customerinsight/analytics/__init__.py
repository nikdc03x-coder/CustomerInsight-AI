"""Analytics subpackage for CustomerInsight AI.
Provides revenue, RFM, segmentation utilities, and product analysis.
Exports core analytics functions directly from the implementation module.
"""

# Re-export core analytics symbols from the implementation module.
from .analytics import (
    calculate_rfm,
    get_revenue_kpis,
    get_revenue_trend,
    get_revenue_by_country,
    get_top_customers,
    segment_customers,
    compare_segments,
)

# Market‑basket analysis lives in the ``products`` sub‑package.
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

