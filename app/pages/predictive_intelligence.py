"""Predictive customer intelligence: recurrence estimation, churn risk, and CLV projection."""

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
from customerinsight.prediction import (
    assess_predictive_eligibility,
    predict_customer_recurrence_and_clv,
)
from customerinsight.ai_assistant import format_currency_symbol


@st.cache_data(show_spinner="Computing forward recurrence and spend projections...")
def _get_predictions(df: pd.DataFrame, projection_days: int = 90):
    return predict_customer_recurrence_and_clv(df, projection_days=projection_days)


def main():
    apply_styles()
    page_header(
        "Customer Intelligence / Machine Learning & Forecasting", "Predictive CLV & Churn",
        "Estimate repeat purchase probabilities, classify customer churn risk, and project 90-day forward spend.",
        purpose="Identify accounts likely to churn, prioritize retention outreach for high-value customers, and forecast near-term cohort cashflow.",
        benefit="Shifts customer analytics from reactive backward reporting to proactive forward-looking retention and budget allocation.",
        technical="Fits an empirical Bayesian recurrence formulation based on inter-purchase intervals and recency decay, applying expected transaction multipliers to historical order values.",
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

    # Eligibility Check
    eligibility = assess_predictive_eligibility(df)
    if not eligibility.get("eligible", False):
        st.warning(f"⚠️ **Dataset is not currently eligible for forward predictive modeling:** {eligibility.get('reason', '')}")
        st.info("Predictive models require multi-month transaction histories and a meaningful sample of repeat purchases.")
        return

    # Run predictions
    pred_df = _get_predictions(df, projection_days=90)
    if pred_df.empty:
        st.info("No customer records met the criteria for prediction.")
        return

    # KPI summary metrics
    total_proj_spend = pred_df["predicted_spend_90d"].sum()
    avg_recurrence = pred_df["p_active"].mean()
    high_risk_mask = pred_df["churn_risk"].str.startswith("High Risk")
    high_risk_count = high_risk_mask.sum()
    vip_threshold = pred_df["predicted_spend_90d"].quantile(0.75)
    vip_at_risk = (high_risk_mask & (pred_df["predicted_spend_90d"] >= vip_threshold)).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Predicted 90-Day Revenue", f"{symbol}{total_proj_spend:,.2f}")
    c2.metric("Mean Recurrence Probability", f"{avg_recurrence:.1%}")
    c3.metric("At-Risk Accounts", f"{high_risk_count:,}")
    c4.metric("VIP Accounts at Risk", f"{vip_at_risk:,}", help="Top quartile accounts currently in High Risk tier")

    st.write("---")

    # Risk Distribution Chart & Details
    col_chart, col_table = st.columns([1, 1], gap="large")

    with col_chart:
        section_header("Churn Risk Distribution", "Classification based on recency decay and inter-purchase interval.")
        tier_counts = pred_df["churn_risk"].value_counts().reset_index()
        tier_counts.columns = ["churn_risk", "count"]

        color_map = {
            "Low Risk (Active)": "#147D72",
            "Medium Risk (Slowing)": "#CF9950",
            "High Risk (At-Risk / Lapsed)": "#D9534F",
        }

        fig_risk = px.pie(
            tier_counts,
            values="count",
            names="churn_risk",
            hole=0.55,
            title="Customer Base Churn Risk",
            color="churn_risk",
            color_discrete_map=color_map,
        )
        fig_risk.update_traces(textposition="inside", textinfo="percent+label")
        show_chart(fig_risk)

    with col_table:
        section_header("Tier Breakdown Summary", "Aggregated projected spend across risk cohorts.")
        summary_agg = pred_df.groupby("churn_risk").agg(
            customers=("customer_id", "count"),
            avg_recurrence=("p_active", "mean"),
            projected_spend=("predicted_spend_90d", "sum"),
        ).reset_index()

        st.dataframe(
            summary_agg.style.format({
                "customers": "{:,}",
                "avg_recurrence": "{:.1%}",
                "projected_spend": f"{symbol}{{:,.2f}}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    st.write("---")

    # Detailed Customer Predictions Table
    section_header("Customer Forecast Explorer", "Individual customer recurrence, expected order cadence, and projected spend.")

    f1, f2 = st.columns(2)
    with f1:
        tier_options = ["All Customers"] + sorted(pred_df["churn_risk"].unique().tolist())
        tier_filter = st.selectbox("Filter Risk Tier", options=tier_options)
    with f2:
        vip_only = st.checkbox("Only VIP Customers (Top 25% Forecast Spend)", value=False)

    filtered_preds = pred_df.copy()
    if tier_filter != "All Customers":
        filtered_preds = filtered_preds[filtered_preds["churn_risk"] == tier_filter]
    if vip_only:
        filtered_preds = filtered_preds[filtered_preds["predicted_spend_90d"] >= vip_threshold]

    st.caption(f"Showing {len(filtered_preds):,} of {len(pred_df):,} customers")

    display_table = filtered_preds[[
        "customer_id", "churn_risk", "p_active", "expected_orders_90d",
        "predicted_spend_90d", "recency_days", "orders",
    ]].head(100)

    st.dataframe(
        display_table.style.format({
            "p_active": "{:.1%}",
            "expected_orders_90d": "{:.2f}",
            "predicted_spend_90d": f"{symbol}{{:,.2f}}",
            "recency_days": "{:.0f} days",
            "orders": "{:,}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    csv_preds = filtered_preds.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Full Customer Predictions CSV",
        data=csv_preds,
        file_name="customer_clv_predictions.csv",
        mime="text/csv",
    )

    st.write("---")
    with st.expander("🔬 Statistical Assumptions and Methodological Limitations", expanded=False):
        st.markdown(
            f"""
            - **Inter-Purchase Cadence**: Recurrence probabilities assume an exponential decay with rate proportional to each customer's individual historical order frequency and elapsed days since last purchase.
            - **Stationarity**: Spending projections assume the customer's average order value remains stationary over the 90-day forecast horizon.
            - **Exogenous Factors**: Projections do not model macroeconomic disruptions, product catalog discontinuations, or major marketing campaigns.
            - **Eligibility Benchmark**: Analysis was performed with {eligibility.get('repeat_customers_pct', 0):.1f}% repeat buyers across {eligibility.get('total_days', 0)} days of recorded activity.
            """
        )


if __name__ == "__main__":
    main()
