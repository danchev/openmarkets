"""Repository layer for quantitative portfolio risk calculations, allocation, and backtesting."""

from typing import Protocol

import pandas as pd
import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.core.exceptions import DataUnavailableError
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
from openmarkets.schemas.portfolio import (
    AssetAllocationWeight,
    BacktestResult,
    BacktestTrade,
    CorrelationMatrixResult,
    DrawdownPoint,
    DrawdownSeriesResult,
    EquityPoint,
    FactorExposureEntry,
    FactorExposuresResult,
    PortfolioAllocationResult,
    PortfolioRiskMetrics,
    RollingBetaSeries,
    RollingMetricPoint,
)


class PortfolioRepository(Protocol):
    """Protocol defining the quantitative portfolio repository interface."""

    def calculate_portfolio_risk(
        self,
        tickers: list[str],
        weights: list[float] | None = None,
        benchmark: str = "SPY",
        period: str = "1y",
        risk_free_rate: float = 0.045,
        session: Session | None = None,
    ) -> PortfolioRiskMetrics: ...

    def calculate_correlation_matrix(
        self,
        tickers: list[str],
        period: str = "1y",
        session: Session | None = None,
    ) -> CorrelationMatrixResult: ...

    def calculate_risk_parity_weights(
        self,
        tickers: list[str],
        period: str = "1y",
        session: Session | None = None,
    ) -> PortfolioAllocationResult: ...

    def calculate_minimum_variance_portfolio(
        self,
        tickers: list[str],
        period: str = "1y",
        session: Session | None = None,
    ) -> PortfolioAllocationResult: ...

    def calculate_rolling_beta(
        self,
        ticker: str,
        benchmark: str = "SPY",
        window: int = 60,
        period: str = "2y",
        session: Session | None = None,
    ) -> RollingBetaSeries: ...

    def calculate_drawdown_series(
        self,
        tickers: list[str],
        weights: list[float] | None = None,
        period: str = "2y",
        session: Session | None = None,
    ) -> DrawdownSeriesResult: ...

    def backtest_trend_following_strategy(
        self,
        ticker: str,
        fast_window: int = 50,
        slow_window: int = 200,
        period: str = "5y",
        initial_capital: float = 10000.0,
        session: Session | None = None,
    ) -> BacktestResult: ...

    def backtest_mean_reversion_strategy(
        self,
        ticker: str,
        rsi_window: int = 14,
        oversold_threshold: float = 30.0,
        overbought_threshold: float = 70.0,
        period: str = "2y",
        initial_capital: float = 10000.0,
        session: Session | None = None,
    ) -> BacktestResult: ...

    def calculate_factor_exposures(
        self,
        ticker: str,
        period: str = "2y",
        session: Session | None = None,
    ) -> FactorExposuresResult: ...


