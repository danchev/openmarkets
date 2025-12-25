from datetime import datetime

import pandas as pd
from pydantic import BaseModel, Field, field_validator


class OptionUnderlying(BaseModel):
    """Schema for the underlying asset of an option chain."""

    language: str | None = Field(None, description="Language code.", alias="language")
    region: str | None = Field(None, description="Region code.", alias="region")
    quote_type: str | None = Field(None, description="Type of quote.", alias="quoteType")
    type_disp: str | None = Field(None, description="Display type.", alias="typeDisp")
    quote_source_name: str | None = Field(None, description="Quote source name.", alias="quoteSourceName")
    triggerable: bool | None = Field(None, description="Whether price alerts can be triggered.", alias="triggerable")
    custom_price_alert_confidence: str | None = Field(
        None, description="Custom price alert confidence level.", alias="customPriceAlertConfidence"
    )
    short_name: str | None = Field(None, description="Short name of the asset.", alias="shortName")
    long_name: str | None = Field(None, description="Long name of the asset.", alias="longName")
    market_state: str | None = Field(
        None, description="Current market state (e.g., PRE, REGULAR, POST, CLOSED).", alias="marketState"
    )
    post_market_time: int | None = Field(
        None, description="Post-market time as Unix timestamp.", alias="postMarketTime"
    )
    regular_market_time: int | None = Field(
        None, description="Regular market time as Unix timestamp.", alias="regularMarketTime"
    )
    exchange: str | None = Field(None, description="Exchange code.", alias="exchange")
    message_board_id: str | None = Field(None, description="Message board identifier.", alias="messageBoardId")
    exchange_timezone_name: str | None = Field(
        None, description="Exchange timezone name.", alias="exchangeTimezoneName"
    )
    exchange_timezone_short_name: str | None = Field(
        None, description="Exchange timezone short name.", alias="exchangeTimezoneShortName"
    )
    gmt_offset_milliseconds: int | None = Field(
        None, description="GMT offset in milliseconds.", alias="gmtOffSetMilliseconds"
    )
    market: str | None = Field(None, description="Market identifier.", alias="market")
    currency: str | None = Field(None, description="Currency of the asset.", alias="currency")
    corporate_actions: list | None = Field(None, description="List of corporate actions.", alias="corporateActions")
    eps_current_year: float | None = Field(
        None, description="Earnings per share for the current year.", alias="epsCurrentYear"
    )
    price_eps_current_year: float | None = Field(
        None, description="Price to EPS ratio for the current year.", alias="priceEpsCurrentYear"
    )
    shares_outstanding: int | None = Field(None, description="Number of shares outstanding.", alias="sharesOutstanding")
    book_value: float | None = Field(None, description="Book value per share.", alias="bookValue")
    fifty_day_average: float | None = Field(None, description="50-day moving average.", alias="fiftyDayAverage")
    fifty_day_average_change: float | None = Field(
        None, description="Change from 50-day average.", alias="fiftyDayAverageChange"
    )
    fifty_day_average_change_percent: float | None = Field(
        None, description="Percentage change from 50-day average.", alias="fiftyDayAverageChangePercent"
    )
    two_hundred_day_average: float | None = Field(
        None, description="200-day moving average.", alias="twoHundredDayAverage"
    )
    two_hundred_day_average_change: float | None = Field(
        None, description="Change from 200-day average.", alias="twoHundredDayAverageChange"
    )
    two_hundred_day_average_change_percent: float | None = Field(
        None, description="Percentage change from 200-day average.", alias="twoHundredDayAverageChangePercent"
    )
    market_cap: int | None = Field(None, description="Market capitalization.", alias="marketCap")
    forward_pe: float | None = Field(None, description="Forward price-to-earnings ratio.", alias="forwardPE")
    price_to_book: float | None = Field(None, description="Price-to-book ratio.", alias="priceToBook")
    source_interval: int | None = Field(None, description="Source data interval in seconds.", alias="sourceInterval")
    exchange_data_delayed_by: int | None = Field(
        None, description="Exchange data delay in minutes.", alias="exchangeDataDelayedBy"
    )
    average_analyst_rating: str | None = Field(
        None, description="Average analyst rating.", alias="averageAnalystRating"
    )
    tradeable: bool | None = Field(None, description="Whether the asset is tradeable.", alias="tradeable")
    crypto_tradeable: bool | None = Field(
        None, description="Whether crypto trading is available.", alias="cryptoTradeable"
    )
    esg_populated: bool | None = Field(None, description="Whether ESG data is populated.", alias="esgPopulated")
    regular_market_change_percent: float | None = Field(
        None, description="Regular market percentage change.", alias="regularMarketChangePercent"
    )
    regular_market_price: float | None = Field(None, description="Regular market price.", alias="regularMarketPrice")
    has_pre_post_market_data: bool | None = Field(
        None, description="Whether pre/post-market data is available.", alias="hasPrePostMarketData"
    )
    first_trade_date_milliseconds: int | None = Field(
        None, description="First trade date in milliseconds since epoch.", alias="firstTradeDateMilliseconds"
    )
    price_hint: int | None = Field(None, description="Price hint for formatting.", alias="priceHint")
    post_market_change_percent: float | None = Field(
        None, description="Post-market percentage change.", alias="postMarketChangePercent"
    )
    post_market_price: float | None = Field(None, description="Post-market price.", alias="postMarketPrice")
    post_market_change: float | None = Field(None, description="Post-market price change.", alias="postMarketChange")
    regular_market_change: float | None = Field(
        None, description="Regular market price change.", alias="regularMarketChange"
    )
    regular_market_day_high: float | None = Field(
        None, description="Regular market day's highest price.", alias="regularMarketDayHigh"
    )
    regular_market_day_range: str | None = Field(
        None, description="Regular market day price range.", alias="regularMarketDayRange"
    )
    regular_market_day_low: float | None = Field(
        None, description="Regular market day's lowest price.", alias="regularMarketDayLow"
    )
    regular_market_volume: int | None = Field(
        None, description="Regular market trading volume.", alias="regularMarketVolume"
    )
    regular_market_previous_close: float | None = Field(
        None, description="Regular market previous close price.", alias="regularMarketPreviousClose"
    )
    bid: float | None = Field(None, description="Current bid price.", alias="bid")
    ask: float | None = Field(None, description="Current ask price.", alias="ask")
    bid_size: int | None = Field(None, description="Size of current bid.", alias="bidSize")
    ask_size: int | None = Field(None, description="Size of current ask.", alias="askSize")
    full_exchange_name: str | None = Field(None, description="Full name of the exchange.", alias="fullExchangeName")
    financial_currency: str | None = Field(
        None, description="Currency used for financial statements.", alias="financialCurrency"
    )
    regular_market_open: float | None = Field(
        None, description="Regular market opening price.", alias="regularMarketOpen"
    )
    average_daily_volume_3_month: int | None = Field(
        None, description="Average daily volume over 3 months.", alias="averageDailyVolume3Month"
    )
    average_daily_volume_10_day: int | None = Field(
        None, description="Average daily volume over 10 days.", alias="averageDailyVolume10Day"
    )
    fifty_two_week_low_change: float | None = Field(
        None, description="Change from 52-week low.", alias="fiftyTwoWeekLowChange"
    )
    fifty_two_week_low_change_percent: float | None = Field(
        None, description="Percentage change from 52-week low.", alias="fiftyTwoWeekLowChangePercent"
    )
    fifty_two_week_range: str | None = Field(None, description="52-week price range.", alias="fiftyTwoWeekRange")
    fifty_two_week_high_change: float | None = Field(
        None, description="Change from 52-week high.", alias="fiftyTwoWeekHighChange"
    )
    fifty_two_week_high_change_percent: float | None = Field(
        None, description="Percentage change from 52-week high.", alias="fiftyTwoWeekHighChangePercent"
    )
    fifty_two_week_low: float | None = Field(None, description="52-week low price.", alias="fiftyTwoWeekLow")
    fifty_two_week_high: float | None = Field(None, description="52-week high price.", alias="fiftyTwoWeekHigh")
    fifty_two_week_change_percent: float | None = Field(
        None, description="52-week percentage change.", alias="fiftyTwoWeekChangePercent"
    )
    dividend_date: int | None = Field(None, description="Dividend date as Unix timestamp.", alias="dividendDate")
    earnings_timestamp: int | None = Field(None, description="Earnings timestamp.", alias="earningsTimestamp")
    earnings_timestamp_start: int | None = Field(
        None, description="Earnings period start timestamp.", alias="earningsTimestampStart"
    )
    earnings_timestamp_end: int | None = Field(
        None, description="Earnings period end timestamp.", alias="earningsTimestampEnd"
    )
    earnings_call_timestamp_start: int | None = Field(
        None, description="Earnings call start timestamp.", alias="earningsCallTimestampStart"
    )
    earnings_call_timestamp_end: int | None = Field(
        None, description="Earnings call end timestamp.", alias="earningsCallTimestampEnd"
    )
    is_earnings_date_estimate: bool | None = Field(
        None, description="Whether the earnings date is an estimate.", alias="isEarningsDateEstimate"
    )
    trailing_annual_dividend_rate: float | None = Field(
        None, description="Trailing annual dividend rate.", alias="trailingAnnualDividendRate"
    )
    trailing_pe: float | None = Field(None, description="Trailing price-to-earnings ratio.", alias="trailingPE")
    dividend_rate: float | None = Field(None, description="Dividend rate.", alias="dividendRate")
    trailing_annual_dividend_yield: float | None = Field(
        None, description="Trailing annual dividend yield.", alias="trailingAnnualDividendYield"
    )
    dividend_yield: float | None = Field(None, description="Dividend yield.", alias="dividendYield")
    eps_trailing_twelve_months: float | None = Field(
        None, description="Earnings per share over trailing twelve months.", alias="epsTrailingTwelveMonths"
    )
    eps_forward: float | None = Field(None, description="Forward earnings per share.", alias="epsForward")
    display_name: str | None = Field(None, description="Display name of the asset.", alias="displayName")
    symbol: str | None = Field(None, description="Ticker symbol.", alias="symbol")


