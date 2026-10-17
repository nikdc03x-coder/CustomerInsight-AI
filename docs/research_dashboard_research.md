# Phase 07 — Research Intelligence Dashboard

## Objective

Present CustomerInsight AI's experimental results
through an interactive and understandable interface.

The dashboard should help non-technical users
explore model performance without requiring
knowledge of clustering algorithms.

## Implementation

The application uses Streamlit and Plotly.

Our original Customer Behaviour Explorer is retained.

A new Research Findings page presents:

- Baseline clustering comparisons
- Silhouette scores
- Cluster coverage
- Stability experiment results
- Adjusted Rand Index
- Experimental methods and limitations

## Research communication

Each visualization explains:

1. What the chart measures
2. What the actual data reveals
3. How to interpret its metrics
4. What conclusions are not supported

Line charts showing algorithms are connected
categorical comparisons, not time series.

Line charts showing experiment runs represent
repeated trials, not chronological observations.

## Data provenance

Results are loaded from the experiment output files.

The dashboard does not invent or hardcode
experimental measurements.

Original experimental methodology is recorded
in the Phase 04 and Phase 05 research documents.

## Validation

Automated test results: Pending

Manual dashboard review: Pending

Verified findings: Pending

## Limitations

The dashboard communicates our existing results.
It does not independently establish model validity.

Results depend on our chosen dataset,
preprocessing and experiment configurations.

## Next steps

Improve experiment reproducibility, expand
parameter sensitivity testing and validate
the clarity of explanations for non-technical users.
