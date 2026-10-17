"""Shared presentation for the research dashboard. No data or model operations."""

from html import escape
from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
PALETTE = ["#147D72", "#5779B3", "#A581BD", "#CF9950", "#8195A5"]

DESTINATIONS = [
    {
        "key": "customers", "path": "customer_insights.py",
        "title": "Customer behaviour", "icon": ":material/groups:",
        "category": "Understand your customers",
        "description": "See how customer groups differ in recency, purchase frequency and spending.",
        "benefit": "Turn group statistics into clear purchasing patterns you can explain.",
        "action": "Explore customer groups",
    },
    {
        "key": "rfm", "path": "pages/rfm_intelligence.py",
        "title": "Purchasing patterns", "icon": ":material/monitoring:",
        "category": "Understand your customers",
        "description": "Explore when customers last purchased, how often they buy and what they spend.",
        "benefit": "Understand the RFM measures behind every customer group.",
        "action": "Explore purchasing patterns",
    },
    {
        "key": "retail", "path": "pages/retail_data_explorer.py",
        "title": "Retail data", "icon": ":material/table_view:",
        "category": "Understand your customers",
        "description": "Inspect the original transactions, data quality, monthly activity and countries.",
        "benefit": "Spot gaps in the source data before interpreting customer patterns.",
        "action": "Inspect retail data",
    },
    {
        "key": "comparison", "path": "pages/research_findings.py",
        "title": "Comparison & stability", "icon": ":material/compare_arrows:",
        "category": "Examine the research",
        "description": "Compare clustering methods and see how consistently customers stay grouped.",
        "benefit": "Judge separation and stability together instead of relying on one score.",
        "action": "Compare the methods",
    },
    {
        "key": "validation", "path": "pages/model_validation_studio.py",
        "title": "Model validation", "icon": ":material/tune:",
        "category": "Examine the research",
        "description": "Explore how the number of groups and data transformations change the results.",
        "benefit": "Understand why the highest-scoring model needs a closer look.",
        "action": "Review model choices",
    },
    {
        "key": "quality", "path": "pages/research_health.py",
        "title": "Research quality", "icon": ":material/fact_check:",
        "category": "Examine the research",
        "description": "Check that research files exist, agree with each other and support the findings.",
        "benefit": "Trace a result to its evidence and see what still needs verification.",
        "action": "Check the evidence",
    },
]


def colors():
    """Inherit native theme colours so client-side theme changes work instantly."""
    return {
        "surface": "rgba(128,148,164,.045)", "text": "currentColor",
        "muted": "color-mix(in srgb, currentColor 80%, transparent)",
        "line": "rgba(128,148,164,.24)", "accent": "currentColor",
        "soft": "rgba(20,125,114,.14)",
    }


