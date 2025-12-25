"""Unit tests for YFinanceAnalysisRepository."""

import pandas as pd

from openmarkets.repositories.analysis import YFinanceAnalysisRepository


class DummyEmpty:
    """Dummy empty data class for testing."""

    empty = True


class TestYFinanceAnalysisRepository:
    """Test suite for YFinanceAnalysisRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = YFinanceAnalysisRepository()

    def test_get_analyst_recommendations_none_or_empty(self, monkeypatch):
        """Test when recommendation data is None or empty."""

        class T:
            def __init__(self, t, session=None):
                self.recommendations_summary = None
                self.upgrades_downgrades = None
                self.revenue_estimate = None
                self.earnings_estimate = None
                self.growth_estimates = None
                self.eps_trend = None
                self.analyst_price_target = None

        monkeypatch.setattr("openmarkets.repositories.analysis.yf", type("Y", (), {"Ticker": T}))
        assert self.repo.get_analyst_recommendations("AAPL") == []
        assert self.repo.get_recommendation_changes("AAPL") == []
        assert self.repo.get_revenue_estimates("AAPL") == []
        assert self.repo.get_earnings_estimates("AAPL") == []
        assert self.repo.get_growth_estimates("AAPL") == []
        assert self.repo.get_eps_trends("AAPL") == []
        pt = self.repo.get_price_targets("AAPL")
        assert pt.current is None and pt.high is None

    def test_get_analyst_recommendations_with_data(self, monkeypatch):
        """Test retrieving analyst recommendations with valid data."""
        df = pd.DataFrame([{"period": "1m", "strongBuy": 1, "buy": 2, "hold": 3, "sell": 4, "strongSell": 5}])

        class T:
            def __init__(self, t, session=None):
                self.recommendations_summary = df

        monkeypatch.setattr("openmarkets.repositories.analysis.yf", type("Y", (), {"Ticker": T}))
        res = self.repo.get_analyst_recommendations("AAPL")
        assert len(res) == 1
        assert res[0].period == "1m"

    def test_get_price_targets_with_dict(self, monkeypatch):
        """Test price targets when data is a dictionary."""

        class T:
            def __init__(self, t, session=None):
                self.analyst_price_target = {"current": 1.0, "high": 2.0, "low": 0.5, "mean": 1.2, "median": 1.0}

        monkeypatch.setattr("openmarkets.repositories.analysis.yf", type("Y", (), {"Ticker": T}))
        pt = self.repo.get_price_targets("AAPL")
        assert pt.current == 1.0

    def test_get_recommendations_data_empty_flag(self, monkeypatch):
        """Test when data exists but empty flag is True."""

        class EmptyData:
            empty = True

            def to_dict(self, orient):
                return []

        class T:
            def __init__(self, t, session=None):
                self.recommendations_summary = EmptyData()
                self.upgrades_downgrades = EmptyData()
                self.revenue_estimate = EmptyData()
                self.earnings_estimate = EmptyData()
                self.growth_estimates = EmptyData()
                self.eps_trend = EmptyData()
                self.analyst_price_target = "not a dict"

        monkeypatch.setattr("openmarkets.repositories.analysis.yf", type("Y", (), {"Ticker": T}))
        assert self.repo.get_analyst_recommendations("AAPL") == []
        assert self.repo.get_recommendation_changes("AAPL") == []
        assert self.repo.get_revenue_estimates("AAPL") == []
        assert self.repo.get_earnings_estimates("AAPL") == []
        assert self.repo.get_growth_estimates("AAPL") == []
        assert self.repo.get_eps_trends("AAPL") == []
        pt = self.repo.get_price_targets("AAPL")
        assert pt.current is None

    def test_get_recommendations_with_non_empty_data(self, monkeypatch):
        """Test successful data retrieval for all recommendation methods."""
        df_changes = pd.DataFrame([{"Firm": "Test", "ToGrade": "Buy", "FromGrade": "Hold", "Action": "up"}])
        df_revenue = pd.DataFrame([{"period": "Q1", "avg": 100, "low": 90, "high": 110, "numberOfAnalysts": 5}])
        df_earnings = pd.DataFrame([{"period": "Q1", "avg": 10, "low": 9, "high": 11, "numberOfAnalysts": 5}])
        df_growth = pd.DataFrame([{"period": "Next 5Y", "growth": 0.05, "numberOfAnalysts": 5}])
        df_eps = pd.DataFrame([{"period": "Q1", "current": 1.0, "7daysAgo": 0.9, "30daysAgo": 0.8, "60daysAgo": 0.7}])

        class T:
            def __init__(self, t, session=None):
                self.recommendations_summary = df_changes
                self.upgrades_downgrades = df_changes
                self.revenue_estimate = df_revenue
                self.earnings_estimate = df_earnings
                self.growth_estimates = df_growth
                self.eps_trend = df_eps

        monkeypatch.setattr("openmarkets.repositories.analysis.yf", type("Y", (), {"Ticker": T}))
        assert len(self.repo.get_recommendation_changes("AAPL")) == 1
        assert len(self.repo.get_revenue_estimates("AAPL")) == 1
        assert len(self.repo.get_earnings_estimates("AAPL")) == 1
        assert len(self.repo.get_growth_estimates("AAPL")) == 1
        assert len(self.repo.get_eps_trends("AAPL")) == 1
