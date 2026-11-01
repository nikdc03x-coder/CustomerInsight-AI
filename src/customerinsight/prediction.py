"""Predictive customer intelligence: Repeat purchase propensity, churn risk, and CLV."""

from typing import Any

import numpy as np
import pandas as pd


def assess_predictive_eligibility(df: pd.DataFrame) -> dict[str, Any]:
    """Verify whether a dataset meets the mathematical preconditions for predictive recurrence modeling."""
    if "order_date" not in df or "customer_id" not in df:
        return {
            "eligible": False,
            "reason": "Dataset is missing customer_id or order_date columns.",
            "total_days": 0,
            "repeat_customers_pct": 0.0,
        }

    valid = df.loc[df["order_date"].notna() & df["customer_id"].notna()].copy()
    if valid.empty:
        return {
            "eligible": False,
            "reason": "No valid transaction dates available.",
            "total_days": 0,
            "repeat_customers_pct": 0.0,
        }

    first_date = valid["order_date"].min()
    last_date = valid["order_date"].max()
    total_days = (last_date - first_date).days

    cust_orders = valid.groupby("customer_id")["order_id"].nunique()
    repeat_rate = (cust_orders > 1).mean() * 100

    if total_days < 45:
        return {
            "eligible": False,
            "reason": f"Insufficient time horizon ({total_days} days). Minimum 45 days required for recurrence modeling.",
            "total_days": total_days,
            "repeat_customers_pct": round(repeat_rate, 2),
        }

    if repeat_rate < 5.0:
        return {
            "eligible": False,
            "reason": f"Insufficient repeat purchase behavior ({repeat_rate:.1f}% repeat customers).",
            "total_days": total_days,
            "repeat_customers_pct": round(repeat_rate, 2),
        }

    return {
        "eligible": True,
        "reason": "Dataset meets temporal and recurrence requirements.",
        "total_days": total_days,
        "repeat_customers_pct": round(repeat_rate, 2),
    }


def predict_customer_recurrence_and_clv(
    df: pd.DataFrame,
    projection_days: int = 90,
    reference_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Estimate customer churn risk, expected future transactions, and projected Customer Lifetime Value.

    Uses an empirical Bayesian recurrence formulation:
    - Calculates customer transaction span, frequency of repeat orders, and monetary averages.
    - Estimates P(Active) based on elapsed inactivity relative to personal cadence.
    - Projects expected purchases over projection_days (default 90 days).
    - Shrinks monetary estimates toward cohort averages to prevent extreme outlier overfitting.
    """
    if "order_date" not in df or "customer_id" not in df:
        return pd.DataFrame(columns=[
            "customer_id", "frequency", "p_active", "churn_risk",
            "expected_orders_90d", "predicted_spend_90d",
        ])

    temp = df.loc[df["order_date"].notna() & df["customer_id"].notna() & df["customer_id"].ne("")].copy()
    if "line_total" not in temp:
        temp["line_total"] = temp["quantity"] * temp["unit_price"]

    temp = temp.loc[temp["line_total"] > 0].copy()
    if temp.empty:
        return pd.DataFrame(columns=[
            "customer_id", "frequency", "p_active", "churn_risk",
            "expected_orders_90d", "predicted_spend_90d",
        ])

    max_date = temp["order_date"].max()
    ref = pd.Timestamp(reference_date).normalize() if reference_date else max_date.normalize() + pd.Timedelta(days=1)

    # 1. Aggregate customer history: first order, last order, unique orders, total spend
    summary = (
        temp.groupby("customer_id")
        .agg(
            first_order=("order_date", "min"),
            last_order=("order_date", "max"),
            orders=("order_id", "nunique"),
            total_spend=("line_total", "sum"),
        )
        .reset_index()
    )

    summary["tenure_days"] = (ref - summary["first_order"].dt.normalize()).dt.days.clip(lower=1)
    summary["recency_days"] = (ref - summary["last_order"].dt.normalize()).dt.days.clip(lower=0)
    summary["historical_aov"] = (summary["total_spend"] / summary["orders"]).round(2)

    # Cohort global mean AOV for Bayesian shrinkage
    global_mean_aov = summary["historical_aov"].median()

    # 2. Probability of Being Active P(Active):
    # Compares recency (inactivity) to the customer's average expected purchase interval
    avg_interval = summary["tenure_days"] / summary["orders"].clip(lower=1)
    relative_lapse = summary["recency_days"] / avg_interval.clip(lower=1)

    # Exponential decay based on lapse ratio
    # If recency is <= personal interval, P(Active) ~ 0.85-0.95
    # If recency is 3x personal interval, P(Active) drops below 0.30
    p_active = 1.0 / (1.0 + np.exp(relative_lapse - 1.5))
    summary["p_active"] = p_active.round(3)

    # 3. Categorize Churn Risk
    conditions = [
        summary["p_active"] >= 0.70,
        summary["p_active"] >= 0.40,
    ]
    choices = ["Low Risk (Active)", "Medium Risk (Slowing)"]
    summary["churn_risk"] = np.select(conditions, choices, default="High Risk (At-Risk / Lapsed)")

    # 4. Expected Future Transactions in projection period
    # Baseline purchase rate lambda = orders / tenure
    daily_rate = summary["orders"] / summary["tenure_days"]
    expected_orders = summary["p_active"] * (daily_rate * projection_days)
    summary[f"expected_orders_{projection_days}d"] = expected_orders.round(2)

    # 5. Bayesian Shrunk Expected Monetary Value
    # Weight m_i with global prior to prevent 1-order high-spend distortion
    shrinkage_weight = summary["orders"] / (summary["orders"] + 3.0)
    shrunk_aov = (shrinkage_weight * summary["historical_aov"]) + ((1.0 - shrinkage_weight) * global_mean_aov)

    # 6. Projected Spend (CLV for period)
    summary[f"predicted_spend_{projection_days}d"] = (
        summary[f"expected_orders_{projection_days}d"] * shrunk_aov
    ).round(2)

    cols = [
        "customer_id",
        "orders",
        "recency_days",
        "tenure_days",
        "p_active",
        "churn_risk",
        f"expected_orders_{projection_days}d",
        f"predicted_spend_{projection_days}d",
    ]
    return summary[cols].sort_values(f"predicted_spend_{projection_days}d", ascending=False).reset_index(drop=True)
