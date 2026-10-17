
"""Compare freshly reproduced model validation results with saved evidence."""

from pathlib import Path

import numpy as np
import pandas as pd

from customerinsight.model_validation import run_parameter_study


ROOT = Path(__file__).resolve().parents[1]

RFM_FILE = ROOT / "data/processed/customer_rfm.csv"
BASELINE_FILE = (
    ROOT / "results/experiments/model_validation_results.csv"
)

OUTPUT_FILE = (
    ROOT / "results/reproducibility/model_validation_comparison.csv"
)

METRICS = ["silhouette", "inertia", "ari_vs_baseline"]

# Numerical tolerance used for floating-point comparison.
ABSOLUTE_TOLERANCE = 0.0001


def validate_table(table, label):
    """Check the expected experiment schema and unique configurations."""

    required = {"preprocessing", "clusters", *METRICS}

    missing = required - set(table.columns)

    if missing:
        raise ValueError(
            f"{label} is missing columns: {sorted(missing)}"
        )

    if table.empty:
        raise ValueError(f"{label} contains no experiment results.")

    if table.duplicated(["preprocessing", "clusters"]).any():
        raise ValueError(
            f"{label} contains duplicate experiment configurations."
        )

    if table[list(METRICS) + ["clusters"]].isna().any().any():
        raise ValueError(f"{label} contains missing numeric measurements.")


def compare_results(original, reproduced):
    """Match the original and new experiments by configuration."""

    validate_table(original, "Original results")
    validate_table(reproduced, "Reproduced results")

    merged = original.merge(
        reproduced,
        on=["preprocessing", "clusters"],
        how="outer",
        suffixes=("_original", "_reproduced"),
        indicator=True,
        validate="one_to_one",
    )

    merged["configuration_match"] = merged["_merge"].eq("both")

    for metric in METRICS:
        original_column = f"{metric}_original"
        new_column = f"{metric}_reproduced"

        merged[f"{metric}_difference"] = (
            merged[original_column] - merged[new_column]
        ).abs()

        merged[f"{metric}_match"] = np.isclose(
            merged[original_column],
            merged[new_column],
            rtol=0,
            atol=ABSOLUTE_TOLERANCE,
            equal_nan=False,
        )

    merged["reproduced_successfully"] = merged[
        [
            "configuration_match",
            "silhouette_match",
            "inertia_match",
            "ari_vs_baseline_match",
        ]
    ].all(axis=1)

    return merged


def main():
    """Run the original study without modifying saved experiment files."""

    print("\nCUSTOMERINSIGHT AI — MODEL VALIDATION REPRODUCTION")
    print("=" * 70)

    if not RFM_FILE.is_file():
        raise FileNotFoundError(RFM_FILE)

    if not BASELINE_FILE.is_file():
        raise FileNotFoundError(BASELINE_FILE)

    rfm = pd.read_csv(RFM_FILE)
    original = pd.read_csv(BASELINE_FILE)

    print(f"Customers: {len(rfm):,}")
    print(f"Original configurations: {len(original)}")

    # Use the project's own parameter-study implementation.
    # Inspect this function for file-writing side effects first.
    result = run_parameter_study(
        rfm,
        cluster_counts=range(2, 11),
    )

    reproduced = (
        result.copy()
        if isinstance(result, pd.DataFrame)
        else pd.DataFrame(result)
    )

    comparison = compare_results(original, reproduced)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(OUTPUT_FILE, index=False)

    print("\nReproduction comparison:")
    print(
        comparison[
            [
                "preprocessing",
                "clusters",
                "silhouette_difference",
                "inertia_difference",
                "ari_vs_baseline_difference",
                "reproduced_successfully",
            ]
        ].to_string(index=False)
    )

    passed = int(comparison["reproduced_successfully"].sum())

    print(f"\nConfigurations reproduced: {passed}/{len(comparison)}")
    print("Comparison report:", OUTPUT_FILE)

    if passed != len(comparison) or len(comparison) != 18:
        raise SystemExit(
            "Some configurations did not reproduce. "
            "Investigate the differences before proceeding."
        )

    print("\nRESULT: All 18 configurations reproduced successfully.")


if __name__ == "__main__":
    main()
