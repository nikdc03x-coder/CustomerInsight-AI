# CustomerInsight AI — Research Quality Review

## Objective

Verify the availability and basic structural
quality of all research outputs.

## Method

We developed an automated research audit using
Python, Pandas and NumPy.

The audit checks:

- Expected research files
- Required CSV columns
- Numeric values
- Selected mathematical ranges
- Customer ID uniqueness
- Selected data-quality constraints

## Actual Findings — 17 October 2026

| Component                | Status |        Rows |
| ------------------------ | ------ | ----------: |
| Original retail workbook | Ready  | Not counted |
| Customer RFM             | Ready  |       4,338 |
| Clustering comparison    | Ready  |           3 |
| Stability runs           | Ready  |          60 |
| Stability summary        | Ready  |           3 |
| Cluster profiles         | Ready  |           4 |
| Model validation         | Ready  |          18 |

### Summary

- Components inspected: 7
- Components passing basic checks: 7
- Missing outputs: 0
- Invalid outputs: 0
- Research audit tests passed: 4

## Interpretation

All expected research outputs were available.

The CSV files passed the implemented structural
and numerical checks.

The original retail workbook was confirmed to
exist, but its internal data was not checked
by this audit.

These findings support the availability of
the expected research outputs.

They do not prove that the experimental
methodology or interpretations are correct.

## Remaining Verification

- Complete automated test suite
- Manual Streamlit dashboard review
- Research notebook reproducibility
- Scientific manuscript review
- Dependency and environment verification

## Next Steps

Complete the scientific research report and
prepare the final project portfolio.

## Research Health 2.0 — Cross-File Evidence Verification

### Research objective

Determine whether independently saved research
results agree with one another and whether the
project's findings can be traced back to
supporting evidence.

### New validation methods

We introduced four consistency checks:

1. Customer coverage reconciliation
2. Stability statistics recalculation
3. Stability run identifier verification
4. Model validation configuration uniqueness

### Research evidence map

We created an evidence map connecting
research questions to:

- Research methodology
- Python implementation
- Automated tests
- Experimental notebooks
- Saved numerical results
- Research documentation
- Methodological limitations

### Actual consistency results

Complete after running run_consistency_checks().

Customer coverage:

Stability statistics:

Stability run identifiers:

Validation configurations:

### Interpretation

Explain the results of each check.

A passed reconciliation supports internal
consistency of saved outputs.

It does not prove the correctness of the
underlying machine-learning methodology.

### Limitations

The system performs selected automated checks.

It does not verify notebook execution,
scientific novelty, statistical significance,
causal explanations or external generalization.

Manual reproducibility reviews remain necessary.

### Next steps

Complete end-to-end reproducibility checks,
consolidate the scientific manuscript and
prepare the research portfolio release.
