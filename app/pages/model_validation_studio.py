
"""Interactive exploration of model validation experiments."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_ui import page_header, show_chart

from k2_diagnostics import show_k2_diagnostics


ROOT = Path(__file__).resolve().parents[2]
RESULTS_FILE = ROOT / "results/experiments/model_validation_results.csv"

METRICS = {
    "silhouette": {
        "label": "Silhouette score",
        "meaning": "Measures how separated the discovered groups are.",
        "interpretation": "Higher values generally indicate better separation.",
    },
    "ari_vs_baseline": {
        "label": "ARI vs baseline",
        "meaning": "Measures agreement with our original four-cluster solution.",
        "interpretation": "Higher agreement does not necessarily mean better clusters.",
    },
    "inertia": {
        "label": "K-Means inertia",
        "meaning": "Measures within-cluster squared distances.",
        "interpretation": (
            "Lower inertia means a smaller within-cluster sum of squares. "
            "Compare it only within the same preprocessing representation."
        ),
    },
}


@st.cache_data(show_spinner="Loading model validation results...")
def load_experiments():
    """Read existing experiments instead of rerunning K-Means."""

    data = pd.read_csv(RESULTS_FILE)

    required = {
        "preprocessing",
        "clusters",
        "silhouette",
        "ari_vs_baseline",
        "inertia",
    }

    if data.empty or not required.issubset(data.columns):
        raise ValueError("The validation results are incomplete.")

    if data[list(required - {"preprocessing"})].isna().any().any():
        raise ValueError("Validation results contain missing numbers.")

    return data.sort_values(["preprocessing", "clusters"])


def create_chart(data, metric, view):
    """Display the selected experiment with a suitable chart."""

    labels = {
        "clusters": "Number of clusters (K)",
        "preprocessing": "Preprocessing method",
        **{key: value["label"] for key, value in METRICS.items()},
    }

    if view == "Line":
        fig = px.line(
            data,
            x="clusters",
            y=metric,
            color="preprocessing",
            markers=True,
            labels=labels,
        )

    elif view == "Grouped bar":
        fig = px.bar(
            data,
            x="clusters",
            y=metric,
            color="preprocessing",
            barmode="group",
            labels=labels,
        )

    elif view == "Scatter":
        fig = px.scatter(
            data,
            x="clusters",
            y=metric,
            color="preprocessing",
            hover_data=["inertia", "silhouette", "ari_vs_baseline"],
            labels=labels,
        )
        fig.update_traces(marker=dict(size=12))

    else:
        matrix = data.pivot(
            index="preprocessing",
            columns="clusters",
            values=metric,
        )

        fig = px.imshow(
            matrix,
            text_auto=".3f",
            aspect="auto",
            color_continuous_scale="Blues",
            labels={
                "x": "Number of clusters (K)",
                "y": "Preprocessing method",
                "color": METRICS[metric]["label"],
            },
        )

    fig.update_layout(
        template="plotly_white",
        height=470,
        title=f"{METRICS[metric]['label']} across tested configurations",
        margin=dict(l=20, r=20, t=75, b=35),
        legend_title_text="Preprocessing",
    )

    if view != "Heatmap":
        fig.update_xaxes(dtick=1)

    return fig


def explain_experiment(data, metric, view):
    """Translate experiment results into understandable observations."""

    st.markdown("### Understand the findings")

    if metric == "silhouette":
        best = data.loc[data["silhouette"].idxmax()]

        finding = (
            f"The highest silhouette score among the displayed "
            f"configurations is **{best['silhouette']:.4f}**, "
            f"using **{best['preprocessing']}** "
            f"with **K = {int(best['clusters'])}**."
        )

    elif metric == "ari_vs_baseline":
        best = data.loc[data["ari_vs_baseline"].idxmax()]

        finding = (
            f"The configuration with the highest agreement "
            f"with the original baseline is "
            f"**{best['preprocessing']}**, "
            f"**K = {int(best['clusters'])}**, "
            f"with ARI **{best['ari_vs_baseline']:.4f}**."
        )

    else:
        finding = (
            "Inertia usually decreases as K increases. "
            "Inspect the changes within each preprocessing method "
            "rather than selecting the smallest value automatically."
        )

    with st.container(border=True):
        st.markdown("**01 · What does this chart measure?**")
        st.write(METRICS[metric]["meaning"])

        st.markdown("**02 · What did we discover?**")
        st.markdown(finding)

        st.markdown("**03 · Why is this useful?**")
        st.write(
            "It helps us investigate whether our conclusions "
            "depend heavily on the chosen cluster count or "
            "feature transformation."
        )

        st.markdown("**04 · How should we interpret this?**")
        st.write(METRICS[metric]["interpretation"])

        if view == "Line":
            st.caption(
                "These lines connect successive numerical K values. "
                "They represent a parameter sweep, not a time trend."
            )

        with st.expander("How was this experiment performed?"):
            st.write(
                "We evaluated K-Means using different cluster counts "
                "and preprocessing methods. Results are loaded from "
                "the saved Phase 08 experiments."
            )
            st.write(
                "The silhouette measure describes internal cluster "
                "structure. ARI describes similarity to the baseline. "
                "Neither proves business usefulness or causation."
            )
            st.write(
                "Different transformations create different distance "
                "scales, so inertia should not be compared directly "
                "between preprocessing methods."
            )


def compare_at_k(data):
    """Compare preprocessing methods for one chosen cluster count."""

    st.subheader("Compare preprocessing at the same K")

    available_k = sorted(data["clusters"].unique())

    chosen_k = st.select_slider(
        "Choose the number of clusters",
        options=available_k,
        value=4 if 4 in available_k else available_k[0],
    )

    selected = data[data["clusters"] == chosen_k]

    st.dataframe(
        selected[
            [
                "preprocessing",
                "silhouette",
                "ari_vs_baseline",
                "inertia",
            ]
        ],
        hide_index=True,
        width="stretch",
    )

    best = selected.loc[selected["silhouette"].idxmax()]

    st.info(
        f"For K = {chosen_k}, **{best['preprocessing']}** "
        f"achieved the highest tested silhouette "
        f"({best['silhouette']:.4f})."
    )

    st.caption(
        "This comparison concerns cluster separation, "
        "not overall business quality."
    )


def main():
    page_header(
        'Research & evidence / Model choices', 'Model validation',
        'Explore how different model settings change the customer groups, and why a high score needs context.',
        purpose='Compare preprocessing methods and group counts, examine the two-group result and download the saved experiments.',
        benefit='See whether an apparent improvement reflects useful differentiation or a small group of exceptional purchasers.',
        technical='K is the number of groups. Silhouette measures separation, ARI measures agreement with the baseline, and inertia measures within-group squared distances.',
    )

    if not RESULTS_FILE.is_file():
        st.warning(
            "Phase 08 results are not available. "
            "Run model_validation.ipynb first."
        )
        st.stop()

    try:
        results = load_experiments()
    except (OSError, ValueError) as error:
        st.error(f"Could not load validation results: {error}")
        st.stop()

    best = results.loc[results["silhouette"].idxmax()]

    metrics = st.columns(4)

    metrics[0].metric("Configurations tested", len(results))
    metrics[1].metric(
        "Cluster counts tested",
        results["clusters"].nunique(),
    )
    metrics[2].metric(
        "Preprocessing methods",
        results["preprocessing"].nunique(),
    )
    metrics[3].metric(
        "Highest silhouette",
        f"{best['silhouette']:.4f}",
    )

    st.caption(
        "These metrics summarize saved experiments, "
        "not live model retraining."
    )

    st.divider()


    explore_tab, comparison_tab, diagnostic_tab, evidence_tab = st.tabs([
        "Explore Configurations",
        "Compare Methods",
        "K=2 Investigation",
        "Research Evidence",
    ])


    with explore_tab:
        st.subheader("Investigate model sensitivity")

        left, right = st.columns(2)

        with left:
            metric = st.selectbox(
                "What would you like to measure?",
                list(METRICS),
                format_func=lambda item: METRICS[item]["label"],
            )

        with right:
            chart_type = st.selectbox(
                "Visualization style",
                ["Line", "Grouped bar", "Scatter", "Heatmap"],
            )

        methods = st.multiselect(
            "Select preprocessing methods",
            sorted(results["preprocessing"].unique()),
            default=sorted(results["preprocessing"].unique()),
        )

        filtered = results[
            results["preprocessing"].isin(methods)
        ]

        if filtered.empty:
            st.info("Select at least one preprocessing method.")
        else:
            figure = create_chart(filtered, metric, chart_type)

            show_chart(
                figure,
                width="stretch",
                config={"displaylogo": False},
            )

            explain_experiment(filtered, metric, chart_type)

    with comparison_tab:
        compare_at_k(results)

    with diagnostic_tab:
        show_k2_diagnostics()


    with evidence_tab:
        st.subheader("Explore the original experiment results")

        st.dataframe(
            results,
            hide_index=True,
            width="stretch",
        )

        st.download_button(
            "Download validation results",
            data=results.to_csv(index=False),
            file_name="model_validation_results.csv",
            mime="text/csv",
        )

        with st.expander("Research limitations", expanded=True):
            st.write(
                "These experiments use one historical retail dataset "
                "and a limited set of preprocessing choices."
            )
            st.write(
                "Silhouette scores describe separation, not the "
                "practical usefulness of a customer segment."
            )
            st.write(
                "Parameter sensitivity is not the same as "
                "independent model validation."
            )


if __name__ == "__main__":
    main()
