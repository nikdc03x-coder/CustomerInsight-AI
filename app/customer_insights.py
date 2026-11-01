
"""Interactive customer behaviour dashboard for CustomerInsight AI."""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_ui import page_header, show_chart, render_dataset_banner, get_active_dataset_id

from customerinsight.explanations import assign_customer_clusters


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/processed/customer_rfm.csv"

FEATURES = {
    "recency": {
        "name": "Purchase recency",
        "short": "Recency",
        "unit": "days",
        "question": "How recently did customers purchase?",
        "help": "Days since the last recorded purchase. Lower means more recent.",
    },
    "frequency": {
        "name": "Purchase frequency",
        "short": "Frequency",
        "unit": "invoices",
        "question": "How often do customers purchase?",
        "help": "Number of distinct positive-sale invoices per customer.",
    },
    "monetary": {
        "name": "Positive spending",
        "short": "Spending",
        "unit": "GBP",
        "question": "How much do customers spend?",
        "help": "Total gross positive purchases in pounds, before refund reconciliation.",
    },
}

CHART_TYPES = [
    "Bar chart",
    "Line plot",
    "Area chart",
    "Grouped comparison",
    "Box plot",
    "Violin plot",
    "Histogram",
    "Scatter plot",
    "Heatmap",
]

COLORS = {
    "Group A": "#0D9488",
    "Group B": "#4676D7",
    "Group C": "#9770D2",
    "Group D": "#E0A04B",
}


@st.cache_data(show_spinner="Analysing customer behaviour...")
def load_data(active_id: str = "online_retail"):
    """Load the saved RFM dataset or compute dynamically for active dataset."""
    if active_id == "online_retail":
        if not DATA_PATH.is_file():
            raise FileNotFoundError(
                "The customer RFM dataset is missing. "
                "Run the Phase 03 feature engineering pipeline."
            )
        rfm = pd.read_csv(
            DATA_PATH,
            dtype={"customer_id": "string"},
        )
        customers = assign_customer_clusters(rfm, clusters=4)
    else:
        from customerinsight.datasets import load_dataset_transactions
        from customerinsight.analytics import calculate_rfm, segment_customers
        df_trans = load_dataset_transactions(active_id)
        rfm = calculate_rfm(df_trans)
        customers = segment_customers(rfm, method="kmeans", n_clusters=4)

    # Sort by spending only to assign readable display letters.
    ordering = (
        customers.groupby("cluster")["monetary"]
        .median()
        .sort_values(ascending=False)
    )

    names = {
        cluster: f"Group {chr(65 + position)}"
        for position, cluster in enumerate(ordering.index)
    }

    customers["group"] = customers["cluster"].map(names)

    return customers


def money(value):
    return f"£{value:,.2f}"


def number(value, metric):
    """Display each feature with an understandable unit."""

    if metric == "monetary":
        return money(value)

    if metric == "recency":
        return f"{value:,.1f} days"

    return f"{value:,.1f} invoices"


def group_profile(customers):
    """Calculate the typical purchasing habits in every selected group."""

    return (
        customers.groupby("group", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            recency=("recency", "median"),
            frequency=("frequency", "median"),
            monetary=("monetary", "median"),
        )
        .sort_values("group")
    )


def describe_group(row, overall):
    """Describe observed purchasing patterns without guessing motivations."""

    findings = []

    for feature in FEATURES:
        baseline = overall[feature]

        if baseline <= 0:
            continue

        ratio = row[feature] / baseline

        if feature == "recency":
            if ratio <= 0.8:
                findings.append("more recent purchases")
            elif ratio >= 1.2:
                findings.append("less recent purchases")
        elif ratio >= 1.2:
            findings.append(
                f"higher {FEATURES[feature]['short'].lower()}"
            )
        elif ratio <= 0.8:
            findings.append(
                f"lower {FEATURES[feature]['short'].lower()}"
            )

    if not findings:
        return "Purchasing habits close to the overall median."

    return "Compared with the full customer population: " + ", ".join(
        findings
    ) + "."