class QuantPortfolioRepository:
    """Concrete repository executing quantitative portfolio mathematics and backtests."""

    def _fetch_price_history(
        self, tickers: list[str], period: str = "1y", session: Session | None = None
    ) -> pd.DataFrame:
        """Fetch historical close price DataFrame for one or multiple tickers."""
        cleaned_tickers = [t.strip().upper() for t in tickers if t.strip()]
        if not cleaned_tickers:
            raise DataUnavailableError("At least one ticker must be provided.")

        try:
            if len(cleaned_tickers) == 1:
                t = yf.Ticker(cleaned_tickers[0], session=session)
                hist = t.history(period=period, interval="1d")
                if hist.empty:
                    raise DataUnavailableError(f"No price history found for ticker '{cleaned_tickers[0]}'.")
                df = pd.DataFrame({cleaned_tickers[0]: hist["Close"]})
            else:
                data = yf.download(
                    cleaned_tickers,
                    period=period,
                    interval="1d",
                    session=session,
                    progress=False,
                    auto_adjust=True,
                )
                if data.empty:
                    raise DataUnavailableError(f"No price history found for tickers {cleaned_tickers}.")
                df = data["Close"]
                if isinstance(df, pd.Series):
                    df = pd.DataFrame({cleaned_tickers[0]: df})
            return df.dropna(how="all").ffill().dropna()
        except Exception as e:
            if isinstance(e, DataUnavailableError):
                raise
            raise DataUnavailableError(f"Failed to fetch market history for {cleaned_tickers}: {e}") from e

    def calculate_portfolio_risk(
        self,
        tickers: list[str],
        weights: list[float] | None = None,
        benchmark: str = "SPY",
        period: str = "1y",
        risk_free_rate: float = 0.045,
        session: Session | None = None,
    ) -> PortfolioRiskMetrics:
        """Calculate multi-asset portfolio Sharpe, Sortino, VaR, CVaR, Beta, and Max Drawdown."""
        clean_tickers = [t.strip().upper() for t in tickers if t.strip()]
        all_symbols = list(set(clean_tickers + [benchmark.strip().upper()]))

        price_df = self._fetch_price_history(all_symbols, period=period, session=session)
        bench_sym = benchmark.strip().upper()

        if bench_sym not in price_df.columns:
            bench_returns = None
        else:
            bench_returns = price_df[bench_sym].pct_change().dropna()

        portfolio_prices = price_df[[t for t in clean_tickers if t in price_df.columns]]
        port_returns, norm_w = compute_portfolio_returns(portfolio_prices, weights=weights)

        metrics = compute_risk_metrics(
            returns=port_returns, benchmark_returns=bench_returns, risk_free_rate=risk_free_rate
        )

        return PortfolioRiskMetrics(
            tickers=list(portfolio_prices.columns),
            weights=[round(w, 4) for w in norm_w],
            benchmark=benchmark.upper(),
            period=period,
            **metrics,
        )

    def calculate_correlation_matrix(
        self,
        tickers: list[str],
        period: str = "1y",
        session: Session | None = None,
    ) -> CorrelationMatrixResult:
        """Calculate pairwise correlation matrix and covariance matrix across asset basket."""
        price_df = self._fetch_price_history(tickers, period=period, session=session)
        assets, corr_dict, cov_dict = compute_correlation_and_covariance(price_df)
        return CorrelationMatrixResult(
            assets=assets,
            period=period,
            correlation_matrix=corr_dict,
            annualized_covariance_matrix=cov_dict,
        )

    def calculate_risk_parity_weights(
        self,
        tickers: list[str],
        period: str = "1y",
        session: Session | None = None,
    ) -> PortfolioAllocationResult:
        """Calculate Inverse-Volatility Risk Parity asset allocation weights."""
        price_df = self._fetch_price_history(tickers, period=period, session=session)
        allocations = compute_risk_parity_weights(price_df)
        return PortfolioAllocationResult(
            strategy="Inverse-Volatility Risk Parity",
            period=period,
            allocations=[AssetAllocationWeight(**a) for a in allocations],
        )

    def calculate_minimum_variance_portfolio(
        self,
        tickers: list[str],
        period: str = "1y",
        session: Session | None = None,
    ) -> PortfolioAllocationResult:
        """Calculate analytical long-only Minimum Variance portfolio allocation weights."""
        price_df = self._fetch_price_history(tickers, period=period, session=session)
        allocations = compute_minimum_variance_weights(price_df)
        return PortfolioAllocationResult(
            strategy="Markowitz Minimum Variance Portfolio",
            period=period,
            allocations=[AssetAllocationWeight(**a) for a in allocations],
        )

    def calculate_rolling_beta(
        self,
        ticker: str,
        benchmark: str = "SPY",
        window: int = 60,
        period: str = "2y",
        session: Session | None = None,
    ) -> RollingBetaSeries:
        """Calculate historical rolling window Beta sensitivity series against benchmark."""
        sym = ticker.strip().upper()
        bench = benchmark.strip().upper()
        price_df = self._fetch_price_history([sym, bench], period=period, session=session)

        ret_asset = price_df[sym].pct_change().dropna()
        ret_bench = price_df[bench].pct_change().dropna()

        points = compute_rolling_beta(ret_asset, ret_bench, window=window)
        current_b = points[-1]["beta"] if points else 1.0

        return RollingBetaSeries(
            ticker=sym,
            benchmark=bench,
            window=window,
            current_beta=current_b,
            data_points=[RollingMetricPoint(**p) for p in points],
        )

    def calculate_drawdown_series(
        self,
        tickers: list[str],
        weights: list[float] | None = None,
        period: str = "2y",
        session: Session | None = None,
    ) -> DrawdownSeriesResult:
        """Calculate historical underwater drawdown curve and maximum peak-to-trough decline."""
        price_df = self._fetch_price_history(tickers, period=period, session=session)
        port_returns, _ = compute_portfolio_returns(price_df, weights=weights)

        points, max_dd_pct, peak_dt, trough_dt = compute_drawdown_curve(port_returns)
        return DrawdownSeriesResult(
            portfolio=list(price_df.columns),
            max_drawdown_percent=max_dd_pct,
            peak_date=peak_dt,
            trough_date=trough_dt,
            data_points=[DrawdownPoint(**p) for p in points],
        )

    def backtest_trend_following_strategy(
        self,
        ticker: str,
        fast_window: int = 50,
        slow_window: int = 200,
        period: str = "5y",
        initial_capital: float = 10000.0,
        session: Session | None = None,
    ) -> BacktestResult:
        """Execute Moving Average Crossover (Golden Cross / Death Cross) rule-based backtest."""
        sym = ticker.strip().upper()
        price_df = self._fetch_price_history([sym], period=period, session=session)
        prices = price_df[sym]

        raw = run_moving_average_crossover(
            prices=prices,
            fast_window=fast_window,
            slow_window=slow_window,
            initial_capital=initial_capital,
        )

        end_cap = round(initial_capital * (1 + raw["total_return_percent"] / 100.0), 2)
        trades = [BacktestTrade(**t) for t in raw.get("trades", [])]
        curve = [EquityPoint(**pt) for pt in raw.get("equity_curve", [])]

        return BacktestResult(
            ticker=sym,
            strategy_name=raw["strategy_name"],
            period=period,
            initial_capital=initial_capital,
            ending_capital=end_cap,
            total_return_percent=raw["total_return_percent"],
            cagr_percent=raw["cagr_percent"],
            buy_and_hold_return_percent=raw["buy_and_hold_return_percent"],
            win_rate_percent=raw["win_rate_percent"],
            profit_factor=raw["profit_factor"],
            total_trades=raw["total_trades"],
            max_drawdown_percent=raw["max_drawdown_percent"],
            trades=trades,
            equity_curve=curve,
        )

    def backtest_mean_reversion_strategy(
        self,
        ticker: str,
        rsi_window: int = 14,
        oversold_threshold: float = 30.0,
        overbought_threshold: float = 70.0,
        period: str = "2y",
        initial_capital: float = 10000.0,
        session: Session | None = None,
    ) -> BacktestResult:
        """Execute RSI Mean-Reversion rule-based backtest."""
        sym = ticker.strip().upper()
        price_df = self._fetch_price_history([sym], period=period, session=session)
        prices = price_df[sym]

        raw = run_rsi_mean_reversion(
            prices=prices,
            rsi_window=rsi_window,
            oversold=oversold_threshold,
            overbought=overbought_threshold,
            initial_capital=initial_capital,
        )

        end_cap = round(initial_capital * (1 + raw["total_return_percent"] / 100.0), 2)
        trades = [BacktestTrade(**t) for t in raw.get("trades", [])]
        curve = [EquityPoint(**pt) for pt in raw.get("equity_curve", [])]

        return BacktestResult(
            ticker=sym,
            strategy_name=raw["strategy_name"],
            period=period,
            initial_capital=initial_capital,
            ending_capital=end_cap,
            total_return_percent=raw["total_return_percent"],
            cagr_percent=raw["cagr_percent"],
            buy_and_hold_return_percent=raw["buy_and_hold_return_percent"],
            win_rate_percent=raw["win_rate_percent"],
            profit_factor=raw["profit_factor"],
            total_trades=raw["total_trades"],
            max_drawdown_percent=raw["max_drawdown_percent"],
            trades=trades,
            equity_curve=curve,
        )

    def calculate_factor_exposures(
        self,
        ticker: str,
        period: str = "2y",
        session: Session | None = None,
    ) -> FactorExposuresResult:
        """Calculate multi-factor linear regression exposures against benchmark market factors."""
        sym = ticker.strip().upper()
        factors = ["SPY", "QQQ", "IWM", "TLT", "GLD"]
        price_df = self._fetch_price_history([sym] + factors, period=period, session=session)

        asset_ret = price_df[sym].pct_change().dropna()
        factor_df = price_df[factors].pct_change().dropna()

        entries = compute_factor_regressions(asset_ret, factor_df)
        return FactorExposuresResult(
            ticker=sym,
            period=period,
            exposures=[FactorExposureEntry(**e) for e in entries],
        )
