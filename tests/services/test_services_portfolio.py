"""Unit tests for PortfolioService delegation and tool definitions."""

from unittest.mock import Mock

import pytest

from openmarkets.schemas.portfolio import (
    CorrelationMatrixResult,
    PortfolioRiskMetrics,
)
from openmarkets.services.portfolio import PortfolioService


def test_portfolio_service_tool_names():
    service = PortfolioService(repository=Mock())
    tools = service.tool_names()
    assert len(tools) == 9
    assert "calculate_portfolio_risk_metrics" in tools
    assert "calculate_asset_correlation_matrix" in tools
    assert "calculate_risk_parity_weights" in tools
    assert "calculate_minimum_variance_portfolio" in tools
    assert "calculate_rolling_beta" in tools
    assert "calculate_drawdown_series" in tools
    assert "backtest_trend_following_strategy" in tools
    assert "backtest_mean_reversion_strategy" in tools
    assert "calculate_factor_exposures" in tools


def test_calculate_portfolio_risk_metrics_delegation():
    mock_repo = Mock()
    mock_metrics = PortfolioRiskMetrics(
        tickers=["AAPL", "MSFT"],
        weights=[0.5, 0.5],
        benchmark="SPY",
        period="1y",
        annualized_return_percent=25.0,
        annualized_volatility_percent=18.0,
        sharpe_ratio=1.1,
        sortino_ratio=1.8,
        calmar_ratio=1.5,
        max_drawdown_percent=-12.0,
        var_95_percent=-1.8,
        var_99_percent=-2.8,
        cvar_95_percent=-2.4,
        cvar_99_percent=-3.4,
        beta=1.05,
        alpha_percent=3.2,
        r_squared=0.85,
    )
    mock_repo.calculate_portfolio_risk.return_value = mock_metrics

    service = PortfolioService(repository=mock_repo)
    result = service.calculate_portfolio_risk_metrics(tickers=["AAPL", "MSFT"])

    assert result == mock_metrics
    mock_repo.calculate_portfolio_risk.assert_called_once()


def test_calculate_asset_correlation_matrix_delegation():
    mock_repo = Mock()
    mock_res = CorrelationMatrixResult(
        assets=["AAPL", "NVDA"],
        period="1y",
        correlation_matrix={"AAPL": {"AAPL": 1.0, "NVDA": 0.5}, "NVDA": {"AAPL": 0.5, "NVDA": 1.0}},
        annualized_covariance_matrix={"AAPL": {"AAPL": 0.04, "NVDA": 0.02}, "NVDA": {"AAPL": 0.02, "NVDA": 0.09}},
    )
    mock_repo.calculate_correlation_matrix.return_value = mock_res

    service = PortfolioService(repository=mock_repo)
    result = service.calculate_asset_correlation_matrix(tickers=["AAPL", "NVDA"])

    assert result == mock_res
    mock_repo.calculate_correlation_matrix.assert_called_once()


def test_trend_following_strategy_enforces_fast_window_before_repository_call():
    mock_repo = Mock()
    service = PortfolioService(repository=mock_repo)

    with pytest.raises(ValueError, match="fast_window must be smaller than slow_window"):
        service.backtest_trend_following_strategy(ticker="AAPL", fast_window=20, slow_window=20)

    mock_repo.backtest_trend_following_strategy.assert_not_called()


def test_mean_reversion_strategy_enforces_threshold_order_before_repository_call():
    mock_repo = Mock()
    service = PortfolioService(repository=mock_repo)

    with pytest.raises(ValueError, match="oversold_threshold must be smaller than overbought_threshold"):
        service.backtest_mean_reversion_strategy(ticker="AAPL", oversold_threshold=80.0, overbought_threshold=70.0)

    mock_repo.backtest_mean_reversion_strategy.assert_not_called()
