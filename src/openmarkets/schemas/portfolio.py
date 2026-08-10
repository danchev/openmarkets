"""Pydantic schemas for quantitative portfolio risk analytics, asset allocation, and strategy backtesting."""

from pydantic import BaseModel, ConfigDict, Field


class PortfolioRiskMetrics(BaseModel):
    """Comprehensive portfolio performance and risk decomposition metrics."""

    model_config = ConfigDict(populate_by_name=True)

    tickers: list[str] = Field(..., description="List of asset tickers in portfolio")
    weights: list[float] = Field(..., description="Normalized portfolio asset weights")
    benchmark: str = Field("SPY", description="Benchmark ticker used for Beta and Alpha")
    period: str = Field("1y", description="Historical lookback period")
    annualized_return_percent: float = Field(..., description="Annualized compound return (%)")
    annualized_volatility_percent: float = Field(..., description="Annualized standard deviation / volatility (%)")
    sharpe_ratio: float = Field(..., description="Sharpe ratio (risk-adjusted excess return above risk-free rate)")
    sortino_ratio: float = Field(..., description="Sortino ratio (downside deviation adjusted return)")
    calmar_ratio: float = Field(..., description="Calmar ratio (Annual return / Max drawdown)")
    max_drawdown_percent: float = Field(..., description="Maximum peak-to-trough decline (%)")
    var_95_percent: float = Field(..., description="1-Day Historical Value-at-Risk at 95% confidence (%)")
    var_99_percent: float = Field(..., description="1-Day Historical Value-at-Risk at 99% confidence (%)")
    cvar_95_percent: float = Field(..., description="1-Day Expected Shortfall / Conditional VaR at 95% confidence (%)")
    cvar_99_percent: float = Field(..., description="1-Day Expected Shortfall / Conditional VaR at 99% confidence (%)")
    beta: float = Field(..., description="Sensitivity / Beta relative to benchmark")
    alpha_percent: float = Field(..., description="Annualized Jensen's Alpha excess return (%)")
    r_squared: float = Field(..., description="R-Squared correlation coefficient to benchmark")


class CorrelationMatrixResult(BaseModel):
    """Pairwise correlation and covariance matrices across multi-asset baskets."""

    model_config = ConfigDict(populate_by_name=True)

    assets: list[str] = Field(..., description="Ordered list of asset tickers")
    period: str = Field("1y", description="Historical lookback period")
    correlation_matrix: dict[str, dict[str, float]] = Field(
        ..., description="Pairwise Pearson correlation matrix (-1.0 to +1.0)"
    )
    annualized_covariance_matrix: dict[str, dict[str, float]] = Field(..., description="Annualized covariance matrix")


class AssetAllocationWeight(BaseModel):
    """Target weight and risk metrics for a single asset in an allocation model."""

    model_config = ConfigDict(populate_by_name=True)

    ticker: str = Field(..., description="Asset ticker symbol")
    weight_percent: float = Field(..., description="Target portfolio allocation weight (%)")
    annualized_volatility_percent: float = Field(..., description="Asset historical annualized volatility (%)")
    risk_contribution_percent: float = Field(..., description="Effective risk contribution (%)")


class PortfolioAllocationResult(BaseModel):
    """Optimal asset allocation portfolio weights."""

    model_config = ConfigDict(populate_by_name=True)

    strategy: str = Field(..., description="Asset allocation strategy name (e.g. Risk Parity, Minimum Variance)")
    period: str = Field("1y", description="Historical lookback period used for optimization")
    allocations: list[AssetAllocationWeight] = Field(..., description="List of optimal asset weights")


class RollingMetricPoint(BaseModel):
    """A single historical observation point in a rolling metric timeseries."""

    model_config = ConfigDict(populate_by_name=True)

    date: str = Field(..., description="Date string (YYYY-MM-DD)")
    beta: float = Field(..., description="Rolling beta value")


