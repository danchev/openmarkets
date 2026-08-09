"""Low-level client for Wall Street Journal (WSJ) Michelangelo timeseries API."""

import json
import logging
from typing import Any

from curl_cffi.requests import Session

from openmarkets.core.http import get_session, retry_with_backoff

logger = logging.getLogger(__name__)

WSJ_TIMESERIES_URL = "https://api.wsj.net/api/michelangelo/timeseries/history"
DEFAULT_ENTITLEMENT_TOKEN = "57494d5ed7ad44af85bc59a51dd87c90"
DEFAULT_CKEY = "57494d5ed7"

# Friendly symbol / alias to WSJ Michelangelo Series Key mapping
SYMBOL_MAP: dict[str, dict[str, str]] = {
    # Energy
    "CRUDE_OIL": {"key": "FUTURE/US/XNYM/CL00", "name": "Crude Oil (WTI)", "exchange": "NYMEX", "unit": "USD/bbl"},
    "WTI": {"key": "FUTURE/US/XNYM/CL00", "name": "Crude Oil (WTI)", "exchange": "NYMEX", "unit": "USD/bbl"},
    "CL": {"key": "FUTURE/US/XNYM/CL00", "name": "Crude Oil (WTI)", "exchange": "NYMEX", "unit": "USD/bbl"},
    "BRENT_CRUDE": {"key": "FUTURE/UK/IFEU/B00", "name": "Brent Crude Oil", "exchange": "ICE", "unit": "USD/bbl"},
    "BZ": {"key": "FUTURE/UK/IFEU/B00", "name": "Brent Crude Oil", "exchange": "ICE", "unit": "USD/bbl"},
    "NATURAL_GAS": {"key": "FUTURE/US/XNYM/NG00", "name": "Natural Gas", "exchange": "NYMEX", "unit": "USD/MMBtu"},
    "NG": {"key": "FUTURE/US/XNYM/NG00", "name": "Natural Gas", "exchange": "NYMEX", "unit": "USD/MMBtu"},
    "GASOLINE": {"key": "FUTURE/US/XNYM/RB00", "name": "RBOB Gasoline", "exchange": "NYMEX", "unit": "USD/gal"},
    "RB": {"key": "FUTURE/US/XNYM/RB00", "name": "RBOB Gasoline", "exchange": "NYMEX", "unit": "USD/gal"},
    "HEATING_OIL": {"key": "FUTURE/US/XNYM/HO00", "name": "Heating Oil", "exchange": "NYMEX", "unit": "USD/gal"},
    "HO": {"key": "FUTURE/US/XNYM/HO00", "name": "Heating Oil", "exchange": "NYMEX", "unit": "USD/gal"},
    # Metals
    "GOLD": {"key": "FUTURE/US/XCEC/GC00", "name": "Gold", "exchange": "COMEX", "unit": "USD/troy oz"},
    "GC": {"key": "FUTURE/US/XCEC/GC00", "name": "Gold", "exchange": "COMEX", "unit": "USD/troy oz"},
    "SILVER": {"key": "FUTURE/US/XCEC/SI00", "name": "Silver", "exchange": "COMEX", "unit": "USD/troy oz"},
    "SI": {"key": "FUTURE/US/XCEC/SI00", "name": "Silver", "exchange": "COMEX", "unit": "USD/troy oz"},
    "COPPER": {"key": "FUTURE/US/XCEC/HG00", "name": "Copper", "exchange": "COMEX", "unit": "USD/lb"},
    "HG": {"key": "FUTURE/US/XCEC/HG00", "name": "Copper", "exchange": "COMEX", "unit": "USD/lb"},
    "PLATINUM": {"key": "FUTURE/US/XNYM/PL00", "name": "Platinum", "exchange": "NYMEX", "unit": "USD/troy oz"},
    "PL": {"key": "FUTURE/US/XNYM/PL00", "name": "Platinum", "exchange": "NYMEX", "unit": "USD/troy oz"},
    # Agriculture
    "WHEAT": {"key": "FUTURE/US/XCBT/W00", "name": "Wheat", "exchange": "CBOT", "unit": "USD/bushel"},
    "W": {"key": "FUTURE/US/XCBT/W00", "name": "Wheat", "exchange": "CBOT", "unit": "USD/bushel"},
    "CORN": {"key": "FUTURE/US/XCBT/C00", "name": "Corn", "exchange": "CBOT", "unit": "USD/bushel"},
    "C": {"key": "FUTURE/US/XCBT/C00", "name": "Corn", "exchange": "CBOT", "unit": "USD/bushel"},
    "SOYBEANS": {"key": "FUTURE/US/XCBT/S00", "name": "Soybeans", "exchange": "CBOT", "unit": "USD/bushel"},
    "S": {"key": "FUTURE/US/XCBT/S00", "name": "Soybeans", "exchange": "CBOT", "unit": "USD/bushel"},
    "COFFEE": {"key": "FUTURE/US/XCEC/KC00", "name": "Coffee", "exchange": "ICE", "unit": "USD/lb"},
    "KC": {"key": "FUTURE/US/XCEC/KC00", "name": "Coffee", "exchange": "ICE", "unit": "USD/lb"},
    "SUGAR": {"key": "FUTURE/US/XCEC/SB00", "name": "Sugar", "exchange": "ICE", "unit": "USD/lb"},
    "SB": {"key": "FUTURE/US/XCEC/SB00", "name": "Sugar", "exchange": "ICE", "unit": "USD/lb"},
    # Fixed Income / US Treasuries
    "US01M": {
        "key": "BOND/US/TMUBMUSD01M",
        "name": "US 1-Month Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    "US03M": {
        "key": "BOND/US/TMUBMUSD03M",
        "name": "US 3-Month Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    "US06M": {
        "key": "BOND/US/TMUBMUSD06M",
        "name": "US 6-Month Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    "US01Y": {"key": "BOND/US/TMUBMUSD01Y", "name": "US 1-Year Treasury Yield", "exchange": "US Treasury", "unit": "%"},
    "US02Y": {"key": "BOND/US/TMUBMUSD02Y", "name": "US 2-Year Treasury Yield", "exchange": "US Treasury", "unit": "%"},
    "US05Y": {"key": "BOND/US/TMUBMUSD05Y", "name": "US 5-Year Treasury Yield", "exchange": "US Treasury", "unit": "%"},
    "US10Y": {
        "key": "BOND/US/TMUBMUSD10Y",
        "name": "US 10-Year Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
    "US30Y": {
        "key": "BOND/US/TMUBMUSD30Y",
        "name": "US 30-Year Treasury Yield",
        "exchange": "US Treasury",
        "unit": "%",
    },
}


def resolve_wsj_key(symbol_or_key: str) -> tuple[str, str, str, str]:
    """Resolve a symbol alias or raw key into (wsj_key, name, exchange, unit)."""
    norm = symbol_or_key.strip().upper()
    if norm in SYMBOL_MAP:
        meta = SYMBOL_MAP[norm]
        return meta["key"], meta["name"], meta["exchange"], meta["unit"]

    # Direct WSJ key format (e.g. FUTURE/US/XCBT/W00 or BOND/US/TMUBMUSD10Y or STOCK/US/XNAS/TSLA)
    if "/" in symbol_or_key:
        return symbol_or_key, symbol_or_key, "Unknown", "USD"

    # Default fallback to stock key format
    return f"STOCK/US/XNAS/{norm}", norm, "NASDAQ", "USD"


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


@retry_with_backoff(retries=3, initial_delay=0.5, backoff_factor=2.0)
def fetch_wsj_timeseries(
    wsj_key: str,
    step: str = "P1D",
    timeframe: str = "P1Y",
    datatypes: list[str] | None = None,
    session: Session | None = None,
) -> dict[str, Any]:
    """Fetch timeseries data from WSJ Michelangelo API.

    Args:
        wsj_key: The series key (e.g. ``FUTURE/US/XCBT/W00``).
        step: Bar step frequency (e.g. ``P1D``, ``PT1M``).
        timeframe: Timespan duration (e.g. ``P1Y``, ``D7``, ``all``).
        datatypes: List of data types requested (defaults to ``["Open", "High", "Low", "Last"]``).
        session: Optional ``curl_cffi`` session.

    Returns:
        The raw JSON response from WSJ.
    """
    if datatypes is None:
        datatypes = ["Open", "High", "Low", "Last"]

    payload = {
        "Step": step,
        "TimeFrame": timeframe,
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
        "Series": [
            {
                "Key": wsj_key,
                "Dialect": "Charting",
                "Kind": "Ticker",
                "SeriesId": "s1",
                "DataTypes": datatypes,
                "Indicators": [{"Parameters": [], "Kind": "Volume", "SeriesId": "i3"}],
            }
        ],
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
    data: dict[str, Any] = response.json()
    return data
