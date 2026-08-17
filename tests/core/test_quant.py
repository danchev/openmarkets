"""Unit tests for core quantitative risk and backtesting mathematics."""

import numpy as np
import pandas as pd
import pytest

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


@pytest.mark.parametrize("prices", [pd.DataFrame(), pd.DataFrame(index=[0, 1])])
def test_empty_portfolios_are_rejected(prices):
    with pytest.raises(ValueError, match="price column"):
        compute_portfolio_returns(prices)


@pytest.mark.parametrize("weights", [[1.0], [-0.5, 1.5], [0.0, 0.0], [float("nan"), 1.0]])
def test_invalid_portfolio_weights_are_rejected(weights):
    with pytest.raises(ValueError, match="weights"):
        compute_portfolio_returns(_make_sample_prices(), weights)


def test_risk_metrics_use_geometric_annualization_and_consistent_beta():
    dates = pd.date_range("2024-01-01", periods=12, freq="B")
    benchmark = pd.Series([0.01, -0.005, 0.012, -0.004, 0.008, 0.003] * 2, index=dates)
    asset = benchmark * 2
    metrics = compute_risk_metrics(asset, benchmark_returns=benchmark, risk_free_rate=0.0)
    expected = ((1 + asset).prod() ** (252 / len(asset)) - 1) * 100
    assert metrics["annualized_return_percent"] == round(expected, 2)
    assert metrics["beta"] == pytest.approx(2.0, abs=0.001)


def test_r_squared_is_none_with_constant_portfolio_returns():
    benchmark = pd.Series([0.01, -0.01, 0.02, -0.02, 0.005, -0.005] * 5)
    returns = pd.Series([0.02] * len(benchmark))

    metrics = compute_risk_metrics(returns, benchmark_returns=benchmark, risk_free_rate=0.0)

    assert metrics["beta"] == pytest.approx(0.0, abs=1e-12)
    assert metrics["r_squared"] is None


def test_unestimable_benchmark_statistics_are_not_fabricated():
    returns = pd.Series([0.01, -0.01, 0.02, -0.02, 0.005, -0.005])
    flat_benchmark = pd.Series([0.0] * len(returns))
    metrics = compute_risk_metrics(returns, benchmark_returns=flat_benchmark)
    assert metrics["beta"] is None
    assert metrics["alpha_percent"] is None
    assert metrics["r_squared"] is None


def test_undefined_ratio_metrics_are_not_fabricated():
    metrics = compute_risk_metrics(pd.Series([0.0] * 10), risk_free_rate=0.0)
    assert metrics["sharpe_ratio"] is None
    assert metrics["sortino_ratio"] is None
    assert metrics["calmar_ratio"] is None


def test_non_finite_risk_free_rate_is_rejected():
    with pytest.raises(ValueError, match="risk_free_rate"):
        compute_risk_metrics(pd.Series([0.01, -0.01]), risk_free_rate=float("nan"))


def test_allocation_risk_contributions_are_true_percentages():
    for calculate in (compute_risk_parity_weights, compute_minimum_variance_weights):
        allocations = calculate(_make_sample_prices())
        total = sum(item["risk_contribution_percent"] for item in allocations)
        assert total == pytest.approx(100.0, abs=0.05)


def test_backtest_liquidates_open_position_and_uses_final_equity():
    dates = pd.date_range("2020-01-01", periods=80, freq="B")
    prices = pd.Series(np.linspace(100, 180, len(dates)), index=dates)
    result = run_moving_average_crossover(prices, fast_window=2, slow_window=5, initial_capital=1000)
    assert result["trades"]
    assert result["trades"][-1]["exit_date"] == str(dates[-1].date())
    assert result["equity_curve"][-1]["equity"] == result["ending_capital"]
    assert result["profit_factor"] is None


def test_backtest_parameter_invariants():
    prices = _make_sample_prices()["AAPL"]
    with pytest.raises(ValueError, match="slow_window"):
        run_moving_average_crossover(prices, fast_window=20, slow_window=10)
    with pytest.raises(ValueError, match="thresholds"):
        run_rsi_mean_reversion(prices, oversold=80, overbought=20)
