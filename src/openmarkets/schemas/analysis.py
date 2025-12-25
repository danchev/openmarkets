from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class AnalystRecommendation(BaseModel):
    """Analyst recommendation summary for a given period."""

    period: str = Field(..., description="Recommendation period.", alias="period")
    strong_buy: int = Field(..., description="Number of strong buy recommendations.", alias="strongBuy")
    buy: int = Field(..., description="Number of buy recommendations.", alias="buy")
    hold: int = Field(..., description="Number of hold recommendations.", alias="hold")
    sell: int = Field(..., description="Number of sell recommendations.", alias="sell")
    strong_sell: int = Field(..., description="Number of strong sell recommendations.", alias="strongSell")


class AnalystRecommendationChange(BaseModel):
    """Schema for ticker upgrades and downgrades data."""

    date: datetime | None = Field(None, alias="Date", description="Date of the upgrade/downgrade")
    firm: str | None = Field(None, alias="Firm", description="Firm issuing the rating")
    to_rating: str | None = Field(None, alias="To Rating", description="New rating assigned")
    from_rating: str | None = Field(None, alias="From Rating", description="Previous rating")
    action: str | None = Field(None, alias="Action", description="Action taken (upgrade/downgrade)")
    notes: str | None = Field(None, alias="Notes", description="Additional notes")

    @field_validator("date", mode="before")
    @classmethod
    def convert_date(cls, v):
        """Convert date field from string to datetime, or pass through if already datetime/None."""
        if v is None or isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d")
        except Exception:
            return None


class RevenueEstimate(BaseModel):
    """Schema for ticker revenue estimates data."""

    period: str | None = Field(None, description="Estimate period.", alias="period")
    avg: int | None = Field(None, description="Average revenue estimate.", alias="avg")
    low: int | None = Field(None, description="Low revenue estimate.", alias="low")
    high: int | None = Field(None, description="High revenue estimate.", alias="high")
    number_of_analysts: int | None = Field(
        None, description="Number of analysts providing estimates.", alias="numberOfAnalysts"
    )
    year_ago_revenue: int | None = Field(
        None, description="Revenue from the same period last year.", alias="yearAgoRevenue"
    )
    growth: float | None = Field(None, description="Estimated growth percentage.", alias="growth")


class EarningsEstimate(BaseModel):
    """Schema for ticker revenue estimates data."""

    period: str | None = Field(None, description="Estimate period.", alias="period")
    avg: float | None = Field(None, description="Average revenue estimate.", alias="avg")
    low: float | None = Field(None, description="Low revenue estimate.", alias="low")
    high: float | None = Field(None, description="High revenue estimate.", alias="high")
    number_of_analysts: int | None = Field(
        None, description="Number of analysts providing estimates.", alias="numberOfAnalysts"
    )
    year_ago_eps: float | None = Field(None, description="Revenue from the same period last year.", alias="yearAgoEps")
    growth: float | None = Field(None, description="Estimated growth percentage.", alias="growth")


class GrowthEstimates(BaseModel):
    """Schema for ticker growth estimates data."""

    period: str | None = Field(None, description="Estimate period.", alias="period")
    stock_trend: float | None = Field(None, description="Stock trend estimate.", alias="stockTrend")
    index_trend: float | None = Field(None, description="Index trend estimate.", alias="indexTrend")


class EPSTrend(BaseModel):
    """Schema for ticker EPS trends data."""

    period: str | None = Field(None, description="Estimate period.", alias="period")
    current: float | None = Field(None, description="Current EPS estimate.", alias="current")
    days_7_ago: float | None = Field(None, alias="7daysAgo", description="EPS estimate 7 days ago.")
    days_30_ago: float | None = Field(None, alias="30daysAgo", description="EPS estimate 30 days ago.")
    days_60_ago: float | None = Field(None, alias="60daysAgo", description="EPS estimate 60 days ago.")
    days_90_ago: float | None = Field(None, alias="90daysAgo", description="EPS estimate 90 days ago.")


class AnalystPriceTargets(BaseModel):
    """Schema for analyst price targets and estimates."""

    current: float | None = Field(None, description="Current price.", alias="current")
    high: float | None = Field(None, description="High target price.", alias="high")
    low: float | None = Field(None, description="Low target price.", alias="low")
    mean: float | None = Field(None, description="Mean target price.", alias="mean")
    median: float | None = Field(None, description="Median target price.", alias="median")
