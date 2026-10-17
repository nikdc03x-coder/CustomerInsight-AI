
"""Interactive explanations of customer purchasing behaviour."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from customerinsight.explanations import (
    assign_customer_clusters,
    describe_clusters,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data/processed/customer_rfm.csv"

METRICS = {
    "recency": {
        "label": "Days since last purchase",
        "description": "How long ago did customers last purchase?",
        "unit": "days",
        "better": "lower",
    },
    "frequency": {
        "label": "Purchase frequency",
        "description": "How many different purchase invoices do customers have?",
        "unit": "invoices",
        "better": "higher",
    },
    "monetary": {
        "label": "Positive spending",
        "description": "How much did customers spend on positive sales?",
        "unit": "£",
        "better": "higher",
    },
}


@st.cache_data
def load_customer_data():
    """Load RFM data and reproduce our baseline customer groups."""

    rfm = pd.read_csv(
        DATA_PATH,
        dtype={"customer_id": "string"},
    )

    customers = assign_customer_clusters(rfm, clusters=4)

    # Stable display names are based on cluster median spending.
    # This ordering is for presentation, not a model ranking.
    profiles = describe_clusters(customers)
    ordered = profiles.sort_values(
        ["median_monetary", "cluster"],
        ascending=[False, True],
    )

    group_names = {
        cluster_id: f"Group {chr(65 + position)}"
        for position, cluster_id in enumerate(ordered["cluster"])
    }

    customers["group"] = customers["cluster"].map(group_names)
    profiles["group"] = profiles["cluster"].map(group_names)

    return customers, profiles.sort_values("group")


def format_value(value, metric):
    """Show purchasing metrics in familiar, readable units."""

    if metric == "monetary":
        return f"£{value:,.2f}"

    if metric == "frequency":
        return f"{value:,.1f} invoices"

    return f"{value:,.1f} days"


def explain_chart(customers, metric, groups):
    """Create an explanation using statistics from the selected data."""

    selected = customers[customers["group"].isin(groups)]

    if selected.empty:
        return "No customer records match this selection."

    medians = selected.groupby("group")[metric].median()
    highest = medians.idxmax()
    lowest = medians.idxmin()

    name = METRICS[metric]["label"].lower()

    meaning = (
        f"This visualization compares {name} across "
        f"{len(medians)} selected customer groups."
    )

    finding = (
        f"{highest} has the highest median "
        f"({format_value(medians[highest], metric)}), "
        f"while {lowest} has the lowest "
        f"({format_value(medians[lowest], metric)})."
    )

    if metric == "recency":
        meaning += (
            " A smaller number means customers "
            "purchased more recently."
        )

    return meaning, finding


def show_explanation(customers, metric, groups, chart_type):
    """Explain the chart without making unsupported claims."""

    result = explain_chart(customers, metric, groups)

    if isinstance(result, str):
        st.info(result)
        return

    meaning, finding = result

    st.markdown("#### Understand this visualization")

    with st.container(border=True):
        st.markdown("**What does this chart show?**")
        st.write(meaning)

        st.markdown("**What did we discover?**")
        st.write(finding)

        st.markdown("**Why did we use this chart?**")

        reasons = {
            "Bar chart": "To compare typical values between groups.",
            "Box plot": "To examine variation and unusually high or low values.",
            "Violin plot": "To explore how values are distributed within groups.",
            "Scatter plot": "To investigate relationships between purchasing features.",
            "Heatmap": "To compare several group characteristics at once.",
        }

        st.write(reasons[chart_type])

        st.markdown("**How was this calculated?**")
        st.write(
            "We grouped customers by their model-assigned segment "
            "and calculated the median of their original RFM values. "
            "The visualization uses historical transaction data."
        )

        st.markdown("**What does this not tell us?**")
        st.caption(
            "These are descriptive patterns, not predictions or "
            "evidence of customer motivations. Group differences "
            "do not establish causal relationships."
        )


def show_chart(customers, profiles, metric, chart_type):
    """Display the selected Plotly visualization."""

    label = METRICS[metric]["label"]
    median_column = f"median_{metric}"

    if chart_type == "Bar chart":
        fig = px.bar(
            profiles,
            x="group",
            y=median_column,
            color="group",
            text_auto=".2f",
            title=f"Typical {label.lower()} by customer group",
            labels={
                "group": "Customer group",
                median_column: label,
            },
        )

    elif chart_type == "Box plot":
        fig = px.box(
            customers,
            x="group",
            y=metric,
            color="group",
            points="outliers",
            title=f"How much does {label.lower()} vary?",
        )

    elif chart_type == "Violin plot":
        fig = px.violin(
            customers,
            x="group",
            y=metric,
            color="group",
            box=True,
            points=False,
            title=f"Distribution of {label.lower()}",
        )

    elif chart_type == "Scatter plot":
        y_metric = "monetary" if metric != "monetary" else "frequency"

        fig = px.scatter(
            customers,
            x=metric,
            y=y_metric,
            color="group",
            hover_data=["recency", "frequency", "monetary"],
            opacity=0.55,
            title="How are customer purchasing features related?",
            labels={
                metric: label,
                y_metric: METRICS[y_metric]["label"],
            },
        )

    else:
        # Ratios are displayed relative to the selected population.
        medians = (
            customers.groupby("group")[
                ["recency", "frequency", "monetary"]
            ]
            .median()
        )

        baseline = customers[
            ["recency", "frequency", "monetary"]
        ].median().replace(0, float("nan"))

        relative = medians.div(baseline)

        fig = px.imshow(
            relative,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            color_continuous_midpoint=1,
            title="How does each group compare with selected customers?",
            labels={
                "x": "Purchasing feature",
                "y": "Customer group",
                "color": "Relative median",
            },
        )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=65, b=30),
    )

    st.plotly_chart(fig, width="stretch")


def compare_groups(customers, first, second):
    """Create an understandable side-by-side group comparison."""

    columns = ["recency", "frequency", "monetary"]

    medians = customers.groupby("group")[columns].median()

    first_values = medians.loc[first]
    second_values = medians.loc[second]

    rows = []

    for metric in columns:
        rows.append({
            "Behaviour": METRICS[metric]["label"],
            first: format_value(first_values[metric], metric),
            second: format_value(second_values[metric], metric),
        })

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        width="stretch",
    )

    st.markdown("#### What makes these groups different?")

    for metric in columns:
        left = first_values[metric]
        right = second_values[metric]

        if left == right:
            st.write(
                f"**{METRICS[metric]['label']}:** "
                "Both groups have the same median."
            )
            continue

        higher = first if left > right else second

        if metric == "recency":
            lower = second if higher == first else first
            st.write(
                f"**Recency:** {lower} purchased more recently "
                "based on the group's median."
            )
        else:
            st.write(
                f"**{METRICS[metric]['label']}:** "
                f"{higher} has the higher median."
            )


def main():
    st.set_page_config(
        page_title="CustomerInsight AI | Behaviour Explorer",
        page_icon="📊",
        layout="wide",
    )

    st.title("CustomerInsight AI")
    st.subheader("Understand Your Customer Groups")

    st.write(
        "Explore how customers differ using purchasing history. "
        "Choose what to investigate, compare groups and read "
        "the explanation behind every visualization."
    )

    if not DATA_PATH.exists():
        st.error(
            "Customer RFM dataset not found. "
            "Run the Phase 03 feature engineering pipeline first."
        )
        st.stop()

    customers, profiles = load_customer_data()

    groups = profiles["group"].tolist()

    col1, col2, col3 = st.columns(3)

    col1.metric("Customers analysed", f"{len(customers):,}")
    col2.metric("Discovered groups", len(groups))
    col3.metric("Research features", 3)

    st.divider()

    st.header("Explore customer behaviour")

    left, right = st.columns(2)

    with left:
        metric = st.selectbox(
            "What would you like to investigate?",
            options=list(METRICS),
            format_func=lambda key: METRICS[key]["description"],
        )

    with right:
        chart_type = st.selectbox(
            "How would you like to visualize it?",
            [
                "Bar chart",
                "Box plot",
                "Violin plot",
                "Scatter plot",
                "Heatmap",
            ],
        )

    selected_groups = st.multiselect(
        "Choose customer groups",
        groups,
        default=groups,
    )

    if not selected_groups:
        st.info("Select at least one customer group.")
        st.stop()

    filtered = customers[
        customers["group"].isin(selected_groups)
    ]

    filtered_profiles = profiles[
        profiles["group"].isin(selected_groups)
    ]

    show_chart(
        filtered,
        filtered_profiles,
        metric,
        chart_type,
    )

    show_explanation(
        filtered,
        metric,
        selected_groups,
        chart_type,
    )

    st.divider()
    st.header("Compare customer groups")

    first_col, second_col = st.columns(2)

    with first_col:
        first = st.selectbox("First group", groups, index=0)

    with second_col:
        second = st.selectbox(
            "Second group",
            groups,
            index=min(1, len(groups) - 1),
        )

    if first == second:
        st.info("Choose two different groups to compare.")
    else:
        compare_groups(customers, first, second)

    with st.expander("Explore the underlying statistics"):
        st.dataframe(
            profiles,
            hide_index=True,
            width="stretch",
        )

        st.caption(
            "Group names are presentation labels ordered by median "
            "positive spending. They are not permanent customer "
            "categories or verified business classifications."
        )


if __name__ == "__main__":
    main()
