"""Services layer for CustomerInsight AI.

This package groups higher‑level orchestration functions that combine
analytics, data loading, and UI helpers. Keeping them in a dedicated
module makes the architecture clear and isolates business‑logic
services from low‑level utilities.
"""

from __future__ import annotations

# Re‑export key service functions so existing imports continue to work.
# The actual implementations live in the original modules.
from ..dashboard_audit import audit_dashboard
from ..insights_engine import generate_business_insights, BusinessInsight
from ..analytics import (
    calculate_rfm,
    get_revenue_kpis,
    get_revenue_trend,
    get_revenue_by_country,
    get_top_customers,
    segment_customers,
    compare_segments,
)
from ..products import (
    get_product_rankings,
    get_lowest_performing_products,
    run_market_basket_analysis,
)
from ..prediction import (
    assess_predictive_eligibility,
    predict_customer_recurrence_and_clv,
)

__all__ = [
    "audit_dashboard",
    "generate_business_insights",
    "BusinessInsight",
    "calculate_rfm",
    "get_revenue_kpis",
    "get_revenue_trend",
    "get_revenue_by_country",
    "get_top_customers",
    "segment_customers",
    "compare_segments",
    "get_product_rankings",
    "get_lowest_performing_products",
    "run_market_basket_analysis",
    "assess_predictive_eligibility",
    "predict_customer_recurrence_and_clv",
]

