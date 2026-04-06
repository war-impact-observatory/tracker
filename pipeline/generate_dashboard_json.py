"""
Generate the dashboard_data.json consumed by the React frontend.
Reads from all processed CSVs and produces a single JSON file.
"""

import json
import csv
from pathlib import Path
from datetime import datetime

PROCESSED_DIR = Path("data/processed")


def load_csv(filename):
    """Load a CSV file and return list of dicts."""
    filepath = PROCESSED_DIR / filename
    if not filepath.exists():
        return []
    with open(filepath) as f:
        return list(csv.DictReader(f))


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    dashboard = {
        "meta": {
            "generated_at": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "conflict_start": "2026-02-28",
        },
        "oil_prices": load_csv("oil_prices.csv"),
        "household_costs": load_csv("household_costs.csv"),
    }

    # Read latest Brent
    latest_file = PROCESSED_DIR / "latest_brent.txt"
    if latest_file.exists():
        dashboard["meta"]["latest_brent"] = latest_file.read_text().strip()

    output = PROCESSED_DIR / "dashboard_data.json"
    with open(output, "w") as f:
        json.dump(dashboard, f, indent=2)

    print(f"Dashboard data generated: {output}")
    print(f"  Oil price records: {len(dashboard['oil_prices'])}")
    print(f"  Country cost records: {len(dashboard['household_costs'])}")


if __name__ == "__main__":
    main()
