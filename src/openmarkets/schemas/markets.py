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

    language: str | None = Field(None, description="Language", alias="language")
    region: str | None = Field(None, description="Region", alias="region")
    quote_type: str | None = Field(None, description="Quote type", alias="quoteType")
    type_disp: str | None = Field(None, description="Type display", alias="typeDisp")
    quote_source_name: str | None = Field(None, description="Quote source name", alias="quoteSourceName")
    triggerable: bool | None = Field(None, description="Is triggerable", alias="triggerable")
    custom_price_alert_confidence: str | None = Field(
        None, description="Custom price alert confidence", alias="customPriceAlertConfidence"
    )
    contract_symbol: bool | None = Field(None, description="Is contract symbol", alias="contractSymbol")
    head_symbol_as_string: str | None = Field(None, description="Head symbol as string", alias="headSymbolAsString")
    short_name: str | None = Field(None, description="Short name", alias="shortName")
    regular_market_change: float | None = Field(None, description="Regular market change", alias="regularMarketChange")
    regular_market_change_percent: float | None = Field(
        None, description="Regular market change percent", alias="regularMarketChangePercent"
    )
    regular_market_time: int | None = Field(
        None, description="Regular market time (timestamp)", alias="regularMarketTime"
    )
    regular_market_price: float | None = Field(None, description="Regular market price", alias="regularMarketPrice")
    regular_market_previous_close: float | None = Field(
        None, description="Regular market previous close", alias="regularMarketPreviousClose"
    )
    exchange: str | None = Field(None, description="Exchange name", alias="exchange")
    market: str | None = Field(None, description="Market name", alias="market")
    full_exchange_name: str | None = Field(None, description="Full exchange name", alias="fullExchangeName")
    market_state: str | None = Field(None, description="Market state", alias="marketState")
    source_interval: int | None = Field(None, description="Source interval", alias="sourceInterval")
    exchange_data_delayed_by: int | None = Field(
        None, description="Exchange data delayed by (ms)", alias="exchangeDataDelayedBy"
    )
    exchange_timezone_name: str | None = Field(None, description="Exchange timezone name", alias="exchangeTimezoneName")
    exchange_timezone_short_name: str | None = Field(
        None, description="Exchange timezone short name", alias="exchangeTimezoneShortName"
    )
    gmt_offset_milliseconds: int | None = Field(None, description="GMT offset in ms", alias="gmtOffSetMilliseconds")
    esg_populated: bool | None = Field(None, description="ESG populated", alias="esgPopulated")
    tradeable: bool | None = Field(None, description="Is tradeable", alias="tradeable")
    crypto_tradeable: bool | None = Field(None, description="Is crypto tradeable", alias="cryptoTradeable")
    has_pre_post_market_data: bool | None = Field(
        None, description="Has pre/post market data", alias="hasPrePostMarketData"
    )
    first_trade_date_milliseconds: int | None = Field(
        None, description="First trade date (ms)", alias="firstTradeDateMilliseconds"
    )
    symbol: str | None = Field(None, description="Symbol", alias="symbol")


class MarketStatus(BaseModel):
    """Schema for market status information."""

    id: str | None = Field(None, description="Market ID", alias="id")
    name: str | None = Field(None, description="Market name", alias="name")
    status: str | None = Field(None, description="Market status", alias="status")
    yfit_market_id: str | None = Field(None, description="Yahoo Finance market ID", alias="yfit_market_id")
    close: datetime | None = Field(None, description="Market close time", alias="close")
    message: str | None = Field(None, description="Status message", alias="message")
    open: datetime | None = Field(None, description="Market open time", alias="open")
    yfit_market_status: str | None = Field(None, description="Yahoo Finance market status", alias="yfit_market_status")
    timezone: dict | None = Field(None, description="Timezone info", alias="timezone")
    # tz: Optional[Any] = Field(None, description="Timezone object", alias="tz")


class MarketSummary(BaseModel):
    """Schema for a summary of markets."""

    summary: dict[str, SummaryEntry] | None = Field(None, description="Dictionary of market summaries", alias="summary")
