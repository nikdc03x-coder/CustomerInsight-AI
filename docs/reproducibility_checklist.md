# CustomerInsight AI — Reproducibility Checklist

## Objective

Verify that the customer segmentation research can be
repeated and its numerical findings independently checked.

## 1. Research Data

- [ ] Original UCI Online Retail dataset is available.
- [ ] Data source and access information are documented.
- [ ] RFM construction rules are documented.
- [ ] Customer exclusions are explained.

## 2. Clustering Experiments

- [ ] K-Means configuration is recorded.
- [ ] Agglomerative clustering settings are recorded.
- [ ] DBSCAN configuration is recorded.
- [ ] Random seeds are documented where applicable.
- [ ] Clustering comparison outputs can be regenerated.

## 3. Stability Experiments

- [ ] All 60 saved runs are available.
- [ ] Stability summary agrees with individual runs.
- [ ] Perturbation methods are documented.
- [ ] ARI interpretation and limitations are explained.

## 4. Model Validation

- [ ] All 18 configurations are documented.
- [ ] Preprocessing methods are described.
- [ ] Silhouette comparisons are reproducible.
- [ ] K=2 cluster imbalance diagnostic is recorded.
- [ ] Baseline comparison method is documented.

## 5. Software Environment

- [ ] Python version is recorded.
- [ ] Library versions are recorded.
- [ ] Project dependencies can be installed.
- [ ] Notebooks execute from a clean kernel.

## 6. Dashboard and Tests

- [ ] Complete pytest suite passes.
- [ ] Customer segmentation dashboard loads.
- [ ] Model Validation Studio loads.
- [ ] Research Quality Center loads.
- [ ] No duplicate Streamlit widget keys occur.

## Final Research Status

Reproducibility review: IN PROGRESS.

Only mark a check as complete after personally
verifying the corresponding evidence.
