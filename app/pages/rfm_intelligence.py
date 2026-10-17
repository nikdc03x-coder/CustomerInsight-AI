
"""Explore customer-level recency, frequency and spending features."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_ui import page_header, show_chart


ROOT = Path(__file__).resolve().parents[2]
RFM_FILE = ROOT / "data/processed/customer_rfm.csv"

METRICS = {
    "recency": {
        "label": "Recency",
        "unit": "Days since purchase",
        "meaning": "Lower values indicate more recent purchases.",
    },
    "frequency": {
        "label": "Frequency",
        "unit": "Distinct positive-sale invoices",
        "meaning": "Higher values indicate more recorded purchase occasions.",
    },
    "monetary": {
        "label": "Monetary",
        "unit": "Gross positive spending (£)",
        "meaning": "Higher values indicate greater recorded positive spending.",
    },
}


@st.cache_data
def load_rfm():
    """Read the customer features produced in Phase 03."""

    data = pd.read_csv(
        RFM_FILE,
        dtype={"customer_id": "string"},
    )

    required = {"customer_id", *METRICS}

    if not required.issubset(data.columns):
        raise ValueError("The RFM file is missing required columns.")

    if data[list(METRICS)].isna().any().any():
        raise ValueError("The RFM dataset contains missing feature values.")

    return data


def interpretation(title, meaning, finding, limitation):
    """Present the research result in understandable language."""

    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.write(f"**What does this show?** {meaning}")
        st.write(f"**What did we discover?** {finding}")

        with st.expander("How should we interpret it?"):
            st.write(limitation)


def main():
    page_header(
        'Customer insights / Purchasing patterns', 'Purchasing patterns',
        'See when customers last purchased, how often they return and how much they spend.',
        purpose='Explore RFM distributions, compare features, inspect individual customer records and download the feature table.',
        benefit='Understand the measures used to form customer groups, including typical values and unusual purchasing patterns.',
        technical='RFM means Recency, Frequency and Monetary. Frequency counts distinct qualifying invoices; monetary is gross positive spending in GBP.',
    )

    if not RFM_FILE.is_file():
        st.warning(
            "The customer RFM file is missing. "
            "Run the Phase 03 feature-engineering script."
        )
        st.stop()

    try:
        customers = load_rfm()
    except ValueError as error:
        st.error(str(error))
        st.stop()

    kpis = st.columns(4)

    kpis[0].metric("Customer records", f"{len(customers):,}")
    kpis[1].metric(
        "Median recency",
        f"{customers['recency'].median():,.1f} days",
    )
    kpis[2].metric(
        "Median frequency",
        f"{customers['frequency'].median():,.1f}",
    )
    kpis[3].metric(
        "Median spending",
        f"£{customers['monetary'].median():,.2f}",
    )

    st.divider()

    overview_tab, distribution_tab, relationship_tab, records_tab = (
        st.tabs([
            "RFM Explained",
            "Feature Distributions",
            "Feature Relationships",
            "Customer Records",
        ])
    )

    with overview_tab:
        st.subheader("What is RFM analysis?")

        for feature, info in METRICS.items():
            with st.container(border=True):
                st.markdown(f"### {info['label']}")
                st.write(info["unit"])
                st.caption(info["meaning"])

        st.markdown("### How did we calculate these features?")

        st.write(
            "**Recency:** Number of days since each customer's "
            "most recent qualifying purchase, measured against "
            "the reference date selected during feature engineering."
        )

        st.write(
            "**Frequency:** Number of distinct qualifying "
            "purchase invoices for each customer."
        )

        st.write(
            "**Monetary:** Sum of qualifying positive purchase "
            "values for each customer in GBP."
        )

        st.info(
            "RFM describes recorded historical behaviour. "
            "It does not automatically predict future purchases."
        )

    with distribution_tab:
        st.subheader("How are customer features distributed?")

        metric = st.selectbox(
            "Select a customer feature",
            list(METRICS),
            format_func=lambda value: METRICS[value]["label"],
        )

        chart = st.segmented_control(
            "Visualization",
            ["Histogram", "Box plot", "Violin plot"],
            default="Histogram",
        )

        if chart == "Box plot":
            fig = px.box(
                customers,
                y=metric,
                points="outliers",
                title=f"{METRICS[metric]['label']} — variation",
            )

        elif chart == "Violin plot":
            fig = px.violin(
                customers,
                y=metric,
                box=True,
                points=False,
                title=f"{METRICS[metric]['label']} — distribution",
            )

        else:
            bins = st.slider(
                "Histogram bins", 10, 100, 40
            )

            fig = px.histogram(
                customers,
                x=metric,
                nbins=bins,
                title=f"{METRICS[metric]['label']} — customer distribution",
            )

        fig.update_layout(
            height=460,
            showlegend=False,
        )

        show_chart(fig, width="stretch")

        median = customers[metric].median()
        q1 = customers[metric].quantile(0.25)
        q3 = customers[metric].quantile(0.75)

        interpretation(
            "Understanding this distribution",
            f"This chart explores how the {metric} values "
            "vary across customers.",
            f"The median is {median:,.2f}, with the middle "
            f"50% of customers between {q1:,.2f} and {q3:,.2f}.",
            f"{METRICS[metric]['meaning']} "
            "The median describes the overall population and "
            "does not represent every individual customer.",
        )

    with relationship_tab:
        st.subheader("How do purchasing behaviours relate?")

        left, right = st.columns(2)

        with left:
            x_feature = st.selectbox(
                "Horizontal feature",
                list(METRICS),
                index=1,
                format_func=lambda value: METRICS[value]["label"],
            )

        with right:
            y_feature = st.selectbox(
                "Vertical feature",
                list(METRICS),
                index=2,
                format_func=lambda value: METRICS[value]["label"],
            )

        if x_feature == y_feature:
            st.info("Choose two different features.")
        else:
            sample = customers.sample(
                n=min(3000, len(customers)),
                random_state=42,
            )

            fig = px.scatter(
                sample,
                x=x_feature,
                y=y_feature,
                opacity=0.45,
                title="Relationship between customer behaviour features",
                hover_data=["customer_id"],
            )

            show_chart(fig, width="stretch")

            # Spearman measures monotonic association, not causation.
            correlation = customers[
                [x_feature, y_feature]
            ].corr(method="spearman").iloc[0, 1]

            interpretation(
                "Understanding feature relationships",
                "Each point represents one sampled customer "
                "and its two purchasing measurements.",
                f"The full-dataset Spearman correlation "
                f"between these features is {correlation:.3f}.",
                "Correlation describes association, not causation. "
                "The plot uses a reproducible sample of at most "
                "3,000 customers for readability, while the "
                "correlation uses the complete RFM dataset.",
            )

        st.divider()
        st.subheader("Correlation overview")

        correlation_matrix = customers[
            list(METRICS)
        ].corr(method="spearman")

        heatmap = px.imshow(
            correlation_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
            title="Spearman correlations between RFM features",
        )

        show_chart(heatmap, width="stretch")

        st.caption(
            "Correlation values range from -1 to +1. "
            "They do not establish why behaviours are related."
        )

    with records_tab:
        st.subheader("Inspect the processed customer features")

        st.dataframe(
            customers.head(1000),
            hide_index=True,
            width="stretch",
        )

        st.download_button(
            "Download RFM dataset",
            customers.to_csv(index=False),
            file_name="customer_rfm.csv",
            mime="text/csv",
        )

        st.caption(
            "This is customer-level analytical data, not "
            "the original individual transaction records."
        )


main()
