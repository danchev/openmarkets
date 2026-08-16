"""Core vectorized quantitative portfolio risk mathematics and strategy backtesting engines."""

from typing import Any

import numpy as np
import pandas as pd


def _clean_prices(price_df: pd.DataFrame, *, minimum_observations: int = 3) -> pd.DataFrame:
    """Validate a price matrix and retain only complete, finite observations."""
    if not isinstance(price_df, pd.DataFrame) or price_df.columns.empty:
        raise ValueError("At least one asset price column is required")
    clean_df = price_df.replace([np.inf, -np.inf], np.nan).dropna(how="all").ffill().dropna()
    if len(clean_df) < minimum_observations:
        raise ValueError(f"At least {minimum_observations} complete price observations are required")
    if (clean_df <= 0).any().any():
        raise ValueError("Asset prices must be positive")
    return clean_df


def _validate_returns(returns: pd.Series, *, minimum_observations: int = 2) -> pd.Series:
    clean = returns.replace([np.inf, -np.inf], np.nan).dropna().astype(float)
    if len(clean) < minimum_observations:
        raise ValueError(f"At least {minimum_observations} finite return observations are required")
    if (clean <= -1).any():
        raise ValueError("Returns must be greater than -100%")
    return clean


def _portfolio_risk_contributions(covariance: np.ndarray, weights: np.ndarray) -> np.ndarray:
    portfolio_variance = float(weights @ covariance @ weights)
    if not np.isfinite(portfolio_variance) or portfolio_variance <= 0:
        raise ValueError("Portfolio variance must be finite and positive")
    return weights * (covariance @ weights) / portfolio_variance * 100


def _project_to_simplex(values: np.ndarray) -> np.ndarray:
    """Euclidean projection onto non-negative weights summing to one."""
    sorted_values = np.sort(values)[::-1]
    cumulative = np.cumsum(sorted_values) - 1
    indices = np.arange(1, len(values) + 1)
    eligible = sorted_values - cumulative / indices > 0
    rho = int(indices[eligible][-1])
    threshold = cumulative[rho - 1] / rho
    return np.maximum(values - threshold, 0)


def _elapsed_years(index: pd.Index) -> float:
    """Calculate elapsed years from dates, falling back to trading observations."""
    if isinstance(index, pd.DatetimeIndex) and len(index) > 1:
        elapsed_days = (index[-1] - index[0]).total_seconds() / 86_400
        if elapsed_days > 0:
            return elapsed_days / 365.25
    return max((len(index) - 1) / 252.0, 1 / 252.0)


def _closed_trade_records(prices: pd.Series, signal: pd.Series, equity: pd.Series) -> list[dict[str, Any]]:
    """Create round-trip records, liquidating an open position at the final close."""
    trades: list[dict[str, Any]] = []
    entry_date: str | None = None
    entry_price = 0.0
    entry_equity = 0.0
    position_changes = signal.diff().fillna(signal)

    for offset, (_, change) in enumerate(position_changes.items()):
        if offset == 0:
            continue
        execution_offset = offset - 1
        execution_date = str(prices.index[execution_offset]).split(" ")[0]
        execution_price = float(prices.iloc[execution_offset])
        execution_equity = float(equity.iloc[execution_offset])
        if change == 1 and entry_date is None:
            entry_date = execution_date
            entry_price = execution_price
            entry_equity = execution_equity
        elif change == -1 and entry_date is not None:
            trades.append(
                {
                    "entry_date": entry_date,
                    "exit_date": execution_date,
                    "entry_price": round(entry_price, 2),
                    "exit_price": round(execution_price, 2),
                    "return_percent": round((execution_price / entry_price - 1) * 100, 2),
                    "profit_loss": round(execution_equity - entry_equity, 2),
                }
            )
            entry_date = None

    if entry_date is not None:
        exit_price = float(prices.iloc[-1])
        trades.append(
            {
                "entry_date": entry_date,
                "exit_date": str(prices.index[-1]).split(" ")[0],
                "entry_price": round(entry_price, 2),
                "exit_price": round(exit_price, 2),
                "return_percent": round((exit_price / entry_price - 1) * 100, 2),
                "profit_loss": round(float(equity.iloc[-1]) - entry_equity, 2),
            }
        )
    return trades


