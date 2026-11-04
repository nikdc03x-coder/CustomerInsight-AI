"""Segmentation utilities placeholder.

These functions provide minimal implementations that satisfy the public API
required by the test suite. Real logic can be added later.
"""

import pandas as pd


def segment_customers(df: pd.DataFrame | None = None, n_clusters: int = 4) -> pd.DataFrame:
    """Perform simple KMeans segmentation on RFM DataFrame.

    Parameters
    ----------
    df: pd.DataFrame | None
        Input DataFrame containing at least the columns ``recency``, ``frequency`` and ``monetary``.
        If ``None`` or empty, returns an empty DataFrame with the expected schema.
    n_clusters: int
        Number of clusters for KMeans. Defaults to 4 to match UI expectations.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - ``segment_name`` (e.g., ``Segment 1``)
        - ``total_spend`` (sum of monetary)
        - ``customers`` (count of customers in segment)
        - ``revenue_share_pct`` (percentage of total revenue)
        - ``median_monetary`` (median monetary value)
    """
    if df is None or df.empty:
        # Return empty DataFrame with required columns
        return pd.DataFrame(columns=["segment_name", "total_spend", "customers", "revenue_share_pct", "median_monetary"])

    # Ensure necessary columns exist; if not, attempt to compute them from transaction data
    required_cols = {"recency", "frequency", "monetary"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required RFM columns for segmentation: {missing}")

    # Use only the numeric columns for clustering
    features = df[["recency", "frequency", "monetary"]].fillna(0)
    # Scale features to mitigate magnitude differences (simple min-max scaling)
    mins = features.min()
    maxs = features.max().replace(0, 1)  # avoid division by zero
    scaled = (features - mins) / (maxs - mins)

    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(scaled)
    df = df.copy()
    df["segment"] = labels

    total_revenue = df["monetary"].sum()
    summary = (
        df.groupby("segment")
        .agg(
            total_spend=pd.NamedAgg(column="monetary", aggfunc="sum"),
            customers=pd.NamedAgg(column="customer_id", aggfunc="nunique"),
            median_monetary=pd.NamedAgg(column="monetary", aggfunc="median"),
        )
        .reset_index()
    )
    summary["revenue_share_pct"] = (summary["total_spend"] / total_revenue * 100).round(2)
    summary["segment_name"] = summary["segment"].apply(lambda x: f"Segment {x + 1}")
    # Reorder columns as expected by UI/tests
    return summary[["segment_name", "total_spend", "customers", "revenue_share_pct", "median_monetary"]]




def compare_segments(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Return a placeholder comparison DataFrame.
    """
    return pd.DataFrame()
