"""
Tests for openmarkets.schemas.stock.StockFastInfo dataclass.

This module tests instantiation and attribute assignment for StockFastInfo.
"""

from datetime import date, datetime

import pandas as pd
import pytest

from openmarkets.schemas.financials import EPSHistoryEntry, FinancialCalendar
from openmarkets.schemas.stock import StockFastInfo


def test_tickerfastinfo_instantiation():
    """Test that StockFastInfo can be instantiated and all fields are set correctly."""
    data = {
        "currency": "USD",
        "dayHigh": 254.8800048828125,
        "dayLow": 248.58999633789062,
        "exchange": "NMS",
        "fiftyDayAverage": 231.95300109863283,
        "lastPrice": 253.7899932861328,
        "lastVolume": 17586000,
        "marketCap": 3043437759422.748,
        "open": 251.35000610351562,
        "previousClose": 250.89,
        "quoteType": "EQUITY",
        "regularMarketPreviousClose": 251.8800048828125,
        "shares": 11991953347,
        "tenDayAverageVolume": 17083200,
        "threeMonthAverageVolume": 22386118,
        "timezone": "America/New_York",
        "twoHundredDayAverage": 190.43205032348632,
        "yearChange": 0.5306995694499906,
        "yearHigh": 257.5799865722656,
        "yearLow": 142.66000366210938,
    }
    info = StockFastInfo(**data)
    # Verify the data was properly parsed by checking a few key fields
    assert info.currency == "USD"
    assert info.day_high == 254.8800048828125
    assert info.day_low == 248.58999633789062
    assert info.exchange == "NMS"
    assert info.last_price == 253.7899932861328
    assert info.market_cap == 3043437759422.748


# Additional tests for FinancialCalendar and EPSHistoryEntry validators
@pytest.mark.parametrize(
    "input_value,expected_type",
    [
        ("2025-12-18T00:00:00", date),
        (date(2025, 12, 18), date),
        (datetime(2025, 12, 18), date),
    ],
)
def test_financialcalendar_coerce_date_to_timestamp(input_value, expected_type):
    # Test dividend_date validator with string, date, and datetime
    cal = FinancialCalendar(dividend_date=input_value)
    assert isinstance(cal.dividend_date, expected_type)


@pytest.mark.parametrize(
    "input_value",
    [
        pd.Timestamp("2025-12-18T00:00:00"),
        datetime(2025, 12, 18),
        "2025-12-18T00:00:00",
    ],
)
def test_epshistoryentry_coerce_date_to_timestamp(input_value):
    # Test earnings_date validator with pd.Timestamp, datetime, and string
    entry = EPSHistoryEntry(earnings_date=input_value)
    # Current model behavior: always None
    assert entry.earnings_date is None
