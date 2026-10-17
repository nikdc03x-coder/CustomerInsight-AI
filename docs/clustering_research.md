# Phase 04 — Customer Clustering Experiments

## Project

CustomerInsight AI

## Research objective

Investigate how different unsupervised learning
algorithms discover customer groups using RFM data.

## Research questions

RQ1: How does clustering quality differ between
K-Means, Agglomerative Clustering and DBSCAN?

RQ2: Does each algorithm identify a similar
number of customer groups?

RQ3: How should clustering quality and coverage
be considered when comparing different methods?

## Dataset

Source: UCI Online Retail

Input: data/processed/customer_rfm.csv

Features:

- Recency
- Frequency
- Monetary

Number of customers: Pending experiment execution

## Methodology

### Feature preprocessing

We applied log1p transformation to reduce the
effect of skewed numerical features.

We then used StandardScaler to standardize
their numerical scales.

### Algorithms

K-Means:
Four clusters, random state 42, n_init 10.

Agglomerative Clustering:
Four clusters, default linkage.

DBSCAN:
eps 0.5, min_samples 10.

These are baseline settings, not optimized
parameters.

### Evaluation

We used silhouette scores to investigate
cluster separation.

We also recorded the number of clusters
and the proportion of observations assigned
to non-noise clusters.

DBSCAN noise observations were excluded from
its silhouette calculation.

## Experiment results

Complete this section using the actual output.

| Algorithm     | Clusters | Silhouette | Coverage |
| ------------- | -------: | ---------: | -------: |
| K-Means       |  Pending |    Pending |  Pending |
| Agglomerative |  Pending |    Pending |  Pending |
| DBSCAN        |  Pending |    Pending |  Pending |

## Interpretation

To be completed after executing the notebook.

Explain differences between the algorithms
rather than only identifying the largest score.

Discuss whether the groupings appear understandable
in relation to purchasing behaviour.

## Limitations

Only one dataset has been tested.

The baseline parameters were selected before
systematic hyperparameter evaluation.

Silhouette scores do not directly measure
business value or explanation quality.

DBSCAN may exclude noise observations when
calculating its score.

The experiment does not yet establish
cluster stability across data samples.

## Implementation references

scikit-learn clustering:
https://scikit-learn.org/stable/modules/clustering.html

scikit-learn preprocessing:
https://scikit-learn.org/stable/modules/preprocessing.html

scikit-learn silhouette score:
https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html

## Next research phase

Test clustering stability under changing
data samples, noise and parameter settings.

Investigate whether discovered customer groups
remain consistent.

## Completion record

Status: Pending experiment execution

Tests: Pending verification

Research findings: Pending

Git commit: Pending
