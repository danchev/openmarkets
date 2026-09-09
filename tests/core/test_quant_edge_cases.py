"""Definition-based tail-risk oracles and portfolio domain/timing edge cases."""

import numpy as np
import pandas as pd
import pytest

from openmarkets.core.quant import (
    compute_drawdown_curve,
    compute_minimum_variance_weights,
    compute_portfolio_returns,
    compute_risk_metrics,
    compute_risk_parity_weights,
    run_moving_average_crossover,
    run_rsi_mean_reversion,
)

pytestmark = pytest.mark.filterwarnings("ignore:VaR and CVaR are being estimated:RuntimeWarning")


def _prices(returns):
    returns = np.asarray(returns)
    return pd.DataFrame(np.vstack([np.ones(returns.shape[1]), np.cumprod(1 + returns, axis=0)]))


@pytest.mark.parametrize("count", [2, 3, 20, 30, 60, 100, 101, 129])
@pytest.mark.parametrize("tail_probability,field", [(0.05, "cvar_95_percent"), (0.01, "cvar_99_percent")])
def test_expected_shortfall_matches_rockafellar_uryasev_loss_optimization(count, tail_probability, field):
    # Independent convex objective: min_t t + E[(loss-t)+]/p. Its empirical
    # piecewise-linear minimum occurs at a sample loss, including tied samples.
    rng = np.random.default_rng(count)
    returns = rng.choice([-0.15, -0.07, -0.02, 0.00, 0.01, 0.03], count)
    losses = -returns
    loss_es = min(t + np.maximum(losses - t, 0).mean() / tail_probability for t in losses)
    actual = compute_risk_metrics(pd.Series(returns), risk_free_rate=0)
    assert actual[field] == pytest.approx(round(-loss_es * 100, 2), abs=1e-10)


@pytest.mark.parametrize("value", [-1.0, -0.01, 0.0, 0.01])
def test_constant_returns_preserve_signed_tail_risk(value):
    result = compute_risk_metrics(pd.Series([value] * 100), risk_free_rate=0)
    assert result["annualized_volatility_percent"] == 0.0
    assert result["sharpe_ratio"] is None
    for field in ["var_95_percent", "var_99_percent", "cvar_95_percent", "cvar_99_percent"]:
        assert result[field] == value * 100


def test_expected_shortfall_coherence_in_loss_convention():
    rng = np.random.default_rng(531)
    x = rng.uniform(-0.1, 0.1, 137)
    y = rng.uniform(-0.1, 0.1, 137)

    def risk(returns):
        result = compute_risk_metrics(pd.Series(returns), risk_free_rate=0)
        return -np.array([result["cvar_95_percent"], result["cvar_99_percent"]]) / 100

    # Public rounding is 0.0001 in return units; accommodate accumulated rounding.
    assert np.all(risk(x + y) <= risk(x) + risk(y) + 0.00015)
    assert risk(2 * x) == pytest.approx(2 * risk(x), abs=0.00015)
    assert risk(x + 0.01) == pytest.approx(risk(x) - 0.01, abs=0.0001)
    assert np.all(risk(x + np.abs(y)) <= risk(x) + 0.0001)


@pytest.mark.parametrize("risk_free", [-0.95, -0.05, 0, 0.045, 0.1])
@pytest.mark.parametrize("periods", [12, 252, 365])
@pytest.mark.parametrize("beta", [-0.5, 0, 1, 2])
def test_jensen_zero_excess_intercept_across_rates_frequencies_and_betas(risk_free, periods, beta):
    benchmark = pd.Series([-0.01, 0.02, 0.005, -0.005] * 30)
    periodic_rf = (1 + risk_free) ** (1 / periods) - 1
    asset = periodic_rf + beta * (benchmark - periodic_rf)
    result = compute_risk_metrics(asset, benchmark, risk_free, periods)
    assert result["alpha_percent"] == 0.0
    assert result["beta"] == beta


@pytest.mark.parametrize("rate", [-1, -1.01, float("nan"), float("inf"), -float("inf")])
def test_invalid_effective_risk_free_domain_fails_explicitly(rate):
    with pytest.raises(ValueError, match="risk_free_rate"):
        compute_risk_metrics(pd.Series([-0.01, 0.02]), risk_free_rate=rate)


@pytest.mark.parametrize("periods", [0, -1, float("nan"), float("inf")])
def test_invalid_annualization_fails_explicitly(periods):
    with pytest.raises(ValueError, match="annualization_factor"):
        compute_risk_metrics(pd.Series([-0.01, 0.02]), annualization_factor=periods)


def test_alpha_uses_only_common_observations_with_nonzero_intercept():
    dates = pd.date_range("2024-01-01", periods=122, freq="B")
    benchmark = pd.Series([-0.01, 0.01] * 60, index=dates[2:])
    periodic_rf = 1.05 ** (1 / 252) - 1
    common_asset = periodic_rf + 1.5 * (benchmark - periodic_rf) + 0.0001
    asset = pd.concat([pd.Series([0.9, 0.8], index=dates[:2]), common_asset])
    result = compute_risk_metrics(asset, benchmark, risk_free_rate=0.05)
    assert result["beta"] == 1.5
    assert result["alpha_percent"] == 2.52


