from datetime import date, datetime
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field, field_validator

from openmarkets.schemas.company import CompanyOfficer


class StockFastInfo(BaseModel):
    """Fast info snapshot for a stock ticker, typically from yfinance or similar APIs."""

    currency: str = Field(..., description="Currency of the ticker.", alias="currency")
    day_high: float = Field(..., description="Day's high price.", alias="dayHigh")
    day_low: float = Field(..., description="Day's low price.", alias="dayLow")
    exchange: str = Field(..., description="Exchange where the ticker is listed.", alias="exchange")
    fifty_day_average: float = Field(..., description="50-day average price.", alias="fiftyDayAverage")
    last_price: float = Field(..., description="Last traded price.", alias="lastPrice")
    last_volume: int = Field(..., description="Last traded volume.", alias="lastVolume")
    market_cap: float | None = Field(None, description="Market capitalization.", alias="marketCap")
    open: float = Field(..., description="Opening price.", alias="open")
    previous_close: float = Field(..., description="Previous closing price.", alias="previousClose")
    quote_type: str = Field(..., description="Type of quote (e.g., equity, ETF).", alias="quoteType")
    regular_market_previous_close: float = Field(
        ..., description="Regular market previous close.", alias="regularMarketPreviousClose"
    )
    shares: int | None = Field(None, description="Number of shares outstanding.", alias="shares")
    ten_day_average_volume: int = Field(..., description="10-day average volume.", alias="tenDayAverageVolume")
    three_month_average_volume: int = Field(..., description="3-month average volume.", alias="threeMonthAverageVolume")
    timezone: str = Field(..., description="Timezone of the exchange.", alias="timezone")
    two_hundred_day_average: float = Field(..., description="200-day average price.", alias="twoHundredDayAverage")
    year_change: float = Field(..., description="Change over the past year.", alias="yearChange")
    year_high: float = Field(..., description="52-week high price.", alias="yearHigh")
    year_low: float = Field(..., description="52-week low price.", alias="yearLow")


