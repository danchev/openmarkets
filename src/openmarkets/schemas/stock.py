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
from typing import Any, List, Optional

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
    marketCap: Optional[float] = Field(None, description="Market capitalization.")
    open: float = Field(..., description="Opening price.")
    previousClose: float = Field(..., description="Previous closing price.")
    quoteType: str = Field(..., description="Type of quote (e.g., equity, ETF).")
    regularMarketPreviousClose: float = Field(..., description="Regular market previous close.")
    shares: Optional[int] = Field(None, description="Number of shares outstanding.")
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

    address1: Optional[str] = Field(None, description="Primary address line of the company.")
    city: Optional[str] = Field(None, description="City of the company's headquarters.")
    state: Optional[str] = Field(None, description="State or province of the company's headquarters.")
    zip: Optional[str] = Field(None, description="Postal code of the company's headquarters.")
    country: Optional[str] = Field(None, description="Country of the company's headquarters.")
    phone: Optional[str] = Field(None, description="Contact phone number.")
    website: Optional[str] = Field(None, description="Company website URL.")
    industry: Optional[str] = Field(None, description="Industry classification.")
    industryKey: Optional[str] = Field(None, description="Industry key.")
    industryDisp: Optional[str] = Field(None, description="Industry display name.")
    sector: Optional[str] = Field(None, description="Sector classification.")
    sectorKey: Optional[str] = Field(None, description="Sector key.")
    sectorDisp: Optional[str] = Field(None, description="Sector display name.")
    longBusinessSummary: Optional[str] = Field(None, description="Extended business description.")
    fullTimeEmployees: Optional[int] = Field(None, description="Number of full-time employees.")
    companyOfficers: Optional[List[CompanyOfficer]] = Field(None, description="List of company officers.")
    auditRisk: Optional[int] = Field(None, description="Audit risk score.")
    boardRisk: Optional[int] = Field(None, description="Board risk score.")
    compensationRisk: Optional[int] = Field(None, description="Compensation risk score.")
    shareHolderRightsRisk: Optional[int] = Field(None, description="Shareholder rights risk score.")
    overallRisk: Optional[int] = Field(None, description="Overall risk score.")
    governanceEpochDate: Optional[int] = Field(None, description="Governance epoch date (timestamp).")
    compensationAsOfEpochDate: Optional[int] = Field(None, description="Compensation as of epoch date (timestamp).")
    irWebsite: Optional[str] = Field(None, description="Investor relations website.")
    executiveTeam: Optional[List[Any]] = Field(None, description="List of executive team members.")
    maxAge: Optional[int] = Field(None, description="Maximum age of the data.")
    priceHint: Optional[int] = Field(None, description="Price hint for display.")
    previousClose: Optional[float] = Field(None, description="Previous closing price.")
    open: Optional[float] = Field(None, description="Opening price.")
    dayLow: Optional[float] = Field(None, description="Day's low price.")
    dayHigh: Optional[float] = Field(None, description="Day's high price.")
    regularMarketPreviousClose: Optional[float] = Field(None, description="Regular market previous close.")
    regularMarketOpen: Optional[float] = Field(None, description="Regular market opening price.")
    regularMarketDayLow: Optional[float] = Field(None, description="Regular market day's low price.")
    regularMarketDayHigh: Optional[float] = Field(None, description="Regular market day's high price.")
    dividendRate: Optional[float] = Field(None, description="Dividend rate.")
    dividendYield: Optional[float] = Field(None, description="Dividend yield.")
    exDividendDate: Optional[datetime] = Field(None, description="Ex-dividend date.")
    payoutRatio: Optional[float] = Field(None, description="Payout ratio.")
    fiveYearAvgDividendYield: Optional[float] = Field(None, description="Five-year average dividend yield.")
    beta: Optional[float] = Field(None, description="Beta value.")
    trailingPE: Optional[float] = Field(None, description="Trailing P/E ratio.")
    forwardPE: Optional[float] = Field(None, description="Forward P/E ratio.")
    volume: Optional[int] = Field(None, description="Trading volume.")
    regularMarketVolume: Optional[int] = Field(None, description="Regular market trading volume.")
    averageVolume: Optional[int] = Field(None, description="Average trading volume.")
    averageVolume10days: Optional[int] = Field(None, description="10-day average trading volume.")
    averageDailyVolume10Day: Optional[int] = Field(None, description="10-day average daily volume.")
    bid: Optional[float] = Field(None, description="Bid price.")
    ask: Optional[float] = Field(None, description="Ask price.")
    bidSize: Optional[int] = Field(None, description="Bid size.")
    askSize: Optional[int] = Field(None, description="Ask size.")
    marketCap: Optional[int] = Field(None, description="Market capitalization.")
    fiftyTwoWeekLow: Optional[float] = Field(None, description="52-week low price.")
    fiftyTwoWeekHigh: Optional[float] = Field(None, description="52-week high price.")
    allTimeHigh: Optional[float] = Field(None, description="All-time high price.")
    allTimeLow: Optional[float] = Field(None, description="All-time low price.")
    priceToSalesTrailing12Months: Optional[float] = Field(None, description="Price to sales (TTM).")
    fiftyDayAverage: Optional[float] = Field(None, description="50-day average price.")
    twoHundredDayAverage: Optional[float] = Field(None, description="200-day average price.")
    trailingAnnualDividendRate: Optional[float] = Field(None, description="Trailing annual dividend rate.")
    trailingAnnualDividendYield: Optional[float] = Field(None, description="Trailing annual dividend yield.")
    currency: Optional[str] = Field(None, description="Trading currency.")
    tradeable: Optional[bool] = Field(None, description="Is the stock tradeable.")
    enterpriseValue: Optional[int] = Field(None, description="Enterprise value.")
    profitMargins: Optional[float] = Field(None, description="Profit margins.")
    floatShares: Optional[int] = Field(None, description="Float shares.")
    sharesOutstanding: Optional[int] = Field(None, description="Shares outstanding.")
    sharesShort: Optional[int] = Field(None, description="Shares short.")
    sharesShortPriorMonth: Optional[int] = Field(None, description="Shares short prior month.")
    sharesShortPreviousMonthDate: Optional[int] = Field(None, description="Shares short previous month date.")
    dateShortInterest: Optional[int] = Field(None, description="Date of short interest.")
    sharesPercentSharesOut: Optional[float] = Field(None, description="Percent shares out.")
    heldPercentInsiders: Optional[float] = Field(None, description="Percent held by insiders.")
    heldPercentInstitutions: Optional[float] = Field(None, description="Percent held by institutions.")
    shortRatio: Optional[float] = Field(None, description="Short ratio.")
    shortPercentOfFloat: Optional[float] = Field(None, description="Short percent of float.")
    impliedSharesOutstanding: Optional[int] = Field(None, description="Implied shares outstanding.")
    bookValue: Optional[float] = Field(None, description="Book value.")
    priceToBook: Optional[float] = Field(None, description="Price to book ratio.")
    lastFiscalYearEnd: Optional[datetime] = Field(None, description="Last fiscal year end.")
    nextFiscalYearEnd: Optional[datetime] = Field(None, description="Next fiscal year end.")
    mostRecentQuarter: Optional[int] = Field(None, description="Most recent quarter (timestamp).")
    earningsQuarterlyGrowth: Optional[float] = Field(None, description="Earnings quarterly growth.")
    netIncomeToCommon: Optional[int] = Field(None, description="Net income to common.")
    trailingEps: Optional[float] = Field(None, description="Trailing EPS.")
    forwardEps: Optional[float] = Field(None, description="Forward EPS.")
    lastSplitFactor: Optional[str] = Field(None, description="Last split factor.")
    lastSplitDate: Optional[datetime] = Field(None, description="Last split date.")
    enterpriseToRevenue: Optional[float] = Field(None, description="Enterprise to revenue ratio.")
    enterpriseToEbitda: Optional[float] = Field(None, description="Enterprise to EBITDA ratio.")
    FiftyTwoWeekChange: Optional[float] = Field(None, alias="52WeekChange", description="52-week change.")
    SandP52WeekChange: Optional[float] = Field(None, description="S&P 52-week change.")
    lastDividendValue: Optional[float] = Field(None, description="Last dividend value.")
    lastDividendDate: Optional[datetime] = Field(None, description="Last dividend date.")
    quoteType: Optional[str] = Field(None, description="Quote type.")
    currentPrice: Optional[float] = Field(None, description="Current price.")
    targetHighPrice: Optional[float] = Field(None, description="Target high price.")
    targetLowPrice: Optional[float] = Field(None, description="Target low price.")
    targetMeanPrice: Optional[float] = Field(None, description="Target mean price.")
    targetMedianPrice: Optional[float] = Field(None, description="Target median price.")
    recommendationMean: Optional[float] = Field(None, description="Recommendation mean.")
    recommendationKey: Optional[str] = Field(None, description="Recommendation key.")
    numberOfAnalystOpinions: Optional[int] = Field(None, description="Number of analyst opinions.")
    totalCash: Optional[int] = Field(None, description="Total cash.")
    totalCashPerShare: Optional[float] = Field(None, description="Total cash per share.")
    ebitda: Optional[int] = Field(None, description="EBITDA.")
    totalDebt: Optional[int] = Field(None, description="Total debt.")
    quickRatio: Optional[float] = Field(None, description="Quick ratio.")
    currentRatio: Optional[float] = Field(None, description="Current ratio.")
    totalRevenue: Optional[int] = Field(None, description="Total revenue.")
    debtToEquity: Optional[float] = Field(None, description="Debt to equity ratio.")
    revenuePerShare: Optional[float] = Field(None, description="Revenue per share.")
    returnOnAssets: Optional[float] = Field(None, description="Return on assets.")
    returnOnEquity: Optional[float] = Field(None, description="Return on equity.")
    grossProfits: Optional[int] = Field(None, description="Gross profits.")
    freeCashflow: Optional[int] = Field(None, description="Free cash flow.")
    operatingCashflow: Optional[int] = Field(None, description="Operating cash flow.")
    earningsGrowth: Optional[float] = Field(None, description="Earnings growth.")
    revenueGrowth: Optional[float] = Field(None, description="Revenue growth.")
    grossMargins: Optional[float] = Field(None, description="Gross margins.")
    ebitdaMargins: Optional[float] = Field(None, description="EBITDA margins.")
    operatingMargins: Optional[float] = Field(None, description="Operating margins.")
    financialCurrency: Optional[str] = Field(None, description="Financial reporting currency.")
    symbol: Optional[str] = Field(None, description="Ticker symbol.")
    language: Optional[str] = Field(None, description="Reporting language.")
    region: Optional[str] = Field(None, description="Region.")
    typeDisp: Optional[str] = Field(None, description="Type display name.")
    quoteSourceName: Optional[str] = Field(None, description="Quote source name.")
    triggerable: Optional[bool] = Field(None, description="Is triggerable.")
    customPriceAlertConfidence: Optional[str] = Field(None, description="Custom price alert confidence.")
    regularMarketChangePercent: Optional[float] = Field(None, description="Regular market change percent.")
    regularMarketPrice: Optional[float] = Field(None, description="Regular market price.")
    shortName: Optional[str] = Field(None, description="Short name.")
    longName: Optional[str] = Field(None, description="Long name.")
    hasPrePostMarketData: Optional[bool] = Field(None, description="Has pre/post market data.")
    firstTradeDateMilliseconds: Optional[int] = Field(None, description="First trade date in milliseconds.")
    postMarketChangePercent: Optional[float] = Field(None, description="Post-market change percent.")
    postMarketPrice: Optional[float] = Field(None, description="Post-market price.")
    postMarketChange: Optional[float] = Field(None, description="Post-market change.")
    regularMarketChange: Optional[float] = Field(None, description="Regular market change.")
    regularMarketDayRange: Optional[str] = Field(None, description="Regular market day range.")
    fullExchangeName: Optional[str] = Field(None, description="Full exchange name.")
    averageDailyVolume3Month: Optional[int] = Field(None, description="3-month average daily volume.")
    fiftyTwoWeekLowChange: Optional[float] = Field(None, description="52-week low change.")
    fiftyTwoWeekLowChangePercent: Optional[float] = Field(None, description="52-week low change percent.")
    fiftyTwoWeekRange: Optional[str] = Field(None, description="52-week range.")
    fiftyTwoWeekHighChange: Optional[float] = Field(None, description="52-week high change.")
    fiftyTwoWeekHighChangePercent: Optional[float] = Field(None, description="52-week high change percent.")
    fiftyTwoWeekChangePercent: Optional[float] = Field(None, description="52-week change percent.")
    marketState: Optional[str] = Field(None, description="Market state.")
    corporateActions: Optional[List[Any]] = Field(None, description="Corporate actions.")
    postMarketTime: Optional[int] = Field(None, description="Post-market time (timestamp).")
    regularMarketTime: Optional[int] = Field(None, description="Regular market time (timestamp).")
    exchange: Optional[str] = Field(None, description="Exchange code.")
    messageBoardId: Optional[str] = Field(None, description="Message board ID.")
    exchangeTimezoneName: Optional[str] = Field(None, description="Exchange timezone name.")
    exchangeTimezoneShortName: Optional[str] = Field(None, description="Exchange timezone short name.")
    gmtOffSetMilliseconds: Optional[int] = Field(None, description="GMT offset in milliseconds.")
    market: Optional[str] = Field(None, description="Market name.")
    esgPopulated: Optional[bool] = Field(None, description="ESG data populated.")
    dividendDate: Optional[datetime] = Field(None, description="Dividend date.")
    earningsTimestamp: Optional[datetime] = Field(None, description="Earnings timestamp.")
    earningsTimestampStart: Optional[datetime] = Field(None, description="Earnings timestamp start.")
    earningsTimestampEnd: Optional[datetime] = Field(None, description="Earnings timestamp end.")
    earningsCallTimestampStart: Optional[datetime] = Field(None, description="Earnings call timestamp start.")
    earningsCallTimestampEnd: Optional[datetime] = Field(None, description="Earnings call timestamp end.")
    isEarningsDateEstimate: Optional[bool] = Field(None, description="Is earnings date an estimate.")
    epsTrailingTwelveMonths: Optional[float] = Field(None, description="EPS trailing twelve months.")
    epsForward: Optional[float] = Field(None, description="EPS forward.")
    epsCurrentYear: Optional[float] = Field(None, description="EPS current year.")
    priceEpsCurrentYear: Optional[float] = Field(None, description="Price/EPS current year.")
    fiftyDayAverageChange: Optional[float] = Field(None, description="50-day average change.")
    fiftyDayAverageChangePercent: Optional[float] = Field(None, description="50-day average change percent.")
    twoHundredDayAverageChange: Optional[float] = Field(None, description="200-day average change.")
    twoHundredDayAverageChangePercent: Optional[float] = Field(None, description="200-day average change percent.")
    sourceInterval: Optional[int] = Field(None, description="Source interval.")
    exchangeDataDelayedBy: Optional[int] = Field(None, description="Exchange data delayed by (seconds).")
    averageAnalystRating: Optional[str] = Field(None, description="Average analyst rating.")
    cryptoTradeable: Optional[bool] = Field(None, description="Is crypto tradeable.")
    displayName: Optional[str] = Field(None, description="Display name.")
    trailingPegRatio: Optional[float] = Field(None, description="Trailing PEG ratio.")

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
    Dividends: Optional[float] = Field(None, description="Dividends paid")
    Stock_Splits: Optional[float] = Field(None, alias="Stock Splits", description="Stock splits")


