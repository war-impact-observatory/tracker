# Methodology — War Impact Observatory

## 1. Framework Overview

We decompose the economic impact of the 2026 US-Israel-Iran conflict into six independent **transmission channels**. This modular approach avoids the pitfalls of a single aggregate number, which is inevitably reductive and politically charged.

Each channel uses the best available data source for that domain, with explicit documentation of assumptions, limitations, and uncertainty.

### Why Not a Single "Cost of War" Number?

Single-number estimates (like "the war costs $X trillion") are attention-grabbing but methodologically fragile. They require heroic assumptions about discount rates, counterfactuals, and value-of-life calculations. Our channel-based approach lets each consumer of this data weight what matters to them: a policymaker may focus on GDP and trade; a journalist on household costs; an activist on food prices.

---

## 2. Channel Definitions

### 2.1 Energy & Fuel Prices
- **Data**: EIA (Brent, WTI spot), GasBuddy (retail US gasoline)
- **Method**: Direct observation of market prices. Pre-conflict baseline = 7-day average ending Feb 27, 2026.
- **Limitation**: Spot prices reflect speculation as well as fundamentals. We report both spot and futures curves where available.

### 2.2 Food & Fertilizer
- **Data**: World Bank Commodity Pink Sheets, FAO Food Price Index
- **Method**: Track monthly commodity price indices. Fertilizer disruption estimated from UNCTAD Hormuz transit share data (30% of global urea).
- **Limitation**: Monthly granularity means delayed signal. National food price transmission depends heavily on subsidies (India, Indonesia) which we account for qualitatively but not quantitatively.

### 2.3 GDP & Growth
- **Data**: IMF WEO forecasts, Oxford Economics nowcasts, OECD interim outlooks
- **Method**: Compare pre-conflict forecasts (Jan 2026 WEO) with post-conflict revisions. Report delta in percentage points.
- **Limitation**: Forecasts are scenario-dependent. We report the "current intensity persists" scenario. Ceasefire or escalation would materially change these numbers.

### 2.4 Currencies & Capital Flows
- **Data**: ECB SDMX (EUR crosses), FRED (DXY), Bloomberg (EM FX)
- **Method**: Spot rate change from Feb 27 baseline. We do not attempt to isolate conflict-specific FX moves from other macro factors.
- **Limitation**: Attribution is imperfect. Some currency moves reflect broader risk-off sentiment, US tariff policy, or idiosyncratic factors.

### 2.5 Trade & Supply Chains
- **Data**: UNCTAD maritime data, Lloyd's List (Hormuz transits), WTO trade forecasts
- **Method**: Direct observation of shipping volumes, plus forecast revisions from WTO/UNCTAD.
- **Limitation**: Real-time shipping data has limited free access. We supplement with news reports and institutional releases.

### 2.6 Household Welfare
- **Data**: Modeled (not directly observed)
- **Method**: IMF oil-price pass-through coefficients by country. For every $10/barrel increase in oil, we apply the country-specific elasticity to estimate the additional annual household cost in local currency (converted to USD at current rates).
- **Formula**: `household_cost = oil_delta * pass_through_coefficient * avg_household_energy_spend * (1 - subsidy_offset)`
- **Limitation**: This is the most approximate channel. Pass-through coefficients are estimated from historical data and may not hold in unprecedented disruptions. We use PPP-adjusted averages, which mask inequality within countries. A low-income household in India faces proportionally far higher costs than the average suggests.

---

## 3. Data Quality Assessment

| Source | Reliability | Timeliness | Granularity | Access |
|--------|------------|------------|-------------|--------|
| EIA | High | Daily | Country | Free API |
| IMF WEO | High | Semiannual | Country | Free |
| FRED | High | Daily–Monthly | US only | Free API |
| World Bank | High | Monthly | Global | Free |
| UNCTAD | Medium-High | Quarterly | Regional | Free |
| Oxford Economics | High | Monthly | Country | Paywalled (we cite public releases) |
| News reports | Variable | Real-time | Event-level | Free |

### Known Gaps
1. **Real-time household microdata**: No freely available source tracks actual household spending changes at daily frequency across G20.
2. **Financial contagion**: Bank exposure to Gulf assets, derivatives exposure, and credit default swap spreads are not yet modeled.
3. **Subnational impacts**: National averages mask huge variation (e.g., rural vs. urban, coastal vs. inland).
4. **Informal economies**: Large informal sectors in India, Indonesia, Turkey mean official data understates actual impact.

---

## 4. Representation Choices & Tradeoffs

| Visualization | Why We Chose It | Alternative Considered | Why Not |
|---------------|----------------|----------------------|---------|
| Area chart for oil prices | Shows volatility, trend, and events on same axis | Candlestick chart | Too finance-specific for general audience |
| Sortable table for countries | Enables user-driven comparison across any metric | Choropleth map | Maps hide small/important countries, hard to show multiple metrics |
| Horizontal bar for household cost | Intuitive comparison, works on mobile | Pie chart | Pie charts are poor for comparing magnitudes |
| Line chart for inflation | Shows trajectory and divergence between regions | Small multiples | Would fragment the comparison story |
| Cards for impact channels | Scannable, each self-contained | Accordion/collapse | Hides information, adds clicks |

### What We Deliberately Avoided
- **Single headline dollar figure**: Too reductive, invites false precision
- **Casualty data**: Beyond our scope; covered by ACLED and UCDP
- **Political framing**: We report economic data without attributing blame
- **Predictive modeling**: We report current data and institutional forecasts, not our own predictions

---

## 5. Update Frequency

| Data Type | Update Frequency | Source Lag |
|-----------|-----------------|------------|
| Oil spot prices | Daily | Same day |
| US gasoline prices | Weekly | 1 week |
| Exchange rates | Daily | Same day |
| Inflation (CPI) | Monthly | 2-4 weeks |
| GDP forecasts | As revised | Variable |
| Trade data | Quarterly | 2-3 months |
| Household cost model | Daily (recomputed from oil price) | Model-dependent |

---

## 6. How to Critique or Improve This Methodology

We actively invite methodological critique. To propose changes:

1. Open a GitHub Issue with the label `methodology`
2. Reference specific data points, assumptions, or calculations
3. Provide alternative data sources or models if possible
4. We will tag relevant maintainers and discuss openly

Priority areas for community contribution:
- Financial contagion modeling
- Subnational impact estimates
- Real-time price scraping (grocery, fuel station level)
- Subsidy-adjusted household cost models for India, Indonesia, Turkey
- Environmental and health cost channels (currently not included)
