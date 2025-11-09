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

from pydantic import BaseModel, Field, field_validator


class InsiderPurchase(BaseModel):
    """Schema for insider purchase data."""

    Insider_Purchases_Last_6m: str | None = Field(
        None, alias="Insider Purchases Last 6m", description="Insider purchases in last 6 months"
    )
    Shares: float | None = Field(None, alias="Shares", description="Number of shares purchased")
    Trans: int | None = Field(None, alias="Trans", description="Number of transactions")


class InsiderRosterHolder(BaseModel):
    """Schema for insider roster holder data."""

    Name: str | None = Field(None, alias="Name", description="Holder's name")
    Position: str | None = Field(None, alias="Position", description="Position held")
    URL: str | None = Field(None, alias="URL", description="Profile URL")
    Most_Recent_Transaction: str | None = Field(
        None, alias="Most Recent Transaction", description="Most recent transaction type"
    )
    Latest_Transaction_Date: datetime | None = Field(
        None, alias="Latest Transaction Date", description="Date of latest transaction"
    )
    Shares_Owned_Directly: float | None = Field(
        None, alias="Shares Owned Directly", description="Shares owned directly"
    )
    Position_Direct_Date: datetime | None = Field(
        None, alias="Position Direct Date", description="Direct position date"
    )
    Shares_Owned_Indirectly: float | None = Field(
        None, alias="Shares Owned Indirectly", description="Shares owned indirectly"
    )
    Position_Indirect_Date: datetime | None = Field(
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

    @field_validator("Shares_Owned_Directly", "Shares_Owned_Indirectly")
    @classmethod
    def convert_shares(cls, v):
        """Convert shares fields to float, or pass through if None."""
        if v in ("nan", "NaN", "Inf", "-Inf"):
            return None
        try:
            return float(v)
        except Exception:
            return None


class StockInstitutionalHoldings(BaseModel):
    """Schema for institutional holdings data."""

    Holder: str | None = Field(None, alias="Holder", description="Name of the institutional holder")
    Shares: int | None = Field(None, alias="Shares", description="Number of shares held")
    Date_Report: datetime | None = Field(None, alias="Date Report", description="Date of the report")
    Value: int | None = Field(None, alias="Value", description="Value of the holdings")
    Percent_Out: float | None = Field(None, alias="Percent Out", description="Percentage of shares outstanding")

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

    Holder: str | None = Field(None, alias="Holder", description="Name of the mutual fund holder")
    Shares: int | None = Field(None, alias="Shares", description="Number of shares held")
    Date_Report: datetime | None = Field(None, alias="Date Report", description="Date of the report")
    Value: int | None = Field(None, alias="Value", description="Value of the holdings")
    Percent_Out: float | None = Field(None, alias="Percent Out", description="Percentage of shares outstanding")

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

    insidersPercentHeld: float | None = Field(None, description="Percentage of shares held by insiders")
    institutionsPercentHeld: float | None = Field(None, description="Percentage of shares held by institutions")
    institutionsFloatPercentHeld: float | None = Field(None, description="Percentage of float held by institutions")
    institutionsCount: int | None = Field(None, description="Number of institutional holders")