def _sample_equity_curve(equity: pd.Series) -> list[dict[str, Any]]:
    sampled = equity.iloc[:: max(1, len(equity) // 30)]
    if sampled.index[-1] != equity.index[-1]:
        sampled = pd.concat([sampled, equity.iloc[[-1]]])
    return [
        {"date": str(timestamp).split(" ")[0], "equity": round(float(value), 2)} for timestamp, value in sampled.items()
    ]


def compute_portfolio_returns(
    price_df: pd.DataFrame, weights: list[float] | None = None
) -> tuple[pd.Series, list[float]]:
    """Compute weighted portfolio daily return series from historical price DataFrame.

    Args:
        price_df: DataFrame of asset close prices indexed by timestamp/date.
        weights: Optional list of portfolio weights summing to 1.0. Defaults to equal-weight.

    Returns:
        Tuple of (portfolio_returns_series, normalized_weights_list).
    """
    clean_df = _clean_prices(price_df)
    daily_returns = clean_df.pct_change().dropna()

    num_assets = len(clean_df.columns)
    if weights is None:
        norm_weights = [1.0 / num_assets] * num_assets
    else:
        if len(weights) != num_assets:
            raise ValueError(f"weights must contain exactly {num_assets} values")
        if not all(np.isfinite(weight) and weight >= 0 for weight in weights):
            raise ValueError("weights must contain only finite, non-negative values")
        total_w = sum(weights)
        if total_w <= 0:
            raise ValueError("weights must sum to a positive value")
        norm_weights = [w / total_w for w in weights]

    w_arr = np.array(norm_weights)
    port_returns = daily_returns.dot(w_arr)
    return port_returns, norm_weights


def compute_drawdown_curve(returns: pd.Series) -> tuple[list[dict[str, Any]], float, str | None, str | None]:
    """Compute underwater drawdown timeseries, max drawdown, and peak/trough dates."""
    if returns.empty:
        return [], 0.0, None, None

    cum_ret = (1 + returns).cumprod()
    high_water = cum_ret.cummax()
    dd_series = (cum_ret - high_water) / high_water

    max_dd = float(dd_series.min())

    # Find trough date and peak date for max drawdown
    trough_date = str(dd_series.idxmin()).split(" ")[0] if not dd_series.empty else None
    peak_date = None
    if trough_date is not None:
        sub_cum = cum_ret.loc[:trough_date]
        if not sub_cum.empty:
            peak_date = str(sub_cum.idxmax()).split(" ")[0]

    points: list[dict[str, Any]] = []
    for dt, val in dd_series.items():
        dt_str = str(dt).split(" ")[0]
        points.append(
            {
                "date": dt_str,
                "drawdown_percent": round(float(val) * 100, 2),
                "high_water_mark": round(float(high_water.loc[dt]), 4),
            }
        )

    return points, round(max_dd * 100, 2), peak_date, trough_date


def compute_risk_metrics(
    returns: pd.Series,
    benchmark_returns: pd.Series | None = None,
    risk_free_rate: float = 0.045,
) -> dict[str, Any]:
    """Compute comprehensive quantitative portfolio risk and performance metrics.

    Args:
        returns: Portfolio daily returns Series.
        benchmark_returns: Benchmark daily returns Series (e.g. SPY).
        risk_free_rate: Annualized risk-free rate (defaults to 4.5%).

    Returns:
        Dictionary of Sharpe, Sortino, Calmar, Volatility, VaR, CVaR, Beta, and Alpha.
    """
    if not np.isfinite(risk_free_rate):
        raise ValueError("risk_free_rate must be finite")
    returns = _validate_returns(returns)

    cumulative_growth = float((1 + returns).prod())
    ann_ret = cumulative_growth ** (252 / len(returns)) - 1
    ann_vol = float(returns.std() * np.sqrt(252))

    # Sharpe Ratio
    sharpe = (ann_ret - risk_free_rate) / ann_vol if ann_vol > 0 else None

    # Sortino Ratio (downside risk deviation)
    downside_std = float(np.sqrt((np.minimum(returns, 0) ** 2).mean()) * np.sqrt(252))
    sortino = (ann_ret - risk_free_rate) / downside_std if downside_std > 0 else None

    # Max Drawdown & Calmar Ratio
    _, max_dd_pct, _, _ = compute_drawdown_curve(returns)
    abs_dd = abs(max_dd_pct) / 100.0
    calmar = (ann_ret / abs_dd) if abs_dd > 0 else None

    # Value-at-Risk (Historical VaR)
    var_95 = float(np.percentile(returns, 5))
    var_99 = float(np.percentile(returns, 1))

    # Conditional VaR (Expected Shortfall)
    tail_95 = returns[returns <= var_95]
    cvar_95 = float(tail_95.mean()) if not tail_95.empty else var_95

    tail_99 = returns[returns <= var_99]
    cvar_99 = float(tail_99.mean()) if not tail_99.empty else var_99

    # Beta and Alpha vs Benchmark
    beta = None
    alpha = None
    r_squared = None

    if benchmark_returns is not None and not benchmark_returns.empty:
        clean_benchmark = benchmark_returns.replace([np.inf, -np.inf], np.nan)
        aligned = pd.concat([returns, clean_benchmark], axis=1).dropna()
        if len(aligned) > 5:
            p_ret = aligned.iloc[:, 0]
            b_ret = aligned.iloc[:, 1]
            if (b_ret <= -1).any():
                raise ValueError("Benchmark returns must be greater than -100%")
            cov = p_ret.cov(b_ret)
            b_var = b_ret.var()
            if b_var > 0:
                beta = float(cov / b_var)
                b_ann_ret = float((1 + b_ret).prod() ** (252 / len(b_ret)) - 1)
                alpha = float(ann_ret - (risk_free_rate + beta * (b_ann_ret - risk_free_rate)))
                corr = np.corrcoef(p_ret, b_ret)[0, 1]
                r_squared = float(corr**2)

    return {
        "annualized_return_percent": round(ann_ret * 100, 2),
        "annualized_volatility_percent": round(ann_vol * 100, 2),
        "sharpe_ratio": round(sharpe, 3) if sharpe is not None else None,
        "sortino_ratio": round(sortino, 3) if sortino is not None else None,
        "calmar_ratio": round(calmar, 3) if calmar is not None else None,
        "max_drawdown_percent": max_dd_pct,
        "var_95_percent": round(var_95 * 100, 2),
        "var_99_percent": round(var_99 * 100, 2),
        "cvar_95_percent": round(cvar_95 * 100, 2),
        "cvar_99_percent": round(cvar_99 * 100, 2),
        "beta": round(beta, 3) if beta is not None else None,
        "alpha_percent": round(alpha * 100, 2) if alpha is not None else None,
        "r_squared": round(r_squared, 3) if r_squared is not None else None,
    }


def compute_correlation_and_covariance(
    price_df: pd.DataFrame,
) -> tuple[list[str], dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    """Compute pairwise correlation matrix and annualized covariance matrix across asset returns."""
    clean_df = _clean_prices(price_df)
    returns = clean_df.pct_change().dropna()
    assets = list(clean_df.columns)

    corr_df = returns.corr()
    cov_df = returns.cov() * 252
    if not np.isfinite(corr_df.to_numpy()).all() or not np.isfinite(cov_df.to_numpy()).all():
        raise ValueError("Correlation requires at least two assets with non-zero return variance")

    corr_dict: dict[str, dict[str, float]] = {}
    cov_dict: dict[str, dict[str, float]] = {}

    for a1 in assets:
        corr_dict[a1] = {}
        cov_dict[a1] = {}
        for a2 in assets:
            corr_dict[a1][a2] = round(float(corr_df.loc[a1, a2]), 4)
            cov_dict[a1][a2] = round(float(cov_df.loc[a1, a2]), 4)

    return assets, corr_dict, cov_dict


def compute_risk_parity_weights(price_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Compute inverse-volatility allocation weights and actual risk contributions.

    Assets with lower historical volatility receive higher allocations so each asset
    contributes approximately equal risk to the overall portfolio.
    """
    clean_df = _clean_prices(price_df)
    returns = clean_df.pct_change().dropna()
    vols = returns.std() * np.sqrt(252)

    if not np.isfinite(vols.to_numpy()).all() or (vols <= 0).any():
        raise ValueError("Inverse-volatility allocation requires positive finite asset volatility")
    inv_vols = 1.0 / vols
    total_inv_vol = inv_vols.sum()
    weights = inv_vols / total_inv_vol

    covariance = returns.cov().to_numpy() * 252
    contributions = _portfolio_risk_contributions(covariance, weights.to_numpy())
    res: list[dict[str, Any]] = []
    for index, ticker in enumerate(clean_df.columns):
        w = float(weights[ticker])
        v = float(vols[ticker])
        res.append(
            {
                "ticker": ticker,
                "weight_percent": round(w * 100, 2),
                "annualized_volatility_percent": round(v * 100, 2),
                "risk_contribution_percent": round(float(contributions[index]), 2),
            }
        )
    return res


def compute_minimum_variance_weights(price_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Compute numerical Minimum Variance portfolio weights with simplex projection.

    Constrained to long-only non-negative weights.
    """
    clean_df = _clean_prices(price_df)
    returns = clean_df.pct_change().dropna()
    cov = returns.cov().values * 252

    if not np.isfinite(cov).all():
        raise ValueError("Covariance matrix contains non-finite values")

    # Projected-gradient solution of the long-only constrained problem.
    num_assets = cov.shape[0]
    ridge = np.eye(num_assets) * 1e-4
    regularized_cov = cov + ridge
    largest_eigenvalue = float(np.linalg.eigvalsh(regularized_cov).max())
    if not np.isfinite(largest_eigenvalue) or largest_eigenvalue <= 0:
        raise ValueError("Covariance matrix is not positive definite")
    step_size = 1.0 / (2.0 * largest_eigenvalue)
    norm_weights = np.ones(num_assets) / num_assets
    for _ in range(10_000):
        candidate = _project_to_simplex(norm_weights - step_size * (2.0 * regularized_cov @ norm_weights))
        if np.linalg.norm(candidate - norm_weights, ord=1) < 1e-10:
            norm_weights = candidate
            break
        norm_weights = candidate
    else:
        raise ValueError("Minimum variance optimization did not converge")

    vols = returns.std() * np.sqrt(252)
    contributions = _portfolio_risk_contributions(cov, norm_weights)
    res: list[dict[str, Any]] = []
    for i, ticker in enumerate(clean_df.columns):
        w = float(norm_weights[i])
        v = float(vols[ticker])
        res.append(
            {
                "ticker": ticker,
                "weight_percent": round(w * 100, 2),
                "annualized_volatility_percent": round(v * 100, 2),
                "risk_contribution_percent": round(float(contributions[i]), 2),
            }
        )
    return res


def compute_rolling_beta(
    asset_returns: pd.Series, benchmark_returns: pd.Series, window: int = 60
) -> list[dict[str, Any]]:
    """Compute rolling window Beta timeseries of an asset against a benchmark."""
    if window < 2:
        raise ValueError("window must be at least 2")
    aligned = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
    if len(aligned) < window:
        return []

    p_ret = aligned.iloc[:, 0]
    b_ret = aligned.iloc[:, 1]

    cov = p_ret.rolling(window=window).cov(b_ret)
    b_var = b_ret.rolling(window=window).var()
    rolling_beta = (cov / b_var.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)

    points: list[dict[str, Any]] = []
    for dt, val in rolling_beta.dropna().items():
        dt_str = str(dt).split(" ")[0]
        points.append({"date": dt_str, "beta": round(float(val), 3)})
    return points


def run_moving_average_crossover(
    prices: pd.Series,
    fast_window: int = 50,
    slow_window: int = 200,
    initial_capital: float = 10000.0,
) -> dict[str, Any]:
    """Execute Moving Average Crossover (Golden Cross / Death Cross) rule-based backtest.

    Buys when fast MA crosses above slow MA; exits to cash when fast MA crosses below slow MA.
    """
    if fast_window < 1 or slow_window <= fast_window:
        raise ValueError("slow_window must be greater than fast_window, and both must be positive")
    if not np.isfinite(initial_capital) or initial_capital <= 0:
        raise ValueError("initial_capital must be a finite positive number")
    clean_p = prices.replace([np.inf, -np.inf], np.nan).dropna().astype(float)
    if (clean_p <= 0).any():
        raise ValueError("prices must be positive")
    if len(clean_p) <= slow_window:
        raise ValueError(f"At least {slow_window + 1} price observations are required")

    fast_ma = clean_p.rolling(window=fast_window).mean()
    slow_ma = clean_p.rolling(window=slow_window).mean()

    # Position signal: 1 = In Market, 0 = In Cash
    signal = (fast_ma > slow_ma).astype(int).shift(1).fillna(0)
    asset_ret = clean_p.pct_change().fillna(0)
    strat_ret = signal * asset_ret

    equity = initial_capital * (1 + strat_ret).cumprod()
    bh_equity = initial_capital * (1 + asset_ret).cumprod()

    total_strat_ret = float((equity.iloc[-1] - initial_capital) / initial_capital)
    total_bh_ret = float((bh_equity.iloc[-1] - initial_capital) / initial_capital)

    years = _elapsed_years(clean_p.index)
    cagr = float((equity.iloc[-1] / initial_capital) ** (1.0 / years) - 1.0)

    trades = _closed_trade_records(clean_p, signal, equity)

    winning_trades = [t for t in trades if t["return_percent"] > 0]
    losing_trades = [t for t in trades if t["return_percent"] <= 0]
    win_rate = (len(winning_trades) / len(trades) * 100) if trades else 0.0

    gross_profit = sum(t["profit_loss"] for t in winning_trades)
    gross_loss = abs(sum(t["profit_loss"] for t in losing_trades))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else None

    _, max_dd_pct, _, _ = compute_drawdown_curve(strat_ret)

    eq_points = _sample_equity_curve(equity)

    return {
        "strategy_name": f"SMA Crossover ({fast_window}/{slow_window})",
        "ending_capital": round(float(equity.iloc[-1]), 2),
        "total_return_percent": round(total_strat_ret * 100, 2),
        "cagr_percent": round(cagr * 100, 2),
        "buy_and_hold_return_percent": round(total_bh_ret * 100, 2),
        "win_rate_percent": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2) if profit_factor is not None else None,
        "total_trades": len(trades),
        "max_drawdown_percent": max_dd_pct,
        "trades": trades[-10:],
        "equity_curve": eq_points,
    }


def run_rsi_mean_reversion(
    prices: pd.Series,
    rsi_window: int = 14,
    oversold: float = 30.0,
    overbought: float = 70.0,
    initial_capital: float = 10000.0,
) -> dict[str, Any]:
    """Execute RSI Mean-Reversion rule-based backtest.

    Buys when RSI < oversold threshold; exits to cash when RSI > overbought threshold.
    """
    if rsi_window < 2:
        raise ValueError("rsi_window must be at least 2")
    if not 0 <= oversold < overbought <= 100:
        raise ValueError("RSI thresholds must satisfy 0 <= oversold < overbought <= 100")
    if not np.isfinite(initial_capital) or initial_capital <= 0:
        raise ValueError("initial_capital must be a finite positive number")
    clean_p = prices.replace([np.inf, -np.inf], np.nan).dropna().astype(float)
    if (clean_p <= 0).any():
        raise ValueError("prices must be positive")
    if len(clean_p) <= rsi_window + 10:
        raise ValueError(f"At least {rsi_window + 11} price observations are required")

    # Calculate RSI
    delta = clean_p.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window).mean()
    rs = gain / loss.replace(0, 0.0001)
    rsi = 100 - (100 / (1 + rs))

    # Generate signals
    in_pos = False
    signals = []
    for val in rsi:
        if pd.isna(val):
            signals.append(0)
        elif not in_pos and val < oversold:
            in_pos = True
            signals.append(1)
        elif in_pos and val > overbought:
            in_pos = False
            signals.append(0)
        else:
            signals.append(1 if in_pos else 0)

    signal_series = pd.Series(signals, index=clean_p.index).shift(1).fillna(0)
    asset_ret = clean_p.pct_change().fillna(0)
    strat_ret = signal_series * asset_ret

    equity = initial_capital * (1 + strat_ret).cumprod()
    bh_equity = initial_capital * (1 + asset_ret).cumprod()

    total_strat_ret = float((equity.iloc[-1] - initial_capital) / initial_capital)
    total_bh_ret = float((bh_equity.iloc[-1] - initial_capital) / initial_capital)

    years = _elapsed_years(clean_p.index)
    cagr = float((equity.iloc[-1] / initial_capital) ** (1.0 / years) - 1.0)

    trades = _closed_trade_records(clean_p, signal_series, equity)

    winning_trades = [t for t in trades if t["return_percent"] > 0]
    losing_trades = [t for t in trades if t["return_percent"] <= 0]
    win_rate = (len(winning_trades) / len(trades) * 100) if trades else 0.0

    gross_profit = sum(t["profit_loss"] for t in winning_trades)
    gross_loss = abs(sum(t["profit_loss"] for t in losing_trades))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else None

    _, max_dd_pct, _, _ = compute_drawdown_curve(strat_ret)

    eq_points = _sample_equity_curve(equity)

    return {
        "strategy_name": f"RSI Mean-Reversion ({rsi_window} RSI < {oversold} / > {overbought})",
        "ending_capital": round(float(equity.iloc[-1]), 2),
        "total_return_percent": round(total_strat_ret * 100, 2),
        "cagr_percent": round(cagr * 100, 2),
        "buy_and_hold_return_percent": round(total_bh_ret * 100, 2),
        "win_rate_percent": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2) if profit_factor is not None else None,
        "total_trades": len(trades),
        "max_drawdown_percent": max_dd_pct,
        "trades": trades[-10:],
        "equity_curve": eq_points,
    }


def compute_factor_regressions(asset_returns: pd.Series, factor_returns_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Compute multi-factor linear regression exposures (Beta, Alpha, t-statistic, R-squared)."""
    aligned = pd.concat([asset_returns, factor_returns_df], axis=1).dropna()
    if len(aligned) < 20:
        return []

    y = aligned.iloc[:, 0].values
    x_matrix = aligned.iloc[:, 1:].values

    # Add constant intercept for Alpha

    x_with_const = np.column_stack([np.ones(len(y)), x_matrix])

    try:
        beta_coeffs, _, _, _ = np.linalg.lstsq(x_with_const, y, rcond=None)
        alpha = float(beta_coeffs[0] * 252)

        # Residuals and R-squared
        y_pred = x_with_const.dot(beta_coeffs)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r_sq = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

        res: list[dict[str, Any]] = [
            {"factor": "Alpha (Annualized Intercept)", "exposure_beta": round(alpha * 100, 2), "unit": "%"}
        ]
        for i, col in enumerate(factor_returns_df.columns):
            b_val = float(beta_coeffs[i + 1])
            res.append({"factor": col, "exposure_beta": round(b_val, 3), "unit": "Beta"})

        res.append({"factor": "Model R-Squared", "exposure_beta": round(r_sq, 3), "unit": "R2"})
        return res
    except Exception:
        return []
