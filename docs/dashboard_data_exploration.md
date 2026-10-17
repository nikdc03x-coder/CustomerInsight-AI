# CustomerInsight AI — Data Exploration Dashboard

## Objective

Extend the Streamlit research application to
visualize original transaction data and the
customer features used for clustering.

## Problem

The earlier dashboard mainly focused on
customer groups and model evaluation.

Users also need to understand the input data
and feature engineering process.

## Implementation

Two new pages were developed:

1. Retail Data Explorer
2. RFM Intelligence

## Retail Data Explorer

The page uses the original UCI Online Retail
transaction workbook.

It supports:

- Data quality investigation
- Monthly positive purchasing trends
- Country-level purchasing comparisons
- Source transaction inspection

## RFM Intelligence

The page uses the processed customer-level
RFM dataset.

It supports:

- Feature explanations
- Histograms
- Box plots
- Violin plots
- Feature relationship scatter plots
- Spearman correlation heatmaps

## Explainability

Each major chart includes an explanation
based on measured statistics.

Explanations distinguish observations
from assumptions and causal claims.

## Implementation libraries

- Pandas
- Plotly Express
- Streamlit
- openpyxl

## Limitations

Original transaction data may contain
cancellations and incomplete records.

Gross positive purchasing value is not
fully reconciled net revenue.

RFM values describe recorded historical
purchasing behaviour.

Customer-level correlations do not
establish causality.

## Validation

Automated tests: Pending verification

Manual dashboard review: Pending verification

## Next steps

Improve the interface consistency,
automate dashboard data validation,
and finalize end-to-end research
reproducibility.
