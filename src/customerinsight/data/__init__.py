# Data package
"""Data loading and preprocessing utilities for CustomerInsight AI.

Provides functions to load transaction data and generate simple summaries.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path

# Required columns for transaction CSV
_REQUIRED_COLUMNS = {
    "customer_id",
    "invoice_id",
    "invoice_date",
    "quantity",
    "unit_price",
}


def load_transactions(csv_path: Path | str) -> pd.DataFrame:
    """Load a transaction CSV file.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        pandas.DataFrame with the transaction records.

    Raises:
        ValueError: If required columns are missing or dates cannot be parsed.
    """
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Transaction file not found: {path}")

    df = pd.read_csv(path)
    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    # Ensure invoice_date parses to a datetime; raise on failure
    try:
        df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="raise")
    except Exception as exc:
        raise ValueError(f"Invalid invoice_date column: {exc}") from exc

    return df


def describe_transactions(df: pd.DataFrame) -> dict:
    """Return a summary of transaction data.

    The summary includes the total number of transaction rows, the number of unique
    customers, and the count of return rows (where ``quantity`` is negative).

    Args:
        df: DataFrame containing transaction records.

    Returns:
        dict with keys ``transactions``, ``unique_customers`` and ``return_rows``.
    """
    total = len(df)
    unique_customers = df["customer_id"].nunique()
    return_rows = int((df["quantity"] < 0).sum())
    return {
        "transactions": total,
        "unique_customers": unique_customers,
        "return_rows": return_rows,
    }

__all__ = ["load_transactions", "describe_transactions"]

