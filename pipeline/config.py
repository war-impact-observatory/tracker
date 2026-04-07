"""
War Impact Observatory — Pipeline Configuration
Baseline values (pre-conflict, 3-day avg Feb 25-27 2026) and country-level parameters.
"""

# ── Oil Price Baseline ────────────────────────────────────────────────────────
# Brent crude spot price (USD/bbl): 3-day average Feb 25-27, 2026 (days before conflict)
# February 2026 monthly average was $69.41 (FRED); slight pre-war tension premium → $70.0
BASELINE_BRENT = 70.0
CONFLICT_START_DATE = "2026-02-28"

# ── ECB API (Free, No Key Required) ──────────────────────────────────────────
ECB_RATES_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
ECB_SDMX_URL  = "https://data-api.ecb.europa.eu/service/data/EXR/D.{currencies}.EUR.SP00.A"

# ── FRED API (Free Key at fred.stlouisfed.org) ───────────────────────────────
FRED_BASE_URL  = "https://api.stlouisfed.org/fred/series/observations"
FRED_BRENT_ID  = "DCOILBRENTEU"   # Brent crude daily (USD/bbl)
FRED_WTI_ID    = "DCOILWTICO"     # WTI crude daily  (USD/bbl)
FRED_US_CPI_ID = "CPIAUCSL"       # US CPI monthly

# ── Baseline EUR/currency rates (3-day avg Feb 25-27, 2026 — days before conflict) ──
# ECB quotes as "how many local units per 1 EUR"
# Sources: ECB official API (primary); verified web sources for SAR, ARS, RUB;
#          USD-peg arithmetic for IQD, QAR, KWD, AED
BASELINE_EUR_RATES = {
    "USD": 1.1801,    # ECB 3-day avg
    "CNY": 8.0911,    # ECB 3-day avg
    "INR": 107.3695,  # ECB 3-day avg
    "JPY": 184.40,    # ECB 3-day avg
    "GBP": 0.8732,    # ECB 3-day avg
    "BRL": 6.0618,    # ECB 3-day avg
    "CAD": 1.6142,    # ECB 3-day avg
    "AUD": 1.6607,    # ECB 3-day avg
    "KRW": 1689.71,   # ECB 3-day avg
    "MXN": 20.2731,   # ECB 3-day avg
    "IDR": 19818.9,   # ECB 3-day avg
    "TRY": 51.8104,   # ECB 3-day avg
    "ILS": 3.6776,    # ECB 3-day avg
    "ZAR": 18.7546,   # ECB 3-day avg
    "SAR": 4.4297,    # web-verified (≈ 3.75 USD-peg × 1.1801)
    "ARS": 1649.4,    # web-verified (exchange-rates.org)
    "RUB": 91.023,    # web-verified (exchange-rates.org)
    "IQD": 1543.9,    # derived: IQD/USD peg ~1308 × 1.1801
    "QAR": 4.2967,    # derived: QAR/USD peg 3.641 × 1.1801
    "KWD": 0.3624,    # derived: KWD/USD ~0.307 × 1.1801
    "AED": 4.3345,    # derived: AED/USD peg 3.673 × 1.1801
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
# Pass-through coefficients: structural sensitivity of retail fuel to oil price
# Calibrated as: coeff = seed_fuelUp / oil_change_pct_at_baseline
# With baseline $70 → $110: oil_change_pct = (110-70)/70*100 = 57.1%

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
