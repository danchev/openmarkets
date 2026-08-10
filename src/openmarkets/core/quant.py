"""Core vectorized quantitative portfolio risk mathematics and strategy backtesting engines."""

from typing import Any

import numpy as np
import pandas as pd


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
    clean_df = price_df.dropna(how="all").ffill().dropna()
    daily_returns = clean_df.pct_change().dropna()

    num_assets = len(clean_df.columns)
    if weights is None or len(weights) != num_assets:
        norm_weights = [1.0 / num_assets] * num_assets
    else:
        total_w = sum(weights)
        norm_weights = [w / total_w for w in weights] if total_w > 0 else [1.0 / num_assets] * num_assets

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
    if returns.empty or len(returns) < 2:
        return {
            "annualized_return_percent": 0.0,
            "annualized_volatility_percent": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "calmar_ratio": 0.0,
            "max_drawdown_percent": 0.0,
            "var_95_percent": 0.0,
            "var_99_percent": 0.0,
            "cvar_95_percent": 0.0,
            "cvar_99_percent": 0.0,
            "beta": 1.0,
            "alpha_percent": 0.0,
            "r_squared": 1.0,
        }

    mean_daily = returns.mean()
    ann_ret = float(mean_daily * 252)
    ann_vol = float(returns.std() * np.sqrt(252))

    # Sharpe Ratio
    sharpe = (ann_ret - risk_free_rate) / ann_vol if ann_vol > 0 else 0.0

    # Sortino Ratio (downside risk deviation)
    neg_ret = returns[returns < 0]
    downside_std = float(neg_ret.std() * np.sqrt(252)) if len(neg_ret) > 1 else 0.0001
    sortino = (ann_ret - risk_free_rate) / downside_std if downside_std > 0 else 0.0

    # Max Drawdown & Calmar Ratio
    _, max_dd_pct, _, _ = compute_drawdown_curve(returns)
    abs_dd = abs(max_dd_pct) / 100.0
    calmar = (ann_ret / abs_dd) if abs_dd > 0 else (ann_ret if ann_ret > 0 else 0.0)

    # Value-at-Risk (Historical VaR)
    var_95 = float(np.percentile(returns, 5))
    var_99 = float(np.percentile(returns, 1))

    # Conditional VaR (Expected Shortfall)
    tail_95 = returns[returns <= var_95]
    cvar_95 = float(tail_95.mean()) if not tail_95.empty else var_95

    tail_99 = returns[returns <= var_99]
    cvar_99 = float(tail_99.mean()) if not tail_99.empty else var_99

    # Beta and Alpha vs Benchmark
    beta = 1.0
    alpha = 0.0
    r_squared = 1.0

    if benchmark_returns is not None and not benchmark_returns.empty:
        aligned = pd.concat([returns, benchmark_returns], axis=1).dropna()
        if len(aligned) > 5:
            p_ret = aligned.iloc[:, 0]
            b_ret = aligned.iloc[:, 1]
            cov = np.cov(p_ret, b_ret)[0, 1]
            b_var = np.var(b_ret)
            if b_var > 0:
                beta = float(cov / b_var)
                b_ann_ret = float(b_ret.mean() * 252)
                alpha = float(ann_ret - (risk_free_rate + beta * (b_ann_ret - risk_free_rate)))
                corr = np.corrcoef(p_ret, b_ret)[0, 1]
                r_squared = float(corr**2)

    return {
        "annualized_return_percent": round(ann_ret * 100, 2),
        "annualized_volatility_percent": round(ann_vol * 100, 2),
        "sharpe_ratio": round(sharpe, 3),
        "sortino_ratio": round(sortino, 3),
        "calmar_ratio": round(calmar, 3),
        "max_drawdown_percent": max_dd_pct,
        "var_95_percent": round(var_95 * 100, 2),
        "var_99_percent": round(var_99 * 100, 2),
        "cvar_95_percent": round(cvar_95 * 100, 2),
        "cvar_99_percent": round(cvar_99 * 100, 2),
        "beta": round(beta, 3),
        "alpha_percent": round(alpha * 100, 2),
        "r_squared": round(r_squared, 3),
    }


