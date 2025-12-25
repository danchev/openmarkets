"""
Tests for openmarkets.schemas.analysis.AnalystRecommendationChange Date validator.
"""

from datetime import datetime

from openmarkets.schemas.analysis import AnalystRecommendationChange


def test_date_validator_none():
    # Should return None if Date is None
    obj = AnalystRecommendationChange(Date=None)
    assert obj.Date is None


def test_date_validator_datetime():
    # Should return the datetime as-is if Date is already a datetime
    dt = datetime(2023, 1, 1)
    obj = AnalystRecommendationChange(Date=dt)
    assert obj.Date == dt


def test_date_validator_valid_string():
    # Should parse a valid date string
    obj = AnalystRecommendationChange(Date="2023-01-01")
    assert isinstance(obj.Date, datetime)
    assert obj.Date.year == 2023 and obj.Date.month == 1 and obj.Date.day == 1


def test_date_validator_invalid_string():
    # Should return None for an invalid date string
    obj = AnalystRecommendationChange(Date="not-a-date")
    assert obj.Date is None