class StockInfo(BaseModel):
    """Comprehensive schema for stock information, typically from yfinance Ticker.info."""

    address1: str | None = Field(None, description="Primary address line of the company.", alias="address1")
    city: str | None = Field(None, description="City of the company's headquarters.", alias="city")
    state: str | None = Field(None, description="State or province of the company's headquarters.", alias="state")
    zip: str | None = Field(None, description="Postal code of the company's headquarters.", alias="zip")
    country: str | None = Field(None, description="Country of the company's headquarters.", alias="country")
    phone: str | None = Field(None, description="Contact phone number.", alias="phone")
    website: str | None = Field(None, description="Company website URL.", alias="website")
    industry: str | None = Field(None, description="Industry classification.", alias="industry")
    industry_key: str | None = Field(None, description="Industry key.", alias="industryKey")
    industry_disp: str | None = Field(None, description="Industry display name.", alias="industryDisp")
    sector: str | None = Field(None, description="Sector classification.", alias="sector")
    sector_key: str | None = Field(None, description="Sector key.", alias="sectorKey")
    sector_disp: str | None = Field(None, description="Sector display name.", alias="sectorDisp")
    long_business_summary: str | None = Field(
        None, description="Extended business description.", alias="longBusinessSummary"
    )
    full_time_employees: int | None = Field(
        None, description="Number of full-time employees.", alias="fullTimeEmployees"
    )
    company_officers: list[CompanyOfficer] | None = Field(
        None, description="List of company officers.", alias="companyOfficers"
    )
    audit_risk: int | None = Field(None, description="Audit risk score.", alias="auditRisk")
    board_risk: int | None = Field(None, description="Board risk score.", alias="boardRisk")
    compensation_risk: int | None = Field(None, description="Compensation risk score.", alias="compensationRisk")
    share_holder_rights_risk: int | None = Field(
        None, description="Shareholder rights risk score.", alias="shareHolderRightsRisk"
    )
    overall_risk: int | None = Field(None, description="Overall risk score.", alias="overallRisk")
    governance_epoch_date: int | None = Field(
        None, description="Governance epoch date (timestamp).", alias="governanceEpochDate"
    )
    compensation_as_of_epoch_date: int | None = Field(
        None, description="Compensation as of epoch date (timestamp).", alias="compensationAsOfEpochDate"
    )
    ir_website: str | None = Field(None, description="Investor relations website.", alias="irWebsite")
    executive_team: list[Any] | None = Field(None, description="List of executive team members.", alias="executiveTeam")
    max_age: int | None = Field(None, description="Maximum age of the data.", alias="maxAge")
    price_hint: int | None = Field(None, description="Price hint for display.", alias="priceHint")
    previous_close: float | None = Field(None, description="Previous closing price.", alias="previousClose")
    open: float | None = Field(None, description="Opening price.", alias="open")
    day_low: float | None = Field(None, description="Day's low price.", alias="dayLow")
    day_high: float | None = Field(None, description="Day's high price.", alias="dayHigh")
    regular_market_previous_close: float | None = Field(
        None, description="Regular market previous close.", alias="regularMarketPreviousClose"
    )
    regular_market_open: float | None = Field(
        None, description="Regular market opening price.", alias="regularMarketOpen"
    )
    regular_market_day_low: float | None = Field(
        None, description="Regular market day's low price.", alias="regularMarketDayLow"
    )
    regular_market_day_high: float | None = Field(
        None, description="Regular market day's high price.", alias="regularMarketDayHigh"
    )
    dividend_rate: float | None = Field(None, description="Dividend rate.", alias="dividendRate")
    dividend_yield: float | None = Field(None, description="Dividend yield.", alias="dividendYield")
    ex_dividend_date: datetime | None = Field(None, description="Ex-dividend date.", alias="exDividendDate")
    payout_ratio: float | None = Field(None, description="Payout ratio.", alias="payoutRatio")
    five_year_avg_dividend_yield: float | None = Field(
        None, description="Five-year average dividend yield.", alias="fiveYearAvgDividendYield"
    )
    beta: float | None = Field(None, description="Beta value.", alias="beta")
    trailing_pe: float | None = Field(None, description="Trailing P/E ratio.", alias="trailingPE")
    forward_pe: float | None = Field(None, description="Forward P/E ratio.", alias="forwardPE")
    volume: int | None = Field(None, description="Trading volume.", alias="volume")
    regular_market_volume: int | None = Field(
        None, description="Regular market trading volume.", alias="regularMarketVolume"
    )
    average_volume: int | None = Field(None, description="Average trading volume.", alias="averageVolume")
    average_volume_10days: int | None = Field(
        None, description="10-day average trading volume.", alias="averageVolume10days"
    )
    average_daily_volume_10_day: int | None = Field(
        None, description="10-day average daily volume.", alias="averageDailyVolume10Day"
    )
    bid: float | None = Field(None, description="Bid price.", alias="bid")
    ask: float | None = Field(None, description="Ask price.", alias="ask")
    bid_size: int | None = Field(None, description="Bid size.", alias="bidSize")
    ask_size: int | None = Field(None, description="Ask size.", alias="askSize")
    market_cap: int | None = Field(None, description="Market capitalization.", alias="marketCap")
    fifty_two_week_low: float | None = Field(None, description="52-week low price.", alias="fiftyTwoWeekLow")
    fifty_two_week_high: float | None = Field(None, description="52-week high price.", alias="fiftyTwoWeekHigh")
    all_time_high: float | None = Field(None, description="All-time high price.", alias="allTimeHigh")
    all_time_low: float | None = Field(None, description="All-time low price.", alias="allTimeLow")
    price_to_sales_trailing_12_months: float | None = Field(
        None, description="Price to sales (TTM).", alias="priceToSalesTrailing12Months"
    )
    fifty_day_average: float | None = Field(None, description="50-day average price.", alias="fiftyDayAverage")
    two_hundred_day_average: float | None = Field(
        None, description="200-day average price.", alias="twoHundredDayAverage"
    )
    trailing_annual_dividend_rate: float | None = Field(
        None, description="Trailing annual dividend rate.", alias="trailingAnnualDividendRate"
    )
    trailing_annual_dividend_yield: float | None = Field(
        None, description="Trailing annual dividend yield.", alias="trailingAnnualDividendYield"
    )
    currency: str | None = Field(None, description="Trading currency.", alias="currency")
    tradeable: bool | None = Field(None, description="Is the stock tradeable.", alias="tradeable")
    enterprise_value: int | None = Field(None, description="Enterprise value.", alias="enterpriseValue")
    profit_margins: float | None = Field(None, description="Profit margins.", alias="profitMargins")
    float_shares: int | None = Field(None, description="Float shares.", alias="floatShares")
    shares_outstanding: int | None = Field(None, description="Shares outstanding.", alias="sharesOutstanding")
    shares_short: int | None = Field(None, description="Shares short.", alias="sharesShort")
    shares_short_prior_month: int | None = Field(
        None, description="Shares short prior month.", alias="sharesShortPriorMonth"
    )
    shares_short_previous_month_date: int | None = Field(
        None, description="Shares short previous month date.", alias="sharesShortPreviousMonthDate"
    )
    date_short_interest: int | None = Field(None, description="Date of short interest.", alias="dateShortInterest")
    shares_percent_shares_out: float | None = Field(
        None, description="Percent shares out.", alias="sharesPercentSharesOut"
    )
    held_percent_insiders: float | None = Field(
        None, description="Percent held by insiders.", alias="heldPercentInsiders"
    )
    held_percent_institutions: float | None = Field(
        None, description="Percent held by institutions.", alias="heldPercentInstitutions"
    )
    short_ratio: float | None = Field(None, description="Short ratio.", alias="shortRatio")
    short_percent_of_float: float | None = Field(
        None, description="Short percent of float.", alias="shortPercentOfFloat"
    )
    implied_shares_outstanding: int | None = Field(
        None, description="Implied shares outstanding.", alias="impliedSharesOutstanding"
    )
    book_value: float | None = Field(None, description="Book value.", alias="bookValue")
    price_to_book: float | None = Field(None, description="Price to book ratio.", alias="priceToBook")
    last_fiscal_year_end: datetime | None = Field(None, description="Last fiscal year end.", alias="lastFiscalYearEnd")
    next_fiscal_year_end: datetime | None = Field(None, description="Next fiscal year end.", alias="nextFiscalYearEnd")
    most_recent_quarter: int | None = Field(
        None, description="Most recent quarter (timestamp).", alias="mostRecentQuarter"
    )
    earnings_quarterly_growth: float | None = Field(
        None, description="Earnings quarterly growth.", alias="earningsQuarterlyGrowth"
    )
    net_income_to_common: int | None = Field(None, description="Net income to common.", alias="netIncomeToCommon")
    trailing_eps: float | None = Field(None, description="Trailing EPS.", alias="trailingEps")
    forward_eps: float | None = Field(None, description="Forward EPS.", alias="forwardEps")
    last_split_factor: str | None = Field(None, description="Last split factor.", alias="lastSplitFactor")
    last_split_date: datetime | None = Field(None, description="Last split date.", alias="lastSplitDate")
    enterprise_to_revenue: float | None = Field(
        None, description="Enterprise to revenue ratio.", alias="enterpriseToRevenue"
    )
    enterprise_to_ebitda: float | None = Field(
        None, description="Enterprise to EBITDA ratio.", alias="enterpriseToEbitda"
    )
    fifty_two_week_change: float | None = Field(None, alias="52WeekChange", description="52-week change.")
    sandp_52_week_change: float | None = Field(None, description="S&P 52-week change.", alias="SandP52WeekChange")
    last_dividend_value: float | None = Field(None, description="Last dividend value.", alias="lastDividendValue")
    last_dividend_date: datetime | None = Field(None, description="Last dividend date.", alias="lastDividendDate")
    quote_type: str | None = Field(None, description="Quote type.", alias="quoteType")
    current_price: float | None = Field(None, description="Current price.", alias="currentPrice")
    target_high_price: float | None = Field(None, description="Target high price.", alias="targetHighPrice")
    target_low_price: float | None = Field(None, description="Target low price.", alias="targetLowPrice")
    target_mean_price: float | None = Field(None, description="Target mean price.", alias="targetMeanPrice")
    target_median_price: float | None = Field(None, description="Target median price.", alias="targetMedianPrice")
    recommendation_mean: float | None = Field(None, description="Recommendation mean.", alias="recommendationMean")
    recommendation_key: str | None = Field(None, description="Recommendation key.", alias="recommendationKey")
    number_of_analyst_opinions: int | None = Field(
        None, description="Number of analyst opinions.", alias="numberOfAnalystOpinions"
    )
    total_cash: int | None = Field(None, description="Total cash.", alias="totalCash")
    total_cash_per_share: float | None = Field(None, description="Total cash per share.", alias="totalCashPerShare")
    ebitda: int | None = Field(None, description="EBITDA.", alias="ebitda")
    total_debt: int | None = Field(None, description="Total debt.", alias="totalDebt")
    quick_ratio: float | None = Field(None, description="Quick ratio.", alias="quickRatio")
    current_ratio: float | None = Field(None, description="Current ratio.", alias="currentRatio")
    total_revenue: int | None = Field(None, description="Total revenue.", alias="totalRevenue")
    debt_to_equity: float | None = Field(None, description="Debt to equity ratio.", alias="debtToEquity")
    revenue_per_share: float | None = Field(None, description="Revenue per share.", alias="revenuePerShare")
    return_on_assets: float | None = Field(None, description="Return on assets.", alias="returnOnAssets")
    return_on_equity: float | None = Field(None, description="Return on equity.", alias="returnOnEquity")
    gross_profits: int | None = Field(None, description="Gross profits.", alias="grossProfits")
    free_cashflow: int | None = Field(None, description="Free cash flow.", alias="freeCashflow")
    operating_cashflow: int | None = Field(None, description="Operating cash flow.", alias="operatingCashflow")
    earnings_growth: float | None = Field(None, description="Earnings growth.", alias="earningsGrowth")
    revenue_growth: float | None = Field(None, description="Revenue growth.", alias="revenueGrowth")
    gross_margins: float | None = Field(None, description="Gross margins.", alias="grossMargins")
    ebitda_margins: float | None = Field(None, description="EBITDA margins.", alias="ebitdaMargins")
    operating_margins: float | None = Field(None, description="Operating margins.", alias="operatingMargins")
    financial_currency: str | None = Field(None, description="Financial reporting currency.", alias="financialCurrency")
    symbol: str | None = Field(None, description="Ticker symbol.", alias="symbol")
    language: str | None = Field(None, description="Reporting language.", alias="language")
    region: str | None = Field(None, description="Region.", alias="region")
    type_disp: str | None = Field(None, description="Type display name.", alias="typeDisp")
    quote_source_name: str | None = Field(None, description="Quote source name.", alias="quoteSourceName")
    triggerable: bool | None = Field(None, description="Is triggerable.", alias="triggerable")
    custom_price_alert_confidence: str | None = Field(
        None, description="Custom price alert confidence.", alias="customPriceAlertConfidence"
    )
    regular_market_change_percent: float | None = Field(
        None, description="Regular market change percent.", alias="regularMarketChangePercent"
    )
    regular_market_price: float | None = Field(None, description="Regular market price.", alias="regularMarketPrice")
    short_name: str | None = Field(None, description="Short name.", alias="shortName")
    long_name: str | None = Field(None, description="Long name.", alias="longName")
    has_pre_post_market_data: bool | None = Field(
        None, description="Has pre/post market data.", alias="hasPrePostMarketData"
    )
    first_trade_date_milliseconds: int | None = Field(
        None, description="First trade date in milliseconds.", alias="firstTradeDateMilliseconds"
    )
    post_market_change_percent: float | None = Field(
        None, description="Post-market change percent.", alias="postMarketChangePercent"
    )
    post_market_price: float | None = Field(None, description="Post-market price.", alias="postMarketPrice")
    post_market_change: float | None = Field(None, description="Post-market change.", alias="postMarketChange")
    regular_market_change: float | None = Field(None, description="Regular market change.", alias="regularMarketChange")
    regular_market_day_range: str | None = Field(
        None, description="Regular market day range.", alias="regularMarketDayRange"
    )
    full_exchange_name: str | None = Field(None, description="Full exchange name.", alias="fullExchangeName")
    average_daily_volume_3_month: int | None = Field(
        None, description="3-month average daily volume.", alias="averageDailyVolume3Month"
    )
    fifty_two_week_low_change: float | None = Field(
        None, description="52-week low change.", alias="fiftyTwoWeekLowChange"
    )
    fifty_two_week_low_change_percent: float | None = Field(
        None, description="52-week low change percent.", alias="fiftyTwoWeekLowChangePercent"
    )
    fifty_two_week_range: str | None = Field(None, description="52-week range.", alias="fiftyTwoWeekRange")
    fifty_two_week_high_change: float | None = Field(
        None, description="52-week high change.", alias="fiftyTwoWeekHighChange"
    )
    fifty_two_week_high_change_percent: float | None = Field(
        None, description="52-week high change percent.", alias="fiftyTwoWeekHighChangePercent"
    )
    fifty_two_week_change_percent: float | None = Field(
        None, description="52-week change percent.", alias="fiftyTwoWeekChangePercent"
    )
    market_state: str | None = Field(None, description="Market state.", alias="marketState")
    corporate_actions: list[Any] | None = Field(None, description="Corporate actions.", alias="corporateActions")
    post_market_time: int | None = Field(None, description="Post-market time (timestamp).", alias="postMarketTime")
    regular_market_time: int | None = Field(
        None, description="Regular market time (timestamp).", alias="regularMarketTime"
    )
    exchange: str | None = Field(None, description="Exchange code.", alias="exchange")
    message_board_id: str | None = Field(None, description="Message board ID.", alias="messageBoardId")
    exchange_timezone_name: str | None = Field(
        None, description="Exchange timezone name.", alias="exchangeTimezoneName"
    )
    exchange_timezone_short_name: str | None = Field(
        None, description="Exchange timezone short name.", alias="exchangeTimezoneShortName"
    )
    gmt_offset_milliseconds: int | None = Field(
        None, description="GMT offset in milliseconds.", alias="gmtOffSetMilliseconds"
    )
    market: str | None = Field(None, description="Market name.", alias="market")
    esg_populated: bool | None = Field(None, description="ESG data populated.", alias="esgPopulated")
    dividend_date: datetime | None = Field(None, description="Dividend date.", alias="dividendDate")
    earnings_timestamp: datetime | None = Field(None, description="Earnings timestamp.", alias="earningsTimestamp")
    earnings_timestamp_start: datetime | None = Field(
        None, description="Earnings timestamp start.", alias="earningsTimestampStart"
    )
    earnings_timestamp_end: datetime | None = Field(
        None, description="Earnings timestamp end.", alias="earningsTimestampEnd"
    )
    earnings_call_timestamp_start: datetime | None = Field(
        None, description="Earnings call timestamp start.", alias="earningsCallTimestampStart"
    )
    earnings_call_timestamp_end: datetime | None = Field(
        None, description="Earnings call timestamp end.", alias="earningsCallTimestampEnd"
    )
    is_earnings_date_estimate: bool | None = Field(
        None, description="Is earnings date an estimate.", alias="isEarningsDateEstimate"
    )
    eps_trailing_twelve_months: float | None = Field(
        None, description="EPS trailing twelve months.", alias="epsTrailingTwelveMonths"
    )
    eps_forward: float | None = Field(None, description="EPS forward.", alias="epsForward")
    eps_current_year: float | None = Field(None, description="EPS current year.", alias="epsCurrentYear")
    price_eps_current_year: float | None = Field(
        None, description="Price/EPS current year.", alias="priceEpsCurrentYear"
    )
    fifty_day_average_change: float | None = Field(
        None, description="50-day average change.", alias="fiftyDayAverageChange"
    )
    fifty_day_average_change_percent: float | None = Field(
        None, description="50-day average change percent.", alias="fiftyDayAverageChangePercent"
    )
    two_hundred_day_average_change: float | None = Field(
        None, description="200-day average change.", alias="twoHundredDayAverageChange"
    )
    two_hundred_day_average_change_percent: float | None = Field(
        None, description="200-day average change percent.", alias="twoHundredDayAverageChangePercent"
    )
    source_interval: int | None = Field(None, description="Source interval.", alias="sourceInterval")
    exchange_data_delayed_by: int | None = Field(
        None, description="Exchange data delayed by (seconds).", alias="exchangeDataDelayedBy"
    )
    average_analyst_rating: str | None = Field(
        None, description="Average analyst rating.", alias="averageAnalystRating"
    )
    crypto_tradeable: bool | None = Field(None, description="Is crypto tradeable.", alias="cryptoTradeable")
    display_name: str | None = Field(None, description="Display name.", alias="displayName")
    trailing_peg_ratio: float | None = Field(None, description="Trailing PEG ratio.", alias="trailingPegRatio")

    @field_validator(
        "ex_dividend_date",
        "last_dividend_date",
        "dividend_date",
        "last_split_date",
        "earnings_timestamp",
        "earnings_timestamp_start",
        "earnings_timestamp_end",
        "earnings_call_timestamp_start",
        "earnings_call_timestamp_end",
        "last_fiscal_year_end",
        "next_fiscal_year_end",
        mode="before",
    )
    @classmethod
    def _convert_to_datetime(cls, v):
        """Convert Unix timestamp (int/str) to datetime, or pass through if already datetime/None."""
        if v is None or isinstance(v, datetime):
            return v
        try:
            ts = int(float(v))
            return datetime.fromtimestamp(ts)
        except Exception:
            return None


