"""Low-level client for Wall Street Journal (WSJ) Michelangelo timeseries API."""

import json
import logging
from typing import Any

from curl_cffi.requests import Session

from openmarkets.core.exceptions import ProviderContractError
from openmarkets.core.http import get_session, retry_with_backoff

logger = logging.getLogger(__name__)

WSJ_TIMESERIES_URL = "https://api.wsj.net/api/michelangelo/timeseries/history"
# This is WSJ's published client entitlement value, not an OpenMarkets
# credential. It is sent as part of the public endpoint contract.
DEFAULT_ENTITLEMENT_TOKEN = "57494d5ed7ad44af85bc59a51dd87c90"  # nosec B105
DEFAULT_CKEY = "57494d5ed7"

# Friendly symbol / alias to WSJ Michelangelo Series Key mapping
SYMBOL_MAP: dict[str, dict[str, str]] = {
    # Energy
    "CRUDE_OIL": {"key": "FUTURE/US/XNYM/CL00", "name": "Crude Oil (WTI)", "exchange": "NYMEX", "unit": "USD/bbl"},
    "WTI": {"key": "FUTURE/US/XNYM/CL00", "name": "Crude Oil (WTI)", "exchange": "NYMEX", "unit": "USD/bbl"},
    "CL": {"key": "FUTURE/US/XNYM/CL00", "name": "Crude Oil (WTI)", "exchange": "NYMEX", "unit": "USD/bbl"},
    "BRENT_CRUDE": {"key": "FUTURE/UK/IFEU/BRN00", "name": "Brent Crude Oil", "exchange": "ICE", "unit": "USD/bbl"},
    "BZ": {"key": "FUTURE/UK/IFEU/BRN00", "name": "Brent Crude Oil", "exchange": "ICE", "unit": "USD/bbl"},
    "NATURAL_GAS": {"key": "FUTURE/US/XNYM/NG00", "name": "Natural Gas", "exchange": "NYMEX", "unit": "USD/MMBtu"},
    "NG": {"key": "FUTURE/US/XNYM/NG00", "name": "Natural Gas", "exchange": "NYMEX", "unit": "USD/MMBtu"},
    "GASOLINE": {"key": "FUTURE/US/XNYM/RB00", "name": "RBOB Gasoline", "exchange": "NYMEX", "unit": "USD/gal"},
    "RB": {"key": "FUTURE/US/XNYM/RB00", "name": "RBOB Gasoline", "exchange": "NYMEX", "unit": "USD/gal"},
    "HEATING_OIL": {"key": "FUTURE/US/XNYM/HO00", "name": "Heating Oil", "exchange": "NYMEX", "unit": "USD/gal"},
    "HO": {"key": "FUTURE/US/XNYM/HO00", "name": "Heating Oil", "exchange": "NYMEX", "unit": "USD/gal"},
    # Metals
    "GOLD": {"key": "FUTURE/US/XNYM/GC00", "name": "Gold", "exchange": "COMEX", "unit": "USD/troy oz"},
    "GC": {"key": "FUTURE/US/XNYM/GC00", "name": "Gold", "exchange": "COMEX", "unit": "USD/troy oz"},
    "SILVER": {"key": "FUTURE/US/XNYM/SI00", "name": "Silver", "exchange": "COMEX", "unit": "USD/troy oz"},
    "SI": {"key": "FUTURE/US/XNYM/SI00", "name": "Silver", "exchange": "COMEX", "unit": "USD/troy oz"},
    "COPPER": {"key": "FUTURE/US/XNYM/HG00", "name": "Copper", "exchange": "COMEX", "unit": "USD/lb"},
    "HG": {"key": "FUTURE/US/XNYM/HG00", "name": "Copper", "exchange": "COMEX", "unit": "USD/lb"},
    "PLATINUM": {"key": "FUTURE/US/XNYM/PL00", "name": "Platinum", "exchange": "NYMEX", "unit": "USD/troy oz"},
    "PL": {"key": "FUTURE/US/XNYM/PL00", "name": "Platinum", "exchange": "NYMEX", "unit": "USD/troy oz"},
    # Agriculture
    "WHEAT": {"key": "FUTURE/US/XCBT/W00", "name": "Wheat", "exchange": "CBOT", "unit": "USD/bushel"},
    "W": {"key": "FUTURE/US/XCBT/W00", "name": "Wheat", "exchange": "CBOT", "unit": "USD/bushel"},
    "CORN": {"key": "FUTURE/US/XCBT/C00", "name": "Corn", "exchange": "CBOT", "unit": "USD/bushel"},
    "C": {"key": "FUTURE/US/XCBT/C00", "name": "Corn", "exchange": "CBOT", "unit": "USD/bushel"},
    "SOYBEANS": {"key": "FUTURE/US/XCBT/S00", "name": "Soybeans", "exchange": "CBOT", "unit": "USD/bushel"},
    "S": {"key": "FUTURE/US/XCBT/S00", "name": "Soybeans", "exchange": "CBOT", "unit": "USD/bushel"},
    "COFFEE": {"key": "FUTURE/US//KC00", "name": "Coffee", "exchange": "ICE", "unit": "USD/lb"},
    "KC": {"key": "FUTURE/US//KC00", "name": "Coffee", "exchange": "ICE", "unit": "USD/lb"},
    "SUGAR": {"key": "FUTURE/US//SB00", "name": "Sugar", "exchange": "ICE", "unit": "USD/lb"},
    "SB": {"key": "FUTURE/US//SB00", "name": "Sugar", "exchange": "ICE", "unit": "USD/lb"},
    # Softs & Additional Agriculture
    "COCOA": {"key": "FUTURE/US//CC00", "name": "Cocoa", "exchange": "ICE", "unit": "USD/metric ton"},
    "CC": {"key": "FUTURE/US//CC00", "name": "Cocoa", "exchange": "ICE", "unit": "USD/metric ton"},
    "COTTON": {"key": "FUTURE/US//CT00", "name": "Cotton", "exchange": "ICE", "unit": "USD/lb"},
    "CT": {"key": "FUTURE/US//CT00", "name": "Cotton", "exchange": "ICE", "unit": "USD/lb"},
    # Livestock
    "LIVE_CATTLE": {"key": "FUTURE/US/XCME/LC00", "name": "Live Cattle", "exchange": "CME", "unit": "USD/cwt"},
    "LC": {"key": "FUTURE/US/XCME/LC00", "name": "Live Cattle", "exchange": "CME", "unit": "USD/cwt"},
    "FEEDER_CATTLE": {"key": "FUTURE/US/XCME/FC00", "name": "Feeder Cattle", "exchange": "CME", "unit": "USD/cwt"},
    "FC": {"key": "FUTURE/US/XCME/FC00", "name": "Feeder Cattle", "exchange": "CME", "unit": "USD/cwt"},
    "LEAN_HOGS": {"key": "FUTURE/US/XCME/LH00", "name": "Lean Hogs", "exchange": "CME", "unit": "USD/cwt"},
    "LH": {"key": "FUTURE/US/XCME/LH00", "name": "Lean Hogs", "exchange": "CME", "unit": "USD/cwt"},
    # Additional Metals
    "PALLADIUM": {"key": "FUTURE/US/XNYM/PA00", "name": "Palladium", "exchange": "NYMEX", "unit": "USD/troy oz"},
    "PA": {"key": "FUTURE/US/XNYM/PA00", "name": "Palladium", "exchange": "NYMEX", "unit": "USD/troy oz"},
    # Fixed Income / US Treasuries
    "US01M": {
        "key": "BOND/BX/XTUP/TMUBMUSD01M",
        "name": "US 1-Month Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    "US03M": {
        "key": "BOND/BX/XTUP/TMUBMUSD03M",
        "name": "US 3-Month Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    "US06M": {
        "key": "BOND/BX/XTUP/TMUBMUSD06M",
        "name": "US 6-Month Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    "US01Y": {
        "key": "BOND/BX/XTUP/TMUBMUSD01Y",
        "name": "US 1-Year Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    "US02Y": {
        "key": "BOND/BX/XTUP/TMUBMUSD02Y",
        "name": "US 2-Year Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    "US05Y": {
        "key": "BOND/BX/XTUP/TMUBMUSD05Y",
        "name": "US 5-Year Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    "US10Y": {
        "key": "BOND/BX/XTUP/TMUBMUSD10Y",
        "name": "US 10-Year Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    "US30Y": {
        "key": "BOND/BX/XTUP/TMUBMUSD30Y",
        "name": "US 30-Year Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    # Global Benchmark Sovereign Yields
    "DE10Y": {
        "key": "BOND/BX/XTUP/TMBMKDE-10Y",
        "name": "Germany 10-Year Bund Yield",
        "exchange": "Deutsche Bundesbank",
        "unit": "%",
    },
    "UK10Y": {
        "key": "BOND/BX/XTUP/TMBMKGB-10Y",
        "name": "UK 10-Year Gilt Yield",
        "exchange": "UK DMO",
        "unit": "%",
    },
    "JP10Y": {
        "key": "BOND/BX/XTUP/TMBMKJP-10Y",
        "name": "Japan 10-Year JGB Yield",
        "exchange": "Ministry of Finance Japan",
        "unit": "%",
    },
    "CA10Y": {
        "key": "BOND/BX/XTUP/TMBMKCA-10Y",
        "name": "Canada 10-Year Benchmark Yield",
        "exchange": "Bank of Canada",
        "unit": "%",
    },
    "FR10Y": {
        "key": "BOND/BX/XTUP/TMBMKFR-10Y",
        "name": "France 10-Year OAT Yield",
        "exchange": "Agence France Trésor",
        "unit": "%",
    },
    "IT10Y": {
        "key": "BOND/BX/XTUP/TMBMKIT-10Y",
        "name": "Italy 10-Year BTP Yield",
        "exchange": "Ministero Economia Finanze",
        "unit": "%",
    },
    "AU10Y": {
        "key": "BOND/BX/XTUP/TMBMKAU-10Y",
        "name": "Australia 10-Year Sovereign Yield",
        "exchange": "RBA",
        "unit": "%",
    },
    "ES10Y": {
        "key": "BOND/BX/XTUP/TMBMKES-10Y",
        "name": "Spain 10-Year Bonos Yield",
        "exchange": "Tesoro Público",
        "unit": "%",
    },
    # Foreign Exchange / Currencies (Forex)
    "EURUSD": {"key": "CURRENCY/US//EURUSD", "name": "EUR/USD", "exchange": "Forex", "unit": "USD"},
    "USDJPY": {"key": "CURRENCY/US//USDJPY", "name": "USD/JPY", "exchange": "Forex", "unit": "JPY"},
    "GBPUSD": {"key": "CURRENCY/US//GBPUSD", "name": "GBP/USD", "exchange": "Forex", "unit": "USD"},
    "AUDUSD": {"key": "CURRENCY/US//AUDUSD", "name": "AUD/USD", "exchange": "Forex", "unit": "USD"},
    "USDCAD": {"key": "CURRENCY/US//USDCAD", "name": "USD/CAD", "exchange": "Forex", "unit": "CAD"},
    "USDCHF": {"key": "CURRENCY/US//USDCHF", "name": "USD/CHF", "exchange": "Forex", "unit": "CHF"},
    "USDCNY": {"key": "CURRENCY/US//USDCNY", "name": "USD/CNY", "exchange": "Forex", "unit": "CNY"},
    "USDMXN": {"key": "CURRENCY/US//USDMXN", "name": "USD/MXN", "exchange": "Forex", "unit": "MXN"},
    "USDINR": {"key": "CURRENCY/US//USDINR", "name": "USD/INR", "exchange": "Forex", "unit": "INR"},
    "DXY": {"key": "INDEX/US//DXY", "name": "US Dollar Index (DXY)", "exchange": "ICE", "unit": "Index"},
    # Major Market Benchmark Indexes & Volatility
    "SPX": {"key": "INDEX/US//SPX", "name": "S&P 500 Index", "exchange": "S&P Dow Jones", "unit": "Index"},
    "SP500": {"key": "INDEX/US//SPX", "name": "S&P 500 Index", "exchange": "S&P Dow Jones", "unit": "Index"},
    "DJIA": {
        "key": "INDEX/US//DJIA",
        "name": "Dow Jones Industrial Average",
        "exchange": "S&P Dow Jones",
        "unit": "Index",
    },
    "COMP": {"key": "INDEX/US//COMP", "name": "Nasdaq Composite Index", "exchange": "NASDAQ", "unit": "Index"},
    "NASDAQ": {"key": "INDEX/US//COMP", "name": "Nasdaq Composite Index", "exchange": "NASDAQ", "unit": "Index"},
    "RUT": {"key": "INDEX/US//RUT", "name": "Russell 2000 Index", "exchange": "FTSE Russell", "unit": "Index"},
    "RUSSELL2000": {"key": "INDEX/US//RUT", "name": "Russell 2000 Index", "exchange": "FTSE Russell", "unit": "Index"},
    "VIX": {"key": "INDEX/US//VIX", "name": "CBOE Volatility Index (VIX)", "exchange": "CBOE", "unit": "Index"},
    "DAX": {"key": "INDEX/DX//DAX", "name": "DAX 40 Index", "exchange": "Deutsche Börse", "unit": "Index"},
    "FTSE": {"key": "INDEX/UK//UKX", "name": "FTSE 100 Index", "exchange": "FTSE Russell", "unit": "Index"},
    "FTSE100": {"key": "INDEX/UK//UKX", "name": "FTSE 100 Index", "exchange": "FTSE Russell", "unit": "Index"},
    "CAC": {"key": "INDEX/FR//PX1", "name": "CAC 40 Index", "exchange": "Euronext Paris", "unit": "Index"},
    "CAC40": {"key": "INDEX/FR//PX1", "name": "CAC 40 Index", "exchange": "Euronext Paris", "unit": "Index"},
    "SX5E": {"key": "INDEX/XX//SX5E", "name": "Euro Stoxx 50 Index", "exchange": "STOXX", "unit": "Index"},
    "EUROSTOXX50": {"key": "INDEX/XX//SX5E", "name": "Euro Stoxx 50 Index", "exchange": "STOXX", "unit": "Index"},
    "NIKKEI": {"key": "INDEX/JP//NI225", "name": "Nikkei 225 Index", "exchange": "Nikkei Inc.", "unit": "Index"},
    "NIKKEI225": {"key": "INDEX/JP//NI225", "name": "Nikkei 225 Index", "exchange": "Nikkei Inc.", "unit": "Index"},
    "HSI": {"key": "INDEX/HK/XHKG/HSI", "name": "Hang Seng Index", "exchange": "Hang Seng Indexes", "unit": "Index"},
    "HANGSENG": {
        "key": "INDEX/HK/XHKG/HSI",
        "name": "Hang Seng Index",
        "exchange": "Hang Seng Indexes",
        "unit": "Index",
    },
}


def resolve_wsj_key(symbol_or_key: str) -> tuple[str, str, str, str]:
    """Resolve a symbol alias or raw key into (wsj_key, name, exchange, unit)."""
    norm = symbol_or_key.strip().upper()
    if norm in SYMBOL_MAP:
        meta = SYMBOL_MAP[norm]
        return meta["key"], meta["name"], meta["exchange"], meta["unit"]

    # Check without slashes (e.g. 'EUR/USD' -> 'EURUSD')
    stripped = norm.replace("/", "")
    if stripped in SYMBOL_MAP:
        meta = SYMBOL_MAP[stripped]
        return meta["key"], meta["name"], meta["exchange"], meta["unit"]

    # Direct WSJ key format (e.g. FUTURE/US/XCBT/W00 or BOND/US/TMUBMUSD10Y or STOCK/US/XNAS/TSLA)
    if any(norm.startswith(prefix) for prefix in ("STOCK/", "FUTURE/", "BOND/", "INDEX/", "CURRENCY/")):
        return symbol_or_key, symbol_or_key, "Unknown", "USD"

    # Default fallback to universal stock key format
    return f"STOCK/US//{norm}", norm, "US Equity", "USD"


def _build_wsj_headers(token: str = DEFAULT_ENTITLEMENT_TOKEN) -> dict[str, str]:
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Dylan2010.EntitlementToken": token,
        "Origin": "https://www.wsj.com",
        "Referer": "https://www.wsj.com/",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }


