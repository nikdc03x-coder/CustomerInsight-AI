"""Lightweight business‑insights engine.

The production version performs sophisticated statistical analysis. For the
current repository we provide a minimal, deterministic implementation that
generates a few representative insights from the canonical transaction data.
These insights are sufficient for the Streamlit *Business Insights Engine*
page to display meaningful information.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["generate_business_insights", "BusinessInsight"]


class BusinessInsight:
    """Container for a single insight.

    Attributes
    ----------
    title : str
        Short headline for the insight.
    category : str
        Broad group (e.g., "Revenue", "Churn", "Retention").
    priority : str
        One of "High", "Medium", "Low" – used for badge colour.
    observation : str
        Human‑readable description of the finding.
    supporting_metric : str
        Metric or statistic that backs the observation.
    business_impact : str
        Narrative of the potential impact on the business.
    recommended_action : str
        Actionable recommendation for the user.
    limitations : str
        Known caveats of the heuristic.
    """

    def __init__(
        self,
        title: str = "",
        category: str = "General",
        priority: str = "Low",
        observation: str = "",
        supporting_metric: str = "",
        business_impact: str = "",
        recommended_action: str = "",
        limitations: str = "",
    ) -> None:
        self.title = title
        self.category = category
        self.priority = priority
        self.observation = observation
        self.supporting_metric = supporting_metric
        self.business_impact = business_impact
        self.recommended_action = recommended_action
        self.limitations = limitations

    def __repr__(self) -> str:
        return (
            f"BusinessInsight(title={self.title!r}, category={self.category!r}, "
            f"priority={self.priority!r})"
        )


def _revenue_concentration(df: pd.DataFrame) -> BusinessInsight:
    # Top 10 % of customers by spend
    spend = df.groupby("customer_id")["line_total"].sum()
    top_threshold = spend.quantile(0.90)
    top_spend = spend[spend >= top_threshold].sum()
    total_spend = spend.sum()
    pct = (top_spend / total_spend * 100) if total_spend else 0.0
    return BusinessInsight(
        title="Revenue concentration in top 10 % customers",
        category="Revenue",
        priority="High",
        observation=f"The top 10 % of customers generate {pct:.1f}% of total revenue.",
        supporting_metric=f"{pct:.1f}% of revenue from {len(spend[spend >= top_threshold])} customers",
        business_impact="High dependence on a small cohort makes revenue vulnerable to churn.",
        recommended_action="Target retention campaigns at the identified high‑value customers.",
        limitations="Based on historic spend only; does not consider future growth potential.",
    )


def _churn_risk(df: pd.DataFrame) -> BusinessInsight:
    # Customers with no purchase in the last 180 days are considered at risk
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=180)
    last_purchase = df.groupby("customer_id")["order_date"].max()
    at_risk = last_purchase[last_purchase <= cutoff]
    pct = (len(at_risk) / len(last_purchase) * 100) if len(last_purchase) else 0.0
    return BusinessInsight(
        title="Potential churn risk based on inactivity",
        category="Churn",
        priority="Medium",
        observation=f"{pct:.1f}% of customers have not purchased in the last 180 days.",
        supporting_metric=f"{len(at_risk)} of {len(last_purchase)} customers inactive",
        business_impact="Inactive customers may represent lost revenue if not re‑engaged.",
        recommended_action="Run win‑back email/SMS campaigns for the inactive cohort.",
        limitations="Simple inactivity rule; does not account for seasonality or intentional gaps.",
    )


def _single_order_retention(df: pd.DataFrame) -> BusinessInsight:
    cust_orders = df.groupby("customer_id")["order_id"].nunique()
    single_order = (cust_orders == 1).sum()
    pct = (single_order / len(cust_orders) * 100) if len(cust_orders) else 0.0
    return BusinessInsight(
        title="Low repeat‑purchase rate",
        category="Retention",
        priority="Low",
        observation=f"{pct:.1f}% of customers have only a single order.",
        supporting_metric=f"{single_order} of {len(cust_orders)} customers",
        business_impact="Opportunities to increase lifetime value through repeat purchases.",
        recommended_action="Introduce loyalty incentives for first‑time buyers.",
        limitations="Does not differentiate between new vs. mature customers.",
    )


def generate_business_insights(df: pd.DataFrame | None = None, rfm: pd.DataFrame | None = None) -> list[BusinessInsight]:
    """Generate a small set of deterministic insights.

    The function accepts a DataFrame of transactions (the same schema used
    throughout the app). If ``df`` is ``None`` or empty, an empty list is
    returned.
    """
    if df is None or df.empty:
        return []
    # Ensure required columns exist
    required = {"customer_id", "order_id", "order_date", "line_total"}
    if not required.issubset(set(df.columns)):
        return []
    insights: list[BusinessInsight] = []
    insights.append(_revenue_concentration(df))
    insights.append(_churn_risk(df))
    insights.append(_single_order_retention(df))
    return insights