def compute_correlation_and_covariance(
    price_df: pd.DataFrame,
) -> tuple[list[str], dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    """Compute pairwise correlation matrix and annualized covariance matrix across asset returns."""
    clean_df = price_df.dropna(how="all").ffill().dropna()
    returns = clean_df.pct_change().dropna()
    assets = list(clean_df.columns)

    corr_df = returns.corr()
    cov_df = returns.cov() * 252

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
    """Compute Inverse-Volatility Risk Parity asset allocation weights.

    Assets with lower historical volatility receive higher allocations so each asset
    contributes approximately equal risk to the overall portfolio.
    """
    clean_df = price_df.dropna(how="all").ffill().dropna()
    returns = clean_df.pct_change().dropna()
    vols = returns.std() * np.sqrt(252)

    inv_vols = 1.0 / vols.replace(0, 0.0001)
    total_inv_vol = inv_vols.sum()
    weights = inv_vols / total_inv_vol

    res: list[dict[str, Any]] = []
    for ticker in clean_df.columns:
        w = float(weights[ticker])
        v = float(vols[ticker])
        res.append(
            {
                "ticker": ticker,
                "weight_percent": round(w * 100, 2),
                "annualized_volatility_percent": round(v * 100, 2),
                "risk_contribution_percent": round(w * v * 100, 2),
            }
        )
    return res


def compute_minimum_variance_weights(price_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Compute analytical Minimum Variance portfolio weights using covariance matrix inversion.

    Constrained to long-only non-negative weights.
    """
    clean_df = price_df.dropna(how="all").ffill().dropna()
    returns = clean_df.pct_change().dropna()
    cov = returns.cov().values * 252

    # Invert covariance matrix (with Tikhonov ridge regularization for matrix stability)
    num_assets = cov.shape[0]
    ridge = np.eye(num_assets) * 1e-4
    try:
        inv_cov = np.linalg.inv(cov + ridge)
        ones = np.ones(num_assets)
        raw_weights = inv_cov.dot(ones) / (ones.T.dot(inv_cov).dot(ones))
        # Long only clipping
        clipped = np.clip(raw_weights, 0, None)
        norm_weights = clipped / clipped.sum() if clipped.sum() > 0 else np.ones(num_assets) / num_assets
    except Exception:
        norm_weights = np.ones(num_assets) / num_assets

    vols = returns.std() * np.sqrt(252)
    res: list[dict[str, Any]] = []
    for i, ticker in enumerate(clean_df.columns):
        w = float(norm_weights[i])
        v = float(vols[ticker])
        res.append(
            {
                "ticker": ticker,
                "weight_percent": round(w * 100, 2),
                "annualized_volatility_percent": round(v * 100, 2),
                "risk_contribution_percent": round(w * v * 100, 2),
            }
        )
    return res


def compute_rolling_beta(
    asset_returns: pd.Series, benchmark_returns: pd.Series, window: int = 60
) -> list[dict[str, Any]]:
    """Compute rolling window Beta timeseries of an asset against a benchmark."""
    aligned = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
    if len(aligned) < window:
        return []

    p_ret = aligned.iloc[:, 0]
    b_ret = aligned.iloc[:, 1]

    cov = p_ret.rolling(window=window).cov(b_ret)
    b_var = b_ret.rolling(window=window).var()
    rolling_beta = cov / b_var

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
    clean_p = prices.dropna()
    if len(clean_p) <= slow_window:
        return {
            "strategy_name": f"SMA Crossover ({fast_window}/{slow_window})",
            "total_return_percent": 0.0,
            "cagr_percent": 0.0,
            "buy_and_hold_return_percent": 0.0,
            "win_rate_percent": 0.0,
            "profit_factor": 0.0,
            "total_trades": 0,
            "max_drawdown_percent": 0.0,
            "trades": [],
            "equity_curve": [],
        }

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

    years = max(len(clean_p) / 252.0, 0.1)
    cagr = float((equity.iloc[-1] / initial_capital) ** (1.0 / years) - 1.0)

    # Trade tracking
    trades: list[dict[str, Any]] = []
    in_trade = False
    entry_date = None
    entry_price = 0.0

    pos_diff = signal.diff()
    for dt, diff in pos_diff.items():
        dt_str = str(dt).split(" ")[0]
        p = float(clean_p.loc[dt])
        if diff == 1 and not in_trade:
            in_trade = True
            entry_date = dt_str
            entry_price = p
        elif diff == -1 and in_trade:
            in_trade = False
            ret_pct = float((p - entry_price) / entry_price * 100) if entry_price > 0 else 0.0
            trades.append(
                {
                    "entry_date": entry_date,
                    "exit_date": dt_str,
                    "entry_price": round(entry_price, 2),
                    "exit_price": round(p, 2),
                    "return_percent": round(ret_pct, 2),
                    "profit_loss": round((p - entry_price) * (initial_capital / entry_price), 2)
                    if entry_price > 0
                    else 0.0,
                }
            )

    winning_trades = [t for t in trades if t["return_percent"] > 0]
    losing_trades = [t for t in trades if t["return_percent"] <= 0]
    win_rate = (len(winning_trades) / len(trades) * 100) if trades else 0.0

    gross_profit = sum(t["profit_loss"] for t in winning_trades)
    gross_loss = abs(sum(t["profit_loss"] for t in losing_trades))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 1.0)

    _, max_dd_pct, _, _ = compute_drawdown_curve(strat_ret)

    # Downsample equity curve to monthly points
    eq_points: list[dict[str, Any]] = []
    sampled = equity.iloc[:: max(1, len(equity) // 30)]
    for dt, val in sampled.items():
        dt_str = str(dt).split(" ")[0]
        eq_points.append({"date": dt_str, "equity": round(float(val), 2)})

    return {
        "strategy_name": f"SMA Crossover ({fast_window}/{slow_window})",
        "total_return_percent": round(total_strat_ret * 100, 2),
        "cagr_percent": round(cagr * 100, 2),
        "buy_and_hold_return_percent": round(total_bh_ret * 100, 2),
        "win_rate_percent": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2),
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
    clean_p = prices.dropna()
    if len(clean_p) <= rsi_window + 10:
        return {
            "strategy_name": f"RSI Mean-Reversion ({rsi_window} RSI < {oversold} / > {overbought})",
            "total_return_percent": 0.0,
            "cagr_percent": 0.0,
            "buy_and_hold_return_percent": 0.0,
            "win_rate_percent": 0.0,
            "profit_factor": 0.0,
            "total_trades": 0,
            "max_drawdown_percent": 0.0,
            "trades": [],
            "equity_curve": [],
        }

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

    years = max(len(clean_p) / 252.0, 0.1)
    cagr = float((equity.iloc[-1] / initial_capital) ** (1.0 / years) - 1.0)

    # Trade tracking
    trades: list[dict[str, Any]] = []
    in_trade = False
    entry_date = None
    entry_price = 0.0

    pos_diff = signal_series.diff()
    for dt, diff in pos_diff.items():
        dt_str = str(dt).split(" ")[0]
        p = float(clean_p.loc[dt])
        if diff == 1 and not in_trade:
            in_trade = True
            entry_date = dt_str
            entry_price = p
        elif diff == -1 and in_trade:
            in_trade = False
            ret_pct = float((p - entry_price) / entry_price * 100) if entry_price > 0 else 0.0
            trades.append(
                {
                    "entry_date": entry_date,
                    "exit_date": dt_str,
                    "entry_price": round(entry_price, 2),
                    "exit_price": round(p, 2),
                    "return_percent": round(ret_pct, 2),
                    "profit_loss": round((p - entry_price) * (initial_capital / entry_price), 2)
                    if entry_price > 0
                    else 0.0,
                }
            )

    winning_trades = [t for t in trades if t["return_percent"] > 0]
    losing_trades = [t for t in trades if t["return_percent"] <= 0]
    win_rate = (len(winning_trades) / len(trades) * 100) if trades else 0.0

    gross_profit = sum(t["profit_loss"] for t in winning_trades)
    gross_loss = abs(sum(t["profit_loss"] for t in losing_trades))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 1.0)

    _, max_dd_pct, _, _ = compute_drawdown_curve(strat_ret)

    eq_points: list[dict[str, Any]] = []
    sampled = equity.iloc[:: max(1, len(equity) // 30)]
    for dt, val in sampled.items():
        dt_str = str(dt).split(" ")[0]
        eq_points.append({"date": dt_str, "equity": round(float(val), 2)})

    return {
        "strategy_name": f"RSI Mean-Reversion ({rsi_window} RSI < {oversold} / > {overbought})",
        "total_return_percent": round(total_strat_ret * 100, 2),
        "cagr_percent": round(cagr * 100, 2),
        "buy_and_hold_return_percent": round(total_bh_ret * 100, 2),
        "win_rate_percent": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2),
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
