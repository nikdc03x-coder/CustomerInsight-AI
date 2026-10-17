# CustomerInsight AI

An exploratory customer-segmentation research project using historical retail
transactions. It turns qualifying purchases into recency, frequency and monetary
(RFM) features, compares clustering methods, measures assignment stability, and
explains groups through a seven-page Streamlit dashboard.

The project uses established machine-learning methods. Its findings describe one
historical dataset; they do not establish future purchasing behaviour or measured
business impact. Monetary values are gross positive spending, not net revenue.

## What is implemented

- Original-workbook exploration and customer-level RFM construction.
- K-Means, Agglomerative Clustering and DBSCAN baseline comparison.
- K-Means stability under seeds, training subsets and feature noise.
- Two preprocessing methods and K=2–10 sensitivity experiments.
- Four-group descriptions and a separate K=2 imbalance investigation.
- File-integrity checks, cross-file consistency and numerical comparison scripts.
- Six research notebooks, a manuscript draft and research logs.

See [the project review](docs/project_review.md) for architecture, findings,
cleanup decisions and remaining limitations, and [the research manuscript](research/research_manuscript.md)
for the study narrative.

## Installation

Python 3.11 or newer is required. Run these commands from the repository root.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dashboard,dev]"
```

On macOS/Linux, activate with `source .venv/bin/activate` instead.
Install only `-e .` for the reusable analysis package, `-e ".[dashboard]"`
for Streamlit, or `-e ".[dev]"` for tests and notebooks. The development extra
includes Matplotlib, required by the clustering notebook.

```powershell
python scripts/inspect_data.py
python -m pytest -q
python -m streamlit run app/main.py
```

The sample CSV supports a small loader demonstration and tests. It is not a
replacement for the research dataset or the complete dashboard evidence.

## Research data and execution

The raw workbook, processed RFM data and original experiment CSVs are local,
ignored files. A fresh clone therefore needs these inputs before all dashboard
pages can show results. Obtain the dataset using the source listed in
[docs/data_exploration_research.md](docs/data_exploration_research.md), then place
the workbook at `data/raw/Online Retail.xlsx`.

1. Run `python scripts/build_customer_features.py` to write
   `data/processed/customer_rfm.csv`.
2. Read the six notebooks in order: `data_exploration`, `feature_engineering`,
   `clustering_experiments`, `stability_analysis`, `customer_explainability`,
   and `model_validation`.
3. Keep a copy of existing local evidence before regenerating it. The feature
   and stability notebooks write their data/results; the restored clustering,
   explainability and validation notebooks primarily inspect or compare saved
   evidence. Some do not generate every original CSV from scratch.

Full recreation from a fresh clone remains incomplete. The exact expected
artifacts and verification boundaries are documented in
[docs/reproducibility_research.md](docs/reproducibility_research.md).

With the original local evidence present, these commands compare new calculations
against it and write separate reports under `results/reproducibility/`:

```powershell
python scripts/reproduce_clustering.py
python scripts/reproduce_model_validation.py
python scripts/verify_customer_profiles.py
python scripts/verify_research_reproduction.py
```

The last command inspects stored comparison/notebook evidence; it does not rerun
all experiments. `python scripts/research_evidence_summary.py` prints the original
tables. `python scripts/audit_notebook_reproducibility.py` writes a structural
notebook audit, which does not prove successful execution.

## Repository guide

| Location | Purpose |
| --- | --- |
| `src/customerinsight/` | Reusable data, features, modelling and audit functions |
| `app/main.py` | Streamlit navigation and dashboard entry point |
| `app/pages/`, `app/customer_insights.py`, `app/k2_diagnostics.py` | Dashboard pages and diagnostic component |
| `scripts/` | Data preparation, reproduction, inspection and environment tools |
| `tests/` | Synthetic unit tests and optional local-evidence checks |
| `notebooks/` | Research narratives and experiments; edit these directly |
| `docs/`, `research/` | Phase history, current verification record and manuscript |
| `data/sample/` | Small tracked software-verification fixture |
| `data/raw/`, `data/processed/`, `results/experiments/` | Local inputs and original evidence, ignored by Git |
| `results/reproducibility/` | Tracked historical verification artifacts |

Phase documents describe work at the time they were written. Current limitations
and the latest cleanup verification are recorded in the project review.
