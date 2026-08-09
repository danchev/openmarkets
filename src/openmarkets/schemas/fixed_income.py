"""Pydantic schemas for fixed income, bond yields, and yield curves."""

from pydantic import BaseModel, ConfigDict, Field


class TreasuryYieldPoint(BaseModel):
    """A single treasury yield observation."""

    model_config = ConfigDict(populate_by_name=True)

    maturity: str = Field(..., description="Maturity label (e.g. '1M', '3M', '6M', '1Y', '2Y', '5Y', '10Y', '30Y')")
    name: str = Field(..., description="Descriptive name")
    yield_percent: float = Field(..., description="Yield in percentage points (e.g. 4.35)")
    date: str = Field(..., description="Date of observation in YYYY-MM-DD format")
    timestamp: int = Field(..., description="Unix timestamp in milliseconds")


class TreasuryYieldCurve(BaseModel):
    """Complete snapshot of the US Treasury yield curve."""

    model_config = ConfigDict(populate_by_name=True)

    as_of_date: str = Field(..., description="Date of the yield curve snapshot")
    yields: list[TreasuryYieldPoint] = Field(default_factory=list, description="Yield curve points by maturity")
    spread_2y_10y_bps: float | None = Field(None, description="2Y/10Y spread in basis points ((10Y - 2Y) * 100)")
    spread_3m_10y_bps: float | None = Field(None, description="3M/10Y spread in basis points ((10Y - 3M) * 100)")
    is_inverted: bool = Field(False, description="Whether the 2Y/10Y yield curve is currently inverted")


class FixedIncomeHistory(BaseModel):
    """Historical timeseries of bond yields."""

    model_config = ConfigDict(populate_by_name=True)

    maturity: str = Field(..., description="Maturity label")
    name: str = Field(..., description="Descriptive name")
    data_points: list[TreasuryYieldPoint] = Field(default_factory=list, description="Historical yield observations")


class SovereignYieldQuote(BaseModel):
    """Benchmark sovereign 10-year yield quote for a country."""

    model_config = ConfigDict(populate_by_name=True)

    country: str = Field(..., description="Country name (e.g. 'United States', 'Germany', 'United Kingdom', 'Japan')")
    symbol: str = Field(..., description="Symbol alias (e.g. 'US10Y', 'DE10Y', 'UK10Y', 'JP10Y')")
    name: str = Field(..., description="Bond instrument name (e.g. 'Germany 10-Year Bund Yield')")
    yield_percent: float = Field(..., description="10-Year benchmark yield in percent")
    spread_vs_us10y_bps: float | None = Field(
        None, description="Spread against US 10-Year Treasury yield in basis points"
    )
    date: str = Field(..., description="Observation date in YYYY-MM-DD format")
    timestamp: int = Field(..., description="Unix timestamp in milliseconds")


class GlobalSovereignYields(BaseModel):
    """Comparison snapshot of major global 10-year sovereign bond benchmark yields."""

    model_config = ConfigDict(populate_by_name=True)

    as_of_date: str = Field(..., description="Snapshot date")
    sovereigns: list[SovereignYieldQuote] = Field(
        default_factory=list, description="Benchmark 10-year yields across major economies"
    )
