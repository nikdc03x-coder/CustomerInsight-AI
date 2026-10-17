# Phase 06 — Explainable Customer Behaviour Discovery

## Project

CustomerInsight AI

## 1. Research objective

Investigate whether customer groups discovered by
K-Means can be described using understandable
purchasing behaviour features.

This phase focuses on group-level interpretation,
not causal explanations of individual decisions.

## 2. Previous research

Phase 04 compared three clustering algorithms.

K-Means achieved the highest baseline silhouette
score among the tested configurations.

Phase 05 evaluated its assignment stability under
different random seeds, training subsets and noise.

We now investigate what the discovered groups
mean in terms of purchasing behaviour.

## 3. Research questions

RQ1: How do recency, frequency and spending
differ across the discovered customer groups?

RQ2: Which features distinguish each cluster
from the overall customer population?

RQ3: Can these differences be communicated
without unsupported assumptions?

## 4. Methodology

We use the customer-level RFM dataset created
during Phase 03.

K-Means is fitted using the preprocessing and
baseline configuration established in Phase 04.

Cluster assignments are attached to the original
customer-level dataset.

We calculate:

- Number of customers in each cluster
- Share of customers in each cluster
- Median recency
- Median purchase frequency
- Median positive spending
- Total positive spending
- Relative medians compared with the population

## 5. Explanation method

We compare each cluster median with the
corresponding population median.

Relative values above 1.2 are described as higher.

Relative values below 0.8 are described as lower.

Values between these thresholds are described
as similar.

These thresholds are descriptive conventions,
not statistical significance tests.

When a population median is zero, we avoid
calculating an invalid ratio.

## 6. Implementation

Python module:
src/customerinsight/explanations.py

Tests:
tests/test_explanations.py

Research notebook:
notebooks/customer_explainability.ipynb

Outputs:
results/experiments/customer_cluster_profiles.csv
results/experiments/customer_cluster_descriptions.csv

## 7. Research results

Complete after executing the notebook.

Number of customers:

Number of groups:

Largest group:

Smallest group:

Group with lowest median recency:

Group with highest median frequency:

Group with highest median positive spending:

## 8. Interpretation

Explain what distinguishes each cluster.

Use actual medians and comparisons from
the notebook rather than invented descriptions.

Avoid assuming customer satisfaction,
income, loyalty, motivation or future behaviour.

## 9. Limitations

The explanation uses the same RFM features that
the clustering algorithm used.

Therefore, differences between clusters are
expected and do not independently validate them.

Median-based summaries can hide variation
within individual groups.

A small cluster may contain too few customers
for reliable generalization.

The model is trained on historical data from
one retailer.

Descriptions are not causal explanations.

## 10. Implementation references

Pandas:
https://pandas.pydata.org/docs/

scikit-learn K-Means:
https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

Plotly:
https://plotly.com/python/

Original dataset:
https://archive.ics.uci.edu/dataset/352/online+retail

## 11. Next research phase

Evaluate the clarity and consistency of
customer group descriptions.

Develop an interactive application that presents
the research findings to non-technical users.

## 12. Completion record

Status: Pending notebook execution

Automated tests: Pending

Research findings: Pending

Git commit: Pending

## Interactive Explainability Dashboard

We extended the explainability analysis into an
interactive Streamlit research dashboard.

The interface allows users to:

- Switch between different statistical visualizations.
- Investigate individual customer groups.
- Compare customer groups using original RFM values.
- Read explanations calculated from the actual data.
- Inspect the underlying customer-level observations.

### Visualization design

We use Plotly to provide interactive graphs.

Different chart types answer different questions.
Bar charts compare groups, while distribution
charts reveal variation within groups.

Line and area plots represent connected categorical
comparisons, not changes over time.

### Explainability approach

The dashboard uses descriptive statistics instead
of generating unsupported claims about customers.

Each visualization includes its interpretation,
purpose, calculation method and limitations.

### Limitations

The interface describes historical purchasing
behaviour rather than predicting future purchases.

Group names depend on the current clustering results.

Median comparisons do not establish causation,
customer motivation or statistical significance.

### Next steps

Validate the dashboard's usability and introduce
more systematic research visualization tests.
