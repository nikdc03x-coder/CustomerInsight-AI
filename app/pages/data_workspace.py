# -*- coding: utf-8 -*-
"""Data Workspace page – now operates on the single built‑in Online Retail dataset.
All upload / multi‑dataset logic has been removed. The page displays a quick
overview, preview and quality summary of the benchmark data.
"""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parents[1]
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

import pandas as pd
import streamlit as st

from dashboard_ui import apply_styles, page_header, section_header, render_dataset_banner
from customerinsight.data_source import (
    load_builtin_dataset,
    get_dataset_metadata,
    dataset_quality_summary,
)


def main():
    apply_styles()
    page_header(
        "Workspace / Data Overview",
        "Data Workspace",
        "Explore the built‑in Online Retail transaction dataset – no uploads required.",
        purpose="Provide immediate access to a realistic retail transaction set for analytics.",
        benefit="All downstream pages (RFM, revenue, AI assistant) operate on this single source.",
        technical="Loads the built‑in Parquet cache, computes basic quality metrics, and displays a preview.",
    )

    render_dataset_banner()
    meta = get_dataset_metadata()
    dataset_name = meta.get("display_name", "Online Retail (Benchmark)")
    st.subheader(f"Dataset: {dataset_name}")

    # Load data (cached)
    df = load_builtin_dataset()

    # Quality summary
    summary = dataset_quality_summary(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Transactions", f"{summary['total_rows']:,}")
    col2.metric("Unique customers", f"{summary['unique_customers']:,}")
    col3.metric("Missing Customer IDs", f"{summary['missing_customer_id']}")
    col4.metric("Duplicate rows", f"{summary['duplicate_transactions']}")

    # Data preview
    with st.expander("📊 Preview first 10 rows", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)

    st.write("---")
    st.caption("All analytics pages now reference this dataset automatically.")


if __name__ == "__main__":
    main()
