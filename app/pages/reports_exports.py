"""Executive brief reporting and structured data export center."""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parents[1]
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))


import streamlit as st

from dashboard_ui import (
    apply_styles, page_header, section_header,
    load_active_transactions, get_active_dataset_metadata,
    render_dataset_banner,
)
from customerinsight.reporting import (
    generate_executive_brief_markdown,
    export_customer_segments_csv,
)
from customerinsight.analytics import get_revenue_trend
from customerinsight.products import get_product_rankings
from customerinsight.prediction import predict_customer_recurrence_and_clv, assess_predictive_eligibility


@st.cache_data(show_spinner="Synthesizing executive brief...")
def _get_brief(df, dataset_name, currency):
    return generate_executive_brief_markdown(
        df,
        dataset_name=dataset_name,
        currency=currency,
    )


def main():
    apply_styles()
    page_header(
        "AI & Strategy / Reporting & Exports", "Reports & Exports",
        "Generate executive-ready summary briefs and export enriched customer segment datasets for CRM and downstream workflows.",
        purpose="Produce shareable reports for leadership and download structured customer lists for marketing campaigns.",
        benefit="Eliminates manual presentation preparation and provides instant data sync with CRM/marketing automation tools.",
        technical="Generates formatted Markdown documents aggregating core KPIs and compiles clean CSV files with segment labels, RFM scores, and predictive probabilities.",
    )

    render_dataset_banner()
    meta = get_active_dataset_metadata()
    dataset_name = meta.get("display_name", "Active Dataset")
    currency = meta.get("currency", "GBP")

    try:
        df = load_active_transactions()
    except Exception as e:
        st.error(f"Could not load active dataset: {e}")
        return

    if df.empty:
        st.warning("Active dataset has no transaction records.")
        return

    tab_brief, tab_exports = st.tabs(["📄 Executive Brief", "📥 Data Export Center"])

    with tab_brief:
        section_header("Executive Summary Brief", "Synthesized overview of active workspace metrics and strategic findings.")

        brief_md = _get_brief(df, dataset_name, currency)

        st.download_button(
            label="📥 Download Executive Brief (.md)",
            data=brief_md,
            file_name=f"executive_brief_{meta.get('dataset_id', 'dataset')}.md",
            mime="text/markdown",
            type="primary",
        )

        st.write("---")
        with st.container(border=True):
            st.markdown(brief_md)

    with tab_exports:
        section_header("Export Analytical Datasets", "Download clean, enriched CSV files for CRM activation or external BI tools.")

        # 1. Customer Segments Export
        with st.container(border=True):
            st.markdown("### 1. Customer RFM & Segmentation Export")
            st.caption("Includes Customer ID, Recency (days), Frequency (orders), Monetary (gross spend), and Assigned Persona / Cluster.")
            if st.button("Generate Customer Segments Export", key="btn_exp_segments"):
                with st.spinner("Compiling customer segments..."):
                    csv_segments = export_customer_segments_csv(df)
                    st.download_button(
                        label="⬇️ Download Customer Segments CSV",
                        data=csv_segments,
                        file_name="customer_segments_enriched.csv",
                        mime="text/csv",
                    )

        # 2. Product Rankings Export
        with st.container(border=True):
            st.markdown("### 2. Product Catalog Rankings Export")
            st.caption("Includes Product ID, Name, Total Units Sold, Gross Revenue, Orders Count, and Average Selling Price.")
            if st.button("Generate Product Performance Export", key="btn_exp_products"):
                with st.spinner("Compiling product performance..."):
                    prod_df = get_product_rankings(df, top_n=5000)
                    csv_products = prod_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="⬇️ Download Product Catalog CSV",
                        data=csv_products,
                        file_name="product_catalog_performance.csv",
                        mime="text/csv",
                    )

        # 3. Revenue Trend Export
        with st.container(border=True):
            st.markdown("### 3. Periodic Revenue Trend Export")
            st.caption("Aggregated daily revenue, transaction order volume, and unit dispatch counts.")
            if st.button("Generate Daily Revenue Trend Export", key="btn_exp_trend"):
                with st.spinner("Compiling revenue trend..."):
                    trend_df = get_revenue_trend(df, freq="D")
                    csv_trend = trend_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="⬇️ Download Revenue Trend CSV",
                        data=csv_trend,
                        file_name="daily_revenue_trend.csv",
                        mime="text/csv",
                    )

        # 4. Predictive Intelligence Export
        with st.container(border=True):
            st.markdown("### 4. Predictive Churn & CLV Export")
            st.caption("Individual recurrence probability, churn risk classification tier, and 90-day forward spend projection.")
            elig = assess_predictive_eligibility(df)
            if elig.get('eligible', False):
                if st.button("Generate Predictive CLV & Churn Export", key="btn_exp_predict"):
                    with st.spinner("Compiling predictions..."):
                        pred_df = predict_customer_recurrence_and_clv(df, projection_days=90)
                        csv_pred = pred_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="⬇️ Download Predictive CLV CSV",
                            data=csv_pred,
                            file_name="predictive_clv_and_churn.csv",
                            mime="text/csv",
                        )
            else:
                st.info("Predictive model export is unavailable because this dataset does not meet minimum repeat purchase criteria.")


if __name__ == "__main__":
    main()
