"""Evidence-backed deterministic business insight generator."""

from dataclasses import dataclass, asdict
from typing import Any

import pandas as pd

from customerinsight.analytics import calculate_rfm, get_revenue_kpis, segment_customers, compare_segments
from customerinsight.products import run_market_basket_analysis


@dataclass
class BusinessInsight:
    category: str
    priority: str  # High, Medium, Low
    title: str
    observation: str
    supporting_metric: str
    business_impact: str
    recommended_action: str
    limitations: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def generate_business_insights(
    df: pd.DataFrame,
    rfm: pd.DataFrame | None = None,
    currency: str = "GBP",
) -> list[BusinessInsight]:
    """Generate evidence-grounded strategic insights from actual customer and transaction metrics."""
    insights: list[BusinessInsight] = []
    if df.empty:
        return insights

    if rfm is None or rfm.empty:
        try:
            rfm = calculate_rfm(df)
        except Exception:
            return insights

    kpis = get_revenue_kpis(df)
    total_revenue = kpis["total_revenue"]
    total_customers = len(rfm)

    # 1. Revenue Concentration (Pareto Principle Analysis)
    if total_customers > 10 and total_revenue > 0:
        sorted_rfm = rfm.sort_values("monetary", ascending=False)
        top_10_pct_count = max(1, int(total_customers * 0.10))
        top_10_spend = sorted_rfm.iloc[:top_10_pct_count]["monetary"].sum()
        top_10_pct_share = round((top_10_spend / total_revenue) * 100, 1)

        if top_10_pct_share >= 50.0:
            insights.append(BusinessInsight(
                category="Revenue Risk",
                priority="High",
                title="Extreme Revenue Concentration in Top 10% of Customers",
                observation=(
                    f"The top 10% of customers ({top_10_pct_count:,} accounts) generate {top_10_pct_share}% "
                    f"(£{top_10_spend:,.2f}) of your total recorded gross revenue."
                ),
                supporting_metric=f"{top_10_pct_share}% revenue from top 10% of customer base",
                business_impact="High vulnerability to key-account churn; losing a few top buyers would severely reduce topline cash flow.",
                recommended_action="Establish an executive VIP concierge program and dedicated relationship management for the top tier.",
                limitations="Gross spending excludes returns and credit notes. Wholesale transactions can inflate customer concentration.",
            ))

    # 2. High-Value Inactivity / Churn Alert
    if len(rfm) >= 20:
        high_value_threshold = rfm["monetary"].quantile(0.75)
        high_value_inactive = rfm.loc[(rfm["monetary"] >= high_value_threshold) & (rfm["recency"] > 90)]
        inactive_count = len(high_value_inactive)
        inactive_spend = high_value_inactive["monetary"].sum()

        if inactive_count > 0:
            insights.append(BusinessInsight(
                category="Customer Retention",
                priority="High",
                title=f"{inactive_count} High-Value Customers At Risk of Churn",
                observation=(
                    f"{inactive_count:,} top-quartile spenders (spend > £{high_value_threshold:,.2f}) have had no "
                    f"recorded purchases in over 90 days. Historically they accounted for £{inactive_spend:,.2f}."
                ),
                supporting_metric=f"£{inactive_spend:,.2f} historical spend at lapse risk across {inactive_count} accounts",
                business_impact="Preventable revenue leakage from proven, previously loyal buyers.",
                recommended_action="Deploy automated personalized win-back outreach offering exclusive incentives or account check-ins.",
                limitations="Inactivity is measured against the latest dataset reference date, not real-time calendar dates.",
            ))

    # 3. Single-Purchase Customer Retention Opportunity
    if total_customers > 10:
        one_time_buyers = rfm.loc[rfm["frequency"] == 1]
        one_time_pct = round((len(one_time_buyers) / total_customers) * 100, 1)

        if one_time_pct >= 30.0:
            insights.append(BusinessInsight(
                category="Acquisition & Activation",
                priority="Medium",
                title="High Proportion of Single-Purchase Buyers",
                observation=(
                    f"{len(one_time_buyers):,} customers ({one_time_pct}% of total base) have only purchased once "
                    f"throughout the recorded dataset history."
                ),
                supporting_metric=f"{one_time_pct}% of customers have exactly 1 order",
                business_impact="Customer acquisition costs (CAC) are not being amortized over repeat transactions.",
                recommended_action="Introduce an automated post-purchase email onboarding sequence 14–30 days after first purchase.",
                limitations="Customers who joined near the end of the data collection window may not have had time to make a second purchase.",
            ))

    # 4. Market Basket Cross-Sell Opportunity
    try:
        rules = run_market_basket_analysis(df, min_support=0.015, min_confidence=0.15, min_lift=1.5, max_rules=5)
        if not rules.empty:
            best_rule = rules.iloc[0]
            insights.append(BusinessInsight(
                category="Catalog & Merchandising",
                priority="Medium",
                title=f"Strong Product Cross-Sell Synergy (Lift {best_rule['lift']}x)",
                observation=(
                    f"Orders containing '{best_rule['antecedent']}' are {best_rule['lift']}x more likely to also "
                    f"include '{best_rule['consequent']}' (confidence: {best_rule['confidence']*100:.1f}% across {best_rule['order_count']} orders)."
                ),
                supporting_metric=f"Lift {best_rule['lift']}x | Confidence {best_rule['confidence']*100:.1f}%",
                business_impact="Bundling or cross-recommending these products increases basket size and average order value (AOV).",
                recommended_action=f"Create a curated product bundle or checkout recommendation for '{best_rule['antecedent']}' and '{best_rule['consequent']}'.",
                limitations="Co-occurrence indicates statistical correlation, not direct causal buying motivations.",
            ))
    except Exception:
        pass

    # 5. Segment Champions Revenue Anchor
    try:
        segmented = segment_customers(rfm, n_clusters=4)
        comp = compare_segments(segmented)
        if not comp.empty:
            champ = comp.iloc[0]
            insights.append(BusinessInsight(
                category="Segmentation Strategy",
                priority="Medium",
                title=f"'{champ['segment_name']}' Segment Drives Majority of Cash Flow",
                observation=(
                    f"Your top segment ({champ['segment_name']}) contains {champ['customers']:,} customers ({champ['customer_share_pct']}%) "
                    f"and accounts for {champ['revenue_share_pct']}% of total spending (£{champ['total_spend']:,.2f})."
                ),
                supporting_metric=f"{champ['revenue_share_pct']}% revenue from {champ['customer_share_pct']}% of customer base",
                business_impact="Validates clear behavioral differentiation; this group forms the financial core of your business.",
                recommended_action="Reward this segment with early product access, dedicated loyalty incentives, and volume tiers.",
                limitations="Cluster boundaries are defined statistically via K-Means and depend on feature standardization.",
            ))
    except Exception:
        pass

    return insights
