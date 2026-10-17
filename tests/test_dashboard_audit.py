
"""Tests for the research dashboard audit."""

import pandas as pd

from customerinsight.dashboard_audit import (
    inspect_csv,
    run_research_audit,
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
