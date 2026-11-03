
"""Check whether research outputs are available and structurally valid."""

from pathlib import Path

import numpy as np
import pandas as pd


RESEARCH_FILES = {
    "Customer RFM": {
        "path": "data/processed/customer_rfm.csv",
        "columns": ["customer_id", "recency", "frequency", "monetary"],
    },
    "Clustering comparison": {
        "path": "results/experiments/clustering_baseline.csv",
        "columns": ["algorithm", "clusters", "silhouette", "coverage"],
    },
    "Stability runs": {
        "path": "results/experiments/stability_runs.csv",
        "columns": ["experiment", "run", "ari"],
    },
    "Stability summary": {
        "path": "results/experiments/stability_summary.csv",
        "columns": ["experiment", "mean", "std", "min", "max"],
    },
    "Cluster profiles": {
        "path": "results/experiments/customer_cluster_profiles.csv",
        "columns": [
            "cluster",
            "customers",
            "median_recency",
            "median_frequency",
            "median_monetary",
        ],
    },
    "Model validation": {
        "path": "results/experiments/model_validation_results.csv",
        "columns": [
            "preprocessing",
            "clusters",
            "silhouette",
            "inertia",
            "ari_vs_baseline",
        ],
    },
}


def inspect_csv(path: Path, required: list[str]) -> tuple[str, int, str]:
    """Check a result file without modifying its contents."""

    if not path.is_file():
        return "Missing", 0, "Result file not found."

    try:
        data = pd.read_csv(path)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        return "Invalid", 0, f"Cannot read CSV: {error}"

    if data.empty:
        return "Invalid", 0, "The CSV contains no records."

    missing = sorted(set(required) - set(data.columns))

    if missing:
        return "Invalid", len(data), f"Missing columns: {missing}"

    text_columns = {
        "customer_id",
        "algorithm",
        "experiment",
        "preprocessing",
    }

    # Verify that expected numeric fields contain usable numbers.
    for column in required:
        if column in text_columns:
            continue

        values = pd.to_numeric(data[column], errors="coerce")

        if not np.isfinite(values.to_numpy(dtype=float)).all():
            return "Invalid", len(data), f"Invalid numbers in {column}."

        data[column] = values

    # Scores have known mathematical boundaries.
    for column in [
        "silhouette",
        "ari",
        "ari_vs_baseline",
        "mean",
        "min",
        "max",
    ]:
        if column in data and not data[column].between(-1, 1).all():
            return "Invalid", len(data), f"{column} is outside [-1, 1]."

    if "coverage" in data and not data["coverage"].between(0, 1).all():
        return "Invalid", len(data), "Coverage is outside [0, 1]."

    nonnegative = [
        "recency",
        "frequency",
        "monetary",
        "inertia",
        "std",
        "median_recency",
        "median_frequency",
        "median_monetary",
    ]

    for column in nonnegative:
        if column in data and (data[column] < 0).any():
            return "Invalid", len(data), f"Negative value in {column}."

    if "customer_id" in data:
        if data["customer_id"].isna().any():
            return "Invalid", len(data), "Missing customer IDs."

        if data["customer_id"].duplicated().any():
            return "Invalid", len(data), "Duplicate customer IDs."

    if "clusters" in data and (data["clusters"] < 2).any():
        return "Invalid", len(data), "Invalid cluster count."

    if "customers" in data and (data["customers"] <= 0).any():
        return "Invalid", len(data), "Invalid customer count."

    return "Ready", len(data), "Basic validation checks passed."


def run_research_audit(root: Path) -> pd.DataFrame:
    """Produce an audit table for all expected research outputs."""

    results = []

    workbook = root / "data/raw/Online Retail.xlsx"

    results.append({
        "Component": "Original retail workbook",
        "Status": "Ready" if workbook.is_file() else "Missing",
        "Rows": None,
        "Details": (
            "Workbook exists; contents not validated."
            if workbook.is_file()
            else "Original workbook not found."
        ),
    })

    for name, config in RESEARCH_FILES.items():
        status, rows, details = inspect_csv(
            root / config["path"],
            config["columns"],
        )

        results.append({
            "Component": name,
            "Status": status,
            "Rows": rows,
            "Details": details,
        })

    return pd.DataFrame(results)

def check_customer_coverage(rfm: pd.DataFrame, profiles: pd.DataFrame) -> dict:
    """Check that every RFM customer is represented in group totals."""

    expected = len(rfm)
    actual = int(profiles["customers"].sum())
    difference = actual - expected

    return {
        "Check": "Customer coverage",
        "Status": "Passed" if difference == 0 else "Failed",
        "Expected": expected,
        "Actual": actual,
        "Details": (
            "Cluster profile totals match the RFM population."
            if difference == 0
            else f"Customer counts differ by {difference:+,}."
        ),
    }


