from pydantic import BaseModel, Field


class CompanyOfficer(BaseModel):
    """Schema for a company officer in yfinance Ticker.info."""

    max_age: int | None = Field(None, alias="maxAge", description="Maximum age of the officer.")
    name: str | None = Field(None, description="Name of the officer.")
    year_born: int | None = Field(None, alias="yearBorn", description="Year the officer was born.")
    fiscal_year: int | None = Field(
        None, alias="fiscalYear", description="Fiscal year relevant to the officer's compensation."
    )
    total_pay: float | None = Field(None, alias="totalPay", description="Total pay of the officer.")
    exercised_value: float | None = Field(None, alias="exercisedValue", description="Value of exercised options.")
    unexercised_value: float | None = Field(None, alias="unexercisedValue", description="Value of unexercised options.")
