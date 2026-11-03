"""Test fixtures for CustomerInsight AI.

Provides a small transaction DataFrame matching the canonical schema used
throughout the project. The data includes a few customers, multiple orders,
and one cancelled transaction.
"""

import pandas as pd
import pytest

from customerinsight.cleaning import clean_canonical_transactions

@pytest.fixture(scope="session")
def sample_transaction_df():
    """Return a DataFrame with canonical columns.

    Columns:
        order_id, customer_id, order_date, product_id, product_name,
        quantity, unit_price, country, currency, line_total, is_cancellation
    """
    data = {
        "order_id": ["INV-001", "INV-002", "INV-003", "C-INV-005", "INV-004"],
        "customer_id": ["CUST-1", "CUST-2", "CUST-1", "CUST-2", "CUST-3"],
        "order_date": pd.to_datetime([
            "2026-01-10", "2026-02-15", "2026-03-05", "2026-03-10", "2026-01-20"
        ]),
        "product_id": ["P1", "P2", "P1", "P3", "P4"],
        "product_name": ["Keyboard", "Wireless Mouse", "Keyboard", "Headset", "Monitor"],
        "quantity": [2, 1, 1, 1, 1],
        "unit_price": [100.0, 50.0, 150.0, 25.0, 50.0],
        "country": ["US", "US", "US", "US", "US"],
        "currency": ["USD"] * 5,
        "line_total": [200.0, 50.0, 150.0, 25.0, 50.0],
        "is_cancellation": [False, False, False, True, False],
    }
    return pd.DataFrame(data)

@pytest.fixture(scope="session")
def accepted_transactions(sample_transaction_df):
    """Return the accepted (non‑cancellation) transactions after cleaning.
    """
    accepted, _, _ = clean_canonical_transactions(sample_transaction_df)
    return accepted

