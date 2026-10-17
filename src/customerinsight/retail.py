
from pathlib import Path

import pandas as pd


RETAIL_COLUMNS = {
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
}


def load_retail_data(file_path: str | Path) -> pd.DataFrame:
    """Read the original UCI retail workbook without dropping records."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Retail dataset not found: {path}")

    # Keep invoice and product identifiers as text.
    df = pd.read_excel(
        path,
        engine="openpyxl",
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string",
            "CustomerID": "string",
        },
    )

    missing_columns = RETAIL_COLUMNS - set(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing retail columns: {missing}")

    if df.empty:
        raise ValueError("The retail dataset is empty.")

    # Create analysis-friendly names without changing the raw workbook.
    df = df.rename(columns={
        "InvoiceNo": "invoice_id",
        "StockCode": "stock_code",
        "Description": "description",
        "Quantity": "quantity",
        "InvoiceDate": "invoice_date",
        "UnitPrice": "unit_price",
        "CustomerID": "customer_id",
        "Country": "country",
    })

    df["invoice_date"] = pd.to_datetime(
        df["invoice_date"], errors="coerce"
    )

    for column in ["quantity", "unit_price"]:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    # Cancellation invoices have a C prefix in this dataset.
    df["is_cancellation"] = (
        df["invoice_id"].str.upper().str.startswith("C").fillna(False)
    )

    df["line_total"] = df["quantity"] * df["unit_price"]

    return df


def data_quality_summary(df: pd.DataFrame) -> dict:
    """Report possible issues before deciding how to clean the data."""

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "unique_customers": int(df["customer_id"].nunique()),
        "missing_customer_ids": int(df["customer_id"].isna().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "cancellation_rows": int(df["is_cancellation"].sum()),
        "negative_quantities": int((df["quantity"] < 0).sum()),
        "nonpositive_prices": int((df["unit_price"] <= 0).sum()),
        "invalid_dates": int(df["invoice_date"].isna().sum()),
    }


def valid_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Select positive sales for descriptive revenue charts.

    This is only a view for exploration. It does not modify raw data.
    Refunds and cancellations require separate treatment in later phases.
    """

    valid = (
        ~df["is_cancellation"]
        & (df["quantity"] > 0)
        & (df["unit_price"] > 0)
        & df["invoice_date"].notna()
        & df["country"].notna()
    )

    return df.loc[valid].copy()
