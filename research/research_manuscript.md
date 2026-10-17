# CustomerInsight AI

## An Explainable and Stability-Aware Framework

## for Customer Behaviour Segmentation Using

## Unsupervised Machine Learning

**Document type:** Research manuscript draft

**Status:** In preparation

---

## Abstract

Customer segmentation is used to identify
patterns in purchasing behaviour.

This study investigates unsupervised customer
segmentation using Recency, Frequency and
Monetary (RFM) features derived from historical
retail transactions.

We compare K-Means, Agglomerative Clustering
and DBSCAN using clustering quality measures.

We subsequently examine K-Means assignment
stability under random initialization changes,
training-subset changes and feature perturbations.

An explainability layer describes the resulting
groups using original RFM measurements.

[TODO: Add verified parameter sensitivity results.]

[TODO: Complete the abstract after all results
have been verified.]

## 1. Introduction

Retail transaction data contains information
about when customers purchase, how frequently
they purchase and their historical spending.

Identifying patterns in these measurements can
support exploratory business analysis.

However, clustering presents several challenges:

- Clusters have no predefined ground-truth labels.
- Different algorithms may produce different groups.
- Cluster assignments may change with data
  perturbations or parameter settings.
- Algorithm outputs can be difficult for
  non-technical users to understand.

This project investigates these challenges
through an experimental Python research pipeline.

### 1.1 Research objectives

1. Construct reproducible RFM customer features.
2. Compare multiple unsupervised clustering methods.
3. Evaluate assignment stability.
4. Investigate sensitivity to model configuration.
5. Develop understandable cluster descriptions.
6. Communicate findings through an interactive interface.

### 1.2 Research questions

RQ1: Which tested clustering configuration
produces the strongest baseline separation?

RQ2: How stable are K-Means customer assignments
under the tested perturbations?

RQ3: How sensitive are results to preprocessing
and cluster count?

RQ4: Can customer groups be described using
transparent purchasing statistics?

## 2. Related Work

[TODO: Add and review relevant published papers
on RFM segmentation, clustering, cluster
validation, stability and explainability.]

Do not add citations without checking the
original sources.

## 3. Dataset

The study uses the UCI Online Retail dataset.

The dataset contains transaction records
from a UK-based online retailer during 2010–2011.

The research pipeline constructs customer-level
RFM features from positive sale transactions.

### 3.1 Data cleaning

The baseline processing excludes cancelled
transactions and records without valid customer
identifiers from the positive-sales RFM analysis.

### 3.2 Feature engineering

Recency:
Days between the reference date and the
customer's most recent qualifying purchase.

Frequency:
Number of unique positive-sale invoices.

Monetary:
Total gross value of qualifying positive purchases.

[TODO: Add verified customer count, data-quality
statistics and reference date from Phase 03.]

## 4. Methodology

### 4.1 Clustering

We evaluated:

- K-Means
- Agglomerative Clustering
- DBSCAN

The initial feature representation used
log1p transformation and standardization.

### 4.2 Baseline evaluation

Silhouette score was used to examine
within-cluster cohesion and separation.

DBSCAN coverage was also reported because
some observations may be classified as noise.

### 4.3 Stability evaluation

We investigated three perturbation settings:

- Different random initializations
- Different training subsets
- Small feature perturbations

Adjusted Rand Index measured agreement
between alternative cluster assignments
and a reference partition.

### 4.4 Explainability

The system describes groups using original
RFM values instead of scaled features.

We examine cluster sizes, median recency,
median frequency and median positive spending.

### 4.5 Parameter sensitivity

[TODO: Insert the verified Phase 08 methodology
and findings.]

## 5. Experimental Results

### 5.1 Baseline clustering

| Algorithm     | Silhouette | Coverage |
| ------------- | ---------: | -------: |
| K-Means       |   0.332372 |   1.0000 |
| Agglomerative |   0.270554 |   1.0000 |
| DBSCAN        |   0.289804 |   0.9818 |