class StockDividends(BaseModel):
    """Dividend payment for a ticker."""

    date_: datetime = Field(..., description="Date of the dividend payment.", alias="Date")
    dividend: float = Field(..., description="Dividend amount.", alias="Dividends")

    @field_validator("date_", mode="before")
    def parse_date(cls, value) -> date:
        """Validator to parse date from timestamp to date."""
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        return value


class StockHistory(BaseModel):
    """Schema for historical ticker data (OHLCV, splits, dividends)."""

    date: datetime = Field(..., description="Date of record", alias="Date")
    open: float = Field(..., description="Opening price", alias="Open")
    high: float = Field(..., description="Highest price", alias="High")
    low: float = Field(..., description="Lowest price", alias="Low")
    close: float = Field(..., description="Closing price", alias="Close")
    volume: int = Field(..., description="Volume traded", alias="Volume")
    dividends: float | None = Field(None, description="Dividends paid", alias="Dividends")
    stock_splits: float | None = Field(None, alias="Stock Splits", description="Stock splits")


class StockInfo_v2(BaseModel):
    """Schema for general stock information."""

    symbol: str | None = Field(None, description="Ticker symbol", alias="symbol")
    short_name: str | None = Field(None, description="Short name of the company", alias="shortName")
    long_name: str | None = Field(None, description="Long name of the company", alias="longName")
    sector: str | None = Field(None, description="Sector of the company", alias="sector")
    industry: str | None = Field(None, description="Industry of the company", alias="industry")
    market_cap: int | None = Field(None, description="Market capitalization", alias="marketCap")
    current_price: float | None = Field(None, description="Current trading price", alias="currentPrice")
    previous_close: float | None = Field(None, description="Previous closing price", alias="previousClose")
    open: float | None = Field(None, description="Opening price", alias="open")
    day_low: float | None = Field(None, description="Lowest price of the day", alias="dayLow")
    day_high: float | None = Field(None, description="Highest price of the day", alias="dayHigh")
    volume: int | None = Field(None, description="Trading volume", alias="volume")
    average_volume: int | None = Field(None, description="Average trading volume", alias="averageVolume")
    beta: float | None = Field(None, description="Beta value", alias="beta")
    trailing_pe: float | None = Field(None, description="Trailing P/E ratio", alias="trailingPE")
    forward_pe: float | None = Field(None, description="Forward P/E ratio", alias="forwardPE")
    dividend_yield: float | None = Field(None, description="Dividend yield", alias="dividendYield")
    payout_ratio: float | None = Field(None, description="Payout ratio", alias="payoutRatio")
    fifty_two_week_low: float | None = Field(None, description="52-week low price", alias="fiftyTwoWeekLow")
    fifty_two_week_high: float | None = Field(None, description="52-week high price", alias="fiftyTwoWeekHigh")
    price_to_book: float | None = Field(None, description="Price to book ratio", alias="priceToBook")
    debt_to_equity: float | None = Field(None, description="Debt to equity ratio", alias="debtToEquity")
    return_on_equity: float | None = Field(None, description="Return on equity", alias="returnOnEquity")
    return_on_assets: float | None = Field(None, description="Return on assets", alias="returnOnAssets")
    free_cashflow: float | None = Field(None, description="Free cash flow", alias="freeCashflow")
    operating_cashflow: float | None = Field(None, description="Operating cash flow", alias="operatingCashflow")
    website: str | None = Field(None, description="Company website", alias="website")
    country: str | None = Field(None, description="Country of headquarters", alias="country")
    city: str | None = Field(None, description="City of headquarters", alias="city")
    phone: str | None = Field(None, description="Contact phone number", alias="phone")
    full_time_employees: int | None = Field(
        None, description="Number of full-time employees", alias="fullTimeEmployees"
    )
    long_business_summary: str | None = Field(None, description="Long business summary", alias="longBusinessSummary")
    ex_dividend_date: datetime | None = Field(None, description="Ex-dividend date as datetime", alias="exDividendDate")

    @field_validator("ex_dividend_date", mode="before")
    @classmethod
    def convert_ex_dividend_date(cls, v):
        """Convert exDividendDate from Unix timestamp (int/str) to datetime, or pass through if already datetime/None."""
        if v is None or isinstance(v, datetime):
            return v
        try:
            # Accept int, float, or string representations of Unix timestamp
            ts = int(float(v))
            return datetime.fromtimestamp(ts)
        except Exception:
            return None


