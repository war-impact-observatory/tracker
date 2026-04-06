"""
Fetch daily exchange rates from the ECB Statistical Data Warehouse (SDMX API).
https://sdw-wsrest.ecb.europa.eu/

No API key required. Free and open.
Output: data/raw/ecb/exchange_rates_{date}.json
"""

import json
import requests
from datetime import datetime
from pathlib import Path

BASE_URL = "https://sdw-wsrest.ecb.europa.eu/service"

# Key currencies to track (vs EUR)
CURRENCIES = ["USD", "GBP", "JPY", "CNY", "INR", "TRY", "ZAR", "BRL", "KRW", "IDR", "MXN", "AUD", "CAD", "SAR", "RUB", "ARS"]

OUTPUT_DIR = Path("data/raw/ecb")
PROCESSED_DIR = Path("data/processed")


def fetch_ecb_rates(start_date: str, end_date: str) -> dict:
    """Fetch exchange rates from ECB SDMX API."""
    currency_str = "+".join(CURRENCIES)
    url = f"{BASE_URL}/data/EXR/D.{currency_str}.EUR.SP00.A"
    params = {
        "startPeriod": start_date,
        "endPeriod": end_date,
        "format": "jsondata",
    }
    headers = {"Accept": "application/json"}
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.utcnow().strftime("%Y-%m-%d")
    start = "2026-02-01"

    print(f"Fetching ECB exchange rates from {start} to {today}...")

    try:
        data = fetch_ecb_rates(start, today)

        # Save raw response
        raw_file = OUTPUT_DIR / f"exchange_rates_{today}.json"
        with open(raw_file, "w") as f:
            json.dump({"fetched_at": today, "data": data}, f, indent=2)
        print(f"Saved raw data to {raw_file}")

        # Process into CSV (simplified — real implementation would parse SDMX structure)
        print("Exchange rate data fetched successfully.")

    except requests.RequestException as e:
        print(f"ERROR fetching exchange rates: {e}")
        raise


if __name__ == "__main__":
    main()
