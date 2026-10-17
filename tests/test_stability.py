
import numpy as np
import pandas as pd
import pytest

from customerinsight.stability import (
    fit_kmeans,
    run_stability_study,
    test_feature_noise as evaluate_feature_noise,
    test_random_seeds as evaluate_random_seeds,
    test_resampling as evaluate_resampling,
)


@pytest.fixture
def customer_features():
    """Create repeatable customer-like data for testing."""

    rng = np.random.default_rng(42)

    # Four groups with small variation around different centres.
    groups = [
        rng.normal(center, 0.3, size=(20, 3))
        for center in [-3, -1, 1, 3]
    ]

    return pd.DataFrame(
        np.vstack(groups),
        columns=["recency", "frequency", "monetary"],
    )


def test_model_assigns_each_customer(customer_features):
    model = fit_kmeans(customer_features)

    assert len(model.labels_) == len(customer_features)


def test_seed_experiment(customer_features):
    results = evaluate_random_seeds(customer_features, runs=3)

    assert len(results) == 3
    assert results["ari"].between(-1, 1).all()


def test_resampling_experiment(customer_features):
    results = evaluate_resampling(customer_features, runs=3)

    assert len(results) == 3
    assert results["ari"].between(-1, 1).all()


def test_noise_experiment(customer_features):
    results = evaluate_feature_noise(customer_features, runs=3)

    assert len(results) == 3
    assert results["ari"].between(-1, 1).all()


def test_invalid_sample_fraction(customer_features):
    with pytest.raises(ValueError, match="sample_fraction"):
        evaluate_resampling(
            customer_features, sample_fraction=0
        )


def test_invalid_noise_level(customer_features):
    with pytest.raises(ValueError, match="noise_level"):
        evaluate_feature_noise(
            customer_features, noise_level=-0.1
        )


def test_combined_results(customer_features):
    detailed, summary = run_stability_study(
        customer_features, runs=3
    )

    assert len(detailed) == 9
    assert len(summary) == 3
    assert {"mean", "std", "min", "max"}.issubset(
        summary.columns
    )
