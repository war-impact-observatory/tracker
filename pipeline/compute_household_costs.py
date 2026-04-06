"""
Compute updated per-country metrics from live oil prices and exchange rates.

For each country, calculates:
  fuelUp      — retail fuel price increase % (from oil price change × pass-through coeff)
  currencyChg — % change of local currency vs USD since pre-conflict baseline
  householdCost — estimated extra annual household cost in USD

Reads:
  data/raw/oil_prices.json
  data/raw/exchange_rates.json
  data/baseline/countries.json

Writes:
  data/processed/computed_metrics.json
"""

import json
from datetime import datetime
from pathlib import Path

from config import (
    BASELINE_BRENT,
    BASELINE_EUR_RATES,
    COUNTRY_CONFIG,
    FOOD_WEIGHT,
    FUEL_WEIGHT,
)

RAW_DIR      = Path("data/raw")
BASELINE_DIR = Path("data/baseline")
PROCESSED_DIR = Path("data/processed")


def load_json(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def get_current_usd_rate(currency: str, eur_rates: dict, eur_usd: float) -> float | None:
    """
    Convert ECB's EUR/currency rate to USD/currency.
    Returns how many local units = 1 USD.
    """
    if currency == "USD":
        return 1.0
    if currency == "EUR":
        return 1.0 / eur_usd  # EUR per USD = 1/eur_usd → USD per EUR = eur_usd

    eur_per_local = eur_rates.get(currency)
    if not eur_per_local:
        return None
    # USD per local = (EUR per local) / (EUR per USD) = eur_per_local / eur_usd
    # USD/local means how many local units buy 1 USD
    # eur_rates[currency] = local units per 1 EUR
    # eur_usd = USD per 1 EUR
    # → local per 1 USD = eur_per_local / eur_usd
    return eur_per_local / eur_usd


def compute_currency_change(country: str, cfg: dict, eur_rates: dict, eur_usd: float) -> float:
    """
    Compute % change of local currency vs USD since baseline.
    Negative = local currency weakened (more local units per USD).
    Positive = local currency strengthened.
    """
    currency = cfg["currency"]
    if currency in ("IRR", "LBP", "SYP", "YER"):
        # Not tracked by ECB — return 0 (keep baseline value from countries.json)
        return None

    # Baseline: how many local units per 1 USD (pre-conflict)
    baseline_eur_local = BASELINE_EUR_RATES.get(currency)
    baseline_eur_usd   = BASELINE_EUR_RATES.get("USD", 1.085)
    if not baseline_eur_local:
        return None

    if currency == "EUR":
        # EUR/USD change
        current_eur_usd = eur_usd
        baseline_eur_usd_val = baseline_eur_usd
        # Positive = EUR strengthened vs USD
        return round((current_eur_usd - baseline_eur_usd_val) / baseline_eur_usd_val * 100, 1)

    # baseline local per USD
    baseline_local_per_usd = baseline_eur_local / baseline_eur_usd

    # current EUR/currency from ECB
    current_eur_local = eur_rates.get(currency)
    if not current_eur_local:
        return None

    current_local_per_usd = current_eur_local / eur_usd

    # If local_per_usd went UP, local currency WEAKENED → negative
    change = -(current_local_per_usd - baseline_local_per_usd) / baseline_local_per_usd * 100
    return round(change, 1)


def compute_fuel_up(oil_change_pct: float, pass_through: float) -> float:
    """Retail fuel price increase % from oil price change."""
    return round(oil_change_pct * pass_through, 1)


def compute_household_cost(baseline: dict, fuel_up: float) -> int:
    """
    Estimated extra annual household cost in USD.
    Formula: avgIncomePPP × (ffShare/100) × weighted_price_increase
    where weighted_price_increase = FOOD_WEIGHT×foodUp + FUEL_WEIGHT×fuelUp (all /100)
    """
    income   = baseline.get("avgIncomePPP", 0)
    ff_share = baseline.get("ffShare", 0)
    food_up  = baseline.get("foodUp", 0)

    weighted = (FOOD_WEIGHT * food_up + FUEL_WEIGHT * fuel_up) / 100
    cost = income * (ff_share / 100) * weighted
    return max(0, round(cost))


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Load raw data
    oil_data  = load_json(RAW_DIR / "oil_prices.json")
    fx_data   = load_json(RAW_DIR / "exchange_rates.json")
    baseline_countries = load_json(BASELINE_DIR / "countries.json")

    current_brent = oil_data.get("brent_usd", BASELINE_BRENT)
    eur_rates     = fx_data.get("rates", {})
    eur_usd       = fx_data.get("eur_usd", BASELINE_EUR_RATES["USD"])

    oil_change_pct = (current_brent - BASELINE_BRENT) / BASELINE_BRENT * 100
    print(f"Brent: ${current_brent}/bbl  |  Change from baseline: +{oil_change_pct:.1f}%")
    print(f"EUR/USD: {eur_usd}")

    metrics = {}
    for baseline in baseline_countries:
        country = baseline["country"]
        cfg = COUNTRY_CONFIG.get(country, {})
        if not cfg:
            print(f"  WARNING: No config for {country} — skipping")
            continue

        pass_through = cfg.get("passThrough", 0.4)
        fuel_up      = compute_fuel_up(oil_change_pct, pass_through)
        currency_chg = compute_currency_change(country, cfg, eur_rates, eur_usd)
        if currency_chg is None:
            # Keep baseline value for countries ECB doesn't track
            currency_chg = baseline.get("currencyChg", 0.0)

        household_cost = compute_household_cost(baseline, fuel_up)

        metrics[country] = {
            "fuelUp":        fuel_up,
            "currencyChg":   currency_chg,
            "householdCost": household_cost,
        }
        print(f"  {country}: fuelUp={fuel_up}%  currChg={currency_chg}%  cost=${household_cost}")

    result = {
        "generated_at":    datetime.utcnow().isoformat() + "Z",
        "brent_price":     current_brent,
        "brent_baseline":  BASELINE_BRENT,
        "oil_change_pct":  round(oil_change_pct, 1),
        "eur_usd":         eur_usd,
        "countries":       metrics,
    }

    out = PROCESSED_DIR / "computed_metrics.json"
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved computed metrics for {len(metrics)} countries → {out}")


if __name__ == "__main__":
    main()