class StockSplit(BaseModel):
    """Stock split event for a ticker."""

    date: datetime = Field(..., description="Date of the stock split.", alias="date")
    stock_splits: float = Field(..., description="Stock split", alias="stock_splits")


class CorporateActions(BaseModel):
    """Actions for a ticker."""

    date: datetime = Field(..., description="Date of the action.", alias="Date")
    dividend: float | None = Field(None, description="Dividend amount.", alias="Dividends")
    stock_splits: float | None = Field(None, description="Stock split amount.", alias="Stock Splits")


class NewsItem(BaseModel):
    """News item for a stock ticker."""

    id: str = Field(..., description="Unique identifier for the news item.", alias="id")
    content: dict = Field(..., description="Content of the news item.", alias="content")


class FinancialSummary(BaseModel):
    """Selected profitability, liquidity and cash-flow metrics."""

    total_revenue: int | None = Field(None, alias="totalRevenue", description="Total revenue.")
    revenue_growth: float | None = Field(None, alias="revenueGrowth", description="Revenue growth.")
    gross_profits: int | None = Field(None, alias="grossProfits", description="Gross profits.")
    gross_margins: float | None = Field(None, alias="grossMargins", description="Gross margins.")
    operating_margins: float | None = Field(None, alias="operatingMargins", description="Operating margins.")
    profit_margins: float | None = Field(None, alias="profitMargins", description="Profit margins.")
    operating_cashflow: int | None = Field(None, alias="operatingCashflow", description="Operating cash flow.")
    free_cashflow: int | None = Field(None, alias="freeCashflow", description="Free cash flow.")
    total_cash: int | None = Field(None, alias="totalCash", description="Total cash.")
    total_debt: int | None = Field(None, alias="totalDebt", description="Total debt.")
    total_cash_per_share: float | None = Field(None, alias="totalCashPerShare", description="Total cash per share.")
    earnings_growth: float | None = Field(None, alias="earningsGrowth", description="Earnings growth.")
    current_ratio: float | None = Field(None, alias="currentRatio", description="Current ratio.")
    quick_ratio: float | None = Field(None, alias="quickRatio", description="Quick ratio.")
    return_on_assets: float | None = Field(None, alias="returnOnAssets", description="Return on assets.")
    return_on_equity: float | None = Field(None, alias="returnOnEquity", description="Return on equity.")
    debt_to_equity: float | None = Field(None, alias="debtToEquity", description="Debt to equity ratio.")


