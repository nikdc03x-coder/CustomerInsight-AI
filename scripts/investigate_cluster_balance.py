
"""Investigate the customer groups produced by the K=2 configuration."""

from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans

from customerinsight.model_validation import transform_features


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data/processed/customer_rfm.csv"
OUTPUT_FILE = ROOT / "results/experiments/k2_cluster_diagnostics.csv"


def main():
    """Compare the sizes and typical behaviour of two customer groups."""

    rfm = pd.read_csv(
        DATA_FILE,
        dtype={"customer_id": "string"},
    )

    # Reproduce the Phase 08 standard-scaled, two-cluster model.
    features = transform_features(rfm, use_log=False)

    model = KMeans(
        n_clusters=2,
        random_state=42,
        n_init=10,
    )

    clustered = rfm.copy()
    clustered["cluster"] = model.fit_predict(features)

    profiles = (
        clustered.groupby("cluster")
        .agg(
            customers=("cluster", "size"),
            median_recency=("recency", "median"),
            median_frequency=("frequency", "median"),
            median_monetary=("monetary", "median"),
            maximum_monetary=("monetary", "max"),
        )
        .reset_index()
    )

    profiles["customer_share_pct"] = (
        profiles["customers"] / len(clustered) * 100
    ).round(2)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    profiles.to_csv(OUTPUT_FILE, index=False)

    print("\nK=2 customer group diagnostics:")
    print(profiles.to_string(index=False))

    smallest_share = profiles["customer_share_pct"].min()

    print(f"\nSmallest cluster share: {smallest_share:.2f}%")

    if smallest_share < 5:
        print(
            "Observation: One cluster contains fewer than 5% "
            "of customers. Investigate potential outlier separation."
        )
    else:
        print(
            "Observation: Both clusters contain at least 5% "
            "of customers. Further interpretation is still needed."
        )

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
