
from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks/01_data_exploration.ipynb"


def markdown(text):
    """Add a research explanation to the notebook."""
    return nbf.v4.new_markdown_cell(text.strip())


def code(text):
    """Add an executable Python cell."""
    return nbf.v4.new_code_cell(text.strip())


cells = [
    markdown("""
# CustomerInsight AI — Exploratory Data Analysis

**Phase 02: Understanding Real Customer Transactions**

### Research objective

Before applying machine learning, we need to understand
what the dataset contains, identify data-quality issues,
and explore how purchasing behaviour varies.

**Dataset:** UCI Online Retail (2010–2011)

**Source:** https://archive.ics.uci.edu/dataset/352/online+retail

**Important:** The charts below describe historical data
from one retailer. They are not evidence of general
customer behaviour across all businesses.
"""),

    markdown("""
## 1. Load the research dataset

**Why are we doing this?**

We first read the original dataset without removing
missing values or cancelled transactions.

This allows us to investigate the raw data and make
our preprocessing decisions transparently.
"""),

    code("""
from pathlib import Path

import pandas as pd
import plotly.express as px

from customerinsight.retail import (
    load_retail_data,
    data_quality_summary,
    valid_sales,
)

# The notebook lives inside the notebooks folder.
PROJECT_ROOT = Path.cwd().resolve()

if PROJECT_ROOT.name == "notebooks":
    PROJECT_ROOT = PROJECT_ROOT.parent

DATA_PATH = PROJECT_ROOT / "data/raw/Online Retail.xlsx"

df = load_retail_data(DATA_PATH)

print(f"Loaded {len(df):,} transaction rows")
display(df.head())
"""),

    markdown("""
## 2. Understand the dataset

A row represents a product line on an invoice,
not necessarily a different customer or a complete order.

We should not confuse the number of rows with the
number of customers.

Let's examine the dataset structure.
"""),

    code("""
print("Dataset shape:", df.shape)
print("\\nColumn types:")
display(df.dtypes.to_frame("Data type"))

print("\\nData quality summary:")
quality = data_quality_summary(df)
display(pd.DataFrame(
    quality.items(),
    columns=["Check", "Value"]
))
"""),

    markdown("""
## 3. Where is data missing?

### Why use a bar chart?

A bar chart makes it easy to compare the number of
missing values across the dataset's columns.

**How to read it:** Taller bars mean that more values
are missing from that column.

**Research significance:** Missing customer identifiers
may prevent us from linking purchases to individual
customers during segmentation.
"""),

    code("""
missing = df.isna().sum().sort_values(ascending=False)

fig = px.bar(
    x=missing.index,
    y=missing.values,
    title="How much information is missing?",
    labels={
        "x": "Dataset column",
        "y": "Missing records",
    },
    text=missing.values,
)

fig.update_traces(textposition="outside")
fig.update_layout(
    xaxis_tickangle=-30,
    yaxis_title="Number of missing values",
)
fig.show()

print(
    "Customer ID missing rate:",
    f"{df['customer_id'].isna().mean():.1%}"
)
"""),

    markdown("""
## 4. Examine positive sales

For the next charts, we focus on transaction rows
with a positive quantity and price, excluding
identified cancellations.

**Important limitation:**

These charts show gross positive sales, not
net revenue or profit. Refunds, cancellations,
taxes and expenses are not fully accounted for.

We will study how to handle these issues during
feature engineering.
"""),

    code("""
sales = valid_sales(df)
sales = sales.assign(
    month=sales["invoice_date"].dt.to_period("M").astype(str)
)

print(f"Positive-sale rows: {len(sales):,}")
print(f"Gross positive sales: £{sales['line_total'].sum():,.2f}")
"""),

    markdown("""
## 5. How do sales change over time?

### Why use a line chart?

A line chart helps us observe patterns and changes
in a numerical value across time.

**How to read it:** A higher point represents more
gross positive sales during that month.

**Research significance:** Time variation may
influence customer behaviour features and clustering.

**Limitation:** The first and last months may have
incomplete coverage. We must avoid treating them
as directly comparable to complete months.
"""),

    code("""
monthly = (
    sales.groupby("month", as_index=False)["line_total"]
    .sum()
    .sort_values("month")
)

fig = px.line(
    monthly,
    x="month",
    y="line_total",
    markers=True,
    title="How do gross positive sales change each month?",
    labels={
        "month": "Month",
        "line_total": "Gross positive sales (£)",
    },
)

fig.update_layout(hovermode="x unified")
fig.show()

display(monthly)
"""),

    markdown("""
## 6. Which countries contribute most to sales?

### Why use a horizontal bar chart?

Country names are easier to read horizontally.

**How to read it:** Longer bars represent larger
gross positive sales totals.

**Research significance:** Geographic differences
may affect the interpretation of customer behaviour.

**Limitation:** Higher total sales do not necessarily
mean higher average spending per customer.
"""),

    code("""
countries = (
    sales.groupby("country", as_index=False)["line_total"]
    .sum()
    .nlargest(10, "line_total")
    .sort_values("line_total")
)

fig = px.bar(
    countries,
    x="line_total",
    y="country",
    orientation="h",
    title="Top 10 countries by gross positive sales",
    labels={
        "line_total": "Gross positive sales (£)",
        "country": "Customer country",
    },
)

fig.show()
display(countries)
"""),

    markdown("""
## 7. How are individual line-item values distributed?

### Why use a histogram?

A histogram shows how often different numerical
values occur.

**How to read it:** Taller bars mean more transaction
lines fall within that value range.

We show values up to the 99th percentile to keep
the typical range visible. The excluded extreme
values remain in the original data.

This is not a customer-spending distribution.
Customer-level spending will be studied in Phase 03.
"""),

    code("""
upper = sales["line_total"].quantile(0.99)
typical_lines = sales.loc[
    sales["line_total"] <= upper, "line_total"
]

fig = px.histogram(
    x=typical_lines,
    nbins=50,
    title="How are typical purchase-line values distributed?",
    labels={
        "x": "Line-item value (£)",
        "y": "Number of transaction lines",
    },
)

fig.update_layout(
    yaxis_title="Number of transaction lines"
)
fig.show()

print(f"99th percentile of line-item value: £{upper:,.2f}")
"""),

    markdown("""
## 8. Research observations and limitations

After running the notebook, record:

1. Which columns contain missing values?
2. How many cancellation records were observed?
3. What changes are visible in monthly positive sales?
4. Which countries contribute most to sales?
5. Does the value distribution appear skewed?
6. Which findings may affect our future clustering?

### What this notebook does not establish

These descriptive charts do not prove causation.

They do not tell us which clustering method is best
or whether identified customer segments will be stable.

Those questions require experiments in later phases.

### Next phase

Create customer-level purchasing features, including
recency, frequency and monetary value.
"""),
]


def main():
    # Generate a standard Jupyter notebook from our research cells.
    notebook = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
            },
        },
    )

    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, NOTEBOOK_PATH)

    print(f"Created: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
