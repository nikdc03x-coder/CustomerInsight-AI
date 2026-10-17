
"""Restore the clustering research notebook using existing project modules."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks/clustering_experiments.ipynb"


def markdown(source):
    """Create a notebook Markdown cell."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code(source):
    """Create an executable notebook code cell."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def main():
    """Build the notebook without running experiments."""

    cells = [
        markdown(
            "# Clustering Experiments — CustomerInsight AI\n\n"
            "## Research Objective\n\n"
            "Compare K-Means, Agglomerative Clustering and DBSCAN "
            "using customer-level RFM measurements.\n\n"
            "This notebook uses existing project code instead of "
            "implementing clustering algorithms from scratch."
        ),

        markdown(
            "## 1. Research Question\n\n"
            "**Which of the tested clustering configurations "
            "produces the strongest internal separation?**\n\n"
            "We use silhouette score and cluster coverage, "
            "while recognising their limitations."
        ),

        code(
            "from pathlib import Path\n"
            "import sys\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "\n"
            "# Make the project package importable in Jupyter.\n"
            "ROOT = Path.cwd().resolve()\n"
            "if ROOT.name == 'notebooks':\n"
            "    ROOT = ROOT.parent\n"
            "if not (ROOT / 'src/customerinsight').exists():\n"
            "    raise FileNotFoundError('Open this notebook from the project.')\n"
            "sys.path.insert(0, str(ROOT / 'src'))\n"
            "\n"
            "from customerinsight.clustering import (\n"
            "    prepare_clustering_features,\n"
            "    run_clustering_experiments,\n"
            ")\n"
            "\n"
            "print('Project:', ROOT)"
        ),

        markdown(
            "## 2. Research Data\n\n"
            "We use the saved customer-level RFM dataset. "
            "Each row represents one customer.\n\n"
            "- Recency: days since the last qualifying purchase\n"
            "- Frequency: number of distinct positive-sale invoices\n"
            "- Monetary: gross positive spending\n\n"
            "Historical returns and cancellations are not fully "
            "reconciled into net monetary value."
        ),

        code(
            "rfm_path = ROOT / 'data/processed/customer_rfm.csv'\n"
            "rfm = pd.read_csv(rfm_path)\n"
            "\n"
            "required = {'customer_id', 'recency', 'frequency', 'monetary'}\n"
            "assert required.issubset(rfm.columns)\n"
            "assert not rfm.empty\n"
            "\n"
            "print('Customers:', len(rfm))\n"
            "display(rfm.head())\n"
            "display(rfm[['recency', 'frequency', 'monetary']].describe())"
        ),

        markdown(
            "## 3. Feature Preparation\n\n"
            "The existing project implementation prepares RFM "
            "features for clustering using the methodology "
            "implemented in `clustering.py`.\n\n"
            "We reuse that function instead of independently "
            "recreating its preprocessing steps."
        ),

        code(
            "features = prepare_clustering_features(rfm)\n"
            "print('Prepared feature type:', type(features).__name__)\n"
            "print('Prepared shape:', features.shape)\n"
            "display(features.head() if hasattr(features, 'head') else features[:5])"
        ),

        markdown(
            "## 4. Saved Baseline Evidence\n\n"
            "First, inspect the original experiment results.\n\n"
            "Reading this CSV does **not** reproduce the "
            "experiment; it establishes the saved baseline "
            "against which future execution can be checked."
        ),

        code(
            "baseline_path = ROOT / 'results/experiments/clustering_baseline.csv'\n"
            "baseline = pd.read_csv(baseline_path)\n"
            "display(baseline)\n"
            "\n"
            "ax = baseline.plot.bar(\n"
            "    x='algorithm', y='silhouette', legend=False,\n"
            "    title='Baseline clustering comparison', figsize=(8, 4)\n"
            ")\n"
            "ax.set_ylabel('Silhouette score')\n"
            "ax.set_xlabel('Algorithm')\n"
            "plt.xticks(rotation=0)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),

        markdown(
            "## 5. Re-execution of Clustering Experiments\n\n"
            "The following cell calls the same project function "
            "used to create the original clustering comparison.\n\n"
            "It does not explicitly save any results. "
            "Before executing this cell, confirm that "
            "`run_clustering_experiments` itself does not write "
            "to protected experiment files."
        ),

        code(
            "# Safety guard: intentionally disabled until function\n"
            "# side effects and execution settings are reviewed.\n"
            "RUN_EXPERIMENT = False\n"
            "\n"
            "if RUN_EXPERIMENT:\n"
            "    reproduced = run_clustering_experiments(features)\n"
            "    print('Experiment result type:', type(reproduced).__name__)\n"
            "    display(reproduced)\n"
            "else:\n"
            "    print('Experiment not run. Review the function first.')"
        ),

        markdown(
            "## 6. Verified Baseline Results\n\n"
            "The saved Phase 04 results were:\n\n"
            "| Algorithm | Clusters | Silhouette | Coverage |\n"
            "|---|---:|---:|---:|\n"
            "| K-Means | 4 | 0.332372 | 1.0000 |\n"
            "| Agglomerative | 4 | 0.270554 | 1.0000 |\n"
            "| DBSCAN | 2 | 0.289804 | 0.9818 |\n\n"
            "These values are the recorded baseline results, "
            "not a claim that the notebook has reproduced them."
        ),

        markdown(
            "## 7. Interpretation\n\n"
            "K-Means achieved the highest silhouette score among "
            "the three tested baseline configurations.\n\n"
            "However, this result does not establish that K-Means "
            "is universally superior or that its clusters are "
            "ground-truth customer categories."
        ),

        markdown(
            "## 8. Limitations\n\n"
            "- Only selected algorithm configurations were compared.\n"
            "- Silhouette evaluates internal structure, not business value.\n"
            "- DBSCAN assigned some observations to noise.\n"
            "- Results depend on feature transformations and parameters.\n"
            "- A fresh experiment execution must be compared with "
            "the original saved results before reproducibility is claimed."
        ),

        markdown(
            "## 9. Reproducibility Status\n\n"
            "**Notebook restored; numerical reproduction pending.**\n\n"
            "Next actions:\n\n"
            "1. Review clustering function side effects.\n"
            "2. Execute the experiment under controlled conditions.\n"
            "3. Compare regenerated scores and cluster counts.\n"
            "4. Record discrepancies and software versions."
        ),
    ]

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(notebook, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Restored notebook: {OUTPUT}")
    print(f"Total cells: {len(cells)}")
    print(
        "Experiment execution remains disabled until "
        "function side effects are reviewed."
    )


if __name__ == "__main__":
    main()