class RollingBetaSeries(BaseModel):
    """Historical rolling window Beta sensitivity series against a benchmark."""

    model_config = ConfigDict(populate_by_name=True)

    ticker: str = Field(..., description="Asset ticker symbol")
    benchmark: str = Field("SPY", description="Benchmark ticker symbol")
    window: int = Field(60, description="Rolling calculation window in trading days")
    current_beta: float = Field(..., description="Most recent rolling beta value")
    data_points: list[RollingMetricPoint] = Field(default_factory=list, description="Historical rolling beta points")


class DrawdownPoint(BaseModel):
    """A single underwater drawdown point."""

    model_config = ConfigDict(populate_by_name=True)

    date: str = Field(..., description="Date string (YYYY-MM-DD)")
    drawdown_percent: float = Field(..., description="Percentage decline from historical peak (%)")
    high_water_mark: float = Field(..., description="Cumulative peak high water mark")


class DrawdownSeriesResult(BaseModel):
    """Historical underwater drawdown curve and recovery statistics."""

    model_config = ConfigDict(populate_by_name=True)

    portfolio: list[str] = Field(..., description="Portfolio tickers")
    max_drawdown_percent: float = Field(..., description="Maximum historical peak-to-trough drawdown (%)")
    peak_date: str | None = Field(None, description="Date of the peak before maximum drawdown")
    trough_date: str | None = Field(None, description="Date of the trough of maximum drawdown")
    data_points: list[DrawdownPoint] = Field(default_factory=list, description="Historical drawdown curve points")


class BacktestTrade(BaseModel):
    """A single closed trade record generated during a strategy backtest."""

    model_config = ConfigDict(populate_by_name=True)

    entry_date: str = Field(..., description="Position entry date")
    exit_date: str = Field(..., description="Position exit date")
    entry_price: float = Field(..., description="Execution entry price")
    exit_price: float = Field(..., description="Execution exit price")
    return_percent: float = Field(..., description="Percentage trade return (%)")
    profit_loss: float = Field(..., description="Dollar profit or loss")


class EquityPoint(BaseModel):
    """An equity curve observation point."""

    model_config = ConfigDict(populate_by_name=True)

    date: str = Field(..., description="Date string")
    equity: float = Field(..., description="Account equity balance ($)")


class BacktestResult(BaseModel):
    """Comprehensive performance report from a rule-based quantitative strategy backtest."""

    model_config = ConfigDict(populate_by_name=True)

    ticker: str = Field(..., description="Tested asset ticker")
    strategy_name: str = Field(..., description="Strategy name and parameters")
    period: str = Field("5y", description="Backtest lookback period")
    initial_capital: float = Field(10000.0, description="Starting cash capital")
    ending_capital: float = Field(..., description="Final equity capital")
    total_return_percent: float = Field(..., description="Cumulative strategy return (%)")
    cagr_percent: float = Field(..., description="Compound Annual Growth Rate (%)")
    buy_and_hold_return_percent: float = Field(..., description="Benchmark Buy & Hold return for comparison (%)")
    win_rate_percent: float = Field(..., description="Percentage of winning closed trades (%)")
    profit_factor: float = Field(..., description="Profit Factor (Gross profits / Gross losses)")
    total_trades: int = Field(..., description="Total round-trip trades executed")
    max_drawdown_percent: float = Field(..., description="Strategy maximum drawdown (%)")
    trades: list[BacktestTrade] = Field(default_factory=list, description="Sample of executed trades")
    equity_curve: list[EquityPoint] = Field(default_factory=list, description="Sampled historical equity curve")


class FactorExposureEntry(BaseModel):
    """Factor regression exposure coefficient."""

    model_config = ConfigDict(populate_by_name=True)

    factor: str = Field(..., description="Macro/Market Factor name (e.g. Market SPY, Tech QQQ, SmallCap IWM)")
    exposure_beta: float = Field(..., description="Factor Beta coefficient or Alpha")
    unit: str = Field("Beta", description="Unit type (Beta, %, R2)")


class FactorExposuresResult(BaseModel):
    """Multi-factor regression exposures analyzing systematic market drivers."""

    model_config = ConfigDict(populate_by_name=True)

    ticker: str = Field(..., description="Analyzed ticker or portfolio")
    period: str = Field("2y", description="Regression lookback period")
    exposures: list[FactorExposureEntry] = Field(default_factory=list, description="Estimated factor loadings")