def build_figure(customers, metric, chart_type):
    """Generate a chart using real data and the user's current selection."""

    profile = group_profile(customers)
    name = FEATURES[metric]["name"]
    groups = sorted(customers["group"].unique())
    palette = {group: COLORS.get(group, "#64748B") for group in groups}

    if chart_type == "Bar chart":
        fig = px.bar(
            profile,
            x="group",
            y=metric,
            color="group",
            color_discrete_map=palette,
            text_auto=".2f",
            title=f"Typical {name.lower()} by group",
        )

    elif chart_type == "Line plot":
        # Group letters are categories, not chronological observations.
        fig = px.line(
            profile,
            x="group",
            y=metric,
            markers=True,
            title=f"Compare {name.lower()} across groups",
            category_orders={"group": groups},
        )
        fig.update_traces(
            line=dict(color="#0D9488", width=3),
            marker=dict(size=11),
        )

    elif chart_type == "Area chart":
        fig = px.area(
            profile,
            x="group",
            y=metric,
            markers=True,
            title=f"Connected view of typical {name.lower()}",
            category_orders={"group": groups},
        )

    elif chart_type == "Grouped comparison":
        # Compare each group's median with the full population median.
        baseline = st.session_state["population_medians"][metric]

        comparison = profile[["group", metric]].copy()
        comparison["Population median"] = baseline

        comparison = comparison.melt(
            id_vars="group",
            value_vars=[metric, "Population median"],
            var_name="Measure",
            value_name="Value",
        )
        comparison["Measure"] = comparison["Measure"].replace(
            {metric: "Group median"}
        )

        fig = px.bar(
            comparison,
            x="group",
            y="Value",
            color="Measure",
            barmode="group",
            title="Group median versus overall customer median",
        )

    elif chart_type == "Box plot":
        fig = px.box(
            customers,
            x="group",
            y=metric,
            color="group",
            color_discrete_map=palette,
            points="outliers",
            title=f"How much does {name.lower()} vary?",
        )

    elif chart_type == "Violin plot":
        fig = px.violin(
            customers,
            x="group",
            y=metric,
            color="group",
            color_discrete_map=palette,
            box=True,
            points=False,
            title=f"Distribution of {name.lower()}",
        )

    elif chart_type == "Histogram":
        fig = px.histogram(
            customers,
            x=metric,
            color="group",
            color_discrete_map=palette,
            nbins=45,
            barmode="overlay",
            opacity=0.65,
            title=f"How is {name.lower()} distributed?",
        )

    elif chart_type == "Scatter plot":
        second = (
            "monetary" if metric != "monetary" else "frequency"
        )

        fig = px.scatter(
            customers,
            x=metric,
            y=second,
            color="group",
            color_discrete_map=palette,
            opacity=0.55,
            hover_data=["recency", "frequency", "monetary"],
            title="Explore the relationship between purchasing features",
        )

        fig.update_yaxes(title=FEATURES[second]["name"])

    else:
        medians = profile.set_index("group")[
            ["recency", "frequency", "monetary"]
        ]

        baseline = pd.Series(
            st.session_state["population_medians"]
        ).replace(0, np.nan)

        relative = medians.div(baseline)

        fig = px.imshow(
            relative,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            color_continuous_midpoint=1,
            title="Group behaviour relative to all customers",
            labels={
                "x": "Behaviour feature",
                "y": "Customer group",
                "color": "Relative median",
            },
        )

    fig.update_layout(
        template="plotly_white",
        height=455,
        font=dict(size=13),
        title=dict(font=dict(size=19)),
        margin=dict(l=20, r=20, t=75, b=35),
        hovermode="closest",
        legend_title_text="Customer groups",
    )

    if chart_type not in ["Scatter plot", "Heatmap", "Histogram"]:
        fig.update_xaxes(title="Customer group")
        fig.update_yaxes(title=name)

    if chart_type == "Histogram":
        fig.update_yaxes(title="Number of customers")

    if chart_type not in ["Scatter plot", "Heatmap"]:
        fig.update_layout(
            xaxis=dict(categoryorder="array", categoryarray=groups)
            if chart_type != "Histogram"
            else {},
        )

    return fig


