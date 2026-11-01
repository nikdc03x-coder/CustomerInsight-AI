"""Automated strategic business insights engine."""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parents[1]
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

import streamlit as st
import pandas as pd

from dashboard_ui import (
    apply_styles, page_header, section_header,
    load_active_transactions, get_active_dataset_metadata,
    render_dataset_banner,
)
from customerinsight.insights_engine import generate_business_insights


def render_priority_badge(priority: str):
    colors = {
        "High": ("#D9534F", "rgba(217, 83, 79, 0.15)"),
        "Medium": ("#CF9950", "rgba(207, 153, 80, 0.15)"),
        "Low": ("#147D72", "rgba(20, 125, 114, 0.15)"),
    }
    fg, bg = colors.get(priority, ("#8195A5", "rgba(128, 148, 164, 0.15)"))
    return f'<span style="padding:.2rem .55rem; border-radius:100px; font-size:.72rem; font-weight:700; color:{fg}; background:{bg};">{priority.upper()} PRIORITY</span>'


@st.cache_data(show_spinner="Evaluating statistical business insights...")
def _get_insights(df: pd.DataFrame, currency: str = "GBP"):
    return generate_business_insights(df, currency=currency)


def main():
    apply_styles()
    page_header(
        "AI & Strategy / Prescriptive Recommendations", "Business Insights Engine",
        "Automated, evidence-backed findings across revenue concentration, churn risk, single-order retention, and cross-sell.",
        purpose="Translate complex transaction patterns into prioritized executive summaries and actionable marketing/operational tactics.",
        benefit="Saves leadership hours of manual querying and provides immediate business guidance backed by empirical transaction data.",
        technical="Evaluates statistical distribution rules across customer RFM deciles, basket association matrices, and historical transaction cadences.",
    )

    render_dataset_banner()
    meta = get_active_dataset_metadata()
    currency = meta.get("currency", "GBP")

    try:
        df = load_active_transactions()
    except Exception as e:
        st.error(f"Could not load active dataset: {e}")
        return

    if df.empty:
        st.warning("Active dataset has no transaction records.")
        return

    insights = _get_insights(df, currency=currency)

    # Filter controls
    f_col1, f_col2 = st.columns([1, 1])
    with f_col1:
        categories = ["All Categories"] + sorted(list({ins.category for ins in insights}))
        selected_cat = st.selectbox("Filter Category", options=categories)
    with f_col2:
        priorities = ["All Priorities", "High", "Medium", "Low"]
        selected_pri = st.selectbox("Filter Priority", options=priorities)

    filtered = [
        ins for ins in insights
        if (selected_cat == "All Categories" or ins.category == selected_cat)
        and (selected_pri == "All Priorities" or ins.priority == selected_pri)
    ]

    st.write("")
    section_header(f"Active Insights ({len(filtered)} findings)", "Review strategic findings and corresponding recommendations.")

    for ins in filtered:
        with st.container(border=True):
            badge_html = render_priority_badge(ins.priority)
            st.markdown(
                f"""<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:.5rem;">
                    <span style="font-size:.75rem; text-transform:uppercase; font-weight:700; color:var(--ci-muted);">{ins.category}</span>
                    {badge_html}
                </div>""",
                unsafe_allow_html=True,
            )

            st.markdown(f"### {ins.title}")
            st.write(ins.observation)

            if ins.supporting_metric:
                st.info(f"📊 **Evidence Metric:** {ins.supporting_metric}")

            if ins.business_impact:
                st.caption(f"💼 **Business Impact:** {ins.business_impact}")

            # Recommendation Box
            st.markdown(
                f"""<div style="margin-top:.8rem; padding:.8rem 1rem; border-left:3px solid #147D72;
                background:var(--ci-surface); border-radius:0 8px 8px 0;">
                    <strong style="color:var(--ci-text);">Actionable Recommendation:</strong>
                    <p style="margin:.3rem 0 0; color:var(--ci-text);">{ins.recommended_action}</p>
                </div>""",
                unsafe_allow_html=True,
            )
            if ins.limitations:
                st.caption(f"⚠️ *Limitation: {ins.limitations}*")

    # Export Insights
    st.write("---")
    export_text = "# Executive Business Insights Report\n\n"
    for ins in insights:
        export_text += f"## [{ins.priority.upper()}] {ins.title}\n"
        export_text += f"**Category:** {ins.category}\n\n"
        export_text += f"**Observation:** {ins.observation}\n\n"
        export_text += f"**Evidence Metric:** {ins.supporting_metric}\n\n"
        export_text += f"**Business Impact:** {ins.business_impact}\n\n"
        export_text += f"**Recommendation:** {ins.recommended_action}\n\n"
        export_text += f"**Limitations:** {ins.limitations}\n\n"
        export_text += "---\n\n"

    st.download_button(
        label="📥 Download Complete Insights Brief (Markdown)",
        data=export_text,
        file_name="business_insights_brief.md",
        mime="text/markdown",
    )


if __name__ == "__main__":
    main()
