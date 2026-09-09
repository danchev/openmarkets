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
