# Project analysis and cleanup

Reviewed on 17 October 2026. Cleanup branch: `codex/project-cleanup`, based on
`7aa6543` from `phase-09-research-report`.

## What this project is about

CustomerInsight AI is an exploratory data-science research application. Its main
question is how to discover customer purchasing groups that are separated,
stable under controlled changes, and understandable in original purchasing
units. It uses one historical retail workbook, established scikit-learn models,
and a Streamlit interface for examining evidence.

The useful contribution is the combination of algorithm comparison, stability
experiments, parameter sensitivity, descriptive explanations and evidence
traceability. The code does not implement a novel clustering algorithm, a live
customer database, forecasting, recommendations or demonstrated commercial impact.

## Architecture and data flow

`Online Retail.xlsx` → `retail.py` → `features.py` → `customer_rfm.csv` →
clustering/stability/sensitivity functions → saved CSV evidence → dashboard.

| Component | Responsibility |
| --- | --- |
| `data.py` | Validate the small normalized CSV fixture; separate from the UCI workbook loader |
| `retail.py` | Normalize workbook columns, identify cancellation invoices and select valid positive sales |
| `features.py` | Require usable customer/invoice IDs and aggregate recency, invoice frequency and positive spending |
| `clustering.py` | Log-transform and standardize RFM; compare K-Means, Agglomerative and DBSCAN |
| `stability.py` | Compare K-Means assignments under random seeds, training subsets and feature noise |
| `model_validation.py` | Compare two transformations and K=2–10 using silhouette, inertia and baseline ARI |
| `explanations.py` | Assign baseline clusters and describe original-unit profiles relative to population medians |
| `dashboard_audit.py` | Inspect CSV structure/numeric ranges and reconcile selected evidence across files |
| `research_evidence.py` | Connect the manuscript's four research questions to implementations and evidence |

`app/main.py` exposes seven pages: Research Overview, Retail Data Explorer, RFM
Intelligence, Customer Behaviour Explorer, Model Comparison & Stability, Model
Validation Studio and Research Quality Center. `app/k2_diagnostics.py` is a used
component of Model Validation Studio, so it is retained.

Notebooks contain the experimental narrative and some file-writing steps.
Scripts provide data preparation, evidence inspection and separate numerical
comparison reports. Tests exercise synthetic inputs; three existing result tests
also inspect local experiment files when available and skip when absent.

## Method and findings

The saved processed dataset contains 4,338 customers. Qualifying sales have
positive quantity/price, a valid invoice date/country, and usable customer/invoice
identifiers. Duplicates are reported rather than automatically removed. Monetary
values are positive spending before refund reconciliation. Recency uses the day
after the latest qualifying purchase by default, rather than today's date.

The baseline applies `log1p` and `StandardScaler`. K-Means uses K=4, seed 42 and
10 initializations; Agglomerative uses K=4; DBSCAN uses eps=0.5 and min_samples=10.
Silhouette samples up to 2,000 observations with seed 42; DBSCAN excludes noise
and reports coverage separately. The saved scores are approximately 0.3324,
0.2706 and 0.2898 respectively, with DBSCAN coverage 98.18%.

Stability uses 20 runs per condition: seeds 0–19; 80% training subsets selected
with seeds 1000–1019 and evaluated on all customers; Gaussian noise with standard
deviation 0.05 in standardized feature space and seeds 2000–2019. ARI compares
each partition with the seed-42 reference. These are perturbation tests rather
than temporal or external validation.

The sensitivity study tests 18 configurations, using up to 1,500 observations for
silhouette. Standard-scaled K=2 scores about 0.8918 but separates 4,312 customers
from 26. This motivates inspecting composition and purpose alongside scores.
The four-group baseline profiles contain 877, 1,579, 720 and 1,162 customers.
Group numbers are identifiers and their medians cannot establish individual
motivation or future behaviour.

## Cleanup decisions

