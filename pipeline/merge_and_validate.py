"""
Validate all pipeline outputs before generating the final dashboard JSON.
Checks for:
  - Required files present
  - Oil price in a plausible range ($20–$400)
  - At least 20 countries computed
  - No NaN / null values in key fields
  - Currency changes within plausible bounds

Exits with code 1 if any critical validation fails.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

PROCESSED_DIR = Path("data/processed")
RAW_DIR       = Path("data/raw")
BASELINE_DIR  = Path("data/baseline")

REQUIRED_FILES = [
    RAW_DIR / "oil_prices.json",          # critical
    BASELINE_DIR / "countries.json",       # critical
    PROCESSED_DIR / "computed_metrics.json",  # critical
]
OPTIONAL_FILES = [
    RAW_DIR / "exchange_rates.json",      # non-critical; fallback to baseline rates
]

BRENT_MIN, BRENT_MAX       = 30.0, 250.0   # tightened from 20–400
BRENT_MAX_DAILY_CHANGE_PCT = 25.0           # >25% single-day swing = suspect
MIN_COUNTRIES         = 20


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def check_required_files() -> bool:
    ok = True
    for f in REQUIRED_FILES:
        if f.exists():
            print(f"  [OK] {f}")
        else:
            print(f"  [MISSING] {f}")
            ok = False
    return ok


def check_oil_price() -> bool:
    data = load_json(RAW_DIR / "oil_prices.json")
    if not data:
        print("  [FAIL] oil_prices.json is empty or missing")
        return False

    price = data.get("brent_usd", 0)

    # Absolute bounds check
    if not (BRENT_MIN <= price <= BRENT_MAX):
        print(f"  [FAIL] Brent ${price}/bbl outside allowed range ${BRENT_MIN}–${BRENT_MAX}")
        return False

    # Day-over-day sanity check
    prev_data = load_json(PROCESSED_DIR / "computed_metrics.json")
    if prev_data:
        prev_price = prev_data.get("brent_price")
        if prev_price and prev_price > 0:
            change_pct = abs(price - prev_price) / prev_price * 100
            if change_pct > BRENT_MAX_DAILY_CHANGE_PCT:
                src = data.get("source", "?")
                print(f"  [FAIL] Brent ${price}/bbl is {change_pct:.1f}% away from "
                      f"previous ${prev_price}/bbl — exceeds {BRENT_MAX_DAILY_CHANGE_PCT}% threshold")
                print(f"  Source: {src}")
                print(f"  → Likely a bad API value. Set data/raw/oil_price_override.json to override.")
                return False
            print(f"  [OK] Brent = ${price}/bbl ({change_pct:+.1f}% vs prev ${prev_price}) "
                  f"[{data.get('source','?')}]")
        else:
            print(f"  [OK] Brent = ${price}/bbl (no prev to compare) [{data.get('source','?')}]")
    else:
        print(f"  [OK] Brent = ${price}/bbl [{data.get('source','?')}]")

    return True


def check_exchange_rates() -> bool:
    data = load_json(RAW_DIR / "exchange_rates.json")
    if not data:
        print("  [WARN] exchange_rates.json missing — will use baseline rates")
        return True   # non-fatal: compute step uses fallback
    n = len(data.get("rates", {}))
    eur_usd = data.get("eur_usd", 0)
    if eur_usd < 0.5 or eur_usd > 2.0:
        print(f"  [FAIL] EUR/USD = {eur_usd} — implausible")
        return False
    print(f"  [OK] Exchange rates: {n} currencies, EUR/USD = {eur_usd}")
    return True


def check_computed_metrics() -> bool:
    data = load_json(PROCESSED_DIR / "computed_metrics.json")
    if not data:
        print("  [FAIL] computed_metrics.json missing")
        return False

    countries = data.get("countries", {})
    if len(countries) < MIN_COUNTRIES:
        print(f"  [FAIL] Only {len(countries)} countries computed (expected ≥{MIN_COUNTRIES})")
        return False

    issues = []
    for name, m in countries.items():
        fuel = m.get("fuelUp", None)
        if fuel is None or fuel < 0 or fuel > 500:
            issues.append(f"{name}: fuelUp={fuel} out of range")
        chg = m.get("currencyChg", None)
        if chg is None or abs(chg) > 90:
            issues.append(f"{name}: currencyChg={chg} suspicious")
        cost = m.get("householdCost", None)
        if cost is None or cost < 0 or cost > 50000:
            issues.append(f"{name}: householdCost={cost} out of range")

    if issues:
        for i in issues:
            print(f"  [WARN] {i}")
    else:
        print(f"  [OK] {len(countries)} countries — all metrics in range")

    # Freshness check — warn if data is over 48 hours old
    gen_at = data.get("generated_at", "")
    if gen_at:
        try:
            dt = datetime.fromisoformat(gen_at.rstrip("Z")).replace(tzinfo=timezone.utc)
            age_h = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
            if age_h > 48:
                print(f"  [WARN] computed_metrics.json is {age_h:.0f}h old")
            else:
                print(f"  [OK] Data freshness: {age_h:.1f}h old")
        except Exception:
            pass

    return True  # warnings only; don't block pipeline


def main():
    print("=" * 55)
    print("WAR IMPACT OBSERVATORY — Pipeline Validation")
    print(f"  {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 55)

    print("\n[1] Required files")
    files_ok = check_required_files()

    print("\n[2] Oil price sanity check")
    oil_ok = check_oil_price()

    print("\n[3] Exchange rates check")
    fx_ok = check_exchange_rates()

    print("\n[4] Computed metrics check")
    metrics_ok = check_computed_metrics()

    print("\n" + "=" * 55)
    if files_ok and oil_ok and fx_ok and metrics_ok:
        print("VALIDATION PASSED — proceeding to dashboard JSON generation")
    else:
        print("VALIDATION FAILED — check warnings above")
        if not (files_ok and oil_ok):
            sys.exit(1)  # Critical failure only on missing files or bad oil price


if __name__ == "__main__":
    main()
