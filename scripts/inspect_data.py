
from pathlib import Path

from customerinsight.data import (
    describe_transactions,
    load_transactions,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data/sample/demo_transactions.csv"


def main():
    # Check our sample data before introducing a real dataset.
    transactions = load_transactions(DATA_PATH)
    summary = describe_transactions(transactions)

    print("\nCustomerInsight AI — Dataset Inspection")
    print("-" * 42)

    for name, value in summary.items():
        label = name.replace("_", " ").title()
        print(f"{label}: {value}")


if __name__ == "__main__":
    main()
