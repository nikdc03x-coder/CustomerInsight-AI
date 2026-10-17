# CustomerInsight AI

### Explainable Customer Behaviour Discovery

CustomerInsight AI is a research-oriented Data Science
and Machine Learning project investigating how
unsupervised learning algorithms discover and explain
customer purchasing patterns.

## Research objective

Our primary goal is to investigate the quality,
stability and interpretability of customer segmentation
methods using retail transaction data.

## Research questions

- How do different clustering algorithms compare?
- How stable are their customer segments?
- How can we explain the identified groups clearly?

## Research approach

The project combines:

- Customer transaction analysis
- Behavioural feature engineering
- Unsupervised machine learning
- Model evaluation and stability testing
- Explainable visualizations
- Reproducible Python software

## Architecture

We use Jupyter notebooks for research experiments
and Python modules for reusable implementation.

The final Streamlit application will demonstrate
the results in a way that non-technical users
can understand.

## Getting started

Requirements: Python 3.11 or newer.

Create an environment:

    python -m venv .venv
    source .venv/Scripts/activate

Install dependencies:

    python -m pip install -e ".[dev]"

Inspect the demonstration data:

    python scripts/inspect_data.py

Run the tests:

    python -m pytest -v

## Research documentation

Phase-by-phase research records are stored in `docs/`.

The first report is:

`docs/phase_01_foundation.md`

## Project status

Phase 01 — Research foundation and data-loading module.

The sample data is only for software verification.
Experimental findings will be reported after
the research dataset has been selected and analysed.
