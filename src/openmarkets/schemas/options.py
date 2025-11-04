from datetime import datetime
from typing import Optional

import pandas as pd
from pydantic import BaseModel, Field, field_validator


class OptionUnderlying(BaseModel):
    """Schema for the underlying asset of an option chain."""

    language: Optional[str] = None
    region: Optional[str] = None
    quoteType: Optional[str] = None
    typeDisp: Optional[str] = None
    quoteSourceName: Optional[str] = None
    triggerable: Optional[bool] = None
    customPriceAlertConfidence: Optional[str] = None
    shortName: Optional[str] = None
    longName: Optional[str] = None
    marketState: Optional[str] = None
    postMarketTime: Optional[int] = None
    regularMarketTime: Optional[int] = None
    exchange: Optional[str] = None
    messageBoardId: Optional[str] = None
    exchangeTimezoneName: Optional[str] = None
    exchangeTimezoneShortName: Optional[str] = None
    gmtOffSetMilliseconds: Optional[int] = None
    market: Optional[str] = None
    currency: Optional[str] = None
    corporateActions: Optional[list] = None
    epsCurrentYear: Optional[float] = None
    priceEpsCurrentYear: Optional[float] = None
    sharesOutstanding: Optional[int] = None
    bookValue: Optional[float] = None
    fiftyDayAverage: Optional[float] = None
    fiftyDayAverageChange: Optional[float] = None
    fiftyDayAverageChangePercent: Optional[float] = None
    twoHundredDayAverage: Optional[float] = None
    twoHundredDayAverageChange: Optional[float] = None
    twoHundredDayAverageChangePercent: Optional[float] = None
    marketCap: Optional[int] = None
    forwardPE: Optional[float] = None
    priceToBook: Optional[float] = None
    sourceInterval: Optional[int] = None
    exchangeDataDelayedBy: Optional[int] = None
    averageAnalystRating: Optional[str] = None
    tradeable: Optional[bool] = None
    cryptoTradeable: Optional[bool] = None
    esgPopulated: Optional[bool] = None
    regularMarketChangePercent: Optional[float] = None
    regularMarketPrice: Optional[float] = None
    hasPrePostMarketData: Optional[bool] = None
    firstTradeDateMilliseconds: Optional[int] = None
    priceHint: Optional[int] = None
    postMarketChangePercent: Optional[float] = None
    postMarketPrice: Optional[float] = None
    postMarketChange: Optional[float] = None
    regularMarketChange: Optional[float] = None
    regularMarketDayHigh: Optional[float] = None
    regularMarketDayRange: Optional[str] = None
    regularMarketDayLow: Optional[float] = None
    regularMarketVolume: Optional[int] = None
    regularMarketPreviousClose: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    bidSize: Optional[int] = None
    askSize: Optional[int] = None
    fullExchangeName: Optional[str] = None
    financialCurrency: Optional[str] = None
    regularMarketOpen: Optional[float] = None
    averageDailyVolume3Month: Optional[int] = None
    averageDailyVolume10Day: Optional[int] = None
    fiftyTwoWeekLowChange: Optional[float] = None
    fiftyTwoWeekLowChangePercent: Optional[float] = None
    fiftyTwoWeekRange: Optional[str] = None
    fiftyTwoWeekHighChange: Optional[float] = None
    fiftyTwoWeekHighChangePercent: Optional[float] = None
    fiftyTwoWeekLow: Optional[float] = None
    fiftyTwoWeekHigh: Optional[float] = None
    fiftyTwoWeekChangePercent: Optional[float] = None
    dividendDate: Optional[int] = None
    earningsTimestamp: Optional[int] = None
    earningsTimestampStart: Optional[int] = None
    earningsTimestampEnd: Optional[int] = None
    earningsCallTimestampStart: Optional[int] = None
    earningsCallTimestampEnd: Optional[int] = None
    isEarningsDateEstimate: Optional[bool] = None
    trailingAnnualDividendRate: Optional[float] = None
    trailingPE: Optional[float] = None
    dividendRate: Optional[float] = None
    trailingAnnualDividendYield: Optional[float] = None
    dividendYield: Optional[float] = None
    epsTrailingTwelveMonths: Optional[float] = None
    epsForward: Optional[float] = None
    displayName: Optional[str] = None
    symbol: Optional[str] = None


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
    volume: Optional[float] = Field(None, description="Trading volume.")
    openInterest: int = Field(..., description="Open interest.")
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
    volume: Optional[float] = Field(None, description="Trading volume.")
    openInterest: int = Field(..., description="Open interest.")
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

    calls: Optional[list[CallOption]] = Field(None, description="Call option contracts.")
    puts: Optional[list[PutOption]] = Field(None, description="Put option contracts.")
    underlying: Optional[OptionUnderlying] = Field(None, description="Underlying asset information.")
