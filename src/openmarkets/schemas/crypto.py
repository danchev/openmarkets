from datetime import datetime

from pydantic import BaseModel, Field


class CryptoFastInfo(BaseModel):
    """Fast info snapshot for a stock ticker, typically from yfinance or similar APIs."""

    currency: str = Field(..., description="Currency of the ticker.")
    dayHigh: float = Field(..., description="Day's high price.")
    dayLow: float = Field(..., description="Day's low price.")
    exchange: str = Field(..., description="Exchange where the ticker is listed.")
    fiftyDayAverage: float = Field(..., description="50-day average price.")
    lastPrice: float = Field(..., description="Last traded price.")
    lastVolume: int = Field(..., description="Last traded volume.")
    open: float = Field(..., description="Opening price.")
    previousClose: float = Field(..., description="Previous closing price.")
    quoteType: str = Field(..., description="Type of quote (e.g., CRYPTOCURRENCY).")
    regularMarketPreviousClose: float = Field(..., description="Regular market previous close.")
    tenDayAverageVolume: int = Field(..., description="10-day average volume.")
    threeMonthAverageVolume: int = Field(..., description="3-month average volume.")
    timezone: str = Field(..., description="Timezone of the exchange.")
    twoHundredDayAverage: float = Field(..., description="200-day average price.")
    yearChange: float = Field(..., description="Change over the past year.")
    yearHigh: float = Field(..., description="52-week high price.")
    yearLow: float = Field(..., description="52-week low price.")


class CryptoHistory(BaseModel):
    """Schema for historical crypto data (OHLCV)."""

    Date: datetime = Field(..., description="Date of record")
    Open: float = Field(..., description="Opening price")
    High: float = Field(..., description="Highest price")
    Low: float = Field(..., description="Lowest price")
    Close: float = Field(..., description="Closing price")
    Volume: int = Field(..., description="Volume traded")