def test_tail_sample_size_is_after_nonfinite_cleaning():
    returns = pd.Series([np.nan, -0.1, np.inf, -0.04, -np.inf] + [0.01] * 28)
    result = compute_risk_metrics(returns, risk_free_rate=0)
    assert result["cvar_95_percent"] == -8.0


def test_tiny_drawdown_does_not_label_the_trough_as_a_peak():
    dates = pd.date_range("2024-01-01", periods=3)
    _, _, peak, trough = compute_drawdown_curve(pd.Series([0.01, -0.000001, 0], index=dates))
    assert peak == "2024-01-01"
    assert trough == "2024-01-02"


def test_total_loss_and_no_drawdown_calmar_boundaries():
    total_loss = compute_risk_metrics(pd.Series([-1.0, 0.01, 0.02]), risk_free_rate=0)
    assert total_loss["calmar_ratio"] == -1.0
    assert total_loss["max_drawdown_percent"] == -100.0
    gains = compute_risk_metrics(pd.Series([0.001, 0.002, 0.001]), risk_free_rate=0)
    assert gains["calmar_ratio"] is None


@pytest.mark.parametrize("assets", [1, 2, 4])
def test_all_zero_covariance_uses_equal_weights_and_undefined_attribution(assets):
    result = compute_minimum_variance_weights(pd.DataFrame(np.full((5, assets), 100.0)))
    assert [row["weight_percent"] for row in result] == [100 / assets] * assets
    assert all(row["risk_contribution_percent"] is None for row in result)


def test_perfectly_hedged_minimum_variance_has_undefined_attribution():
    a = np.array([0.01, -0.01, 0.02, -0.02])
    result = compute_minimum_variance_weights(_prices(np.column_stack([a, -a])))
    assert [row["weight_percent"] for row in result] == [50.0, 50.0]
    assert all(row["risk_contribution_percent"] is None for row in result)


def test_small_absolute_variance_is_not_automatically_zero_risk():
    returns = 1e-8 * np.array([[1, 2], [1, -2], [-1, 2], [-1, -2]])
    result = compute_minimum_variance_weights(_prices(returns))
    assert [row["weight_percent"] for row in result] == pytest.approx([80.0, 20.0], abs=0.01)
    assert sum(row["risk_contribution_percent"] for row in result) == pytest.approx(100, abs=0.01)


def test_risk_parity_still_rejects_zero_volatility_assets():
    with pytest.raises(ValueError, match="positive finite asset volatility"):
        compute_risk_parity_weights(pd.DataFrame({"A": [100, 110, 105], "CASH": [100, 100, 100]}))


@pytest.mark.parametrize("bad_index", [[0, 0, 1], [2, 1, 0]])
def test_ambiguous_observation_order_is_rejected(bad_index):
    returns = pd.Series([0.01, -0.01, 0.02], index=bad_index)
    prices = pd.Series([100, 101, 102], index=bad_index)
    for calculate in (
        lambda: compute_risk_metrics(returns),
        lambda: compute_drawdown_curve(returns),
        lambda: compute_portfolio_returns(prices.to_frame()),
        lambda: run_moving_average_crossover(prices, fast_window=1, slow_window=2),
        lambda: run_rsi_mean_reversion(prices, rsi_window=2),
    ):
        with pytest.raises(ValueError, match="index must be unique and increasing"):
            calculate()


@pytest.mark.parametrize(
    "method,kwargs,warmup",
    [
        (run_moving_average_crossover, {"fast_window": 1, "slow_window": 2}, 2),
        (run_rsi_mean_reversion, {"rsi_window": 2}, 3),
    ],
)
def test_backtest_full_history_comparison_includes_warmup(method, kwargs, warmup):
    dates = pd.date_range("2024-01-01", periods=30, freq="B", tz="America/New_York")
    prices = pd.Series(np.linspace(100, 150, 30), index=dates)
    result = method(prices, **kwargs)
    assert result["buy_and_hold_return_percent"] == 50.0
    assert result["evaluation_start"] == str(dates[0].date())
    assert result["evaluation_end"] == str(dates[-1].date())
    assert result["warmup_observations"] == warmup
    assert result["equity_curve"][0]["equity"] == 10000.0
    years = (dates[-1] - dates[0]).total_seconds() / (86400 * 365.25)
    # Public ending capital is rounded; allow the propagated dollar rounding.
    assert result["cagr_percent"] == pytest.approx(
        ((result["ending_capital"] / 10000) ** (1 / years) - 1) * 100, abs=0.05
    )


def test_terminal_only_execution_has_same_full_period_benchmark():
    prices = pd.Series([100, 110, 120], index=pd.date_range("2024-01-01", periods=3))
    result = run_moving_average_crossover(prices, fast_window=1, slow_window=2, slippage_bps=100)
    assert result["ending_capital"] == 9801.0
    assert result["buy_and_hold_return_percent"] == 20.0
    assert result["trades"][0]["entry_date"] == result["evaluation_end"]
