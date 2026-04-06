"""
Compute estimated additional annual household costs per country using
IMF oil-price pass-through coefficients.

Model:
  household_cost = oil_price_delta * pass_through_coef * avg_energy_spend * (1 - subsidy_offset)

Coefficients sourced from:
  - IMF Working Paper WP/16/210: "How Much Do Global Oil Prices Affect Food Prices?"
  - IMF Regional Economic Outlooks (energy pass-through by region)
  - National statistical agencies for average household energy expenditure

Output: data/processed/household_costs.csv
"""

import json
import csv
from pathlib import Path
from datetime import datetime

PROCESSED_DIR = Path("data/processed")

# Pre-conflict Brent baseline (7-day avg ending Feb 27, 2026)
BASELINE_BRENT = 73.0

# Country-specific parameters
# pass_through: fraction of oil price increase that reaches consumer prices (0-1)
# avg_energy_spend: annual household energy expenditure in USD
# subsidy_offset: government subsidy absorption (0-1, where 1 = full subsidy)
COUNTRY_PARAMS = {
    "United States":   {"pass_through": 0.65, "avg_energy_spend": 5200, "subsidy_offset": 0.0, "oil_import_pct": 0.40},
    "China":           {"pass_through": 0.45, "avg_energy_spend": 2800, "subsidy_offset": 0.10, "oil_import_pct": 0.72},
    "India":           {"pass_through": 0.60, "avg_energy_spend": 1200, "subsidy_offset": 0.15, "oil_import_pct": 0.85},
    "Japan":           {"pass_through": 0.70, "avg_energy_spend": 4800, "subsidy_offset": 0.05, "oil_import_pct": 0.90},
    "Germany":         {"pass_through": 0.75, "avg_energy_spend": 5600, "subsidy_offset": 0.0, "oil_import_pct": 0.65},
    "United Kingdom":  {"pass_through": 0.70, "avg_energy_spend": 4800, "subsidy_offset": 0.0, "oil_import_pct": 0.46},
    "France":          {"pass_through": 0.60, "avg_energy_spend": 4200, "subsidy_offset": 0.0, "oil_import_pct": 0.98},
    "Brazil":          {"pass_through": 0.50, "avg_energy_spend": 1400, "subsidy_offset": 0.10, "oil_import_pct": 0.12},
    "Canada":          {"pass_through": 0.65, "avg_energy_spend": 5000, "subsidy_offset": 0.0, "oil_import_pct": 0.10},
    "Australia":       {"pass_through": 0.65, "avg_energy_spend": 4200, "subsidy_offset": 0.0, "oil_import_pct": 0.58},
    "South Korea":     {"pass_through": 0.70, "avg_energy_spend": 3800, "subsidy_offset": 0.0, "oil_import_pct": 0.93},
    "Italy":           {"pass_through": 0.72, "avg_energy_spend": 4800, "subsidy_offset": 0.0, "oil_import_pct": 0.70},
    "Mexico":          {"pass_through": 0.45, "avg_energy_spend": 1800, "subsidy_offset": 0.15, "oil_import_pct": 0.30},
    "Indonesia":       {"pass_through": 0.40, "avg_energy_spend": 800, "subsidy_offset": 0.25, "oil_import_pct": 0.65},
    "Turkey":          {"pass_through": 0.75, "avg_energy_spend": 1200, "subsidy_offset": 0.0, "oil_import_pct": 0.93},
    "Saudi Arabia":    {"pass_through": 0.20, "avg_energy_spend": 3600, "subsidy_offset": 0.50, "oil_import_pct": 0.0},
    "Argentina":       {"pass_through": 0.55, "avg_energy_spend": 800, "subsidy_offset": 0.10, "oil_import_pct": 0.15},
    "South Africa":    {"pass_through": 0.65, "avg_energy_spend": 900, "subsidy_offset": 0.0, "oil_import_pct": 0.95},
    "Russia":          {"pass_through": 0.25, "avg_energy_spend": 1200, "subsidy_offset": 0.30, "oil_import_pct": 0.0},
}


def compute_cost(current_brent: float, params: dict) -> float:
    """Compute additional annual household cost for a country."""
    oil_delta_pct = (current_brent - BASELINE_BRENT) / BASELINE_BRENT
    cost = (
        oil_delta_pct
        * params["pass_through"]
        * params["avg_energy_spend"]
        * (1 - params["subsidy_offset"])
    )
    return round(max(cost, 0), 0)


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Read latest Brent price
    latest_file = PROCESSED_DIR / "latest_brent.txt"
    if latest_file.exists():
        text = latest_file.read_text().strip()
        # Parse "Brent $113/bbl" format
        current_brent = float(text.split("$")[1].split("/")[0])
    else:
        # Fallback to hardcoded current
        current_brent = 113.0

    print(f"Computing household costs at Brent = ${current_brent}/bbl (baseline: ${BASELINE_BRENT})")
    print(f"Oil price delta: +{((current_brent - BASELINE_BRENT) / BASELINE_BRENT * 100):.1f}%")

    rows = []
    for country, params in COUNTRY_PARAMS.items():
        cost = compute_cost(current_brent, params)
        rows.append({
            "country": country,
            "household_cost_usd": cost,
            "brent_price": current_brent,
            "oil_import_pct": params["oil_import_pct"],
            "pass_through": params["pass_through"],
            "subsidy_offset": params["subsidy_offset"],
            "computed_at": datetime.utcnow().isoformat(),
        })
        print(f"  {country}: ${cost}/yr")

    # Save CSV
    csv_file = PROCESSED_DIR / "household_costs.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved to {csv_file}")


if __name__ == "__main__":
    main()
