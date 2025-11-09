from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class MarketType(str, Enum):
    """Enumeration for market types."""

    US = "US"
    GB = "GB"
    ASIA = "ASIA"
    EUROPE = "EUROPE"
    RATES = "RATES"
    COMMODITIES = "COMMODITIES"
    CURRENCIES = "CURRENCIES"
    CRYPTOCURRENCIES = "CRYPTOCURRENCIES"


class SummaryEntry(BaseModel):
    """Schema for exchange information."""

    language: str | None = Field(None, description="Language")
    region: str | None = Field(None, description="Region")
    quoteType: str | None = Field(None, description="Quote type")
    typeDisp: str | None = Field(None, description="Type display")
    quoteSourceName: str | None = Field(None, description="Quote source name")
    triggerable: bool | None = Field(None, description="Is triggerable")
    customPriceAlertConfidence: str | None = Field(None, description="Custom price alert confidence")
    contractSymbol: bool | None = Field(None, description="Is contract symbol")
    headSymbolAsString: str | None = Field(None, description="Head symbol as string")
    shortName: str | None = Field(None, description="Short name")
    regularMarketChange: float | None = Field(None, description="Regular market change")
    regularMarketChangePercent: float | None = Field(None, description="Regular market change percent")
    regularMarketTime: int | None = Field(None, description="Regular market time (timestamp)")
    regularMarketPrice: float | None = Field(None, description="Regular market price")
    regularMarketPreviousClose: float | None = Field(None, description="Regular market previous close")
    exchange: str | None = Field(None, description="Exchange name")
    market: str | None = Field(None, description="Market name")
    fullExchangeName: str | None = Field(None, description="Full exchange name")
    marketState: str | None = Field(None, description="Market state")
    sourceInterval: int | None = Field(None, description="Source interval")
    exchangeDataDelayedBy: int | None = Field(None, description="Exchange data delayed by (ms)")
    exchangeTimezoneName: str | None = Field(None, description="Exchange timezone name")
    exchangeTimezoneShortName: str | None = Field(None, description="Exchange timezone short name")
    gmtOffSetMilliseconds: int | None = Field(None, description="GMT offset in ms")
    esgPopulated: bool | None = Field(None, description="ESG populated")
    tradeable: bool | None = Field(None, description="Is tradeable")
    cryptoTradeable: bool | None = Field(None, description="Is crypto tradeable")
    hasPrePostMarketData: bool | None = Field(None, description="Has pre/post market data")
    firstTradeDateMilliseconds: int | None = Field(None, description="First trade date (ms)")
    symbol: str | None = Field(None, description="Symbol")


class MarketStatus(BaseModel):
    """Schema for market status information."""

    id: str | None = Field(None, description="Market ID")
    name: str | None = Field(None, description="Market name")
    status: str | None = Field(None, description="Market status")
    yfit_market_id: str | None = Field(None, description="Yahoo Finance market ID")
    close: datetime | None = Field(None, description="Market close time")
    message: str | None = Field(None, description="Status message")
    open: datetime | None = Field(None, description="Market open time")
    yfit_market_status: str | None = Field(None, description="Yahoo Finance market status")
    timezone: dict | None = Field(None, description="Timezone info")
    # tz: Optional[Any] = Field(None, description="Timezone object")


class MarketSummary(BaseModel):
    """Schema for a summary of markets."""

    summary: dict[str, SummaryEntry] | None = Field(None, description="Dictionary of market summaries")
