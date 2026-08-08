"""Schemas for the yfinance screener API (added in yfinance 1.3.0).

The screener returns quote objects with 80+ fields that vary between
instrument types (an equity quote has marketCap; an ETF/fund quote has
netAssets instead, and neither field is present on the other's response).
Rather than modeling every field or forcing equities/funds/ETFs into one
shape, ScreenerQuote captures the subset that is genuinely common across
all three - confirmed by sampling real equity, ETF, mutual-fund and bond
screens - and leaves quote_type on the entry so callers know what kind of
instrument each result is.
"""

from pydantic import BaseModel, Field, field_validator


def _nan_to_none(value: object) -> object:
    """Map a float NaN to None, passing through everything else unchanged.

    Screener quotes are read from the same kind of upstream response as
    Ticker.info, which represents a missing numeric field as float NaN
    rather than absent-or-null.
    """
    if isinstance(value, float) and value != value:  # NaN is the only float that is != itself
        return None
    return value


class ScreenerQuote(BaseModel):
    """A single result from a screener query.

    market_cap is None for funds and ETFs, which report net_assets
    instead - confirmed against real top_etfs_us, top_mutual_funds and
    bond_etfs screens, where every sampled entry had it missing.
    """

    symbol: str = Field(..., description="Ticker symbol.")
    quote_type: str | None = Field(
        None, alias="quoteType", description="Instrument type, e.g. 'EQUITY', 'ETF' or 'MUTUALFUND'."
    )
    short_name: str | None = Field(None, alias="shortName", description="Short display name.")
    long_name: str | None = Field(None, alias="longName", description="Full display name.")
    exchange: str | None = Field(None, alias="exchange", description="Exchange code.")
    currency: str | None = Field(None, alias="currency", description="Trading currency.")
    regular_market_price: float | None = Field(
        None, alias="regularMarketPrice", description="Latest regular-market price."
    )
    regular_market_change: float | None = Field(
        None, alias="regularMarketChange", description="Change from the previous close."
    )
    regular_market_change_percent: float | None = Field(
        None, alias="regularMarketChangePercent", description="Percentage change from the previous close."
    )
    regular_market_volume: float | None = Field(
        None, alias="regularMarketVolume", description="Regular-market trading volume."
    )
    market_cap: float | None = Field(
        None, alias="marketCap", description="Market capitalization. None for funds and ETFs; see net_assets."
    )
    net_assets: float | None = Field(
        None, alias="netAssets", description="Net assets under management. Present for funds and ETFs."
    )
    fifty_two_week_high: float | None = Field(None, alias="fiftyTwoWeekHigh", description="52-week high price.")
    fifty_two_week_low: float | None = Field(None, alias="fiftyTwoWeekLow", description="52-week low price.")

    @field_validator(
        "regular_market_price",
        "regular_market_change",
        "regular_market_change_percent",
        "regular_market_volume",
        "market_cap",
        "net_assets",
        "fifty_two_week_high",
        "fifty_two_week_low",
        mode="before",
    )
    @classmethod
    def _normalize_missing_metric(cls, value: object) -> object:
        return _nan_to_none(value)


class ScreenerResult(BaseModel):
    """A page of screener results."""

    total: int = Field(..., description="Total number of matches for the query, across all pages.")
    quotes: list[ScreenerQuote] = Field(..., description="Matching instruments for this page.")
