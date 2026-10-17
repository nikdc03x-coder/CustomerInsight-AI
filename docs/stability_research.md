# Phase 05 — Clustering Stability and Reliability

## Project

CustomerInsight AI

## 1. Research objective

Investigate the consistency of customer clustering
assignments when experimental conditions change.

Our earlier baseline comparison found that K-Means
achieved the highest silhouette score among three
tested algorithms.

This phase evaluates whether its assignments remain
consistent under controlled changes.

## 2. Research questions

RQ1: How sensitive is K-Means clustering to random
initialization?

RQ2: How much do customer assignments change when
the model is trained using different data subsets?

RQ3: How robust are assignments to small amounts
of noise in the customer features?

## 3. Hypotheses

H1: K-Means assignments may change with different
initial random seeds.

H2: Different training subsets may produce changes
in customer assignments.

H3: Noise added to the customer features may
reduce assignment agreement.

These are hypotheses to be tested, not conclusions.

## 4. Dataset and features

Dataset: UCI Online Retail

Input: data/processed/customer_rfm.csv

Features:

- Recency
- Frequency
- Monetary

Preprocessing:

- Log1p transformation
- StandardScaler

The preprocessing transformation was fixed using
the original full dataset for this experiment.

## 5. Experimental design

We use K-Means with four clusters and n_init=10.

Experiment A: Random initialization

Train the model 20 times using different random
seeds and compare assignments with a reference model.

Experiment B: Training subset

Train the model using repeated 80% random subsets
of the customer population.

Predict assignments for the same full customer
population and compare with the reference model.

Experiment C: Feature noise

Add Gaussian noise with standard deviation 0.05
to the standardized feature values.

Retrain the model and compare assignments.

## 6. Evaluation

We use Adjusted Rand Index (ARI).

ARI measures agreement between two partitions
while adjusting for agreement expected by chance.

An ARI of 1 indicates perfect agreement.

Agreement with our baseline does not demonstrate
that the groups represent true customer categories.

## 7. Experimental results

Complete after running the research notebook.

| Experiment            | Mean ARI | Std. deviation | Minimum | Maximum |
| --------------------- | -------: | -------------: | ------: | ------: |
| Random initialization |  Pending |        Pending | Pending | Pending |
| Training subset       |  Pending |        Pending | Pending | Pending |
| Feature noise         |  Pending |        Pending | Pending | Pending |

## 8. Interpretation

To be completed using actual observations.

Discuss the differences between conditions,
the consistency of repeated runs and the
implications for customer segmentation.

## 9. Limitations

We studied one dataset and one main clustering model.

The experimental conditions were selected as
initial baselines and were not systematically tuned.

Preprocessing was fixed instead of refitted
within each training subset.

Results are measured against full-data clustering
assignments, not ground-truth customer categories.

A high ARI does not guarantee useful or
interpretable customer groups.

## 10. Implementation

Python module:
src/customerinsight/stability.py

Tests:
tests/test_stability.py

Research notebook:
notebooks/stability_analysis.ipynb

Experiment outputs:
results/experiments/stability_runs.csv
results/experiments/stability_summary.csv

## 11. Implementation references

scikit-learn K-Means:
https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

scikit-learn Adjusted Rand Index:
https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html

NumPy random generator:
https://numpy.org/doc/stable/reference/random/generator.html

## 12. Next research phase

Extend stability analysis and investigate how
customer segments can be described and explained
using their purchasing behaviour.

## 13. Completion record

Status: Pending experiment execution

Automated tests: Pending verification

Research findings: Pending actual results

Git commit: Pending
