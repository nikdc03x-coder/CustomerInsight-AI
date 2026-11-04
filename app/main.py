"""Navigation for the CustomerInsight AI customer intelligence platform."""

from pathlib import Path

import streamlit as st

from dashboard_ui import (
    DESTINATIONS, brand, get_active_dataset_id,
    get_active_dataset_metadata, set_active_dataset_id,
)
from customerinsight.datasets import list_datasets


APP_DIR = Path(__file__).resolve().parent


def main():
    """Entry point for the Streamlit app with simple performance logging.

    The function measures the total time taken to initialise the UI and
    navigates to the selected page. The elapsed time is displayed in the
    sidebar as a caption, allowing us to see cold‑start vs. warm‑start
    timings directly in the running app.
    """
    import time
    _start = time.perf_counter()

    """Keep every analytical and research workspace accessible from the sidebar."""
    st.set_page_config(
        page_title="CustomerInsight AI", page_icon=":material/monitoring:",
        layout="wide", initial_sidebar_state="auto",
    )
    brand()
    by_key = {destination["key"]: destination for destination in DESTINATIONS}

    def page(key):
        destination = by_key[key]
        return st.Page(
            str(APP_DIR / destination["path"]),
            title=destination["title"], icon=destination["icon"],
        )

    selected = st.navigation({
        "Workspace": [
            st.Page(
                str(APP_DIR / "pages/research_overview.py"),
                title="Dashboard", icon=":material/space_dashboard:", default=True,
            ),
            page("workspace"),
        ],
        "Customer Intelligence": [
            page("customers"),
            page("revenue"),
            page("products"),
            page("predictive"),
        ],
        "AI & Strategy": [
            page("assistant"),
            page("insights"),
            page("reports"),
        ],
        "Research Lab": [
            page("retail"),
            page("rfm"),
            page("comparison"),
            page("validation"),
            page("quality"),
        ],
    }, position="sidebar")
    st.session_state["_ci_navigation_ready"] = True
    selected.run()
    # Log elapsed time for UI init
    _elapsed = time.perf_counter() - _start
    st.sidebar.caption(f"⚡️ Init time: {_elapsed:.2f}s")

    with st.sidebar:
        st.divider()
        st.caption("ACTIVE DATASET")
        datasets = list_datasets()
        ds_map = {d["dataset_id"]: d["display_name"] for d in datasets}
        current_id = get_active_dataset_id()
        if current_id not in ds_map and datasets:
            current_id = datasets[0]["dataset_id"]
            set_active_dataset_id(current_id)

        options = list(ds_map.keys())
        index = options.index(current_id) if current_id in options else 0
        chosen_id = st.selectbox(
            "Select Workspace Dataset",
            options=options,
            format_func=lambda k: ds_map.get(k, k),
            index=index,
            key="_sidebar_dataset_selector",
            label_visibility="collapsed",
        )
        if chosen_id != current_id:
            set_active_dataset_id(chosen_id)
            st.rerun()

        meta = get_active_dataset_metadata()
        if meta:
            st.caption(
                f"📊 {meta.get('accepted_rows', 0):,} records • "
                f"{meta.get('unique_customers', 0):,} customers • "
                f"{meta.get('currency', 'GBP')}"
            )
        st.divider()
        st.caption("CustomerInsight AI Platform v2.0")


if __name__ == "__main__":
    main()
