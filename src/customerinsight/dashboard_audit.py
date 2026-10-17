
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
