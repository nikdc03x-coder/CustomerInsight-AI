
"""Map our research questions to implementations and saved evidence."""

from pathlib import Path


RESEARCH_QUESTIONS = [
    {
        "id": "RQ1",
        "title": "Data quality and preparation",
        "question": "Can historical transactions be prepared for customer analysis?",
        "method": "Inspect source records, exclude unsuitable purchases, and construct clean data.",
        "implementation": [
            "src/customerinsight/retail.py",
            "tests/test_retail.py",
        ],
        "notebook": "notebooks/data_exploration.ipynb",
        "evidence": [
            "data/processed/customer_rfm.csv",
        ],
        "documentation": "docs/data_exploration_research.md",
        "limitation": (
            "Qualifying sales do not fully reconcile refunds "
            "or establish complete transaction profitability."
        ),
    },
    {
        "id": "RQ2",
        "title": "Customer behaviour representation",
        "question": "Can purchasing behaviour be represented using RFM features?",
        "method": "Calculate customer recency, unique invoice frequency, and positive spending.",
        "implementation": [
            "src/customerinsight/features.py",
            "tests/test_features.py",
        ],
        "notebook": "notebooks/feature_engineering.ipynb",
        "evidence": [
            "data/processed/customer_rfm.csv",
        ],
        "documentation": "docs/feature_engineering_research.md",
        "limitation": (
            "RFM summarizes observed purchasing history "
            "but does not capture every aspect of customer behaviour."
        ),
    },
    {
        "id": "RQ3",
        "title": "Clustering algorithm comparison",
        "question": "Which baseline clustering method provides stronger separation?",
        "method": "Compare K-Means, Agglomerative Clustering, and DBSCAN.",
        "implementation": [
            "src/customerinsight/clustering.py",
            "tests/test_clustering.py",
        ],
        "notebook": "notebooks/clustering_experiments.ipynb",
        "evidence": [
            "results/experiments/clustering_baseline.csv",
        ],
        "documentation": "docs/clustering_research.md",
        "limitation": (
            "Internal separation is not equivalent to "
            "ground-truth accuracy or business usefulness."
        ),
    },
    {
        "id": "RQ4",
        "title": "Clustering stability",
        "question": "Do customer assignments remain similar under tested changes?",
        "method": "Compare seeds, training subsets, and feature perturbations using ARI.",
        "implementation": [
            "src/customerinsight/stability.py",
            "tests/test_stability.py",
        ],
        "notebook": "notebooks/stability_analysis.ipynb",
        "evidence": [
            "results/experiments/stability_runs.csv",
            "results/experiments/stability_summary.csv",
        ],
        "documentation": "docs/stability_research.md",
        "limitation": (
            "Agreement with a reference partition does not "
            "establish objective correctness."
        ),
    },
    {
        "id": "RQ5",
        "title": "Explainability and parameter sensitivity",
        "question": "Can groups be understood, and how sensitive are model settings?",
        "method": (
            "Profile customer groups and compare K-Means "
            "configurations under different preprocessing methods."
        ),
        "implementation": [
            "src/customerinsight/explanations.py",
            "src/customerinsight/model_validation.py",
        ],
        "notebook": "notebooks/model_validation.ipynb",
        "evidence": [
            "results/experiments/customer_cluster_profiles.csv",
            "results/experiments/model_validation_results.csv",
        ],
        "documentation": "docs/model_validation_research.md",
        "limitation": (
            "Descriptive profiles and parameter sensitivity "
            "do not prove causal explanations or external validity."
        ),
    },
]


def get_evidence_status(question: dict, root: Path) -> dict:
    """List available and missing evidence files for a research question."""

    files = (
        question["implementation"]
        + [question["notebook"]]
        + question["evidence"]
        + [question["documentation"]]
    )

    found = [path for path in files if (root / path).is_file()]
    missing = [path for path in files if not (root / path).is_file()]

    return {
        "found": found,
        "missing": missing,
        "total": len(files),
        "available": len(found),
    }
