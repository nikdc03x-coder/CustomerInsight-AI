"""Navigation for the CustomerInsight AI research dashboard."""

from pathlib import Path

import streamlit as st

from dashboard_ui import DESTINATIONS, brand


APP_DIR = Path(__file__).resolve().parent


def main():
    """Keep every existing workspace one click from the dashboard or sidebar."""
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
        "Workspace": [st.Page(
            str(APP_DIR / "pages/research_overview.py"),
            title="Dashboard", icon=":material/space_dashboard:", default=True,
        )],
        "Customer insights": [page("retail"), page("rfm"), page("customers")],
        "Research & evidence": [page("comparison"), page("validation"), page("quality")],
    }, position="sidebar")
    st.session_state["_ci_navigation_ready"] = True
    selected.run()
    with st.sidebar:
        st.divider()
        st.caption("UCI ONLINE RETAIL")
        st.caption("Explore historical purchasing patterns. Group descriptions reflect recorded behaviour.")


if __name__ == "__main__":
    main()
