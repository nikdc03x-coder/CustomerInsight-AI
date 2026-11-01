"""Multi-dataset management, metadata tracking, and Parquet storage engine."""

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any

import pandas as pd

from customerinsight.retail import load_retail_data, valid_sales
from customerinsight.schema import detect_column_mappings, coerce_canonical_types, assess_capabilities
from customerinsight.cleaning import clean_canonical_transactions


ROOT_DIR = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT_DIR / "data/datasets"
DB_PATH = DATASETS_DIR / "registry.sqlite"

DEFAULT_DATASET_ID = "online_retail"


def _init_db():
    """Initialize the SQLite dataset metadata store."""
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                dataset_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                filename TEXT NOT NULL,
                created_at TEXT NOT NULL,
                original_rows INTEGER NOT NULL,
                accepted_rows INTEGER NOT NULL,
                rejected_rows INTEGER NOT NULL,
                unique_customers INTEGER NOT NULL,
                currency TEXT NOT NULL,
                mapping_json TEXT NOT NULL,
                capabilities_json TEXT NOT NULL,
                is_builtin INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


def list_datasets() -> list[dict[str, Any]]:
    """List all available datasets including the built-in Online Retail dataset."""
    _init_db()

    # Ensure built-in dataset is registered
    _ensure_builtin_registered()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM datasets ORDER BY is_builtin DESC, created_at DESC"
        ).fetchall()

    result = []
    for row in rows:
        item = dict(row)
        item["mapping"] = json.loads(item.pop("mapping_json"))
        item["capabilities"] = json.loads(item.pop("capabilities_json"))
        item["is_builtin"] = bool(item["is_builtin"])
        result.append(item)

    return result


def get_dataset_metadata(dataset_id: str) -> dict[str, Any] | None:
    """Retrieve metadata for a specific dataset."""
    _init_db()
    _ensure_builtin_registered()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM datasets WHERE dataset_id = ?", (dataset_id,)
        ).fetchone()

    if not row:
        return None

    item = dict(row)
    item["mapping"] = json.loads(item.pop("mapping_json"))
    item["capabilities"] = json.loads(item.pop("capabilities_json"))
    item["is_builtin"] = bool(item["is_builtin"])
    return item


def _ensure_builtin_registered():
    """Ensure the built-in Online Retail benchmark dataset is registered."""
    raw_excel = ROOT_DIR / "data/raw/Online Retail.xlsx"
    parquet_path = DATASETS_DIR / DEFAULT_DATASET_ID / "transactions.parquet"

    with sqlite3.connect(DB_PATH) as conn:
        exists = conn.execute(
            "SELECT 1 FROM datasets WHERE dataset_id = ?", (DEFAULT_DATASET_ID,)
        ).fetchone()

        if exists and parquet_path.is_file():
            return

    # If raw excel exists, build initial Parquet cache for sub-second performance
    if raw_excel.is_file():
        df_raw = load_retail_data(raw_excel)
        mapping = {
            "customer_id": "customer_id",
            "order_id": "invoice_id",
            "order_date": "invoice_date",
            "product_id": "stock_code",
            "product_name": "description",
            "quantity": "quantity",
            "unit_price": "unit_price",
            "currency": None,
            "country": "country",
        }
        canonical = coerce_canonical_types(df_raw, mapping, default_currency="GBP")
        accepted, rejected, summary = clean_canonical_transactions(canonical)

        target_dir = DATASETS_DIR / DEFAULT_DATASET_ID
        target_dir.mkdir(parents=True, exist_ok=True)
        accepted.to_parquet(parquet_path, index=False)

        capabilities = assess_capabilities(mapping)

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO datasets (
                    dataset_id, display_name, filename, created_at,
                    original_rows, accepted_rows, rejected_rows,
                    unique_customers, currency, mapping_json,
                    capabilities_json, is_builtin
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                DEFAULT_DATASET_ID,
                "UCI Online Retail (Benchmark)",
                "Online Retail.xlsx",
                "2026-10-17T00:00:00Z",
                len(df_raw),
                len(accepted),
                len(rejected),
                int(accepted["customer_id"].nunique()),
                "GBP",
                json.dumps(mapping),
                json.dumps(capabilities),
                1,
            ))
            conn.commit()


