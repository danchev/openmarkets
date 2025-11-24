from unittest import mock

from openmarkets.repositories.analysis import YFinanceAnalysisRepository
from openmarkets.schemas.analysis import (
    AnalystPriceTargets,
    AnalystRecommendation,
    AnalystRecommendationChange,
    EarningsEstimate,
    EPSTrend,
    GrowthEstimates,
    RevenueEstimate,
)


class DummyDF:
    def __init__(self, records=None, empty=False):
        self._records = records or []
        self.empty = empty

    def to_dict(self, how):
        return self._records


def make_yf_ticker(monkeypatch, attr, records=None, empty=False):
    dummy = DummyDF(records, empty)
    t = mock.Mock()
    setattr(t, attr, dummy)
    monkeypatch.setattr("yfinance.Ticker", lambda ticker: t)
    return t


def test_get_analyst_recommendations(monkeypatch):
    repo = YFinanceAnalysisRepository()
    make_yf_ticker(monkeypatch, "recommendations_summary", [{"foo": "bar"}], empty=False)
    monkeypatch.setattr(AnalystRecommendation, "__init__", lambda self, **kw: None)
    assert isinstance(repo.get_analyst_recommendations("AAPL"), list)
    make_yf_ticker(monkeypatch, "recommendations_summary", empty=True)
    assert repo.get_analyst_recommendations("AAPL") == []
    make_yf_ticker(monkeypatch, "recommendations_summary", None)
    assert repo.get_analyst_recommendations("AAPL") == []


def test_get_recommendation_changes(monkeypatch):
    repo = YFinanceAnalysisRepository()
    make_yf_ticker(monkeypatch, "upgrades_downgrades", [{"foo": "bar"}], empty=False)
    monkeypatch.setattr(AnalystRecommendationChange, "__init__", lambda self, **kw: None)
    assert isinstance(repo.get_recommendation_changes("AAPL"), list)
    make_yf_ticker(monkeypatch, "upgrades_downgrades", empty=True)
    assert repo.get_recommendation_changes("AAPL") == []
    make_yf_ticker(monkeypatch, "upgrades_downgrades", None)
    assert repo.get_recommendation_changes("AAPL") == []


def test_get_revenue_estimates(monkeypatch):
    repo = YFinanceAnalysisRepository()
    make_yf_ticker(monkeypatch, "revenue_estimate", [{"foo": "bar"}], empty=False)
    monkeypatch.setattr(RevenueEstimate, "__init__", lambda self, **kw: None)
    assert isinstance(repo.get_revenue_estimates("AAPL"), list)
    make_yf_ticker(monkeypatch, "revenue_estimate", empty=True)
    assert repo.get_revenue_estimates("AAPL") == []
    make_yf_ticker(monkeypatch, "revenue_estimate", None)
    assert repo.get_revenue_estimates("AAPL") == []


def test_get_earnings_estimates(monkeypatch):
    repo = YFinanceAnalysisRepository()
    make_yf_ticker(monkeypatch, "earnings_estimate", [{"foo": "bar"}], empty=False)
    monkeypatch.setattr(EarningsEstimate, "__init__", lambda self, **kw: None)
    assert isinstance(repo.get_earnings_estimates("AAPL"), list)
    make_yf_ticker(monkeypatch, "earnings_estimate", empty=True)
    assert repo.get_earnings_estimates("AAPL") == []
    make_yf_ticker(monkeypatch, "earnings_estimate", None)
    assert repo.get_earnings_estimates("AAPL") == []


def test_get_growth_estimates(monkeypatch):
    repo = YFinanceAnalysisRepository()
    make_yf_ticker(monkeypatch, "growth_estimates", [{"foo": "bar"}], empty=False)
    monkeypatch.setattr(GrowthEstimates, "__init__", lambda self, **kw: None)
    assert isinstance(repo.get_growth_estimates("AAPL"), list)
    make_yf_ticker(monkeypatch, "growth_estimates", empty=True)
    assert repo.get_growth_estimates("AAPL") == []
    make_yf_ticker(monkeypatch, "growth_estimates", None)
    assert repo.get_growth_estimates("AAPL") == []


def test_get_eps_trends(monkeypatch):
    repo = YFinanceAnalysisRepository()
    make_yf_ticker(monkeypatch, "eps_trend", [{"foo": "bar"}], empty=False)
    monkeypatch.setattr(EPSTrend, "__init__", lambda self, **kw: None)
    assert isinstance(repo.get_eps_trends("AAPL"), list)
    make_yf_ticker(monkeypatch, "eps_trend", empty=True)
    assert repo.get_eps_trends("AAPL") == []
    make_yf_ticker(monkeypatch, "eps_trend", None)
    assert repo.get_eps_trends("AAPL") == []


def test_get_price_targets(monkeypatch):
    repo = YFinanceAnalysisRepository()
    make_yf_ticker(monkeypatch, "analyst_price_target", {"current": 1, "high": 2, "low": 3, "mean": 4, "median": 5})
    monkeypatch.setattr(AnalystPriceTargets, "__init__", lambda self, **kw: None)
    assert isinstance(repo.get_price_targets("AAPL"), AnalystPriceTargets)
    make_yf_ticker(monkeypatch, "analyst_price_target", None)
    result = repo.get_price_targets("AAPL")
    assert isinstance(result, AnalystPriceTargets)
    make_yf_ticker(monkeypatch, "analyst_price_target", [])
    result = repo.get_price_targets("AAPL")
    assert isinstance(result, AnalystPriceTargets)
