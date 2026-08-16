from typing import Annotated

from curl_cffi.requests import Session
from pydantic import Field

from openmarkets.core.cache import cached
from openmarkets.core.http import get_session
from openmarkets.core.types import Period
from openmarkets.repositories.portfolio import PortfolioRepository, QuantPortfolioRepository
from openmarkets.schemas.portfolio import (
    BacktestResult,
    CorrelationMatrixResult,
    DrawdownSeriesResult,
    FactorExposuresResult,
    PortfolioAllocationResult,
    PortfolioRiskMetrics,
    RollingBetaSeries,
)
from openmarkets.services.utils import ToolRegistrationMixin, tool


class PortfolioService(ToolRegistrationMixin):
    """Service layer for quantitative portfolio risk analysis, asset allocation, and algorithmic backtesting.

    Provides computational methods for calculating multi-asset Sharpe/Sortino ratios,
    Value-at-Risk (VaR/CVaR), correlation matrices, Risk Parity and Markowitz Minimum Variance
    allocations, rolling Beta sensitivities, multi-factor regressions, and rule-based strategy backtests.
    """

    def __init__(
        self,
        repository: PortfolioRepository | None = None,
        session: Session | None = None,
    ) -> None:
        """Initialize the PortfolioService.

        Args:
            repository: Repository instance for data and analytics. Defaults to QuantPortfolioRepository.
            session: HTTP session for requests.
        """
        self.repository: PortfolioRepository = repository or QuantPortfolioRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests."""
        return self._session if self._session is not None else get_session()

    @tool
    @cached(ttl=300.0)
    def calculate_portfolio_risk_metrics(
        self,
        tickers: Annotated[
            list[str],
            Field(min_length=1, description="List of asset tickers in the portfolio"),
        ],
        weights: Annotated[
            list[float] | None,
            Field(
                min_length=1,
                description="Optional list of non-negative portfolio weights, normalized to sum to 1.0",
            ),
        ] = None,
        benchmark: Annotated[
            str, Field(description="Benchmark ticker symbol used to calculate Beta and Alpha (e.g. 'SPY', 'QQQ')")
        ] = "SPY",
        period: Annotated[Period, Field(description="Historical lookback period")] = "1y",
        risk_free_rate: Annotated[
            float, Field(allow_inf_nan=False, description="Annualized risk-free interest rate (e.g. 0.045 for 4.5%)")
        ] = 0.045,
    ) -> PortfolioRiskMetrics:
        """Calculate comprehensive quantitative risk and performance metrics for a multi-asset portfolio.

        Computes Annualized Return, Annualized Volatility, Sharpe Ratio, Sortino Ratio, Calmar Ratio,
        Max Drawdown, 1-Day Historical Value-at-Risk (VaR 95% & 99%), Expected Shortfall (CVaR 95% & 99%),
        Beta, and Jensen's Alpha against a benchmark.

        Args:
            tickers: Asset ticker symbols.
            weights: Portfolio weights.
            benchmark: Benchmark symbol.
            period: Lookback duration.
            risk_free_rate: Risk-free rate.

        Returns:
            PortfolioRiskMetrics object with risk-adjusted performance breakdown.
        """
        return self.repository.calculate_portfolio_risk(
            tickers=tickers,
            weights=weights,
            benchmark=benchmark,
            period=period,
            risk_free_rate=risk_free_rate,
            session=self.session,
        )

    @tool
    @cached(ttl=300.0)
    def calculate_asset_correlation_matrix(
        self,
        tickers: Annotated[
            list[str],
            Field(min_length=1, description="List of asset tickers to correlate"),
        ],
        period: Annotated[Period, Field(description="Historical lookback period")] = "1y",
    ) -> CorrelationMatrixResult:
        """Calculate pairwise correlation matrix and annualized covariance matrix across a basket of assets.

        Evaluates diversification benefits and cross-asset correlations (-1.0 to +1.0) across equities,
        ETFs, crypto, commodities, and fixed income.

        Args:
            tickers: Asset symbols to compare.
            period: Lookback timespan.

        Returns:
            CorrelationMatrixResult with correlation and covariance matrices.
        """
        return self.repository.calculate_correlation_matrix(tickers=tickers, period=period, session=self.session)

    @tool
    @cached(ttl=300.0)
    def calculate_risk_parity_weights(
        self,
        tickers: Annotated[
            list[str],
            Field(min_length=1, description="List of asset tickers to allocate"),
        ],
        period: Annotated[Period, Field(description="Historical lookback period used to measure volatility")] = "1y",
    ) -> PortfolioAllocationResult:
        """Calculate inverse-volatility asset allocation weights.

        Allocates capital inversely proportional to historical volatility so each asset
        reports each asset's actual covariance-based contribution to portfolio risk.

        Args:
            tickers: Asset symbols to allocate.
            period: Historical volatility lookback duration.

        Returns:
            PortfolioAllocationResult with recommended percentage weights.
        """
        return self.repository.calculate_risk_parity_weights(tickers=tickers, period=period, session=self.session)

    @tool
    @cached(ttl=300.0)
    def calculate_minimum_variance_portfolio(
        self,
        tickers: Annotated[
            list[str],
            Field(min_length=1, description="List of asset tickers to optimize"),
        ],
        period: Annotated[Period, Field(description="Historical lookback period")] = "1y",
    ) -> PortfolioAllocationResult:
        """Calculate Markowitz numerical Minimum Variance portfolio allocation weights.

        Solves for long-only asset weights that minimize overall portfolio variance using the empirical
        covariance matrix.

        Args:
            tickers: Asset symbols.
            period: Lookback duration for covariance estimation.

        Returns:
            PortfolioAllocationResult with minimum variance asset weights.
        """
        return self.repository.calculate_minimum_variance_portfolio(
            tickers=tickers, period=period, session=self.session
        )

    @tool
    @cached(ttl=300.0)
    def calculate_rolling_beta(
        self,
        ticker: Annotated[str, Field(description="Asset ticker symbol to analyze (e.g. 'NVDA', 'TSLA')")],
        benchmark: Annotated[str, Field(description="Benchmark ticker (e.g. 'SPY', 'QQQ')")] = "SPY",
        window: Annotated[int, Field(ge=2, description="Rolling calculation window in trading days")] = 60,
        period: Annotated[Period, Field(description="Historical lookback period")] = "2y",
    ) -> RollingBetaSeries:
        """Calculate historical rolling window Beta sensitivity series against a benchmark.

        Reveals how an asset's market correlation and systematic risk exposure have evolved over time.

        Args:
            ticker: Asset symbol.
            benchmark: Benchmark symbol.
            window: Rolling window length in days.
            period: Lookback duration.

        Returns:
            RollingBetaSeries with chronological rolling beta values.
        """
        return self.repository.calculate_rolling_beta(
            ticker=ticker,
            benchmark=benchmark,
            window=window,
            period=period,
            session=self.session,
        )

    @tool
    @cached(ttl=300.0)
    def calculate_drawdown_series(
        self,
        tickers: Annotated[
            list[str],
            Field(min_length=1, description="List of asset tickers in portfolio"),
        ],
        weights: Annotated[
            list[float] | None,
            Field(min_length=1, description="Optional portfolio allocation weights list"),
        ] = None,
        period: Annotated[Period, Field(description="Historical lookback period")] = "2y",
    ) -> DrawdownSeriesResult:
        """Calculate historical underwater drawdown curve and maximum peak-to-trough decline series.

        Evaluates historical capital drawdown depths and recovery timelines from previous peaks.

        Args:
            tickers: Portfolio asset tickers.
            weights: Portfolio weights.
            period: Lookback duration.

        Returns:
            DrawdownSeriesResult with underwater percentage drawdown points.
        """
        return self.repository.calculate_drawdown_series(
            tickers=tickers, weights=weights, period=period, session=self.session
        )

    @tool
    @cached(ttl=300.0)
    def backtest_trend_following_strategy(
        self,
        ticker: Annotated[str, Field(description="Asset ticker symbol to backtest (e.g. 'AAPL', 'NVDA', 'SPY')")],
        fast_window: Annotated[int, Field(ge=1, description="Fast moving average window in trading days")] = 50,
        slow_window: Annotated[int, Field(ge=2, description="Slow moving average window in trading days")] = 200,
        period: Annotated[Period, Field(description="Backtest duration")] = "5y",
        initial_capital: Annotated[float, Field(gt=0, description="Starting cash capital in USD")] = 10000.0,
    ) -> BacktestResult:
        """Execute Moving Average Crossover (Golden Cross / Death Cross) rule-based strategy backtest.

        Enters long position when fast MA crosses above slow MA; exits to cash when fast MA crosses below slow MA.
        Calculates cumulative return, CAGR, benchmark buy & hold comparison, win rate, profit factor, and equity curve.

        Args:
            ticker: Asset ticker.
            fast_window: Fast SMA period in days.
            slow_window: Slow SMA period in days.
            period: Backtest timespan.
            initial_capital: Starting capital in USD.

        Returns:
            BacktestResult with complete trade log and performance statistics.
        """
        return self.repository.backtest_trend_following_strategy(
            ticker=ticker,
            fast_window=fast_window,
            slow_window=slow_window,
            period=period,
            initial_capital=initial_capital,
            session=self.session,
        )

    @tool
    @cached(ttl=300.0)
    def backtest_mean_reversion_strategy(
        self,
        ticker: Annotated[str, Field(description="Asset ticker symbol to backtest (e.g. 'AAPL', 'MSFT', 'SPY')")],
        rsi_window: Annotated[int, Field(ge=2, description="RSI calculation window in days")] = 14,
        oversold_threshold: Annotated[
            float, Field(ge=0, le=100, description="RSI level to trigger position entry")
        ] = 30.0,
        overbought_threshold: Annotated[
            float, Field(ge=0, le=100, description="RSI level to trigger position exit to cash")
        ] = 70.0,
        period: Annotated[Period, Field(description="Backtest duration")] = "2y",
        initial_capital: Annotated[float, Field(gt=0, description="Starting cash capital in USD")] = 10000.0,
    ) -> BacktestResult:
        """Execute Relative Strength Index (RSI) Mean-Reversion strategy backtest.

        Enters long when RSI drops below oversold threshold; exits to cash when RSI reaches overbought threshold.
        Evaluates trade win rate, profit factor, max drawdown, and equity progression.

        Args:
            ticker: Asset ticker.
            rsi_window: RSI calculation window in days.
            oversold_threshold: RSI buy trigger level.
            overbought_threshold: RSI sell trigger level.
            period: Backtest timespan.
            initial_capital: Starting capital in USD.

        Returns:
            BacktestResult with performance metrics and closed trades.
        """
        return self.repository.backtest_mean_reversion_strategy(
            ticker=ticker,
            rsi_window=rsi_window,
            oversold_threshold=oversold_threshold,
            overbought_threshold=overbought_threshold,
            period=period,
            initial_capital=initial_capital,
            session=self.session,
        )

    @tool
    @cached(ttl=300.0)
    def calculate_factor_exposures(
        self,
        ticker: Annotated[str, Field(description="Asset ticker symbol to analyze (e.g. 'AAPL', 'NVDA', 'ARKK')")],
        period: Annotated[Period, Field(description="Regression lookback period")] = "2y",
    ) -> FactorExposuresResult:
        """Calculate multi-factor linear regression exposures against benchmark macro market drivers.

        Regresses asset returns against Market (SPY), Tech Growth (QQQ), Small-Cap (IWM), Treasuries (TLT),
        and Gold (GLD) to estimate systematic factor loadings, Jensen's Alpha, and R-squared.

        Args:
            ticker: Asset ticker.
            period: Lookback timespan.

        Returns:
            FactorExposuresResult with estimated factor betas and model statistics.
        """
        return self.repository.calculate_factor_exposures(ticker=ticker, period=period, session=self.session)


portfolio_service = PortfolioService()
