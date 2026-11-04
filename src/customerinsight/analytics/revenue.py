"""Revenue analytics utilities for CustomerInsight AI.

Provides KPI calculations, revenue trends, geographic breakdowns, and top‑customer
ranking based on the canonical transaction schema.
"""

import pandas as pd
import streamlit as st
from typing import Literal
from typing import Literal


def _validate_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned view of accepted (non‑cancellation) transactions.

    The canonical schema includes an ``is_cancellation`` boolean flag.  Cancellations
    are excluded from revenue calculations.  If the column is missing we assume no
    cancellations.
    """
    if "is_cancellation" in df.columns:
        df = df.loc[~df["is_cancellation"]].copy()
    return df


@st.cache_data(show_spinner="Calculating revenue KPIs…")
def get_revenue_kpis(df: pd.DataFrame | None = None) -> dict:
    """Calculate core revenue KPIs.

    Returns a dictionary with the keys required by the test suite:
    ``total_revenue``, ``total_orders``, ``total_customers``,
    ``average_order_value``, ``average_customer_spend`` and ``currency``.
    """
    if df is None:
        return {}
    df = _validate_transactions(df)
    # Gross revenue is the sum of ``line_total`` for accepted orders.
    total_revenue = float(df["line_total"].sum())
    # An order is identified by ``order_id`` – cancellations have been removed.
    total_orders = int(df["order_id"].nunique())
    total_customers = int(df["customer_id"].nunique())
    average_order_value = round(total_revenue / total_orders, 2) if total_orders else 0.0
    # Spend per customer.
    spend_per_customer = df.groupby("customer_id")["line_total"].sum()
    average_customer_spend = round(spend_per_customer.mean(), 2) if not spend_per_customer.empty else 0.0
    currency = df["currency"].iloc[0] if "currency" in df.columns and not df.empty else "GBP"
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "average_order_value": average_order_value,
        "average_customer_spend": average_customer_spend,
        "currency": currency,
    }


@st.cache_data(show_spinner="Calculating revenue trend…")
def get_revenue_trend(df: pd.DataFrame | None = None, freq: Literal["D", "W", "M"] = "M") -> pd.DataFrame:
    """Return revenue aggregated by the given frequency.

    The resulting DataFrame contains columns ``period`` (datetime), ``revenue``
    (float), ``orders`` (int) and ``active_customers`` (int).
    """
    if df is None:
        return pd.DataFrame()
    df = _validate_transactions(df)
    df["period"] = pd.to_datetime(df["order_date"]).dt.to_period(freq).dt.start_time
    agg = df.groupby("period").agg(
        revenue=("line_total", "sum"),
        orders=("order_id", "nunique"),
        active_customers=("customer_id", "nunique"),
    ).reset_index()
    agg["period"] = pd.to_datetime(agg["period"]).dt.normalize()
    return agg


def get_revenue_by_country(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Aggregate revenue, order count and customer count per country.

    Returns a DataFrame sorted by revenue descending and includes a share %.
    """
    if df is None:
        return pd.DataFrame()
    df = _validate_transactions(df)
    agg = df.groupby("country").agg(
        revenue=("line_total", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique"),
    ).reset_index()
    total_rev = agg["revenue"].sum()
    agg["revenue_share_pct"] = (agg["revenue"] / total_rev * 100).round(1) if total_rev else 0.0
    return agg.sort_values("revenue", ascending=False)


def get_top_customers(df: pd.DataFrame | None = None, top_n: int = 10) -> pd.DataFrame:
    """Return the top N customers by total spend.

    Columns: ``customer_id``, ``total_spend``, ``total_orders``,
    ``average_order_value``, ``first_purchase``, ``last_purchase``.
    """
    if df is None:
        return pd.DataFrame()
    df = _validate_transactions(df)
    cust = df.groupby("customer_id").agg(
        total_spend=("line_total", "sum"),
        total_orders=("order_id", "nunique"),
        first_purchase=("order_date", "min"),
        last_purchase=("order_date", "max"),
    )
    cust["average_order_value"] = cust["total_spend"] / cust["total_orders"]
    cust = cust.sort_values("total_spend", ascending=False).head(top_n).reset_index()
    # Convert timestamps to ISO strings for JSON‑friendly output.
    cust["first_purchase"] = pd.to_datetime(cust["first_purchase"]).dt.strftime("%Y-%m-%d")
    cust["last_purchase"] = pd.to_datetime(cust["last_purchase"]).dt.strftime("%Y-%m-%d")
    return cust
