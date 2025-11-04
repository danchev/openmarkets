"""Pydantic schemas for stock information tools."""

from typing import Optional

from pydantic import BaseModel, Field


class CompanyOfficer(BaseModel):
    """Schema for a company officer in yfinance Ticker.info."""

    maxAge: Optional[int] = Field(None, description="Maximum age of the officer.")
    name: Optional[str] = Field(None, description="Name of the officer.")
    yearBorn: Optional[int] = Field(None, description="Year the officer was born.")
    fiscalYear: Optional[int] = Field(None, description="Fiscal year relevant to the officer's compensation.")
    totalPay: Optional[float] = Field(None, description="Total pay of the officer.")
    exercisedValue: Optional[float] = Field(None, description="Value of exercised options.")
    unexercisedValue: Optional[float] = Field(None, description="Value of unexercised options.")
