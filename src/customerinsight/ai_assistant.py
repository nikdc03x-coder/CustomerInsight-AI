"""Grounded AI Data Assistant: Natural-language query interface backed by verified analytics tools."""

from dataclasses import dataclass, asdict
import re
from typing import Any, Callable

import pandas as pd

from customerinsight.datasets import load_dataset_transactions, get_dataset_metadata
from customerinsight.analytics import (
    calculate_rfm,
    get_revenue_kpis,
    get_revenue_trend,
    get_revenue_by_country,
    get_top_customers,
    segment_customers,
    compare_segments,
)
from customerinsight.products import get_product_rankings, run_market_basket_analysis


def format_currency_symbol(code: str) -> str:
    """Map standard ISO currency codes to familiar symbols."""
    symbols = {"GBP": "£", "USD": "$", "EUR": "€", "JPY": "¥"}
    return symbols.get(str(code).upper().strip(), str(code))


@dataclass
class AssistantResponse:
    question: str
    direct_answer: str
    dataset_id: str
    analysis_period: str
    records_analyzed: int
    tool_executed: str
    supporting_metrics: dict[str, Any]
    table_data: list[dict[str, Any]] | None
    limitations: str
    suggested_followups: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# =====================================================================
# Approved Analytics Tool Registry
# =====================================================================

def tool_dataset_summary(dataset_id: str) -> dict[str, Any]:
    """Get high-level dataset metrics, date ranges, and customer counts."""
    df = load_dataset_transactions(dataset_id)
    kpis = get_revenue_kpis(df)
    meta = get_dataset_metadata(dataset_id) or {}
    return {
        "display_name": meta.get("display_name", dataset_id),
        "total_revenue": kpis["total_revenue"],
        "total_orders": kpis["total_orders"],
        "total_customers": kpis["total_customers"],
        "average_order_value": kpis["average_order_value"],
        "first_order_date": str(kpis["first_order_date"]) if kpis["first_order_date"] else "N/A",
        "last_order_date": str(kpis["last_order_date"]) if kpis["last_order_date"] else "N/A",
        "currency": kpis["currency"],
        "records_count": len(df),
    }


def tool_top_customers(dataset_id: str, n: int = 10) -> dict[str, Any]:
    """List the top N customers by total monetary spending."""
    df = load_dataset_transactions(dataset_id)
    top = get_top_customers(df, top_n=n)
    return {
        "top_customers": top.to_dict(orient="records"),
        "currency": str(df["currency"].iloc[0]) if "currency" in df and not df.empty else "GBP",
        "records_count": len(df),
    }


def tool_revenue_by_segment(dataset_id: str) -> dict[str, Any]:
    """Calculate revenue distribution across customer segments."""
    df = load_dataset_transactions(dataset_id)
    rfm = calculate_rfm(df)
    segmented = segment_customers(rfm, n_clusters=4)
    comparison = compare_segments(segmented)
    return {
        "segments": comparison.to_dict(orient="records"),
        "total_revenue": round(float(segmented["monetary"].sum()), 2),
        "records_count": len(df),
    }


def tool_average_order_value(dataset_id: str) -> dict[str, Any]:
    """Calculate the average order value and order count."""
    df = load_dataset_transactions(dataset_id)
    kpis = get_revenue_kpis(df)
    return {
        "average_order_value": kpis["average_order_value"],
        "total_revenue": kpis["total_revenue"],
        "total_orders": kpis["total_orders"],
        "currency": kpis["currency"],
        "records_count": len(df),
    }


def tool_product_performance(dataset_id: str, n: int = 10) -> dict[str, Any]:
    """Identify top selling products by revenue and units sold."""
    df = load_dataset_transactions(dataset_id)
    rankings = get_product_rankings(df, top_n=n, sort_by="revenue")
    return {
        "products": rankings.to_dict(orient="records"),
        "records_count": len(df),
    }


def tool_product_associations(dataset_id: str, min_lift: float = 1.0) -> dict[str, Any]:
    """Discover frequently co-purchased items via Market Basket Analysis."""
    df = load_dataset_transactions(dataset_id)
    rules = run_market_basket_analysis(df, min_support=0.005, min_confidence=0.08, min_lift=min_lift, max_rules=15)
    return {
        "rules": rules.to_dict(orient="records"),
        "rules_count": len(rules),
        "records_count": len(df),
    }


