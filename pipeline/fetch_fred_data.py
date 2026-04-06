"""
Fetch US economic indicators from FRED (Federal Reserve Economic Data).
https://fred.stlouisfed.org/

Free API key at: https://fred.stlouisfed.org/docs/api/api_key.html
Set env var: FRED_API_KEY

Fetches monthly CPI and weekly gas prices for US calibration.
Output: data/raw/fred_data.json
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
FRED_URL     = "https://api.stlouisfed.org/fred/series/observations"
OUTPUT_DIR   = Path("data/raw")

# FRED series to track
SERIES = {
    "us_cpi":       "CPIAUCSL",    # US CPI All Urban Consumers (monthly)
    "us_gas":       "GASREGW",     # US Regular Gasoline Price Weekly ($/gallon)
    "us_food_cpi":  "CPIUFDSL",    # US CPI Food (monthly)
    "us_energy_cpi":"CPIENGSL",    # US CPI Energy (monthly)
    "usd_index":    "DTWEXBGS",    # Trade Weighted USD Index (daily)
}


def fetch_series(series_id: str, limit: int = 3) -> list:
    """Fetch the last N observations of a FRED series."""
    if not FRED_API_KEY:
        return []
    params = {
        "series_id":  series_id,
        "api_key":    FRED_API_KEY,
        "file_type":  "json",
        "sort_order": "desc",
        "limit":      limit,
    }
    resp = requests.get(FRED_URL, params=params, timeout=20)
    resp.raise_for_status()
    obs = resp.json().get("observations", [])
    # Filter out missing values
    return [o for o in obs if o.get("value") not in (".", "")]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not FRED_API_KEY:
        print("WARNING: FRED_API_KEY not set — skipping FRED fetch")
        empty = {
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "note": "FRED_API_KEY not set",
            "series": {},
        }
        with open(OUTPUT_DIR / "fred_data.json", "w") as f:
            json.dump(empty, f, indent=2)
        return

    print("Fetching FRED economic indicators...")
    result = {"fetched_at": datetime.utcnow().isoformat() + "Z", "series": {}}

    for name, series_id in SERIES.items():
        try:
            obs = fetch_series(series_id, limit=3)
            result["series"][name] = obs
            val = obs[0]["value"] if obs else "N/A"
            print(f"  {name} ({series_id}): latest = {val}")
        except Exception as e:
            print(f"  WARNING: {name} failed — {e}")
            result["series"][name] = []

    out = OUTPUT_DIR / "fred_data.json"
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()