class RiskMetrics(BaseModel):
    """Governance and audit risk scores (1 = lowest risk, 10 = highest)."""

    audit_risk: int | None = Field(None, alias="auditRisk", description="Audit risk score.")
    board_risk: int | None = Field(None, alias="boardRisk", description="Board risk score.")
    compensation_risk: int | None = Field(None, alias="compensationRisk", description="Compensation risk score.")
    overall_risk: int | None = Field(None, alias="overallRisk", description="Overall risk score.")
    share_holder_rights_risk: int | None = Field(
        None, alias="shareHolderRightsRisk", description="Shareholder rights risk score."
    )


class DividendSummary(BaseModel):
    """Dividend rates, yields and key dates."""

    dividend_rate: float | None = Field(None, alias="dividendRate", description="Dividend rate.")
    dividend_yield: float | None = Field(None, alias="dividendYield", description="Dividend yield.")
    payout_ratio: float | None = Field(None, alias="payoutRatio", description="Payout ratio.")
    five_year_avg_dividend_yield: float | None = Field(
        None, alias="fiveYearAvgDividendYield", description="Five-year average dividend yield."
    )
    trailing_annual_dividend_rate: float | None = Field(
        None, alias="trailingAnnualDividendRate", description="Trailing annual dividend rate."
    )
    trailing_annual_dividend_yield: float | None = Field(
        None, alias="trailingAnnualDividendYield", description="Trailing annual dividend yield."
    )
    ex_dividend_date: datetime | None = Field(None, alias="exDividendDate", description="Ex-dividend date.")
    last_dividend_date: datetime | None = Field(None, alias="lastDividendDate", description="Last dividend date.")
    last_dividend_value: float | None = Field(None, alias="lastDividendValue", description="Last dividend value.")


