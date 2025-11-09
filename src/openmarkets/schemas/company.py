"""Pydantic schemas for stock information tools."""

from pydantic import BaseModel, Field


class CompanyOfficer(BaseModel):
    """Schema for a company officer in yfinance Ticker.info."""

    maxAge: int | None = Field(None, description="Maximum age of the officer.")
    name: str | None = Field(None, description="Name of the officer.")
    yearBorn: int | None = Field(None, description="Year the officer was born.")
    fiscalYear: int | None = Field(None, description="Fiscal year relevant to the officer's compensation.")
    totalPay: float | None = Field(None, description="Total pay of the officer.")
    exercisedValue: float | None = Field(None, description="Value of exercised options.")
    unexercisedValue: float | None = Field(None, description="Value of unexercised options.")
