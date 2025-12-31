"""
Tests for openmarkets.schemas.analysis.AnalystRecommendationChange Date validator.
"""

from datetime import datetime

import pytest

from openmarkets.schemas.analysis import AnalystRecommendationChange


@pytest.mark.parametrize(
    ("date_input", "expected_output"),
    [
        (None, None),
        (datetime(2023, 1, 1), datetime(2023, 1, 1)),
        ("2023-01-01", datetime(2023, 1, 1)),
        ("not-a-date", None),
    ],
)
def test_date_validator(date_input, expected_output):
    """Test AnalystRecommendationChange date validator with various inputs."""
    obj = AnalystRecommendationChange(Date=date_input)
    if expected_output is None:
        assert obj.date is None
    elif isinstance(expected_output, datetime):
        assert isinstance(obj.date, datetime)
        if date_input == "2023-01-01":
            assert obj.date.year == 2023 and obj.date.month == 1 and obj.date.day == 1
        else:
            assert obj.date == expected_output
