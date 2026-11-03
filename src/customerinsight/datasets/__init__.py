"""Datasets subpackage for CustomerInsight AI.
Provides dataset loading utilities and built‑in dataset registration.
"""

# Re‑export key symbols for backward‑compatible imports
from .datasets import (
    ROOT_DIR,
    DATASETS_DIR,
    DB_PATH,
    DEFAULT_DATASET_ID,
    _init_db,
    list_datasets,
    get_dataset_metadata,
    _ensure_builtin_registered,
    load_dataset_transactions,
    register_uploaded_dataset,
    delete_dataset,
)
