
import pandas as pd
import pytest

from customerinsight.data import (
    describe_transactions,
    load_transactions,
)


def test_loads_valid_transactions(tmp_path):
    # Create a small file to test the loading process.
    path = tmp_path / "transactions.csv"

    path.write_text(
        "customer_id,invoice_id,invoice_date,quantity,unit_price\n"
        "C001,INV001,2026-01-01,2,500\n",
        encoding="utf-8",
    )

    df = load_transactions(path)

    assert len(df) == 1
    assert df["quantity"].iloc[0] == 2
    assert df["customer_id"].iloc[0] == "C001"


def test_rejects_missing_columns(tmp_path):
    # A missing field should produce a clear error.
    path = tmp_path / "incomplete.csv"

    path.write_text(
        "customer_id,invoice_id\nC001,INV001\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        load_transactions(path)


def test_rejects_invalid_dates(tmp_path):
    path = tmp_path / "bad_dates.csv"

    path.write_text(
        "customer_id,invoice_id,invoice_date,quantity,unit_price\n"
        "C001,INV001,not-a-date,2,500\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invoice_date"):
        load_transactions(path)


def test_counts_returns_separately():
    # Returns must not disappear during initial inspection.
    df = pd.DataFrame({
        "customer_id": ["C001", "C002"],
        "invoice_id": ["INV001", "INV002"],
        "invoice_date": pd.to_datetime([
            "2026-01-01", "2026-01-02"
        ]),
        "quantity": [2, -1],
        "unit_price": [500, 500],
    })

    summary = describe_transactions(df)

    assert summary["transactions"] == 2
    assert summary["unique_customers"] == 2
    assert summary["return_rows"] == 1
