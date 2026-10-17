
"""Reproduce Phase 04 clustering without changing baseline results."""

from pathlib import Path

import numpy as np
import pandas as pd

from customerinsight.clustering import (
    prepare_clustering_features,
    run_clustering_experiments,
)


ROOT = Path(__file__).resolve().parents[1]

RFM_PATH = ROOT / "data/processed/customer_rfm.csv"
BASELINE_PATH = ROOT / "results/experiments/clustering_baseline.csv"

OUTPUT_DIR = ROOT / "results/reproducibility"
OUTPUT_PATH = OUTPUT_DIR / "clustering_comparison.csv"

# Numerical results may differ slightly across software versions.
SCORE_TOLERANCE = 0.0001


def compare_results(baseline, reproduced):
    """Compare the original and newly calculated experiment results."""

    required = {
        "algorithm",
        "clusters",
        "silhouette",
        "coverage",
    }

    for name, data in [
        ("Baseline", baseline),
        ("Reproduced", reproduced),
    ]:
        missing = required - set(data.columns)

        if missing:
            raise ValueError(
                f"{name} results are missing: {sorted(missing)}"
            )

        if data["algorithm"].duplicated().any():
            raise ValueError(
                f"{name} results contain duplicate algorithm names."
            )

    merged = baseline.merge(
        reproduced,
        on="algorithm",
        how="outer",
        suffixes=("_original", "_reproduced"),
        indicator=True,
    )

    # Check every algorithm using its name, not its row position.
    merged["clusters_match"] = (
        merged["clusters_original"]
        == merged["clusters_reproduced"]
    )

    merged["coverage_match"] = np.isclose(
        merged["coverage_original"],
        merged["coverage_reproduced"],
        atol=0.0001,
        rtol=0,
    )

    merged["silhouette_difference"] = (
        merged["silhouette_original"]
        - merged["silhouette_reproduced"]
    ).abs()

    merged["silhouette_match"] = np.isclose(
        merged["silhouette_original"],
        merged["silhouette_reproduced"],
        atol=SCORE_TOLERANCE,
        rtol=0,
        equal_nan=True,
    )

    merged["reproduced_successfully"] = (
        merged["_merge"].eq("both")
        & merged["clusters_match"]
        & merged["coverage_match"]
        & merged["silhouette_match"]
    )

    return merged


def main():
    """Run the existing algorithms and check their reproducibility."""

    print("\nCUSTOMERINSIGHT AI — CLUSTERING REPRODUCTION")
    print("=" * 65)

    if not RFM_PATH.is_file():
        raise FileNotFoundError(RFM_PATH)

    if not BASELINE_PATH.is_file():
        raise FileNotFoundError(BASELINE_PATH)

    # Load the exact processed RFM data used in our research.
    rfm = pd.read_csv(RFM_PATH)

    print(f"\nCustomers loaded: {len(rfm):,}")

    # Reuse the same preprocessing as the original project.
    features = prepare_clustering_features(rfm)

    print(f"Prepared feature shape: {features.shape}")

    # Fit the three original clustering algorithms again.
    # This function does not write to our research files.
    reproduced, labels_by_model = run_clustering_experiments(
        features
    )

    baseline = pd.read_csv(BASELINE_PATH)

    # Compare the freshly calculated values with the saved baseline.
    comparison = compare_results(
        baseline,
        reproduced,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save a separate verification report.
    # Do not overwrite clustering_baseline.csv.
    comparison.to_csv(OUTPUT_PATH, index=False)

    print("\nOriginal results:")
    print(baseline.to_string(index=False))

    print("\nReproduced results:")
    print(reproduced.to_string(index=False))

    print("\nReproducibility checks:")
    print(
        comparison[
            [
                "algorithm",
                "clusters_match",
                "coverage_match",
                "silhouette_difference",
                "silhouette_match",
                "reproduced_successfully",
            ]
        ].to_string(index=False)
    )

    passed = bool(
        comparison["reproduced_successfully"].all()
    )

    print(f"\nVerification report: {OUTPUT_PATH}")

    if passed:
        print("\nRESULT: All three baseline configurations reproduced.")
    else:
        print(
            "\nRESULT: One or more configurations did not match. "
            "Review differences before drawing conclusions."
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