def tool_customer_inactivity(dataset_id: str, days: int = 90) -> dict[str, Any]:
    """Find customers who have not made an order in over N days."""
    df = load_dataset_transactions(dataset_id)
    rfm = calculate_rfm(df)
    inactive = rfm.loc[rfm["recency"] >= days].sort_values("monetary", ascending=False)
    total_customers = len(rfm)
    inactive_count = len(inactive)
    inactive_spend = float(inactive["monetary"].sum())
    return {
        "inactive_threshold_days": days,
        "inactive_count": inactive_count,
        "inactive_pct": round((inactive_count / total_customers) * 100, 2) if total_customers > 0 else 0,
        "inactive_historical_spend": round(inactive_spend, 2),
        "top_inactive": inactive.head(10).to_dict(orient="records"),
        "records_count": len(df),
    }


def tool_customer_profile(dataset_id: str, customer_id: str) -> dict[str, Any]:
    """Retrieve full purchasing profile and RFM for a specific customer."""
    df = load_dataset_transactions(dataset_id)
    rfm = calculate_rfm(df)
    match = rfm.loc[rfm["customer_id"].astype(str) == str(customer_id)]
    if match.empty:
        return {"found": False, "customer_id": customer_id}

    row = match.iloc[0]
    segmented = segment_customers(rfm, n_clusters=4)
    seg_match = segmented.loc[segmented["customer_id"].astype(str) == str(customer_id)]
    seg_name = seg_match.iloc[0]["segment_name"] if not seg_match.empty else "Unassigned"

    return {
        "found": True,
        "customer_id": str(customer_id),
        "recency_days": int(row["recency"]),
        "frequency_orders": int(row["frequency"]),
        "monetary_spend": float(row["monetary"]),
        "segment_name": seg_name,
        "records_count": len(df),
    }


TOOL_REGISTRY: dict[str, Callable] = {
    "dataset_summary": tool_dataset_summary,
    "top_customers": tool_top_customers,
    "revenue_by_segment": tool_revenue_by_segment,
    "average_order_value": tool_average_order_value,
    "product_performance": tool_product_performance,
    "product_associations": tool_product_associations,
    "customer_inactivity": tool_customer_inactivity,
    "customer_profile": tool_customer_profile,
}


# =====================================================================
# Intent Resolution & Question Answering Engine
# =====================================================================

