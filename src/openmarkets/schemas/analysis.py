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
from typing import Optional

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

    Date: Optional[datetime] = Field(None, alias="Date", description="Date of the upgrade/downgrade")
    Firm: Optional[str] = Field(None, alias="Firm", description="Firm issuing the rating")
    To_Rating: Optional[str] = Field(None, alias="To Rating", description="New rating assigned")
    From_Rating: Optional[str] = Field(None, alias="From Rating", description="Previous rating")
    Action: Optional[str] = Field(None, alias="Action", description="Action taken (upgrade/downgrade)")
    Notes: Optional[str] = Field(None, alias="Notes", description="Additional notes")

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

    period: Optional[str] = Field(None, description="Estimate period.")
    avg: Optional[int] = Field(None, description="Average revenue estimate.")
    low: Optional[int] = Field(None, description="Low revenue estimate.")
    high: Optional[int] = Field(None, description="High revenue estimate.")
    numberOfAnalysts: Optional[int] = Field(None, description="Number of analysts providing estimates.")
    yearAgoRevenue: Optional[int] = Field(None, description="Revenue from the same period last year.")
    growth: Optional[float] = Field(None, description="Estimated growth percentage.")


class EarningsEstimate(BaseModel):
    """Schema for ticker revenue estimates data."""

    period: Optional[str] = Field(None, description="Estimate period.")
    avg: Optional[float] = Field(None, description="Average revenue estimate.")
    low: Optional[float] = Field(None, description="Low revenue estimate.")
    high: Optional[float] = Field(None, description="High revenue estimate.")
    numberOfAnalysts: Optional[int] = Field(None, description="Number of analysts providing estimates.")
    yearAgoEps: Optional[float] = Field(None, description="Revenue from the same period last year.")
    growth: Optional[float] = Field(None, description="Estimated growth percentage.")


class GrowthEstimates(BaseModel):
    """Schema for ticker growth estimates data."""

    period: Optional[str] = Field(None, description="Estimate period.")
    stockTrend: Optional[float] = Field(None, description="Stock trend estimate.")
    indexTrend: Optional[float] = Field(None, description="Index trend estimate.")


class EPSTrend(BaseModel):
    """Schema for ticker EPS trends data."""

    period: Optional[str] = Field(None, description="Estimate period.")
    current: Optional[float] = Field(None, description="Current EPS estimate.")
    days_7_ago: Optional[float] = Field(None, alias="7daysAgo", description="EPS estimate 7 days ago.")
    days_30_ago: Optional[float] = Field(None, alias="30daysAgo", description="EPS estimate 30 days ago.")
    days_60_ago: Optional[float] = Field(None, alias="60daysAgo", description="EPS estimate 60 days ago.")
    days_90_ago: Optional[float] = Field(None, alias="90daysAgo", description="EPS estimate 90 days ago.")


class AnalystPriceTargets(BaseModel):
    """Schema for analyst price targets and estimates."""

    current: Optional[float] = Field(None, description="Current price.")
    high: Optional[float] = Field(None, description="High target price.")
    low: Optional[float] = Field(None, description="Low target price.")
    mean: Optional[float] = Field(None, description="Mean target price.")
    median: Optional[float] = Field(None, description="Median target price.")
