# Reproducibility status

Updated 17 October 2026 during the project cleanup. This record supersedes the
earlier appended restoration/pending notes. Phase documents retain historical
observations; a historical checklist is not a fresh execution record.

## Verified evidence and its scope

| Check | Result | Boundary |
| --- | --- | --- |
| Existing automated suite | 49 passed before cleanup | Current environment; synthetic unit tests plus available local-result checks |
| Cleanup test suite | 51 passed | Adds isolated Streamlit diagnostic interaction and missing-results regressions |
| Feature-engineering notebook | Fresh clean-kernel execution passed | All 4,338 regenerated RFM rows matched saved data within 1e-8; writes stayed in scratch storage |
| Package wheel | Built successfully | Isolated build dependency installation; no fresh installation of all runtime/development extras |
| Dashboard pages and navigation | Seven pages rendered without application exceptions; all seven registered | Streamlit AppTest; separate page checks, with the real 541,909-row workbook preloaded for Retail Data Explorer |
| Original baseline comparison | 3/3 freshly matched | Starts from saved RFM, not raw workbook |
| Parameter study | 18/18 freshly matched within 0.0001 | Maximum inertia difference about 1.82e-12; other differences at floating-point precision |
| Customer profiles | 4/4 freshly matched | Counts and median RFM compared; counts exact, medians within 0.01 |
| Research input audit | 7/7 ready | Raw workbook checked for existence; selected CSV structure/numeric checks |
| Cross-file consistency | 4/4 passed | Population totals, stability summary, run IDs and validation configuration uniqueness |
| Stored explainability notebook | 8/8 executed, no recorded errors | Inspected existing saved artifact; not a fresh execution in this cleanup |
| Stored validation notebook | 8/8 executed, no recorded errors | Its reproduction toggle is disabled; execution alone does not rerun the parameter study |

Fresh comparison reports were generated separately in the chat workspace during
cleanup. The original `results/experiments/` and historical
`results/reproducibility/` files were preserved.

The cold Excel read exceeded the first 90-second AppTest timeout. A separate
preload completed, and page rendering then passed. AppTest also lost custom
registrations after switching into its legacy `pages/` handling, so the remaining
pages were checked directly and the initial navigation registry was checked
separately. This is not a full browser visual/navigation review. The source-record
preview triggered Streamlit's automatic Arrow type coercion for mixed invoice
identifiers; no application exception was recorded. Slow cold loading and
consistent source identifier types remain useful follow-up improvements.

## Data and configuration

- Raw input: `data/raw/Online Retail.xlsx`.
- Processed input: `data/processed/customer_rfm.csv`, 4,338 rows.
- Baseline: log1p plus StandardScaler; K-Means K=4/seed 42/n_init=10,
  Agglomerative K=4, DBSCAN eps=0.5/min_samples=10.
- Baseline silhouette: at most 2,000 observations, seed 42; exclude DBSCAN noise
  and report its coverage.
- Stability: 20 runs for each of random initialization, 80% training subsets
  and Gaussian noise with scale 0.05 in standardized space. See
  `src/customerinsight/stability.py` for seeds and evaluation populations.
- Sensitivity: standard scaling or log1p plus scaling, K=2–10, K-Means seed
  42/n_init=10; silhouette sample at most 1,500, seed 42.
- RFM includes qualifying positive spending and does not fully reconcile refunds.

## Commands and file effects

Run from the repository root in the installed environment.

| Command | Reads | Writes |
| --- | --- | --- |
| `python scripts/build_customer_features.py` | Raw workbook | Processed RFM; replaces an existing local file |
| `python scripts/reproduce_clustering.py` | RFM and original clustering baseline | Separate clustering comparison report |
| `python scripts/reproduce_model_validation.py` | RFM and original parameter-study results | Separate model-validation comparison report |
| `python scripts/verify_customer_profiles.py` | RFM and original profiles | Separate customer-profile comparison report |
| `python scripts/verify_research_reproduction.py` | Saved validation comparison and two executed notebook artifacts | Console only; does not refit models |
| `python scripts/research_evidence_summary.py` | Original experiment CSVs | Console only |
| `python scripts/audit_notebook_reproducibility.py` | Six source notebooks | Structural notebook audit CSV |
| `python scripts/research_environment.py` | Installed-package metadata | Environment Markdown record |

The comparison reports are written under `results/reproducibility/` by the
normal project commands. Take copies if preserving an earlier verification run.
Notebook source is maintained directly; one-time notebook generators were
removed after their outputs became the maintained research artifacts.

## Remaining verification

- A completely fresh environment installation remains unverified.
- The entire six-notebook workflow has not been rerun in this cleanup.
- A fresh clone lacks ignored raw/processed/original-result files. Several
  notebooks inspect saved evidence rather than creating all required tables.
- A single raw-workbook-to-all-results command does not yet exist.
- External datasets, temporal generalization and business impact are unverified.
- Literature references still need reconciliation with checked primary sources.

See `project_review.md` for the full analysis and cleanup scope.
