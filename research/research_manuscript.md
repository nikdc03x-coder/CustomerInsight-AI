# CustomerInsight AI: An Explainable and Stability-Aware Framework for Customer Behaviour Segmentation Using Unsupervised Machine Learning

**Document type:** Research manuscript draft  
**Status:** Consolidated draft — literature review and independent reproducibility verification outstanding  
**Research data:** UCI Online Retail, historical transactions from 2010–2011  
**Last consolidated:** 17 October 2026

> **Evidence note.** Numerical findings in this manuscript come from the experimental outputs reported for CustomerInsight AI. This draft does not claim independent replication, external validation, or a completed literature review. Statements about possible explanations and business applications are clearly distinguished from measured findings.

## Abstract

Customer segmentation aims to identify differences in purchasing behaviour that may assist exploratory retail analysis. This study investigates a reproducible, interpretable approach to segmentation using customer-level recency, frequency and monetary (RFM) features constructed from historical transactions in the UCI Online Retail dataset. Three unsupervised learning methods—K-Means, Agglomerative Clustering and DBSCAN—were evaluated in a baseline comparison. The four-cluster K-Means configuration achieved a silhouette score of **0.332372**, compared with **0.270554** for Agglomerative Clustering and **0.289804** for the evaluated DBSCAN configuration; the DBSCAN coverage was **98.18%**. Stability was assessed through 60 runs spanning random initialization, training-subset variation and feature noise, with mean adjusted Rand index (ARI) values of **0.9360**, **0.9413** and **0.9172**, respectively. The four-cluster solution described **4,338 customers** with different observed RFM profiles. A sensitivity study evaluated 18 K-Means configurations across two preprocessing approaches and cluster counts of 2–10. Although standard scaling with two clusters produced a high silhouette score (**0.891827**), a follow-up diagnostic found a highly imbalanced partition: **4,312 customers (99.40%)** in one group and **26 (0.60%)** in the other. This illustrates that high internal separation does not, by itself, establish useful broad segmentation. The project also includes an interactive research dashboard and a system for inspecting saved research evidence. Findings are descriptive and restricted to the dataset, configurations and validation conditions studied.

**Keywords:** customer segmentation; RFM; K-Means; unsupervised learning; clustering stability; adjusted Rand index; silhouette score; explainable analytics; research reproducibility.

## 1. Introduction

Historical retail records document when customers transact, how often they buy, and the monetary value of their recorded purchases. Summarizing these observations at customer level can help identify differences in purchasing patterns. Recency, frequency and monetary (RFM) analysis provides an interpretable representation of these behaviours.

Customer segmentation using unsupervised machine learning remains challenging. Unlike supervised classification, the clustering task has no predefined segment labels against which predictions can be judged. Results can change when algorithms, preprocessing rules, cluster counts or training samples change. Furthermore, a high internal clustering score does not necessarily establish that a partition is useful for retail analysis.

CustomerInsight AI was developed as an experimental Python framework that integrates customer-level feature engineering, comparative clustering, assignment-stability analysis, sensitivity testing, descriptive cluster profiling and interactive communication of research findings. The work emphasizes the interpretation and verification of experimental outcomes rather than the automatic acceptance of a single numerical score.

### 1.1 Research objectives

1. Construct interpretable customer-level RFM features from qualifying historical transactions.
2. Compare selected clustering algorithms using recorded internal evaluation measures.
3. Examine K-Means assignment stability under defined perturbation conditions.
4. Assess sensitivity to preprocessing and the number of clusters.
5. Describe discovered groups using original, unscaled RFM measurements.
6. Make experimental findings, supporting files and limitations accessible through an interactive dashboard.

### 1.2 Research questions

- **RQ1 — Algorithm comparison:** Among the tested baseline configurations, which clustering method achieved the highest recorded silhouette score, and what qualifications affect the comparison?
- **RQ2 — Stability:** How consistent were the baseline K-Means assignments under changes in initialization, training subsets and small feature perturbations?
- **RQ3 — Sensitivity and model choice:** How did cluster count and preprocessing affect the evaluated results, and what did the unusually high-scoring two-cluster configuration reveal?
- **RQ4 — Interpretability:** How did the four baseline customer groups differ in their recorded RFM characteristics?