def ask_assistant(question: str, dataset_id: str = "online_retail") -> AssistantResponse:
    """Interpret user question, execute verified analytics tool, and format answer.

    Guarantees zero hallucinations: answers strictly from computed mathematical output.
    """
    q_lower = question.lower().strip()

    # Match 1: Top Customers
    is_top_cust = (
        bool(re.search(r"\b(top|best|highest|biggest|leading)\s*(\d+)?\s*customers?\b", q_lower))
        or ("customer" in q_lower and any(w in q_lower for w in ["top", "best", "biggest", "highest", "most", "valuable"]))
    )
    if is_top_cust:
        n_match = re.search(r"\b(\d+)\b", q_lower)
        n = int(n_match.group(1)) if n_match and int(n_match.group(1)) <= 50 else 10
        data = tool_top_customers(dataset_id, n=n)
        top_list = data["top_customers"]
        curr = format_currency_symbol(data["currency"])

        if top_list:
            leader = top_list[0]
            answer = (
                f"Your top customer is **{leader['customer_id']}** with a total positive spend of "
                f"**{curr} {leader['total_spend']:,.2f}** across {leader['orders']} orders. "
                f"The top {len(top_list)} customers together represent significant revenue concentration."
            )
        else:
            answer = "No customer spending records were found."

        return AssistantResponse(
            question=question,
            direct_answer=answer,
            dataset_id=dataset_id,
            analysis_period="Full recorded dataset horizon",
            records_analyzed=data["records_count"],
            tool_executed="tool_top_customers",
            supporting_metrics={"top_n": n, "leader_id": leader["customer_id"] if top_list else None},
            table_data=top_list,
            limitations="Rankings reflect gross positive spend before refund reconciliation. Identifier numbers do not convey customer identity.",
            suggested_followups=[
                "Which segment generates the highest revenue?",
                "Which customers have not purchased recently?",
                "What is my average order value?",
            ],
        )

    # Match 2: Revenue by Segment
    if any(k in q_lower for k in ["segment", "clusters", "customer group", "who generates the most revenue", "highest revenue"]):
        data = tool_revenue_by_segment(dataset_id)
        segs = data["segments"]
        if segs:
            top_seg = segs[0]
            answer = (
                f"The **{top_seg['segment_name']}** segment generates the highest revenue, accounting for "
                f"**{top_seg['revenue_share_pct']}%** of all positive sales "
                f"(£{top_seg['total_spend']:,.2f} across {top_seg['customers']:,} customers, "
                f"median spend £{top_seg['median_monetary']:,.2f})."
            )
        else:
            answer = "Unable to compute segment revenue distribution."

        return AssistantResponse(
            question=question,
            direct_answer=answer,
            dataset_id=dataset_id,
            analysis_period="Aggregated customer RFM baseline",
            records_analyzed=data["records_count"],
            tool_executed="tool_revenue_by_segment",
            supporting_metrics={"total_spend": data["total_revenue"]},
            table_data=segs,
            limitations="Segments are formed using K-Means clustering (K=4) on log-standardized RFM features.",
            suggested_followups=[
                "Who are my top 10 customers?",
                "Which products are frequently purchased together?",
                "What is my overall revenue summary?",
            ],
        )

    # Match 3: Average Order Value (AOV)
    if any(k in q_lower for k in ["average order", "aov", "mean order", "basket size"]):
        data = tool_average_order_value(dataset_id)
        curr = format_currency_symbol(data["currency"])
        answer = (
            f"The Average Order Value (AOV) is **{curr} {data['average_order_value']:,.2f}**, "
            f"calculated across **{data['total_orders']:,}** distinct qualifying orders with total positive revenue of "
            f"**{curr} {data['total_revenue']:,.2f}**."
        )
        return AssistantResponse(
            question=question,
            direct_answer=answer,
            dataset_id=dataset_id,
            analysis_period="Complete dataset transaction period",
            records_analyzed=data["records_count"],
            tool_executed="tool_average_order_value",
            supporting_metrics=data,
            table_data=None,
            limitations="AOV excludes cancellations and refund lines. Invoices with multiple items are grouped as single orders.",
            suggested_followups=[
                "Which products are top sellers?",
                "Who are my top 10 customers?",
                "Which segment generates the highest revenue?",
            ],
        )

    # Match 4: Products Frequently Purchased Together (Basket / Cross-sell)
    if any(k in q_lower for k in ["together", "basket", "associated", "cross sell", "pairs", "bought with"]):
        data = tool_product_associations(dataset_id)
        rules = data["rules"]
        if rules:
            top_rule = rules[0]
            answer = (
                f"Customers who purchase **'{top_rule['antecedent']}'** are highly likely to also purchase "
                f"**'{top_rule['consequent']}'** (Lift: **{top_rule['lift']}x**, Confidence: **{top_rule['confidence']*100:.1f}%**, "
                f"co-occurring in {top_rule['order_count']} orders)."
            )
        else:
            answer = "No frequent item pairs exceeded the minimum support threshold in this dataset."

        return AssistantResponse(
            question=question,
            direct_answer=answer,
            dataset_id=dataset_id,
            analysis_period="Distinct order baskets",
            records_analyzed=data["records_count"],
            tool_executed="tool_product_associations",
            supporting_metrics={"rules_discovered": data["rules_count"]},
            table_data=rules,
            limitations="High lift indicates co-occurrence frequency above statistical independence. It proves correlation, not causal purchasing intent.",
            suggested_followups=[
                "What are my top selling products?",
                "Which customers have not purchased recently?",
                "What is my average order value?",
            ],
        )

    # Match 5: Top Selling Products
    if any(k in q_lower for k in ["product", "item", "top seller", "best seller", "catalog"]):
        data = tool_product_performance(dataset_id, n=10)
        items = data["products"]
        if items:
            best = items[0]
            answer = (
                f"Your top selling item by revenue is **'{best['product']}'** with "
                f"**£{best['revenue']:,.2f}** in gross sales across **{best['units_sold']:,} units** and {best['orders']:,} orders."
            )
        else:
            answer = "No product catalog sales records were found."

        return AssistantResponse(
            question=question,
            direct_answer=answer,
            dataset_id=dataset_id,
            analysis_period="All positive product transactions",
            records_analyzed=data["records_count"],
            tool_executed="tool_product_performance",
            supporting_metrics={"top_item": best["product"] if items else None},
            table_data=items,
            limitations="Product sales aggregate positive transactions only. Postage/freight line items may appear if recorded in source invoices.",
            suggested_followups=[
                "Which products are frequently purchased together?",
                "What is my average order value?",
                "Who are my top 10 customers?",
            ],
        )

    # Match 6: Inactivity / Lapsing Customers / Churn Risk
    if any(k in q_lower for k in ["inactive", "lapsed", "churn", "not purchased", "at risk", "haven't bought"]):
        days_match = re.search(r"\b(\d+)\s*days?\b", q_lower)
        days = int(days_match.group(1)) if days_match else 90
        data = tool_customer_inactivity(dataset_id, days=days)
        answer = (
            f"**{data['inactive_count']:,} customers ({data['inactive_pct']}%)** have had zero recorded orders "
            f"in over **{days} days**. Historically, this inactive cohort has contributed "
            f"**£{data['inactive_historical_spend']:,.2f}** in purchases, representing a key retention opportunity."
        )
        return AssistantResponse(
            question=question,
            direct_answer=answer,
            dataset_id=dataset_id,
            analysis_period=f"Recency evaluated relative to latest dataset purchase date (> {days} days)",
            records_analyzed=data["records_count"],
            tool_executed="tool_customer_inactivity",
            supporting_metrics=data,
            table_data=data["top_inactive"],
            limitations="Recency measures days elapsed between the customer's last purchase and the study reference date, not today's calendar date.",
            suggested_followups=[
                "Which segment generates the highest revenue?",
                "Who are my top 10 customers?",
                "What is my overall revenue summary?",
            ],
        )

    # Match 7: Specific Customer ID lookup
    cust_match = re.search(r"\b(\d{4,6})\b", q_lower)
    if "customer" in q_lower and cust_match:
        cid = cust_match.group(1)
        data = tool_customer_profile(dataset_id, customer_id=cid)
        if data["found"]:
            answer = (
                f"Customer **#{cid}** belongs to the **{data['segment_name']}** segment. "
                f"They have completed **{data['frequency_orders']} orders** totaling **£{data['monetary_spend']:,.2f}**, "
                f"with their last purchase occurring **{data['recency_days']} days** prior to the reference cutoff."
            )
        else:
            answer = f"Customer ID #{cid} was not found in the active dataset."

        return AssistantResponse(
            question=question,
            direct_answer=answer,
            dataset_id=dataset_id,
            analysis_period="Customer lifetime transaction history",
            records_analyzed=data.get("records_count", 0),
            tool_executed="tool_customer_profile",
            supporting_metrics=data,
            table_data=None,
            limitations="Customer profiles reflect aggregated positive spending before refunds.",
            suggested_followups=[
                "Who are my top 10 customers?",
                "Which segment generates the highest revenue?",
            ],
        )

    # Default Fallback: Dataset Summary & Overview
    summary = tool_dataset_summary(dataset_id)
    curr = format_currency_symbol(summary["currency"])
    answer = (
        f"In **{summary['display_name']}**, there are **{summary['total_customers']:,} customers** who generated "
        f"**{curr} {summary['total_revenue']:,.2f}** across **{summary['total_orders']:,} orders** "
        f"(Average Order Value: **{curr} {summary['average_order_value']:,.2f}**), "
        f"recorded between {summary['first_order_date'][:10]} and {summary['last_order_date'][:10]}."
    )
    return AssistantResponse(
        question=question,
        direct_answer=answer,
        dataset_id=dataset_id,
        analysis_period=f"{summary['first_order_date'][:10]} to {summary['last_order_date'][:10]}",
        records_analyzed=summary["records_count"],
        tool_executed="tool_dataset_summary",
        supporting_metrics=summary,
        table_data=None,
        limitations="Figures reflect clean qualifying positive sales from the active dataset.",
        suggested_followups=[
            "Who are my top 10 customers?",
            "Which segment generates the highest revenue?",
            "What is my average order value?",
            "Which products are frequently purchased together?",
        ],
    )
