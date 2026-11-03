"""Products package stub for CustomerInsight AI.

This module provides minimal placeholder implementations required for the
test suite and application imports. The real product‑related analytics are
outside the current scope of the repository, so we expose only the
`run_market_basket_analysis` function with a simple signature that returns an
empty pandas DataFrame.

If downstream code expects additional columns, they can be added later
without breaking the public API.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["run_market_basket_analysis"]


def get_product_rankings(df: pd.DataFrame, top_n: int = 10, sort_by: str = "revenue") -> pd.DataFrame:
    """Calculate product rankings based on revenue and units sold.

    Parameters
    ----------
    df : pd.DataFrame
        Transaction data after cleaning (canonical schema).
    top_n : int, optional
        Maximum number of products to return. Defaults to 10.
    sort_by : str, optional
        Column to sort by – currently only ``"revenue"`` is supported.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``product`` (product_name), ``revenue`` and ``units_sold``.
        Sorted descending by the chosen metric and limited to ``top_n`` rows.
    """
    import pandas as pd

    if df.empty:
        return pd.DataFrame()
    # Aggregate revenue and quantity per product name
    agg = (
        df.groupby("product_name")
        .agg(revenue=("line_total", "sum"), units_sold=("quantity", "sum"))
        .reset_index()
        .rename(columns={"product_name": "product"})
    )
    # Sort by revenue descending (only option supported for now)
    if sort_by == "revenue":
        agg = agg.sort_values("revenue", ascending=False)
    # Limit to top_n
    if top_n is not None:
        agg = agg.head(top_n)
    return agg.reset_index(drop=True)



def get_lowest_performing_products(*args, **kwargs):
    """Placeholder returning empty DataFrame for lowest‑performing products."""
    import pandas as pd
    return pd.DataFrame()


def run_market_basket_analysis(df: pd.DataFrame, min_support: float = 0.01, min_confidence: float = 0.1, min_lift: float = 1.0, max_rules: int = 100) -> pd.DataFrame:
    """Simple market‑basket analysis returning association rules.

    Parameters
    ----------
    df : pd.DataFrame
        Canonical transaction data.
    min_support, min_confidence, min_lift, max_rules : float / int
        Thresholds for rule generation – used loosely in this lightweight
        implementation.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``antecedent``, ``consequent``, ``support``,
        ``confidence`` and ``lift``. May be empty if no co‑purchased items are
        found.
    """
    import pandas as pd
    from itertools import combinations

    if df.empty:
        return pd.DataFrame(columns=["antecedent", "consequent", "support", "confidence", "lift"])

    # Build list of products per order
    order_products = (
        df.groupby("order_id")["product_name"]
        .apply(lambda xs: list(set(xs)))
        .reset_index(name="products")
    )
    # Count occurrences of each item and each pair
    item_counts = {}
    pair_counts = {}
    total_orders = len(order_products)
    for prod_list in order_products["products"]:
        for item in prod_list:
            item_counts[item] = item_counts.get(item, 0) + 1
        for a, b in combinations(sorted(prod_list), 2):
            pair = (a, b)
            pair_counts[pair] = pair_counts.get(pair, 0) + 1
    # Build rules DataFrame
    rows = []
    for (a, b), pair_cnt in pair_counts.items():
        support = pair_cnt / total_orders
        if support < min_support:
            continue
        confidence = pair_cnt / item_counts[a]
        if confidence < min_confidence:
            continue
        lift = confidence / (item_counts[b] / total_orders) if item_counts[b] else 0
        if lift < min_lift:
            continue
        rows.append({
            "antecedent": a,
            "consequent": b,
            "support": round(support, 4),
            "confidence": round(confidence, 4),
            "lift": round(lift, 4),
        })
        if len(rows) >= max_rules:
            break
    return pd.DataFrame(rows, columns=["antecedent", "consequent", "support", "confidence", "lift"])