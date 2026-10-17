
import numpy as np
import pandas as pd
import pytest

from customerinsight.explanations import (
    assign_customer_clusters,
    compare_with_population,
    describe_clusters,
    generate_cluster_descriptions,
)


@pytest.fixture
def customer_data():
    """Create simple customer-like records for reproducible tests."""

    rng = np.random.default_rng(42)

    return pd.DataFrame({
        "customer_id": [f"C{i:03d}" for i in range(40)],
        "recency": rng.integers(1, 300, 40),
        "frequency": rng.integers(1, 15, 40),
        "monetary": rng.uniform(100, 5000, 40),
    })


def test_assigns_every_customer(customer_data):
    result = assign_customer_clusters(customer_data)

    assert len(result) == 40
    assert result["cluster"].nunique() == 4


def test_original_customer_data_is_preserved(customer_data):
    original = customer_data.copy(deep=True)

    assign_customer_clusters(customer_data)

    pd.testing.assert_frame_equal(customer_data, original)


def test_rejects_duplicate_customers(customer_data):
    customer_data.loc[1, "customer_id"] = "C000"

    with pytest.raises(ValueError, match="one RFM record"):
        assign_customer_clusters(customer_data)


def test_cluster_profiles_cover_all_customers(customer_data):
    clustered = assign_customer_clusters(customer_data)
    profiles = describe_clusters(clustered)

    assert profiles["customers"].sum() == 40
    assert profiles["customer_share_pct"].sum() == pytest.approx(100)


def test_population_comparison(customer_data):
    clustered = assign_customer_clusters(customer_data)
    profiles = compare_with_population(clustered)

    assert "recency_relative" in profiles.columns
    assert "frequency_relative" in profiles.columns
    assert "monetary_relative" in profiles.columns


def test_cluster_descriptions(customer_data):
    clustered = assign_customer_clusters(customer_data)
    profiles = compare_with_population(clustered)

    descriptions = generate_cluster_descriptions(profiles)

    assert len(descriptions) == 4
    assert descriptions["description"].str.len().gt(0).all()
