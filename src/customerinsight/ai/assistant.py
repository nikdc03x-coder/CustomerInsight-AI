"""Assistant module for CustomerInsight AI.

This file re‑exports the original implementation from ``ai_assistant.py``
so that ``customerinsight.ai`` provides a clean namespace while keeping the
original code unchanged.
"""

from __future__ import annotations

# Import the full implementation; the name ``ai_assistant`` remains the
# original module file in the project root.
from ..ai_assistant import (
    format_currency_symbol,
    AssistantResponse,
    TOOL_REGISTRY,
    ask_assistant,
    tool_dataset_summary,
    tool_top_customers,
    tool_revenue_by_segment,
    tool_average_order_value,
    tool_product_performance,
    tool_product_associations,
    tool_customer_inactivity,
    tool_customer_profile,
)

__all__ = [
    "format_currency_symbol",
    "AssistantResponse",
    "TOOL_REGISTRY",
    "ask_assistant",
    "tool_dataset_summary",
    "tool_top_customers",
    "tool_revenue_by_segment",
    "tool_average_order_value",
    "tool_product_performance",
    "tool_product_associations",
    "tool_customer_inactivity",
    "tool_customer_profile",
]

