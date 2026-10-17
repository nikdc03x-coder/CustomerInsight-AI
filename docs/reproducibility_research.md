# CustomerInsight AI — Reproducibility Research

## Objective

Assess whether the research experiments can be
independently rerun and their results verified.

## Research Question

Are the experiments sufficiently documented
and reproducible using the available project
code, datasets and software environment?

## Methodology

We perform three levels of verification:

1. Notebook availability and structural audit
2. Consistency checks across saved research outputs
3. Automated Python test execution

Notebook regeneration from a clean environment
will be evaluated separately.

## Tools Used

- Python standard library
- Pandas
- pytest
- Jupyter notebooks
- Existing research audit module

## Actual Findings

### Notebook Audit

Date:
Notebooks inspected:
Structurally valid:
Missing:
Invalid:

### Cross-File Consistency

Customer coverage:
Stability statistics:
Experiment run identifiers:
Validation configurations:

### Automated Tests

Number of tests:
Passed:
Failed:

## Interpretation

To be completed using actual verification results.

## Limitations

A structurally valid notebook is not necessarily
reproducible.

Saved notebook outputs do not establish that
the notebook can execute successfully again.

Passing unit tests alone does not establish
that research experiments can be regenerated.

## Next Steps

- Execute the notebooks in a controlled environment.
- Record errors and missing dependencies.
- Compare regenerated results against saved evidence.
- Document random seeds and sampling settings.
- Update the scientific manuscript.

## Verified Audit Findings — 17 October 2026

### Notebook Audit

- Notebooks inspected: 6
- Files available: 6
- Structurally valid notebooks: 6
- Notebooks containing executable code: 3
- Notebooks without code cells: 3
- Clean notebook executions verified: 0

The audit found no code cells in:

- clustering_experiments.ipynb
- customer_explainability.ipynb
- model_validation.ipynb

These notebooks require further development before
their experiments can be independently reproduced.

### Cross-File Consistency

All four implemented checks passed:

- Customer coverage: 4,338 / 4,338
- Stability summary: 3 / 3 experiments agree
- Stability run identifiers: 60 / 60 unique
- Model validation configurations: 18 / 18 unique

### Automated Tests

- Tests passed: 49
- Tests failed: 0
- Reported execution time: 4.75 seconds

### Interpretation

The saved research outputs passed the implemented
consistency checks, and the automated test suite passed.

However, full computational reproducibility has not
yet been demonstrated.

Three experiment notebooks do not contain executable
code cells. The remaining notebooks also require
controlled re-execution.

### Next Action

Restore executable notebook workflows using the
existing tested Python research modules.

Preserve original research outputs during verification.

## Clustering Notebook Restoration

The clustering experiments notebook was restored
using the existing project functions.

The restored notebook includes:

- Research objective and research question
- RFM data loading and inspection
- Existing clustering feature preparation
- Original saved baseline results
- A guarded experiment re-execution cell
- Research interpretation and limitations

Re-execution remains pending review of
the experimental function's side effects.

The restoration does not yet establish
numerical reproducibility.

## Phase 04 — Clustering Reproduction

### Objective

Determine whether the original clustering comparison
can be reproduced from the saved customer RFM dataset.

### Dataset

- Customer RFM dataset: 4,338 customers
- Features: Recency, Frequency and Monetary

### Methods

- Log1p transformation
- StandardScaler
- K-Means: K=4, random_state=42, n_init=10
- Agglomerative Clustering: K=4
- DBSCAN: eps=0.5, min_samples=10
- Silhouette evaluation: up to 2,000 observations
- Silhouette sampling seed: 42

### Verification Method

The original clustering experiment function was
executed again using the processed RFM dataset.

Results were compared against the original
clustering_baseline.csv.

We checked:

1. Number of clusters
2. Customer coverage
3. Silhouette score within numerical tolerance

### Actual Results

K-Means: Pending reproduction output.

Agglomerative: Pending reproduction output.

DBSCAN: Pending reproduction output.

### Interpretation

To be completed using the actual reproduction results.

### Limitations

Passing this comparison would establish agreement
for the tested configuration in the current environment.

It would not independently establish correct
customer-segment labels or reproducibility
across different operating systems and environments.

### Verified Results — 17 October 2026

- Customers processed: 4,338
- Prepared features: 3
- Clustering configurations reproduced: 3/3
- Cluster counts: All matched
- Coverage measurements: All matched
- Silhouette differences: 0.0
- Automated tests: 49 passed

### Interpretation

All three baseline clustering configurations
successfully reproduced their saved results
in the current Python environment.

This supports numerical reproducibility
of the baseline clustering experiments.

It does not establish full pipeline
reproducibility from the original raw
transactions in a new environment.
