"""Reporting subpackage for CustomerInsight AI.
Provides utilities for generating reports and exports.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["generate_executive_brief_markdown", "export_customer_segments_csv"]


def generate_executive_brief_markdown(*args, **kwargs) -> str:
    """Placeholder that returns an empty markdown string.

    Parameters are accepted for signature compatibility but ignored.
    """
    return ""


def export_customer_segments_csv(*args, **kwargs) -> pd.DataFrame:
    """Placeholder that returns an empty DataFrame representing CSV export.

    The real function would write to a file; here we just return a DataFrame.
    """
    return pd.DataFrame()
