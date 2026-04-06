"""
Fetch US economic indicators from FRED (Federal Reserve Economic Data).
https://fred.stlouisfed.org/

Requires: FRED_API_KEY environment variable (free at https://fred.stlouisfed.org/docs/api/api_key.html)
Output: data/raw/fred/fred_data_{date}.json
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

API_KEY = os.environ.get("FRED_API_KEY", "")
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# FRED series to track
SERIES = {
    "cpi_all": "CPIAUCSL",           # CPI for All Urban Consumers
    "gas_price": "GASREGW",           # US Regular Gasoline Price (weekly)
    "breakeven_5y": "T5YIE",          # 5-Year Breakeven Inflation Rate
    "breakeven_10y": "T10YIE",        # 10-Year Breakeven Inflation Rate
    "dollar_index": "DTWEXBGS",       # Trade Weighted Dollar Index
    "food_cpi": "CPIUFDSL",           # CPI: Food
    "energy_cpi": "CPIENGSL",         # CPI: Energy
}

OUTPUT_DIR = Path("data/raw/fred")
PROCESSED_DIR = Path("data/processed")


def fetch_fred_series(series_id: str, start_date: str) -> list:
    """Fetch a single FRED series."""
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "observation_start": start_date,
        "file_type": "json",
    }
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("observations", [])


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.utcnow().strftime("%Y-%m-%d")
    start = "2026-01-01"

    print(f"Fetching FRED data from {start} to {today}...")

    all_data = {}
    for name, series_id in SERIES.items():
        try:
            print(f"  Fetching {name} ({series_id})...")
            data = fetch_fred_series(series_id, start)
            all_data[name] = data
            print(f"    Got {len(data)} observations")
        except requests.RequestException as e:
            print(f"  ERROR fetching {name}: {e}")
            all_data[name] = []

    # Save raw response
    raw_file = OUTPUT_DIR / f"fred_data_{today}.json"
    with open(raw_file, "w") as f:
        json.dump({"fetched_at": today, "series": all_data}, f, indent=2)
    print(f"Saved raw data to {raw_file}")


if __name__ == "__main__":
    main()