def check_stability_summary(
    runs: pd.DataFrame,
    summary: pd.DataFrame,
    tolerance: float = 0.00015,
) -> dict:
    """Recalculate stability statistics from the saved experiment runs."""

    # Pandas std() uses sample standard deviation (ddof=1).
    actual = (
        runs.groupby("experiment")["ari"]
        .agg(["mean", "std", "min", "max"])
        .reset_index()
    )

    merged = summary.merge(
        actual,
        on="experiment",
        how="outer",
        suffixes=("_saved", "_computed"),
        indicator=True,
    )

    if not merged["_merge"].eq("both").all():
        return {
            "Check": "Stability statistics",
            "Status": "Failed",
            "Expected": len(summary),
            "Actual": len(actual),
            "Details": "Experiment names differ between runs and summary.",
        }

    for metric in ["mean", "std", "min", "max"]:
        saved = merged[f"{metric}_saved"]
        computed = merged[f"{metric}_computed"]

        if not (
            (saved - computed).abs() <= tolerance
        ).fillna(False).all():
            return {
                "Check": "Stability statistics",
                "Status": "Failed",
                "Expected": len(summary),
                "Actual": len(actual),
                "Details": f"Saved {metric} does not match the experiment runs.",
            }

    return {
        "Check": "Stability statistics",
        "Status": "Passed",
        "Expected": len(summary),
        "Actual": len(actual),
        "Details": "Saved statistics match recalculated experiment results.",
    }


def check_stability_runs(runs: pd.DataFrame) -> dict:
    """Check that repeated experiment runs have unique identifiers."""

    unique = runs[["experiment", "run"]].drop_duplicates()
    duplicates = len(runs) - len(unique)

    return {
        "Check": "Stability run identifiers",
        "Status": "Passed" if duplicates == 0 else "Failed",
        "Expected": len(runs),
        "Actual": len(unique),
        "Details": (
            "Every experiment/run combination is unique."
            if duplicates == 0
            else f"{duplicates} duplicate experiment/run combinations found."
        ),
    }


def check_validation_configurations(results: pd.DataFrame) -> dict:
    """Verify that each preprocessing and K combination is unique."""

    unique = results[
        ["preprocessing", "clusters"]
    ].drop_duplicates()

    duplicates = len(results) - len(unique)

    return {
        "Check": "Validation configurations",
        "Status": "Passed" if duplicates == 0 else "Failed",
        "Expected": len(results),
        "Actual": len(unique),
        "Details": (
            "Every preprocessing/K combination is unique."
            if duplicates == 0
            else f"{duplicates} duplicate configurations found."
        ),
    }


def run_consistency_checks(root: Path) -> pd.DataFrame:
    """Check whether related research result files agree."""

    output = root / "results/experiments"
    rfm_path = root / "data/processed/customer_rfm.csv"

    def read_pair(first, second):
        """Return valid CSV dataframes or a reason to skip."""

        for path in [first, second]:
            if not path.is_file():
                return None, None, f"Missing input: {path.name}"

        try:
            return pd.read_csv(first), pd.read_csv(second), None
        except (OSError, ValueError, pd.errors.ParserError) as error:
            return None, None, f"Unreadable input: {error}"

    checks = [
        (
            "Customer coverage",
            rfm_path,
            output / "customer_cluster_profiles.csv",
            {"customer_id"},
            {"customers"},
            check_customer_coverage,
        ),
        (
            "Stability statistics",
            output / "stability_runs.csv",
            output / "stability_summary.csv",
            {"experiment", "ari"},
            {"experiment", "mean", "std", "min", "max"},
            check_stability_summary,
        ),
        (
            "Stability run identifiers",
            output / "stability_runs.csv",
            output / "stability_runs.csv",
            {"experiment", "run"},
            {"experiment", "run"},
            lambda a, b: check_stability_runs(a),
        ),
        (
            "Validation configurations",
            output / "model_validation_results.csv",
            output / "model_validation_results.csv",
            {"preprocessing", "clusters"},
            {"preprocessing", "clusters"},
            lambda a, b: check_validation_configurations(a),
        ),
    ]

    findings = []

    for name, first, second, first_cols, second_cols, check in checks:
        left, right, error = read_pair(first, second)

        if error:
            findings.append({
                "Check": name,
                "Status": "Not checked",
                "Expected": None,
                "Actual": None,
                "Details": error,
            })
            continue

        missing = (
            (first_cols - set(left.columns))
            | (second_cols - set(right.columns))
        )

        if missing or left.empty or right.empty:
            findings.append({
                "Check": name,
                "Status": "Not checked",
                "Expected": None,
                "Actual": None,
                "Details": (
                    f"Missing columns: {sorted(missing)}"
                    if missing else "One of the input files is empty."
                ),
            })
            continue

        try:
            findings.append(check(left, right))
        except (ValueError, TypeError, KeyError, OverflowError) as error:
            findings.append({
                "Check": name,
                "Status": "Failed",
                "Expected": None,
                "Actual": None,
                "Details": f"Could not reconcile result files: {error}",
            })

    return pd.DataFrame(findings)


def audit_dashboard(root: Path = Path.cwd()) -> pd.DataFrame:
    """Compatibility wrapper for the original dashboard audit.

    Returns the DataFrame produced by :func:`run_research_audit`.

    Args:
        root: The root directory of the project or data. Defaults to the current working directory.

    Returns:
        pd.DataFrame: The audit results DataFrame.
    """
    return run_research_audit(root)
