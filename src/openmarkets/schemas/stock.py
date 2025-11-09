"""
Ticker Stock Schemas:
    dividends
    splits
    actions
    capital_gains
    shares_full
    info
    fast_info
    news
"""

from datetime import date, datetime
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field, field_validator

from openmarkets.schemas.company import CompanyOfficer


class StockFastInfo(BaseModel):
    """Fast info snapshot for a stock ticker, typically from yfinance or similar APIs."""

    currency: str = Field(..., description="Currency of the ticker.")
    dayHigh: float = Field(..., description="Day's high price.")
    dayLow: float = Field(..., description="Day's low price.")
    exchange: str = Field(..., description="Exchange where the ticker is listed.")
    fiftyDayAverage: float = Field(..., description="50-day average price.")
    lastPrice: float = Field(..., description="Last traded price.")
    lastVolume: int = Field(..., description="Last traded volume.")
    marketCap: float | None = Field(None, description="Market capitalization.")
    open: float = Field(..., description="Opening price.")
    previousClose: float = Field(..., description="Previous closing price.")
    quoteType: str = Field(..., description="Type of quote (e.g., equity, ETF).")
    regularMarketPreviousClose: float = Field(..., description="Regular market previous close.")
    shares: int | None = Field(None, description="Number of shares outstanding.")
    tenDayAverageVolume: int = Field(..., description="10-day average volume.")
    threeMonthAverageVolume: int = Field(..., description="3-month average volume.")
    timezone: str = Field(..., description="Timezone of the exchange.")
    twoHundredDayAverage: float = Field(..., description="200-day average price.")
    yearChange: float = Field(..., description="Change over the past year.")
    yearHigh: float = Field(..., description="52-week high price.")
    yearLow: float = Field(..., description="52-week low price.")


