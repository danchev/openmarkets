"""Unit tests for core quantitative risk and backtesting mathematics."""

import numpy as np
import pandas as pd

from openmarkets.core.quant import (
    compute_correlation_and_covariance,
    compute_drawdown_curve,
    compute_factor_regressions,
    compute_minimum_variance_weights,
    compute_portfolio_returns,
    compute_risk_metrics,
    compute_risk_parity_weights,
    compute_rolling_beta,
    run_moving_average_crossover,
    run_rsi_mean_reversion,
)


def _make_sample_prices() -> pd.DataFrame:
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=260, freq="B")
    ret_a = np.random.normal(0.001, 0.015, 260)
    ret_b = np.random.normal(0.0008, 0.012, 260)

    price_a = 100.0 * np.exp(np.cumsum(ret_a))
    price_b = 50.0 * np.exp(np.cumsum(ret_b))
    return pd.DataFrame({"AAPL": price_a, "MSFT": price_b}, index=dates)


def test_compute_portfolio_returns():
    df = _make_sample_prices()
    returns, weights = compute_portfolio_returns(df, weights=[0.6, 0.4])
    assert len(returns) == 259
    assert weights == [0.6, 0.4]
    assert isinstance(returns, pd.Series)


def test_compute_drawdown_curve():
    df = _make_sample_prices()
    ret = df["AAPL"].pct_change().dropna()
    points, max_dd, peak, trough = compute_drawdown_curve(ret)
    assert len(points) == len(ret)
    assert max_dd <= 0.0
    assert peak is not None
    assert trough is not None


def test_compute_risk_metrics():
    df = _make_sample_prices()
    ret_a = df["AAPL"].pct_change().dropna()
    ret_b = df["MSFT"].pct_change().dropna()

    metrics = compute_risk_metrics(ret_a, benchmark_returns=ret_b, risk_free_rate=0.045)
    assert "sharpe_ratio" in metrics
    assert "sortino_ratio" in metrics
    assert "calmar_ratio" in metrics
    assert "var_95_percent" in metrics
    assert "cvar_95_percent" in metrics
    assert "beta" in metrics
    assert metrics["annualized_volatility_percent"] > 0


def test_compute_correlation_and_covariance():
    df = _make_sample_prices()
    assets, corr, cov = compute_correlation_and_covariance(df)
    assert assets == ["AAPL", "MSFT"]
    assert corr["AAPL"]["AAPL"] == 1.0
    assert corr["AAPL"]["MSFT"] == corr["MSFT"]["AAPL"]
    assert cov["AAPL"]["AAPL"] > 0


def test_compute_risk_parity_weights():
    df = _make_sample_prices()
    weights = compute_risk_parity_weights(df)
    assert len(weights) == 2
    total_w = sum(w["weight_percent"] for w in weights)
    assert abs(total_w - 100.0) < 0.1


def test_compute_minimum_variance_weights():
    df = _make_sample_prices()
    weights = compute_minimum_variance_weights(df)
    assert len(weights) == 2
    total_w = sum(w["weight_percent"] for w in weights)
    assert abs(total_w - 100.0) < 0.1


def test_compute_rolling_beta():
    df = _make_sample_prices()
    ret_a = df["AAPL"].pct_change().dropna()
    ret_b = df["MSFT"].pct_change().dropna()
    points = compute_rolling_beta(ret_a, ret_b, window=30)
    assert len(points) > 0
    assert "date" in points[0]
    assert "beta" in points[0]


def test_run_moving_average_crossover():
    df = _make_sample_prices()
    res = run_moving_average_crossover(df["AAPL"], fast_window=10, slow_window=30, initial_capital=10000.0)
    assert "total_return_percent" in res
    assert "cagr_percent" in res
    assert "win_rate_percent" in res
    assert "equity_curve" in res


def test_run_rsi_mean_reversion():
    df = _make_sample_prices()
    res = run_rsi_mean_reversion(df["AAPL"], rsi_window=14, oversold=35.0, overbought=65.0, initial_capital=10000.0)
    assert "total_return_percent" in res
    assert "win_rate_percent" in res
    assert "equity_curve" in res


def test_compute_factor_regressions():
    df = _make_sample_prices()
    ret_a = df["AAPL"].pct_change().dropna()
    factors = pd.DataFrame({"MSFT": df["MSFT"].pct_change().dropna()})
    res = compute_factor_regressions(ret_a, factors)
    assert len(res) >= 2
    assert any(e["factor"] == "MSFT" for e in res)
