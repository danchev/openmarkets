import pandas as pd
import pytest

from openmarkets.repositories.technical_analysis import YFinanceTechnicalAnalysisRepository


def _make_hist(close_vals, high_vals=None, low_vals=None, volume_vals=None):
    df = pd.DataFrame()
    df["Close"] = close_vals
    df["High"] = high_vals if high_vals is not None else close_vals
    df["Low"] = low_vals if low_vals is not None else close_vals
    df["Volume"] = volume_vals if volume_vals is not None else [1] * len(close_vals)
    return df


def test_calculate_sma_and_price_position_and_vs_sma():
    repo = YFinanceTechnicalAnalysisRepository()

    hist = _make_hist([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # SMA window larger than len -> None
    assert repo._calculate_sma(hist, window=20) is None

    # Valid SMA
    sma_3 = repo._calculate_sma(hist, window=3)
    assert sma_3 is not None

    # price position when range zero
    assert repo._calculate_price_position(10, 5, 5) is None

    # price vs sma when sma None or zero
    assert repo._calculate_price_vs_sma(10, None) is None
    assert repo._calculate_price_vs_sma(10, 0) is None


def test_extract_levels_and_nearest_helpers():
    repo = YFinanceTechnicalAnalysisRepository()

    highs = pd.Series([10, 12, 15, 20, 8, 7])
    lows = pd.Series([1, 2, 3, 4, 5, 6])

    res = repo._extract_resistance_levels(highs, current_price=9)
    assert isinstance(res, list)
    assert all(r > 9 for r in res)

    sup = repo._extract_support_levels(lows, current_price=9)
    assert isinstance(sup, list)
    assert all(s < 9 for s in sup)

    # nearest helpers
    assert repo._get_nearest_resistance(res) == (res[0] if res else None)
    assert repo._get_nearest_support(sup) == (sup[0] if sup else None)


def test_get_technical_indicators_with_hist(monkeypatch):
    repo = YFinanceTechnicalAnalysisRepository()

    df = _make_hist(
        [1, 2, 3, 4, 5] * 50,
        high_vals=[2, 3, 4, 5, 6] * 50,
        low_vals=[1, 1, 2, 2, 3] * 50,
        volume_vals=[100, 200, 150, 130, 110] * 50,
    )

    import openmarkets.repositories.technical_analysis as repo_mod

    class FakeTicker:
        def __init__(self, ticker, session=None):
            pass

        def history(self, period="6mo"):
            return df

    monkeypatch.setattr(repo_mod, "yf", type("M", (), {"Ticker": FakeTicker}))

    out = repo.get_technical_indicators("A")
    assert "current_price" in out
    assert "sma_20" in out


def test_get_technical_indicators_empty_raises(monkeypatch):
    repo = YFinanceTechnicalAnalysisRepository()

    import openmarkets.repositories.technical_analysis as repo_mod

    class FakeTickerEmpty:
        def __init__(self, ticker, session=None):
            pass

        def history(self, period="6mo"):
            return pd.DataFrame()

    monkeypatch.setattr(repo_mod, "yf", type("M", (), {"Ticker": FakeTickerEmpty}))

    with pytest.raises(ValueError):
        repo.get_technical_indicators("A")


def test_get_volatility_metrics(monkeypatch):
    repo = YFinanceTechnicalAnalysisRepository()

    # construct close series with variability
    close = [100, 102, 101, 103, 105, 107, 110]
    df = _make_hist(close)

    import openmarkets.repositories.technical_analysis as repo_mod

    class FakeTicker:
        def __init__(self, ticker, session=None):
            pass

        def history(self, period="1y"):
            return df

    monkeypatch.setattr(repo_mod, "yf", type("M", (), {"Ticker": FakeTicker}))

    out = repo.get_volatility_metrics("A")
    assert "daily_volatility" in out
    assert "positive_days" in out
    assert "total_trading_days" in out
