from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class InsiderPurchase(BaseModel):
    """Schema for insider purchase data."""

    insider_purchases_last_6m: str | None = Field(
        None, alias="Insider Purchases Last 6m", description="Insider purchases in last 6 months"
    )
    shares: float | None = Field(None, alias="Shares", description="Number of shares purchased")
    trans: int | None = Field(None, alias="Trans", description="Number of transactions")


class InsiderRosterHolder(BaseModel):
    """Schema for insider roster holder data."""

    name: str | None = Field(None, alias="Name", description="Holder's name")
    position: str | None = Field(None, alias="Position", description="Position held")
    url: str | None = Field(None, alias="URL", description="Profile URL")
    most_recent_transaction: str | None = Field(
        None, alias="Most Recent Transaction", description="Most recent transaction type"
    )
    latest_transaction_date: datetime | None = Field(
        None, alias="Latest Transaction Date", description="Date of latest transaction"
    )
    shares_owned_directly: float | None = Field(
        None, alias="Shares Owned Directly", description="Shares owned directly"
    )
    position_direct_date: datetime | None = Field(
        None, alias="Position Direct Date", description="Direct position date"
    )
    shares_owned_indirectly: float | None = Field(
        None, alias="Shares Owned Indirectly", description="Shares owned indirectly"
    )
    position_indirect_date: datetime | None = Field(
        None, alias="Position Indirect Date", description="Indirect position date"
    )

    @field_validator("latest_transaction_date", "position_direct_date", "position_indirect_date", mode="before")
    @classmethod
    def convert_dates(cls, v):
        """Convert date fields from string to datetime, or pass through if already datetime/None."""
        if v is None or isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d")
        except Exception:
            return None

    @field_validator("shares_owned_directly", "shares_owned_indirectly", mode="before")
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

    holder: str | None = Field(None, alias="Holder", description="Name of the institutional holder")
    shares: int | None = Field(None, alias="Shares", description="Number of shares held")
    date_report: datetime | None = Field(None, alias="Date Report", description="Date of the report")
    value: int | None = Field(None, alias="Value", description="Value of the holdings")
    percent_out: float | None = Field(None, alias="Percent Out", description="Percentage of shares outstanding")

    @field_validator("date_report", mode="before")
    @classmethod
    def convert_date(cls, v):
        """Convert date_report field from string to datetime, or pass through if already datetime/None."""
        if v is None or isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d")
        except Exception:
            return None


class StockMutualFundHoldings(BaseModel):
    """Schema for mutual fund holdings data."""

    holder: str | None = Field(None, alias="Holder", description="Name of the mutual fund holder")
    shares: int | None = Field(None, alias="Shares", description="Number of shares held")
    date_report: datetime | None = Field(None, alias="Date Report", description="Date of the report")
    value: int | None = Field(None, alias="Value", description="Value of the holdings")
    percent_out: float | None = Field(None, alias="Percent Out", description="Percentage of shares outstanding")

    @field_validator("date_report", mode="before")
    @classmethod
    def convert_date(cls, v):
        """Convert date_report field from string to datetime, or pass through if already datetime/None."""
        if v is None or isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d")
        except Exception:
            return None


class StockMajorHolders(BaseModel):
    """Schema for major holders data."""

    insiders_percent_held: float | None = Field(
        None, description="Percentage of shares held by insiders", alias="insidersPercentHeld"
    )
    institutions_percent_held: float | None = Field(
        None, description="Percentage of shares held by institutions", alias="institutionsPercentHeld"
    )
    institutions_float_percent_held: float | None = Field(
        None, description="Percentage of float held by institutions", alias="institutionsFloatPercentHeld"
    )
    institutions_count: int | None = Field(
        None, description="Number of institutional holders", alias="institutionsCount"
    )
