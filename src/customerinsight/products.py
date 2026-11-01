"""Product intelligence, catalog performance, and Market Basket Analysis."""

from collections import Counter, defaultdict
from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd


def get_product_rankings(
    df: pd.DataFrame,
    top_n: int = 20,
    sort_by: str = "revenue",
) -> pd.DataFrame:
    """Analyze product sales performance across revenue, units, and customer reach."""
    if "product_name" not in df and "product_id" not in df:
        return pd.DataFrame(columns=["product", "revenue", "units_sold", "orders", "customers", "avg_price"])

    temp = df.copy()
    if "line_total" not in temp:
        temp["line_total"] = temp["quantity"] * temp["unit_price"]

    # Choose primary display label
    if "product_name" in temp and temp["product_name"].notna().any():
        item_col = "product_name"
    else:
        item_col = "product_id"

    temp = temp.loc[temp[item_col].notna() & temp[item_col].ne("")].copy()
    if temp.empty:
        return pd.DataFrame(columns=["product", "revenue", "units_sold", "orders", "customers", "avg_price"])

    grouped = (
        temp.groupby(item_col)
        .agg(
            revenue=("line_total", "sum"),
            units_sold=("quantity", "sum"),
            orders=("order_id", "nunique") if "order_id" in temp else ("line_total", "count"),
            customers=("customer_id", "nunique") if "customer_id" in temp else ("line_total", "count"),
        )
        .reset_index()
        .rename(columns={item_col: "product"})
    )

    grouped["avg_price"] = (grouped["revenue"] / grouped["units_sold"]).replace([np.inf, -np.inf], 0).round(2)
    grouped["revenue"] = grouped["revenue"].round(2)
    grouped["units_sold"] = grouped["units_sold"].round(0).astype("int64")

    sort_col = "revenue" if sort_by == "revenue" else "units_sold"
    return grouped.sort_values(sort_col, ascending=False).head(top_n).reset_index(drop=True)


def get_lowest_performing_products(
    df: pd.DataFrame,
    bottom_n: int = 20,
) -> pd.DataFrame:
    """Identify catalog items with the lowest positive sales volume."""
    rankings = get_product_rankings(df, top_n=len(df), sort_by="revenue")
    if rankings.empty:
        return rankings
    # Filter for products with positive revenue
    positive = rankings.loc[rankings["revenue"] > 0]
    return positive.sort_values("revenue", ascending=True).head(bottom_n).reset_index(drop=True)


def run_market_basket_analysis(
    df: pd.DataFrame,
    min_support: float = 0.01,
    min_confidence: float = 0.1,
    min_lift: float = 1.0,
    max_rules: int = 50,
) -> pd.DataFrame:
    """Discover frequent itemsets and association rules using an efficient transaction-cooccurrence algorithm.

    Metrics calculated:
    - Support: P(A and B) = (Orders containing both A and B) / (Total Orders)
    - Confidence: P(B|A) = Support(A and B) / Support(A)
    - Lift: Support(A and B) / (Support(A) * Support(B))

    Note: Lift > 1 indicates items appear together more frequently than expected by chance (association, not causation).
    """
    if "order_id" not in df:
        return pd.DataFrame(columns=["antecedent", "consequent", "support", "confidence", "lift", "order_count"])

    item_col = "product_name" if "product_name" in df and df["product_name"].notna().any() else "product_id"
    if item_col not in df:
        return pd.DataFrame(columns=["antecedent", "consequent", "support", "confidence", "lift", "order_count"])

    valid = df.loc[df["order_id"].notna() & df[item_col].notna() & df[item_col].ne("")].copy()
    if valid.empty:
        return pd.DataFrame(columns=["antecedent", "consequent", "support", "confidence", "lift", "order_count"])

    # Build basket sets per order efficiently
    order_items = defaultdict(set)
    for oid, item in zip(valid["order_id"], valid[item_col]):
        order_items[oid].add(item)
    baskets = list(order_items.values())
    total_orders = len(baskets)
    if total_orders < 2:
        return pd.DataFrame(columns=["antecedent", "consequent", "support", "confidence", "lift", "order_count"])

    # 1. Count individual item frequencies
    item_counts: Counter[str] = Counter()
    for basket in baskets:
        item_counts.update(basket)

    # Filter single items by min_support
    min_count = max(1, int(min_support * total_orders))
    frequent_items = {item: count for item, count in item_counts.items() if count >= min_count}

    if len(frequent_items) < 2:
        # If threshold is too strict, dynamically fallback to top 50 items
        frequent_items = dict(item_counts.most_common(50))
        min_count = 1

    # 2. Count pair co-occurrences (capping basket size at 30 items to prevent combinatorial explosion on wholesale orders)
    pair_counts: Counter[tuple[str, str]] = Counter()
    for basket in baskets:
        filtered_basket = sorted([item for item in basket if item in frequent_items])[:30]
        if len(filtered_basket) >= 2:
            for pair in combinations(filtered_basket, 2):
                pair_counts[pair] += 1

    # 3. Calculate association rules for both directions (A -> B and B -> A)
    rules = []
    for (item_a, item_b), pair_count in pair_counts.items():
        if pair_count < min_count:
            continue

        pair_support = pair_count / total_orders
        supp_a = frequent_items[item_a] / total_orders
        supp_b = frequent_items[item_b] / total_orders

        # Direction 1: item_a -> item_b
        conf_a_b = pair_support / supp_a
        lift_a_b = conf_a_b / supp_b

        if conf_a_b >= min_confidence and lift_a_b >= min_lift:
            rules.append({
                "antecedent": item_a,
                "consequent": item_b,
                "support": round(pair_support, 4),
                "confidence": round(conf_a_b, 4),
                "lift": round(lift_a_b, 3),
                "order_count": pair_count,
            })

        # Direction 2: item_b -> item_a
        conf_b_a = pair_support / supp_b
        lift_b_a = conf_b_a / supp_a

        if conf_b_a >= min_confidence and lift_b_a >= min_lift:
            rules.append({
                "antecedent": item_b,
                "consequent": item_a,
                "support": round(pair_support, 4),
                "confidence": round(conf_b_a, 4),
                "lift": round(lift_b_a, 3),
                "order_count": pair_count,
            })

    if not rules:
        return pd.DataFrame(columns=["antecedent", "consequent", "support", "confidence", "lift", "order_count"])

    result_df = pd.DataFrame(rules).sort_values(["lift", "confidence"], ascending=[False, False])
    return result_df.head(max_rules).reset_index(drop=True)
