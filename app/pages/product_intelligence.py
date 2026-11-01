"""Product catalog performance and market basket association rules."""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parents[1]
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_ui import (
    apply_styles, page_header, section_header,
    load_active_transactions, get_active_dataset_metadata,
    render_dataset_banner, show_chart,
)
from customerinsight.products import (
    get_product_rankings, get_lowest_performing_products,
    run_market_basket_analysis,
)
from customerinsight.ai_assistant import format_currency_symbol


@st.cache_data(show_spinner="Analyzing basket co-occurrences...")
def _cached_basket_rules(df: pd.DataFrame, min_support: float, min_confidence: float, min_lift: float):
    return run_market_basket_analysis(
        df,
        min_support=min_support,
        min_confidence=min_confidence,
        min_lift=min_lift,
        max_rules=50,
    )


def main():
    apply_styles()
    page_header(
        "Customer Intelligence / Catalog & Assortment", "Product & Basket Intelligence",
        "Identify bestselling products, catalog long-tail underperformers, and cross-sell association rules.",
        purpose="Discover which products drive top-line revenue, which items gather dust, and which item pairs are frequently purchased together in the same order.",
        benefit="Optimise merchandising, create data-backed bundle promotions, and enhance cross-sell recommendation engines.",
        technical="Computes item-level volume and revenue aggregates, and evaluates pairwise co-occurrence frequencies across unique basket invoices to generate support, confidence, and lift statistics.",
    )

    render_dataset_banner()
    meta = get_active_dataset_metadata()
    currency_code = meta.get("currency", "GBP")
    symbol = format_currency_symbol(currency_code)

    try:
        df = load_active_transactions()
    except Exception as e:
        st.error(f"Could not load active dataset: {e}")
        return

    if df.empty or "product_id" not in df.columns:
        st.warning("Product information is not mapped or available in this dataset.")
        return

    tab_catalog, tab_basket = st.tabs(["🏆 Product Rankings & Catalog", "🛒 Market Basket Analysis"])

    with tab_catalog:
        section_header("Catalog Performance", "Analyze product sales volume, gross revenue, and pricing.")

        sort_by = st.radio(
            "Rank By",
            options=["Revenue", "Units Sold"],
            index=0,
            horizontal=True,
        )
        sort_col = "revenue" if sort_by == "Revenue" else "units_sold"

        top_products = get_product_rankings(df, sort_by=sort_col, top_n=20)
        low_products = get_lowest_performing_products(df, bottom_n=10)

        # Catalog Metrics
        unique_products = df["product_id"].nunique()
        total_units = int(df["quantity"].sum())
        top_item_name = top_products.iloc[0]["product"] if not top_products.empty else "N/A"

        c1, c2, c3 = st.columns(3)
        c1.metric("Unique Catalog Items", f"{unique_products:,}")
        c2.metric("Total Units Dispatched", f"{total_units:,}")
        c3.metric("Top Bestseller", str(top_item_name)[:28] + ("..." if len(str(top_item_name)) > 28 else ""))

        st.write("")

        if not top_products.empty:
            chart_df = top_products.head(12).copy()
            chart_df["display_label"] = chart_df["product"].astype(str).str[:30]
            fig_prod = px.bar(
                chart_df.sort_values(sort_col, ascending=True),
                x=sort_col,
                y="display_label",
                orientation="h",
                title=f"Top 12 Products by {sort_by}",
                labels={
                    sort_col: f"Revenue ({symbol})" if sort_by == "Revenue" else "Units Sold",
                    "display_label": "Product",
                },
                color_discrete_sequence=["#147D72"],
            )
            fig_prod.update_layout(xaxis_title="", yaxis_title="")
            show_chart(fig_prod)

            with st.expander("View Top 20 Product Details Table"):
                st.dataframe(
                    top_products.style.format({
                        "revenue": f"{symbol}{{:,.2f}}",
                        "units_sold": "{:,}",
                        "orders": "{:,}",
                        "avg_price": f"{symbol}{{:,.2f}}",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )

        st.write("---")
        section_header("Underperforming Inventory / Long Tail", "Items with low sales volume that may indicate overstock or discontinuation candidates.")
        if not low_products.empty:
            st.dataframe(
                low_products.style.format({
                    "revenue": f"{symbol}{{:,.2f}}",
                    "units_sold": "{:,}",
                    "orders": "{:,}",
                    "avg_price": f"{symbol}{{:,.2f}}",
                }),
                use_container_width=True,
                hide_index=True,
            )

    with tab_basket:
        section_header("Market Basket Association Rules", "Discover item combinations that frequently co-occur in the same basket.")

        with st.expander("ℹ️ How to interpret Support, Confidence, and Lift", expanded=False):
            st.markdown(
                """
                - **Support**: Proportion of all customer orders that contain both Item A and Item B.
                - **Confidence**: When a customer buys Item A, how often does their basket also contain Item B?
                  *Formula: Orders(A + B) / Orders(A)*
                - **Lift**: How much more likely is Item B to be purchased when Item A is in the basket, compared to random chance?
                  *A Lift of 3.0 means customers buying Item A are **3 times more likely** to purchase Item B than average.*
                """
            )

        c_sup, c_conf, c_lift = st.columns(3)
        with c_sup:
            min_support = st.slider("Minimum Support", min_value=0.005, max_value=0.05, value=0.015, step=0.005, format="%.3f")
        with c_conf:
            min_confidence = st.slider("Minimum Confidence", min_value=0.10, max_value=0.80, value=0.20, step=0.05, format="%.2f")
        with c_lift:
            min_lift = st.slider("Minimum Lift", min_value=1.0, max_value=10.0, value=1.5, step=0.5, format="%.1f")

        run_calc = st.button("🔍 Find Association Rules", type="primary")
        if run_calc or st.session_state.get("_basket_rules_ready"):
            st.session_state["_basket_rules_ready"] = True
            rules_df = _cached_basket_rules(
                df,
                min_support=min_support,
                min_confidence=min_confidence,
                min_lift=min_lift,
            )

            if not rules_df.empty:
                st.success(f"Discovered **{len(rules_df)} association rules** matching your threshold criteria.")

                display_rules = rules_df.copy()
                st.dataframe(
                    display_rules.style.format({
                        "support": "{:.2%}",
                        "confidence": "{:.1%}",
                        "lift": "{:.2f}x",
                        "both_count": "{:,}",
                        "antecedent_count": "{:,}",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )

                csv_rules = rules_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Association Rules CSV",
                    data=csv_rules,
                    file_name="market_basket_rules.csv",
                    mime="text/csv",
                )
            else:
                st.info("No product pairs met the selected support, confidence, and lift thresholds. Try lowering the Minimum Support or Lift sliders.")
        else:
            st.info("Click 'Find Association Rules' to compute item co-occurrence metrics for this catalog.")


if __name__ == "__main__":
    main()
