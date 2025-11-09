"""
Ticker Analysis Schemas:
    recommendations
    recommendations_summary
    upgrades_downgrades
    sustainability
    analyst_price_targets
    earnings_estimate
    revenue_estimate
    earnings_history
    eps_trend
    eps_revisions
    growth_estimates
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class AnalystRecommendation(BaseModel):
    """Analyst recommendation summary for a given period."""

    period: str = Field(..., description="Recommendation period.")
    strongBuy: int = Field(..., description="Number of strong buy recommendations.")
    buy: int = Field(..., description="Number of buy recommendations.")
    hold: int = Field(..., description="Number of hold recommendations.")
    sell: int = Field(..., description="Number of sell recommendations.")
    strongSell: int = Field(..., description="Number of strong sell recommendations.")


class AnalystRecommendationChange(BaseModel):
    """Schema for ticker upgrades and downgrades data."""

    Date: datetime | None = Field(None, alias="Date", description="Date of the upgrade/downgrade")
    Firm: str | None = Field(None, alias="Firm", description="Firm issuing the rating")
    To_Rating: str | None = Field(None, alias="To Rating", description="New rating assigned")
    From_Rating: str | None = Field(None, alias="From Rating", description="Previous rating")
    Action: str | None = Field(None, alias="Action", description="Action taken (upgrade/downgrade)")
    Notes: str | None = Field(None, alias="Notes", description="Additional notes")

    @field_validator("Date", mode="before")
    @classmethod
    def convert_date(cls, v):
        """Convert Date field from string to datetime, or pass through if already datetime/None."""
        if v is None or isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d")
        except Exception:
            return None


class RevenueEstimate(BaseModel):
    """Schema for ticker revenue estimates data."""

    period: str | None = Field(None, description="Estimate period.")
    avg: int | None = Field(None, description="Average revenue estimate.")
    low: int | None = Field(None, description="Low revenue estimate.")
    high: int | None = Field(None, description="High revenue estimate.")
    numberOfAnalysts: int | None = Field(None, description="Number of analysts providing estimates.")
    yearAgoRevenue: int | None = Field(None, description="Revenue from the same period last year.")
    growth: float | None = Field(None, description="Estimated growth percentage.")


class EarningsEstimate(BaseModel):
    """Schema for ticker revenue estimates data."""

    period: str | None = Field(None, description="Estimate period.")
    avg: float | None = Field(None, description="Average revenue estimate.")
    low: float | None = Field(None, description="Low revenue estimate.")
    high: float | None = Field(None, description="High revenue estimate.")
    numberOfAnalysts: int | None = Field(None, description="Number of analysts providing estimates.")
    yearAgoEps: float | None = Field(None, description="Revenue from the same period last year.")
    growth: float | None = Field(None, description="Estimated growth percentage.")


class GrowthEstimates(BaseModel):
    """Schema for ticker growth estimates data."""

    period: str | None = Field(None, description="Estimate period.")
    stockTrend: float | None = Field(None, description="Stock trend estimate.")
    indexTrend: float | None = Field(None, description="Index trend estimate.")


class EPSTrend(BaseModel):
    """Schema for ticker EPS trends data."""

    period: str | None = Field(None, description="Estimate period.")
    current: float | None = Field(None, description="Current EPS estimate.")
    days_7_ago: float | None = Field(None, alias="7daysAgo", description="EPS estimate 7 days ago.")
    days_30_ago: float | None = Field(None, alias="30daysAgo", description="EPS estimate 30 days ago.")
    days_60_ago: float | None = Field(None, alias="60daysAgo", description="EPS estimate 60 days ago.")
    days_90_ago: float | None = Field(None, alias="90daysAgo", description="EPS estimate 90 days ago.")


class AnalystPriceTargets(BaseModel):
    """Schema for analyst price targets and estimates."""

    current: float | None = Field(None, description="Current price.")
    high: float | None = Field(None, description="High target price.")
    low: float | None = Field(None, description="Low target price.")
    mean: float | None = Field(None, description="Mean target price.")
    median: float | None = Field(None, description="Median target price.")
