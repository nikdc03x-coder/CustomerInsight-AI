"""Prediction module with lightweight RFM‑based implementations for CLV and churn.

The real production models are out of scope for the current test suite, but the UI
expects concrete data frames with specific columns. This module provides a simple
heuristic based on Recency‑Frequency‑Monetary (RFM) aggregation to compute:

* **Eligibility** – Does the dataset have enough history for forecasting?
* **Recurrence probability** – An empirical estimate of the chance a customer
  will make another purchase within the projection horizon.
* **Projected 90‑day spend** – Expected spend derived from recurrence and average
  order value.
* **Churn risk tier** – Categorical label derived from the recurrence
  probability.

These functions are deliberately lightweight, deterministic, and fully
compatible with the existing UI (`predictive_intelligence.py`).
"""

from __future__ import annotations

import pandas as pd

__all__ = ["assess_predictive_eligibility", "predict_customer_recurrence_and_clv"]


def assess_predictive_eligibility(df: pd.DataFrame, min_days: int = 30, min_repeat_pct: float = 5.0) -> dict:
    """Assess whether the dataset has sufficient history for predictive modeling.

    Heuristics:
    * At least *min_days* of activity span.
    * At least *min_repeat_pct* percent of customers have >1 order.
    Returns a dictionary consumed by the UI.
    """
    if df.empty:
        return {"eligible": False, "reason": "Dataset is empty"}
    # Ensure order_date is datetime
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    if df["order_date"].isna().all():
        return {"eligible": False, "reason": "No valid order_date values"}
    total_days = (df["order_date"].max() - df["order_date"].min()).days
    # Compute repeat customers
    cust_orders = df.groupby("customer_id")["order_id"].nunique()
    repeat_customers = (cust_orders > 1).sum()
    total_customers = cust_orders.size
    repeat_pct = (repeat_customers / total_customers) * 100 if total_customers else 0.0
    eligible = total_days >= min_days and repeat_pct >= min_repeat_pct
    reason = "" if eligible else "Insufficient history or low repeat rate"
    return {
        "eligible": eligible,
        "reason": reason,
        "repeat_customers_pct": repeat_pct,
        "total_days": total_days,
    }


def predict_customer_recurrence_and_clv(df: pd.DataFrame, projection_days: int = 90) -> pd.DataFrame:
    """Compute simple recurrence probabilities and 90‑day CLV forecasts.

    The algorithm aggregates transactions per customer, calculates a recurrence
    probability based on order frequency and recency, and projects spend using
    the average order value. It also assigns a churn‑risk tier.
    """
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    max_date = df["order_date"].max()
    # Aggregate per‑customer
    agg = df.groupby("customer_id").agg(
        recency_days=("order_date", lambda x: (max_date - x.max()).days),
        orders=("order_id", "nunique"),
        monetary=("line_total", "sum"),
    ).reset_index()
    # Simple recurrence probability (higher frequency & more recent = higher)
    agg["p_active"] = (agg["orders"] / (agg["recency_days"] + 1)).clip(upper=1.0)
    # Expected number of orders in projection window (linear scaling)
    agg["expected_orders_90d"] = agg["p_active"] * (projection_days / 30.0) * agg["orders"]
    # Average order value (avoid division by zero)
    agg["avg_order_value"] = agg["monetary"] / agg["orders"].replace(0, 1)
    agg["predicted_spend_90d"] = agg["expected_orders_90d"] * agg["avg_order_value"]
    # Churn risk tier based on probability
    def risk_label(p: float) -> str:
        if p >= 0.6:
            return "Low Risk (Active)"
        if p >= 0.3:
            return "Medium Risk (Slowing)"
        return "High Risk (At-Risk / Lapsed)"
    agg["churn_risk"] = agg["p_active"].apply(risk_label)
    # Return only columns required by the UI
    return agg[[
        "customer_id",
        "churn_risk",
        "p_active",
        "expected_orders_90d",
        "predicted_spend_90d",
        "recency_days",
        "orders",
    ]]
