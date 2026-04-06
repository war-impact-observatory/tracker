"""
Fetch daily exchange rates from the ECB (European Central Bank).
Uses the free daily XML reference rate feed — no API key required.
https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml

All rates are quoted as: 1 EUR = N local currency units.
Output: data/raw/exchange_rates.json
"""

import json
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from pathlib import Path

ECB_XML_URL  = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
OUTPUT_DIR   = Path("data/raw")


def fetch_ecb_rates() -> dict | None:
    """
    Parse ECB daily XML and return a dict:
      { "date": "2026-04-04", "eur_usd": 1.092, "rates": {"USD": 1.092, "INR": 93.2, ...} }
    """
    headers = {"User-Agent": "WarImpactObservatory/1.0 (sumitb1808@gmail.com)"}
    resp = requests.get(ECB_XML_URL, headers=headers, timeout=20)
    resp.raise_for_status()

    ns = {
        "gesmes": "http://www.gesmes.org/xml/2002-08-01",
        "ecb":    "http://www.ecb.int/vocabulary/2002-08-01/eurofxref",
    }
    root = ET.fromstring(resp.content)

    # Find the <Cube time="..."> element
    cube_time = root.find(".//ecb:Cube[@time]", ns)
    if cube_time is None:
        return None

    rate_date = cube_time.attrib.get("time", datetime.utcnow().strftime("%Y-%m-%d"))
    rates = {}
    for cube in cube_time.findall("ecb:Cube", ns):
        currency = cube.attrib.get("currency")
        rate_str = cube.attrib.get("rate")
        if currency and rate_str:
            try:
                rates[currency] = float(rate_str)
            except ValueError:
                pass

    eur_usd = rates.get("USD", 1.085)
    return {
        "date":       rate_date,
        "eur_usd":    eur_usd,
        "rates":      rates,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "source":     "ECB/eurofxref-daily",
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching ECB exchange rates...")
    try:
        result = fetch_ecb_rates()
        if result:
            out = OUTPUT_DIR / "exchange_rates.json"
            with open(out, "w") as f:
                json.dump(result, f, indent=2)
            print(f"  Rates for {result['date']}: {len(result['rates'])} currencies fetched")
            print(f"  EUR/USD = {result['eur_usd']}")
        else:
            print("  WARNING: Failed to parse ECB XML — saving empty fallback")
            fallback = {
                "date":       datetime.utcnow().strftime("%Y-%m-%d"),
                "eur_usd":    1.085,
                "rates":      {},
                "fetched_at": datetime.utcnow().isoformat() + "Z",
                "source":     "FALLBACK",
            }
            with open(OUTPUT_DIR / "exchange_rates.json", "w") as f:
                json.dump(fallback, f, indent=2)
    except Exception as e:
        print(f"  ERROR: {e}")
        fallback = {
            "date":       datetime.utcnow().strftime("%Y-%m-%d"),
            "eur_usd":    1.085,
            "rates":      {},
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "source":     "FALLBACK",
        }
        out = OUTPUT_DIR / "exchange_rates.json"
        with open(out, "w") as f:
            json.dump(fallback, f, indent=2)


if __name__ == "__main__":
    main()
