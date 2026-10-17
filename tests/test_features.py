
import pandas as pd
import pytest

from customerinsight.features import (
    build_rfm,
    describe_rfm,
    prepare_customer_sales,
)


@pytest.fixture
def transactions():
    """A small dataset with repeat purchases, a return and missing IDs."""

    df = pd.DataFrame({
        "customer_id": [
            "C001", "C001", "C001", "C002", "C002", None
        ],
        "invoice_id": [
            "INV001", "INV001", "INV002",
            "INV003", "CINV004", "INV005"
        ],
        "invoice_date": pd.to_datetime([
            "2026-01-05", "2026-01-05", "2026-01-15",
            "2026-01-10", "2026-01-12", "2026-01-13"
        ]),
        "quantity": [2, 1, 1, 3, -1, 1],
        "unit_price": [100, 200, 300, 50, 50, 100],
        "country": ["UK"] * 6,
        "is_cancellation": [
            False, False, False, False, True, False
        ],
    })

    df["line_total"] = df["quantity"] * df["unit_price"]
    return df


def test_excludes_returns_and_missing_customers(transactions):
    sales = prepare_customer_sales(transactions)

    assert len(sales) == 4
    assert sales["customer_id"].nunique() == 2
    assert not sales["is_cancellation"].any()


def test_frequency_counts_unique_invoices(transactions):
    rfm = build_rfm(transactions, reference_date="2026-01-21")

    customer = rfm.set_index("customer_id").loc["C001"]

    # Three product lines, but only two distinct invoices.
    assert customer["frequency"] == 2


def test_monetary_uses_positive_sale_values(transactions):
    rfm = build_rfm(transactions, reference_date="2026-01-21")

    customer = rfm.set_index("customer_id").loc["C001"]

    assert customer["monetary"] == 700


def test_recency_uses_reference_date(transactions):
    rfm = build_rfm(transactions, reference_date="2026-01-21")

    customer = rfm.set_index("customer_id").loc["C001"]

    assert customer["recency"] == 6


def test_rejects_invalid_reference_date(transactions):
    with pytest.raises(ValueError, match="Reference date"):
        build_rfm(transactions, reference_date="2025-01-01")


def test_original_data_is_unchanged(transactions):
    original = transactions.copy(deep=True)

    build_rfm(transactions)

    pd.testing.assert_frame_equal(transactions, original)


def test_descriptive_statistics(transactions):
    rfm = build_rfm(transactions)
    summary = describe_rfm(rfm)

    assert "mean" in summary.index
    assert "recency" in summary.columns
    assert "frequency" in summary.columns
    assert "monetary" in summary.columns
