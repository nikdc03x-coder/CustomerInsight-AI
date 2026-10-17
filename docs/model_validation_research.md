# Phase 08 — Advanced Model Validation

## Project

CustomerInsight AI

## 1. Research objective

Investigate the sensitivity of customer segmentation
to changes in cluster count and feature preprocessing.

## 2. Research background

Our baseline experiments used K-Means with four
clusters and log-transformed, standardized RFM data.

K-Means produced the highest silhouette score
among the initially tested clustering models.

A separate stability study found relatively high
agreement under the tested perturbations.

However, these findings do not establish whether
the original configuration is optimal.

## 3. Research questions

RQ1: How do silhouette scores vary with K?

RQ2: How does feature preprocessing affect
clustering quality?

RQ3: How similar are alternative cluster
assignments to the original baseline?

## 4. Methodology

Dataset:
UCI Online Retail

Features:
Recency, Frequency, Monetary

Algorithm:
K-Means

Cluster counts:
2 through 10

Preprocessing:

- StandardScaler
- Log1p + StandardScaler

Random seed:
42

Number of initializations:
10

Evaluation:

- Silhouette score
- K-Means inertia
- Adjusted Rand Index against the baseline

Silhouette scores use a fixed random sample
of up to 1,500 customers to reduce runtime.

## 5. Results

Complete after executing the experiments.

Best K under standard scaling:

Best silhouette under standard scaling:

Best K under log + scaling:

Best silhouette under log + scaling:

Important differences observed:

## 6. Interpretation

Discuss whether changing cluster count or
preprocessing substantially changes the results.

Explain why the configuration with the
highest silhouette score may not necessarily
produce the most useful customer groups.

## 7. Limitations

The same customer dataset is used for model
fitting and silhouette evaluation.

No independent validation dataset is included.

The preprocessing methods were selected as
a limited initial comparison.

ARI measures agreement with the baseline,
not objective clustering correctness.

K-Means inertia is not directly comparable
between differently transformed feature spaces.

The experiments do not establish causation
or universal generalizability.

## 8. Implementation

Module:
src/customerinsight/model_validation.py

Tests:
tests/test_model_validation.py

Notebook:
notebooks/model_validation.ipynb

Outputs:
results/experiments/model_validation_results.csv
results/experiments/model_validation_best.csv

## 9. References

scikit-learn K-Means:
https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

scikit-learn silhouette score:
https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html

scikit-learn Adjusted Rand Index:
https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html

UCI Online Retail:
https://archive.ics.uci.edu/dataset/352/online+retail

## 10. Next research phase

Consolidate the findings from clustering,
stability, explainability and sensitivity studies.

Prepare the scientific research report with
results, limitations and references.

## 11. Completion record

Status: Pending experiment execution

Tests: Pending

Results: Pending

Git commit: Pending
