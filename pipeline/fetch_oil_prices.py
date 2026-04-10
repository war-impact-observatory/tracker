"""
Fetch daily Brent crude oil price.

Priority order:
  1. data/raw/oil_price_override.json  — manual override (used when set, auto-expires after 72h)
  2. FRED API  (DCOILBRENTEU)          — 1–2 day lag, very reliable
  3. EIA API   (RBRTE)                 — 1 day lag, fallback
  4. Previous day price from computed_metrics.json  — freeze-in-place if APIs fail

Sanity guards:
  - Price must be $30–$250/bbl
  - Day-over-day change must be ≤ 25% (real-world limit; catches API anomalies)
  - If fetched price fails sanity check, we keep previous day's price and log a WARNING
  - EIA API response is validated to confirm series = RBRTE (Brent spot)

Output: data/raw/oil_prices.json
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

FRED_API_KEY  = os.environ.get("FRED_API_KEY", "")
FRED_URL      = "https://api.stlouisfed.org/fred/series/observations"
BRENT_SERIES  = "DCOILBRENTEU"

OUTPUT_DIR    = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

BRENT_MIN               = 30.0    # never seen below $30 in modern history
BRENT_MAX               = 250.0   # never seen above $250
MAX_DAILY_CHANGE_PCT    = 25.0    # >25% single-day move = suspect API value
OVERRIDE_MAX_AGE_HOURS  = 72      # manual override respected for 72 hours


# ── Helper ────────────────────────────────────────────────────────────────────

def load_json(path: Path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def previous_brent_price() -> float | None:
    """Read last known brent_price from computed_metrics.json."""
    data = load_json(PROCESSED_DIR / "computed_metrics.json")
    if data:
        price = data.get("brent_price")
        if price and BRENT_MIN <= price <= BRENT_MAX:
            return float(price)
    return None


def sanity_check(price: float, source: str) -> bool:
    """Return True if price passes all sanity checks."""
    if not (BRENT_MIN <= price <= BRENT_MAX):
        print(f"  [SANITY FAIL] {source}: ${price}/bbl outside allowed range "
              f"${BRENT_MIN}–${BRENT_MAX}")
        return False

    prev = previous_brent_price()
    if prev:
        change_pct = abs(price - prev) / prev * 100
        if change_pct > MAX_DAILY_CHANGE_PCT:
            print(f"  [SANITY FAIL] {source}: ${price}/bbl is {change_pct:.1f}% away from "
                  f"previous ${prev}/bbl (max allowed: {MAX_DAILY_CHANGE_PCT}%)")
            print(f"  → Rejecting suspicious value. Use oil_price_override.json to manually set.")
            return False
        print(f"  [SANITY OK] ${price}/bbl ({change_pct:+.1f}% vs prev ${prev})")
    else:
        print(f"  [SANITY OK] ${price}/bbl (no previous price to compare)")

    return True


# ── Source 1: Manual override ─────────────────────────────────────────────────

def check_override() -> dict | None:
    """
    Read data/raw/oil_price_override.json if it exists and is fresh (<72h).
    Format: { "brent_usd": 95.0, "date": "2026-04-08", "reason": "ceasefire" }
    """
    path = OUTPUT_DIR / "oil_price_override.json"
    data = load_json(path)
    if not data:
        return None

    # Check age
    set_at_str = data.get("set_at", "")
    if set_at_str:
        try:
            set_at = datetime.fromisoformat(set_at_str.rstrip("Z")).replace(tzinfo=timezone.utc)
            age_h  = (datetime.now(timezone.utc) - set_at).total_seconds() / 3600
            if age_h > OVERRIDE_MAX_AGE_HOURS:
                print(f"  Override file is {age_h:.0f}h old (>{OVERRIDE_MAX_AGE_HOURS}h) — expired, ignoring.")
                return None
            print(f"  Override active ({age_h:.1f}h old, expires in {OVERRIDE_MAX_AGE_HOURS - age_h:.0f}h): "
                  f"${data['brent_usd']}/bbl — {data.get('reason','')}")
        except Exception:
            pass

    price = data.get("brent_usd")
    if price and BRENT_MIN <= float(price) <= BRENT_MAX:
        return {
            "brent_usd": round(float(price), 2),
            "date":      data.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
            "source":    f"MANUAL_OVERRIDE — {data.get('reason', 'set manually')}",
        }
    return None


# ── Source 2: FRED API ────────────────────────────────────────────────────────

def fetch_brent_fred() -> dict | None:
    if not FRED_API_KEY:
        print("  FRED_API_KEY not set — skipping FRED")
        return None

    params = {
        "series_id":  BRENT_SERIES,
        "api_key":    FRED_API_KEY,
        "file_type":  "json",
        "sort_order": "desc",
        "limit":      5,
    }
    try:
        resp = requests.get(FRED_URL, params=params, timeout=20)
        resp.raise_for_status()
        obs = resp.json().get("observations", [])
        for o in obs:
            if o.get("value") not in (".", "", None):
                price = round(float(o["value"]), 2)
                date  = o["date"]
                print(f"  FRED: ${price}/bbl on {date}")
                if sanity_check(price, "FRED"):
                    return {"brent_usd": price, "date": date, "source": "FRED/DCOILBRENTEU"}
                return None   # failed sanity — don't try EIA (same lag issue)
    except Exception as e:
        print(f"  FRED fetch failed: {e}")
    return None


# ── Source 3: EIA API ─────────────────────────────────────────────────────────

def fetch_brent_eia() -> dict | None:
    eia_key = os.environ.get("EIA_API_KEY", "")
    if not eia_key:
        print("  EIA_API_KEY not set — skipping EIA")
        return None

    url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
    params = {
        "api_key":             eia_key,
        "frequency":           "daily",
        "data[0]":             "value",
        "facets[series][]":    "RBRTE",   # Brent spot price
        "sort[0][column]":     "period",
        "sort[0][direction]":  "desc",
        "length":              5,
    }
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        rows = resp.json().get("response", {}).get("data", [])
        for row in rows:
            # Validate this row IS the Brent series (not a stray series)
            if row.get("series") and row["series"] != "RBRTE":
                print(f"  EIA: skipping series={row['series']} (expected RBRTE)")
                continue
            val = row.get("value")
            if val in (None, ""):
                continue
            price = round(float(val), 2)
            date  = row.get("period", "")
            print(f"  EIA: ${price}/bbl on {date} (series={row.get('series','?')})")
            if sanity_check(price, "EIA"):
                return {"brent_usd": price, "date": date, "source": "EIA/RBRTE"}
            return None
    except Exception as e:
        print(f"  EIA fetch failed: {e}")
    return None


# ── Source 4: Freeze previous price ──────────────────────────────────────────

def freeze_previous() -> dict | None:
    prev = previous_brent_price()
    if prev:
        print(f"  [FREEZE] Using previous price ${prev}/bbl from computed_metrics.json")
        return {
            "brent_usd": prev,
            "date":      (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "source":    "FROZEN — API fetch failed or failed sanity check; using previous day",
        }
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching Brent crude oil price...")
    print(f"  Sanity bounds: ${BRENT_MIN}–${BRENT_MAX}, max daily change: {MAX_DAILY_CHANGE_PCT}%")

    result = (
        check_override()       or   # Manual override (highest priority)
        fetch_brent_fred()     or   # FRED (most reliable)
        fetch_brent_eia()      or   # EIA fallback
        freeze_previous()           # Last resort: freeze yesterday's price
    )

    if not result:
        # Absolute last resort — hardcoded safe value
        print("  [CRITICAL] All sources failed. Using hardcoded fallback $95/bbl.")
        result = {
            "brent_usd": 95.0,
            "date":      datetime.utcnow().strftime("%Y-%m-%d"),
            "source":    "HARDCODED_FALLBACK — all sources failed",
        }

    result["fetched_at"] = datetime.utcnow().isoformat() + "Z"

    out = OUTPUT_DIR / "oil_prices.json"
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved: ${result['brent_usd']}/bbl [{result['source']}]")

    with open(PROCESSED_DIR / "latest_brent.txt", "w") as f:
        f.write(f"Brent ${result['brent_usd']}/bbl")


if __name__ == "__main__":
    main()
