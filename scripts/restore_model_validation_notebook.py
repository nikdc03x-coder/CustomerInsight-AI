
"""Restore the model validation research notebook.

The generated notebook reads saved experimental evidence.
It does not overwrite the original experiment results.
"""

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks/model_validation.ipynb"


def main():
    """Build a research notebook using Jupyter's existing library."""

    cells = []

    def markdown(content):
        """Add a research explanation."""
        cells.append(nbf.v4.new_markdown_cell(content))

    def code(content):
        """Add an executable Python cell."""
        cells.append(nbf.v4.new_code_cell(content))

    markdown("""# Model Validation and Sensitivity Analysis

## CustomerInsight AI — Phase 08

### Research question

How do preprocessing and cluster count influence
K-Means results, and why can the highest silhouette
score be misleading?

### Objectives

1. Examine the 18 saved K-Means configurations.
2. Compare two preprocessing approaches.
3. Visualize silhouette scores across K=2 to K=10.
4. Analyse assignment agreement with the baseline.
5. Investigate the high-scoring K=2 solution.
6. Document limitations and reproducibility status.
""")

    markdown("""## 1. Environment and research evidence

We use Pandas, Plotly and the existing project modules.

The analysis reads the original experiment files.
It does not generate or overwrite baseline results.
""")

    code("""from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px

ROOT = Path.cwd().resolve()

if ROOT.name == "notebooks":
    ROOT = ROOT.parent

if not (ROOT / "src/customerinsight").is_dir():
    raise FileNotFoundError("Run from the project or notebooks directory.")

if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from customerinsight.model_validation import (
    transform_features,
    evaluate_configuration,
    run_parameter_study,
    summarize_best_configs,
)

RESULTS = ROOT / "results/experiments"
RFM_PATH = ROOT / "data/processed/customer_rfm.csv"

print("Project:", ROOT)
""")

    markdown("""## 2. Load and validate saved experiments

The model validation study compares:

- Standard scaling
- Logarithmic transformation followed by scaling

Each approach evaluates K from 2 through 10.

This gives 18 configurations in total.
""")

    code("""rfm = pd.read_csv(
    RFM_PATH,
    dtype={"customer_id": "string"},
)

validation = pd.read_csv(
    RESULTS / "model_validation_results.csv"
)

required = {
    "preprocessing",
    "clusters",
    "silhouette",
    "inertia",
    "ari_vs_baseline",
}

assert required.issubset(validation.columns)
assert len(validation) == 18
assert len(rfm) == 4338
assert validation["clusters"].between(2, 10).all()
assert not validation[list(required)].isna().any().any()

combinations = validation[
    ["preprocessing", "clusters"]
].drop_duplicates()

assert len(combinations) == 18

print("Customers:", len(rfm))
print("Configurations:", len(validation))
print("Preprocessing methods:", validation["preprocessing"].unique())

display(validation)
""")

    markdown("""## 3. Silhouette score sensitivity

Silhouette measures how separated a partition is
in its feature representation.

We compare scores across cluster counts.

**Important:** Different preprocessing methods
change distances, so silhouette scores should
not automatically be treated as directly
interchangeable evidence of practical quality.
""")

    code("""fig = px.line(
    validation,
    x="clusters",
    y="silhouette",
    color="preprocessing",
    markers=True,
    title="Silhouette score by cluster count",
    labels={
        "clusters": "Number of clusters (K)",
        "silhouette": "Silhouette score",
        "preprocessing": "Preprocessing",
    },
)

fig.update_xaxes(dtick=1)
fig.show()

best_by_method = (
    validation.sort_values(
        "silhouette",
        ascending=False,
    )
    .drop_duplicates("preprocessing")
)

display(best_by_method)
""")

    markdown("""## 4. Agreement with the baseline

Adjusted Rand Index (ARI) compares partitions.

Higher ARI indicates greater agreement with the
reference clustering partition.

ARI does not measure customer satisfaction,
predictive accuracy or business usefulness.
""")

    code("""fig = px.line(
    validation,
    x="clusters",
    y="ari_vs_baseline",
    color="preprocessing",
    markers=True,
    title="ARI against the baseline partition",
    labels={
        "clusters": "Number of clusters (K)",
        "ari_vs_baseline": "Adjusted Rand Index",
    },
)

fig.update_xaxes(dtick=1)
fig.show()

reference = validation.loc[
    (validation["preprocessing"] == "Log + standard scaling")
    & (validation["clusters"] == 4)
]

display(reference)
""")

    markdown("""## 5. Inertia and preprocessing

Inertia measures within-cluster squared distances.

It typically falls as K increases.

Do not compare inertia values directly across
different feature transformations as though
they shared an identical distance representation.
""")

    code("""fig = px.line(
    validation,
    x="clusters",
    y="inertia",
    color="preprocessing",
    markers=True,
    title="K-Means inertia across cluster counts",
    labels={
        "clusters": "Number of clusters (K)",
        "inertia": "Inertia",
    },
)

fig.update_xaxes(dtick=1)
fig.show()
""")

    markdown("""## 6. Investigating the high-scoring K=2 result

The highest silhouette score under standard
scaling came from K=2.

A separate diagnostic experiment examined the
distribution of customers between its two groups.

These findings are read from the saved diagnostic
CSV rather than being manually reconstructed.
""")

    code("""diagnostic = pd.read_csv(
    RESULTS / "k2_cluster_diagnostics.csv"
)

required_diagnostic = {
    "cluster",
    "customers",
    "median_recency",
    "median_frequency",
    "median_monetary",
}

assert required_diagnostic.issubset(diagnostic.columns)
assert len(diagnostic) == 2
assert diagnostic["customers"].sum() == len(rfm)

diagnostic["share_pct"] = (
    100 * diagnostic["customers"]
    / diagnostic["customers"].sum()
)

selected = validation.loc[
    (validation["preprocessing"] == "Standard scaling")
    & (validation["clusters"] == 2)
]

assert len(selected) == 1

print(
    "Standard scaling, K=2 silhouette:",
    selected.iloc[0]["silhouette"],
)

display(diagnostic)

fig = px.bar(
    diagnostic,
    x="cluster",
    y="customers",
    text="customers",
    title="Customer distribution in the K=2 solution",
    labels={"cluster": "Cluster", "customers": "Customers"},
)

fig.update_xaxes(type="category")
fig.show()
""")

    markdown("""## 7. Purchasing behaviour comparison

Cluster sizes should be considered alongside
median frequency, spending and recency.

A very high silhouette score can correspond
to an extremely imbalanced partition.

Imbalance alone does not make clustering incorrect;
suitability depends on the analytical objective.
""")

    code("""metrics = {
    "median_recency": "Median recency (days)",
    "median_frequency": "Median frequency (invoices)",
    "median_monetary": "Median positive spending (£)",
}

for metric, title in metrics.items():
    fig = px.bar(
        diagnostic,
        x="cluster",
        y=metric,
        text_auto=".2f",
        title=title,
        labels={"cluster": "Cluster", metric: title},
    )

    fig.update_xaxes(type="category")
    fig.show()
""")

    markdown("""## 8. Controlled experiment reproduction

The project provides:

- `transform_features(rfm, use_log)`
- `evaluate_configuration(features, clusters, sample_size)`
- `run_parameter_study(rfm, cluster_counts)`
- `summarize_best_configs(results)`

Before re-executing the full study, inspect the exact
implementation, random settings, return values and
file-writing side effects.

The existing notebook cells above inspect saved results.
They do not claim numerical reproduction of all
18 configurations.
""")

    code("""import inspect

print(inspect.getsource(run_parameter_study))
print(inspect.getsource(evaluate_configuration))

# The full parameter study remains disabled until
# its implementation and side effects are reviewed.
RUN_REPRODUCTION = False

if RUN_REPRODUCTION:
    fresh_results = run_parameter_study(
        rfm,
        cluster_counts=range(2, 11),
    )
    display(fresh_results)
else:
    print("Fresh parameter study execution: not yet verified.")
""")

    markdown("""## 9. Research interpretation

The saved Phase 08 results show:

- Two different preprocessing methods were tested.
- Nine cluster counts were evaluated for each method.
- Standard scaling with K=2 produced the highest
  recorded silhouette score.
- The K=2 diagnostic showed a strongly imbalanced
  customer partition.
- Log + standard scaling with K=4 matched the baseline
  partition under the saved ARI comparison.

This illustrates why model evaluation should consider
internal metrics, group sizes, interpretability,
stability and the research objective together.

## 10. Limitations and next steps

- There are no verified ground-truth customer labels.
- The silhouette score does not prove business usefulness.
- ARI evaluates agreement, not correctness.
- Different preprocessing methods change feature distances.
- The saved parameter study has not yet been freshly reproduced.
- Results concern one historical retail dataset.

### Reproducibility status

**Saved evidence inspected; full parameter-study
reproduction remains pending.**
""")

    notebook = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            }
        },
    )

    nbf.validate(notebook)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, OUTPUT)

    print("Notebook restored:", OUTPUT)
    print("Markdown cells:", sum(c.cell_type == "markdown" for c in cells))
    print("Code cells:", sum(c.cell_type == "code" for c in cells))
    print("Original experiment CSVs were not changed.")


if __name__ == "__main__":
    main()
