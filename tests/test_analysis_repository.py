import pandas as pd

from openmarkets.repositories.analysis import YFinanceAnalysisRepository


class DummyEmpty:
    empty = True


def test_get_analyst_recommendations_none_or_empty(monkeypatch):
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
    repo = YFinanceAnalysisRepository()
    assert repo.get_analyst_recommendations("AAPL") == []
    assert repo.get_recommendation_changes("AAPL") == []
    assert repo.get_revenue_estimates("AAPL") == []
    assert repo.get_earnings_estimates("AAPL") == []
    assert repo.get_growth_estimates("AAPL") == []
    assert repo.get_eps_trends("AAPL") == []
    pt = repo.get_price_targets("AAPL")
    assert pt.current is None and pt.high is None


def test_get_analyst_recommendations_with_data(monkeypatch):
    df = pd.DataFrame([{"period": "1m", "strongBuy": 1, "buy": 2, "hold": 3, "sell": 4, "strongSell": 5}])

    class T:
        def __init__(self, t, session=None):
            self.recommendations_summary = df

    monkeypatch.setattr("openmarkets.repositories.analysis.yf", type("Y", (), {"Ticker": T}))
    repo = YFinanceAnalysisRepository()
    res = repo.get_analyst_recommendations("AAPL")
    assert len(res) == 1
    assert res[0].period == "1m"


def test_get_price_targets_with_dict(monkeypatch):
    class T:
        def __init__(self, t, session=None):
            self.analyst_price_target = {"current": 1.0, "high": 2.0, "low": 0.5, "mean": 1.2, "median": 1.0}

    monkeypatch.setattr("openmarkets.repositories.analysis.yf", type("Y", (), {"Ticker": T}))
    repo = YFinanceAnalysisRepository()
    pt = repo.get_price_targets("AAPL")
    assert pt.current == 1.0
