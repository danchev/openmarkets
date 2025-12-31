import pandas as pd

from openmarkets.repositories.analysis import YFinanceAnalysisRepository


def test_get_analyst_recommendations_none_or_empty(patch_yf_with_attributes):
    """Test that repository handles None/empty analyst data correctly."""
    attributes = {
        "recommendations_summary": None,
        "upgrades_downgrades": None,
        "revenue_estimate": None,
        "earnings_estimate": None,
        "growth_estimates": None,
        "eps_trend": None,
        "analyst_price_target": None,
    }
    patch_yf_with_attributes("openmarkets.repositories.analysis.yf", attributes)

    repo = YFinanceAnalysisRepository()
    assert repo.get_analyst_recommendations("AAPL") == []
    assert repo.get_recommendation_changes("AAPL") == []
    assert repo.get_revenue_estimates("AAPL") == []
    assert repo.get_earnings_estimates("AAPL") == []
    assert repo.get_growth_estimates("AAPL") == []
    assert repo.get_eps_trends("AAPL") == []
    pt = repo.get_price_targets("AAPL")
    assert pt.current is None and pt.high is None


def test_get_analyst_recommendations_with_data(patch_yf_with_attributes):
    """Test that repository correctly parses analyst recommendations data."""
    df = pd.DataFrame([{"period": "1m", "strongBuy": 1, "buy": 2, "hold": 3, "sell": 4, "strongSell": 5}])
    patch_yf_with_attributes("openmarkets.repositories.analysis.yf", {"recommendations_summary": df})

    repo = YFinanceAnalysisRepository()
    res = repo.get_analyst_recommendations("AAPL")
    assert len(res) == 1
    assert res[0].period == "1m"


def test_get_price_targets_with_dict(patch_yf_with_attributes):
    """Test that repository correctly parses price target data from dict."""
    target_data = {"current": 1.0, "high": 2.0, "low": 0.5, "mean": 1.2, "median": 1.0}
    patch_yf_with_attributes("openmarkets.repositories.analysis.yf", {"analyst_price_target": target_data})

    repo = YFinanceAnalysisRepository()
    pt = repo.get_price_targets("AAPL")
    assert pt.current == 1.0
