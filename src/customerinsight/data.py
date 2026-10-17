
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "customer_id",
    "invoice_id",
    "invoice_date",
    "quantity",
    "unit_price",
}


def load_transactions(file_path: str | Path) -> pd.DataFrame:
    """Load transaction records and check their basic structure."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")

    # Keep identifiers as text so leading zeros are preserved.
    df = pd.read_csv(
        path,
        dtype={
            "customer_id": "string",
            "invoice_id": "string",
        },
    )

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        columns = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {columns}")

    if df.empty:
        raise ValueError("The dataset contains no transaction records.")

    # Convert dates and numeric values before any analysis.
    df["invoice_date"] = pd.to_datetime(
        df["invoice_date"], errors="coerce"
    )

    for column in ["quantity", "unit_price"]:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    # Invalid records should be reported, not silently removed.
    for column in ["invoice_date", "quantity", "unit_price"]:
        invalid_count = df[column].isna().sum()

        if invalid_count:
            raise ValueError(
                f"{column} contains {invalid_count} invalid or missing values."
            )

    return df


def describe_transactions(df: pd.DataFrame) -> dict:
    """Summarize a dataset before we begin modelling."""

    return {
        "transactions": len(df),
        "unique_customers": df["customer_id"].nunique(),
        "missing_customer_ids": int(df["customer_id"].isna().sum()),
        "return_rows": int((df["quantity"] < 0).sum()),
        "first_purchase": df["invoice_date"].min(),
        "last_purchase": df["invoice_date"].max(),
    }
