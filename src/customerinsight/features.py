
"""Build customer-level purchasing features from retail transactions."""

import pandas as pd

from customerinsight.retail import valid_sales


RFM_COLUMNS = [
    "customer_id",
    "recency",
    "frequency",
    "monetary",
]


def prepare_customer_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Keep identifiable customers with valid positive purchases."""

    # Reuse our existing sales rules so phases stay consistent.
    sales = valid_sales(df)

    # Customer-level features require a usable customer identifier.
    sales = sales.loc[sales["customer_id"].notna()].copy()
    sales["customer_id"] = sales["customer_id"].astype("string").str.strip()
    sales = sales.loc[sales["customer_id"].ne("").fillna(False)].copy()

    # We need an invoice ID to count distinct purchasing occasions.
    sales = sales.loc[sales["invoice_id"].notna()].copy()
    sales["invoice_id"] = sales["invoice_id"].astype("string").str.strip()
    sales = sales.loc[sales["invoice_id"].ne("").fillna(False)].copy()

    return sales


def build_rfm(
    df: pd.DataFrame,
    reference_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Calculate recency, frequency and monetary value per customer."""

    sales = prepare_customer_sales(df)

    if sales.empty:
        raise ValueError("No valid customer purchases available for RFM.")

    latest_purchase = sales["invoice_date"].max()

    # An explicit reference date makes repeated experiments reproducible.
    if reference_date is None:
        reference = latest_purchase.normalize() + pd.Timedelta(days=1)
    else:
        reference = pd.Timestamp(reference_date).normalize()

    if pd.isna(reference):
        raise ValueError("Reference date must be a valid date.")

    if reference < latest_purchase.normalize():
        raise ValueError(
            "Reference date cannot be before the latest purchase date."
        )

    # Each customer receives a single row of behavioural features.
    rfm = (
        sales.groupby("customer_id")
        .agg(
            last_purchase=("invoice_date", "max"),
            frequency=("invoice_id", "nunique"),
            monetary=("line_total", "sum"),
        )
        .reset_index()
    )

    rfm["recency"] = (
        reference - rfm["last_purchase"].dt.normalize()
    ).dt.days

    rfm = rfm[RFM_COLUMNS].copy()

    # Preserve whole-day and whole-invoice counts.
    rfm["recency"] = rfm["recency"].astype("int64")
    rfm["frequency"] = rfm["frequency"].astype("int64")

    return rfm.sort_values("customer_id").reset_index(drop=True)


def describe_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for our customer features."""

    return rfm[["recency", "frequency", "monetary"]].describe().round(2)
