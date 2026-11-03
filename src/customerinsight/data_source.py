# -*- coding: utf-8 -*-
"""Central data‑access module for the CustomerInsight platform.

Provides a single source of truth – the built‑in Online Retail benchmark – and
exposes helper utilities used throughout the Streamlit UI and AI assistant.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

# Re‑use the existing dataset loader for parity with the original implementation
from .datasets import load_dataset_transactions, DEFAULT_DATASET_ID

# ---------------------------------------------------------------------------
# Cached loading of the built‑in dataset
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading built‑in dataset…")
def load_builtin_dataset() -> pd.DataFrame:
    """Load the built‑in Online Retail benchmark as a canonical DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: customer_id, order_id, order_date, product_id, product_name,
        quantity, unit_price, currency, country, line_total
    """
    return load_dataset_transactions(dataset_id=DEFAULT_DATASET_ID)

# ---------------------------------------------------------------------------
# Metadata & preview helpers (used by UI pages)
# ---------------------------------------------------------------------------
def get_dataset_metadata() -> dict:
    """Return metadata for the built‑in dataset (mirrors ``datasets.get_dataset_metadata``)."""
    from .datasets import get_dataset_metadata as _meta
    meta = _meta(DEFAULT_DATASET_ID) or {}
    return meta


def dataset_preview(df: pd.DataFrame, rows: int = 5) -> pd.DataFrame:
    """Return a preview slice of the DataFrame for display."""
    return df.head(rows)


def dataset_quality_summary(df: pd.DataFrame) -> dict:
    """Simple quality summary used by the Data Workspace page.

    The summary includes basic row counts and simple data‑quality flags.
    """
    total_rows = len(df)
    missing_cust = df["customer_id"].isna().sum()
    duplicated = df.duplicated(subset=["order_id", "product_id"]).sum()
    return {
        "total_rows": total_rows,
        "missing_customer_id": missing_cust,
        "duplicate_transactions": duplicated,
        "unique_customers": int(df["customer_id"].nunique()),
    }

