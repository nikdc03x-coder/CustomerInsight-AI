
"""Measure how consistently K-Means groups the same customers."""

import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score


def fit_kmeans(
    features: pd.DataFrame,
    seed: int = 42,
    clusters: int = 4,
) -> KMeans:
    """Fit a reproducible K-Means model."""

    model = KMeans(
        n_clusters=clusters,
        random_state=seed,
        n_init=10,
    )
    model.fit(features)
    return model


def test_random_seeds(
    features: pd.DataFrame,
    runs: int = 20,
    clusters: int = 4,
) -> pd.DataFrame:
    """Check whether initialization changes customer assignments."""

    # The same customers and features are used in every run.
    reference = fit_kmeans(features, clusters=clusters).labels_

    results = []

    for seed in range(runs):
        labels = fit_kmeans(
            features, seed=seed, clusters=clusters
        ).labels_

        results.append({
            "experiment": "Random initialization",
            "run": seed + 1,
            "ari": adjusted_rand_score(reference, labels),
        })

    return pd.DataFrame(results)


def test_resampling(
    features: pd.DataFrame,
    runs: int = 20,
    sample_fraction: float = 0.8,
    clusters: int = 4,
) -> pd.DataFrame:
    """Check assignments when models learn from different subsets."""

    if not 0 < sample_fraction <= 1:
        raise ValueError("sample_fraction must be between 0 and 1.")

    values = features.to_numpy()
    count = len(values)
    sample_size = int(count * sample_fraction)

    if sample_size < clusters:
        raise ValueError("The sample is too small for clustering.")

    # All models are evaluated on the same full customer population.
    reference = fit_kmeans(features, clusters=clusters)
    reference_labels = reference.predict(features)

    results = []

    for run in range(runs):
        rng = np.random.default_rng(1000 + run)

        indices = rng.choice(
            count,
            size=sample_size,
            replace=False,
        )

        model = fit_kmeans(
            features.iloc[indices],
            seed=42,
            clusters=clusters,
        )

        # Predict the same customers using the newly trained model.
        labels = model.predict(features)

        results.append({
            "experiment": "Training subset",
            "run": run + 1,
            "ari": adjusted_rand_score(
                reference_labels, labels
            ),
        })

    return pd.DataFrame(results)


def test_feature_noise(
    features: pd.DataFrame,
    runs: int = 20,
    noise_level: float = 0.05,
    clusters: int = 4,
) -> pd.DataFrame:
    """Check how small feature changes affect customer assignments."""

    if noise_level < 0:
        raise ValueError("noise_level cannot be negative.")

    reference = fit_kmeans(features, clusters=clusters)
    reference_labels = reference.labels_
    values = features.to_numpy()

    results = []

    for run in range(runs):
        rng = np.random.default_rng(2000 + run)

        # Add small noise in the standardized feature space.
        noise = rng.normal(
            loc=0,
            scale=noise_level,
            size=values.shape,
        )

        changed_features = pd.DataFrame(
            values + noise,
            columns=features.columns,
            index=features.index,
        )

        model = fit_kmeans(
            changed_features,
            seed=42,
            clusters=clusters,
        )

        labels = model.predict(changed_features)

        results.append({
            "experiment": "Feature noise",
            "run": run + 1,
            "ari": adjusted_rand_score(
                reference_labels, labels
            ),
        })

    return pd.DataFrame(results)


def run_stability_study(
    features: pd.DataFrame,
    runs: int = 20,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run our three experiments and summarize their results."""

    if runs < 1:
        raise ValueError("At least one run is required.")

    if len(features) < 5:
        raise ValueError("At least five customers are required.")

    experiments = [
        test_random_seeds(features, runs=runs),
        test_resampling(features, runs=runs),
        test_feature_noise(features, runs=runs),
    ]

    detailed = pd.concat(experiments, ignore_index=True)

    summary = (
        detailed.groupby("experiment")["ari"]
        .agg(["mean", "std", "min", "max"])
        .reset_index()
        .round(4)
    )

    return detailed, summary
