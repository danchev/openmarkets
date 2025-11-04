from datetime import datetime
from enum import Enum
from typing import Optional

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

    language: Optional[str] = Field(None, description="Language")
    region: Optional[str] = Field(None, description="Region")
    quoteType: Optional[str] = Field(None, description="Quote type")
    typeDisp: Optional[str] = Field(None, description="Type display")
    quoteSourceName: Optional[str] = Field(None, description="Quote source name")
    triggerable: Optional[bool] = Field(None, description="Is triggerable")
    customPriceAlertConfidence: Optional[str] = Field(None, description="Custom price alert confidence")
    contractSymbol: Optional[bool] = Field(None, description="Is contract symbol")
    headSymbolAsString: Optional[str] = Field(None, description="Head symbol as string")
    shortName: Optional[str] = Field(None, description="Short name")
    regularMarketChange: Optional[float] = Field(None, description="Regular market change")
    regularMarketChangePercent: Optional[float] = Field(None, description="Regular market change percent")
    regularMarketTime: Optional[int] = Field(None, description="Regular market time (timestamp)")
    regularMarketPrice: Optional[float] = Field(None, description="Regular market price")
    regularMarketPreviousClose: Optional[float] = Field(None, description="Regular market previous close")
    exchange: Optional[str] = Field(None, description="Exchange name")
    market: Optional[str] = Field(None, description="Market name")
    fullExchangeName: Optional[str] = Field(None, description="Full exchange name")
    marketState: Optional[str] = Field(None, description="Market state")
    sourceInterval: Optional[int] = Field(None, description="Source interval")
    exchangeDataDelayedBy: Optional[int] = Field(None, description="Exchange data delayed by (ms)")
    exchangeTimezoneName: Optional[str] = Field(None, description="Exchange timezone name")
    exchangeTimezoneShortName: Optional[str] = Field(None, description="Exchange timezone short name")
    gmtOffSetMilliseconds: Optional[int] = Field(None, description="GMT offset in ms")
    esgPopulated: Optional[bool] = Field(None, description="ESG populated")
    tradeable: Optional[bool] = Field(None, description="Is tradeable")
    cryptoTradeable: Optional[bool] = Field(None, description="Is crypto tradeable")
    hasPrePostMarketData: Optional[bool] = Field(None, description="Has pre/post market data")
    firstTradeDateMilliseconds: Optional[int] = Field(None, description="First trade date (ms)")
    symbol: Optional[str] = Field(None, description="Symbol")


class MarketStatus(BaseModel):
    """Schema for market status information."""

    id: Optional[str] = Field(None, description="Market ID")
    name: Optional[str] = Field(None, description="Market name")
    status: Optional[str] = Field(None, description="Market status")
    yfit_market_id: Optional[str] = Field(None, description="Yahoo Finance market ID")
    close: Optional[datetime] = Field(None, description="Market close time")
    message: Optional[str] = Field(None, description="Status message")
    open: Optional[datetime] = Field(None, description="Market open time")
    yfit_market_status: Optional[str] = Field(None, description="Yahoo Finance market status")
    timezone: Optional[dict] = Field(None, description="Timezone info")
    # tz: Optional[Any] = Field(None, description="Timezone object")


class MarketSummary(BaseModel):
    """Schema for a summary of markets."""

    summary: Optional[dict[str, SummaryEntry]] = Field(None, description="Dictionary of market summaries")