### 1.3 Scope and contribution

The contribution is an integrated experimental and explanatory workflow, not a claim to have invented a new clustering algorithm. The study combines standard, established Python machine-learning methods with systematic comparisons, stability experiments, a targeted follow-up diagnostic and traceable descriptive findings. Business outcomes, causal explanations and predictive customer behavior are not evaluated.

## 2. Related Work and Theoretical Background

### 2.1 RFM-based customer representation

RFM represents purchasing history through time since the most recent qualifying transaction (recency), the number of qualifying purchase occasions or invoices (frequency), and recorded expenditure (monetary). Its appeal for exploratory segmentation lies in its transparent connection to observed transaction data. Its limitation is that three summary features cannot describe all dimensions of customer behaviour.

### 2.2 Unsupervised segmentation methods

K-Means partitions observations around cluster centers; Agglomerative Clustering forms groups through hierarchical merging; DBSCAN identifies density-connected groups and may label some points as noise. These methods embody different assumptions and need not produce directly comparable partitions even on the same customer representation.

### 2.3 Internal validation and stability

The silhouette score evaluates within-group cohesion relative to separation from another group, under the chosen distance representation. Adjusted Rand index measures agreement between two partitions after adjustment for chance. Neither metric independently confirms that discovered groups represent true customer categories or create business value. A partition may also be stable while reflecting a persistent dataset artefact.

### 2.4 Explainability and reproducibility

Describing clusters in original RFM units allows readers to understand observed purchasing differences without interpreting standardized coordinates. Saving experiment tables, methods, random settings and data-preparation decisions improves auditability; full reproducibility additionally requires successfully rerunning the pipeline under a documented environment.

**Literature-review status:** The sections above provide conceptual background only. A publication-ready literature review still requires reading and citing verified original scholarly works addressing RFM segmentation, cluster validation, stability and interpretability. Specific paper claims and citations have intentionally not been invented.

## 3. Dataset and Feature Construction

### 3.1 Dataset

The study uses the **UCI Online Retail** dataset, a historical transactional dataset associated with a UK-based online retailer during 2010–2011. The analysis produces **4,338 customer-level RFM records** after applying the implemented customer and transaction eligibility rules. This is the number of customers in the processed RFM result, not the number of original transaction rows.

Dataset source: <https://archive.ics.uci.edu/dataset/352/online+retail>.

### 3.2 Transaction eligibility and cleaning

The baseline feature-engineering process uses qualifying positive sales. Cancelled transactions and records lacking valid customer identifiers are excluded from the positive-sales RFM analysis. The treatment does not amount to complete customer-level refund reconciliation. Thus, monetary values are **gross qualifying positive spending**, not verified net revenue or profit.

Further publication details to retrieve from the original preprocessing output include the precise reference date, the count of excluded transactions and the relevant data-quality statistics. These values are not established by the manuscript source alone and are not inserted as guesses.

### 3.3 RFM feature definitions

For each included customer:

- **Recency:** Number of days between the experiment's reference date and the most recent qualifying purchase. Lower values correspond to more recent recorded activity.
- **Frequency:** Count of distinct qualifying positive-sale invoices.
- **Monetary:** Sum of the monetary values of qualifying positive-sale transactions over the observed dataset period.

The processed customer-level dataset is stored at `data/processed/customer_rfm.csv`.

## 4. Research Methodology

### 4.1 Feature preprocessing

The baseline clustering experiments used `log1p` transformation followed by standardization of RFM features. This transformation reduces the influence of large raw differences in non-negative RFM values. The sensitivity experiments compared this representation with **standard scaling without the logarithmic transformation**. Because these transformations change the feature-space distances, silhouette values calculated under different preprocessing representations require careful interpretation.

### 4.2 Baseline algorithm comparison

