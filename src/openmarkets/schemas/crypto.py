from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CryptoFastInfo(BaseModel):
    """Fast info snapshot for a crypto ticker, typically from yfinance or similar APIs."""

    model_config = ConfigDict(validate_by_name=True)

    currency: str | None = Field(None, description="Currency of the ticker.")
    day_high: float | None = Field(None, alias="dayHigh", description="Day's high price.")
    day_low: float | None = Field(None, alias="dayLow", description="Day's low price.")
    exchange: str | None = Field(None, description="Exchange where the ticker is listed.")
    fifty_day_average: float | None = Field(None, alias="fiftyDayAverage", description="50-day average price.")
    last_price: float | None = Field(None, alias="lastPrice", description="Last traded price.")
    last_volume: int | None = Field(None, alias="lastVolume", description="Last traded volume.")
    open: float | None = Field(None, description="Opening price.")
    previous_close: float | None = Field(None, alias="previousClose", description="Previous closing price.")
    quote_type: str | None = Field(None, alias="quoteType", description="Type of quote (e.g., CRYPTOCURRENCY).")
    regular_market_previous_close: float | None = Field(
        None, alias="regularMarketPreviousClose", description="Regular market previous close."
    )
    ten_day_average_volume: int | None = Field(None, alias="tenDayAverageVolume", description="10-day average volume.")
    three_month_average_volume: int | None = Field(
        None, alias="threeMonthAverageVolume", description="3-month average volume."
    )
    timezone: str | None = Field(None, description="Timezone of the exchange.")
    two_hundred_day_average: float | None = Field(
        None, alias="twoHundredDayAverage", description="200-day average price."
    )
    year_change: float | None = Field(None, alias="yearChange", description="Change over the past year.")
    year_high: float | None = Field(None, alias="yearHigh", description="52-week high price.")
    year_low: float | None = Field(None, alias="yearLow", description="52-week low price.")


class CryptoHistory(BaseModel):
    """Schema for historical crypto data (OHLCV)."""

    model_config = ConfigDict(validate_by_name=True)

    date: datetime = Field(..., alias="Date", description="Date of record")
    open: float = Field(..., alias="Open", description="Opening price")
    high: float = Field(..., alias="High", description="Highest price")
    low: float = Field(..., alias="Low", description="Lowest price")
    close: float = Field(..., alias="Close", description="Closing price")
    volume: int = Field(..., alias="Volume", description="Volume traded")


class CryptoSentimentEntry(BaseModel):
    """Per-asset price movement used to derive the sentiment proxy."""

    symbol: str = Field(..., description="Cryptocurrency symbol.")
    daily_change_percent: float | None = Field(..., description="Daily percentage change, None if not computable.")
    weekly_change_percent: float | None = Field(..., description="Weekly percentage change, None if not computable.")


class CryptoSentiment(BaseModel):
    """Sentiment proxy derived from recent crypto price movements."""

    sentiment_proxy: str = Field(
        ...,
        description="Sentiment label: Extreme Greed, Greed, Neutral-Positive, "
        "Neutral-Negative, Fear, Extreme Fear, or Unknown when no data is usable.",
    )
    average_weekly_change: float | None = Field(
        ..., description="Mean weekly percentage change, None when no asset had a usable value."
    )
    crypto_data: list[CryptoSentimentEntry] = Field(..., description="Per-asset supporting data.")
    note: str = Field(..., description="Caveat describing how the proxy is derived.")
