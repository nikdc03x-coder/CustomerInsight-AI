"""Shared presentation for the research dashboard. No data or model operations."""

from html import escape
from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
PALETTE = ["#147D72", "#5779B3", "#A581BD", "#CF9950", "#8195A5"]

DESTINATIONS = [
    {
        "key": "workspace", "path": "pages/data_workspace.py",
        "title": "Data workspace", "icon": ":material/dataset:",
        "category": "Workspace & Data",
        "description": "Upload CSV/Excel datasets, auto-detect schemas, audit quality, and manage active datasets.",
        "benefit": "Switch seamlessly between custom datasets or the built-in online retail dataset.",
        "action": "Manage datasets",
    },
    {
        "key": "customers", "path": "customer_insights.py",
        "title": "Customer behaviour", "icon": ":material/groups:",
        "category": "Understand your customers",
        "description": "See how customer groups differ in recency, purchase frequency and spending.",
        "benefit": "Turn group statistics into clear purchasing patterns you can explain.",
        "action": "Explore customer groups",
    },
    {
        "key": "revenue", "path": "pages/revenue_analytics.py",
        "title": "Revenue analytics", "icon": ":material/payments:",
        "category": "Understand your customers",
        "description": "Track total revenue, average order value, sales trends and geographic concentration.",
        "benefit": "Monitor top-line business metrics and high-value customer accounts.",
        "action": "Explore revenue",
    },
    {
        "key": "products", "path": "pages/product_intelligence.py",
        "title": "Product & basket intelligence", "icon": ":material/shopping_basket:",
        "category": "Understand your customers",
        "description": "Discover bestsellers, underperforming inventory, and market basket association rules.",
        "benefit": "Identify cross-sell bundles with support, confidence and lift metrics.",
        "action": "Explore products & baskets",
    },
    {
        "key": "predictive", "path": "pages/predictive_intelligence.py",
        "title": "Predictive CLV & churn", "icon": ":material/vital_signs:",
        "category": "Understand your customers",
        "description": "Estimate customer recurrence probability, churn risk classification, and projected 90-day spend.",
        "benefit": "Target high-value customers before they lapse.",
        "action": "Explore predictions",
    },
    {
        "key": "assistant", "path": "pages/ai_data_assistant.py",
        "title": "AI data assistant", "icon": ":material/smart_toy:",
        "category": "AI & Strategy",
        "description": "Ask natural language questions answered strictly by deterministic calculations on your dataset.",
        "benefit": "Get reliable data answers with zero hallucinated figures.",
        "action": "Ask assistant",
    },
    {
        "key": "insights", "path": "pages/business_insights_page.py",
        "title": "Business insights engine", "icon": ":material/lightbulb:",
        "category": "AI & Strategy",
        "description": "Automated executive-ready findings across revenue concentration, churn risk, and cross-sell.",
        "benefit": "Turn raw patterns into prioritized, evidence-backed actions.",
        "action": "View insights",
    },
    {
        "key": "reports", "path": "pages/reports_exports.py",
        "title": "Reports & exports", "icon": ":material/summarize:",
        "category": "AI & Strategy",
        "description": "Generate an executive markdown brief and export customer segment CSV lists.",
        "benefit": "Share verified findings with stakeholders and sync with CRM tools.",
        "action": "Generate reports",
    },
    {
        "key": "rfm", "path": "pages/rfm_intelligence.py",
        "title": "Purchasing patterns", "icon": ":material/monitoring:",
        "category": "Examine the research",
        "description": "Explore when customers last purchased, how often they buy and what they spend.",
        "benefit": "Understand the RFM measures behind every customer group.",
        "action": "Explore purchasing patterns",
    },
    {
        "key": "retail", "path": "pages/retail_data_explorer.py",
        "title": "Retail data", "icon": ":material/table_view:",
        "category": "Examine the research",
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
    categories = [
        (
            "Customer Intelligence & Analytics",
            ["customers", "revenue", "products", "predictive"],
            "Explore customer groups, revenue momentum, product bestsellers and predictive CLV.",
        ),
        (
            "AI & Strategy",
            ["assistant", "insights", "reports"],
            "Query your data with grounded AI, review strategic insights and export briefs.",
        ),
        (
            "Examine the Research Lab",
            ["retail", "rfm", "comparison", "validation", "quality"],
            "Review benchmark experiments, clustering algorithms and model validation evidence.",
        ),
    ]
    by_key = {item["key"]: item for item in DESTINATIONS}
    for cat_title, keys, cat_desc in categories:
        section_header(cat_title, cat_desc)
        items = [by_key[k] for k in keys if k in by_key]
        for row_start in range(0, len(items), 3):
            row_items = items[row_start : row_start + 3]
            cols = st.columns(3, gap="medium")
            for col, destination in zip(cols, row_items):
                with col:
                    with st.container(border=True, height="stretch", key=f"ci-card-{destination['key']}"):
                        label = {
                            "workspace": "DATA WORKSPACE",
                            "customers": "CUSTOMER GROUPS", "rfm": "RFM FEATURES",
                            "retail": "TRANSACTIONS", "comparison": "METHODS",
                            "validation": "MODEL SETTINGS", "quality": "EVIDENCE",
                            "revenue": "REVENUE", "products": "PRODUCTS",
                            "predictive": "PREDICTIONS", "assistant": "AI ASSISTANT",
                            "insights": "BUSINESS INSIGHTS", "reports": "REPORTS",
                        }.get(destination["key"], "ANALYSIS")
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


def get_active_dataset_id() -> str:
    """Return the currently selected dataset id from session state."""
    return st.session_state.get("active_dataset_id", "online_retail")


def set_active_dataset_id(dataset_id: str):
    """Set the active dataset id in session state."""
    st.session_state["active_dataset_id"] = dataset_id


def get_active_dataset_metadata() -> dict:
    """Retrieve metadata for the currently active dataset."""
    from customerinsight.datasets import get_dataset_metadata
    active_id = get_active_dataset_id()
    meta = get_dataset_metadata(active_id)
    if meta is None and active_id != "online_retail":
        set_active_dataset_id("online_retail")
        meta = get_dataset_metadata("online_retail")
    return meta or {}


@st.cache_data(show_spinner=False)
def _cached_load_transactions(dataset_id: str):
    from customerinsight.datasets import load_dataset_transactions
    return load_dataset_transactions(dataset_id)


def load_active_transactions():
    """Load cleaned transactions for the currently active dataset."""
    active_id = get_active_dataset_id()
    try:
        return _cached_load_transactions(active_id)
    except Exception:
        set_active_dataset_id("online_retail")
        return _cached_load_transactions("online_retail")


def render_dataset_banner():
    """Render a clean information banner showing the active dataset and quick switch."""
    meta = get_active_dataset_metadata()
    if not meta:
        return

    name = meta.get("display_name", meta.get("dataset_id", "Dataset"))
    rows = meta.get("accepted_rows", 0)
    customers = meta.get("unique_customers", 0)
    currency = meta.get("currency", "GBP")
    is_builtin = meta.get("is_builtin", False)
    badge = "Benchmark Dataset" if is_builtin else "Custom Dataset"

    st.markdown(
        f"""<div style="display:flex; justify-content:space-between; align-items:center;
        background:var(--ci-surface); border:1px solid var(--ci-line); border-radius:10px;
        padding:.6rem 1rem; margin-bottom:1.25rem;">
            <div style="display:flex; align-items:center; gap:.75rem; flex-wrap:wrap;">
                <span style="font-weight:650; color:var(--ci-text);">📊 Active Dataset: {escape(name)}</span>
                <span class="ci-badge">{badge}</span>
                <span style="color:var(--ci-muted); font-size:.85rem;">• {rows:,} transactions</span>
                <span style="color:var(--ci-muted); font-size:.85rem;">• {customers:,} customers</span>
                <span style="color:var(--ci-muted); font-size:.85rem;">• Currency: {escape(currency)}</span>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