The study evaluated three configurations: K-Means with four clusters, Agglomerative Clustering with four clusters, and a DBSCAN configuration producing two non-noise groups. Silhouette score was used for internal clustering assessment. Coverage reports the proportion of observations assigned to non-noise groups; it is particularly relevant to DBSCAN, which may designate points as noise. Comparisons apply only to these tested configurations and evaluation conventions.

### 4.3 Assignment-stability experiments

The four-cluster K-Means solution was assessed through three experimental conditions:

1. **Random initialization:** Repeating the clustering process with differing random starts.
2. **Training-subset variation:** Examining assignment agreement when the training observations are varied.
3. **Feature noise:** Introducing small perturbations to the feature representation.

Each condition had **20 runs**, giving **60 runs** in total. ARI measured agreement with a reference partition. The results represent tested perturbation settings rather than a guarantee of stability under all possible conditions.

### 4.4 Cluster explainability

The resulting groups were summarized using customer counts and the median values of unscaled recency, frequency and positive spending. Relative group descriptions were derived from observed summary statistics, avoiding unsupported labels such as guaranteed “loyal,” “lost” or “profitable” customers.

### 4.5 Parameter sensitivity

K-Means was evaluated for **K = 2 through K = 10** under two preprocessing approaches: (i) standard scaling and (ii) `log1p` followed by standard scaling. This produced **18 saved configurations**. The reported measures included silhouette score, inertia and ARI relative to the baseline partition. Inertia should be compared cautiously, especially across differing scaled feature representations or values of K.

### 4.6 Follow-up diagnosis of the highest-scoring configuration

The standard-scaled K=2 solution achieved a noticeably higher silhouette score than the four-cluster baseline. A separate experiment reproduced the two-cluster assignment and examined cluster membership counts, customer shares and RFM distributions to investigate whether the model was separating a very small set of exceptional purchasers.

### 4.7 Research output inspection

The project stores experiment results as CSV tables and presents them through Streamlit. A research audit checks expected file availability and selected schema/numerical constraints. Additional consistency checks were proposed and implemented in the project workflow, but this manuscript does not claim verified passing reconciliation results because their execution output has not been supplied. File availability should not be confused with scientific correctness or reproduction of the entire workflow.

## 5. Experimental Results

### 5.1 Baseline clustering comparison (RQ1)

| Algorithm                | Non-noise clusters | Silhouette score | Coverage |
| ------------------------ | -----------------: | ---------------: | -------: |
| K-Means                  |                  4 |     **0.332372** |   1.0000 |
| Agglomerative Clustering |                  4 |         0.270554 |   1.0000 |
| DBSCAN                   |                  2 |         0.289804 |   0.9818 |

K-Means recorded the highest silhouette score among the three tested baseline configurations. DBSCAN assigned approximately 98.18% of the evaluated observations to non-noise groups. The result does not establish global superiority of K-Means: the methods used different resulting cluster counts, and DBSCAN's noise treatment affects the interpretation of coverage and comparison.

**Evidence:** `results/experiments/clustering_baseline.csv`.

### 5.2 K-Means assignment stability (RQ2)

| Perturbation condition | Runs |   Mean ARI | Standard deviation | Minimum | Maximum |
| ---------------------- | ---: | ---------: | -----------------: | ------: | ------: |
| Random initialization  |   20 |     0.9360 |             0.0298 |  0.9132 |  1.0000 |
| Training subset        |   20 | **0.9413** |             0.0381 |  0.8840 |  0.9942 |
| Feature noise          |   20 |     0.9172 |             0.0200 |  0.8756 |  0.9408 |

All three conditions yielded high average agreement with the reference partition under the tested settings. The training-subset condition had the highest mean ARI and the highest reported variation. The feature-noise condition had the lowest mean ARI. These measurements reflect relative partition agreement, not proof of segment validity.

**Evidence:** `results/experiments/stability_runs.csv` and `results/experiments/stability_summary.csv`.

### 5.3 Descriptive profiles of the four baseline groups (RQ4)

