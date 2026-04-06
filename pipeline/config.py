"""
War Impact Observatory — Pipeline Configuration
Baseline values (pre-conflict, ~April 2025) and country-level parameters.
"""

# ── Oil Price Baseline ────────────────────────────────────────────────────────
# Brent crude spot price (USD/bbl) before conflict escalation
BASELINE_BRENT = 73.0
CONFLICT_START_DATE = "2026-02-28"

# ── ECB API (Free, No Key Required) ──────────────────────────────────────────
ECB_RATES_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
ECB_SDMX_URL  = "https://data-api.ecb.europa.eu/service/data/EXR/D.{currencies}.EUR.SP00.A"

# ── FRED API (Free Key at fred.stlouisfed.org) ───────────────────────────────
FRED_BASE_URL  = "https://api.stlouisfed.org/fred/series/observations"
FRED_BRENT_ID  = "DCOILBRENTEU"   # Brent crude daily (USD/bbl)
FRED_WTI_ID    = "DCOILWTICO"     # WTI crude daily  (USD/bbl)
FRED_US_CPI_ID = "CPIAUCSL"       # US CPI monthly

# ── Baseline EUR/currency rates (pre-conflict, April 2025 approx) ─────────────
# ECB quotes as "how many local units per 1 EUR"
BASELINE_EUR_RATES = {
    "USD": 1.085,
    "CNY": 7.850,
    "INR": 90.1,
    "JPY": 161.7,
    "GBP": 0.854,
    "BRL": 5.640,
    "CAD": 1.476,
    "AUD": 1.703,
    "KRW": 1454.0,
    "MXN": 18.66,
    "IDR": 16926.0,
    "TRY": 35.26,
    "SAR": 4.07,
    "ARS": 944.0,
    "ZAR": 20.4,
    "RUB": 96.6,
    "ILS": 3.98,
    "IQD": 1419.0,
    "QAR": 3.95,
    "KWD": 0.333,
    "AED": 3.985,
    # ECB does not track these — use manual/static fallback
    "LBP": 97200.0,
    "SYP": 15000.0,
    "YER": 545.0,
}

# ── Country Configuration ─────────────────────────────────────────────────────
# Each entry:
#   currency       : ISO 4217 code (for ECB lookup)
#   passThrough    : how strongly oil price change flows to retail fuel price
#                    (computed as historical fuelUp / oil_price_change_pct)
#   ecb_tracked    : whether ECB publishes this currency (else use static fallback)
#
# Pass-through coefficients reverse-engineered from observed data:
# oil_change_pct = (126 - 73) / 73 * 100 = 72.6%  →  coeff = fuelUp / 72.6

COUNTRY_CONFIG = {
    "United States":   {"currency": "USD", "passThrough": 0.413, "ecb_tracked": True},
    "China":           {"currency": "CNY", "passThrough": 0.303, "ecb_tracked": True},
    "India":           {"currency": "INR", "passThrough": 0.482, "ecb_tracked": True},
    "Japan":           {"currency": "JPY", "passThrough": 0.386, "ecb_tracked": True},
    "Germany":         {"currency": "EUR", "passThrough": 0.441, "ecb_tracked": True},
    "United Kingdom":  {"currency": "GBP", "passThrough": 0.358, "ecb_tracked": True},
    "France":          {"currency": "EUR", "passThrough": 0.331, "ecb_tracked": True},
    "Brazil":          {"currency": "BRL", "passThrough": 0.248, "ecb_tracked": True},
    "Canada":          {"currency": "CAD", "passThrough": 0.276, "ecb_tracked": True},
    "Australia":       {"currency": "AUD", "passThrough": 0.344, "ecb_tracked": True},
    "South Korea":     {"currency": "KRW", "passThrough": 0.413, "ecb_tracked": True},
    "Italy":           {"currency": "EUR", "passThrough": 0.400, "ecb_tracked": True},
    "Mexico":          {"currency": "MXN", "passThrough": 0.276, "ecb_tracked": True},
    "Indonesia":       {"currency": "IDR", "passThrough": 0.386, "ecb_tracked": True},
    "Turkey":          {"currency": "TRY", "passThrough": 0.551, "ecb_tracked": True},
    "Saudi Arabia":    {"currency": "SAR", "passThrough": 0.138, "ecb_tracked": True},
    "Argentina":       {"currency": "ARS", "passThrough": 0.482, "ecb_tracked": True},
    "South Africa":    {"currency": "ZAR", "passThrough": 0.441, "ecb_tracked": True},
    "Russia":          {"currency": "RUB", "passThrough": 0.110, "ecb_tracked": True},
    "European Union":  {"currency": "EUR", "passThrough": 0.386, "ecb_tracked": True},
    "Iran":            {"currency": "IRR", "passThrough": 1.171, "ecb_tracked": False},
    "Israel":          {"currency": "ILS", "passThrough": 0.524, "ecb_tracked": True},
    "Iraq":            {"currency": "IQD", "passThrough": 0.758, "ecb_tracked": True},
    "Qatar":           {"currency": "QAR", "passThrough": 0.165, "ecb_tracked": True},
    "Kuwait":          {"currency": "KWD", "passThrough": 0.207, "ecb_tracked": True},
    "UAE":             {"currency": "AED", "passThrough": 0.138, "ecb_tracked": True},
    "Lebanon":         {"currency": "LBP", "passThrough": 1.240, "ecb_tracked": False},
    "Syria":           {"currency": "SYP", "passThrough": 1.309, "ecb_tracked": False},
    "Yemen":           {"currency": "YER", "passThrough": 1.102, "ecb_tracked": False},
}

# Household cost formula weights
FOOD_WEIGHT = 0.6   # food is ~60% of the food+fuel spend
FUEL_WEIGHT = 0.4   # fuel is ~40%
