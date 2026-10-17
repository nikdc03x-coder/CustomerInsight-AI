
"""Display the real results needed for our scientific manuscript."""

from pathlib import Path

import pandas as pd

from customerinsight.dashboard_audit import inspect_csv


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/experiments"

FILES = {
    "Customer profiles": (
        "customer_cluster_profiles.csv",
        ["cluster", "customers", "median_recency", "median_frequency", "median_monetary"],
    ),
    "Clustering comparison": (
        "clustering_baseline.csv", ["algorithm", "clusters", "silhouette", "coverage"],
    ),
    "Stability summary": (
        "stability_summary.csv", ["experiment", "mean", "std", "min", "max"],
    ),
    "Model validation": (
        "model_validation_results.csv",
        ["preprocessing", "clusters", "silhouette", "inertia", "ari_vs_baseline"],
    ),
    "Best model configurations": (
        "model_validation_best.csv", ["preprocessing", "clusters", "silhouette"],
    ),
}


def main():
    """Print research results while identifying missing evidence."""

    for title, (filename, required) in FILES.items():
        path = RESULTS / filename

        print("\n" + "=" * 65)
        print(title)
        print("=" * 65)

        status, _, details = inspect_csv(path, required)
        if status != "Ready":
            print(f"{status.upper()}: {filename}: {details}")
            continue

        data = pd.read_csv(path)
        print(data.to_string(index=False))

    print("\nResearch evidence summary completed.")


if __name__ == "__main__":
    main()
