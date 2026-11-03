"""Prediction module stubs for CustomerInsight AI.

The real predictive models are out of scope for the current test suite. We provide
light‑weight placeholder implementations that satisfy the public API expected by
`customerinsight.__init__` and the unit tests.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["assess_predictive_eligibility", "predict_customer_recurrence_and_clv"]


def assess_predictive_eligibility(*args, **kwargs) -> pd.DataFrame:
    """Placeholder returning an empty DataFrame for eligibility assessment.

    Parameters
    ----------
    *args, **kwargs : Any
        Ignored – present only for signature compatibility.
    """
    return pd.DataFrame()


def predict_customer_recurrence_and_clv(*args, **kwargs) -> pd.DataFrame:
    """Placeholder returning an empty DataFrame for CLV predictions.

    Parameters
    ----------
    *args, **kwargs : Any
        Ignored – present only for signature compatibility.
    """
    return pd.DataFrame()

