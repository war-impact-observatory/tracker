"""
Fetch daily Brent crude oil price from FRED (Federal Reserve Economic Data).
FRED series: DCOILBRENTEU — Brent Crude Oil Spot Price (USD/barrel, daily)

Free API key at: https://fred.stlouisfed.org/docs/api/api_key.html
Set env var: FRED_API_KEY

Output: data/raw/oil_prices.json
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
FRED_URL     = "https://api.stlouisfed.org/fred/series/observations"
BRENT_SERIES = "DCOILBRENTEU"

OUTPUT_DIR   = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def fetch_brent_fred() -> dict | None:
    """Fetch latest Brent price from FRED. Returns dict with brent_usd + date."""
    if not FRED_API_KEY:
        print("WARNING: FRED_API_KEY not set — skipping FRED fetch")
        return None

    params = {
        "series_id":   BRENT_SERIES,
        "api_key":     FRED_API_KEY,
        "file_type":   "json",
        "sort_order":  "desc",
        "limit":       5,          # grab last 5 trading days (handles weekends/holidays)
    }
    resp = requests.get(FRED_URL, params=params, timeout=20)
    resp.raise_for_status()
    obs = resp.json().get("observations", [])

    for o in obs:
        if o["value"] not in (".", ""):
            return {
                "brent_usd": round(float(o["value"]), 2),
                "date":      o["date"],
                "source":    "FRED/DCOILBRENTEU",
            }
    return None


def fetch_brent_eia() -> dict | None:
    """Fallback: fetch Brent from EIA Open Data API (requires EIA_API_KEY)."""
    eia_key = os.environ.get("EIA_API_KEY", "")
    if not eia_key:
        return None

    url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
    params = {
        "api_key":             eia_key,
        "frequency":           "daily",
        "data[0]":             "value",
        "facets[series][]":    "RBRTE",
        "sort[0][column]":     "period",
        "sort[0][direction]":  "desc",
        "length":              5,
    }
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json().get("response", {}).get("data", [])
        for row in data:
            if row.get("value") not in (None, ""):
                return {
                    "brent_usd": round(float(row["value"]), 2),
                    "date":      row["period"],
                    "source":    "EIA/RBRTE",
                }
    except Exception as e:
        print(f"EIA fallback failed: {e}")
    return None


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching Brent crude oil price...")
    result = fetch_brent_fred() or fetch_brent_eia()

    if result:
        result["fetched_at"] = datetime.utcnow().isoformat() + "Z"
        out = OUTPUT_DIR / "oil_prices.json"
        with open(out, "w") as f:
            json.dump(result, f, indent=2)
        print(f"  Brent: ${result['brent_usd']}/bbl on {result['date']} [{result['source']}]")

        # Also write the changelog text file
        with open(PROCESSED_DIR / "latest_brent.txt", "w") as f:
            f.write(f"Brent ${result['brent_usd']}/bbl")
    else:
        print("  WARNING: Could not fetch live oil price — using hardcoded fallback")
        result = {
            "brent_usd":  126.0,
            "date":       datetime.utcnow().strftime("%Y-%m-%d"),
            "source":     "FALLBACK",
            "fetched_at": datetime.utcnow().isoformat() + "Z",
        }
        out = OUTPUT_DIR / "oil_prices.json"
        with open(out, "w") as f:
            json.dump(result, f, indent=2)
        with open(PROCESSED_DIR / "latest_brent.txt", "w") as f:
            f.write(f"Brent ${result['brent_usd']}/bbl (fallback)")


if __name__ == "__main__":
    main()