| Cluster   | Customers | Customer share | Median recency (days) | Median frequency (invoices) | Median positive spending (£) |
| --------- | --------: | -------------: | --------------------: | --------------------------: | ---------------------------: |
| 0         |       877 |         20.22% |                    19 |                           2 |                       450.84 |
| 1         |     1,579 |         36.40% |                   183 |                           1 |                       300.42 |
| 2         |       720 |         16.60% |                     9 |                          10 |                     3,726.08 |
| 3         |     1,162 |         26.79% |                    54 |                           4 |                     1,353.74 |
| **Total** | **4,338** |  **100.01%\*** |                     — |                           — |                            — |

\* Customer shares are individually rounded to two decimal places, which explains the 0.01 percentage-point total difference.

Cluster 1 was the largest group and exhibited the longest median interval since a qualifying purchase, the lowest median invoice frequency and the lowest median positive spending. Cluster 2 had the most recent median activity, the highest median frequency and highest median positive spending. Cluster 0 showed comparatively recent but infrequent purchases; Cluster 3 had intermediate RFM characteristics. These patterns describe historical transactions, not customer intent, satisfaction, lifetime value or prospective churn.

**Evidence:** `results/experiments/customer_cluster_profiles.csv`.

**Precision note:** The terminal export used to consolidate this table displayed some monetary columns without a visible separator. Median values are reported to two decimals from that export. The source CSV should be checked for full-precision values before final submission.

### 5.4 Sensitivity to preprocessing and K (RQ3)

| Preprocessing          | Highest observed silhouette | K at highest silhouette | ARI against baseline at that K |
| ---------------------- | --------------------------: | ----------------------: | -----------------------------: |
| Standard scaling       |                **0.891827** |                       2 |                       0.003682 |
| Log + standard scaling |                **0.426760** |                       2 |                       0.304038 |

Across the 18 recorded configurations, the maximum silhouette value under each preprocessing approach occurred at K=2. For the log-transformed and standardized representation, K=4 had a silhouette score of **0.333866** and ARI of **1.000000** relative to the baseline partition. The score is close to—but not identical to—the baseline K-Means score of **0.332372**, indicating that the evaluation procedures and/or implementation settings must be checked before asserting exact comparability.

The very low ARI of **0.003682** for standard-scaled K=2 indicates minimal agreement with the baseline four-group partition under the comparison used. A strong silhouette score therefore did not imply preservation of the original customer groups. ARI comparisons involving different K values reflect partition disagreement, not a direct ranking of cluster quality.

**Evidence:** `results/experiments/model_validation_results.csv` and `results/experiments/model_validation_best.csv`.

### 5.5 Diagnostic investigation of standard-scaled K=2 (RQ3)

| Statistic                     | Cluster 0 |  Cluster 1 |
| ----------------------------- | --------: | ---------: |
| Customers                     | **4,312** |     **26** |
| Share of customers            | **99.4%** |   **0.6%** |
| Median recency (days)         |      52.0 |        3.5 |
| Median frequency (invoices)   |         2 |         53 |
| Median positive spending (£)  |    667.88 |  59,796.87 |
| Maximum positive spending (£) | 77,183.60 | 280,206.02 |

The two-cluster partition was highly imbalanced. The smaller cluster represented only 26 of 4,338 customers, with substantially higher recorded purchasing frequency and spending than the larger group. This observation is consistent with the model separating an exceptionally high-activity group from the broader customer population. It provides a plausible explanation for the unusually high silhouette score, but the precise contribution of outliers to the metric was not isolated experimentally.

This division may be relevant to exceptional-customer detection but differentiates little within the 99.4% majority group. Its suitability should be evaluated against the analytical objective rather than ruled out automatically because of imbalance.

**Evidence:** `results/experiments/k2_cluster_diagnostics.csv`.

## 6. Discussion

### 6.1 What the baseline comparison supports

The evaluated four-cluster K-Means model provided greater internal separation than the specific Agglomerative and DBSCAN baselines. This supports using it as a useful reference partition for subsequent description and stability testing. It does not imply that four groups or K-Means would be optimal across other configurations, retail datasets or feature definitions.

### 6.2 Stability versus validity

The mean ARI results between 0.9172 and 0.9413 indicate considerable agreement with the reference partition under the evaluated perturbations. Nevertheless, repeated agreement can occur for a systematically misleading structure. Stability is therefore an additional quality dimension, not a substitute for business or external validation.

