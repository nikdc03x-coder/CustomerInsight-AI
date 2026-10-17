
"""Verify that four customer profiles match saved research evidence."""

from pathlib import Path

import numpy as np
import pandas as pd

from customerinsight.clustering import (
    prepare_clustering_features,
    run_clustering_experiments,
)


ROOT = Path(__file__).resolve().parents[1]

RFM_FILE = ROOT / "data/processed/customer_rfm.csv"

SAVED_PROFILES = (
    ROOT / "results/experiments/customer_cluster_profiles.csv"
)

REPORT_FILE = (
    ROOT / "results/reproducibility/customer_profile_comparison.csv"
)

MEASUREMENTS = [
    "customers",
    "median_recency",
    "median_frequency",
    "median_monetary",
]


def main():
    """Recreate group profiles without modifying the original results."""

    rfm = pd.read_csv(
        RFM_FILE,
        dtype={"customer_id": "string"},
    )

    original = pd.read_csv(SAVED_PROFILES)

    # Refit the exact baseline clustering algorithm.
    features = prepare_clustering_features(rfm)

    _, labels_by_model = run_clustering_experiments(features)

    customers = rfm.copy()
    customers["cluster"] = labels_by_model["K-Means"]

    # Rebuild customer profiles using original RFM measurements.
    reproduced = (
        customers.groupby("cluster")
        .agg(
            customers=("customer_id", "size"),
            median_recency=("recency", "median"),
            median_frequency=("frequency", "median"),
            median_monetary=("monetary", "median"),
        )
        .reset_index()
    )

    # Match groups by their saved cluster identifier.
    comparison = original[
        ["cluster", *MEASUREMENTS]
    ].merge(
        reproduced,
        on="cluster",
        how="outer",
        suffixes=("_original", "_reproduced"),
        indicator=True,
        validate="one_to_one",
    )

    comparison["matches"] = comparison["_merge"].eq("both")

    for metric in MEASUREMENTS:
        comparison[f"{metric}_difference"] = (
            comparison[f"{metric}_original"]
            - comparison[f"{metric}_reproduced"]
        ).abs()

        comparison["matches"] &= np.isclose(
            comparison[f"{metric}_original"],
            comparison[f"{metric}_reproduced"],
            rtol=0,
            atol=0.01 if metric != "customers" else 0,
            equal_nan=False,
        )

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(REPORT_FILE, index=False)

    print("\nCUSTOMER PROFILE REPRODUCTION")
    print("=" * 65)

    print(
        comparison[
            [
                "cluster",
                "customers_original",
                "customers_reproduced",
                "median_monetary_difference",
                "matches",
            ]
        ].to_string(index=False)
    )

    passed = (
        len(comparison) == 4
        and comparison["matches"].all()
    )

    print(f"\nProfiles matched: {int(comparison['matches'].sum())}/4")
    print("Saved report:", REPORT_FILE)

    if not passed:
        raise SystemExit(
            "Profile comparison failed. "
            "Investigate differences before completing Phase 09."
        )

    print("\nRESULT: All four customer profiles reproduced.")


if __name__ == "__main__":
    main()
