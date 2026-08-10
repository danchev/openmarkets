"""Core client utilities for Federal Reserve Economic Data (FRED).

Fetches public macroeconomic timeseries data from the Federal Reserve Bank of St. Louis
without requiring mandatory API keys.
"""

from typing import Any

from curl_cffi.requests import Session

from openmarkets.core.http import get_session

# Catalog of primary macroeconomic series metadata
FRED_SERIES_CATALOG: dict[str, dict[str, str]] = {
    "CPIAUCSL": {
        "title": "Consumer Price Index for All Urban Consumers: All Items",
        "units": "Index 1982-1984=100",
        "frequency": "Monthly",
    },
    "CPILFESL": {
        "title": "Core CPI (All Items Less Food and Energy)",
        "units": "Index 1982-1984=100",
        "frequency": "Monthly",
    },
    "PCEPILFE": {
        "title": "Core PCE Price Index (Excluding Food and Energy)",
        "units": "Index 2017=100",
        "frequency": "Monthly",
    },
    "FEDFUNDS": {
        "title": "Effective Federal Funds Rate",
        "units": "Percent",
        "frequency": "Monthly",
    },
    "DFF": {
        "title": "Daily Effective Federal Funds Rate",
        "units": "Percent",
        "frequency": "Daily",
    },
    "SOFR": {
        "title": "Secured Overnight Financing Rate",
        "units": "Percent",
        "frequency": "Daily",
    },
    "UNRATE": {
        "title": "Civilian Unemployment Rate",
        "units": "Percent",
        "frequency": "Monthly",
    },
    "PAYEMS": {
        "title": "All Employees, Total Nonfarm Payrolls",
        "units": "Thousands of Persons",
        "frequency": "Monthly",
    },
    "GDPC1": {
        "title": "Real Gross Domestic Product",
        "units": "Billions of Chained 2017 Dollars",
        "frequency": "Quarterly",
    },
    "GDP": {
        "title": "Gross Domestic Product (Nominal)",
        "units": "Billions of Dollars",
        "frequency": "Quarterly",
    },
    "M2SL": {
        "title": "M2 Money Supply",
        "units": "Billions of Dollars",
        "frequency": "Monthly",
    },
    "WALCL": {
        "title": "Federal Reserve Total Assets (Balance Sheet)",
        "units": "Millions of Dollars",
        "frequency": "Weekly",
    },
    "T10YIE": {
        "title": "10-Year Breakeven Inflation Rate",
        "units": "Percent",
        "frequency": "Daily",
    },
    "T5YIE": {
        "title": "5-Year Breakeven Inflation Rate",
        "units": "Percent",
        "frequency": "Daily",
    },
    "T10Y2Y": {
        "title": "10-Year Treasury Minus 2-Year Treasury Yield Spread",
        "units": "Percent",
        "frequency": "Daily",
    },
    "STLFSI4": {
        "title": "St. Louis Fed Financial Stress Index",
        "units": "Index",
        "frequency": "Weekly",
    },
    "BAMLH0A0HYM2": {
        "title": "ICE BofA US High Yield Index Option-Adjusted Spread",
        "units": "Percent",
        "frequency": "Daily",
    },
}

_FRED_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/csv,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch_fred_timeseries(
    series_id: str,
    session: Session | None = None,
    timeout: float = 10.0,
) -> list[dict[str, Any]]:
    """Fetch timeseries data for a given FRED series ID.

    Args:
        series_id: The FRED series identifier (e.g. 'CPIAUCSL', 'FEDFUNDS').
        session: Optional curl_cffi Session instance.
        timeout: Request timeout in seconds.

    Returns:
        List of dicts with 'date' (YYYY-MM-DD) and 'value' (float).

    Raises:
        ValueError: If the series cannot be retrieved or is invalid.
    """
    series_key = series_id.strip().upper()
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_key}"
    sess = session or get_session()

    try:
        resp = sess.get(url, headers=_FRED_HEADERS, timeout=timeout)
    except Exception as e:
        raise ValueError(f"Failed to fetch FRED series '{series_key}': {e}") from e

    if resp.status_code != 200:
        raise ValueError(f"FRED endpoint returned HTTP {resp.status_code} for series '{series_key}'")

    lines = resp.text.strip().splitlines()
    if len(lines) <= 1:
        raise ValueError(f"Empty or invalid response from FRED for series '{series_key}'")

    results: list[dict[str, Any]] = []
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) < 2:
            continue
        date_str, val_str = parts[0].strip(), parts[1].strip()
        if not date_str or val_str in (".", "", "ND", "null"):
            continue
        try:
            val = float(val_str)
            results.append({"date": date_str, "value": val})
        except ValueError:
            continue

    if not results:
        raise ValueError(f"No valid data points parsed for FRED series '{series_key}'")

    return results