def apply_styles():
    """Style native widgets without replacing their accessibility or behaviour."""
    c = colors()
    st.markdown(
        f"""<style>
        .stApp {{ --ci-text:{c['text']}; --ci-muted:{c['muted']};
            --ci-surface:{c['surface']}; --ci-line:{c['line']};
            --ci-accent:{c['accent']}; --ci-soft:{c['soft']};
            }}
        .stMainBlockContainer {{ max-width:1360px; padding:4.5rem 3rem 4rem; }}
        .stApp, .stApp p, .stApp label, .stApp button {{
            font-family:Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
        .stApp h1 {{ font-size:2.45rem; font-weight:720; letter-spacing:-.055em;
            line-height:1.15; padding-bottom:.6rem; color:var(--ci-text); }}
        .stApp h2 {{ font-size:1.45rem; font-weight:650; letter-spacing:-.035em;
            color:var(--ci-text); padding-top:.6rem; }}
        .stApp h3 {{ font-size:1.12rem; font-weight:650; letter-spacing:-.02em;
            color:var(--ci-text); }}
        .stApp p {{ line-height:1.65; }}
        [data-testid="stCaptionContainer"] {{ color:var(--ci-muted); }}
        [data-testid="stSidebar"] {{ border-right:1px solid var(--ci-line); }}
        [data-testid="stSidebarNav"] {{ padding-top:.5rem; }}
        [data-testid="stSidebarNav"] a {{ border-radius:8px; margin:3px 0;
            min-height:40px; color:var(--ci-muted); }}
        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background:var(--ci-soft); color:var(--ci-accent); font-weight:650; }}
        [data-testid="stSidebarNav"] a:hover {{ background:var(--ci-soft); }}
        [data-testid="stMetric"] {{ background:var(--ci-surface);
            border:1px solid var(--ci-line); border-radius:12px;
            padding:1.2rem 1.25rem; min-height:118px; }}
        [data-testid="stMetricLabel"] {{ color:var(--ci-muted); font-size:.8rem; }}
        [data-testid="stMetricValue"] {{ color:var(--ci-text);
            font-variant-numeric:tabular-nums; font-size:1.9rem; font-weight:650;
            letter-spacing:-.045em; }}
        [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stVerticalBlock"][style*="border"] {{
            background:var(--ci-surface); border-color:var(--ci-line)!important;
            border-radius:12px!important; }}
        [class*="st-key-ci-card-"] {{ padding:1.25rem!important;
            background:var(--ci-surface); min-height:280px; gap:.65rem;
            transition:border-color .15s ease, box-shadow .15s ease; }}
        [class*="st-key-ci-card-"] > :last-child {{ margin-top:auto; }}
        [class*="st-key-ci-card-"]:hover {{ border-color:var(--ci-accent)!important;
            box-shadow:0 5px 18px #102B4210; }}
        [class*="st-key-ci-card-"] [data-testid="stPageLink"] {{
            border-top:1px solid var(--ci-line); padding-top:.65rem; margin-top:.25rem; }}
        [class*="st-key-ci-card-"] [data-testid="stPageLink"] a {{
            color:var(--ci-accent); font-weight:600; }}
        [data-testid="stPlotlyChart"] {{ background:var(--ci-surface);
            border:1px solid var(--ci-line); border-radius:12px; overflow:hidden; }}
        [data-testid="stTabs"] [role="tablist"] {{
            gap:1.3rem; border-bottom:1px solid var(--ci-line); padding-bottom:.15rem; }}
        [data-testid="stTabs"] [role="tab"] {{ padding:.7rem .1rem;
            font-size:.88rem; color:var(--ci-muted); }}
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
            color:inherit; font-weight:650; }}
        [data-testid="stTab"] .react-aria-SelectionIndicator {{
            background:#147D72!important; border-color:#147D72!important; }}
        [data-baseweb="tab-highlight"] {{ background:var(--ci-accent); }}
        [data-testid="stExpander"] {{ background:var(--ci-surface);
            border-radius:10px; }}
        [data-testid="stButton"] button, [data-testid="stDownloadButton"] button {{
            border-radius:8px; font-weight:550; }}
        .stApp a:focus-visible, .stApp button:focus-visible {{
            outline:3px solid var(--ci-accent)!important; outline-offset:3px; }}
        .ci-topline {{ display:flex; justify-content:space-between; align-items:center;
            gap:1rem; margin-bottom:.85rem; color:var(--ci-muted); }}
        .ci-eyebrow {{ font-size:.7rem; letter-spacing:.12em; text-transform:uppercase;
            font-weight:700; color:var(--ci-muted); }}
        .ci-badge {{ font-size:.72rem; padding:.3rem .65rem; border-radius:100px;
            background:var(--ci-soft); color:var(--ci-accent); white-space:nowrap; }}
        .ci-lead {{ max-width:800px; color:var(--ci-muted); font-size:1.03rem;
            line-height:1.7; margin:0 0 1rem; }}
        .ci-card-number {{ display:inline-flex; padding:.3rem .6rem;
            align-items:center; justify-content:center; background:var(--ci-soft);
            color:var(--ci-accent); border-radius:6px; font-size:.65rem;
            letter-spacing:.07em; font-weight:700; margin-bottom:.2rem; }}
        .ci-section-copy {{ color:var(--ci-muted); margin-top:-.2rem; margin-bottom:.8rem;
            font-size:.9rem; }}
        .insight-lead {{ font-size:1rem; line-height:1.75; }}
        hr {{ border-color:var(--ci-line)!important; margin:1.5rem 0!important; }}
        @media(max-width:800px) {{ .stMainBlockContainer {{ padding:4.5rem 1.1rem 3rem; }}
            .stApp h1 {{ font-size:1.95rem; }} .ci-topline {{ align-items:flex-start; }}
            [class*="st-key-ci-card-"] {{ min-height:0; }}
            [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] [data-testid="stMetric"]) {{
                display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.75rem; }}
            [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] [data-testid="stMetric"]) > [data-testid="stColumn"] {{
                width:100%; min-width:0; }}
            [data-testid="stMetric"] {{ min-height:104px; padding:1rem; }}
            [data-testid="stMetricValue"] {{ font-size:1.6rem; }} }}
        @media(prefers-reduced-motion:reduce) {{ [class*="st-key-ci-card-"] {{ transition:none; }} }}
        </style>""",
        unsafe_allow_html=True,
    )


