
"""Investigate how preprocessing and cluster count affect K-Means."""

import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

from customerinsight.clustering import FEATURE_COLUMNS


PREPROCESSING_METHODS = {
    "Standard scaling": False,
    "Log + standard scaling": True,
}


def transform_features(
    rfm: pd.DataFrame,
    use_log: bool = True,
) -> pd.DataFrame:
    """Prepare RFM features while keeping customer rows aligned."""

    missing = set(FEATURE_COLUMNS) - set(rfm.columns)

    if missing:
        raise ValueError(f"Missing features: {sorted(missing)}")

    features = rfm[FEATURE_COLUMNS].astype(float).copy()

    if not np.isfinite(features.to_numpy()).all():
        raise ValueError("Features contain missing or infinite values.")

    if (features < 0).any().any():
        raise ValueError("RFM features must be non-negative.")

    # Test whether reducing skew changes the clustering outcome.
    if use_log:
        features = np.log1p(features)

    scaled = StandardScaler().fit_transform(features)

    return pd.DataFrame(
        scaled,
        columns=FEATURE_COLUMNS,
        index=rfm.index,
    )


def evaluate_configuration(
    features: pd.DataFrame,
    clusters: int,
    sample_size: int = 1500,
) -> tuple[np.ndarray, dict]:
    """Train K-Means and evaluate one experimental configuration."""

    if not 2 <= clusters < len(features):
        raise ValueError("Invalid number of clusters.")

    model = KMeans(
        n_clusters=clusters,
        random_state=42,
        n_init=10,
    )

    labels = model.fit_predict(features)

    # Sampling keeps evaluation practical for larger datasets.
    score = silhouette_score(
        features,
        labels,
        sample_size=min(sample_size, len(features)),
        random_state=42,
    )

    return labels, {
        "clusters": clusters,
        "silhouette": float(score),
        "inertia": float(model.inertia_),
    }


def run_parameter_study(
    rfm: pd.DataFrame,
    cluster_counts=range(2, 11),
) -> pd.DataFrame:
    """Compare cluster counts under two preprocessing choices."""

    if not rfm["customer_id"].is_unique:
        raise ValueError("Customer identifiers must be unique.")

    configurations = [
        (name, transform_features(rfm, use_log))
        for name, use_log in PREPROCESSING_METHODS.items()
    ]

    # Our Phase 04 model is the comparison reference.
    baseline_features = transform_features(rfm, use_log=True)
    baseline_labels, _ = evaluate_configuration(
        baseline_features, clusters=4
    )

    results = []

    for method_name, features in configurations:
        for k in cluster_counts:
            labels, metrics = evaluate_configuration(
                features, clusters=k
            )

            results.append({
                "preprocessing": method_name,
                **metrics,
                "ari_vs_baseline": adjusted_rand_score(
                    baseline_labels, labels
                ),
            })

    return pd.DataFrame(results)


def summarize_best_configs(results: pd.DataFrame) -> pd.DataFrame:
    """Find the highest-scoring tested configuration per method."""

    if results.empty:
        raise ValueError("No experiment results were provided.")

    indices = results.groupby("preprocessing")[
        "silhouette"
    ].idxmax()

    return (
        results.loc[indices]
        .sort_values("silhouette", ascending=False)
        .reset_index(drop=True)
    )
