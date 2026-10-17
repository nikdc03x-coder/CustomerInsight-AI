
"""Explore the original retail transactions and their data quality."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_ui import page_header, show_chart


ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = ROOT / "data/raw/Online Retail.xlsx"

@st.cache_data(show_spinner="Reading retail transactions...")
def load_transactions():
    """Read the original workbook without modifying the source file."""

    data = pd.read_excel(RAW_FILE, engine="openpyxl")
    data["InvoiceDate"] = pd.to_datetime(
        data["InvoiceDate"], errors="coerce"
    )
    return data


def describe_result(title, meaning, finding, limitation):
    """Give each research visualization an understandable explanation."""

    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.write(f"**What this shows:** {meaning}")
        st.write(f"**What we discovered:** {finding}")

        with st.expander("Research interpretation and limitations"):
            st.write(limitation)


def main():
    page_header(
        'Customer insights / Source data', 'Retail data',
        'Understand the transactions behind your analysis, from data quality to purchasing activity over time.',
        purpose='Inspect missing information and cancellations, compare monthly activity and countries, and preview original records.',
        benefit='Spot issues in the source data so you can interpret customer patterns with the right context.',
        technical='A transaction row is a product line, not a customer. Sales charts use qualifying positive purchases, before refund reconciliation.',
    )

    if not RAW_FILE.is_file():
        st.warning(
            "The original workbook is missing. Place "
            "'Online Retail.xlsx' in data/raw/."
        )
        st.stop()

    data = load_transactions()

    # Count cancellations independently of monetary values.
    cancelled = (
        data["InvoiceNo"].astype("string")
        .str.startswith("C", na=False)
    )

    missing_customers = data["CustomerID"].isna()

    # This follows our baseline positive-sales eligibility rules.
    positive_sales = data.loc[
        ~cancelled
        & data["CustomerID"].notna()
        & (data["Quantity"] > 0)
        & (data["UnitPrice"] > 0)
        & data["InvoiceDate"].notna()
    ].copy()

    positive_sales["sale_value"] = (
        positive_sales["Quantity"] * positive_sales["UnitPrice"]
    )

    metrics = st.columns(4)
    metrics[0].metric("Transaction rows", f"{len(data):,}")
    metrics[1].metric(
        "Unique invoices",
        f"{data['InvoiceNo'].nunique():,}",
    )
    metrics[2].metric(
        "Missing customer IDs",
        f"{missing_customers.sum():,}",
    )
    metrics[3].metric(
        "Cancellation rows",
        f"{cancelled.sum():,}",
    )

    st.caption(
        "These counts refer to transaction rows, not unique "
        "customers. Cancellation rows and missing customer IDs "
        "can overlap."
    )

    st.divider()

    quality_tab, timeline_tab, country_tab, records_tab = st.tabs([
        "Data Quality",
        "Purchase Timeline",
        "Country Analysis",
        "Source Records",
    ])

    with quality_tab:
        st.subheader("What problems exist in the source data?")

        quality = pd.DataFrame({
            "Check": [
                "Missing customer ID",
                "Cancelled invoice",
                "Non-positive quantity",
                "Non-positive unit price",
                "Invalid invoice date",
            ],
            "Rows": [
                int(missing_customers.sum()),
                int(cancelled.sum()),
                int((data["Quantity"] <= 0).sum()),
                int((data["UnitPrice"] <= 0).sum()),
                int(data["InvoiceDate"].isna().sum()),
            ],
        })

        style = st.segmented_control(
            "Visualization",
            ["Bar", "Horizontal bar", "Table"],
            default="Bar",
            key="quality_view",
        )

        if style == "Table":
            st.dataframe(quality, hide_index=True)
        elif style == "Horizontal bar":
            fig = px.bar(
                quality,
                x="Rows",
                y="Check",
                orientation="h",
                color="Check",
                title="Source-data quality checks",
            )
            fig.update_layout(showlegend=False)
            show_chart(fig, width="stretch")
        else:
            fig = px.bar(
                quality,
                x="Check",
                y="Rows",
                color="Check",
                text_auto=True,
                title="Source-data quality checks",
            )
            fig.update_layout(showlegend=False)
            show_chart(fig, width="stretch")

        largest = quality.loc[quality["Rows"].idxmax()]

        describe_result(
            "Understanding data quality",
            "Each bar counts transaction rows matching a "
            "specific data-quality condition.",
            f"The largest displayed category is "
            f"{largest['Check'].lower()}, involving "
            f"{largest['Rows']:,} rows.",
            "These conditions overlap, so adding their counts "
            "does not produce the number of invalid records. "
            "Some zero-price rows may represent special "
            "transactions rather than simple data-entry errors.",
        )

    with timeline_tab:
        st.subheader("How did recorded purchases change over time?")

        monthly = positive_sales.copy()
        monthly["month"] = (
            monthly["InvoiceDate"]
            .dt.to_period("M")
            .dt.to_timestamp()
        )

        trend = (
            monthly.groupby("month", as_index=False)
            .agg(
                positive_sales_value=("sale_value", "sum"),
                transaction_rows=("InvoiceNo", "size"),
                invoices=("InvoiceNo", "nunique"),
            )
            .sort_values("month")
        )

        measure = st.selectbox(
            "Choose a measure",
            [
                "positive_sales_value",
                "transaction_rows",
                "invoices",
            ],
            format_func=lambda value: {
                "positive_sales_value": "Gross positive sales (£)",
                "transaction_rows": "Transaction rows",
                "invoices": "Distinct purchase invoices",
            }[value],
        )

        view = st.segmented_control(
            "Chart style",
            ["Line", "Area", "Bar"],
            default="Line",
            key="timeline_view",
        )

        if view == "Bar":
            fig = px.bar(trend, x="month", y=measure)
        elif view == "Area":
            fig = px.area(trend, x="month", y=measure)
        else:
            fig = px.line(
                trend, x="month", y=measure, markers=True
            )

        fig.update_layout(
            title="Monthly positive purchasing activity",
            xaxis_title="Month",
            yaxis_title=measure.replace("_", " ").title(),
            hovermode="x unified",
        )

        show_chart(fig, width="stretch")

        if not trend.empty:
            peak = trend.loc[trend[measure].idxmax()]

            describe_result(
                "Reading purchasing trends",
                "This is a genuine time series based on invoice dates.",
                f"The highest recorded month for this measure was "
                f"{peak['month']:%B %Y}, with "
                f"{peak[measure]:,.2f}.",
                "The first and final months may be incomplete. "
                "Gross positive sales exclude refund reconciliation "
                "and should not be described as net revenue.",
            )

    with country_tab:
        st.subheader("Where were qualifying sales recorded?")

        countries = (
            positive_sales.groupby("Country", as_index=False)
            .agg(
                positive_sales_value=("sale_value", "sum"),
                transaction_rows=("InvoiceNo", "size"),
            )
            .sort_values("positive_sales_value", ascending=False)
        )

        top_n = st.slider(
            "Number of countries",
            min_value=5,
            max_value=min(30, len(countries)),
            value=min(10, len(countries)),
        )

        subset = countries.head(top_n)

        fig = px.bar(
            subset.sort_values("positive_sales_value"),
            x="positive_sales_value",
            y="Country",
            orientation="h",
            color="positive_sales_value",
            color_continuous_scale="Teal",
            title="Countries by gross positive sales",
        )

        fig.update_layout(
            xaxis_title="Gross positive sales (£)",
            yaxis_title="Country",
        )

        show_chart(fig, width="stretch")

        if not subset.empty:
            leader = subset.iloc[0]

            describe_result(
                "Understanding geographic purchasing",
                "Countries are ranked by positive transaction value.",
                f"{leader['Country']} contributed the highest "
                f"value among the displayed countries "
                f"(£{leader['positive_sales_value']:,.2f}).",
                "Country is a recorded transaction attribute. "
                "These results do not prove customer nationality "
                "or identify where individual customers live.",
            )

    with records_tab:
        st.subheader("Inspect the source transactions")

        st.write(
            "The table is a limited preview to keep the dashboard "
            "responsive. It does not display every record at once."
        )

        st.dataframe(data.head(500), hide_index=True, width="stretch")

        st.download_button(
            "Download data-quality summary",
            quality.to_csv(index=False),
            file_name="retail_data_quality.csv",
            mime="text/csv",
        )


main()