K-Means achieved the highest silhouette score
among the tested baseline configurations.

The comparison does not establish global
superiority over other clustering methods.

### 5.2 K-Means stability

| Experiment            | Mean ARI | Std. deviation |
| --------------------- | -------: | -------------: |
| Random initialization |   0.9360 |         0.0298 |
| Training subset       |   0.9413 |         0.0381 |
| Feature noise         |   0.9172 |         0.0200 |

Each experiment was repeated 20 times.

The tested settings generally produced
cluster assignments similar to the baseline.

Training-subset experiments showed the
highest mean agreement, but also the
highest standard deviation.

### 5.3 Parameter sensitivity

[TODO: Insert actual Phase 08 results.]

### 5.4 Explainable cluster profiles

[TODO: Insert verified Phase 06 profiles.]

## 6. Discussion

The baseline experiment suggests that
K-Means produced comparatively well-separated
groups among the tested configurations.

The stability experiments suggest that
its assignments were relatively consistent
under the evaluated perturbations.

However, clustering quality and stability
are not equivalent to business usefulness.

Further interpretation depends on verified
customer group characteristics and broader
validation results.

## 7. Limitations

This study uses one historical retailer dataset.

Cluster results depend on feature engineering,
preprocessing and algorithm settings.

There are no ground-truth customer segment labels.

Silhouette scores measure internal structure,
not actual business outcomes.

Stability results are relative to a reference
partition and selected perturbation settings.

Gross positive spending is not equivalent
to fully reconciled net revenue.

Group descriptions do not establish customer
motivation or causation.

## 8. Conclusion

[TODO: Write after all research results have
been consolidated and reviewed.]

## 9. Future Work

Potential directions include:

- Evaluation on additional datasets
- More extensive parameter sensitivity studies
- Temporal stability experiments
- Human evaluation of explanation clarity
- Assessment of business usefulness

## References

UCI Online Retail dataset:
https://archive.ics.uci.edu/dataset/352/online+retail

scikit-learn documentation:
https://scikit-learn.org/stable/

[TODO: Add verified scholarly references.]

## Reproducibility

The project provides Python source modules,
automated tests, experimental notebooks,
phase research documents and saved result tables.

[TODO: Record the tested environment,
exact commands and all relevant random seeds.]

## Research Evidence and Traceability

| Research question        | Method                                | Supporting evidence          |
| ------------------------ | ------------------------------------- | ---------------------------- |
| RQ1: Data preparation    | Data cleaning and RFM construction    | data_exploration.ipynb       |
| RQ2: Feature engineering | Customer-level RFM calculations       | feature_engineering.ipynb    |
| RQ3: Model comparison    | K-Means, Agglomerative, DBSCAN        | clustering_baseline.csv      |
| RQ4: Stability           | Repeated perturbation experiments     | stability_runs.csv           |
| RQ5: Sensitivity         | K = 2–10 and preprocessing comparison | model_validation_results.csv |

Each numerical claim should be traceable
to a saved experiment result.

Research interpretations must distinguish
observed behaviour from causal conclusions.

## result and discussion

### Customer Segment Characteristics

K-Means clustering with four clusters identified distinct patterns in the purchasing behaviour of 4,338 customers.

Cluster 0 contained 877 customers and was characterized by relatively recent purchases but low purchase frequency. Cluster 1 was the largest group, containing 1,579 customers, and showed the longest median time since purchase (183 days) and the lowest median purchase frequency (1 invoice).

Cluster 2 contained 720 customers and demonstrated the most recent purchasing activity (median recency of 9 days), the highest median purchase frequency (10 invoices), and the highest median positive spending (£3,726.08). Cluster 3 contained 1,162 customers and showed intermediate purchasing patterns, with a median recency of 54 days and a median frequency of 4 invoices.