class PriceTarget(BaseModel):
    """Analyst price targets and consensus recommendation."""

    target_high_price: float | None = Field(None, alias="targetHighPrice", description="Target high price.")
    target_low_price: float | None = Field(None, alias="targetLowPrice", description="Target low price.")
    target_mean_price: float | None = Field(None, alias="targetMeanPrice", description="Target mean price.")
    target_median_price: float | None = Field(None, alias="targetMedianPrice", description="Target median price.")
    recommendation_mean: float | None = Field(None, alias="recommendationMean", description="Recommendation mean.")
    recommendation_key: str | None = Field(None, alias="recommendationKey", description="Recommendation key.")
    number_of_analyst_opinions: int | None = Field(
        None, alias="numberOfAnalystOpinions", description="Number of analyst opinions."
    )


class QuickTechnicalIndicators(BaseModel):
    """Moving averages and 52-week range."""

    current_price: float | None = Field(None, alias="currentPrice", description="Current price.")
    fifty_day_average: float | None = Field(None, alias="fiftyDayAverage", description="50-day average price.")
    two_hundred_day_average: float | None = Field(
        None, alias="twoHundredDayAverage", description="200-day average price."
    )
    fifty_day_average_change: float | None = Field(
        None, alias="fiftyDayAverageChange", description="50-day average change."
    )
    fifty_day_average_change_percent: float | None = Field(
        None, alias="fiftyDayAverageChangePercent", description="50-day average change percent."
    )
    two_hundred_day_average_change: float | None = Field(
        None, alias="twoHundredDayAverageChange", description="200-day average change."
    )
    two_hundred_day_average_change_percent: float | None = Field(
        None, alias="twoHundredDayAverageChangePercent", description="200-day average change percent."
    )
    fifty_two_week_low: float | None = Field(None, alias="fiftyTwoWeekLow", description="52-week low price.")
    fifty_two_week_high: float | None = Field(None, alias="fiftyTwoWeekHigh", description="52-week high price.")


