
"""Tests for the research dashboard audit."""

import pandas as pd

from customerinsight.dashboard_audit import (
    inspect_csv,
    run_research_audit,
)

from customerinsight.dashboard_audit import (
    check_customer_coverage,
    check_stability_summary,
    check_stability_runs,
    check_validation_configurations,
)



def test_missing_file(tmp_path):
    """Missing experiment files should be reported clearly."""

    status, rows, detail = inspect_csv(
        tmp_path / "missing.csv",
        ["customer_id", "monetary"],
    )

    assert status == "Missing"
    assert rows == 0


def test_valid_customer_file(tmp_path):
    """A valid customer dataset should pass the basic checks."""

    path = tmp_path / "customers.csv"

    pd.DataFrame({
        "customer_id": ["A", "B"],
        "recency": [10, 20],
        "frequency": [2, 3],
        "monetary": [100, 200],
    }).to_csv(path, index=False)

    status, rows, _ = inspect_csv(
        path,
        ["customer_id", "recency", "frequency", "monetary"],
    )

    assert status == "Ready"
    assert rows == 2


def test_invalid_score_range(tmp_path):
    """Scores outside their mathematical bounds must be rejected."""

    path = tmp_path / "scores.csv"

    pd.DataFrame({
        "algorithm": ["Example"],
        "silhouette": [1.5],
    }).to_csv(path, index=False)

    status, _, detail = inspect_csv(
        path,
        ["algorithm", "silhouette"],
    )

    assert status == "Invalid"
    assert "outside" in detail


def test_audit_reports_missing_research(tmp_path):
    """The audit should identify all missing research files."""

    findings = run_research_audit(tmp_path)

    assert len(findings) == 7
    assert (findings["Status"] == "Missing").all()


def test_customer_coverage_matches():
    """Cluster totals should match the customer population."""

    rfm = pd.DataFrame({
        "customer_id": ["A", "B", "C", "D"],
    })

    profiles = pd.DataFrame({
        "cluster": [0, 1],
        "customers": [2, 2],
    })

    result = check_customer_coverage(rfm, profiles)

    assert result["Status"] == "Passed"
    assert result["Actual"] == 4


def test_customer_coverage_mismatch():
    """Missing customers should be detected."""

    rfm = pd.DataFrame({
        "customer_id": ["A", "B", "C", "D"],
    })

    profiles = pd.DataFrame({
        "cluster": [0, 1],
        "customers": [2, 1],
    })

    result = check_customer_coverage(rfm, profiles)

    assert result["Status"] == "Failed"


def test_saved_stability_summary_matches_runs():
    """Recalculated ARI statistics should match saved summaries."""

    runs = pd.DataFrame({
        "experiment": ["Noise", "Noise", "Noise"],
        "run": [1, 2, 3],
        "ari": [0.8, 0.9, 1.0],
    })

    summary = (
        runs.groupby("experiment")["ari"]
        .agg(["mean", "std", "min", "max"])
        .reset_index()
    )

    result = check_stability_summary(runs, summary)

    assert result["Status"] == "Passed"


def test_duplicate_stability_run_is_detected():
    """An experiment must not contain duplicate run identifiers."""

    runs = pd.DataFrame({
        "experiment": ["Noise", "Noise"],
        "run": [1, 1],
        "ari": [0.8, 0.9],
    })

    result = check_stability_runs(runs)

    assert result["Status"] == "Failed"


def test_duplicate_validation_setting_is_detected():
    """Each preprocessing and cluster-count pair must be unique."""

    results = pd.DataFrame({
        "preprocessing": ["Log + scaling", "Log + scaling"],
        "clusters": [4, 4],
    })

    result = check_validation_configurations(results)

    assert result["Status"] == "Failed"
