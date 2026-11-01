"""Generalised customer and revenue analytics across datasets."""

from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def calculate_rfm(
    df: pd.DataFrame,
    reference_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Calculate Recency, Frequency, and Monetary features for each customer.

    Requires canonical columns: customer_id, order_id, order_date, line_total (or quantity & unit_price).
    """
    if "customer_id" not in df.columns or "order_id" not in df.columns or "order_date" not in df.columns:
        raise ValueError("DataFrame missing required columns for RFM calculation.")

    valid = df.loc[df["customer_id"].notna() & df["customer_id"].ne("")].copy()
    valid = valid.loc[valid["order_id"].notna() & valid["order_id"].ne("")].copy()
    valid = valid.loc[valid["order_date"].notna()].copy()

    if "line_total" not in valid.columns:
        valid["line_total"] = valid["quantity"] * valid["unit_price"]

    # Filter for positive monetary transactions
    valid = valid.loc[valid["line_total"] > 0].copy()

    if valid.empty:
        raise ValueError("No valid customer transactions available for RFM calculation.")

    latest_date = valid["order_date"].max()
    if reference_date is None:
        ref = latest_date.normalize() + pd.Timedelta(days=1)
    else:
        ref = pd.Timestamp(reference_date).normalize()

    rfm = (
        valid.groupby("customer_id")
        .agg(
            last_order=("order_date", "max"),
            frequency=("order_id", "nunique"),
            monetary=("line_total", "sum"),
        )
        .reset_index()
    )

    rfm["recency"] = (ref - rfm["last_order"].dt.normalize()).dt.days.astype("int64")
    rfm["frequency"] = rfm["frequency"].astype("int64")
    rfm["monetary"] = rfm["monetary"].round(2)

    return rfm[["customer_id", "recency", "frequency", "monetary"]].sort_values("customer_id").reset_index(drop=True)


def get_revenue_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Calculate core revenue and activity summary metrics."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_orders": 0,
            "total_customers": 0,
            "average_order_value": 0.0,
            "average_customer_spend": 0.0,
            "first_order_date": None,
            "last_order_date": None,
            "currency": "GBP",
        }

    spend_col = "line_total" if "line_total" in df else None
    if spend_col is None and "quantity" in df and "unit_price" in df:
        df = df.copy()
        df["line_total"] = df["quantity"] * df["unit_price"]
        spend_col = "line_total"

    total_revenue = float(df[spend_col].sum()) if spend_col else 0.0
    total_orders = int(df["order_id"].nunique()) if "order_id" in df else 0
    total_customers = int(df["customer_id"].dropna().nunique()) if "customer_id" in df else 0
    aov = (total_revenue / total_orders) if total_orders > 0 else 0.0
    avg_cust_spend = (total_revenue / total_customers) if total_customers > 0 else 0.0

    first_date = df["order_date"].min() if "order_date" in df else None
    last_date = df["order_date"].max() if "order_date" in df else None
    currency = str(df["currency"].dropna().iloc[0]) if "currency" in df and not df["currency"].dropna().empty else "GBP"

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "total_customers": total_customers,
        "average_order_value": round(aov, 2),
        "average_customer_spend": round(avg_cust_spend, 2),
        "first_order_date": first_date,
        "last_order_date": last_date,
        "currency": currency,
    }


def get_revenue_trend(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """Group transactions by periodic interval and calculate revenue timeline."""
    if "order_date" not in df or df["order_date"].dropna().empty:
        return pd.DataFrame(columns=["period", "revenue", "orders", "active_customers", "average_order_value"])

    temp = df.loc[df["order_date"].notna()].copy()
    if "line_total" not in temp:
        temp["line_total"] = temp["quantity"] * temp["unit_price"]

    temp["period"] = temp["order_date"].dt.to_period(freq).dt.to_timestamp()

    trend = (
        temp.groupby("period")
        .agg(
            revenue=("line_total", "sum"),
            orders=("order_id", "nunique"),
            active_customers=("customer_id", "nunique"),
        )
        .reset_index()
        .sort_values("period")
    )

    trend["average_order_value"] = (trend["revenue"] / trend["orders"]).replace(np.nan, 0).round(2)
    trend["revenue"] = trend["revenue"].round(2)
    return trend


def get_revenue_by_country(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Aggregate gross revenue by geographic location."""
    if "country" not in df or df["country"].dropna().empty:
        return pd.DataFrame(columns=["country", "revenue", "orders", "customers", "revenue_share_pct"])

    temp = df.loc[df["country"].notna()].copy()
    if "line_total" not in temp:
        temp["line_total"] = temp["quantity"] * temp["unit_price"]

    total_revenue = temp["line_total"].sum()

    grouped = (
        temp.groupby("country")
        .agg(
            revenue=("line_total", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    grouped["revenue_share_pct"] = ((grouped["revenue"] / total_revenue) * 100).round(2) if total_revenue > 0 else 0
    grouped["revenue"] = grouped["revenue"].round(2)
    return grouped.head(top_n)


def get_top_customers(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """List the highest-spending customers with purchase counts and average order size."""
    if "customer_id" not in df or df["customer_id"].dropna().empty:
        return pd.DataFrame(columns=["customer_id", "total_spend", "orders", "aov", "last_order"])

    temp = df.loc[df["customer_id"].notna()].copy()
    if "line_total" not in temp:
        temp["line_total"] = temp["quantity"] * temp["unit_price"]

    top = (
        temp.groupby("customer_id")
        .agg(
            total_spend=("line_total", "sum"),
            orders=("order_id", "nunique"),
            last_order=("order_date", "max"),
        )
        .reset_index()
        .sort_values("total_spend", ascending=False)
    )

    top["aov"] = (top["total_spend"] / top["orders"]).round(2)
    top["total_spend"] = top["total_spend"].round(2)
    return top.head(top_n).reset_index(drop=True)


def segment_customers(rfm: pd.DataFrame, n_clusters: int = 4, random_state: int = 42) -> pd.DataFrame:
    """Segment customers using log1p + StandardScaler K-Means and assign descriptive personas."""
    if len(rfm) < n_clusters:
        result = rfm.copy()
        result["cluster"] = 0
        result["segment_name"] = "All Customers"
        return result

    features = rfm[["recency", "frequency", "monetary"]].copy()
    scaled = StandardScaler().fit_transform(np.log1p(features))

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(scaled)

    result = rfm.copy()
    result["cluster"] = labels

    # Order clusters by monetary spend descending to produce standard persona tiers
    medians = (
        result.groupby("cluster")["monetary"]
        .median()
        .sort_values(ascending=False)
    )

    # Standard persona naming template based on spending ranking
    rank_names = [
        "High-Value Champions",
        "Loyal Frequent Shoppers",
        "Recent Moderate Buyers",
        "At-Risk / Lapsed Buyers",
        "Occasional Infrequent",
    ]

    cluster_to_name = {}
    for rank, cluster_id in enumerate(medians.index):
        name = rank_names[rank] if rank < len(rank_names) else f"Cluster {chr(65 + rank)}"
        cluster_to_name[cluster_id] = name

    result["segment_name"] = result["cluster"].map(cluster_to_name)
    return result


def compare_segments(segmented: pd.DataFrame) -> pd.DataFrame:
    """Summarize customer counts, medians, and total revenue across segments."""
    total_spend = segmented["monetary"].sum()
    total_customers = len(segmented)

    summary = (
        segmented.groupby(["cluster", "segment_name"])
        .agg(
            customers=("customer_id", "count"),
            median_recency=("recency", "median"),
            median_frequency=("frequency", "median"),
            median_monetary=("monetary", "median"),
            total_spend=("monetary", "sum"),
        )
        .reset_index()
        .sort_values("total_spend", ascending=False)
    )

    summary["customer_share_pct"] = ((summary["customers"] / total_customers) * 100).round(2)
    summary["revenue_share_pct"] = ((summary["total_spend"] / total_spend) * 100).round(2) if total_spend > 0 else 0.0
    summary["total_spend"] = summary["total_spend"].round(2)

    return summary
