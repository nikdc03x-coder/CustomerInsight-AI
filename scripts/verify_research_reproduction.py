
"""Verify saved experiment comparisons and notebook execution evidence."""

from pathlib import Path

import nbformat
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/reproducibility"

COMPARISON_FILE = RESULTS / "model_validation_comparison.csv"

NOTEBOOKS = {
    "Customer Explainability": (
        RESULTS / "customer_explainability_executed.ipynb"
    ),
    "Model Validation": (
        RESULTS / "model_validation_executed.ipynb"
    ),
}


def check_model_validation():
    """Inspect the actual 18-configuration comparison results."""

    print("\nMODEL VALIDATION REPRODUCTION")
    print("=" * 65)

    if not COMPARISON_FILE.is_file():
        print("NOT VERIFIED: Comparison CSV is missing.")
        return False

    data = pd.read_csv(COMPARISON_FILE)

    required = {
        "preprocessing",
        "clusters",
        "reproduced_successfully",
        "silhouette_difference",
        "inertia_difference",
        "ari_vs_baseline_difference",
    }

    missing = required - set(data.columns)

    if missing:
        print("NOT VERIFIED: Missing columns:", sorted(missing))
        return False

    if len(data) != 18:
        print(f"NOT VERIFIED: Expected 18 rows, found {len(data)}.")
        return False

    if data.duplicated(["preprocessing", "clusters"]).any():
        print("NOT VERIFIED: Duplicate experiment configurations.")
        return False

    # Read saved pass/fail values without treating missing values as passing.
    values = (
        data["reproduced_successfully"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    passed = values.eq("true").fillna(False)

    print("Configurations:", len(data))
    print("Passed:", int(passed.sum()))
    print("Failed:", int((~passed).sum()))

    for metric in [
        "silhouette_difference",
        "inertia_difference",
        "ari_vs_baseline_difference",
    ]:
        numeric = pd.to_numeric(data[metric], errors="coerce")
        if numeric.isna().any():
            print(f"INVALID: {metric} contains missing/non-numeric values.")
            return False

        print(f"Maximum {metric}: {numeric.max():.10f}")

    if not passed.all():
        print("\nConfigurations requiring investigation:")
        print(
            data.loc[
                ~passed,
                [
                    "preprocessing",
                    "clusters",
                    "silhouette_difference",
                    "inertia_difference",
                    "ari_vs_baseline_difference",
                ],
            ].to_string(index=False)
        )
        return False

    print("\nRESULT: All 18 saved comparison checks passed.")
    return True


def check_notebook(title, path):
    """Check execution counts and recorded notebook errors."""

    print(f"\n{title.upper()}")
    print("=" * 65)

    if not path.is_file():
        print("NOT VERIFIED: Executed notebook not found.")
        return False

    try:
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
    except (OSError, ValueError) as error:
        print("INVALID NOTEBOOK:", error)
        return False

    code_cells = [
        cell
        for cell in notebook.cells
        if cell.cell_type == "code"
    ]

    errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.output_type == "error"
    ]

    executed_count = sum(
        cell.execution_count is not None
        for cell in code_cells
    )

    print("Code cells:", len(code_cells))
    print("Executed cells:", executed_count)
    print("Recorded errors:", len(errors))

    for error in errors:
        print(error.get("ename"), error.get("evalue"))

    success = (
        bool(code_cells)
        and executed_count == len(code_cells)
        and not errors
    )

    if success:
        print("RESULT: Saved notebook execution completed without errors.")
    else:
        print("RESULT: Notebook execution evidence is incomplete.")

    return success


def main():
    """Print verification results without modifying research files."""

    validation_ok = check_model_validation()

    notebook_results = {
        name: check_notebook(name, path)
        for name, path in NOTEBOOKS.items()
    }

    print("\nFINAL VERIFICATION SUMMARY")
    print("=" * 65)

    print(
        "Model validation comparison:",
        "PASSED" if validation_ok else "NOT VERIFIED",
    )

    for name, passed in notebook_results.items():
        print(
            f"{name} notebook:",
            "PASSED" if passed else "NOT VERIFIED",
        )

    print(
        "\nNote: Notebook execution without errors does not "
        "prove numerical reproduction of its findings."
    )

    if not validation_ok or not all(notebook_results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
