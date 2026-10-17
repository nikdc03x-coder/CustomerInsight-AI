
"""Display the real results needed for our scientific manuscript."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/experiments"

FILES = {
    "Customer profiles": "customer_cluster_profiles.csv",
    "Clustering comparison": "clustering_baseline.csv",
    "Stability summary": "stability_summary.csv",
    "Model validation": "model_validation_results.csv",
    "Best model configurations": "model_validation_best.csv",
}


def main():
    """Print research results while identifying missing evidence."""

    for title, filename in FILES.items():
        path = RESULTS / filename

        print("\n" + "=" * 65)
        print(title)
        print("=" * 65)

        if not path.exists():
            print(f"PENDING: {filename} is missing.")
            continue

        data = pd.read_csv(path)

        if data.empty:
            print("WARNING: No results found.")
            continue

        print(data.to_string(index=False))

    print("\nResearch evidence summary completed.")


if __name__ == "__main__":
    main()
