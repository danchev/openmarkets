"""Live integration tests for PortfolioService against real market data."""

import pytest

from openmarkets.schemas.portfolio import (
    BacktestResult,
    CorrelationMatrixResult,
    DrawdownSeriesResult,
    FactorExposuresResult,
    PortfolioAllocationResult,
    PortfolioRiskMetrics,
    RollingBetaSeries,
)
from openmarkets.services.portfolio import portfolio_service


@pytest.mark.live
def test_live_calculate_portfolio_risk_metrics():
    res = portfolio_service.calculate_portfolio_risk_metrics(tickers=["AAPL", "MSFT"], period="1y")
    assert isinstance(res, PortfolioRiskMetrics)
    assert len(res.tickers) == 2
    assert res.sharpe_ratio is not None
    assert res.max_drawdown_percent <= 0.0


@pytest.mark.live
def test_live_calculate_asset_correlation_matrix():
    res = portfolio_service.calculate_asset_correlation_matrix(tickers=["AAPL", "MSFT", "GLD"], period="6mo")
    assert isinstance(res, CorrelationMatrixResult)
    assert len(res.assets) == 3
    assert res.correlation_matrix["AAPL"]["AAPL"] == 1.0


@pytest.mark.live
def test_live_calculate_risk_parity_weights():
    res = portfolio_service.calculate_risk_parity_weights(tickers=["SPY", "TLT", "GLD"], period="1y")
    assert isinstance(res, PortfolioAllocationResult)
    assert len(res.allocations) == 3


@pytest.mark.live
def test_live_calculate_minimum_variance_portfolio():
    res = portfolio_service.calculate_minimum_variance_portfolio(tickers=["AAPL", "MSFT", "JNJ"], period="1y")
    assert isinstance(res, PortfolioAllocationResult)
    assert len(res.allocations) == 3


@pytest.mark.live
def test_live_calculate_rolling_beta():
    res = portfolio_service.calculate_rolling_beta(ticker="AAPL", benchmark="SPY", window=30, period="1y")
    assert isinstance(res, RollingBetaSeries)
    assert len(res.data_points) > 0


@pytest.mark.live
def test_live_calculate_drawdown_series():
    res = portfolio_service.calculate_drawdown_series(tickers=["AAPL", "MSFT"], period="1y")
    assert isinstance(res, DrawdownSeriesResult)
    assert len(res.data_points) > 0


@pytest.mark.live
def test_live_backtest_trend_following_strategy():
    res = portfolio_service.backtest_trend_following_strategy(
        ticker="AAPL", fast_window=20, slow_window=50, period="2y"
    )
    assert isinstance(res, BacktestResult)
    assert res.total_trades >= 0
    assert len(res.equity_curve) > 0


@pytest.mark.live
def test_live_backtest_mean_reversion_strategy():
    res = portfolio_service.backtest_mean_reversion_strategy(ticker="AAPL", rsi_window=14, period="1y")
    assert isinstance(res, BacktestResult)
    assert len(res.equity_curve) > 0


@pytest.mark.live
def test_live_calculate_factor_exposures():
    res = portfolio_service.calculate_factor_exposures(ticker="AAPL", period="1y")
    assert isinstance(res, FactorExposuresResult)
    assert len(res.exposures) > 0
