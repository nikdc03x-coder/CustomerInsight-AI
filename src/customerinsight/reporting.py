"""Exportable executive reports, analytical briefs, and CSV formatted data sets."""

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from customerinsight.analytics import calculate_rfm, get_revenue_kpis, get_revenue_trend, get_revenue_by_country, segment_customers, compare_segments
from customerinsight.products import get_product_rankings, run_market_basket_analysis
from customerinsight.insights_engine import generate_business_insights


def generate_executive_brief_markdown(
    df: pd.DataFrame,
    dataset_name: str = "UCI Online Retail",
    currency: str = "GBP",
) -> str:
    """Generate a clean, professional executive markdown report for export or presentation."""
    kpis = get_revenue_kpis(df)
    rfm = calculate_rfm(df)
    segmented = segment_customers(rfm, n_clusters=4)
    seg_summary = compare_segments(segmented)
    insights = generate_business_insights(df, rfm)
    top_products = get_product_rankings(df, top_n=5)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Customer Intelligence Executive Brief — {dataset_name}",
        f"*Generated on {now_str} by CustomerInsight AI Platform*",
        "",
        "## 1. Executive Summary & Core KPIs",
        "",
        f"- **Total Gross Revenue**: {currency} {kpis['total_revenue']:,.2f}",
        f"- **Total Distinct Orders**: {kpis['total_orders']:,}",
        f"- **Active Customer Base**: {kpis['total_customers']:,} accounts",
        f"- **Average Order Value (AOV)**: {currency} {kpis['average_order_value']:,.2f}",
        f"- **Average Customer Lifetime Spend**: {currency} {kpis['average_customer_spend']:,.2f}",
        f"- **Transaction Window**: {str(kpis['first_order_date'])[:10]} to {str(kpis['last_order_date'])[:10]}",
        "",
        "## 2. Customer Segmentation Breakdown",
        "",
        "| Segment | Customers | Customer Share (%) | Total Spend | Revenue Share (%) | Median Recency | Median Orders | Median Spend |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for _, row in seg_summary.iterrows():
        lines.append(
            f"| **{row['segment_name']}** | {row['customers']:,} | {row['customer_share_pct']}% | "
            f"{currency} {row['total_spend']:,.2f} | {row['revenue_share_pct']}% | "
            f"{row['median_recency']} days | {row['median_frequency']} | {currency} {row['median_monetary']:,.2f} |"
        )

    lines.extend([
        "",
        "## 3. Top Evidence-Grounded Strategic Insights",
        "",
    ])

    if insights:
        for i, insight in enumerate(insights, 1):
            lines.extend([
                f"### {i}. [{insight.priority} Priority] {insight.title}",
                f"- **Observation**: {insight.observation}",
                f"- **Business Impact**: {insight.business_impact}",
                f"- **Recommended Action**: {insight.recommended_action}",
                f"- *Evidence Metric*: `{insight.supporting_metric}`",
                f"- *Limitations*: {insight.limitations}",
                "",
            ])
    else:
        lines.append("No critical threshold alerts triggered for this dataset.\n")

    lines.extend([
        "## 4. Top Performing Catalog Products",
        "",
        "| Product | Revenue | Units Sold | Distinct Orders | Average Price |",
        "|---|---|---|---|---|",
    ])

    for _, prod in top_products.iterrows():
        lines.append(
            f"| {prod['product']} | {currency} {prod['revenue']:,.2f} | "
            f"{prod['units_sold']:,} | {prod['orders']:,} | {currency} {prod['avg_price']:,.2f} |"
        )

    lines.extend([
        "",
        "## 5. Audit & Data Methodology Notes",
        "",
        "- Monetary numbers represent gross positive spending before refund adjustments.",
        "- Customer recency measures days elapsed prior to the final recorded dataset transaction.",
        "- Customer segments are formed using K-Means (K=4) over log-standardized RFM vectors.",
        "- Product relationships reflect transaction co-occurrence; correlation does not imply causation.",
        "",
        "---",
        "*Report compiled by CustomerInsight AI Platform.*",
    ])

    return "\n".join(lines)


def export_customer_segments_csv(rfm_segmented: pd.DataFrame) -> str:
    """Export the segmented customer base as CSV text."""
    return rfm_segmented.to_csv(index=False)
