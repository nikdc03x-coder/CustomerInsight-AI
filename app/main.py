"""Navigation for the CustomerInsight AI research dashboard."""

from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent


def main():
    """Present the implemented research pages in workflow order."""
    st.set_page_config(
        page_title="CustomerInsight AI",
        page_icon=":material/analytics:",
        layout="wide",
    )
    sections = {
        "Research Overview": [
            st.Page(
                str(APP_DIR / "pages/research_overview.py"),
                title="Research Overview", icon=":material/dashboard:",
            ),
        ],
        "Understand the Data": [
            st.Page(
                str(APP_DIR / "pages/retail_data_explorer.py"),
                title="Retail Data Explorer", icon=":material/database:",
            ),
            st.Page(
                str(APP_DIR / "pages/rfm_intelligence.py"),
                title="RFM Intelligence", icon=":material/analytics:",
            ),
        ],
        "Customer Intelligence": [
            st.Page(
                str(APP_DIR / "customer_insights.py"),
                title="Customer Behaviour Explorer", icon=":material/groups:",
            ),
        ],
        "Research Evidence": [
            st.Page(
                str(APP_DIR / "pages/research_findings.py"),
                title="Model Comparison & Stability", icon=":material/science:",
            ),
            st.Page(
                str(APP_DIR / "pages/model_validation_studio.py"),
                title="Model Validation Studio", icon=":material/tune:",
            ),
            st.Page(
                str(APP_DIR / "pages/research_health.py"),
                title="Research Quality Center", icon=":material/fact_check:",
            ),
        ],
    }
    st.navigation(sections, position="sidebar").run()


if __name__ == "__main__":
    main()
