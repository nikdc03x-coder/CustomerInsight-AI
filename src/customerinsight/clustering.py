
"""Compare clustering algorithms using customer RFM features."""

import numpy as np
import pandas as pd

from sklearn.cluster import (
    AgglomerativeClustering,
    DBSCAN,
    KMeans,
)
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = ["recency", "frequency", "monetary"]


def prepare_clustering_features(rfm: pd.DataFrame) -> pd.DataFrame:
    """Transform skewed RFM values into comparable model inputs."""

    missing = set(FEATURE_COLUMNS) - set(rfm.columns)

    if missing:
        raise ValueError(f"Missing features: {sorted(missing)}")

    features = rfm[FEATURE_COLUMNS].copy()

    if features.isna().any().any():
        raise ValueError("RFM contains missing feature values.")

    if not np.isfinite(features.to_numpy(dtype=float)).all():
        raise ValueError("RFM contains non-finite values.")

    if (features < 0).any().any():
        raise ValueError("RFM features must be non-negative.")

    # Log transformation reduces the effect of very large values.
    features = np.log1p(features)

    # Standardization prevents one feature's scale from dominating.
    scaler = StandardScaler()
    transformed = scaler.fit_transform(features)

    return pd.DataFrame(
        transformed,
        columns=FEATURE_COLUMNS,
        index=rfm.index,
    )


def run_clustering_experiments(
    features: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    """Fit three baseline methods and compare their cluster structure."""

    models = {
        "K-Means": KMeans(
            n_clusters=4,
            random_state=42,
            n_init=10,
        ),
        "Agglomerative": AgglomerativeClustering(
            n_clusters=4,
        ),
        "DBSCAN": DBSCAN(
            eps=0.5,
            min_samples=10,
        ),
    }

    rows = []
    labels_by_model = {}

    for name, model in models.items():
        labels = model.fit_predict(features)
        labels_by_model[name] = labels

        # DBSCAN labels outlying observations as -1.
        clustered = labels != -1
        cluster_labels = set(labels) - {-1}
        n_clusters = len(cluster_labels)

        # Exclude DBSCAN noise from silhouette calculations.
        evaluated = clustered if name == "DBSCAN" else np.ones(
            len(labels), dtype=bool
        )

        evaluated_labels = labels[evaluated]
        sample = features.loc[evaluated]

        # Silhouette requires at least two valid groups.
        score = np.nan

        if 2 <= n_clusters < len(sample):
            score = silhouette_score(
                sample,
                evaluated_labels,
                sample_size=min(2000, len(sample)),
                random_state=42,
            )

        rows.append({
            "algorithm": name,
            "clusters": n_clusters,
            "silhouette": score,
            "coverage": round(evaluated.mean(), 4),
        })

    return pd.DataFrame(rows), labels_by_model
