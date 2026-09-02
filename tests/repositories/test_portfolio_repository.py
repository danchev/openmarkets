"""Unit tests for QuantPortfolioRepository layer."""

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from openmarkets.repositories.portfolio import QuantPortfolioRepository
from openmarkets.schemas.portfolio import (
    BacktestResult,
    CorrelationMatrixResult,
    DrawdownSeriesResult,
    FactorExposuresResult,
    PortfolioAllocationResult,
    PortfolioRiskMetrics,
    RollingBetaSeries,
)


def _mock_df():
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    return pd.DataFrame(
        {
            "AAPL": np.linspace(150, 180, 100),
            "MSFT": np.linspace(300, 350, 100),
            "SPY": np.linspace(450, 500, 100),
            "QQQ": np.linspace(350, 400, 100),
            "IWM": np.linspace(190, 210, 100),
            "TLT": np.linspace(95, 90, 100),
            "GLD": np.linspace(180, 200, 100),
        },
        index=dates,
    )


def test_calculate_portfolio_risk():
    repo = QuantPortfolioRepository()
    with patch.object(repo, "_fetch_price_history", return_value=_mock_df()):
        res = repo.calculate_portfolio_risk(["AAPL", "MSFT"], weights=[0.5, 0.5])
        assert isinstance(res, PortfolioRiskMetrics)
        assert res.tickers == ["AAPL", "MSFT"]
        assert res.sharpe_ratio is not None


def test_calculate_portfolio_risk_rejects_duplicate_tickers():
    repo = QuantPortfolioRepository()
    with pytest.raises(ValueError, match="unique"):
        repo.calculate_portfolio_risk(["AAPL", "aapl"])


def test_calculate_correlation_matrix():
    repo = QuantPortfolioRepository()
    with patch.object(repo, "_fetch_price_history", return_value=_mock_df()[["AAPL", "MSFT"]]):
        res = repo.calculate_correlation_matrix(["AAPL", "MSFT"])
        assert isinstance(res, CorrelationMatrixResult)
        assert res.assets == ["AAPL", "MSFT"]


def test_calculate_risk_parity_weights():
    repo = QuantPortfolioRepository()
    with patch.object(repo, "_fetch_price_history", return_value=_mock_df()[["AAPL", "MSFT"]]):
        res = repo.calculate_risk_parity_weights(["AAPL", "MSFT"])
        assert isinstance(res, PortfolioAllocationResult)
        assert len(res.allocations) == 2


def test_calculate_minimum_variance_portfolio():
    repo = QuantPortfolioRepository()
    with patch.object(repo, "_fetch_price_history", return_value=_mock_df()[["AAPL", "MSFT"]]):
        res = repo.calculate_minimum_variance_portfolio(["AAPL", "MSFT"])
        assert isinstance(res, PortfolioAllocationResult)
        assert len(res.allocations) == 2


def test_calculate_rolling_beta():
    repo = QuantPortfolioRepository()
    with patch.object(repo, "_fetch_price_history", return_value=_mock_df()[["AAPL", "SPY"]]):
        res = repo.calculate_rolling_beta("AAPL", benchmark="SPY", window=20)
        assert isinstance(res, RollingBetaSeries)
        assert res.ticker == "AAPL"


def test_calculate_drawdown_series():
    repo = QuantPortfolioRepository()
    with patch.object(repo, "_fetch_price_history", return_value=_mock_df()[["AAPL", "MSFT"]]):
        res = repo.calculate_drawdown_series(["AAPL", "MSFT"])
        assert isinstance(res, DrawdownSeriesResult)
        assert len(res.data_points) > 0


def test_backtest_trend_following_strategy():
    repo = QuantPortfolioRepository()
    with patch.object(repo, "_fetch_price_history", return_value=_mock_df()[["AAPL"]]):
        res = repo.backtest_trend_following_strategy("AAPL", fast_window=10, slow_window=20)
        assert isinstance(res, BacktestResult)
        assert res.ticker == "AAPL"


def test_backtest_mean_reversion_strategy():
    repo = QuantPortfolioRepository()
    with patch.object(repo, "_fetch_price_history", return_value=_mock_df()[["AAPL"]]):
        res = repo.backtest_mean_reversion_strategy("AAPL", rsi_window=10)
        assert isinstance(res, BacktestResult)
        assert res.ticker == "AAPL"


def test_calculate_factor_exposures():
    repo = QuantPortfolioRepository()
    with patch.object(repo, "_fetch_price_history", return_value=_mock_df()):
        res = repo.calculate_factor_exposures("AAPL")
        assert isinstance(res, FactorExposuresResult)
        assert len(res.exposures) > 0


def test_calculate_factor_exposures_excludes_target_from_factor_matrix():
    repo = QuantPortfolioRepository()
    with patch.object(repo, "_fetch_price_history", return_value=_mock_df()) as fetch:
        res = repo.calculate_factor_exposures("SPY")
        assert isinstance(res, FactorExposuresResult)
        requested = fetch.call_args.args[0]
        assert requested.count("SPY") == 1


def test_fetch_price_history_uses_adjusted_prices_for_single_ticker(monkeypatch):
    history = pd.DataFrame(
        {"Close": [150.0, 151.0, 152.0]},
        index=pd.date_range("2024-01-01", periods=3, freq="D"),
    )
    calls = []

    class FakeTicker:
        def __init__(self, _ticker, session=None):
            pass

        def history(self, *args, **kwargs):
            calls.append(kwargs)
            return history

    class FakeYFinance:
        Ticker = FakeTicker

    monkeypatch.setattr("openmarkets.repositories.portfolio.yf", FakeYFinance())
    repo = QuantPortfolioRepository()

    out = repo._fetch_price_history(["AAPL"], period="1y", session=None)

    assert not out.empty
    assert calls
    assert calls[0]["auto_adjust"] is True
    assert calls[0]["interval"] == "1d"


def test_fetch_price_history_does_not_forward_fill_gaps(monkeypatch):
    index = pd.date_range("2024-01-01", periods=5, freq="D")
    close_data = pd.DataFrame(
        {
            "AAPL": [100.0, 101.0, 102.0, 103.0, 104.0],
            "MSFT": [np.nan, 200.0, 201.0, np.nan, 204.0],
        },
        index=index,
    )
    calls = []

    class FakeYFinance:
        @staticmethod
        def download(*args, **kwargs):
            calls.append((args, kwargs))
            return pd.concat({"Close": close_data}, axis=1)

    monkeypatch.setattr("openmarkets.repositories.portfolio.yf", FakeYFinance())
    repo = QuantPortfolioRepository()

    out = repo._fetch_price_history(["AAPL", "MSFT"], period="1y", session=None)

    assert len(out) == 3
    assert pd.Timestamp("2024-01-01") not in out.index
    assert pd.Timestamp("2024-01-04") not in out.index
    assert calls