class StockInfo_v2(BaseModel):
    """Schema for general stock information."""

    symbol: Optional[str] = Field(None, description="Ticker symbol")
    shortName: Optional[str] = Field(None, description="Short name of the company")
    longName: Optional[str] = Field(None, description="Long name of the company")
    sector: Optional[str] = Field(None, description="Sector of the company")
    industry: Optional[str] = Field(None, description="Industry of the company")
    marketCap: Optional[int] = Field(None, description="Market capitalization")
    currentPrice: Optional[float] = Field(None, description="Current trading price")
    previousClose: Optional[float] = Field(None, description="Previous closing price")
    open: Optional[float] = Field(None, description="Opening price")
    dayLow: Optional[float] = Field(None, description="Lowest price of the day")
    dayHigh: Optional[float] = Field(None, description="Highest price of the day")
    volume: Optional[int] = Field(None, description="Trading volume")
    averageVolume: Optional[int] = Field(None, description="Average trading volume")
    beta: Optional[float] = Field(None, description="Beta value")
    trailingPE: Optional[float] = Field(None, description="Trailing P/E ratio")
    forwardPE: Optional[float] = Field(None, description="Forward P/E ratio")
    dividendYield: Optional[float] = Field(None, description="Dividend yield")
    payoutRatio: Optional[float] = Field(None, description="Payout ratio")
    fiftyTwoWeekLow: Optional[float] = Field(None, description="52-week low price")
    fiftyTwoWeekHigh: Optional[float] = Field(None, description="52-week high price")
    priceToBook: Optional[float] = Field(None, description="Price to book ratio")
    debtToEquity: Optional[float] = Field(None, description="Debt to equity ratio")
    returnOnEquity: Optional[float] = Field(None, description="Return on equity")
    returnOnAssets: Optional[float] = Field(None, description="Return on assets")
    freeCashflow: Optional[float] = Field(None, description="Free cash flow")
    operatingCashflow: Optional[float] = Field(None, description="Operating cash flow")
    website: Optional[str] = Field(None, description="Company website")
    country: Optional[str] = Field(None, description="Country of headquarters")
    city: Optional[str] = Field(None, description="City of headquarters")
    phone: Optional[str] = Field(None, description="Contact phone number")
    fullTimeEmployees: Optional[int] = Field(None, description="Number of full-time employees")
    longBusinessSummary: Optional[str] = Field(None, description="Long business summary")
    exDividendDate: Optional[datetime] = Field(None, description="Ex-dividend date as datetime")

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
    dividend: Optional[float] = Field(None, description="Dividend amount.", alias="Dividends")
    stock_splits: Optional[float] = Field(None, description="Stock split amount.", alias="Stock Splits")


class NewsItem(BaseModel):
    """News item for a stock ticker."""

    id: str = Field(..., description="Unique identifier for the news item.")
    content: dict = Field(..., description="Content of the news item.")
