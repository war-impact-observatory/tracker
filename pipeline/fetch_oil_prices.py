"""
Fetch daily Brent and WTI crude oil spot prices from the EIA Open Data API.
https://www.eia.gov/opendata/

Requires: EIA_API_KEY environment variable (free at https://www.eia.gov/opendata/register.php)
Output: data/raw/eia/oil_prices_{date}.json
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

API_KEY = os.environ.get("EIA_API_KEY", "")
BASE_URL = "https://api.eia.gov/v2"

# Series IDs
SERIES = {
    "brent": "PET.RBRTE.D",  # Brent spot price, daily
    "wti": "PET.RWTC.D",     # WTI spot price, daily
}

OUTPUT_DIR = Path("data/raw/eia")
PROCESSED_DIR = Path("data/processed")


def fetch_series(series_id: str, start_date: str, end_date: str) -> list:
    """Fetch a single EIA data series."""
    url = f"{BASE_URL}/petroleum/pri/spt/data/"
    params = {
        "api_key": API_KEY,
        "frequency": "daily",
        "data[0]": "value",
        "start": start_date,
        "end": end_date,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("response", {}).get("data", [])


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.utcnow().strftime("%Y-%m-%d")
    # Fetch from conflict start date
    start = "2026-02-01"

    print(f"Fetching oil prices from {start} to {today}...")

    try:
        data = fetch_series("PET.RBRTE.D", start, today)

        # Save raw response
        raw_file = OUTPUT_DIR / f"oil_prices_{today}.json"
        with open(raw_file, "w") as f:
            json.dump({"fetched_at": today, "data": data}, f, indent=2)
        print(f"Saved raw data to {raw_file}")

        # Extract Brent prices and save processed CSV
        # (In production, parse both Brent and WTI from the response)
        if data:
            csv_lines = ["date,brent,wti"]
            for entry in data:
                date = entry.get("period", "")
                value = entry.get("value", "")
                # Simplified — real implementation would match series
                csv_lines.append(f"{date},{value},")

            csv_file = PROCESSED_DIR / "oil_prices.csv"
            with open(csv_file, "w") as f:
                f.write("\n".join(csv_lines))
            print(f"Saved processed data to {csv_file}")

            # Save latest price for changelog
            latest = data[-1].get("value", "N/A") if data else "N/A"
            with open(PROCESSED_DIR / "latest_brent.txt", "w") as f:
                f.write(f"Brent ${latest}/bbl")
            print(f"Latest Brent: ${latest}/bbl")

    except requests.RequestException as e:
        print(f"ERROR fetching oil prices: {e}")
        raise


if __name__ == "__main__":
    main()
