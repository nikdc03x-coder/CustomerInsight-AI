"""RFM calculation utilities for CustomerInsight.

Provides a straightforward implementation of `calculate_rfm` that aggregates
recency, frequency, and monetary metrics from a transactional dataframe using
the canonical column names defined by the project:

* ``order_date`` – transaction date
* ``line_total`` – monetary value of the transaction
* ``customer_id`` – identifier of the customer

The function returns a DataFrame with exactly four lower‑case columns:
``customer_id``, ``recency``, ``frequency`` and ``monetary``. No score columns are
included because the test suite expects only the raw RFM values.
"""

import pandas as pd
import streamlit as st
from datetime import datetime

@st.cache_data(show_spinner="Calculating RFM…")
def calculate_rfm(
    df: pd.DataFrame,
    customer_id_col: str = "customer_id",
    date_col: str = "order_date",
    amount_col: str = "line_total",
    snapshot_date: str | None = None,
) -> pd.DataFrame:
    """Calculate RFM metrics using the canonical column names.

    Parameters
    ----------
    df : pd.DataFrame
        Transactional data containing at least the customer ID, date, and amount.
    customer_id_col : str, optional
        Column name for the unique customer identifier (default ``"customer_id"``).
    date_col : str, optional
        Column name for the transaction date (default ``"order_date"``).
    amount_col : str, optional
        Column name for the monetary value of each transaction (default ``"line_total"``).
    snapshot_date : str | None, optional
        Reference date for recency calculation. If ``None`` the function uses
        ``df[date_col].max() + 1 day``.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``customer_id``, ``recency``, ``frequency`` and ``monetary``.
    """
    # Work on a copy to avoid mutating the caller's DataFrame.
    df = df.copy()
    # Ensure the date column is datetime.
    df[date_col] = pd.to_datetime(df[date_col])

    # Determine the snapshot date for recency calculation.
    if snapshot_date is None:
        snapshot = df[date_col].max() + pd.Timedelta(days=1)
    else:
        snapshot = pd.to_datetime(snapshot_date)

    # Aggregate raw RFM values.
    rfm = (
        df.groupby(customer_id_col)
        .agg(
            recency=(date_col, lambda x: (snapshot - x.max()).days),
            frequency=("order_id", "nunique"),
            monetary=(amount_col, "sum"),
        )
        .reset_index()
    )
    return rfm
