"""Pydantic schemas for macroeconomic data and Federal Reserve economic telemetry."""

from pydantic import BaseModel, ConfigDict, Field


class MacroeconomicPoint(BaseModel):
    """A single macroeconomic observation point in time."""

    model_config = ConfigDict(populate_by_name=True)

    date: str = Field(..., description="Observation date in YYYY-MM-DD format")
    value: float = Field(..., description="Numerical observation value")


class MacroeconomicSeries(BaseModel):
    """A complete macroeconomic time series from FRED."""

    model_config = ConfigDict(populate_by_name=True)

    series_id: str = Field(..., description="FRED series identifier (e.g. 'CPIAUCSL')")
    title: str = Field(..., description="Descriptive title of the economic series")
    units: str = Field(..., description="Unit of measurement (e.g. 'Index', 'Percent', 'Billions of Dollars')")
    frequency: str = Field(..., description="Sampling frequency (e.g. 'Monthly', 'Quarterly', 'Daily')")
    latest_date: str = Field(..., description="Date of the most recent data release (YYYY-MM-DD)")
    latest_value: float = Field(..., description="Most recent observation value")
    data_points: list[MacroeconomicPoint] = Field(default_factory=list, description="Historical observations")


class InflationSummary(BaseModel):
    """Consumer Price Index (CPI) and Core CPI inflation summary."""

    model_config = ConfigDict(populate_by_name=True)

    headline_cpi_latest: float = Field(..., description="Latest Headline CPI index level")
    headline_cpi_date: str = Field(..., description="Latest Headline CPI release date")
    core_cpi_latest: float = Field(..., description="Latest Core CPI index level (less food & energy)")
    core_cpi_date: str = Field(..., description="Latest Core CPI release date")
    cpi_yoy_percent: float | None = Field(None, description="Headline CPI year-over-year percentage change (%)")
    core_cpi_yoy_percent: float | None = Field(None, description="Core CPI year-over-year percentage change (%)")
    headline_cpi_history: list[MacroeconomicPoint] = Field(
        default_factory=list, description="Recent Headline CPI observations"
    )
    core_cpi_history: list[MacroeconomicPoint] = Field(default_factory=list, description="Recent Core CPI observations")


class PCESummary(BaseModel):
    """Core Personal Consumption Expenditures (PCE) inflation summary (Fed's primary target)."""

    model_config = ConfigDict(populate_by_name=True)

    core_pce_latest: float = Field(..., description="Latest Core PCE Price Index level (2017=100)")
    core_pce_date: str = Field(..., description="Latest Core PCE release date")
    core_pce_yoy_percent: float | None = Field(None, description="Core PCE year-over-year percentage change (%)")
    fed_target_percent: float = Field(2.0, description="Federal Reserve official long-run inflation target (%)")
    history: list[MacroeconomicPoint] = Field(default_factory=list, description="Recent Core PCE observations")


class EmploymentSummary(BaseModel):
    """US labor market summary including Unemployment Rate and Nonfarm Payrolls."""

    model_config = ConfigDict(populate_by_name=True)

    unemployment_rate_percent: float = Field(..., description="Civilian unemployment rate (%)")
    unemployment_date: str = Field(..., description="Latest unemployment release date")
    nonfarm_payrolls_thousands: float = Field(..., description="Total nonfarm employees (in thousands)")
    nonfarm_payrolls_date: str = Field(..., description="Latest nonfarm payrolls release date")
    monthly_job_growth_thousands: float | None = Field(
        None, description="Month-over-month net nonfarm job creation in thousands"
    )
    unemployment_history: list[MacroeconomicPoint] = Field(
        default_factory=list, description="Recent unemployment rate observations"
    )
    payrolls_history: list[MacroeconomicPoint] = Field(
        default_factory=list, description="Recent nonfarm payrolls observations"
    )