class OptionExpirationDate(BaseModel):
    """Available option expiration date for a ticker."""

    date_: datetime = Field(..., description="Expiration date.", alias="date")


class CallOption(BaseModel):
    """Schema for a call option contract."""

    contract_symbol: str = Field(..., description="Option contract symbol.", alias="contractSymbol")
    last_trade_date: datetime = Field(..., description="Last trade date.", alias="lastTradeDate")
    strike: float = Field(..., description="Strike price.", alias="strike")
    last_price: float = Field(..., description="Last traded price.", alias="lastPrice")
    bid: float = Field(..., description="Bid price.", alias="bid")
    ask: float = Field(..., description="Ask price.", alias="ask")
    change: float = Field(..., description="Change in price.", alias="change")
    percent_change: float = Field(..., description="Percent change in price.", alias="percentChange")
    volume: float | None = Field(None, description="Trading volume.", alias="volume")
    open_interest: float | None = Field(None, description="Open interest.", alias="openInterest")
    implied_volatility: float = Field(..., description="Implied volatility.", alias="impliedVolatility")
    in_the_money: bool = Field(..., description="Is the option in the money.", alias="inTheMoney")
    contract_size: str = Field(..., description="Contract size.", alias="contractSize")
    currency: str = Field(..., description="Currency of the contract.", alias="currency")

    @field_validator("last_trade_date", mode="before")
    def parse_last_trade_date(cls, value) -> datetime:
        """Validator to parse lastTradeDate from timestamp to date."""
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        return value