def load_dataset_transactions(dataset_id: str = DEFAULT_DATASET_ID) -> pd.DataFrame:
    """Load cleaned, canonical transactions for the specified dataset.

    Returns DataFrame with canonical columns:
    [customer_id, order_id, order_date, product_id, product_name, quantity, unit_price, currency, country, line_total]
    """
    _init_db()
    _ensure_builtin_registered()

    parquet_path = DATASETS_DIR / dataset_id / "transactions.parquet"
    if parquet_path.is_file():
        return pd.read_parquet(parquet_path)

    # Fallback for built-in if parquet is building or absent
    if dataset_id == DEFAULT_DATASET_ID:
        raw_excel = ROOT_DIR / "data/raw/Online Retail.xlsx"
        if raw_excel.is_file():
            df_raw = load_retail_data(raw_excel)
            sales = valid_sales(df_raw)
            # Match canonical column names
            return sales.rename(columns={
                "invoice_id": "order_id",
                "stock_code": "product_id",
                "description": "product_name",
                "invoice_date": "order_date",
            })

    raise FileNotFoundError(f"Dataset transactions not found for: {dataset_id}")


def register_uploaded_dataset(
    file_bytes: bytes,
    filename: str,
    display_name: str,
    mapping: dict[str, str | None],
    accepted_df: pd.DataFrame,
    summary: Any,
    default_currency: str = "GBP",
) -> str:
    """Save raw file, write canonical Parquet table, and record metadata."""
    _init_db()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    clean_name = "".join(c if c.isalnum() else "_" for c in display_name.lower())[:24]
    dataset_id = f"ds_{clean_name}_{timestamp}"

    dataset_folder = DATASETS_DIR / dataset_id
    dataset_folder.mkdir(parents=True, exist_ok=True)

    # 1. Save raw bytes
    raw_path = dataset_folder / f"raw_{filename}"
    raw_path.write_bytes(file_bytes)

    # 2. Save canonical Parquet
    parquet_path = dataset_folder / "transactions.parquet"
    accepted_df.to_parquet(parquet_path, index=False)

    # 3. Assess capabilities
    capabilities = assess_capabilities(mapping)

    # 4. Insert into SQLite registry
    created_at = datetime.now(timezone.utc).isoformat()
    unique_cust = int(accepted_df["customer_id"].dropna().nunique()) if "customer_id" in accepted_df else 0

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO datasets (
                dataset_id, display_name, filename, created_at,
                original_rows, accepted_rows, rejected_rows,
                unique_customers, currency, mapping_json,
                capabilities_json, is_builtin
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dataset_id,
            display_name,
            filename,
            created_at,
            summary.original_rows,
            summary.accepted_rows,
            summary.rejected_rows,
            unique_cust,
            default_currency,
            json.dumps(mapping),
            json.dumps(capabilities),
            0,
        ))
        conn.commit()

    return dataset_id


def delete_dataset(dataset_id: str) -> bool:
    """Delete a user-uploaded dataset. Built-in benchmark cannot be deleted."""
    if dataset_id == DEFAULT_DATASET_ID:
        raise ValueError("Cannot delete the built-in benchmark dataset.")

    _init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("DELETE FROM datasets WHERE dataset_id = ? AND is_builtin = 0", (dataset_id,))
        conn.commit()
        deleted = cursor.rowcount > 0

    if deleted:
        dataset_folder = DATASETS_DIR / dataset_id
        if dataset_folder.exists():
            import shutil
            shutil.rmtree(dataset_folder, ignore_errors=True)

    return deleted
