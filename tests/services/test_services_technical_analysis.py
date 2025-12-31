import pandas as pd
import pytest

from openmarkets.repositories.technical_analysis import YFinanceTechnicalAnalysisRepository


@pytest.fixture
def technical_analysis_repository() -> YFinanceTechnicalAnalysisRepository:
    return YFinanceTechnicalAnalysisRepository()


def test_calculate_sma_and_price_position_and_vs_sma(technical_analysis_repository, hist_factory):
    hist = hist_factory([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # SMA window larger than len -> None
    assert technical_analysis_repository._calculate_sma(hist, window=20) is None

    # Valid SMA
    sma_3 = technical_analysis_repository._calculate_sma(hist, window=3)
    assert sma_3 is not None

    # price position when range zero
    assert technical_analysis_repository._calculate_price_position(10, 5, 5) is None

    # price vs sma when sma None or zero
    assert technical_analysis_repository._calculate_price_vs_sma(10, None) is None
    assert technical_analysis_repository._calculate_price_vs_sma(10, 0) is None


def test_extract_levels_and_nearest_helpers(technical_analysis_repository):
    highs = pd.Series([10, 12, 15, 20, 8, 7])
    lows = pd.Series([1, 2, 3, 4, 5, 6])

    res = technical_analysis_repository._extract_resistance_levels(highs, current_price=9)
    assert isinstance(res, list)
    assert all(r > 9 for r in res)

    sup = technical_analysis_repository._extract_support_levels(lows, current_price=9)
    assert isinstance(sup, list)
    assert all(s < 9 for s in sup)

    # nearest helpers
    assert technical_analysis_repository._get_nearest_resistance(res) == (res[0] if res else None)
    assert technical_analysis_repository._get_nearest_support(sup) == (sup[0] if sup else None)


def test_get_technical_indicators_with_hist(monkeypatch, technical_analysis_repository, hist_factory):
    df = hist_factory(
        [1, 2, 3, 4, 5] * 50,
        high_values=[2, 3, 4, 5, 6] * 50,
        low_values=[1, 1, 2, 2, 3] * 50,
        volume_values=[100, 200, 150, 130, 110] * 50,
    )

    import openmarkets.repositories.technical_analysis as repo_mod

    class FakeTicker:
        def __init__(self, ticker, session=None):
            pass

        def history(self, period="6mo"):
            return df

    monkeypatch.setattr(repo_mod, "yf", type("M", (), {"Ticker": FakeTicker}))

    out = technical_analysis_repository.get_technical_indicators("A")
    assert "current_price" in out
    assert "sma_20" in out


def test_get_technical_indicators_empty_raises(monkeypatch, technical_analysis_repository):
    import openmarkets.repositories.technical_analysis as repo_mod

    class FakeTickerEmpty:
        def __init__(self, ticker, session=None):
            pass

        def history(self, period="6mo"):
            return pd.DataFrame()

    monkeypatch.setattr(repo_mod, "yf", type("M", (), {"Ticker": FakeTickerEmpty}))

    with pytest.raises(ValueError):
        technical_analysis_repository.get_technical_indicators("A")


def test_get_volatility_metrics(monkeypatch, technical_analysis_repository, hist_factory):
    # construct close series with variability
    close = [100, 102, 101, 103, 105, 107, 110]
    df = hist_factory(close)

    import openmarkets.repositories.technical_analysis as repo_mod

    class FakeTicker:
        def __init__(self, ticker, session=None):
            pass

        def history(self, period="1y"):
            return df

    monkeypatch.setattr(repo_mod, "yf", type("M", (), {"Ticker": FakeTicker}))

    out = technical_analysis_repository.get_volatility_metrics("A")
    assert "daily_volatility" in out
    assert "positive_days" in out
    assert "total_trading_days" in out
