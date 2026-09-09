"""Independent formula checks against primary literature.

ES: Acerbi–Tasche (2002), Definition 2.6, https://arxiv.org/abs/cond-mat/0104295.
HAC: Newey–West (1986/1987), equation (5), https://www.nber.org/papers/t0055.
Sharpe: https://web.stanford.edu/~wfsharpe/art/sr/SR.htm.
"""

import numpy as np
import pandas as pd
import pytest

from openmarkets.core.quant import (
    compute_risk_metrics,
)

pytestmark = pytest.mark.filterwarnings("ignore:VaR and CVaR are being estimated:RuntimeWarning")


def _prices(returns):
    returns = np.asarray(returns)
    return pd.DataFrame(np.vstack([np.ones(returns.shape[1]), np.cumprod(1 + returns, axis=0)]))


def test_sharpe_and_full_sample_downside_moment():
    # Differential returns have mean .01, sample variance .0008 / 3,
    # and second lower partial moment .0001 / 4, including non-loss days.
    metrics = compute_risk_metrics(pd.Series([-0.01, 0.01, 0.01, 0.03]), risk_free_rate=0, annualization_factor=1)
    assert metrics["sharpe_ratio"] == round(0.01 / np.sqrt(0.0008 / 3), 3)
    assert metrics["sortino_ratio"] == 2.0


def test_empirical_expected_shortfall_uses_exact_tail_mass_with_ties():
    returns = pd.Series([-0.10] + [-0.02] * 9 + [0.01] * 90)
    # Worst five percent: one -10% and four -2% outcomes, not all ten losses.
    assert compute_risk_metrics(returns, risk_free_rate=0)["cvar_95_percent"] == -3.6


def test_empirical_expected_shortfall_uses_fractional_boundary_mass():
    returns = pd.Series([-0.10, -0.04] + [0.01] * 28)
    # 30 * .05 = 1.5 equally weighted observations in the tail.
    assert compute_risk_metrics(returns, risk_free_rate=0)["cvar_95_percent"] == -8.0


def test_zero_intercept_excess_return_model_has_zero_jensen_alpha():
    benchmark = pd.Series([-0.01, 0.01] * 60)
    daily_rf = 1.1 ** (1 / 252) - 1
    # asset - rf = 2 * (benchmark - rf), so the regression intercept is zero.
    asset = 2 * benchmark - daily_rf
    assert compute_risk_metrics(asset, benchmark, risk_free_rate=0.1)["alpha_percent"] == 0.0


def test_calmar_retains_small_nonzero_drawdown():
    returns = pd.Series([-0.00001] + [0.0001] * 99)
    expected = ((1 - 0.00001) * (1 + 0.0001) ** 99) ** (252 / 100) - 1
    assert compute_risk_metrics(returns, risk_free_rate=0)["calmar_ratio"] == pytest.approx(
        expected / 0.00001, abs=0.001
    )