TIMEFRAME_MAP: dict[str, str] = {
    "1D": "D1",
    "5D": "D5",
    "7D": "D7",
    "1MO": "P1M",
    "1M": "P1M",
    "M1": "P1M",
    "3MO": "P3M",
    "3M": "P3M",
    "M3": "P3M",
    "6MO": "P6M",
    "6M": "P6M",
    "M6": "P6M",
    "1Y": "P1Y",
    "Y1": "P1Y",
    "5Y": "P5Y",
    "Y5": "P5Y",
    "MAX": "all",
    "ALL": "all",
}


def normalize_wsj_timeframe(timeframe: str) -> str:
    """Normalize human timeframe strings (e.g. '1y', '1mo', '5y') to WSJ ISO durations."""
    norm = timeframe.strip().upper()
    return TIMEFRAME_MAP.get(norm, timeframe)


@retry_with_backoff(retries=3, initial_delay=0.5, backoff_factor=2.0)
def fetch_wsj_timeseries(
    wsj_key: str,
    step: str = "P1D",
    timeframe: str = "P1Y",
    datatypes: list[str] | None = None,
    indicators: list[dict[str, Any]] | None = None,
    session: Session | None = None,
) -> dict[str, Any]:
    """Fetch timeseries data from WSJ Michelangelo API.

    Args:
        wsj_key: The series key (e.g. ``FUTURE/US/XCBT/W00``).
        step: Bar step frequency (e.g. ``P1D``, ``PT1M``).
        timeframe: Timespan duration (e.g. ``P1Y``, ``D7``, ``all``).
        datatypes: List of data types requested (defaults to ``["Open", "High", "Low", "Last"]``).
        indicators: Optional list of server-side indicators (e.g. Bollinger Bands).
        session: Optional ``curl_cffi`` session.

    Returns:
        The raw JSON response from WSJ.
    """
    if not wsj_key.strip():
        raise ValueError("wsj_key must not be empty")
    if not step.strip():
        raise ValueError("step must not be empty")
    if not timeframe.strip():
        raise ValueError("timeframe must not be empty")
    if datatypes is None:
        datatypes = ["Open", "High", "Low", "Last"]
    elif not datatypes:
        raise ValueError("datatypes must contain at least one value")

    valid_timeframe = normalize_wsj_timeframe(timeframe)

    series_obj: dict[str, Any] = {
        "Key": wsj_key,
        "Dialect": "Charting",
        "Kind": "Ticker",
        "SeriesId": "s1",
        "DataTypes": datatypes,
    }
    if indicators:
        series_obj["Indicators"] = indicators
    elif not wsj_key.startswith("BOND/"):
        series_obj["Indicators"] = [{"Parameters": [], "Kind": "Volume", "SeriesId": "i3"}]

    payload = {
        "Step": step,
        "TimeFrame": valid_timeframe,
        "EntitlementToken": DEFAULT_ENTITLEMENT_TOKEN,
        "IncludeMockTick": True,
        "FilterNullSlots": False,
        "FilterClosedPoints": True,
        "IncludeClosedSlots": False,
        "IncludeOfficialClose": True,
        "InjectOpen": False,
        "ShowPreMarket": True,
        "ShowAfterHours": True,
        "UseExtendedTimeFrame": True,
        "WantPriorClose": False,
        "IncludeCurrentQuotes": False,
        "ResetTodaysAfterHoursPercentChange": False,
        "Series": [series_obj],
    }

    params = {
        "json": json.dumps(payload),
        "ckey": DEFAULT_CKEY,
    }

    headers = _build_wsj_headers()
    http_session = session or get_session()

    response = http_session.get(
        WSJ_TIMESERIES_URL,
        headers=headers,
        params=params,
        timeout=15.0,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ProviderContractError(f"WSJ timeseries returned {type(data).__name__}; expected a JSON object")
    return data
