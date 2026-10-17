
"""Overview of the research evidence produced by CustomerInsight AI."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results/experiments"


def read_results(filename, required_columns):
    """Load saved experiments without substituting invented results."""

    path = RESULTS / filename

    if not path.is_file():
        return None

    data = pd.read_csv(path)

    if data.empty or not set(required_columns).issubset(data.columns):
        st.warning(f"{filename} is empty or has unexpected columns.")
        return None

    return data


def explain(title, finding, method, limitation):
    """Keep research explanations readable and consistent."""

    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.write(finding)

        with st.expander("How do we know?"):
            st.write(method)
            st.caption(limitation)


def main():
    st.title("CustomerInsight AI")
    st.caption("RESEARCH OVERVIEW / UNSUPERVISED LEARNING")

    st.write(
        "Explore the complete research journey: from identifying "
        "customer groups to evaluating their separation, stability "
        "and sensitivity to model settings."
    )

    clustering = read_results(
        "clustering_baseline.csv",
        ["algorithm", "clusters", "silhouette", "coverage"],
    )

    stability = read_results(
        "stability_summary.csv",
        ["experiment", "mean", "std", "min", "max"],
    )

    validation = read_results(
        "model_validation_results.csv",
        ["preprocessing", "clusters", "silhouette"],
    )

    profiles = read_results(
        "customer_cluster_profiles.csv",
        ["cluster", "customers", "median_recency",
         "median_frequency", "median_monetary"],
    )

    customer_path = ROOT / "data/processed/customer_rfm.csv"

    customer_count = None
    if customer_path.is_file():
        customer_count = len(pd.read_csv(
            customer_path,
            usecols=["customer_id"],
        ))

    cols = st.columns(4)

    cols[0].metric(
        "Customers analysed",
        f"{customer_count:,}" if customer_count is not None else "Pending",
    )

    cols[1].metric(
        "Algorithms compared",
        clustering["algorithm"].nunique()
        if clustering is not None else "Pending",
    )

    cols[2].metric(
        "Mean stability ARI",
        f"{stability['mean'].mean():.3f}"
        if stability is not None else "Pending",
        help="Unweighted average across the experiment types.",
    )

    cols[3].metric(
        "Validation configurations",
        len(validation) if validation is not None else "Pending",
    )

    st.divider()

    st.subheader("1. Which clustering algorithm performed best?")

    if clustering is not None:
        fig = px.bar(
            clustering,
            x="algorithm",
            y="silhouette",
            color="algorithm",
            text_auto=".3f",
            title="Baseline silhouette scores",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

        best = clustering.loc[clustering["silhouette"].idxmax()]

        explain(
            "What did we discover?",
            f"{best['algorithm']} had the highest silhouette "
            f"score ({best['silhouette']:.4f}) among the "
            "tested baseline configurations.",
            "Silhouette score measures how closely observations "
            "match their own cluster relative to other clusters.",
            "This does not prove the algorithm is universally "
            "best. DBSCAN's score also excludes noise observations.",
        )
    else:
        st.info("Baseline clustering results are not available.")

    st.divider()

    st.subheader("2. How stable are the customer groups?")

    if stability is not None:
        fig = px.bar(
            stability,
            x="experiment",
            y="mean",
            error_y="std",
            text_auto=".3f",
            title="Average ARI with standard-deviation bars",
        )
        fig.update_yaxes(
            title="Mean Adjusted Rand Index",
        )
        st.plotly_chart(fig, width="stretch")

        explain(
            "What did we discover?",
            "The bars show average agreement with the baseline "
            "for random initialization, training subsets "
            "and feature noise.",
            "Each experiment compares resulting customer "
            "assignments with a reference partition using ARI. "
            "Error bars represent standard deviations, "
            "not confidence intervals.",
            "High agreement is evidence of stability under "
            "the tested conditions, not proof of correctness.",
        )
    else:
        st.info("Stability experiment results are not available.")

    st.divider()

    st.subheader("3. Does changing K affect the results?")

    if validation is not None:
        fig = px.line(
            validation,
            x="clusters",
            y="silhouette",
            color="preprocessing",
            markers=True,
            title="Sensitivity to cluster count and preprocessing",
        )
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, width="stretch")

        explain(
            "What question does this answer?",
            "This experiment compares the separation of "
            "customer groups across cluster counts and "
            "feature preprocessing approaches.",
            "Each point represents an evaluated model "
            "configuration recorded in Phase 08.",
            "The best silhouette score is not necessarily "
            "the most useful segmentation for a retailer.",
        )
    else:
        st.info(
            "Model validation results are pending. "
            "Run the Phase 08 notebook to generate them."
        )

    st.divider()

    st.subheader("4. What do the discovered customer groups look like?")

    if profiles is not None:
        fig = px.bar(
            profiles,
            x="cluster",
            y="customers",
            text_auto=True,
            title="Customers assigned to each cluster",
        )
        st.plotly_chart(fig, width="stretch")

        explain(
            "What does this show?",
            "The chart shows the population size of each "
            "machine-learning-discovered customer group.",
            "Group sizes are calculated from customer-level "
            "cluster assignments.",
            "Cluster numbers are identifiers, not quality rankings.",
        )
    else:
        st.info(
            "Customer group profiles are pending. "
            "Run the Phase 06 explainability notebook."
        )

    st.divider()

    st.subheader("Explore the evidence")

    for label, data in [
        ("Baseline clustering", clustering),
        ("Stability", stability),
        ("Model validation", validation),
        ("Customer group profiles", profiles),
    ]:
        if data is not None:
            with st.expander(label):
                st.dataframe(data, hide_index=True)
                st.download_button(
                    f"Download {label.lower()}",
                    data.to_csv(index=False),
                    file_name=label.lower().replace(" ", "_") + ".csv",
                    mime="text/csv",
                    key=f"download_{label}",
                )


main()
