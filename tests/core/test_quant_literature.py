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


def test_empirical_expected_shortfall_uses_exact_tail_mass_with_ties():
    returns = pd.Series([-0.10] + [-0.02] * 9 + [0.01] * 90)
    # Worst five percent: one -10% and four -2% outcomes, not all ten losses.
    assert compute_risk_metrics(returns, risk_free_rate=0)["cvar_95_percent"] == -3.6


def test_empirical_expected_shortfall_uses_fractional_boundary_mass():
    returns = pd.Series([-0.10, -0.04] + [0.01] * 28)
    # 30 * .05 = 1.5 equally weighted observations in the tail.
    assert compute_risk_metrics(returns, risk_free_rate=0)["cvar_95_percent"] == -8.0
