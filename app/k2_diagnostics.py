
"""Investigate why the highest-scoring K=2 model needs careful evaluation."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Find the project root and saved experimental results.
ROOT = Path(__file__).resolve().parents[1]

DIAGNOSTICS = (
    ROOT / "results/experiments/k2_cluster_diagnostics.csv"
)

VALIDATION = (
    ROOT / "results/experiments/model_validation_results.csv"
)


@st.cache_data
def load_k2_diagnostics():
    """Load and validate the saved K=2 research evidence."""

    if not DIAGNOSTICS.is_file() or not VALIDATION.is_file():
        return None, None

    try:
        profiles = pd.read_csv(DIAGNOSTICS)
        validation = pd.read_csv(VALIDATION)

    except (OSError, ValueError, pd.errors.ParserError):
        return None, None

    # These columns are needed for the diagnostic dashboard.
    required_profiles = {
        "cluster",
        "customers",
        "median_recency",
        "median_frequency",
        "median_monetary",
        "customer_share_pct",
    }

    required_validation = {
        "preprocessing",
        "clusters",
        "silhouette",
        "ari_vs_baseline",
    }

    if (
        not required_profiles.issubset(profiles.columns)
        or not required_validation.issubset(validation.columns)
    ):
        return None, None

    if profiles.empty or validation.empty:
        return None, None

    # Convert numerical columns without modifying saved files.
    profile_numbers = [
        "cluster",
        "customers",
        "median_recency",
        "median_frequency",
        "median_monetary",
        "customer_share_pct",
    ]

    validation_numbers = [
        "clusters",
        "silhouette",
        "ari_vs_baseline",
    ]

    for column in profile_numbers:
        profiles[column] = pd.to_numeric(
            profiles[column],
            errors="coerce",
        )

    for column in validation_numbers:
        validation[column] = pd.to_numeric(
            validation[column],
            errors="coerce",
        )

    # Required profile measurements must contain valid values.
    if profiles[profile_numbers].isna().any().any():
        return None, None

    if not profiles[profile_numbers].apply(
        lambda col: col.map(lambda value: abs(value) != float("inf"))
    ).all().all():
        return None, None

    # A K=2 diagnostic must describe exactly two groups.
    if len(profiles) != 2:
        return None, None

    if profiles["cluster"].duplicated().any():
        return None, None

    # Each group must contain at least one customer.
    if (profiles["customers"] <= 0).any():
        return None, None

    if (profiles["customers"] % 1 != 0).any():
        return None, None

    # RFM measurements cannot be negative in this dataset.
    rfm_columns = [
        "median_recency",
        "median_frequency",
        "median_monetary",
    ]

    if (profiles[rfm_columns] < 0).any().any():
        return None, None

    # Validate the model configuration identifiers.
    if validation["clusters"].isna().any():
        return None, None

    # Recalculate population percentages from the customer counts.
    total_customers = profiles["customers"].sum()

    profiles["customer_share_pct"] = (
        profiles["customers"] / total_customers * 100
    )

    return profiles, validation


def show_k2_diagnostics(key_prefix="k2_diagnostics"):
    """Display the K=2 experiment and explain its limitations."""

    # Use a stable prefix so Streamlit remembers widget selections.
    # Give each instance a different prefix if rendering it twice.
    prefix = str(key_prefix)

    st.header("When a High Score Can Be Misleading")

    st.write(
        "This experiment investigates the highest-scoring "
        "two-cluster configuration and examines whether "
        "its customer groups are useful for our original "
        "segmentation objective."
    )

    # -----------------------------------------------------
    # Load the original research results.
    # -----------------------------------------------------

    profiles, validation = load_k2_diagnostics()

    if profiles is None or validation is None:
        st.warning(
            "K=2 research results are missing or invalid. "
            "Check the experiment CSV files and rerun "
            "scripts/investigate_cluster_balance.py if needed."
        )
        return

    # Select the exact configuration investigated in Phase 08.
    selected = validation.loc[
        (validation["preprocessing"] == "Standard scaling")
        & (validation["clusters"] == 2)
    ]

    if len(selected) != 1:
        st.warning(
            "Expected exactly one Standard scaling, K=2 "
            "validation result. Check for missing or duplicate rows."
        )
        return

    experiment = selected.iloc[0]

    if pd.isna(experiment["silhouette"]):
        st.warning(
            "The selected experiment has no valid silhouette score."
        )
        return

    silhouette = float(experiment["silhouette"])

    if not -1 <= silhouette <= 1:
        st.warning("The saved silhouette score is outside its valid range.")
        return

    # -----------------------------------------------------
    # Calculate dashboard statistics.
    # -----------------------------------------------------

    total_customers = int(profiles["customers"].sum())

    smallest_share = float(
        profiles["customer_share_pct"].min()
    )

    largest_share = float(
        profiles["customer_share_pct"].max()
    )

    smallest_group = profiles.loc[
        profiles["customers"].idxmin()
    ]

    smallest_count = int(smallest_group["customers"])

    # -----------------------------------------------------
    # Overview cards
    # -----------------------------------------------------

    st.subheader("Experiment overview")

    a, b, c, d = st.columns(4)

    a.metric(
        "Silhouette score",
        f"{silhouette:.4f}",
    )

    b.metric(
        "Customers analysed",
        f"{total_customers:,}",
    )

    c.metric(
        "Largest cluster",
        f"{largest_share:.2f}%",
    )

    d.metric(
        "Smallest cluster",
        f"{smallest_share:.2f}%",
    )

    st.caption(
        "All values are calculated from the saved research "
        "outputs, not hardcoded dashboard examples."
    )

    st.divider()

    # -----------------------------------------------------
    # Customer distribution
    # -----------------------------------------------------

    st.subheader("Customer distribution")

    st.write(
        "The first diagnostic is cluster size. "
        "A high silhouette score can occur even when "
        "most customers are assigned to one group."
    )

    chart = profiles.copy()

    chart["Group"] = (
        "Cluster " + chart["cluster"].astype(int).astype(str)
    )

    chart = chart.sort_values("cluster")

    fig = px.bar(
        chart,
        x="Group",
        y="customers",
        color="Group",
        text="customers",
        title="Number of customers in each cluster",
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="Number of customers",
        margin=dict(l=20, r=20, t=60, b=20),
    )

    fig.update_traces(
        textposition="outside",
        hovertemplate=(
            "%{x}<br>"
            "Customers: %{y:,}"
            "<extra></extra>"
        ),
    )

    # Unique and stable chart key.
    st.plotly_chart(
        fig,
        width="stretch",
        key=f"{prefix}_customer_distribution_chart",
    )

    # Show a proportional chart for easier comparison.
    st.markdown("#### Percentage of customers")

    share_chart = px.bar(
        chart,
        x="customer_share_pct",
        y="Group",
        orientation="h",
        color="Group",
        text="customer_share_pct",
        title="Customer population share (%)",
    )

    share_chart.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
    )

    share_chart.update_layout(
        showlegend=False,
        xaxis_title="Customer share (%)",
        yaxis_title="",
        xaxis_range=[0, 110],
        margin=dict(l=20, r=20, t=60, b=20),
    )

    st.plotly_chart(
        share_chart,
        width="stretch",
        key=f"{prefix}_customer_share_chart",
    )

    st.caption(
        "The percentage chart illustrates the imbalance "
        "in the two-cluster partition."
    )

    st.divider()

    # -----------------------------------------------------
    # Interactive RFM comparison
    # -----------------------------------------------------

    st.subheader("Compare purchasing behaviour")

    st.write(
        "Explore how the two groups differ in recency, "
        "purchase frequency and positive spending."
    )

    metrics = {
        "Recency (days)": "median_recency",
        "Purchase frequency (invoices)": "median_frequency",
        "Positive spending (£)": "median_monetary",
    }

    metric_name = st.selectbox(
        "Choose a behaviour measurement",
        options=list(metrics.keys()),
        key=f"{prefix}_metric_selector",
    )

    metric = metrics[metric_name]

    comparison = px.bar(
        chart,
        x="Group",
        y=metric,
        color="Group",
        text_auto=".2f",
        title=f"Median customer behaviour: {metric_name}",
    )

    comparison.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title=metric_name,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    comparison.update_traces(
        textposition="outside",
    )

    st.plotly_chart(
        comparison,
        width="stretch",
        key=f"{prefix}_rfm_comparison_chart",
    )

    st.info(
        "Lower recency means a more recent purchase. "
        "Higher frequency and spending indicate greater "
        "recorded purchasing activity during the dataset period."
    )

    st.divider()

    # -----------------------------------------------------
    # Detailed customer group statistics
    # -----------------------------------------------------

    st.subheader("Detailed cluster statistics")

    display_columns = [
        "Group",
        "customers",
        "customer_share_pct",
        "median_recency",
        "median_frequency",
        "median_monetary",
    ]

    st.dataframe(
        chart[display_columns],
        hide_index=True,
        width="stretch",
        column_config={
            "Group": "Customer group",
            "customers": st.column_config.NumberColumn(
                "Customers",
                format="%d",
            ),
            "customer_share_pct": st.column_config.NumberColumn(
                "Customer share (%)",
                format="%.2f",
            ),
            "median_recency": st.column_config.NumberColumn(
                "Median recency (days)",
                format="%.2f",
            ),
            "median_frequency": st.column_config.NumberColumn(
                "Median frequency",
                format="%.2f",
            ),
            "median_monetary": st.column_config.NumberColumn(
                "Median spending (£)",
                format="%.2f",
            ),
        },
    )

    st.divider()

    # -----------------------------------------------------
    # Scientific interpretation
    # -----------------------------------------------------

    st.subheader("Scientific interpretation")

    with st.container(border=True):

        st.markdown("#### What did we observe?")

        st.write(
            f"The smallest group contains {smallest_count:,} "
            f"customers ({smallest_share:.2f}% of the population). "
            f"The corresponding K=2 configuration achieved "
            f"a silhouette score of {silhouette:.4f}."
        )

        st.markdown("#### Why does this matter?")

        st.write(
            "The model separates a relatively small customer "
            "group from the broader population. This can produce "
            "strong internal cluster separation without providing "
            "much differentiation within the larger group."
        )

        st.markdown("#### Does this mean K=2 is incorrect?")

        st.write(
            "No. The result may be useful for identifying "
            "exceptional purchasing activity. However, it may "
            "be less informative for a research goal requiring "
            "several interpretable customer behaviour groups."
        )

        st.markdown("#### What does this teach us?")

        st.write(
            "Model selection should consider multiple factors: "
            "silhouette score, group size distribution, "
            "interpretability, stability and the intended "
            "research objective."
        )

    # -----------------------------------------------------
    # Research limitations
    # -----------------------------------------------------

    with st.expander("Methodological limitations"):
        st.write(
            "The silhouette score measures internal cluster "
            "separation. It does not establish customer loyalty, "
            "business profitability or predictive accuracy."
        )

        st.write(
            "Cluster imbalance alone does not prove that "
            "a clustering configuration is incorrect."
        )

        st.write(
            "The two-cluster results describe historical "
            "purchasing patterns. They do not validate "
            "future behaviour or causal explanations."
        )

    # -----------------------------------------------------
    # Download saved evidence
    # -----------------------------------------------------

    st.download_button(
        label="Download K=2 diagnostic results",
        data=DIAGNOSTICS.read_bytes(),
        file_name="k2_cluster_diagnostics.csv",
        mime="text/csv",
        key=f"{prefix}_download",
    )


# This file is imported by the existing Streamlit page.
# The page calls show_k2_diagnostics() where appropriate.
