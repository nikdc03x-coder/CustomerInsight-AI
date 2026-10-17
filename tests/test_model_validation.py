
import numpy as np
import pandas as pd
import pytest

from customerinsight.model_validation import (
    evaluate_configuration,
    run_parameter_study,
    summarize_best_configs,
    transform_features,
)


@pytest.fixture
def customers():
    """Create repeatable data for our validation tests."""

    rng = np.random.default_rng(42)

    return pd.DataFrame({
        "customer_id": [f"C{i:03d}" for i in range(60)],
        "recency": rng.integers(1, 300, 60),
        "frequency": rng.integers(1, 25, 60),
        "monetary": rng.uniform(100, 8000, 60),
    })


def test_feature_transformation(customers):
    features = transform_features(customers)

    assert features.shape == (60, 3)
    assert np.isfinite(features.to_numpy()).all()


def test_log_changes_feature_representation(customers):
    logged = transform_features(customers, use_log=True)
    standard = transform_features(customers, use_log=False)

    assert not np.allclose(logged, standard)


def test_rejects_negative_values(customers):
    customers.loc[0, "monetary"] = -10

    with pytest.raises(ValueError, match="non-negative"):
        transform_features(customers)


def test_kmeans_returns_valid_results(customers):
    features = transform_features(customers)
    labels, metrics = evaluate_configuration(features, clusters=4)

    assert len(labels) == 60
    assert len(set(labels)) == 4
    assert -1 <= metrics["silhouette"] <= 1


def test_parameter_study(customers):
    results = run_parameter_study(
        customers, cluster_counts=[3, 4]
    )

    assert len(results) == 4
    assert results["ari_vs_baseline"].between(-1, 1).all()
    assert results["silhouette"].between(-1, 1).all()


def test_best_configuration_summary(customers):
    results = run_parameter_study(
        customers, cluster_counts=[3, 4]
    )

    best = summarize_best_configs(results)

    assert len(best) == 2
    assert best["preprocessing"].nunique() == 2
