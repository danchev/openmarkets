"""Independent formula checks against primary literature.

ES: Acerbi–Tasche (2002), Definition 2.6, https://arxiv.org/abs/cond-mat/0104295.
HAC: Newey–West (1986/1987), equation (5), https://www.nber.org/papers/t0055.
Sharpe: https://web.stanford.edu/~wfsharpe/art/sr/SR.htm.
"""

import numpy as np
import pandas as pd
import pytest

from openmarkets.core.quant import (
    compute_factor_regressions,
    compute_minimum_variance_weights,
    compute_risk_metrics,
    compute_risk_parity_weights,
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


def test_diagonal_covariance_erc_has_inverse_volatility_solution():
    # Orthogonal, zero-mean returns with volatility ratio 1:2:4.
    returns = 0.01 * np.array([[1, 2, 4], [1, -2, -4], [-1, 2, -4], [-1, -2, 4]])
    result = compute_risk_parity_weights(_prices(returns))
    assert [row["weight_percent"] for row in result] == pytest.approx([57.14, 28.57, 14.29], abs=0.01)
    assert [row["risk_contribution_percent"] for row in result] == pytest.approx([100 / 3] * 3, abs=0.01)


def test_diagonal_covariance_minimum_variance_has_inverse_variance_solution():
    returns = 0.01 * np.array([[1, 2], [1, -2], [-1, 2], [-1, -2]])
    result = compute_minimum_variance_weights(_prices(returns))
    assert [row["weight_percent"] for row in result] == pytest.approx([80, 20], abs=0.01)


def test_newey_west_against_dense_bartlett_kernel_and_qr_ols():
    # An independent dense kernel oracle, rather than the implementation's lag loop.
    rng = np.random.default_rng(20260908)
    n = 120
    factors = rng.normal(0, 0.01, (n, 2))
    innovations = rng.normal(0, 0.002, n + 1)
    y = 0.0002 + factors @ np.array([0.7, -0.3]) + innovations[1:] + 0.6 * innovations[:-1]
    x = np.column_stack([np.ones(n), factors])
    q, r = np.linalg.qr(x)
    coefficients = np.linalg.solve(r, q.T @ y)
    residual = y - x @ coefficients
    lag = int(4 * (n / 100) ** (2 / 9))
    distances = np.abs(np.arange(n)[:, None] - np.arange(n)[None, :])
    kernel = np.maximum(1 - distances / (lag + 1), 0)
    influence = np.linalg.solve(r, q.T) * residual
    covariance = influence @ kernel @ influence.T * n / (n - x.shape[1])
    expected_t = coefficients / np.sqrt(np.diag(covariance))
    result = compute_factor_regressions(pd.Series(y), pd.DataFrame(factors, columns=["F1", "F2"]))
    assert [row["t_statistic"] for row in result[:3]] == pytest.approx(np.round(expected_t, 3), abs=0.001)
    assert result[0]["exposure_beta"] == round(coefficients[0] * 252 * 100, 2)
    assert [row["exposure_beta"] for row in result[1:3]] == pytest.approx(np.round(coefficients[1:], 3))


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


def test_minimum_variance_accepts_zero_variance_optimum():
    prices = pd.DataFrame({"RISKY": [100, 110, 99], "CASH": [100, 100, 100]})
    result = compute_minimum_variance_weights(prices)
    assert [row["weight_percent"] for row in result] == [0.0, 100.0]
