# Phase 02 — Dataset Selection and Exploration

## Project

CustomerInsight AI

## 1. Research objective

This phase focuses on understanding a real retail
transaction dataset before applying machine learning.

We want to identify data-quality problems, observe
purchasing patterns, and decide which preprocessing
steps are necessary for reliable customer segmentation.

## 2. Dataset selection

Dataset: UCI Online Retail

Source:
https://archive.ics.uci.edu/dataset/352/online+retail

Dataset creator: Daqing Chen

Publication: UCI Machine Learning Repository, 2015

DOI: https://doi.org/10.24432/C5BW33

License: Creative Commons Attribution 4.0

Period covered: December 2010 to December 2011

Original format: Microsoft Excel

Published dataset size: 541,909 transaction rows

## 3. Why we selected this dataset

We selected this dataset because it contains
real purchasing transactions rather than
artificially generated customer profiles.

It includes customer identifiers, invoice dates,
quantities, prices and countries.

These fields can support customer behaviour analysis
and later experiments using unsupervised learning.

## 4. Tools and libraries

Pandas:
Used to read and inspect the transaction data.

openpyxl:
Used to read the original Excel workbook.

Plotly:
Used to create understandable interactive charts.

Jupyter Notebook:
Used to combine experiments, visualizations
and explanations.

pytest:
Used to test data-processing functionality.

## 5. Data quality questions

We will investigate:

- Missing customer identifiers
- Missing product descriptions
- Duplicate transaction rows
- Cancelled orders
- Negative quantities
- Zero or negative prices
- Invalid transaction dates

We will record these issues before deciding
which records should be included in modelling.

## 6. Exploratory visualizations

Our notebook will contain:

1. Missing-value comparison
2. Monthly gross positive sales
3. Sales distribution by country
4. Line-item value distribution

Each visualization includes an explanation
of why the chart was selected and how its
results should be interpreted.

## 7. Important methodological decisions

The original data will be preserved.

No records will be silently deleted during
the initial data-quality inspection.

Descriptive sales charts will use positive
quantity and positive price records while
excluding identified cancellations.

These charts do not represent net revenue
or business profit.

Customer-level segmentation features will
be developed in Phase 03.

## 8. Observations

To be completed after running the notebook.

Total records observed:

Unique customers:

Missing customer IDs:

Cancellation rows:

Duplicate rows:

Main trends observed:

## 9. Limitations

The data comes from one UK-based retailer.

The dataset is historical and may not represent
modern retail purchasing patterns.

Some customers are wholesalers.

Incomplete customer identifiers may limit
customer-level analysis.

Gross positive sales calculations do not
include full refund reconciliation.

## 10. Research questions informed by this phase

Which data-quality problems could affect
customer segmentation?

How should cancellations and missing customer
identifiers be handled during feature engineering?

What purchasing features are likely to be
useful for comparing customer groups?

## 11. Next phase

Phase 03 will create customer-level behavioural
features such as recency, frequency and monetary
value.

We will test and document the transformations
before using them in clustering experiments.

## 12. Completion record

Status: Pending notebook execution

Test results: Pending verification

Research findings: Pending actual observations

Git commit: Pending
