
"""Main navigation for the complete CustomerInsight AI dashboard."""

from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent


def page_if_available(path, title, icon):
    """Register a dashboard page if its Python file exists."""

    file_path = APP_DIR / path

    if not file_path.is_file():
        return None

    return st.Page(
        str(file_path),
        title=title,
        icon=icon,
    )


def main():
    """Organize the research into an understandable workflow."""

    sections = {
        "Research Overview": [
            page_if_available(
                "pages/research_overview.py",
                "Research Overview",
                ":material/dashboard:",
            ),
        ],
        "Understand the Data": [
            page_if_available(
                "pages/retail_data_explorer.py",
                "Retail Data Explorer",
                ":material/database:",
            ),
            page_if_available(
                "pages/rfm_intelligence.py",
                "RFM Intelligence",
                ":material/analytics:",
            ),
        ],
        "Customer Intelligence": [
            page_if_available(
                "customer_insights.py",
                "Customer Behaviour Explorer",
                ":material/groups:",
            ),
        ],
      
"Research Evidence": [
    page_if_available(
        "pages/research_findings.py",
        "Model Comparison & Stability",
        ":material/science:",
    ),
    page_if_available(
        "pages/model_validation_studio.py",
        "Model Validation Studio",
        ":material/tune:",
    ),
],

    }

    # Hide pages that have not been implemented yet.
    sections = {
        section: [page for page in pages if page is not None]
        for section, pages in sections.items()
    }

    sections = {
        section: pages
        for section, pages in sections.items()
        if pages
    }

    selected = st.navigation(
        sections,
        position="sidebar",
    )

    selected.run()


if __name__ == "__main__":
    main()
