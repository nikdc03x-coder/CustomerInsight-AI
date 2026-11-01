"""Data hygiene, validation, and cleaning rules for canonical transactions."""

from dataclasses import dataclass, asdict
from typing import Any

import pandas as pd


@dataclass
class CleaningSummary:
    original_rows: int
    accepted_rows: int
    rejected_rows: int
    missing_customer_ids: int
    cancellation_rows: int
    nonpositive_quantities: int
    nonpositive_prices: int
    invalid_dates: int
    duplicate_rows: int
    rejection_breakdown: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def audit_data_quality(df: pd.DataFrame) -> dict[str, Any]:
    """Inspect canonical or pre-canonical DataFrame for data hygiene metrics."""
    total_rows = len(df)
    if total_rows == 0:
        return {
            "total_rows": 0,
            "unique_customers": 0,
            "unique_orders": 0,
            "missing_customer_ids": 0,
            "duplicate_rows": 0,
            "cancellation_rows": 0,
            "nonpositive_quantities": 0,
            "nonpositive_prices": 0,
            "invalid_dates": 0,
        }

    return {
        "total_rows": total_rows,
        "unique_customers": int(df["customer_id"].dropna().nunique()) if "customer_id" in df else 0,
        "unique_orders": int(df["order_id"].dropna().nunique()) if "order_id" in df else 0,
        "missing_customer_ids": int(df["customer_id"].isna().sum()) if "customer_id" in df else 0,
        "duplicate_rows": int(df.duplicated().sum()),
        "cancellation_rows": int(df["is_cancellation"].sum()) if "is_cancellation" in df else 0,
        "nonpositive_quantities": int((df["quantity"] <= 0).sum()) if "quantity" in df else 0,
        "nonpositive_prices": int((df["unit_price"] <= 0).sum()) if "unit_price" in df else 0,
        "invalid_dates": int(df["order_date"].isna().sum()) if "order_date" in df else 0,
    }


def clean_canonical_transactions(
    df: pd.DataFrame,
    require_customer: bool = True,
    exclude_cancellations: bool = True,
    require_positive_monetary: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, CleaningSummary]:
    """Clean canonical transactions and partition into accepted vs rejected records.

    Never silently drops records without recording the specific rejection reason.

    Returns:
        (accepted_df, rejected_df, cleaning_summary)
    """
    original_count = len(df)
    if original_count == 0:
        empty_summary = CleaningSummary(
            original_rows=0, accepted_rows=0, rejected_rows=0,
            missing_customer_ids=0, cancellation_rows=0,
            nonpositive_quantities=0, nonpositive_prices=0,
            invalid_dates=0, duplicate_rows=0, rejection_breakdown={},
        )
        return df.copy(), df.copy(), empty_summary

    reasons = pd.Series("", index=df.index, dtype="string")

    # 1. Missing customer ID check
    missing_cust = df["customer_id"].isna() | df["customer_id"].eq("")
    if require_customer:
        reasons = reasons.mask(missing_cust, reasons + "Missing Customer ID; ")

    # 2. Cancellation check
    is_cancel = df["is_cancellation"].fillna(False)
    if exclude_cancellations:
        reasons = reasons.mask(is_cancel, reasons + "Cancelled Order; ")

    # 3. Non-positive quantity check
    bad_qty = df["quantity"].isna() | (df["quantity"] <= 0)
    if require_positive_monetary:
        reasons = reasons.mask(bad_qty & ~is_cancel, reasons + "Non-positive Quantity; ")

    # 4. Non-positive unit price check
    bad_price = df["unit_price"].isna() | (df["unit_price"] <= 0)
    if require_positive_monetary:
        reasons = reasons.mask(bad_price, reasons + "Non-positive Unit Price; ")

    # 5. Invalid order date check
    bad_date = df["order_date"].isna()
    reasons = reasons.mask(bad_date, reasons + "Invalid Order Date; ")

    # Separate accepted and rejected
    rejected_mask = reasons.ne("")
    accepted_df = df.loc[~rejected_mask].copy()
    rejected_df = df.loc[rejected_mask].copy()
    rejected_df["rejection_reason"] = reasons[rejected_mask].str.rstrip("; ")

    # Rejection breakdown
    breakdown: dict[str, int] = {}
    if missing_cust.sum() > 0:
        breakdown["Missing Customer ID"] = int(missing_cust.sum())
    if is_cancel.sum() > 0:
        breakdown["Cancelled Order"] = int(is_cancel.sum())
    if bad_qty.sum() > 0:
        breakdown["Non-positive Quantity"] = int(bad_qty.sum())
    if bad_price.sum() > 0:
        breakdown["Non-positive Unit Price"] = int(bad_price.sum())
    if bad_date.sum() > 0:
        breakdown["Invalid Order Date"] = int(bad_date.sum())

    summary = CleaningSummary(
        original_rows=original_count,
        accepted_rows=len(accepted_df),
        rejected_rows=len(rejected_df),
        missing_customer_ids=int(missing_cust.sum()),
        cancellation_rows=int(is_cancel.sum()),
        nonpositive_quantities=int(bad_qty.sum()),
        nonpositive_prices=int(bad_price.sum()),
        invalid_dates=int(bad_date.sum()),
        duplicate_rows=int(df.duplicated().sum()),
        rejection_breakdown=breakdown,
    )

    return accepted_df, rejected_df, summary
