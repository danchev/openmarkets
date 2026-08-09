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
