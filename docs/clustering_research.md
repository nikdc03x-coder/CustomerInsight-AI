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

We compared three clustering algorithms using
customer-level RFM features.

| Algorithm     | Clusters | Silhouette | Coverage |
| ------------- | -------: | ---------: | -------: |
| K-Means       |        4 |   0.332372 |     100% |
| Agglomerative |        4 |   0.270554 |     100% |
| DBSCAN        |        2 |   0.289804 |   98.18% |

## Interpretation

K-Means achieved the highest silhouette score
among the three baseline configurations.

Agglomerative Clustering produced four clusters,
but its silhouette score was lower than K-Means.

DBSCAN identified two clusters and classified
approximately 1.82% of observations as noise.

The DBSCAN silhouette calculation excluded noise,
so its score is not directly equivalent to those
of the other two algorithms.

These findings represent preliminary results.
They do not establish that K-Means is universally
better for customer segmentation.

## Research limitations

- Only one dataset was evaluated.
- The algorithms used initial parameter settings.
- Cluster stability has not yet been measured.
- Business interpretability has not yet been validated.
- Further experiments are needed before model selection.

## Implementation references

scikit-learn clustering:
https://scikit-learn.org/stable/modules/clustering.html

scikit-learn preprocessing:
https://scikit-learn.org/stable/modules/preprocessing.html

scikit-learn silhouette score:
https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html

## Next research question

How consistently do the algorithms identify
customer groups when the data is resampled
or the model parameters change?
