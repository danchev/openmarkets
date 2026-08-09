"""Unit tests for WSJFixedIncomeRepository."""

from unittest.mock import patch

from openmarkets.repositories.fixed_income import WSJFixedIncomeRepository


def test_get_yield_history():
    repo = WSJFixedIncomeRepository()
    mock_raw = {
        "TimeInfo": {"Ticks": [1616457600000, 1616544000000]},
        "Series": [{"DataPoints": [[4.25], [4.30]]}],
    }

    with patch("openmarkets.repositories.fixed_income.fetch_wsj_timeseries", return_value=mock_raw):
        history = repo.get_yield_history("10Y")
        assert history.maturity == "10Y"
        assert len(history.data_points) == 2
        assert history.data_points[0].yield_percent == 4.25
        assert history.data_points[1].yield_percent == 4.30


def test_get_treasury_yield_curve():
    repo = WSJFixedIncomeRepository()

    def mock_fetch(wsj_key, **kwargs):
        # Return different yields based on maturity to test inversion calculation
        val = 4.50 if "02Y" in wsj_key else 4.20
        return {
            "TimeInfo": {"Ticks": [1616457600000]},
            "Series": [{"DataPoints": [[val]]}],
        }

    with patch("openmarkets.repositories.fixed_income.fetch_wsj_timeseries", side_effect=mock_fetch):
        curve = repo.get_treasury_yield_curve()
        assert len(curve.yields) == 8
        # 10Y is 4.20, 2Y is 4.50 -> spread is (4.20 - 4.50) * 100 = -30.0 bps
        assert curve.spread_2y_10y_bps == -30.0
        assert curve.is_inverted is True
