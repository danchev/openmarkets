"""
Ticker Holdings Schemas:
    insider_purchases
    insider_transactions
    insider_roster_holders
    major_holders
    institutional_holders
    mutualfund_holders
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class InsiderPurchase(BaseModel):
    """Schema for insider purchase data."""

    Insider_Purchases_Last_6m: Optional[str] = Field(
        None, alias="Insider Purchases Last 6m", description="Insider purchases in last 6 months"
    )
    Shares: Optional[float] = Field(None, alias="Shares", description="Number of shares purchased")
    Trans: Optional[int] = Field(None, alias="Trans", description="Number of transactions")


class InsiderRosterHolder(BaseModel):
    """Schema for insider roster holder data."""

    Name: Optional[str] = Field(None, alias="Name", description="Holder's name")
    Position: Optional[str] = Field(None, alias="Position", description="Position held")
    URL: Optional[str] = Field(None, alias="URL", description="Profile URL")
    Most_Recent_Transaction: Optional[str] = Field(
        None, alias="Most Recent Transaction", description="Most recent transaction type"
    )
    Latest_Transaction_Date: Optional[datetime] = Field(
        None, alias="Latest Transaction Date", description="Date of latest transaction"
    )
    Shares_Owned_Directly: Optional[float] = Field(
        None, alias="Shares Owned Directly", description="Shares owned directly"
    )
    Position_Direct_Date: Optional[datetime] = Field(
        None, alias="Position Direct Date", description="Direct position date"
    )
    Shares_Owned_Indirectly: Optional[float] = Field(
        None, alias="Shares Owned Indirectly", description="Shares owned indirectly"
    )
    Position_Indirect_Date: Optional[datetime] = Field(
        None, alias="Position Indirect Date", description="Indirect position date"
    )

    @field_validator("Latest_Transaction_Date", "Position_Direct_Date", "Position_Indirect_Date", mode="before")
    @classmethod
    def convert_dates(cls, v):
        """Convert date fields from string to datetime, or pass through if already datetime/None."""
        if v is None or isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d")
        except Exception:
            return None


class StockInstitutionalHoldings(BaseModel):
    """Schema for institutional holdings data."""

    Holder: Optional[str] = Field(None, alias="Holder", description="Name of the institutional holder")
    Shares: Optional[int] = Field(None, alias="Shares", description="Number of shares held")
    Date_Report: Optional[datetime] = Field(None, alias="Date Report", description="Date of the report")
    Value: Optional[int] = Field(None, alias="Value", description="Value of the holdings")
    Percent_Out: Optional[float] = Field(None, alias="Percent Out", description="Percentage of shares outstanding")

    @field_validator("Date_Report", mode="before")
    @classmethod
    def convert_date(cls, v):
        """Convert Date_Report field from string to datetime, or pass through if already datetime/None."""
        if v is None or isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d")
        except Exception:
            return None


class StockMutualFundHoldings(BaseModel):
    """Schema for mutual fund holdings data."""

    Holder: Optional[str] = Field(None, alias="Holder", description="Name of the mutual fund holder")
    Shares: Optional[int] = Field(None, alias="Shares", description="Number of shares held")
    Date_Report: Optional[datetime] = Field(None, alias="Date Report", description="Date of the report")
    Value: Optional[int] = Field(None, alias="Value", description="Value of the holdings")
    Percent_Out: Optional[float] = Field(None, alias="Percent Out", description="Percentage of shares outstanding")

    @field_validator("Date_Report", mode="before")
    @classmethod
    def convert_date(cls, v):
        """Convert Date_Report field from string to datetime, or pass through if already datetime/None."""
        if v is None or isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d")
        except Exception:
            return None


class StockMajorHolders(BaseModel):
    """Schema for major holders data."""

    insidersPercentHeld: Optional[float] = Field(None, description="Percentage of shares held by insiders")
    institutionsPercentHeld: Optional[float] = Field(None, description="Percentage of shares held by institutions")
    institutionsFloatPercentHeld: Optional[float] = Field(None, description="Percentage of float held by institutions")
    institutionsCount: Optional[int] = Field(None, description="Number of institutional holders")