def explanation_text(customers, metric, chart_type):
    """Generate a specific, verifiable observation from selected records."""

    profile = group_profile(customers)

    highest = profile.loc[profile[metric].idxmax()]
    lowest = profile.loc[profile[metric].idxmin()]

    if len(profile) == 1:
        finding = (
            f"{highest['group']} has a median of "
            f"{number(highest[metric], metric)}."
        )
    else:
        finding = (
            f"{highest['group']} has the highest median "
            f"({number(highest[metric], metric)}). "
            f"{lowest['group']} has the lowest "
            f"({number(lowest[metric], metric)})."
        )

    if metric == "recency":
        finding += (
            " Lower recency means a more recent recorded purchase."
        )

    chart_reasons = {
        "Bar chart":
            "Best for comparing typical values across different groups.",
        "Line plot":
            "Connects group medians to make differences easier to follow. "
            "The group order is categorical, not chronological.",
        "Area chart":
            "A connected, filled comparison of group medians. "
            "The filled area is not cumulative sales or a time trend.",
        "Grouped comparison":
            "Shows whether each group's median is above or below "
            "the full customer population's median.",
        "Box plot":
            "Reveals the middle value, variability and outliers "
            "within each customer group.",
        "Violin plot":
            "Shows how customer values are distributed within groups.",
        "Histogram":
            "Shows how many customers fall into different value ranges.",
        "Scatter plot":
            "Reveals how two purchasing features relate across customers.",
        "Heatmap":
            "Compares all three purchasing features relative to "
            "the full population at the same time.",
    }

    return finding, chart_reasons[chart_type]


def insight_panel(customers, metric, chart_type):
    """Explain what the visualization means in everyday language."""

    finding, reason = explanation_text(
        customers, metric, chart_type
    )

    st.markdown("### What can we learn from this chart?")

    with st.container(border=True):
        st.markdown("**01 · What are we looking at?**")
        st.write(
            FEATURES[metric]["help"]
            if chart_type != "Heatmap"
            else "A comparison of recency, frequency and spending "
                 "against the full customer population's medians."
        )

        st.markdown("**02 · What did the data reveal?**")
        st.markdown(
            f'<div class="insight-lead">{finding}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**03 · Why use this visualization?**")
        st.write(reason)

        st.markdown("**04 · Why is it useful?**")
        st.write(
            "It helps us understand how purchasing behaviour differs "
            "among model-discovered customer groups, and which patterns "
            "deserve further investigation."
        )

        with st.expander("Research method and limitations"):
            st.write(
                "The analysis uses historical RFM features. "
                "Group comparisons are based on median values, "
                "and cluster membership comes from K-Means."
            )
            st.write(
                "These results do not explain customer motivations, "
                "prove causation or predict future purchases. "
                "A group median does not describe every customer."
            )


def show_group_cards(customers):
    """Turn cluster statistics into short, readable customer stories."""

    profile = group_profile(customers)

    overall = st.session_state["population_medians"]

    st.subheader("Meet the customer groups")
    st.caption(
        "Labels A–D are display identifiers. "
        "Their descriptions are derived from actual purchasing features."
    )

    columns = st.columns(4)

    for position, row in profile.reset_index(drop=True).iterrows():
        with columns[position % 4]:
            with st.container(border=True):
                st.markdown(f"### {row['group']}")
                st.metric("Customers", f"{row['customers']:,.0f}")
                st.caption(describe_group(row, overall))

                st.write(
                    f"**Recency:** {number(row['recency'], 'recency')}"
                )
                st.write(
                    f"**Frequency:** {number(row['frequency'], 'frequency')}"
                )
                st.write(
                    f"**Spending:** {number(row['monetary'], 'monetary')}"
                )


def group_comparison(customers):
    """Compare the typical behaviour of two selected groups."""

    available = sorted(customers["group"].unique())

    if len(available) < 2:
        st.info("Select at least two groups to compare.")
        return

    left, right = st.columns(2)

    with left:
        first = st.selectbox(
            "First group",
            available,
            key="compare_first",
        )

    with right:
        second = st.selectbox(
            "Second group",
            available,
            index=1,
            key="compare_second",
        )

    if first == second:
        st.info("Select two different groups.")
        return

    profiles = group_profile(customers).set_index("group")

    rows = []

    for metric in FEATURES:
        first_value = profiles.loc[first, metric]
        second_value = profiles.loc[second, metric]

        rows.append({
            "Behaviour": FEATURES[metric]["name"],
            first: number(first_value, metric),
            second: number(second_value, metric),
        })

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        width="stretch",
    )

    with st.container(border=True):
        st.markdown("#### Key differences")

        for metric in FEATURES:
            a = profiles.loc[first, metric]
            b = profiles.loc[second, metric]

            if np.isclose(a, b):
                st.write(
                    f"**{FEATURES[metric]['short']}:** "
                    "The two medians are equal."
                )
                continue

            higher = first if a > b else second

            if metric == "recency":
                recent = second if higher == first else first
                st.write(
                    f"**Recency:** {recent} has more recent "
                    "purchases based on its median."
                )
            else:
                st.write(
                    f"**{FEATURES[metric]['short']}:** "
                    f"{higher} has the higher median."
                )


