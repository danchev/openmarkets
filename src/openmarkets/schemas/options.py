from datetime import datetime

import pandas as pd
from pydantic import BaseModel, Field, field_validator


class OptionUnderlying(BaseModel):
    """Schema for the underlying asset of an option chain."""

    language: str | None = None
    region: str | None = None
    quoteType: str | None = None
    typeDisp: str | None = None
    quoteSourceName: str | None = None
    triggerable: bool | None = None
    customPriceAlertConfidence: str | None = None
    shortName: str | None = None
    longName: str | None = None
    marketState: str | None = None
    postMarketTime: int | None = None
    regularMarketTime: int | None = None
    exchange: str | None = None
    messageBoardId: str | None = None
    exchangeTimezoneName: str | None = None
    exchangeTimezoneShortName: str | None = None
    gmtOffSetMilliseconds: int | None = None
    market: str | None = None
    currency: str | None = None
    corporateActions: list | None = None
    epsCurrentYear: float | None = None
    priceEpsCurrentYear: float | None = None
    sharesOutstanding: int | None = None
    bookValue: float | None = None
    fiftyDayAverage: float | None = None
    fiftyDayAverageChange: float | None = None
    fiftyDayAverageChangePercent: float | None = None
    twoHundredDayAverage: float | None = None
    twoHundredDayAverageChange: float | None = None
    twoHundredDayAverageChangePercent: float | None = None
    marketCap: int | None = None
    forwardPE: float | None = None
    priceToBook: float | None = None
    sourceInterval: int | None = None
    exchangeDataDelayedBy: int | None = None
    averageAnalystRating: str | None = None
    tradeable: bool | None = None
    cryptoTradeable: bool | None = None
    esgPopulated: bool | None = None
    regularMarketChangePercent: float | None = None
    regularMarketPrice: float | None = None
    hasPrePostMarketData: bool | None = None
    firstTradeDateMilliseconds: int | None = None
    priceHint: int | None = None
    postMarketChangePercent: float | None = None
    postMarketPrice: float | None = None
    postMarketChange: float | None = None
    regularMarketChange: float | None = None
    regularMarketDayHigh: float | None = None
    regularMarketDayRange: str | None = None
    regularMarketDayLow: float | None = None
    regularMarketVolume: int | None = None
    regularMarketPreviousClose: float | None = None
    bid: float | None = None
    ask: float | None = None
    bidSize: int | None = None
    askSize: int | None = None
    fullExchangeName: str | None = None
    financialCurrency: str | None = None
    regularMarketOpen: float | None = None
    averageDailyVolume3Month: int | None = None
    averageDailyVolume10Day: int | None = None
    fiftyTwoWeekLowChange: float | None = None
    fiftyTwoWeekLowChangePercent: float | None = None
    fiftyTwoWeekRange: str | None = None
    fiftyTwoWeekHighChange: float | None = None
    fiftyTwoWeekHighChangePercent: float | None = None
    fiftyTwoWeekLow: float | None = None
    fiftyTwoWeekHigh: float | None = None
    fiftyTwoWeekChangePercent: float | None = None
    dividendDate: int | None = None
    earningsTimestamp: int | None = None
    earningsTimestampStart: int | None = None
    earningsTimestampEnd: int | None = None
    earningsCallTimestampStart: int | None = None
    earningsCallTimestampEnd: int | None = None
    isEarningsDateEstimate: bool | None = None
    trailingAnnualDividendRate: float | None = None
    trailingPE: float | None = None
    dividendRate: float | None = None
    trailingAnnualDividendYield: float | None = None
    dividendYield: float | None = None
    epsTrailingTwelveMonths: float | None = None
    epsForward: float | None = None
    displayName: str | None = None
    symbol: str | None = None


class OptionExpirationDate(BaseModel):
    """Available option expiration date for a ticker."""

    date_: datetime = Field(..., description="Expiration date.", alias="date")


class CallOption(BaseModel):
    """Schema for a call option contract."""

    contractSymbol: str = Field(..., description="Option contract symbol.")
    lastTradeDate: datetime = Field(..., description="Last trade date.")
    strike: float = Field(..., description="Strike price.")
    lastPrice: float = Field(..., description="Last traded price.")
    bid: float = Field(..., description="Bid price.")
    ask: float = Field(..., description="Ask price.")
    change: float = Field(..., description="Change in price.")
    percentChange: float = Field(..., description="Percent change in price.")
    volume: float | None = Field(None, description="Trading volume.")
    openInterest: float | None = Field(None, description="Open interest.")
    impliedVolatility: float = Field(..., description="Implied volatility.")
    inTheMoney: bool = Field(..., description="Is the option in the money.")
    contractSize: str = Field(..., description="Contract size.")
    currency: str = Field(..., description="Currency of the contract.")

    @field_validator("lastTradeDate")
    def parse_last_trade_date(cls, value) -> datetime:
        """Validator to parse lastTradeDate from timestamp to date."""
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        return value


class PutOption(BaseModel):
    """Schema for a put option contract."""

    contractSymbol: str = Field(..., description="Option contract symbol.")
    lastTradeDate: datetime = Field(..., description="Last trade date.")
    strike: float = Field(..., description="Strike price.")
    lastPrice: float = Field(..., description="Last traded price.")
    bid: float = Field(..., description="Bid price.")
    ask: float = Field(..., description="Ask price.")
    change: float = Field(..., description="Change in price.")
    percentChange: float = Field(..., description="Percent change in price.")
    volume: float | None = Field(None, description="Trading volume.")
    openInterest: float | None = Field(None, description="Open interest.")
    impliedVolatility: float = Field(..., description="Implied volatility.")
    inTheMoney: bool = Field(..., description="Is the option in the money.")
    contractSize: str = Field(..., description="Contract size.")
    currency: str = Field(..., description="Currency of the contract.")

    @field_validator("lastTradeDate")
    def parse_last_trade_date(cls, value) -> datetime:
        """Validator to parse lastTradeDate from timestamp to date."""
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        return value


class OptionContractChain(BaseModel):
    """Schema for the options chain data of a ticker."""

    calls: list[CallOption] | None = Field(None, description="Call option contracts.")
    puts: list[PutOption] | None = Field(None, description="Put option contracts.")
    underlying: OptionUnderlying | None = Field(None, description="Underlying asset information.")
