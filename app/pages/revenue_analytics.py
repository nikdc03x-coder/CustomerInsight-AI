"""Revenue analytics and top-line performance dashboard."""

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
from customerinsight.analytics import (
    get_revenue_kpis, get_revenue_trend,
    get_revenue_by_country, get_top_customers,
)
from customerinsight.ai_assistant import format_currency_symbol


def main():
    apply_styles()
    page_header(
        "Customer Intelligence / Financial Performance", "Revenue Analytics",
        "Monitor gross revenue, average order value, sales momentum across time, and geographic revenue concentration.",
        purpose="Analyze the financial dynamics of customer transactions, track timeline trends, and identify the highest-spending customer accounts.",
        benefit="Connects customer behaviour directly to revenue growth, order volume, and geographic distribution.",
        technical="Computes exact aggregations over verified canonical transactions, grouping by periodic date frequencies and order identifiers.",
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

    if df.empty:
        st.warning("Active dataset has no transaction records.")
        return

    # Top-line KPI Cards
    kpis = get_revenue_kpis(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Gross Revenue", f"{symbol}{kpis['total_revenue']:,.2f}")
    c2.metric("Completed Orders", f"{kpis['total_orders']:,}")
    c3.metric("Average Order Value", f"{symbol}{kpis['average_order_value']:,.2f}")
    c4.metric("Unique Customers", f"{kpis['total_customers']:,}")
    c5.metric("Avg Spend / Customer", f"{symbol}{kpis['average_customer_spend']:,.2f}")

    st.write("---")

    # Revenue Trend Section
    section_header("Revenue Over Time", "Track periodic sales momentum, transaction volumes, and seasonality.")
    freq_choice = st.radio(
        "Aggregation Interval",
        options=["Daily", "Weekly", "Monthly"],
        index=2,
        horizontal=True,
    )
    freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M"}
    trend_df = get_revenue_trend(df, freq=freq_map[freq_choice])

    if not trend_df.empty:
        trend_df["date_str"] = trend_df["period"].dt.strftime("%Y-%m-%d")
        fig_trend = px.line(
            trend_df,
            x="period",
            y="revenue",
            markers=True,
            title=f"{freq_choice} Gross Revenue ({currency_code})",
            labels={"period": "Timeline", "revenue": f"Revenue ({symbol})"},
            hover_data={"orders": ":,", "active_customers": ":,", "revenue": f":,.2f"},
        )
        fig_trend.update_traces(line_color="#147D72", line_width=2.5)
        fig_trend.update_layout(xaxis_title="", yaxis_title=f"Revenue ({symbol})", hovermode="x unified")
        show_chart(fig_trend)
    else:
        st.info("Insufficient timestamp range to plot revenue trend.")

    st.write("---")

    # Geographic Breakdown and Top Customers in 2 columns
    col_geo, col_top = st.columns([1, 1], gap="large")

    with col_geo:
        section_header("Geographic Distribution", "Top countries generating sales revenue.")
        if "country" in df.columns and df["country"].notna().sum() > 0:
            geo_df = get_revenue_by_country(df)
            if not geo_df.empty:
                top_10_geo = geo_df.head(10).copy()
                fig_geo = px.bar(
                    top_10_geo.sort_values("revenue", ascending=True),
                    x="revenue",
                    y="country",
                    orientation="h",
                    title="Top 10 Countries by Revenue",
                    labels={"revenue": f"Revenue ({symbol})", "country": "Country"},
                    color_discrete_sequence=["#5779B3"],
                    text_auto=".2s",
                )
                fig_geo.update_layout(xaxis_title=f"Revenue ({symbol})", yaxis_title="")
                show_chart(fig_geo)

                with st.expander("View Full Country Revenue Table"):
                    st.dataframe(
                        geo_df.style.format({
                            "revenue": f"{symbol}{{:,.2f}}",
                            "orders": "{:,}",
                            "customers": "{:,}",
                            "revenue_share_pct": "{:.1f}%",
                        }),
                        use_container_width=True,
                        hide_index=True,
                    )
            else:
                st.info("No country records found.")
        else:
            st.info("Country field is not mapped for this dataset.")

    with col_top:
        section_header("Top Spending Accounts", "Highest gross revenue generating customers.")
        top_n = st.selectbox("Show Top Customers", options=[10, 25, 50], index=0)
        top_cust_df = get_top_customers(df, top_n=top_n)

        if not top_cust_df.empty:
            display_df = top_cust_df.copy()
            st.dataframe(
                display_df.style.format({
                    "total_spend": f"{symbol}{{:,.2f}}",
                    "total_orders": "{:,}",
                    "average_order_value": f"{symbol}{{:,.2f}}",
                    "first_purchase": lambda x: pd.to_datetime(x).strftime("%Y-%m-%d"),
                    "last_purchase": lambda x: pd.to_datetime(x).strftime("%Y-%m-%d"),
                }),
                use_container_width=True,
                hide_index=True,
            )

            csv_data = top_cust_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"📥 Download Top {top_n} Customers CSV",
                data=csv_data,
                file_name=f"top_{top_n}_customers.csv",
                mime="text/csv",
            )
        else:
            st.info("No customer transaction data available.")


if __name__ == "__main__":
    main()