### 6.3 Why the highest silhouette was not automatically preferred

The standard-scaled K=2 configuration had the highest recorded silhouette score but separated only 26 exceptionally high-activity customers from the remaining 4,312. This is a concrete example of the gap between optimizing an internal metric and producing informative segmentation for a particular task. Neither the two-cluster nor the four-cluster solution can be declared universally superior without specifying that task and evaluating its downstream consequences.

### 6.4 Interpretability of the four baseline groups

Four RFM profiles exposed more differentiated purchasing patterns than the two-group diagnostic: less-recent low-frequency customers, recent high-frequency and higher-spending customers, and groups with intermediate or recent but less frequent purchasing behaviour. The labels are descriptive summaries rather than scientifically validated customer categories. Medians do not convey all within-group variability, and additional distribution-level checks remain useful.

### 6.5 Contribution of the integrated workflow

The project demonstrates the value of combining algorithm comparison, stability analysis, preprocessing sensitivity, follow-up diagnostics and transparent descriptive profiling. The dashboard provides an interface for inspecting saved evidence, while the research manuscript records assumptions, observed findings and remaining uncertainties. These components form a research-oriented analytical workflow using existing open-source libraries rather than a novel clustering method.

## 7. Limitations and Threats to Validity

1. **Single historical source:** Results concern one retailer's 2010–2011 transactions and may not generalize to other businesses, periods or retail contexts.
2. **Transaction selection:** Monetary totals reflect positive qualifying purchases; cancellations and refunds are not fully reconciled into net customer revenue.
3. **Restricted feature representation:** RFM does not directly capture products, geography, customer motivation, satisfaction or seasonal preferences.
4. **No ground-truth segmentation:** There are no verified segment labels with which to establish real-world clustering accuracy.
5. **Configuration dependence:** Results depend on preprocessing, distance representation, algorithm settings and K.
6. **Metric limitations:** Silhouette and ARI quantify specific mathematical properties, not business usefulness or causal relationships.
7. **Cluster-size imbalance:** The high-scoring K=2 model showed extreme imbalance. This is informative diagnostically but not a sufficient reason alone to reject it.
8. **Incomplete external validation:** No prospective business experiment or independent retail dataset has verified the practical value of the groups.
9. **Reproduction still pending:** Saving outputs and passing basic file audits does not independently establish successful rerun of every notebook and experiment in a clean environment.
10. **Documentation gaps:** The precise data-cleaning counts, feature reference date, full runtime settings and verified scholarly citations need to be incorporated from original sources before formal submission.

## 8. Conclusion

CustomerInsight AI investigated RFM-based customer segmentation through multiple unsupervised clustering methods and complementary evaluation procedures. On the 4,338-customer processed dataset, the tested four-cluster K-Means configuration achieved the highest silhouette score in the baseline algorithm comparison. Sixty stability runs showed relatively strong assignment agreement with a reference partition under three controlled perturbation conditions, and descriptive profiling identified distinct patterns of purchasing recency, frequency and positive spending.

An 18-configuration sensitivity analysis revealed that the highest silhouette score did not correspond to the chosen four-group representation. Follow-up examination of standard-scaled K=2 showed that 99.4% of customers belonged to one group while 0.6% formed an exceptionally high-activity group. This supports a central methodological lesson: **clustering decisions should be informed by model separation, robustness, group composition, interpretability and research purpose together**, rather than a single numerical ranking.

The findings are exploratory, dataset-specific and descriptive. They do not establish causal customer categories or demonstrated commercial impact. Their value lies in the combination of observable results, targeted diagnosis and transparent interpretation.

## 9. Future Work

- Reproduce each experiment from the original source data in a clean environment and document settings, runtime and output agreement.
- Evaluate additional retail datasets and more recent observation windows to examine external validity.
- Study temporal changes in purchasing segments and the effect of the recency reference date.
- Compare alternative feature representations and clustering hyperparameters using clearly matched evaluation procedures.
- Examine within-group distributions and influential high-spending observations in more depth.
- Evaluate explanation clarity with users and test whether the partitions support real decisions.
- Investigate applications to anomaly detection and exceptional purchasing activity separately from broad segmentation.

