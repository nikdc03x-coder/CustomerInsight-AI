# Phase 03 — Customer Behaviour Feature Engineering

## Project

CustomerInsight AI

## 1. Research objective

This phase investigates how raw retail transactions
can be transformed into meaningful customer-level
features for unsupervised machine learning.

The goal is to prepare a consistent representation
of each customer's observed purchasing behaviour.

## 2. Background

Transaction datasets contain information about
individual products and invoices.

However, customer segmentation requires features
that describe each customer across their purchases.

We selected Recency, Frequency and Monetary (RFM)
analysis as our initial feature engineering approach.

## 3. Research questions

RQ1: How can transaction records be summarized at
the customer level without counting product lines
as separate purchase occasions?

RQ2: How do data quality and filtering decisions
affect the population included in the analysis?

RQ3: What characteristics do the distributions
of recency, frequency and spending exhibit?

## 4. Methodology

The original UCI Online Retail dataset was loaded
using our existing Python data-processing module.

We defined the following features:

Recency:
Days between the reference date and the customer's
most recent valid purchase date.

Frequency:
Number of distinct valid positive-sale invoices
for each customer.

Monetary:
Sum of valid positive purchase-line values
for each customer.

The default reference date is one day after
the latest date in the prepared sales data.

## 5. Data preparation decisions

We include:

- Rows with positive quantities
- Rows with positive unit prices
- Records with valid dates
- Records with customer identifiers
- Records with invoice identifiers

We exclude identified cancellations and returns
from this initial RFM calculation.

The original source data remains unchanged.

These decisions define a baseline and should
not be interpreted as universally optimal.

## 6. Tools used

Pandas:
Grouping transactions and calculating features.

Plotly:
Interactive visualization of feature distributions.

Jupyter Notebook:
Combining analysis, visualizations and explanations.

pytest:
Testing calculation accuracy and data preservation.

## 7. Software implementation

Module:
src/customerinsight/features.py

Notebook:
notebooks/feature_engineering.ipynb

Tests:
tests/test_features.py

Generated output:
data/processed/customer_rfm.csv

## 8. Experimental observations

Complete this section after running the notebook.

Total original transaction rows:

Transaction rows used for RFM:

Number of identified customers:

Median recency:

Median frequency:

Median positive customer spending:

Notable distribution patterns:

## 9. Interpretation

Describe the actual findings here.

Explain whether the observed distributions
suggest differences between customer behaviours.

Do not infer causal explanations or meaningful
customer segments from descriptive plots alone.

## 10. Limitations

RFM describes purchasing history but does not
directly reveal customer motivations.

Customers without valid identifiers cannot
be included in customer-level segmentation.

Our Monetary feature represents gross positive
sales, not net customer revenue.

Refunds and cancellations are not reconciled
against their original purchases.

Results are limited to the source dataset's
retailer, customers and observation period.

## 11. Implementation references

Pandas documentation:
https://pandas.pydata.org/docs/

Plotly documentation:
https://plotly.com/python/

UCI Online Retail dataset:
https://archive.ics.uci.edu/dataset/352/online+retail

Original data citation:
Chen, D. (2015). Online Retail.
UCI Machine Learning Repository.
https://doi.org/10.24432/C5BW33

## 12. Next research phase

We will investigate feature preprocessing and
compare clustering algorithms using the
customer-level dataset.

We will evaluate clustering quality, rather
than choosing algorithms based only on
attractive visualizations.

## 13. Completion record

Status: Pending notebook execution and verification

Automated test results: Pending

Actual research observations: Pending

Git commit: Pending