class ExtendedFinancialSummary(FinancialSummary):
    """Financial summary extended with valuation and share-count metrics."""

    market_cap: int | None = Field(None, alias="marketCap", description="Market capitalization.")
    enterprise_value: int | None = Field(None, alias="enterpriseValue", description="Enterprise value.")
    float_shares: int | None = Field(None, alias="floatShares", description="Float shares.")
    shares_outstanding: int | None = Field(None, alias="sharesOutstanding", description="Shares outstanding.")
    shares_short: int | None = Field(None, alias="sharesShort", description="Shares short.")
    book_value: float | None = Field(None, alias="bookValue", description="Book value.")
    price_to_book: float | None = Field(None, alias="priceToBook", description="Price to book ratio.")


class ValuationMeasuresEntry(BaseModel):
    """Valuation ratios for a single period, from yfinance's Statistics
    page valuation-measures table (added in yfinance 1.3.0).

    Unlike FinancialSummary/ExtendedFinancialSummary, which are a current
    snapshot, this is one entry per historical period so trend can be seen
    across quarters or years - the same metric can differ meaningfully
    between "Current" and even one quarter prior.
    """

    period: str = Field(
        ...,
        description=(
            "'Current' for the latest value, otherwise the period end date as yfinance reports it (e.g. '6/30/2026')."
        ),
        alias="period",
    )
    market_cap: float | None = Field(None, alias="Market Cap", description="Market capitalization.")
    enterprise_value: float | None = Field(None, alias="Enterprise Value", description="Enterprise value.")
    trailing_pe: float | None = Field(None, alias="Trailing P/E", description="Trailing price-to-earnings ratio.")
    forward_pe: float | None = Field(None, alias="Forward P/E", description="Forward price-to-earnings ratio.")
    peg_ratio: float | None = Field(
        None, alias="PEG Ratio (5yr expected)", description="Price/earnings-to-growth ratio (5-year expected)."
    )
    price_to_sales: float | None = Field(None, alias="Price/Sales", description="Price-to-sales ratio.")
    price_to_book: float | None = Field(None, alias="Price/Book", description="Price-to-book ratio.")
    enterprise_value_to_revenue: float | None = Field(
        None, alias="Enterprise Value/Revenue", description="Enterprise value to revenue ratio."
    )
    enterprise_value_to_ebitda: float | None = Field(
        None, alias="Enterprise Value/EBITDA", description="Enterprise value to EBITDA ratio."
    )

    @field_validator(
        "market_cap",
        "enterprise_value",
        "trailing_pe",
        "forward_pe",
        "peg_ratio",
        "price_to_sales",
        "price_to_book",
        "enterprise_value_to_revenue",
        "enterprise_value_to_ebitda",
        mode="before",
    )
    @classmethod
    def _normalize_missing_metric(cls, value: object) -> object:
        """Map a pandas float NaN to None.

        A company without 5-year growth estimates (e.g. GME) legitimately
        has no PEG ratio; yfinance's DataFrame represents that gap as float
        NaN rather than None, and NaN passes float validation unchanged -
        it is a valid float that is just never equal to itself - so it
        would otherwise reach the client as the literal `NaN` in JSON,
        which is invalid per RFC 8259.
        """
        if isinstance(value, float) and value != value:  # NaN is the only float that is != itself
            return None
        return value
