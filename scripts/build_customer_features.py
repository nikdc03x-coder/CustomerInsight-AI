
from pathlib import Path

from customerinsight.retail import load_retail_data
from customerinsight.features import build_rfm, describe_rfm


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_ROOT / "data/raw/Online Retail.xlsx"
OUTPUT_PATH = PROJECT_ROOT / "data/processed/customer_rfm.csv"


def main():
    # Load the original transaction records.
    print("Loading the retail dataset...")
    transactions = load_retail_data(DATA_PATH)

    # Turn product transactions into customer-level features.
    print("Calculating customer RFM features...")
    rfm = build_rfm(transactions)

    # Save the result for future machine learning experiments.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rfm.to_csv(OUTPUT_PATH, index=False)

    print("\nCustomerInsight AI — Feature Engineering")
    print("-" * 45)
    print(f"Original transaction rows: {len(transactions):,}")
    print(f"Customers in RFM dataset: {len(rfm):,}")
    print(f"Output file: {OUTPUT_PATH}")

    print("\nRFM summary:")
    print(describe_rfm(rfm))


if __name__ == "__main__":
    main()
