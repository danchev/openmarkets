# Open Markets

[![PyPI](https://img.shields.io/pypi/v/openmarkets)](https://pypi.org/project/openmarkets)
[![PyPI - Downloads](https://static.pepy.tech/badge/openmarkets)](https://pypi.org/project/openmarkets)
[![PyPI - Monthly Downloads](https://static.pepy.tech/badge/openmarkets/month)](https://pypi.org/project/openmarkets)
[![Tests](https://img.shields.io/badge/tests-428%20passed-success)](https://github.com/danchev/openmarkets)
[![Tools](https://img.shields.io/badge/MCP%20Tools-118%20tools-blue)](https://github.com/danchev/openmarkets)
[![License](https://img.shields.io/badge/license-AGPLv3%2B-blue.svg)](LICENSE)

A production-grade **Model Context Protocol (MCP) server** for agentic financial data retrieval and algorithmic market analysis. Open Markets connects LLM agents directly to real-time and historical financial intelligence across equities, fixed income, commodities, currencies, derivatives, funds, crypto, macroeconomic telemetry, and SEC EDGAR regulatory disclosures.

---

## 🌟 Multi-Provider Architecture

Open Markets aggregates financial telemetry across institutional-grade data providers:
- **SEC EDGAR Direct Ingestion Engine**: Official regulatory submissions, real-time 10-K annual reports, 10-Q quarterly reports, 8-K material events, Form 4 insider transactions, and structured US-GAAP interactive XBRL disclosures with direct document links.
- **Federal Reserve Economic Data (FRED Engine)**: Comprehensive macroeconomic indicators (CPI Inflation, Core PCE, Effective Fed Funds Rate, SOFR, Nonfarm Payrolls, Unemployment, Real GDP, M2 Money Supply, Fed Balance Sheet, TIPS Breakeven Inflation, and Financial Stress).
- **Wall Street Journal (WSJ Michelangelo Engine)**: High-resolution 1-minute intraday continuous ticks (with pre/post-market), continuous commodities & futures, server-side technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands), global equity benchmark indices, and sovereign bond curves.
- **Yahoo Finance Engine**: Complete fundamental statements, real-time quotes, options chains, analyst consensus, institutional ownership, ETF compositions, and screener queries.
- **Green Markets (Bloomberg / Dow Jones)**: Weekly North American fertilizer price index benchmark.


All network requests use modern **Chrome TLS/JA3-impersonation** (`curl_cffi`), automatic session pooling, thread-safe asynchronous concurrency, and configurable in-memory **TTL caching**.

---

## 🚀 Quick Start

### Installation with `uvx`

```bash
uvx openmarkets
```

### Usage with Cursor

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/en-US/install-mcp?name=openmarkets&config=eyJjb21tYW5kIjoidXZ4IG9wZW5tYXJrZXRzQGxhdGVzdCJ9)

### Usage with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "openmarkets": {
      "command": "uvx",
      "args": ["openmarkets@latest"]
    }
  }
}
```

### Usage with VS Code & Cline

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "openmarkets": {
      "command": "uvx",
      "args": ["openmarkets@latest"]
    }
  }
}
```

---

## 🎯 Tool Profiles

Open Markets supports granular server profiles to tailor tool exposure to specific LLM contexts:

```bash
# Run with specific domain profile
uvx openmarkets --profile equities
uvx openmarkets --profile macro
uvx openmarkets --profile quant
uvx openmarkets --profile sec
```

| Profile | Exposed Services & Focus |
| :--- | :--- |
| **`full`** *(default)* | All 118 tools across all 16 services. |
| **`equities`** | `stock`, `financials`, `analysis`, `holdings`, `options`, `screener`, `sec`. |
| **`quant`** | `stock`, `technical_analysis`, `sector_industry`, `markets`, `crypto`, `funds`, `commodities`, `fixed_income`, `forex`, `macroeconomics`. |
| **`macro`** | `commodities`, `fixed_income`, `forex`, `markets`, `sector_industry`, `macroeconomics`. |
| **`sec`** | Direct SEC EDGAR submissions, 10-K, 10-Q, 8-K, Form 4, CIK search, and interactive XBRL financial statement facts. |
| **`minimal`** | Essential 12 tools across core stock and financial lookups. |
| **`macroeconomics`** | US Inflation, PCE, labor markets, Fed rates, GDP, M2, liquidity, and financial stress. |
| **`commodities`** | Physical commodities, energy, metals, softs, and fertilizer indices. |
| **`fixed_income`**| Treasury yield curves and 10Y sovereign benchmark yield spreads. |
| **`forex`** | Foreign exchange rates, DXY dollar index, and currency conversions. |
| **`crypto`** | Top cryptocurrencies, historical crypto pricing, and fear & greed index proxy. |

---

## 🛠️ Complete Directory of 118 MCP Tools

Open Markets publishes **118 strictly-typed, Pydantic-validated tools** across **16 domain services**:


### 1. Stock & Equities (`StockService` — 19 tools)
- `get_fast_info(ticker)`: Fast summary with real-time price, market cap, 52-week bounds, and currency.
- `get_info(ticker)`: Exhaustive company metadata, valuation ratios, enterprise multiples, and governance.
- `get_history(ticker, period, interval)`: Historical OHLCV pricing with custom intervals (1m to 3mo).
- `get_multiple_tickers(tickers, period)`: Concurrent batch pricing for multiple securities.
- `download_bulk_data(tickers, period, interval)`: High-performance batch timeseries downloader.
- `get_dividends(ticker)`: Historical dividend payout schedule and cash amounts.
- `get_splits(ticker)`: Historical stock split ratios and execution dates.
- `get_corporate_actions(ticker)`: Combined stream of splits and dividend distributions.
- `get_news(ticker)`: Latest real-time financial news headlines and article links.
- `get_financial_summary(ticker)`: Core financial health snapshot (Revenue, Net Income, Margins, Debt).
- `get_extended_financial_summary(ticker)`: Deep financial metrics (Free Cash Flow, ROE, ROA, Quick Ratio).
- `get_risk_metrics(ticker)`: Risk indicators including Beta and institutional short interest.
- `get_dividend_summary(ticker)`: Payout ratio, trailing/forward dividend yields, and 5-year averages.
- `get_price_target(ticker)`: Analyst consensus price targets (Low, Mean, Median, High).
- `get_quick_technical_indicators(ticker)`: Lightweight 50-day & 200-day moving average levels.
- `get_valuation_history(ticker)`: Quarterly & annual historical valuation ratios (P/E, P/S, P/B, EV/EBITDA).
- `get_wsj_stock_history(ticker, timeframe, step)`: WSJ institutional price history with custom timeframes.
- `get_wsj_intraday_bars(ticker)`: Continuous 1-minute intraday tick data including pre-market and after-hours.
- `get_wsj_bollinger_bands(ticker, timeframe, window, num_std)`: Server-side calculated Bollinger Bands directly from WSJ.

### 2. Technical Analysis (`TechnicalAnalysisService` — 7 tools)
- `get_technical_indicators(ticker, period)`: Comprehensive moving averages and 52-week position metrics.
- `get_volatility_metrics(ticker, period)`: Annualized volatility, maximum daily gains/losses, win/loss day ratios.
- `get_support_resistance_levels(ticker, period)`: Identified dynamic support and resistance price floors/ceilings.
- `get_wsj_sma(ticker, window, timeframe, step)`: Server-side computed Simple Moving Average (SMA) via WSJ Michelangelo.
- `get_wsj_ema(ticker, window, timeframe, step)`: Server-side computed Exponential Moving Average (EMA).
- `get_wsj_rsi(ticker, window, timeframe, step)`: Server-side computed Relative Strength Index (RSI momentum).
- `get_wsj_macd(ticker, fast_window, slow_window, signal_window)`: Server-side computed MACD Line, Signal Line, and Histogram.

### 3. Financial Statements & SEC Filings (`FinancialsService` — 8 tools)
- `get_balance_sheet(ticker, quarterly)`: Standardized balance sheet statements (Assets, Liabilities, Equity).
- `get_income_statement(ticker, quarterly)`: Income statements (Revenues, Gross Profits, Operating Income, Net Income).
- `get_cash_flow(ticker, quarterly)`: Cash flow statements (Operating, Investing, Financing, Free Cash Flow).
- `get_ttm_income_statement(ticker)`: Trailing Twelve Months (TTM) income statement.
- `get_ttm_cash_flow_statement(ticker)`: Trailing Twelve Months (TTM) cash flow statement.
- `get_financial_calendar(ticker)`: Upcoming earnings release dates and dividend announcement schedules.
- `get_sec_filings(ticker)`: Official EDGAR SEC filings (10-K, 10-Q, 8-K) with direct document URLs.
- `get_eps_history(ticker)`: Historical EPS consensus estimates versus reported actuals and surprise percentages.

### 4. Analyst Estimates & Consensus (`AnalysisService` — 8 tools)
- `get_analyst_recommendations(ticker)`: Wall Street consensus ratings breakdown (Strong Buy, Buy, Hold, Sell).
- `get_recommendation_changes(ticker)`: Recent rating upgrades and downgrades from major investment banks.
- `get_revenue_estimates(ticker)`: Forward revenue projections and quarterly growth estimates.
- `get_earnings_estimates(ticker)`: Forward EPS estimates (Quarterly & Annual).
- `get_growth_estimates(ticker)`: Multi-year earnings growth forecast comparisons.
- `get_eps_trends(ticker)`: Historical EPS revision trends (30 days, 60 days, 90 days ago).
- `get_price_targets(ticker)`: Wall Street price targets with high, low, and median projections.
- `get_full_analysis(ticker)`: Unified analyst research summary report.

### 5. Options & Derivatives (`OptionsService` — 7 tools)
- `get_option_expiration_dates(ticker)`: Available options chain expiration dates.
- `get_option_chain(ticker, expiration_date)`: Complete options chain with calls and puts.
- `get_call_options(ticker, expiration_date)`: Filtered call options with strike, bid/ask, volume, and open interest.
- `get_put_options(ticker, expiration_date)`: Filtered put options.
- `get_options_volume_analysis(ticker, expiration_date)`: Aggregate Put/Call volume and Open Interest ratios.
- `get_options_by_moneyness(ticker, expiration_date, moneyness_range)`: ITM, ATM, and OTM options filtered by moneyness.
- `get_options_skew(ticker, expiration_date)`: Volatility smile and implied volatility (IV) skew metrics.

### 6. Institutional Holdings & Insider Trades (`HoldingsService` — 6 tools)
- `get_major_holders(ticker)`: Ownership breakdown (Insiders, Institutions, Float percentages).
- `get_institutional_holdings(ticker)`: Top institutional asset managers (Vanguard, BlackRock, etc.) and shares held.
- `get_mutual_fund_holdings(ticker)`: Top mutual fund holders and portfolio portfolio position weights.
- `get_insider_purchases(ticker)`: Executive insider buying vs selling transactions and dollar volumes.
- `get_insider_roster_holders(ticker)`: Key company officers and board member share positions.
- `get_full_holdings(ticker)`: Unified institutional and insider ownership report.

### 7. Stock Screener (`ScreenerService` — 4 tools)
- `screen_day_gainers(count)`: Top percentage gainers in US markets.
- `screen_day_losers(count)`: Top percentage decliners in US markets.
- `screen_most_actives(count)`: Most actively traded securities by volume.
- `screen_top_etfs(count)`: Top-performing Exchange Traded Funds.

### 8. Sectors & Industry Analytics (`SectorIndustryService` — 14 tools)
- `get_sector_overview(sector)`: Macro sector performance and key valuation metrics.
- `get_sector_overview_for_ticker(ticker)`: Sector intelligence inferred from any ticker.
- `get_sector_top_companies(sector)`: Leading corporations by market capitalization in a sector.
- `get_sector_top_companies_for_ticker(ticker)`: Sector peers for any given ticker.
- `get_sector_top_etfs(sector)`: Benchmark ETFs representing the sector.
- `get_sector_top_mutual_funds(sector)`: Top mutual funds specialized in the sector.
- `get_sector_industries(sector)`: Sub-industry breakdown and market weightings within a sector.
- `get_sector_research_reports(sector)`: Sector research notes and macro updates.
- `get_all_industries()`: Complete directory of market industries.
- `get_industry_overview(industry)`: Industry growth, valuation, and market capitalization.
- `get_industry_top_companies(industry)`: Industry market leaders by market cap.
- `get_industry_top_growth_companies(industry)`: Fastest revenue and earnings growers in an industry.
- `get_industry_top_performing_companies(industry)`: Top price momentum leaders within an industry.
- `get_industry_top_companies_by_region(industry, region)`: Geographic region-scoped industry leaders (e.g. US, Europe, Asia).

### 9. Global Markets & Volatility (`MarketsService` — 4 tools)
- `get_market_summary(market)`: Regional market overview (US, Europe, Asia).
- `get_market_status(market)`: Real-time open/closed status for major global exchanges.
- `get_global_indices()`: Live snapshot across world benchmark indices (S&P 500, Dow Jones, Nasdaq, Russell 2000, DAX 40, FTSE 100, CAC 40, Euro Stoxx 50, Nikkei 225, Hang Seng, VIX).
- `get_volatility_vix()`: Real-time quote for CBOE Volatility Index (VIX / Wall Street Fear Gauge).

### 10. Fixed Income & Sovereign Debt (`FixedIncomeService` — 3 tools)
- `get_treasury_yield_curve()`: Complete US Treasury yield curve snapshot (1M to 30Y), 2Y/10Y spread, 3M/10Y spread, and inversion status.
- `get_treasury_yield_history(maturity, timeframe, step)`: Historical yield timeseries for any Treasury tenor.
- `get_global_sovereign_yields()`: Benchmark 10-year sovereign yields and basis-point spreads vs US 10Y across 9 nations (US, Germany, UK, Japan, Canada, France, Italy, Australia, Spain).

### 11. Physical Commodities & Agriculture (`CommoditiesService` — 9 tools)
- `get_commodity_quote(symbol)`: Real-time price quote for Energy, Metals, Agriculture, Livestock, or Softs.
- `get_commodity_history(symbol, timeframe, step)`: Historical continuous futures price charts.
- `get_energy_prices()`: Multi-quote snapshot for WTI Crude, Brent, Natural Gas, Gasoline, and Heating Oil.
- `get_metals_prices()`: Multi-quote snapshot for Gold, Silver, Copper, Platinum, and Palladium.
- `get_agriculture_prices()`: Multi-quote snapshot for Wheat, Corn, Soybeans, Coffee, and Sugar.
- `get_livestock_prices()`: Live snapshot for Live Cattle, Feeder Cattle, and Lean Hogs.
- `get_softs_prices()`: Live snapshot for Coffee, Sugar, Cocoa, and Cotton.
- `get_crude_oil_price()`: Shortcut quote for WTI Crude Oil.
- `get_fertilizer_price_index()`: Green Markets North American Fertilizer Price Index weekly benchmark timeseries.

### 12. Foreign Exchange (`ForexService` — 5 tools)
- `get_forex_quote(pair)`: Real-time FX exchange rate (e.g. `EURUSD`, `USDJPY`, `GBPUSD`).
- `get_forex_history(pair, timeframe, step)`: Historical FX exchange rate timeseries.
- `get_dollar_index_dxy()`: Real-time quote for the US Dollar Index (DXY).
- `get_major_currencies()`: Currency matrix across EUR, GBP, JPY, CAD, AUD, CHF, CNH.
- `convert_currency(amount, from_currency, to_currency)`: Real-time currency conversion calculation.

### 13. ETFs & Mutual Funds (`FundsService` — 8 tools)
- `get_fund_info(ticker)`: ETF/Fund profile, expense ratio, AUM, category, and NAV.
- `get_fund_sector_weightings(ticker)`: Fund portfolio sector allocations and percentage weights.
- `get_fund_operations(ticker)`: Annual turnover, minimum investment, and operational parameters.
- `get_fund_overview(ticker)`: Unified fund overview with performance and fee metrics.
- `get_fund_top_holdings(ticker)`: Top underlying portfolio holdings and percentage weights.
- `get_fund_bond_holdings(ticker)`: Bond ratings breakdown, effective duration, and maturity metrics.
- `get_fund_equity_holdings(ticker)`: Equity price-to-earnings, price-to-book, and median market cap.
- `get_fund_asset_classes(ticker)`: Asset class allocations (Cash, Stocks, Bonds, Real Estate).

### 14. Cryptocurrency (`CryptoService` — 4 tools)
- `get_crypto_info(symbol)`: Cryptocurrency price, market cap, 24h volume, and circulating supply.
- `get_crypto_history(symbol, period, interval)`: Historical OHLCV crypto price bars.
- `get_top_cryptocurrencies(count)`: Leading cryptocurrencies ranked by market cap.
- `get_crypto_fear_greed_proxy()`: Volatility and momentum proxy for crypto market sentiment.

### 15. Macroeconomics & Federal Reserve Telemetry (`MacroeconomicsService` — 9 tools)
- `get_cpi_inflation(limit)`: US Consumer Price Index (Headline CPI & Core CPI) and YoY inflation rates.
- `get_pce_inflation(limit)`: US Core Personal Consumption Expenditures (PCE) Price Index (Fed's primary 2% inflation target).
- `get_employment_indicators(limit)`: Civilian Unemployment Rate (%) and Total Nonfarm Payrolls with monthly net job additions.
- `get_interest_rates_telemetry(limit)`: Benchmark US money market rates: Effective Federal Funds Rate (EFFR) and SOFR.
- `get_gdp_growth(limit)`: Real GDP ($B chained 2017) and Nominal GDP ($B) with quarter-over-quarter annualized real growth rates.
- `get_money_supply_and_fed_balance_sheet(limit)`: US M2 Money Supply ($B) and Federal Reserve Balance Sheet Total Assets ($M).
- `get_inflation_expectations(limit)`: 5-Year and 10-Year market-implied Breakeven Inflation Rates from TIPS.
- `get_financial_stress_and_credit_spreads(limit)`: St. Louis Fed Financial Stress Index and ICE BofA US High Yield OAS credit spreads.
- `get_macroeconomic_series(series_id, limit)`: Universal query tool for any valid FRED economic series identifier (e.g. `MORTGAGE30US`, `INDPRO`, `UMCSENT`).

### 16. SEC EDGAR Filings & XBRL Disclosures (`SECService` — 9 tools)
- `get_sec_company_profile(ticker)`: Official SEC corporate registrant profile, 10-digit CIK, SIC code, business address, and incorporation metadata.
- `get_sec_recent_filings(ticker, form_type, limit)`: Recent official regulatory submissions with direct HTTPS links to primary documents on SEC EDGAR.
- `get_sec_10k_annual_filings(ticker, limit)`: Form 10-K audited annual financial reports with direct primary document links.
- `get_sec_10q_quarterly_filings(ticker, limit)`: Form 10-Q quarterly reports with unaudited financial statements.
- `get_sec_8k_material_events(ticker, limit)`: Form 8-K unscheduled material corporate event announcements (earnings releases, executive changes, M&A).
- `get_sec_insider_form4_filings(ticker, limit)`: Form 4 insider transaction reports by officers, directors, and 10%+ beneficial owners.
- `get_sec_xbrl_company_facts(ticker)`: Catalog summary of all available interactive US-GAAP XBRL disclosure concepts filed by an entity.
- `get_sec_xbrl_concept_timeseries(ticker, concept, limit)`: Multi-quarter historical timeseries for standard GAAP concepts (`REVENUES`, `NET_INCOME`, `GROSS_PROFIT`, `ASSETS`, `CASH`, `EPS`).
- `get_sec_cik_lookup(query, limit)`: Fast search directory resolving company names and tickers to official 10-digit SEC CIKs across 10,000+ public entities.


---


## 🔧 HTTP Transport & Production Deployment

Open Markets can be run as a standalone HTTP service supporting SSE streaming, Bearer token authentication, CORS, and Prometheus metrics:

```bash
# Run streamable HTTP server with auth
uv run python -m openmarkets \
  --transport http \
  --host 0.0.0.0 \
  --port 8000 \
  --http-auth-enabled \
  --http-auth-secret "your-production-secret"
```

Endpoints:
- `GET /health` — Liveness & readiness probe.
- `GET /metrics` — Prometheus metrics (uptime, cache entries).
- `POST /` — MCP streamable JSON-RPC endpoint.

---

## 🧪 Testing & Validation

Open Markets maintains a comprehensive suite of unit tests, property tests, and live network integration tests:

```bash
# Run all unit tests with coverage enforcement (95%+ achieved)
uv run pytest

# Run live endpoint integration tests against real APIs
uv run pytest -m live -o addopts="" tests/live/

# Run code formatters and type checkers
uv run ruff format && uv run ruff check && uv run pyright
```

---

## 📄 License

AGPLv3+ License — see [LICENSE](LICENSE) for details.