class InterestRatesSummary(BaseModel):
    """Benchmark monetary policy and money market interest rates."""

    model_config = ConfigDict(populate_by_name=True)

    effective_fed_funds_rate: float = Field(..., description="Effective Federal Funds Rate (EFFR %)")
    fed_funds_date: str = Field(..., description="Date of EFFR observation")
    sofr_rate: float = Field(..., description="Secured Overnight Financing Rate (SOFR %)")
    sofr_date: str = Field(..., description="Date of SOFR observation")
    fed_funds_history: list[MacroeconomicPoint] = Field(
        default_factory=list, description="Recent Federal Funds Rate observations"
    )
    sofr_history: list[MacroeconomicPoint] = Field(default_factory=list, description="Recent SOFR observations")


class GDPSummary(BaseModel):
    """Gross Domestic Product (GDP) growth and economic output summary."""

    model_config = ConfigDict(populate_by_name=True)

    real_gdp_billions: float = Field(..., description="Real GDP in billions of chained 2017 dollars")
    real_gdp_date: str = Field(..., description="Latest Real GDP observation quarter")
    nominal_gdp_billions: float = Field(..., description="Nominal GDP in billions of current dollars")
    nominal_gdp_date: str = Field(..., description="Latest Nominal GDP observation quarter")
    real_gdp_annualized_growth_percent: float | None = Field(
        None, description="Quarter-over-quarter annualized real growth rate (%)"
    )
    real_gdp_history: list[MacroeconomicPoint] = Field(
        default_factory=list, description="Recent quarterly Real GDP observations"
    )
    nominal_gdp_history: list[MacroeconomicPoint] = Field(
        default_factory=list, description="Recent quarterly Nominal GDP observations"
    )


class LiquiditySummary(BaseModel):
    """Monetary liquidity, M2 Money Supply, and Federal Reserve balance sheet telemetry."""

    model_config = ConfigDict(populate_by_name=True)

    m2_money_supply_billions: float = Field(..., description="M2 Money Supply in billions of dollars")
    m2_date: str = Field(..., description="Date of latest M2 release")
    m2_yoy_growth_percent: float | None = Field(None, description="M2 year-over-year percentage growth (%)")
    fed_total_assets_millions: float = Field(
        ..., description="Federal Reserve Balance Sheet (Total Assets in millions of dollars)"
    )
    fed_assets_date: str = Field(..., description="Date of latest Federal Reserve balance sheet release")
    m2_history: list[MacroeconomicPoint] = Field(default_factory=list, description="Recent M2 observations")
    fed_assets_history: list[MacroeconomicPoint] = Field(
        default_factory=list, description="Recent Federal Reserve balance sheet observations"
    )


class InflationExpectationsSummary(BaseModel):
    """Market-implied inflation expectations from Treasury Inflation-Protected Securities (TIPS)."""

    model_config = ConfigDict(populate_by_name=True)

    breakeven_5y_percent: float = Field(..., description="5-Year Breakeven Inflation Rate (%)")
    breakeven_5y_date: str = Field(..., description="Date of 5-Year Breakeven observation")
    breakeven_10y_percent: float = Field(..., description="10-Year Breakeven Inflation Rate (%)")
    breakeven_10y_date: str = Field(..., description="Date of 10-Year Breakeven observation")
    history_5y: list[MacroeconomicPoint] = Field(default_factory=list, description="Recent 5-Year Breakeven history")
    history_10y: list[MacroeconomicPoint] = Field(default_factory=list, description="Recent 10-Year Breakeven history")


class FinancialStressSummary(BaseModel):
    """Financial market stress and high-yield credit risk telemetry."""

    model_config = ConfigDict(populate_by_name=True)

    financial_stress_index: float = Field(
        ...,
        description="St. Louis Fed Financial Stress Index (0 = normal market conditions, >0 = above-average stress)",
    )
    stress_index_date: str = Field(..., description="Date of latest stress index release")
    stress_level_interpretation: str = Field(
        ..., description="Human-readable interpretation of financial market stress conditions"
    )
    high_yield_oas_percent: float = Field(
        ..., description="ICE BofA US High Yield Index Option-Adjusted Spread (credit spread over Treasuries in %)"
    )
    high_yield_oas_date: str = Field(..., description="Date of High Yield OAS observation")
    stress_history: list[MacroeconomicPoint] = Field(
        default_factory=list, description="Recent Financial Stress Index observations"
    )
    oas_history: list[MacroeconomicPoint] = Field(
        default_factory=list, description="Recent High Yield OAS credit spread observations"
    )
