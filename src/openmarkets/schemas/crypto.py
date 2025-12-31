from datetime import datetime

from pydantic import BaseModel, Field


class CryptoFastInfo(BaseModel):
    """Fast info snapshot for a crypto ticker, typically from yfinance or similar APIs."""

    currency: str = Field(..., description="Currency of the ticker.")
    day_high: float = Field(..., alias="dayHigh", description="Day's high price.")
    day_low: float = Field(..., alias="dayLow", description="Day's low price.")
    exchange: str = Field(..., description="Exchange where the ticker is listed.")
    fifty_day_average: float = Field(..., alias="fiftyDayAverage", description="50-day average price.")
    last_price: float = Field(..., alias="lastPrice", description="Last traded price.")
    last_volume: int = Field(..., alias="lastVolume", description="Last traded volume.")
    open: float = Field(..., description="Opening price.")
    previous_close: float = Field(..., alias="previousClose", description="Previous closing price.")
    quote_type: str = Field(..., alias="quoteType", description="Type of quote (e.g., CRYPTOCURRENCY).")
    regular_market_previous_close: float = Field(
        ..., alias="regularMarketPreviousClose", description="Regular market previous close."
    )
    ten_day_average_volume: int = Field(..., alias="tenDayAverageVolume", description="10-day average volume.")
    three_month_average_volume: int = Field(..., alias="threeMonthAverageVolume", description="3-month average volume.")
    timezone: str = Field(..., description="Timezone of the exchange.")
    two_hundred_day_average: float = Field(..., alias="twoHundredDayAverage", description="200-day average price.")
    year_change: float = Field(..., alias="yearChange", description="Change over the past year.")
    year_high: float = Field(..., alias="yearHigh", description="52-week high price.")
    year_low: float = Field(..., alias="yearLow", description="52-week low price.")

    class Config:
        validate_by_name = True


class CryptoHistory(BaseModel):
    """Schema for historical crypto data (OHLCV)."""

    date: datetime = Field(..., alias="Date", description="Date of record")
    open: float = Field(..., alias="Open", description="Opening price")
    high: float = Field(..., alias="High", description="Highest price")
    low: float = Field(..., alias="Low", description="Lowest price")
    close: float = Field(..., alias="Close", description="Closing price")
    volume: int = Field(..., alias="Volume", description="Volume traded")

    class Config:
        validate_by_name = True
