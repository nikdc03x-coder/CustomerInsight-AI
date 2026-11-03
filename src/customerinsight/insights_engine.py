"""Stub for the insights engine.

The real business‑insight logic is out of scope for the current test suite.
We expose the public API expected by `customerinsight.__init__` and the unit
tests with lightweight placeholder implementations.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["generate_business_insights", "BusinessInsight"]


class BusinessInsight:
    """Simple container for an insight description.

    Attributes
    ----------
    title : str
        Short title of the insight.
    description : str
        Human‑readable description.
    """

    def __init__(self, title: str = "", description: str = "") -> None:
        self.title = title
        self.description = description

    def __repr__(self) -> str:
        return f"BusinessInsight(title={self.title!r}, description={self.description!r})"


def generate_business_insights(*args, **kwargs) -> list[BusinessInsight]:
    """Placeholder that returns an empty list of insights.

    The signature matches the real implementation; all arguments are ignored.
    """
    return []
