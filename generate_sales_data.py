"""Generate a reproducible synthetic sales dataset for EDA practice."""

import csv
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np


NUM_ROWS = 100_000
RANDOM_SEED = 42


def create_sales_data(output_path: Path) -> None:
    """Write 100,000 synthetic transactions with deliberate missing values."""
    rng = np.random.default_rng(RANDOM_SEED)

    products = [
        ("Laptop", "Electronics"),
        ("Headphones", "Electronics"),
        ("Smartphone", "Electronics"),
        ("Desk", "Furniture"),
        ("Chair", "Furniture"),
        ("Lamp", "Furniture"),
        ("Notebook", "Stationery"),
        ("Backpack", "Accessories"),
        ("Blender", "Appliances"),
        ("Coffee Maker", "Appliances"),
    ]
    regions = ["North", "South", "East", "West", "Central"]

    product_indices = rng.integers(0, len(products), size=NUM_ROWS)
    prices = np.round(rng.uniform(5.0, 500.0, size=NUM_ROWS), 2)
    quantities = rng.integers(1, 11, size=NUM_ROWS)

    start_date = date(2023, 1, 1)
    days_in_range = (date(2025, 1, 1) - start_date).days
    day_offsets = rng.integers(0, days_in_range, size=NUM_ROWS)
    customer_ids = rng.integers(1, 20_001, size=NUM_ROWS)
    region_indices = rng.integers(0, len(regions), size=NUM_ROWS)

    # Set exactly 5% of prices and 2% of regions to missing.
    missing_prices = np.zeros(NUM_ROWS, dtype=bool)
    missing_regions = np.zeros(NUM_ROWS, dtype=bool)
    missing_prices[rng.choice(NUM_ROWS, size=NUM_ROWS // 20, replace=False)] = True
    missing_regions[rng.choice(NUM_ROWS, size=NUM_ROWS // 50, replace=False)] = True

    columns = [
        "transaction_id",
        "customer_id",
        "product",
        "category",
        "quantity",
        "price",
        "revenue",
        "date",
        "region",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(columns)

        for index in range(NUM_ROWS):
            product, category = products[product_indices[index]]
            quantity = int(quantities[index])
            price = "" if missing_prices[index] else f"{prices[index]:.2f}"
            revenue = (
                ""
                if missing_prices[index]
                else f"{quantity * prices[index]:.2f}"
            )
            region = "" if missing_regions[index] else regions[region_indices[index]]
            transaction_date = start_date + timedelta(days=int(day_offsets[index]))

            writer.writerow(
                [
                    f"TXN{index + 1:06d}",
                    f"CUST{customer_ids[index]:05d}",
                    product,
                    category,
                    quantity,
                    price,
                    revenue,
                    transaction_date.isoformat(),
                    region,
                ]
            )


def main() -> int:
    """Write the generated dataset next to this script."""
    output_path = Path(__file__).resolve().with_name("sales_data.csv")

    try:
        create_sales_data(output_path)
    except OSError as error:
        print(f"Error saving dataset to {output_path}: {error}", file=sys.stderr)
        return 1

    print(f"Successfully created {NUM_ROWS:,} transactions.")
    print(f"Saved dataset to: {output_path}")
    print(
        "Missing values - "
        f"price: {NUM_ROWS // 20:,}, "
        f"region: {NUM_ROWS // 50:,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
