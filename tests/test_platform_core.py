"""Unit and integration tests for Customer Intelligence Platform core modules."""

import io
from pathlib import Path
import pandas as pd
import pytest

from customerinsight.schema import detect_column_mappings, coerce_canonical_types, assess_capabilities
from customerinsight.cleaning import clean_canonical_transactions, audit_data_quality
from customerinsight.analytics import calculate_rfm, get_revenue_kpis, get_revenue_trend, segment_customers, compare_segments
from customerinsight.products import get_product_rankings, run_market_basket_analysis
from customerinsight.prediction import assess_predictive_eligibility, predict_customer_recurrence_and_clv
from customerinsight.ai_assistant import ask_assistant, tool_top_customers, tool_revenue_by_segment, tool_average_order_value
from customerinsight.insights_engine import generate_business_insights
from customerinsight.reporting import generate_executive_brief_markdown


@pytest.fixture
def sample_transaction_df():
    """A realistic synthetic multi-order e-commerce transaction dataset."""
    return pd.DataFrame({
        "order_id": ["INV-001", "INV-001", "INV-002", "INV-003", "INV-004", "C-INV-005"],
        "customer_id": ["CUST-1", "CUST-1", "CUST-2", "CUST-1", "CUST-3", "CUST-2"],
        "order_date": pd.to_datetime([
            "2026-01-10 10:00", "2026-01-10 10:00", "2026-02-15 14:00",
            "2026-03-01 11:00", "2026-03-10 09:30", "2026-03-12 16:00"
        ]),
        "product_id": ["PROD-A", "PROD-B", "PROD-A", "PROD-B", "PROD-C", "PROD-A"],
        "product_name": ["Wireless Mouse", "Keyboard", "Wireless Mouse", "Keyboard", "USB Cable", "Wireless Mouse"],
        "quantity": [2, 1, 1, 3, 5, -1],
        "unit_price": [25.0, 50.0, 25.0, 50.0, 10.0, 25.0],
        "country": ["United Kingdom", "United Kingdom", "Germany", "United Kingdom", "France", "Germany"],
        "currency": ["GBP", "GBP", "EUR", "GBP", "EUR", "EUR"],
        "line_total": [50.0, 50.0, 25.0, 150.0, 50.0, -25.0],
        "is_cancellation": [False, False, False, False, False, True],
    })


def test_column_mapping_detection():
    cols = ["Client ID", "Invoice_No", "Purchase Date", "SKU", "Item Description", "Qty", "Item Price", "Billing Country"]
    mapping = detect_column_mappings(cols)
    assert mapping["customer_id"] == "Client ID"
    assert mapping["order_id"] == "Invoice_No"
    assert mapping["order_date"] == "Purchase Date"
    assert mapping["product_id"] == "SKU"
    assert mapping["product_name"] == "Item Description"
    assert mapping["quantity"] == "Qty"
    assert mapping["unit_price"] == "Item Price"
    assert mapping["country"] == "Billing Country"

    caps = assess_capabilities(mapping)
    assert caps["rfm_segmentation"] is True
    assert caps["revenue_analytics"] is True
    assert caps["product_intelligence"] is True
    assert caps["market_basket_analysis"] is True
    assert caps["geographic_breakdown"] is True


def test_data_cleaning_and_summary(sample_transaction_df):
    accepted, rejected, summary = clean_canonical_transactions(sample_transaction_df)
    assert summary.original_rows == 6
    assert summary.accepted_rows == 5
    assert summary.rejected_rows == 1
    assert summary.cancellation_rows == 1
    assert "Cancelled Order" in rejected.iloc[0]["rejection_reason"]


def test_generalised_rfm_calculation(sample_transaction_df):
    accepted, _, _ = clean_canonical_transactions(sample_transaction_df)
    rfm = calculate_rfm(accepted)
    assert len(rfm) == 3
    assert set(rfm.columns) == {"customer_id", "recency", "frequency", "monetary"}

    # CUST-1 made 2 distinct positive orders (INV-001, INV-003) totaling 250.0
    cust1 = rfm.loc[rfm["customer_id"] == "CUST-1"].iloc[0]
    assert cust1["frequency"] == 2
    assert cust1["monetary"] == 250.0
    assert cust1["recency"] >= 0


def test_revenue_kpis_and_trend(sample_transaction_df):
    accepted, _, _ = clean_canonical_transactions(sample_transaction_df)
    kpis = get_revenue_kpis(accepted)
    assert kpis["total_revenue"] == 325.0  # 50 + 50 + 25 + 150 + 50
    assert kpis["total_orders"] == 4
    assert kpis["total_customers"] == 3
    assert kpis["average_order_value"] == round(325.0 / 4, 2)

    trend = get_revenue_trend(accepted, freq="M")
    assert len(trend) == 3  # Jan, Feb, Mar 2026


def test_product_rankings_and_basket_analysis(sample_transaction_df):
    accepted, _, _ = clean_canonical_transactions(sample_transaction_df)
    rankings = get_product_rankings(accepted, top_n=5)
    assert len(rankings) == 3
    assert rankings.iloc[0]["product"] in ["Keyboard", "Wireless Mouse"]

    # Market basket on INV-001 which has both Mouse and Keyboard
    rules = run_market_basket_analysis(accepted, min_support=0.1, min_confidence=0.1, min_lift=0.5)
    assert not rules.empty
    assert "antecedent" in rules.columns
    assert "lift" in rules.columns


def test_predictive_eligibility_and_recurrence(sample_transaction_df):
    accepted, _, _ = clean_canonical_transactions(sample_transaction_df)
    # Span is Jan 10 to Mar 10 = ~59 days, repeat rate is 33% -> eligible
    elig = assess_predictive_eligibility(accepted)
    assert elig["eligible"] is True
    assert elig["total_days"] >= 45

    clv = predict_customer_recurrence_and_clv(accepted, projection_days=90)
    assert len(clv) == 3
    assert "p_active" in clv.columns
    assert "churn_risk" in clv.columns
    assert "predicted_spend_90d" in clv.columns


def test_business_insights_generation(sample_transaction_df):
    accepted, _, _ = clean_canonical_transactions(sample_transaction_df)
    rfm = calculate_rfm(accepted)
    insights = generate_business_insights(accepted, rfm)
    assert isinstance(insights, list)
    assert len(insights) > 0
    first = insights[0]
    assert hasattr(first, "title")
    assert hasattr(first, "observation")
    assert hasattr(first, "recommended_action")


def test_grounded_ai_assistant_execution():
    # Ask about top customers on built-in dataset
    res_top = ask_assistant("Who are my top 5 customers?", dataset_id="online_retail")
    assert "top customer" in res_top.direct_answer.lower()
    assert res_top.records_analyzed > 0
    assert res_top.table_data is not None

    # Ask about average order value
    res_aov = ask_assistant("What is my average order value?", dataset_id="online_retail")
    assert "average order value" in res_aov.direct_answer.lower()
    assert "£" in res_aov.direct_answer

    # Ask about segments
    res_seg = ask_assistant("Which segment generates the highest revenue?", dataset_id="online_retail")
    assert "segment" in res_seg.direct_answer.lower()
    assert res_seg.table_data is not None


def test_executive_report_generation(sample_transaction_df):
    accepted, _, _ = clean_canonical_transactions(sample_transaction_df)
    report_md = generate_executive_brief_markdown(accepted, dataset_name="Test Store")
    assert "# Customer Intelligence Executive Brief" in report_md
    assert "Total Gross Revenue" in report_md
    assert "Customer Segmentation Breakdown" in report_md
