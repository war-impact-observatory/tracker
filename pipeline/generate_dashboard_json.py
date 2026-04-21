"""
Generate data/processed/country_data.json — the live data file consumed by the dashboard.

Also generates data/processed/oil_price_history.json — the full Brent/WTI timeline used
by the oil price chart (dynamically fetched, replaces hardcoded chart data in index.html).

Merges:
  data/baseline/countries.json    — research-based fixed values (inflImpact, gdpHit, etc.)
  data/processed/computed_metrics.json — daily computed values (fuelUp, currencyChg, householdCost)

Output:
  data/processed/country_data.json
  data/processed/oil_price_history.json
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


def generate_oil_price_history():
    """
    Build data/processed/oil_price_history.json from:
      - Hardcoded pre-history series (Feb 27 – Apr 6, before daily snapshots began)
      - data/history/YYYY-MM-DD.json files for Apr 7 onwards
    WTI is approximated as Brent − 5.
    """
    PRE_HISTORY = [
        {"date": "Feb 27", "iso": "2026-02-27", "brent": 70,  "wti": 65,  "event": "Pre-conflict baseline ($70)"},
        {"date": "Feb 28", "iso": "2026-02-28", "brent": 80,  "wti": 75,  "event": "US-Israel strikes begin"},
        {"date": "Mar 1",  "iso": "2026-03-01", "brent": 82,  "wti": 77},
        {"date": "Mar 4",  "iso": "2026-03-04", "brent": 91,  "wti": 86,  "event": "Hormuz closure announced"},
        {"date": "Mar 7",  "iso": "2026-03-07", "brent": 98,  "wti": 93},
        {"date": "Mar 8",  "iso": "2026-03-08", "brent": 103, "wti": 98,  "event": "Brent crosses $100"},
        {"date": "Mar 10", "iso": "2026-03-10", "brent": 108, "wti": 102, "event": "Gulf production −6.7M bpd"},
        {"date": "Mar 12", "iso": "2026-03-12", "brent": 115, "wti": 108, "event": "Production −10M bpd (IEA)"},
        {"date": "Mar 15", "iso": "2026-03-15", "brent": 119, "wti": 112},
        {"date": "Mar 19", "iso": "2026-03-19", "brent": 126, "wti": 118, "event": "Brent peak — $126/bbl"},
        {"date": "Mar 23", "iso": "2026-03-23", "brent": 104, "wti": 97,  "event": "Trump 5-day pause"},
        {"date": "Mar 25", "iso": "2026-03-25", "brent": 109, "wti": 102},
        {"date": "Mar 30", "iso": "2026-03-30", "brent": 116, "wti": 108, "event": "US gas hits $4/gal"},
        {"date": "Apr 2",  "iso": "2026-04-02", "brent": 112, "wti": 105},
    ]

    EVENTS = {
        "2026-04-07": "Pre-ceasefire high",
        "2026-04-08": "US-Iran ceasefire — Brent ↓$31",
    }
    # Manual price corrections: history snapshots that captured wrong API values
    # Format: "YYYY-MM-DD" -> correct_brent_price
    PRICE_CORRECTIONS = {
        "2026-04-08": 95.0,  # ceasefire day — daily snapshot ran before override was in place
    }

    series = list(PRE_HISTORY)

    # Append daily history snapshots (sorted by date)
    history_files = sorted(HISTORY_DIR.glob("2026-*.json"))
    for hf in history_files:
        iso = hf.stem   # e.g. "2026-04-07"
        data = load_json(hf)
        if not data or "brent_price" not in data:
            continue
        brent = round(PRICE_CORRECTIONS.get(iso, data["brent_price"]), 1)
        wti   = round(brent - 5, 1)
        # Format display date: "Apr 7"
        from datetime import date as _date
        dt = _date.fromisoformat(iso)
        display = dt.strftime("%b %-d")   # "Apr 7" on Linux/Mac; use %#d on Windows
        point = {"date": display, "iso": iso, "brent": brent, "wti": wti}
        if iso in EVENTS:
            point["event"] = EVENTS[iso]
        series.append(point)

    out = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "series": series,
    }
    out_path = PROCESSED_DIR / "oil_price_history.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"  Oil price history: {len(series)} points → {out_path}")


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
    # Read brent_baseline from computed_metrics (set by config.BASELINE_BRENT) — never hardcode
    brent_baseline = (computed or {}).get("brent_baseline", 70.0)

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

    # Also regenerate the oil price history (chart timeline)
    generate_oil_price_history()


if __name__ == "__main__":
    main()
