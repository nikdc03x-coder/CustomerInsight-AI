
import numpy as np
import pandas as pd
import pytest

from customerinsight.clustering import (
    prepare_clustering_features,
    run_clustering_experiments,
)


def make_customer_data():
    # Create repeatable sample data with different spending habits.
    rng = np.random.default_rng(42)

    return pd.DataFrame({
        "recency": rng.integers(1, 365, size=60),
        "frequency": rng.integers(1, 25, size=60),
        "monetary": rng.uniform(100, 10000, size=60),
    })


def test_feature_preparation():
    data = make_customer_data()

    features = prepare_clustering_features(data)

    assert features.shape == (60, 3)
    assert np.isfinite(features.to_numpy()).all()


def test_missing_features_are_rejected():
    data = pd.DataFrame({"recency": [10, 20]})

    with pytest.raises(ValueError, match="Missing features"):
        prepare_clustering_features(data)


def test_negative_values_are_rejected():
    data = make_customer_data()
    data.loc[0, "monetary"] = -100

    with pytest.raises(ValueError, match="non-negative"):
        prepare_clustering_features(data)


def test_experiment_outputs():
    features = prepare_clustering_features(make_customer_data())

    results, labels = run_clustering_experiments(features)

    assert len(results) == 3
    assert set(labels) == {
        "K-Means",
        "Agglomerative",
        "DBSCAN",
    }

    for model_labels in labels.values():
        assert len(model_labels) == len(features)

    assert results["coverage"].between(0, 1).all()
