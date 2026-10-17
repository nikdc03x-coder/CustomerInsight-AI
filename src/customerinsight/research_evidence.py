"""Map the manuscript's four research questions to project evidence."""

from pathlib import Path


RESEARCH_QUESTIONS = [
    {
        "id": "RQ1",
        "title": "Clustering algorithm comparison",
        "question": "Which tested baseline achieved the strongest internal separation?",
        "method": "Construct qualifying-sale RFM features, then compare K-Means, Agglomerative and DBSCAN.",
        "implementation": [
            "src/customerinsight/retail.py", "tests/test_retail.py",
            "src/customerinsight/features.py", "tests/test_features.py",
            "src/customerinsight/clustering.py", "tests/test_clustering.py",
        ],
        "notebook": "notebooks/clustering_experiments.ipynb",
        "evidence": ["data/processed/customer_rfm.csv", "results/experiments/clustering_baseline.csv"],
        "documentation": "docs/clustering_research.md",
        "limitation": "DBSCAN excludes noise from silhouette; internal separation does not prove business usefulness.",
    },
    {
        "id": "RQ2",
        "title": "Clustering stability",
        "question": "How consistent are assignments under the tested perturbations?",
        "method": "Compare random seeds, training subsets and feature noise using ARI.",
        "implementation": ["src/customerinsight/stability.py", "tests/test_stability.py"],
        "notebook": "notebooks/stability_analysis.ipynb",
        "evidence": ["results/experiments/stability_runs.csv", "results/experiments/stability_summary.csv"],
        "documentation": "docs/stability_research.md",
        "limitation": "Agreement with a reference partition does not establish correctness or temporal stability.",
    },
    {
        "id": "RQ3",
        "title": "Sensitivity and model choice",
        "question": "How do preprocessing and cluster count affect results, including the K=2 diagnostic?",
        "method": "Compare two preprocessing choices and K=2–10, then inspect the two-group distribution.",
        "implementation": ["src/customerinsight/model_validation.py", "tests/test_model_validation.py", "scripts/investigate_cluster_balance.py"],
        "notebook": "notebooks/model_validation.ipynb",
        "evidence": ["results/experiments/model_validation_results.csv", "results/experiments/model_validation_best.csv", "results/experiments/k2_cluster_diagnostics.csv"],
        "documentation": "docs/model_validation_research.md",
        "limitation": "Transformations change distances; high silhouette and cluster imbalance need interpretation in context.",
    },
    {
        "id": "RQ4",
        "title": "Interpretability",
        "question": "How do the four baseline customer groups differ in their observed RFM features?",
        "method": "Describe customer counts and median RFM values in original units.",
        "implementation": ["src/customerinsight/explanations.py", "tests/test_explanations.py"],
        "notebook": "notebooks/customer_explainability.ipynb",
        "evidence": ["results/experiments/customer_cluster_profiles.csv"],
        "documentation": "docs/explainability_research.md",
        "limitation": "Group summaries do not establish motivations, causal explanations or individual future behaviour.",
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
    return {"found": found, "missing": missing, "total": len(files), "available": len(found)}
