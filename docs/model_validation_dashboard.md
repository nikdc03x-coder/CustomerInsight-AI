# Model Validation Studio

## Project

CustomerInsight AI

## Objective

Make Phase 08 model sensitivity experiments
accessible to non-technical users.

## Problem

Our research contains numerical results for
multiple cluster counts and preprocessing methods.

Raw tables make the comparisons difficult to
understand.

## Solution

We developed an interactive Streamlit page
that reads saved experimental results and
presents them through Plotly visualizations.

## Features

- Interactive line plots
- Grouped bar charts
- Scatter plots
- Heatmaps
- Preprocessing filters
- Cluster-count comparisons
- Research result downloads
- Plain-language explanations

## Research questions

1. How does cluster separation change with K?
2. How does preprocessing influence clustering?
3. How do assignments compare with the baseline?
4. What limitations affect our interpretation?

## Libraries

- Pandas
- Streamlit
- Plotly Express

## Data provenance

The dashboard reads:

results/experiments/model_validation_results.csv

It does not replace missing experimental
results with invented data.

## Limitations

Silhouette measures internal cluster structure.

ARI against the baseline measures agreement,
not objective correctness.

Inertia should not be directly compared
across differently transformed feature spaces.

The experiments do not provide independent
validation of business usefulness.

## Verification

Automated tests: Pending

Manual dashboard checks: Pending

Research results reviewed: Pending

## Next steps

Complete end-to-end dashboard testing,
improve navigation and accessibility,
and finalize the portfolio documentation.
