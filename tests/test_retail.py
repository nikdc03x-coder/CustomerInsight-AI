
import pandas as pd

from customerinsight.retail import (
    data_quality_summary,
    valid_sales,
)


def sample_retail_data():
    # Include a sale, a cancellation and a missing customer ID.
    return pd.DataFrame({
        "invoice_id": ["10001", "C10002", "10003"],
        "customer_id": ["C001", "C002", None],
        "quantity": [2, -1, 1],
        "unit_price": [100.0, 100.0, 0.0],
        "invoice_date": pd.to_datetime([
            "2026-01-01",
            "2026-01-02",
            "2026-01-03",
        ]),
        "country": ["UK", "UK", "UK"],
        "is_cancellation": [False, True, False],
        "line_total": [200.0, -100.0, 0.0],
    })


def test_quality_summary_counts_problems():
    df = sample_retail_data()
    summary = data_quality_summary(df)

    assert summary["rows"] == 3
    assert summary["unique_customers"] == 2
    assert summary["missing_customer_ids"] == 1
    assert summary["cancellation_rows"] == 1
    assert summary["nonpositive_prices"] == 1


def test_valid_sales_excludes_cancellations():
    df = sample_retail_data()
    sales = valid_sales(df)

    assert len(sales) == 1
    assert sales["line_total"].sum() == 200.0


def test_source_data_is_not_modified():
    df = sample_retail_data()

    valid_sales(df)

    # We must preserve the original rows for later research.
    assert len(df) == 3
