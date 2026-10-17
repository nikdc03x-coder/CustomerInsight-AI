
"""Summarize verified numerical results for the research manuscript."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "experiments"

FILES = {
    "Baseline clustering": (
        "clustering_baseline.csv",
        ["algorithm", "clusters", "silhouette", "coverage"],
    ),
    "Stability summary": (
        "stability_summary.csv",
        ["experiment", "mean", "std", "min", "max"],
    ),
    "Model validation": (
        "model_validation_best.csv",
        ["preprocessing", "clusters", "silhouette"],
    ),
    "Customer group profiles": (
        "customer_cluster_profiles.csv",
        [
            "cluster",
            "customers",
            "median_recency",
            "median_frequency",
            "median_monetary",
        ],
    ),
}


def main():
    """Print available research evidence and flag missing results."""

    for title, (filename, required) in FILES.items():
        path = RESULTS / filename

        print(f"\n{'=' * 60}")
        print(title)
        print("=" * 60)

        if not path.is_file():
            print(f"PENDING: {filename} not found")
            continue

        data = pd.read_csv(path)
        missing = set(required) - set(data.columns)

        if missing:
            print(f"INVALID: Missing columns {sorted(missing)}")
            continue

        if data.empty:
            print("INVALID: The result file contains no records.")
            continue

        print(data.to_string(index=False))

    print("\nResearch summary inspection complete.")


if __name__ == "__main__":
    main()