## References

1. UCI Machine Learning Repository. **Online Retail**. <https://archive.ics.uci.edu/dataset/352/online+retail>.
2. scikit-learn developers. **scikit-learn documentation**. <https://scikit-learn.org/stable/>.

**Reference status:** These are verified resource pointers already included in the project manuscript, not a substitute for peer-reviewed related work. Before academic submission, add carefully reviewed original scholarly references and in-text citations for RFM, clustering methods, silhouette, ARI, stability and explainability. Do not cite unread work as if it had been reviewed.

## Appendix A. Computational Reproducibility

### A.1 Project environment

The implementation uses Python and existing libraries including Pandas, NumPy, scikit-learn, Plotly and Streamlit. The exact installed versions are to be taken from the generated `docs/research_environment.md`; no software versions are asserted here without the actual environment record.

### A.2 Research artifacts

| Research stage           | Primary evidence                                                                |
| ------------------------ | ------------------------------------------------------------------------------- |
| RFM feature construction | `data/processed/customer_rfm.csv`                                               |
| Baseline clustering      | `results/experiments/clustering_baseline.csv`                                   |
| Stability experiments    | `results/experiments/stability_runs.csv`; `stability_summary.csv`               |
| Cluster descriptions     | `results/experiments/customer_cluster_profiles.csv`                             |
| Sensitivity study        | `results/experiments/model_validation_results.csv`; `model_validation_best.csv` |
| K=2 investigation        | `results/experiments/k2_cluster_diagnostics.csv`                                |
| Research manuscript      | `research/research_manuscript.md`                                               |

### A.3 Basic verification commands

From the repository root, in an activated Python virtual environment:

```bash
python -m pytest -v
python scripts/research_evidence_summary.py
python scripts/investigate_cluster_balance.py
python -m streamlit run app/main.py
```

If `run_consistency_checks` has been incorporated into the audit module, inspect its output with:

```bash
python -c "from pathlib import Path; from customerinsight.dashboard_audit import run_consistency_checks; print(run_consistency_checks(Path.cwd()).to_string(index=False))"
```

**Verification status:** Previous project-specific audit tests and saved research-file availability were reported as passing. The latest end-to-end test summary, cross-file reconciliation output, notebook execution in a clean environment and regenerated-results comparison were **not provided for this manuscript revision**. They should remain marked _unverified_ until run and documented.

### A.4 Pending experiment details

For full reproducibility, record the actual RFM reference date, preprocessing parameterization, random seeds, `n_init`, hierarchical linkage settings, DBSCAN parameters, noise-handling conventions, silhouette computation details and perturbation settings by examining the original code and notebooks. Do not infer them from the summary tables.

## Appendix B. Research Evidence and Traceability

This table deliberately uses the **same research-question definitions** as Section 1.2.

| Research question                      | Evaluation focus                                               | Supporting files                                                                                                               |
| -------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **RQ1** — Algorithm comparison         | Silhouette and coverage across three tested baselines          | `clustering_baseline.csv`; `notebooks/clustering_experiments.ipynb`; `docs/clustering_research.md`                             |
| **RQ2** — Stability                    | 20 repeated runs in each of three conditions; ARI distribution | `stability_runs.csv`; `stability_summary.csv`; `notebooks/stability_analysis.ipynb`; `docs/stability_research.md`              |
| **RQ3** — Sensitivity and model choice | Two preprocessing methods; K=2–10; high-scoring K=2 diagnostic | `model_validation_results.csv`; `model_validation_best.csv`; `k2_cluster_diagnostics.csv`; `docs/model_validation_research.md` |
| **RQ4** — Interpretability             | Four customer-group counts and median RFM profiles             | `customer_cluster_profiles.csv`; `src/customerinsight/explanations.py`; `docs/explainability_research.md`                      |

Relative file basenames in the table refer to the corresponding project `results/experiments/` directory unless a longer path is shown. File paths should be checked against the actual repository before release.
