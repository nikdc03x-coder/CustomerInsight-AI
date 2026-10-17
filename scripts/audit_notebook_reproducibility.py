
"""Audit research notebooks without executing or modifying them."""

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
OUTPUT = ROOT / "results/reproducibility/notebook_audit.csv"

# These are the main notebooks from our research phases.
EXPECTED_NOTEBOOKS = [
    "data_exploration.ipynb",
    "feature_engineering.ipynb",
    "clustering_experiments.ipynb",
    "stability_analysis.ipynb",
    "customer_explainability.ipynb",
    "model_validation.ipynb",
]


def inspect_notebook(name):
    """Check notebook structure and saved execution evidence."""

    path = NOTEBOOKS / name

    result = {
        "Notebook": name,
        "Exists": False,
        "Valid structure": False,
        "Code cells": 0,
        "Executed cells": 0,
        "Cells with outputs": 0,
        "Status": "Missing",
        "Details": "",
    }

    if not path.is_file():
        result["Details"] = "Expected notebook was not found."
        return result

    result["Exists"] = True

    try:
        with path.open(encoding="utf-8") as file:
            notebook = json.load(file)

    except (OSError, ValueError) as error:
        result["Status"] = "Invalid"
        result["Details"] = str(error)
        return result

    if (
        not isinstance(notebook, dict)
        or not isinstance(notebook.get("cells"), list)
        or notebook.get("nbformat") != 4
    ):
        result["Status"] = "Invalid"
        result["Details"] = "Notebook has an unexpected structure."
        return result

    result["Valid structure"] = True

    code_cells = [
        cell
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    ]

    result["Code cells"] = len(code_cells)

    result["Executed cells"] = sum(
        cell.get("execution_count") is not None
        for cell in code_cells
    )

    result["Cells with outputs"] = sum(
        bool(cell.get("outputs"))
        for cell in code_cells
    )

    if not code_cells:
        result["Status"] = "Review"
        result["Details"] = "No code cells were found."
    else:
        result["Status"] = "Execution not verified"
        result["Details"] = (
            "Notebook exists and has code cells. "
            "A clean execution is still required."
        )

    return result


def main():
    """Produce a readable and downloadable notebook audit."""

    results = [
        inspect_notebook(name)
        for name in EXPECTED_NOTEBOOKS
    ]

    # Include unexpected notebooks so none are silently ignored.
    if NOTEBOOKS.is_dir():
        expected = set(EXPECTED_NOTEBOOKS)

        for path in sorted(NOTEBOOKS.glob("*.ipynb")):
            if path.name not in expected:
                results.append(inspect_notebook(path.name))

    report = pd.DataFrame(results)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(OUTPUT, index=False)

    print("\nCUSTOMERINSIGHT AI — NOTEBOOK AUDIT")
    print("=" * 70)
    print(report.to_string(index=False))

    print("\nSummary")
    print(f"Notebooks inspected: {len(report)}")
    print(f"Missing: {(report['Status'] == 'Missing').sum()}")
    print(f"Invalid: {(report['Status'] == 'Invalid').sum()}")
    print(
        "Structurally valid: "
        f"{report['Valid structure'].sum()}"
    )

    print("\nImportant:")
    print(
        "This audit inspects notebook files only. "
        "It does not execute experiments or prove reproducibility."
    )

    print(f"\nSaved report: {OUTPUT}")


if __name__ == "__main__":
    main()
