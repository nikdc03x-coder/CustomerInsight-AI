
"""Explore the evidence behind our customer segmentation research."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_ui import page_header, show_chart


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results/experiments"

ALGORITHM_FILE = RESULTS / "clustering_baseline.csv"
STABILITY_FILE = RESULTS / "stability_summary.csv"
RUNS_FILE = RESULTS / "stability_runs.csv"


@st.cache_data
def load_results():
    """Read the actual experiment outputs, never placeholder results."""

    paths = [ALGORITHM_FILE, STABILITY_FILE, RUNS_FILE]
    missing = [path.name for path in paths if not path.exists()]

    if missing:
        raise FileNotFoundError(
            "Missing experiment files: " + ", ".join(missing)
        )

    algorithms = pd.read_csv(ALGORITHM_FILE)
    stability = pd.read_csv(STABILITY_FILE)
    runs = pd.read_csv(RUNS_FILE)

    return algorithms, stability, runs


def comparison_chart(data, chart_type, metric):
    """Compare our three clustering baselines."""

    labels = {
        "silhouette": "Silhouette score",
        "coverage": "Cluster coverage",
        "clusters": "Number of discovered clusters",
    }

    title = f"{labels[metric]} by clustering algorithm"

    if chart_type == "Bar":
        fig = px.bar(
            data,
            x="algorithm",
            y=metric,
            color="algorithm",
            text_auto=".3f",
            title=title,
        )

    elif chart_type == "Line":
        # The connected points are algorithms, not a time series.
        fig = px.line(
            data,
            x="algorithm",
            y=metric,
            markers=True,
            title=title,
        )
        fig.update_traces(
            line_width=3,
            marker_size=11,
        )

    else:
        fig = px.scatter(
            data,
            x="algorithm",
            y=metric,
            color="algorithm",
            size_max=18,
            title=title,
        )
        fig.update_traces(marker_size=15)

    fig.update_layout(
        height=420,
        hovermode="closest",
        showlegend=False,
        margin=dict(l=20, r=20, t=70, b=30),
    )

    fig.update_yaxes(title=labels[metric])
    fig.update_xaxes(title="Clustering algorithm")

    return fig


def show_algorithm_analysis(algorithms):
    """Present algorithm quality alongside accessible explanations."""

    st.subheader("Which clustering algorithm performed better?")

    st.write(
        "We evaluated three clustering approaches on the same "
        "customer RFM dataset using their initial configurations."
    )

    left, right = st.columns(2)

    with left:
        metric = st.selectbox(
            "Choose an evaluation measure",
            ["silhouette", "coverage", "clusters"],
            format_func=lambda x: {
                "silhouette": "Cluster separation",
                "coverage": "Customers assigned to clusters",
                "clusters": "Number of discovered groups",
            }[x],
        )

    with right:
        chart_type = st.segmented_control(
            "Visualization style",
            ["Bar", "Line", "Scatter"],
            default="Bar",
        )

    chart_type = chart_type or "Bar"

    fig = comparison_chart(algorithms, chart_type, metric)
    show_chart(fig, width="stretch")

    with st.container(border=True):
        st.markdown("#### What does this chart tell us?")

        if metric == "silhouette":
            valid = algorithms.dropna(subset=["silhouette"])
            best = valid.loc[valid["silhouette"].idxmax()]

            st.write(
                f"**{best['algorithm']}** achieved the highest "
                f"baseline silhouette score "
                f"({best['silhouette']:.4f})."
            )
            st.write(
                "Higher silhouette values generally indicate "
                "better-separated groups, but they do not prove "
                "that those groups are useful or stable."
            )

        elif metric == "coverage":
            lowest = algorithms.loc[algorithms["coverage"].idxmin()]

            st.write(
                f"{lowest['algorithm']} assigned "
                f"{lowest['coverage']:.2%} of customers to clusters."
            )
            st.write(
                "Coverage matters because an algorithm can produce "
                "well-separated groups while leaving some observations "
                "unassigned as noise."
            )

        else:
            st.write(
                "Different algorithms may identify different numbers "
                "of groups. More groups do not automatically mean "
                "a better model."
            )

        st.caption(
            "These are initial model settings, not a fully tuned "
            "comparison. DBSCAN's silhouette score excludes noise, "
            "so its coverage must also be considered."
        )

    with st.expander("Inspect the original experiment results"):
        st.dataframe(algorithms, hide_index=True)
        st.download_button(
            "Download clustering results",
            algorithms.to_csv(index=False),
            file_name="clustering_baseline.csv",
            mime="text/csv",
        )


def stability_chart(summary, runs, mode):
    """Visualize stability using the actual ARI experiment results."""

    if mode == "Average ARI":
        fig = px.bar(
            summary,
            x="experiment",
            y="mean",
            text_auto=".4f",
            title="Average clustering agreement",
        )
        fig.update_yaxes(
            title="Mean Adjusted Rand Index",
            range=[min(0, float(summary["min"].min())), 1.05],
        )

    elif mode == "Line":
        fig = px.line(
            runs,
            x="run",
            y="ari",
            color="experiment",
            markers=True,
            title="How does stability vary across repeated experiments?",
        )
        fig.update_yaxes(title="Adjusted Rand Index")

    elif mode == "Box plot":
        fig = px.box(
            runs,
            x="experiment",
            y="ari",
            color="experiment",
            points="all",
            title="Distribution of stability scores",
        )
        fig.update_yaxes(title="Adjusted Rand Index")

    else:
        fig = px.scatter(
            runs,
            x="run",
            y="ari",
            color="experiment",
            title="Individual clustering stability results",
        )
        fig.update_yaxes(title="Adjusted Rand Index")

    fig.update_layout(
        height=445,
        margin=dict(l=20, r=20, t=70, b=30),
        legend_title_text="Experiment",
    )

    return fig


def show_stability_analysis(summary, runs):
    """Explain whether customer assignments remain consistent."""

    st.subheader("How reliable are the discovered customer groups?")

    st.write(
        "We repeated K-Means under different random seeds, "
        "training subsets and feature noise to study how "
        "its customer assignments change."
    )

    mode = st.selectbox(
        "Explore stability results",
        ["Average ARI", "Line", "Box plot", "Scatter"],
    )

    fig = stability_chart(summary, runs, mode)
    show_chart(fig, width="stretch")

    most_stable = summary.loc[summary["mean"].idxmax()]
    least_stable = summary.loc[summary["mean"].idxmin()]

    with st.container(border=True):
        st.markdown("#### What did our experiments reveal?")

        st.write(
            f"**{most_stable['experiment']}** had the highest "
            f"average ARI ({most_stable['mean']:.4f})."
        )

        st.write(
            f"**{least_stable['experiment']}** had the lowest "
            f"average ARI ({least_stable['mean']:.4f})."
        )

        st.markdown("**How should we interpret ARI?**")
        st.write(
            "An ARI of 1 indicates perfect agreement between "
            "two cluster assignments. Values near zero suggest "
            "agreement around chance level."
        )

        if mode == "Line":
            st.info(
                "The horizontal axis represents experiment runs, "
                "not dates. The lines show how the results varied "
                "across repeated trials."
            )

        st.markdown("**What are the limitations?**")
        st.write(
            "The experiments compare assignments against a baseline "
            "K-Means model. High agreement does not mean the groups "
            "are objectively correct or explain customer motivations."
        )

    with st.expander("Explore experiment statistics"):
        st.dataframe(summary, hide_index=True)
        st.dataframe(runs, hide_index=True)

        st.download_button(
            "Download stability summary",
            summary.to_csv(index=False),
            file_name="stability_summary.csv",
            mime="text/csv",
        )


def main():
    page_header(
        "Research & evidence / Comparison", "Comparison & stability",
        "Compare the clustering methods, then see how consistently they group the same customers.",
        purpose="Compare separation and coverage across three algorithms, explore repeated stability runs and inspect the research method.",
        benefit="Understand the strengths and limits of each result before choosing a customer segmentation approach.",
        technical="Silhouette measures separation; coverage reports how many customers are assigned. Adjusted Rand Index (ARI) measures agreement with a reference partition, not accuracy against known customer labels.",
    )

    try:
        algorithms, stability, runs = load_results()
    except (FileNotFoundError, OSError, ValueError) as error:
        st.error(str(error))
        st.stop()

    a, b, c = st.columns(3)

    a.metric("Algorithms evaluated", len(algorithms))
    b.metric("Stability experiments", runs["experiment"].nunique())
    c.metric("Stability runs", len(runs))

    st.divider()

    algorithm_tab, stability_tab, methods_tab = st.tabs([
        "Algorithm Comparison",
        "Model Stability",
        "Research Method",
    ])

    with algorithm_tab:
        show_algorithm_analysis(algorithms)

    with stability_tab:
        show_stability_analysis(stability, runs)

    with methods_tab:
        st.subheader("How was this research performed?")

        st.markdown(
            """
            **Research dataset:** UCI Online Retail

            **Customer features:** Recency, Frequency and Monetary

            **Clustering algorithms:** K-Means,
            Agglomerative Clustering and DBSCAN

            **Clustering quality:** Silhouette score and coverage

            **Stability:** Adjusted Rand Index across
            repeated random-initialization, training-subset
            and feature-noise experiments

            **Important limitation:** These experiments
            use one historical retail dataset. Their findings
            should not be generalized to all customers or
            all retail businesses without further research.
            """
        )


if __name__ == "__main__":
    main()
