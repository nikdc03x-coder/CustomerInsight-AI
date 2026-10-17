
"""Check the experiment files used by the research dashboard."""

from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/experiments"


def test_stability_summary_structure():
    path = RESULTS / "stability_summary.csv"

    if not path.exists():
        pytest.skip("Stability results have not been generated.")

    summary = pd.read_csv(path)

    required = {"experiment", "mean", "std", "min", "max"}

    assert required.issubset(summary.columns)
    assert not summary.empty
    assert summary["mean"].between(-1, 1).all()


def test_stability_runs_structure():
    path = RESULTS / "stability_runs.csv"

    if not path.exists():
        pytest.skip("Stability runs have not been generated.")

    runs = pd.read_csv(path)

    assert {"experiment", "run", "ari"}.issubset(runs.columns)
    assert runs["ari"].between(-1, 1).all()


def test_clustering_results_structure():
    path = RESULTS / "clustering_baseline.csv"

    if not path.exists():
        pytest.skip("Clustering results have not been generated.")

    results = pd.read_csv(path)

    required = {
        "algorithm",
        "clusters",
        "silhouette",
        "coverage",
    }

    assert required.issubset(results.columns)
    assert results["coverage"].between(0, 1).all()