def main():
    page_header(
        "Customer insights / Customer groups", "Customer behaviour",
        "Compare customer groups and turn purchasing statistics into understandable patterns.",
        purpose="Filter customer groups, explore nine chart styles, read group profiles, compare two groups and export the selected records.",
        benefit="Understand how groups differ without having to interpret transformed model inputs or clustering code.",
        technical="Four K-Means clusters use RFM features. Group letters are display identifiers ordered by median spending; they are not rankings of loyalty or profitability.",
    )
    render_dataset_banner()

    active_id = get_active_dataset_id()
    try:
        customers = load_data(active_id)
    except (FileNotFoundError, ValueError, KeyError) as error:
        st.error(f"Unable to load customer analysis: {error}")
        st.stop()

    st.session_state["population_medians"] = (
        customers[["recency", "frequency", "monetary"]]
        .median()
        .to_dict()
    )

    all_groups = sorted(customers["group"].unique())

    # Keep global filters in the sidebar so the content stays uncluttered.
    with st.sidebar:
        st.subheader("Filter customer groups")

        chosen_groups = st.multiselect(
            "Customer groups",
            all_groups,
            default=all_groups,
        )

        st.caption(
            "Select the groups you want to explore. "
            "Group definitions are based on the complete RFM dataset."
        )

        st.divider()

        st.subheader("Research information")
        st.write("**Dataset:** UCI Online Retail")
        st.write("**Clustering:** K-Means (4 clusters)")
        st.write("**Features:** Recency, Frequency, Monetary")

    if not chosen_groups:
        st.warning("Select at least one customer group.")
        st.stop()

    selected = customers[
        customers["group"].isin(chosen_groups)
    ].copy()

    overview = st.columns(4)

    overview[0].metric(
        "Customers in view",
        f"{len(selected):,}",
    )
    overview[1].metric(
        "Selected groups",
        len(chosen_groups),
    )
    overview[2].metric(
        "Median purchase frequency",
        f"{selected['frequency'].median():.1f}",
    )
    overview[3].metric(
        "Median positive spending",
        money(selected["monetary"].median()),
    )

    st.caption(
        "Metrics reflect the current group selection. "
        "Spending is gross positive sales, not net revenue."
    )

    st.divider()

    explore_tab, groups_tab, comparison_tab, data_tab = st.tabs([
        "Behaviour Explorer",
        "Group Stories",
        "Compare Groups",
        "Explore Data",
    ])

    with explore_tab:
        st.subheader("Explore purchasing behaviour")
        st.caption(
            "Choose a research question and change the chart "
            "without changing the underlying customer records."
        )

        control_left, control_right = st.columns([1.4, 1])

        with control_left:
            metric = st.selectbox(
                "What would you like to understand?",
                list(FEATURES),
                format_func=lambda x: FEATURES[x]["question"],
            )

        with control_right:
            chart_type = st.selectbox(
                "Choose a visualization",
                CHART_TYPES,
            )

        figure = build_figure(selected, metric, chart_type)

        show_chart(
            figure,
            width="stretch",
            config={"displaylogo": False},
        )

        insight_panel(selected, metric, chart_type)

    with groups_tab:
        show_group_cards(selected)

        st.divider()

        st.subheader("Detailed behaviour statistics")
        st.dataframe(
            group_profile(selected),
            hide_index=True,
            width="stretch",
        )

    with comparison_tab:
        st.subheader("Compare two customer groups")
        st.caption(
            "See how purchasing habits differ using "
            "original, understandable feature values."
        )

        group_comparison(selected)

    with data_tab:
        st.subheader("Explore the underlying customer data")
        st.caption(
            "These are customer-level RFM observations, "
            "not individual product transactions."
        )

        columns = [
            "customer_id",
            "group",
            "recency",
            "frequency",
            "monetary",
        ]

        st.dataframe(
            selected[columns],
            hide_index=True,
            width="stretch",
        )

        st.download_button(
            "Download selected customer data",
            data=selected[columns].to_csv(index=False),
            file_name="customerinsight_selected_customers.csv",
            mime="text/csv",
        )

        with st.expander("How were these values calculated?"):
            st.write(
                "**Recency:** Days since a customer's last positive purchase."
            )
            st.write(
                "**Frequency:** Number of distinct positive-sale invoices."
            )
            st.write(
                "**Monetary:** Total gross positive purchase value in GBP."
            )
            st.write(
                "Cancellations and refunds are not fully reconciled "
                "in this baseline RFM representation."
            )


if __name__ == "__main__":
    main()
