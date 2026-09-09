"""Definition-based tail-risk oracles and portfolio domain/timing edge cases."""

import numpy as np
import pandas as pd
import pytest

from openmarkets.core.quant import (
    compute_drawdown_curve,
    compute_portfolio_returns,
    compute_risk_metrics,
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


def test_tail_sample_size_is_after_nonfinite_cleaning():
    returns = pd.Series([np.nan, -0.1, np.inf, -0.04, -np.inf] + [0.01] * 28)
    result = compute_risk_metrics(returns, risk_free_rate=0)
    assert result["cvar_95_percent"] == -8.0


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