class PutOption(BaseModel):
    """Schema for a put option contract."""

    contract_symbol: str = Field(..., description="Option contract symbol.", alias="contractSymbol")
    last_trade_date: datetime = Field(..., description="Last trade date.", alias="lastTradeDate")
    strike: float = Field(..., description="Strike price.", alias="strike")
    last_price: float = Field(..., description="Last traded price.", alias="lastPrice")
    bid: float = Field(..., description="Bid price.", alias="bid")
    ask: float = Field(..., description="Ask price.", alias="ask")
    change: float = Field(..., description="Change in price.", alias="change")
    percent_change: float = Field(..., description="Percent change in price.", alias="percentChange")
    volume: float | None = Field(None, description="Trading volume.", alias="volume")
    open_interest: float | None = Field(None, description="Open interest.", alias="openInterest")
    implied_volatility: float = Field(..., description="Implied volatility.", alias="impliedVolatility")
    in_the_money: bool = Field(..., description="Is the option in the money.", alias="inTheMoney")
    contract_size: str = Field(..., description="Contract size.", alias="contractSize")
    currency: str = Field(..., description="Currency of the contract.", alias="currency")

    @field_validator("last_trade_date", mode="before")
    def parse_last_trade_date(cls, value) -> datetime:
        """Validator to parse lastTradeDate from timestamp to date."""
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        return value


class OptionContractChain(BaseModel):
    """Schema for the options chain data of a ticker."""

    calls: list[CallOption] | None = Field(None, description="Call option contracts.", alias="calls")
    puts: list[PutOption] | None = Field(None, description="Put option contracts.", alias="puts")
    underlying: OptionUnderlying | None = Field(None, description="Underlying asset information.", alias="underlying")