These findings indicate that RFM-based clustering separates customers with different recorded purchasing patterns. However, the resulting groups are descriptive and should not be interpreted as verified indicators of loyalty, satisfaction, or future behaviour.

### Sensitivity to Preprocessing and Cluster Count

Eighteen K-Means configurations were evaluated using cluster counts from 2 to 10 and two preprocessing approaches: standard scaling and logarithmic transformation followed by standard scaling.

The highest silhouette score under standard scaling was 0.891827 at K=2. Under log transformation and standard scaling, the highest score was 0.426760, also at K=2.

The standard-scaled K=2 configuration showed very low assignment agreement with the original four-cluster model (ARI = 0.003682). This indicates substantially different cluster partitions.

The large difference in silhouette scores demonstrates that clustering evaluation is sensitive to preprocessing and cluster count. However, a high silhouette score alone does not establish that the resulting customer groups are balanced, interpretable, or useful for business decision-making.

Further inspection of the two-cluster configuration is necessary before drawing conclusions about its suitability.

### Stability of the Baseline Clustering

The baseline four-cluster K-Means model was evaluated through 60 experimental runs across three perturbation conditions.

The average Adjusted Rand Index was 0.9360 for changes in random initialization, 0.9413 for training-subset variation, and 0.9172 for feature noise.

These findings provide evidence of relatively consistent cluster assignments under the tested conditions. However, high assignment stability does not establish that the clusters are objectively correct or externally generalizable.

### Overall Interpretation

The experiments suggest that RFM-based customer segmentation can identify distinguishable purchasing behaviour profiles, but the results depend on the selected algorithm configuration and preprocessing approach.

The study highlights the importance of evaluating clustering quality, assignment stability, parameter sensitivity, and interpretability together rather than relying on a single numerical metric.

### Investigation of the High-Silhouette K=2 Configuration

The Phase 08 parameter sensitivity experiment identified
a standard-scaled K-Means configuration with two clusters
that achieved a silhouette score of 0.891827.

This result was substantially higher than the score
of the original four-cluster configuration.

We performed an additional diagnostic analysis to
examine cluster sizes and RFM feature distributions.

**Cluster sizes:** Pending diagnostic execution.

**Cluster proportions:** Pending diagnostic execution.

**Median purchasing behaviour:** Pending diagnostic execution.

**Interpretation:** To be completed using the actual results.

The analysis will help assess whether the high silhouette
score corresponds to broad customer segmentation or
separation of a comparatively small group of observations.

A high silhouette score alone is insufficient to establish
the practical usefulness of the segmentation.

### Investigation of the High-Silhouette K=2 Configuration

The parameter sensitivity experiment identified a K-Means configuration using standard-scaled RFM features and two clusters, achieving a silhouette score of 0.891827.

To investigate this unusually high score, an additional diagnostic experiment examined the cluster sizes and purchasing characteristics.

The resulting partition was highly imbalanced. Cluster 0 contained 4,312 customers (99.4%), whereas Cluster 1 contained only 26 customers (0.6%).

Cluster 1 displayed substantially higher purchasing activity, with a median purchase frequency of 53 invoices and median positive spending of £59,796.87. In comparison, Cluster 0 had a median frequency of 2 invoices and median spending of £667.88.

The smaller cluster also showed more recent purchasing activity, with a median recency of 3.5 days compared with 52 days for the larger cluster.

These findings suggest that the high silhouette score is associated with separating a small group of exceptionally high-activity customers from the broader population.

Although this configuration achieved stronger internal separation, the resulting partition may be less suitable for research objectives requiring several interpretable purchasing-behaviour segments.

Conversely, the smaller cluster could be relevant to investigations of unusual or exceptionally high purchasing activity.

Therefore, model selection should consider cluster size distribution, interpretability, assignment stability and the intended analytical objective alongside silhouette score.

This experiment demonstrates why selecting the model with the highest internal validation score alone can lead to an incomplete assessment of customer segmentation quality.