class StockInfo(BaseModel):
    """
    Comprehensive schema for stock information, typically from yfinance Ticker.info.
    """

    address1: str | None = Field(None, description="Primary address line of the company.")
    city: str | None = Field(None, description="City of the company's headquarters.")
    state: str | None = Field(None, description="State or province of the company's headquarters.")
    zip: str | None = Field(None, description="Postal code of the company's headquarters.")
    country: str | None = Field(None, description="Country of the company's headquarters.")
    phone: str | None = Field(None, description="Contact phone number.")
    website: str | None = Field(None, description="Company website URL.")
    industry: str | None = Field(None, description="Industry classification.")
    industryKey: str | None = Field(None, description="Industry key.")
    industryDisp: str | None = Field(None, description="Industry display name.")
    sector: str | None = Field(None, description="Sector classification.")
    sectorKey: str | None = Field(None, description="Sector key.")
    sectorDisp: str | None = Field(None, description="Sector display name.")
    longBusinessSummary: str | None = Field(None, description="Extended business description.")
    fullTimeEmployees: int | None = Field(None, description="Number of full-time employees.")
    companyOfficers: list[CompanyOfficer] | None = Field(None, description="List of company officers.")
    auditRisk: int | None = Field(None, description="Audit risk score.")
    boardRisk: int | None = Field(None, description="Board risk score.")
    compensationRisk: int | None = Field(None, description="Compensation risk score.")
    shareHolderRightsRisk: int | None = Field(None, description="Shareholder rights risk score.")
    overallRisk: int | None = Field(None, description="Overall risk score.")
    governanceEpochDate: int | None = Field(None, description="Governance epoch date (timestamp).")
    compensationAsOfEpochDate: int | None = Field(None, description="Compensation as of epoch date (timestamp).")
    irWebsite: str | None = Field(None, description="Investor relations website.")
    executiveTeam: list[Any] | None = Field(None, description="List of executive team members.")
    maxAge: int | None = Field(None, description="Maximum age of the data.")
    priceHint: int | None = Field(None, description="Price hint for display.")
    previousClose: float | None = Field(None, description="Previous closing price.")
    open: float | None = Field(None, description="Opening price.")
    dayLow: float | None = Field(None, description="Day's low price.")
    dayHigh: float | None = Field(None, description="Day's high price.")
    regularMarketPreviousClose: float | None = Field(None, description="Regular market previous close.")
    regularMarketOpen: float | None = Field(None, description="Regular market opening price.")
    regularMarketDayLow: float | None = Field(None, description="Regular market day's low price.")
    regularMarketDayHigh: float | None = Field(None, description="Regular market day's high price.")
    dividendRate: float | None = Field(None, description="Dividend rate.")
    dividendYield: float | None = Field(None, description="Dividend yield.")
    exDividendDate: datetime | None = Field(None, description="Ex-dividend date.")
    payoutRatio: float | None = Field(None, description="Payout ratio.")
    fiveYearAvgDividendYield: float | None = Field(None, description="Five-year average dividend yield.")
    beta: float | None = Field(None, description="Beta value.")
    trailingPE: float | None = Field(None, description="Trailing P/E ratio.")
    forwardPE: float | None = Field(None, description="Forward P/E ratio.")
    volume: int | None = Field(None, description="Trading volume.")
    regularMarketVolume: int | None = Field(None, description="Regular market trading volume.")
    averageVolume: int | None = Field(None, description="Average trading volume.")
    averageVolume10days: int | None = Field(None, description="10-day average trading volume.")
    averageDailyVolume10Day: int | None = Field(None, description="10-day average daily volume.")
    bid: float | None = Field(None, description="Bid price.")
    ask: float | None = Field(None, description="Ask price.")
    bidSize: int | None = Field(None, description="Bid size.")
    askSize: int | None = Field(None, description="Ask size.")
    marketCap: int | None = Field(None, description="Market capitalization.")
    fiftyTwoWeekLow: float | None = Field(None, description="52-week low price.")
    fiftyTwoWeekHigh: float | None = Field(None, description="52-week high price.")
    allTimeHigh: float | None = Field(None, description="All-time high price.")
    allTimeLow: float | None = Field(None, description="All-time low price.")
    priceToSalesTrailing12Months: float | None = Field(None, description="Price to sales (TTM).")
    fiftyDayAverage: float | None = Field(None, description="50-day average price.")
    twoHundredDayAverage: float | None = Field(None, description="200-day average price.")
    trailingAnnualDividendRate: float | None = Field(None, description="Trailing annual dividend rate.")
    trailingAnnualDividendYield: float | None = Field(None, description="Trailing annual dividend yield.")
    currency: str | None = Field(None, description="Trading currency.")
    tradeable: bool | None = Field(None, description="Is the stock tradeable.")
    enterpriseValue: int | None = Field(None, description="Enterprise value.")
    profitMargins: float | None = Field(None, description="Profit margins.")
    floatShares: int | None = Field(None, description="Float shares.")
    sharesOutstanding: int | None = Field(None, description="Shares outstanding.")
    sharesShort: int | None = Field(None, description="Shares short.")
    sharesShortPriorMonth: int | None = Field(None, description="Shares short prior month.")
    sharesShortPreviousMonthDate: int | None = Field(None, description="Shares short previous month date.")
    dateShortInterest: int | None = Field(None, description="Date of short interest.")
    sharesPercentSharesOut: float | None = Field(None, description="Percent shares out.")
    heldPercentInsiders: float | None = Field(None, description="Percent held by insiders.")
    heldPercentInstitutions: float | None = Field(None, description="Percent held by institutions.")
    shortRatio: float | None = Field(None, description="Short ratio.")
    shortPercentOfFloat: float | None = Field(None, description="Short percent of float.")
    impliedSharesOutstanding: int | None = Field(None, description="Implied shares outstanding.")
    bookValue: float | None = Field(None, description="Book value.")
    priceToBook: float | None = Field(None, description="Price to book ratio.")
    lastFiscalYearEnd: datetime | None = Field(None, description="Last fiscal year end.")
    nextFiscalYearEnd: datetime | None = Field(None, description="Next fiscal year end.")
    mostRecentQuarter: int | None = Field(None, description="Most recent quarter (timestamp).")
    earningsQuarterlyGrowth: float | None = Field(None, description="Earnings quarterly growth.")
    netIncomeToCommon: int | None = Field(None, description="Net income to common.")
    trailingEps: float | None = Field(None, description="Trailing EPS.")
    forwardEps: float | None = Field(None, description="Forward EPS.")
    lastSplitFactor: str | None = Field(None, description="Last split factor.")
    lastSplitDate: datetime | None = Field(None, description="Last split date.")
    enterpriseToRevenue: float | None = Field(None, description="Enterprise to revenue ratio.")
    enterpriseToEbitda: float | None = Field(None, description="Enterprise to EBITDA ratio.")
    FiftyTwoWeekChange: float | None = Field(None, alias="52WeekChange", description="52-week change.")
    SandP52WeekChange: float | None = Field(None, description="S&P 52-week change.")
    lastDividendValue: float | None = Field(None, description="Last dividend value.")
    lastDividendDate: datetime | None = Field(None, description="Last dividend date.")
    quoteType: str | None = Field(None, description="Quote type.")
    currentPrice: float | None = Field(None, description="Current price.")
    targetHighPrice: float | None = Field(None, description="Target high price.")
    targetLowPrice: float | None = Field(None, description="Target low price.")
    targetMeanPrice: float | None = Field(None, description="Target mean price.")
    targetMedianPrice: float | None = Field(None, description="Target median price.")
    recommendationMean: float | None = Field(None, description="Recommendation mean.")
    recommendationKey: str | None = Field(None, description="Recommendation key.")
    numberOfAnalystOpinions: int | None = Field(None, description="Number of analyst opinions.")
    totalCash: int | None = Field(None, description="Total cash.")
    totalCashPerShare: float | None = Field(None, description="Total cash per share.")
    ebitda: int | None = Field(None, description="EBITDA.")
    totalDebt: int | None = Field(None, description="Total debt.")
    quickRatio: float | None = Field(None, description="Quick ratio.")
    currentRatio: float | None = Field(None, description="Current ratio.")
    totalRevenue: int | None = Field(None, description="Total revenue.")
    debtToEquity: float | None = Field(None, description="Debt to equity ratio.")
    revenuePerShare: float | None = Field(None, description="Revenue per share.")
    returnOnAssets: float | None = Field(None, description="Return on assets.")
    returnOnEquity: float | None = Field(None, description="Return on equity.")
    grossProfits: int | None = Field(None, description="Gross profits.")
    freeCashflow: int | None = Field(None, description="Free cash flow.")
    operatingCashflow: int | None = Field(None, description="Operating cash flow.")
    earningsGrowth: float | None = Field(None, description="Earnings growth.")
    revenueGrowth: float | None = Field(None, description="Revenue growth.")
    grossMargins: float | None = Field(None, description="Gross margins.")
    ebitdaMargins: float | None = Field(None, description="EBITDA margins.")
    operatingMargins: float | None = Field(None, description="Operating margins.")
    financialCurrency: str | None = Field(None, description="Financial reporting currency.")
    symbol: str | None = Field(None, description="Ticker symbol.")
    language: str | None = Field(None, description="Reporting language.")
    region: str | None = Field(None, description="Region.")
    typeDisp: str | None = Field(None, description="Type display name.")
    quoteSourceName: str | None = Field(None, description="Quote source name.")
    triggerable: bool | None = Field(None, description="Is triggerable.")
    customPriceAlertConfidence: str | None = Field(None, description="Custom price alert confidence.")
    regularMarketChangePercent: float | None = Field(None, description="Regular market change percent.")
    regularMarketPrice: float | None = Field(None, description="Regular market price.")
    shortName: str | None = Field(None, description="Short name.")
    longName: str | None = Field(None, description="Long name.")
    hasPrePostMarketData: bool | None = Field(None, description="Has pre/post market data.")
    firstTradeDateMilliseconds: int | None = Field(None, description="First trade date in milliseconds.")
    postMarketChangePercent: float | None = Field(None, description="Post-market change percent.")
    postMarketPrice: float | None = Field(None, description="Post-market price.")
    postMarketChange: float | None = Field(None, description="Post-market change.")
    regularMarketChange: float | None = Field(None, description="Regular market change.")
    regularMarketDayRange: str | None = Field(None, description="Regular market day range.")
    fullExchangeName: str | None = Field(None, description="Full exchange name.")
    averageDailyVolume3Month: int | None = Field(None, description="3-month average daily volume.")
    fiftyTwoWeekLowChange: float | None = Field(None, description="52-week low change.")
    fiftyTwoWeekLowChangePercent: float | None = Field(None, description="52-week low change percent.")
    fiftyTwoWeekRange: str | None = Field(None, description="52-week range.")
    fiftyTwoWeekHighChange: float | None = Field(None, description="52-week high change.")
    fiftyTwoWeekHighChangePercent: float | None = Field(None, description="52-week high change percent.")
    fiftyTwoWeekChangePercent: float | None = Field(None, description="52-week change percent.")
    marketState: str | None = Field(None, description="Market state.")
    corporateActions: list[Any] | None = Field(None, description="Corporate actions.")
    postMarketTime: int | None = Field(None, description="Post-market time (timestamp).")
    regularMarketTime: int | None = Field(None, description="Regular market time (timestamp).")
    exchange: str | None = Field(None, description="Exchange code.")
    messageBoardId: str | None = Field(None, description="Message board ID.")
    exchangeTimezoneName: str | None = Field(None, description="Exchange timezone name.")
    exchangeTimezoneShortName: str | None = Field(None, description="Exchange timezone short name.")
    gmtOffSetMilliseconds: int | None = Field(None, description="GMT offset in milliseconds.")
    market: str | None = Field(None, description="Market name.")
    esgPopulated: bool | None = Field(None, description="ESG data populated.")
    dividendDate: datetime | None = Field(None, description="Dividend date.")
    earningsTimestamp: datetime | None = Field(None, description="Earnings timestamp.")
    earningsTimestampStart: datetime | None = Field(None, description="Earnings timestamp start.")
    earningsTimestampEnd: datetime | None = Field(None, description="Earnings timestamp end.")
    earningsCallTimestampStart: datetime | None = Field(None, description="Earnings call timestamp start.")
    earningsCallTimestampEnd: datetime | None = Field(None, description="Earnings call timestamp end.")
    isEarningsDateEstimate: bool | None = Field(None, description="Is earnings date an estimate.")
    epsTrailingTwelveMonths: float | None = Field(None, description="EPS trailing twelve months.")
    epsForward: float | None = Field(None, description="EPS forward.")
    epsCurrentYear: float | None = Field(None, description="EPS current year.")
    priceEpsCurrentYear: float | None = Field(None, description="Price/EPS current year.")
    fiftyDayAverageChange: float | None = Field(None, description="50-day average change.")
    fiftyDayAverageChangePercent: float | None = Field(None, description="50-day average change percent.")
    twoHundredDayAverageChange: float | None = Field(None, description="200-day average change.")
    twoHundredDayAverageChangePercent: float | None = Field(None, description="200-day average change percent.")
    sourceInterval: int | None = Field(None, description="Source interval.")
    exchangeDataDelayedBy: int | None = Field(None, description="Exchange data delayed by (seconds).")
    averageAnalystRating: str | None = Field(None, description="Average analyst rating.")
    cryptoTradeable: bool | None = Field(None, description="Is crypto tradeable.")
    displayName: str | None = Field(None, description="Display name.")
    trailingPegRatio: float | None = Field(None, description="Trailing PEG ratio.")

    @field_validator(
        "exDividendDate",
        "lastDividendDate",
        "dividendDate",
        "lastSplitDate",
        "earningsTimestamp",
        "earningsTimestampStart",
        "earningsTimestampEnd",
        "earningsCallTimestampStart",
        "earningsCallTimestampEnd",
        "lastFiscalYearEnd",
        "nextFiscalYearEnd",
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

    @field_validator("date_")
    def parse_date(cls, value) -> date:
        """Validator to parse date from timestamp to date."""
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        return value


class StockHistory(BaseModel):
    """Schema for historical ticker data (OHLCV, splits, dividends)."""

    Date: datetime = Field(..., description="Date of record")
    Open: float = Field(..., description="Opening price")
    High: float = Field(..., description="Highest price")
    Low: float = Field(..., description="Lowest price")
    Close: float = Field(..., description="Closing price")
    Volume: int = Field(..., description="Volume traded")
    Dividends: float | None = Field(None, description="Dividends paid")
    Stock_Splits: float | None = Field(None, alias="Stock Splits", description="Stock splits")


class StockInfo_v2(BaseModel):
    """Schema for general stock information."""

    symbol: str | None = Field(None, description="Ticker symbol")
    shortName: str | None = Field(None, description="Short name of the company")
    longName: str | None = Field(None, description="Long name of the company")
    sector: str | None = Field(None, description="Sector of the company")
    industry: str | None = Field(None, description="Industry of the company")
    marketCap: int | None = Field(None, description="Market capitalization")
    currentPrice: float | None = Field(None, description="Current trading price")
    previousClose: float | None = Field(None, description="Previous closing price")
    open: float | None = Field(None, description="Opening price")
    dayLow: float | None = Field(None, description="Lowest price of the day")
    dayHigh: float | None = Field(None, description="Highest price of the day")
    volume: int | None = Field(None, description="Trading volume")
    averageVolume: int | None = Field(None, description="Average trading volume")
    beta: float | None = Field(None, description="Beta value")
    trailingPE: float | None = Field(None, description="Trailing P/E ratio")
    forwardPE: float | None = Field(None, description="Forward P/E ratio")
    dividendYield: float | None = Field(None, description="Dividend yield")
    payoutRatio: float | None = Field(None, description="Payout ratio")
    fiftyTwoWeekLow: float | None = Field(None, description="52-week low price")
    fiftyTwoWeekHigh: float | None = Field(None, description="52-week high price")
    priceToBook: float | None = Field(None, description="Price to book ratio")
    debtToEquity: float | None = Field(None, description="Debt to equity ratio")
    returnOnEquity: float | None = Field(None, description="Return on equity")
    returnOnAssets: float | None = Field(None, description="Return on assets")
    freeCashflow: float | None = Field(None, description="Free cash flow")
    operatingCashflow: float | None = Field(None, description="Operating cash flow")
    website: str | None = Field(None, description="Company website")
    country: str | None = Field(None, description="Country of headquarters")
    city: str | None = Field(None, description="City of headquarters")
    phone: str | None = Field(None, description="Contact phone number")
    fullTimeEmployees: int | None = Field(None, description="Number of full-time employees")
    longBusinessSummary: str | None = Field(None, description="Long business summary")
    exDividendDate: datetime | None = Field(None, description="Ex-dividend date as datetime")

    @field_validator("exDividendDate", mode="before")
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

    date: datetime = Field(..., description="Date of the stock split.")
    stock_splits: float = Field(..., description="Stock split")


class CorporateActions(BaseModel):
    """Actions for a ticker."""

    date: datetime = Field(..., description="Date of the action.", alias="Date")
    dividend: float | None = Field(None, description="Dividend amount.", alias="Dividends")
    stock_splits: float | None = Field(None, description="Stock split amount.", alias="Stock Splits")


class NewsItem(BaseModel):
    """News item for a stock ticker."""

    id: str = Field(..., description="Unique identifier for the news item.")
    content: dict = Field(..., description="Content of the news item.")
