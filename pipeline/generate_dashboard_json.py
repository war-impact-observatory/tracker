"""
Generate data/processed/country_data.json — the live data file consumed by the dashboard.

Merges:
  data/baseline/countries.json    — research-based fixed values (inflImpact, gdpHit, etc.)
  data/processed/computed_metrics.json — daily computed values (fuelUp, currencyChg, householdCost)

Output:
  data/processed/country_data.json

The dashboard (index.html) fetches this file on load and updates the hardcoded fallback data.
If this file is missing or stale, the dashboard falls back to its embedded data silently.
"""

import json
from datetime import datetime
from pathlib import Path

BASELINE_DIR  = Path("data/baseline")
PROCESSED_DIR = Path("data/processed")
HISTORY_DIR   = Path("data/history")
RAW_DIR       = Path("data/raw")


def load_json(path: Path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def round1(x):
    try:
        return round(float(x), 1)
    except (TypeError, ValueError):
        return x


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    baseline_countries = load_json(BASELINE_DIR / "countries.json")
    computed           = load_json(PROCESSED_DIR / "computed_metrics.json")
    oil_data           = load_json(RAW_DIR / "oil_prices.json")

    if not baseline_countries:
        print("ERROR: data/baseline/countries.json not found")
        return

    computed_by_country = {}
    if computed and "countries" in computed:
        computed_by_country = computed["countries"]

    brent_price    = (oil_data or {}).get("brent_usd", 126.0)
    brent_baseline = 73.0

    countries_out = []
    for b in baseline_countries:
        country = b["country"]
        live    = computed_by_country.get(country, {})

        fuel_up        = round1(live.get("fuelUp",       b.get("fuelUp",       0)))
        currency_chg   = round1(live.get("currencyChg",  b.get("currencyChg",  0)))
        household_cost = int(live.get("householdCost",   b.get("householdCost", 0)))

        entry = {
            "country":       b["country"],
            "flag":          b["flag"],
            "oilDep":        b["oilDep"],
            "inflImpact":    b["inflImpact"],
            "gdpHit":        b["gdpHit"],
            "avgIncomePPP":  b["avgIncomePPP"],
            "foodUp":        b["foodUp"],
            "severity":      b["severity"],
            "ffShare":       b["ffShare"],
            "fuelUp":        fuel_up,
            "currencyChg":   currency_chg,
            "householdCost": household_cost,
        }
        if b.get("participant"):
            entry["participant"] = True

        countries_out.append(entry)

    critical_count = sum(1 for c in countries_out if c["severity"] == "critical")
    avg_inflation  = round(sum(c["inflImpact"] for c in countries_out) / len(countries_out), 2)

    output = {
        "generated_at":   datetime.utcnow().isoformat() + "Z",
        "brent_price":    brent_price,
        "brent_baseline": brent_baseline,
        "oil_change_pct": round1((brent_price - brent_baseline) / brent_baseline * 100),
        "summary": {
            "total_countries":      len(countries_out),
            "critical_countries":   critical_count,
            "avg_inflation_impact": avg_inflation,
        },
        "countries": countries_out,
    }

    # Write live dashboard file
    out_path = PROCESSED_DIR / "country_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Archive daily snapshot to data/history/YYYY-MM-DD.json
    # This powers the newsletter trend comparisons and future API/paid data products
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    today_str   = datetime.utcnow().strftime("%Y-%m-%d")
    history_path = HISTORY_DIR / f"{today_str}.json"
    if not history_path.exists():   # don't overwrite if already ran today
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"  History snapshot saved: {history_path}")
    else:
        print(f"  History snapshot already exists for {today_str} — skipped")

    print(f"Dashboard JSON generated: {out_path}")
    print(f"  Countries: {len(countries_out)}  |  Critical: {critical_count}")
    print(f"  Brent: ${brent_price}/bbl (+{output['oil_change_pct']}% vs baseline)")
    print(f"  Generated at: {output['generated_at']}")


if __name__ == "__main__":
    main()