- Removed four one-time notebook creation/restoration scripts. The six notebooks
  already exist and should be edited directly. The EDA generator used an outdated
  filename; restoration scripts could replace newer notebook work with templates.
- Removed duplicate `summarize_research.py`. Kept the referenced
  `research_evidence_summary.py`, preserving both scripts' useful tables and
  reusing the existing CSV validator.
- Removed two extra top-level K=2 render calls from Model Validation Studio. The
  diagnostic remains once in its dedicated tab, with the same interaction.
- Replaced optional-page filtering with explicit navigation for the seven
  implemented pages and added an application-wide default page configuration.
- Removed unused chart imports/constants and replaced three deprecated chart
  width arguments with the supported `width="stretch"` form.
- Declared direct NumPy use, added a dashboard dependency extra, and declared
  notebook execution/plotting dependencies in the development extra.
- Added the missing `rfm = build_rfm(transactions)` step to the feature notebook
  and cleared its stale execution outputs, which included a saved NameError.
- Aligned the dashboard evidence-map IDs with manuscript RQ1–RQ4.
- Rewrote the outdated Phase-01 README and consolidated contradictory
  reproducibility notes into one current verification record. Updated stale
  manuscript reproduction statements while preserving scientific results.

The original uncommitted `clustering_experiments.ipynb` is preserved byte for
byte and excluded from the cleanup commit. Original raw data, processed RFM,
experiment CSVs and tracked historical reproduction artifacts are preserved.
Phase research logs remain useful provenance and were not deleted as clutter.
The environment and caches are ignored local tooling and were not removed.

## Validation and practical limits

The original suite passed 49 tests before cleanup. Fresh baseline reproduction
matched all three algorithms; parameter-study reproduction matched all 18
configurations within 0.0001; customer profiles matched all four groups. Maximum
observed parameter-study inertia difference was about 1.82e-12. Original evidence
was not overwritten: fresh reports were written to the chat workspace.

All seven research inputs passed the implemented availability/basic checks and
all four cross-file consistency checks passed. These checks are limited to the
implemented constraints, not independent scientific certification.

Additional cleanup checks and their final outcomes are recorded in
`reproducibility_research.md`.

The cleaned suite passed 51 tests, including diagnostic interaction and
missing-evidence UI cases. The repaired feature notebook executed from a clean
kernel against a copied original workbook; all 4,338 generated rows matched the
saved RFM table within 1e-8. An isolated package-wheel build also passed.
All seven pages rendered without application exceptions in AppTest, and all
seven navigation registrations were verified. Retail rendering used the real
541,909-row workbook preloaded after a slow cold parse. This was a page-rendering
check, not a full browser visual review. See the verification record for timeout,
AppTest navigation and source-preview type-coercion details.

## Remaining work, in priority order

1. **Complete fresh-clone reproduction.** Original experiment outputs and the
   processed dataset are ignored, while several restored notebooks expect those
   outputs. Provide a single explicit pipeline that generates all original
   tables into a new output directory and records input hashes/reference date.
2. **Verify the full environment and all six notebooks.** Dependency declarations
   are improved, but a clean network installation and complete notebook suite
   have not been verified by this cleanup. The preserved clustering notebook
   currently imports Matplotlib; it is now declared in the development extra.
3. **Improve audit depth.** Some audit paths check only existence or selected
   columns. Counts and finite/integer checks could be strengthened, particularly
   for malformed evidence and legitimate undefined silhouette values.
4. **Keep dashboard preparation consistent.** The Retail Data Explorer has its
   own original-column loading/filtering, which can diverge from the reusable
   feature pipeline. Refactor this with dedicated comparison coverage before
   changing reported numbers.
5. **Finish research presentation.** Reconcile checked primary-source citations,
   explain the single-dataset limitation and evaluate whether users understand
   the group descriptions. A live-business claim requires separate evidence.

This review inspected the maintained modules, application pages, scripts, tests,
notebook code and research documentation/evidence. It is an engineering cleanup
and methodological review, not an exhaustive security audit or publication review.
