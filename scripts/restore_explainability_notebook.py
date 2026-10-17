
"""Create the customer explainability research notebook."""

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks/customer_explainability.ipynb"


def main():
    """Generate a documented notebook without executing experiments."""

    cells = []

    def note(content):
        cells.append(nbf.v4.new_markdown_cell(content))

    def code(content):
        cells.append(nbf.v4.new_code_cell(content))

    note("""# Customer Explainability — CustomerInsight AI

## Research objective

Investigate how the four baseline K-Means customer groups differ
in their original Recency, Frequency and Monetary (RFM) values.

**Research question (RQ4):** How can the resulting customer groups
be described using transparent purchasing statistics?

This notebook reconstructs the customer profiles and compares
them with the saved Phase 06 research evidence.
""")

    note("""## 1. Environment and research files

We reuse the existing clustering implementation.

No algorithms are reimplemented from scratch.
The notebook does not overwrite the original experimental CSVs.
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
    raise FileNotFoundError("Run this notebook from the project or notebooks folder.")

if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from customerinsight.clustering import (
    prepare_clustering_features,
    run_clustering_experiments,
)

RFM_FILE = ROOT / "data/processed/customer_rfm.csv"
PROFILES_FILE = ROOT / "results/experiments/customer_cluster_profiles.csv"

print("Project directory:", ROOT)
""")

    note("""## 2. Load saved customer data and profiles

The RFM table represents historical positive purchasing activity.

- **Recency:** Days since the last qualifying purchase
- **Frequency:** Number of distinct qualifying invoices
- **Monetary:** Total positive qualifying purchase value

The saved profile table is our reference evidence.
""")

    code("""rfm = pd.read_csv(RFM_FILE, dtype={"customer_id": "string"})
saved_profiles = pd.read_csv(PROFILES_FILE)

required_rfm = {"customer_id", "recency", "frequency", "monetary"}
required_profiles = {
    "cluster", "customers", "median_recency",
    "median_frequency", "median_monetary"
}

assert required_rfm.issubset(rfm.columns)
assert required_profiles.issubset(saved_profiles.columns)
assert rfm["customer_id"].is_unique
assert not rfm.empty

print("Customers:", len(rfm))
print("Saved groups:", len(saved_profiles))

display(rfm.head())
display(saved_profiles)
""")

    note("""## 3. Recreate the baseline cluster assignments

Use the same `log1p` preprocessing and baseline clustering
function used in Phase 04.

K-Means is configured in the existing project module with
four clusters, `random_state=42` and `n_init=10`.

Group numbers are arbitrary identifiers, not rankings.
""")

    code("""features = prepare_clustering_features(rfm)
reproduced_results, labels_by_model = run_clustering_experiments(features)

labels = np.asarray(labels_by_model["K-Means"])

assert len(labels) == len(rfm)
assert len(set(labels)) == 4

customers = rfm.copy()
customers["cluster"] = labels

display(reproduced_results)
display(customers["cluster"].value_counts().sort_index())
""")

    note("""## 4. Reconstruct group characteristics

Pandas aggregation is used to calculate the actual
number of customers and median RFM statistics.

We compare these with the saved research table to check
whether the group profiles can be reproduced.
""")

    code("""recreated = (
    customers.groupby("cluster")
    .agg(
        customers=("customer_id", "size"),
        median_recency=("recency", "median"),
        median_frequency=("frequency", "median"),
        median_monetary=("monetary", "median"),
    )
    .reset_index()
)

recreated["customer_share_pct"] = (
    100 * recreated["customers"] / len(customers)
)

display(recreated)
""")

    code("""comparison = recreated.merge(
    saved_profiles[
        [
            "cluster",
            "customers",
            "median_recency",
            "median_frequency",
            "median_monetary",
        ]
    ],
    on="cluster",
    how="outer",
    suffixes=("_new", "_saved"),
    indicator=True,
)

measurements = [
    "customers",
    "median_recency",
    "median_frequency",
    "median_monetary",
]

comparison["profiles_match"] = comparison["_merge"].eq("both")

for measurement in measurements:
    new = comparison[f"{measurement}_new"]
    saved = comparison[f"{measurement}_saved"]

    comparison["profiles_match"] &= np.isclose(
        new, saved, atol=0.01, rtol=0, equal_nan=False
    )

display(comparison)

if comparison["profiles_match"].all():
    print("All four group profiles reproduced within tolerance.")
else:
    print(
        "Profile mismatch detected. Review cluster assignments, "
        "preprocessing and original profile-generation methods."
    )
""")

    note("""## 5. Group distribution

Customer group sizes help identify whether the segmentation
represents several substantial groups or a highly imbalanced partition.

These four groups belong to the baseline solution;
they must not be confused with the separate K=2 diagnostic.
""")

    code("""fig = px.bar(
    recreated,
    x="cluster",
    y="customers",
    text="customers",
    title="Number of customers in each baseline group",
    labels={"cluster": "Cluster", "customers": "Customers"},
)

fig.update_xaxes(type="category")
fig.show()
""")

    note("""## 6. Compare median purchasing behaviour

The figures below use original RFM measurements,
not standardized feature values.

Lower recency means a more recent recorded purchase.
Frequency and spending reflect observed transaction history.
""")

    code("""metrics = {
    "median_recency": "Median recency (days)",
    "median_frequency": "Median purchase frequency",
    "median_monetary": "Median positive spending (£)",
}

for column, label in metrics.items():
    fig = px.bar(
        recreated,
        x="cluster",
        y=column,
        text_auto=".2f",
        title=label,
        labels={"cluster": "Cluster", column: label},
    )
    fig.update_xaxes(type="category")
    fig.show()
""")

    note("""## 7. Using our existing explainability module

The project also contains:

- `assign_customer_clusters`
- `describe_clusters`
- `compare_with_population`
- `generate_cluster_descriptions`

Their exact implementations should be inspected before
executing them here. This ensures we respect their expected
inputs and do not assume an undocumented return structure.
""")

    code("""import inspect
from customerinsight import explanations

for name in [
    "assign_customer_clusters",
    "describe_clusters",
    "compare_with_population",
    "generate_cluster_descriptions",
]:
    function = getattr(explanations, name)
    print(f"{name}{inspect.signature(function)}")
""")

    note("""## 8. Interpretation

Using the saved baseline profiles:

- Cluster 0: relatively recent, lower-frequency purchasers.
- Cluster 1: less-recent, low-frequency purchasers.
- Cluster 2: recent, high-frequency and higher-spending purchasers.
- Cluster 3: customers with intermediate purchasing characteristics.

These statements describe group-level medians. They do not
establish loyalty, customer satisfaction, churn probability or
individual future behaviour.

Interpretation should be reviewed again if the reconstructed
profiles do not match the original saved evidence.
""")

    note("""## 9. Limitations

1. RFM summarizes a limited set of purchasing behaviours.
2. Group medians can hide substantial within-group variation.
3. Group labels are descriptive, not verified customer categories.
4. Monetary values represent qualifying positive spending,
   not fully reconciled net profit.
5. Agreement with saved profiles does not establish business value.
6. This notebook uses the processed RFM data, not the original
   transaction workbook.

## 10. Reproducibility conclusion

Record the actual comparison outcome after executing the notebook.

A matching profile table supports reproducibility of the
baseline group summaries in the current environment.
It does not establish end-to-end data preparation reproducibility.
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

    print("Notebook created:", OUTPUT)
    print("Code cells:", sum(c.cell_type == "code" for c in cells))
    print("Markdown cells:", sum(c.cell_type == "markdown" for c in cells))
    print("Original result files were not modified.")


if __name__ == "__main__":
    main()