def brand():
    """Use Streamlit's native logo slot so navigation remains keyboard accessible."""
    icon = '<rect x="0" y="3" width="34" height="34" rx="9" fill="#147D72"/><path d="M9 26V20M17 26V14M25 26V10" stroke="white" stroke-width="3" stroke-linecap="round"/>'
    st.logo(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="230" height="40" viewBox="0 0 230 40"><rect width="230" height="40" rx="9" fill="#147D72"/>{icon}<text x="44" y="27" fill="white" font-family="Segoe UI,Arial,sans-serif" font-size="19" font-weight="650">CustomerInsight</text></svg>',
        icon_image=f'<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40">{icon}</svg>',
        size="large",
    )


def page_header(section, title, description, *, purpose, benefit, technical, home=False):
    """A consistent title and optional plain-language guide for each workspace."""
    apply_styles()
    if not home and st.session_state.get("_ci_navigation_ready", False):
        st.page_link(str(APP_DIR / "pages/research_overview.py"), label="Dashboard", icon=":material/arrow_back:")
    st.markdown(
        f'<div class="ci-topline"><span class="ci-eyebrow">{escape(section)}</span>'
        '<span class="ci-badge">Historical retail data</span></div>',
        unsafe_allow_html=True,
    )
    st.title(title)
    st.markdown(f'<p class="ci-lead">{escape(description)}</p>', unsafe_allow_html=True)
    with st.expander("How this page helps", icon=":material/help_outline:"):
        left, right = st.columns(2)
        with left:
            st.markdown("**What you can do**")
            st.write(purpose)
        with right:
            st.markdown("**Why it is useful**")
            st.write(benefit)
        st.caption(technical)


def section_header(title, description):
    st.subheader(title)
    st.markdown(f'<p class="ci-section-copy">{escape(description)}</p>', unsafe_allow_html=True)


def workspace_cards():
    """Direct native links to every existing analytical workspace."""
    for category in ("Understand your customers", "Examine the research"):
        section_header(
            category,
            "Start with the data, then explore the people behind it."
            if category == "Understand your customers"
            else "Review the methods, model choices and evidence behind the findings.",
        )
        columns = st.columns(3, gap="medium")
        destinations = [item for item in DESTINATIONS if item["category"] == category]
        for column, destination in zip(columns, destinations):
            with column:
                with st.container(border=True, height="stretch", key=f"ci-card-{destination['key']}"):
                    label = {
                        "customers": "CUSTOMER GROUPS", "rfm": "RFM FEATURES",
                        "retail": "TRANSACTIONS", "comparison": "METHODS",
                        "validation": "MODEL SETTINGS", "quality": "EVIDENCE",
                    }[destination["key"]]
                    st.markdown(f'<span class="ci-card-number">{label}</span>', unsafe_allow_html=True)
                    st.subheader(destination["title"], anchor=False)
                    st.write(destination["description"])
                    st.caption(destination["benefit"])
                    if st.session_state.get("_ci_navigation_ready", False):
                        st.page_link(
                            str(APP_DIR / destination["path"]), label=destination["action"],
                            icon=destination["icon"], width="stretch",
                        )
        st.write("")


def show_chart(figure, **kwargs):
    """Apply presentation only; keep traces, values, scales and controls intact."""
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Segoe UI, Arial, sans-serif", "size": 12},
        colorway=PALETTE, title_font={"size": 15},
        legend={"font": {"size": 11}},
    )
    figure.update_xaxes(gridcolor="rgba(128,148,164,.2)", zerolinecolor="rgba(128,148,164,.2)")
    figure.update_yaxes(gridcolor="rgba(128,148,164,.2)", zerolinecolor="rgba(128,148,164,.2)")
    return st.plotly_chart(figure, **kwargs)
