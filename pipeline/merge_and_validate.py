"""
Pipeline orchestrator: merges all data sources, validates against schema,
and produces the final processed datasets.

This is the main entry point for the daily pipeline.
"""

import json
import csv
from pathlib import Path
from datetime import datetime

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
SCHEMA_DIR = Path("data/schema")


def validate_oil_prices():
    """Check oil price data for anomalies."""
    csv_file = PROCESSED_DIR / "oil_prices.csv"
    if not csv_file.exists():
        print("WARNING: oil_prices.csv not found — skipping validation")
        return False

    with open(csv_file) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("WARNING: oil_prices.csv is empty")
        return False

    # Check for reasonable price range ($20–$300)
    for row in rows:
        try:
            brent = float(row.get("brent", 0) or 0)
            if brent > 0 and (brent < 20 or brent > 300):
                print(f"WARNING: Brent price {brent} outside reasonable range at {row.get('date')}")
        except ValueError:
            pass

    print(f"Oil prices validated: {len(rows)} records")
    return True


def validate_household_costs():
    """Check household cost estimates for reasonableness."""
    csv_file = PROCESSED_DIR / "household_costs.csv"
    if not csv_file.exists():
        print("WARNING: household_costs.csv not found — skipping validation")
        return False

    with open(csv_file) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        cost = float(row.get("household_cost_usd", 0))
        if cost < 0 or cost > 10000:
            print(f"WARNING: Household cost for {row['country']} = ${cost} — outside expected range")

    print(f"Household costs validated: {len(rows)} countries")
    return True


def generate_summary():
    """Generate a summary JSON with key metrics."""
    summary = {
        "last_updated": datetime.utcnow().isoformat(),
        "pipeline_version": "1.0.0",
        "data_files": [],
    }

    for f in PROCESSED_DIR.glob("*.csv"):
        with open(f) as csvf:
            row_count = sum(1 for _ in csv.reader(csvf)) - 1
        summary["data_files"].append({
            "file": f.name,
            "rows": row_count,
            "updated": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })

    summary_file = PROCESSED_DIR / "pipeline_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Pipeline summary saved to {summary_file}")


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"WAR IMPACT OBSERVATORY — Data Pipeline")
    print(f"Run at: {datetime.utcnow().isoformat()} UTC")
    print("=" * 60)

    # Validate each data source
    print("\n--- Validating oil prices ---")
    validate_oil_prices()

    print("\n--- Validating household costs ---")
    validate_household_costs()

    print("\n--- Generating summary ---")
    generate_summary()

    print("\n" + "=" * 60)
    print("Pipeline complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
