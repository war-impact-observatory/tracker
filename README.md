# War Impact Observatory

**Open-source economic impact tracker for the 2026 US-Israel-Iran conflict.**

Measuring the cost to every G20 economy and its citizens — oil prices, inflation, trade disruption, household costs, and second-order effects. Updated daily via automated pipeline.

[![Daily Update](https://img.shields.io/badge/updates-daily%20at%2006%3A00%20UTC-blue)]()
[![License: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-green)](https://creativecommons.org/licenses/by/4.0/)
[![License: MIT](https://img.shields.io/badge/code-MIT-blue)](LICENSE)
[![Brent Crude](https://img.shields.io/badge/Brent-$113%2Fbbl-red)]()

---

## What This Is

A transparent, modular, community-driven tracker that quantifies six channels through which the Iran conflict transmits economic damage globally:

1. **Energy & Fuel Prices** — Oil, gas, LNG price surges
2. **Food & Fertilizer** — Supply chain disruption through Strait of Hormuz
3. **GDP & Growth** — Revised forecasts, recession risk
4. **Currencies & Capital Flows** — EM currency depreciation, flight to safety
5. **Trade & Supply Chains** — Shipping collapse, insurance premiums
6. **Household Welfare** — Per-household annual cost estimates

## Live Dashboard

Visit **[warimpactobservatory.org](https://warimpactobservatory.org)** for the interactive dashboard, or open `index.html` locally.

## Key Figures (as of April 5, 2026)

| Metric | Value | Change |
|--------|-------|--------|
| Brent Crude | $113/bbl | +55% since Feb 27 |
| US Gasoline | $4.00/gal | +30% |
| Global Inflation (OECD) | 4.0% | +0.8pp |
| Hormuz Ship Transits | 6/day | -95% (from 130) |
| Oil Supply Disrupted | 10M+ bpd | Largest in history (IEA) |

## Project Structure

```
war-impact-observatory/
├── index.html                    # Interactive dashboard (self-contained)
├── README.md                     # This file
├── LICENSE                       # MIT (code) + CC BY 4.0 (data)
├── CONTRIBUTING.md               # How to contribute
├── METHODOLOGY.md                # Full methodology documentation
├── data/
│   ├── raw/                      # Raw API responses, timestamped
│   │   ├── eia/                  # EIA oil price data
│   │   ├── fred/                 # FRED CPI & gas prices
│   │   ├── ecb/                  # ECB exchange rates
│   │   └── worldbank/            # World Bank commodity data
│   ├── processed/                # Cleaned, merged datasets
│   │   ├── oil_prices.csv
│   │   ├── inflation_by_country.csv
│   │   ├── household_costs.csv
│   │   ├── trade_disruption.csv
│   │   └── dashboard_data.json   # JSON consumed by dashboard
│   └── schema/                   # Data schema definitions
│       └── schema.json
├── pipeline/
│   ├── fetch_oil_prices.py       # EIA API fetcher
│   ├── fetch_exchange_rates.py   # ECB SDMX fetcher
│   ├── fetch_fred_data.py        # FRED API fetcher
│   ├── compute_household_costs.py # IMF pass-through model
│   ├── merge_and_validate.py     # Data pipeline orchestrator
│   └── requirements.txt          # Python dependencies
├── media/
│   ├── press_snippet.txt         # Wire-ready press release
│   ├── twitter_thread.md         # Social media templates
│   └── chart_cards/              # PNG chart images for social
├── .github/
│   └── workflows/
│       └── daily-update.yml      # GitHub Actions CI/CD
└── docs/
    ├── data_sources.md           # Detailed source documentation
    ├── api_reference.md          # API endpoints used
    └── changelog.md              # Data update history
```

## Data Sources

| Source | Data | Frequency | Access |
|--------|------|-----------|--------|
| [EIA Open Data](https://www.eia.gov/opendata/) | Oil prices (Brent, WTI) | Daily | Free, API key |
| [FRED](https://fred.stlouisfed.org/) | US CPI, gas prices, breakevens | Daily/Monthly | Free, API key |
| [ECB SDMX](https://sdw-wsrest.ecb.europa.eu/) | EUR exchange rates | Daily | Free, no key |
| [World Bank Commodities](https://www.worldbank.org/en/research/commodity-markets) | Commodity price indices | Monthly | Free, no key |
| [IMF WEO](https://data.imf.org/) | GDP, inflation forecasts | Semiannual | Free, no key |
| [UNCTAD](https://unctad.org/) | Trade flow data | Quarterly | Free, no key |

## Methodology

See [METHODOLOGY.md](METHODOLOGY.md) for full documentation. Key design principles:

- **Modular channels over single numbers** — No single "cost of war" headline. Six independent impact channels that users can weight based on what matters to them.
- **Transparent uncertainty** — All forecasts include confidence intervals. We distinguish between observed data (solid lines) and projections (dashed).
- **IMF pass-through model** — Household costs use IMF oil-price pass-through coefficients by country, adjusted for subsidies and energy mix.
- **PPP-adjusted where appropriate** — Cross-country household comparisons use purchasing power parity.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Ways to contribute:
- **Data**: Add new countries, improve data sources, submit corrections
- **Code**: Improve pipeline scripts, add new API integrations, enhance dashboard
- **Analysis**: Propose new impact channels, improve methodology, add uncertainty quantification
- **Media**: Translate content, create visualizations, write analysis pieces

## Media Use

All data is licensed under **CC BY 4.0**. Journalists and newsrooms may freely use, quote, and republish any data or charts with attribution:

> Source: War Impact Observatory (warimpactobservatory.org), CC BY 4.0

Pre-formatted press snippets and embeddable chart codes are available in the `media/` directory and on the dashboard's Media Kit tab.

## Governance

- **Data review**: All data updates go through PR review. Two maintainer approvals required for methodology changes.
- **Transparency**: Every data point links to its source. Processing scripts are public.
- **Community input**: GitHub Discussions for methodology debates. Monthly community calls.
- **Advisory board**: Open call for economists, data scientists, and conflict researchers.

## Competitive Landscape

This project complements (not replaces) existing work:

| Project | Focus | Our Difference |
|---------|-------|----------------|
| [Brown Costs of War](https://watson.brown.edu/costsofwar/) | US war spending | We track spillover costs globally |
| [Institute for Economics & Peace](https://www.economicsandpeace.org/) | Peace economics index | We focus on real-time household impact |
| [ACLED](https://acleddata.com/) | Conflict event data | We track economic transmission, not events |
| [UCDP](https://ucdp.uu.se/) | Conflict deaths | We measure economic welfare costs |

## License

- **Data**: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
- **Code**: [MIT License](LICENSE)
