
"""Explain customer groups using their original purchasing features."""

import pandas as pd

from customerinsight.clustering import (
    FEATURE_COLUMNS,
    prepare_clustering_features,
)
from customerinsight.stability import fit_kmeans


def assign_customer_clusters(
    rfm: pd.DataFrame,
    clusters: int = 4,
) -> pd.DataFrame:
    """Assign customer groups using our existing clustering pipeline."""

    if "customer_id" not in rfm.columns:
        raise ValueError("Missing customer_id column.")

    if rfm["customer_id"].isna().any():
        raise ValueError("Customer identifiers cannot be missing.")

    if rfm["customer_id"].duplicated().any():
        raise ValueError("Each customer must have one RFM record.")

    if len(rfm) < clusters or clusters < 2:
        raise ValueError("Invalid number of clusters.")

    # The model uses transformed RFM values for distance calculations.
    features = prepare_clustering_features(rfm)
    model = fit_kmeans(features, clusters=clusters)

    # Explanations use the original units, not standardized values.
    customers = rfm.copy()
    customers["cluster"] = model.labels_

    return customers


def describe_clusters(customers: pd.DataFrame) -> pd.DataFrame:
    """Summarize typical purchasing behaviour for each customer group."""

    required = set(FEATURE_COLUMNS) | {"cluster"}

    if not required.issubset(customers.columns):
        raise ValueError("Customer data is missing clustering features.")

    profiles = (
        customers.groupby("cluster")
        .agg(
            customers=("cluster", "size"),
            median_recency=("recency", "median"),
            median_frequency=("frequency", "median"),
            median_monetary=("monetary", "median"),
            total_positive_spending=("monetary", "sum"),
        )
        .reset_index()
        .sort_values("cluster")
    )

    profiles["customer_share_pct"] = (
        profiles["customers"] / len(customers) * 100
    )

    return profiles.round(2)


def compare_with_population(
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Compare each cluster's medians with overall customer medians."""

    profiles = describe_clusters(customers)
    population = customers[FEATURE_COLUMNS].median()

    # Ratios give context: 1.5 means 50% above the overall median.
    for feature in FEATURE_COLUMNS:
        baseline = population[feature]
        column = f"median_{feature}"
        output_column = f"{feature}_relative"

        if baseline > 0:
            profiles[output_column] = profiles[column] / baseline
        else:
            # Ratios cannot be interpreted when the baseline is zero.
            profiles[output_column] = float("nan")

    return profiles.round(3)


def generate_cluster_descriptions(
    profiles: pd.DataFrame,
) -> pd.DataFrame:
    """Describe group differences without guessing customer motivations."""

    descriptions = []

    for _, group in profiles.iterrows():
        observations = []

        for feature, label in [
            ("recency", "time since last purchase"),
            ("frequency", "purchase frequency"),
            ("monetary", "positive spending"),
        ]:
            relative = group[f"{feature}_relative"]

            if pd.isna(relative):
                observation = f"{label}: comparison unavailable"
            elif relative >= 1.2:
                observation = f"higher {label}"
            elif relative <= 0.8:
                observation = f"lower {label}"
            else:
                observation = f"similar {label}"

            observations.append(observation)

        descriptions.append({
            "cluster": int(group["cluster"]),
            "description": "; ".join(observations),
        })

    return pd.DataFrame(descriptions)
