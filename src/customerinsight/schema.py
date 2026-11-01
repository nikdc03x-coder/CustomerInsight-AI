"""Canonical schema definition and automatic column mapping for customer transactions."""

from dataclasses import dataclass
import re
from typing import Any

import numpy as np
import pandas as pd


CANONICAL_FIELDS = {
    "customer_id": {
        "required_for_rfm": True,
        "type": "string",
        "description": "Unique customer identifier",
        "synonyms": [
            "customerid", "customer_id", "customer", "client_id", "clientid",
            "user_id", "userid", "buyer_id", "buyerid", "account_id",
            "customerno", "customer_no", "customer_number",
        ],
    },
    "order_id": {
        "required_for_rfm": True,
        "type": "string",
        "description": "Unique transaction or invoice identifier",
        "synonyms": [
            "orderid", "order_id", "invoiceno", "invoice_no", "invoiceid",
            "invoice_id", "invoice", "transaction_id", "transactionid",
            "receipt_id", "receiptid", "order_number", "orderno",
        ],
    },
    "order_date": {
        "required_for_rfm": True,
        "type": "datetime",
        "description": "Date and time of purchase",
        "synonyms": [
            "orderdate", "order_date", "invoicedate", "invoice_date",
            "date", "timestamp", "transaction_date", "transactiondate",
            "created_at", "purchase_date", "purchasedate",
        ],
    },
    "product_id": {
        "required_for_rfm": False,
        "type": "string",
        "description": "Unique stock or product identifier",
        "synonyms": [
            "productid", "product_id", "stockcode", "stock_code",
            "sku", "item_id", "itemid", "item_code", "itemcode",
            "product_code", "productcode",
        ],
    },
    "product_name": {
        "required_for_rfm": False,
        "type": "string",
        "description": "Product title or description",
        "synonyms": [
            "productname", "product_name", "description", "item_name",
            "itemname", "product_description", "productdescription",
            "item_description", "itemdescription", "itemdesc",
            "title", "name", "product",
        ],
    },
    "quantity": {
        "required_for_rfm": True,
        "type": "numeric",
        "description": "Quantity of items purchased",
        "synonyms": [
            "quantity", "qty", "units", "items", "count", "amount",
            "volume", "num_items",
        ],
    },
    "unit_price": {
        "required_for_rfm": True,
        "type": "numeric",
        "description": "Unit sale price per item",
        "synonyms": [
            "unitprice", "unit_price", "price", "item_price",
            "itemprice", "rate", "cost_per_unit", "unit_cost",
        ],
    },
    "currency": {
        "required_for_rfm": False,
        "type": "string",
        "description": "ISO currency code (e.g., GBP, USD, EUR)",
        "synonyms": ["currency", "curr", "currency_code", "currencycode"],
    },
    "country": {
        "required_for_rfm": False,
        "type": "string",
        "description": "Country or geographic region of sale",
        "synonyms": [
            "country", "nation", "region", "country_name",
            "billing_country", "shipping_country",
        ],
    },
}


def _clean_str(value: str) -> str:
    """Normalize a string for flexible matching."""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def detect_column_mappings(columns: list[str]) -> dict[str, str | None]:
    """Auto-detect mapping from raw file columns to canonical schema fields.

    Returns a dict mapping canonical_field -> raw_column_name (or None if unmatched).
    """
    cleaned_raw = {_clean_str(col): col for col in columns}
    mapping: dict[str, str | None] = {}
    used_raw_cols: set[str] = set()

    for canonical_field, spec in CANONICAL_FIELDS.items():
        matched_raw = None

        # Check exact field name first
        clean_field = _clean_str(canonical_field)
        if clean_field in cleaned_raw and cleaned_raw[clean_field] not in used_raw_cols:
            matched_raw = cleaned_raw[clean_field]

        # Check synonyms if not found
        if matched_raw is None:
            for syn in spec["synonyms"]:
                clean_syn = _clean_str(syn)
                if clean_syn in cleaned_raw and cleaned_raw[clean_syn] not in used_raw_cols:
                    matched_raw = cleaned_raw[clean_syn]
                    break

        mapping[canonical_field] = matched_raw
        if matched_raw:
            used_raw_cols.add(matched_raw)

    return mapping


def assess_capabilities(mapping: dict[str, str | None]) -> dict[str, bool]:
    """Determine which analytical capabilities can be computed from the mapped columns."""
    has_customer = bool(mapping.get("customer_id"))
    has_order = bool(mapping.get("order_id"))
    has_date = bool(mapping.get("order_date"))
    has_qty = bool(mapping.get("quantity"))
    has_price = bool(mapping.get("unit_price"))
    has_product = bool(mapping.get("product_id") or mapping.get("product_name"))
    has_country = bool(mapping.get("country"))

    can_rfm = has_customer and has_order and has_date and has_qty and has_price
    can_revenue = has_order and has_date and has_qty and has_price
    can_products = has_product and has_qty and has_price
    can_basket = has_order and has_product
    can_geo = has_country and has_qty and has_price

    return {
        "rfm_segmentation": can_rfm,
        "revenue_analytics": can_revenue,
        "product_intelligence": can_products,
        "market_basket_analysis": can_basket,
        "geographic_breakdown": can_geo,
    }


def coerce_canonical_types(
    df: pd.DataFrame,
    mapping: dict[str, str | None],
    default_currency: str = "GBP",
) -> pd.DataFrame:
    """Project a raw DataFrame into the canonical schema with strictly typed columns."""
    standardized = pd.DataFrame(index=df.index)

    # 1. Text identifier columns (preserve leading zeros as strings)
    for field in ["customer_id", "order_id", "product_id", "product_name", "country"]:
        raw_col = mapping.get(field)
        if raw_col and raw_col in df.columns:
            standardized[field] = df[raw_col].astype("string").str.strip()
        else:
            standardized[field] = pd.Series(pd.NA, index=df.index, dtype="string")

    # 2. Date column
    date_col = mapping.get("order_date")
    if date_col and date_col in df.columns:
        standardized["order_date"] = pd.to_datetime(df[date_col], errors="coerce")
    else:
        standardized["order_date"] = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")

    # 3. Numeric columns
    for field in ["quantity", "unit_price"]:
        raw_col = mapping.get(field)
        if raw_col and raw_col in df.columns:
            standardized[field] = pd.to_numeric(df[raw_col], errors="coerce")
        else:
            standardized[field] = pd.Series(np.nan, index=df.index, dtype="float64")

    # 4. Currency column
    curr_col = mapping.get("currency")
    if curr_col and curr_col in df.columns:
        standardized["currency"] = (
            df[curr_col].astype("string").str.strip().str.upper().fillna(default_currency)
        )
    else:
        standardized["currency"] = pd.Series(default_currency, index=df.index, dtype="string")

    # 5. Line Total calculation (Gross spending)
    standardized["line_total"] = standardized["quantity"] * standardized["unit_price"]

    # 6. Cancellation flag: starts with 'C' in order_id or negative quantity
    is_c_order = standardized["order_id"].str.upper().str.startswith("C").fillna(False)
    is_neg_qty = standardized["quantity"] < 0
    standardized["is_cancellation"] = is_c_order | is_neg_qty

    return standardized
