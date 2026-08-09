"""Pydantic schemas for Foreign Exchange (Forex) and Currency pairs."""

from pydantic import BaseModel, Field


class ForexHistoryPoint(BaseModel):
    """A single historical bar for a currency pair."""

    timestamp: int = Field(description="Epoch timestamp in milliseconds")
    date: str = Field(description="Date in YYYY-MM-DD or ISO datetime format")
    open: float | None = Field(default=None, description="Open exchange rate")
    high: float | None = Field(default=None, description="High exchange rate")
    low: float | None = Field(default=None, description="Low exchange rate")
    close: float = Field(description="Close / settlement exchange rate")


class ForexQuote(BaseModel):
    """Real-time or latest exchange rate quote for a currency pair."""

    pair: str = Field(description="Currency pair symbol (e.g. 'EURUSD', 'USDJPY', 'DXY')")
    name: str = Field(description="Descriptive name (e.g. 'EUR/USD')")
    rate: float = Field(description="Latest exchange rate")
    date: str = Field(description="Quote date in YYYY-MM-DD format")
    timestamp: int = Field(description="Epoch timestamp in milliseconds")
    base_currency: str = Field(description="Base currency (e.g. 'EUR')")
    quote_currency: str = Field(description="Quote currency (e.g. 'USD')")


class ForexHistory(BaseModel):
    """Historical timeseries for a currency pair."""

    pair: str = Field(description="Currency pair symbol")
    name: str = Field(description="Descriptive name")
    data_points: list[ForexHistoryPoint] = Field(default_factory=list, description="Ordered historical bars")
