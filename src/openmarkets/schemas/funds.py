from typing import Any, List, Optional

from pydantic import BaseModel, Field

from .company import CompanyOfficer


class FundInfo(BaseModel):
    """Schema for fund information, typically from yfinance Ticker.info for funds/ETFs."""

    phone: Optional[str] = None
    longBusinessSummary: Optional[str] = None
    companyOfficers: Optional[List[CompanyOfficer]] = None
    executiveTeam: Optional[List[Any]] = None
    maxAge: Optional[int] = None
    priceHint: Optional[int] = None
    previousClose: Optional[float] = None
    open: Optional[float] = None
    dayLow: Optional[float] = None
    dayHigh: Optional[float] = None
    regularMarketPreviousClose: Optional[float] = None
    regularMarketOpen: Optional[float] = None
    regularMarketDayLow: Optional[float] = None
    regularMarketDayHigh: Optional[float] = None
    trailingPE: Optional[float] = None
    volume: Optional[int] = None
    regularMarketVolume: Optional[int] = None
    averageVolume: Optional[int] = None
    averageVolume10days: Optional[int] = None
    averageDailyVolume10Day: Optional[int] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    bidSize: Optional[int] = None
    askSize: Optional[int] = None
    yield_: Optional[float] = Field(None, alias="yield", description="Fund yield.")
    totalAssets: Optional[float] = None
    fiftyTwoWeekLow: Optional[float] = None
    fiftyTwoWeekHigh: Optional[float] = None
    allTimeHigh: Optional[float] = None
    allTimeLow: Optional[float] = None
    fiftyDayAverage: Optional[float] = None
    twoHundredDayAverage: Optional[float] = None
    trailingAnnualDividendRate: Optional[float] = None
    trailingAnnualDividendYield: Optional[float] = None
    navPrice: Optional[float] = None
    currency: Optional[str] = None
    tradeable: Optional[bool] = None
    category: Optional[str] = None
    ytdReturn: Optional[float] = None
    beta3Year: Optional[float] = None
    fundFamily: Optional[str] = None
    fundInceptionDate: Optional[int] = None
    legalType: Optional[str] = None
    threeYearAverageReturn: Optional[float] = None
    fiveYearAverageReturn: Optional[float] = None
    quoteType: Optional[str] = None
    symbol: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None
    typeDisp: Optional[str] = None
    quoteSourceName: Optional[str] = None
    triggerable: Optional[bool] = None
    customPriceAlertConfidence: Optional[str] = None
    longName: Optional[str] = None
    shortName: Optional[str] = None
    marketState: Optional[str] = None
    fiftyTwoWeekLowChangePercent: Optional[float] = None
    fiftyTwoWeekRange: Optional[str] = None
    fiftyTwoWeekHighChange: Optional[float] = None
    fiftyTwoWeekHighChangePercent: Optional[float] = None
    fiftyTwoWeekChangePercent: Optional[float] = None
    dividendYield: Optional[float] = None
    trailingThreeMonthReturns: Optional[float] = None
    trailingThreeMonthNavReturns: Optional[float] = None
    netAssets: Optional[float] = None
    epsTrailingTwelveMonths: Optional[float] = None
    bookValue: Optional[float] = None
    fiftyDayAverageChange: Optional[float] = None
    fiftyDayAverageChangePercent: Optional[float] = None
    twoHundredDayAverageChange: Optional[float] = None
    twoHundredDayAverageChangePercent: Optional[float] = None
    netExpenseRatio: Optional[float] = None
    priceToBook: Optional[float] = None
    sourceInterval: Optional[int] = None
    exchangeDataDelayedBy: Optional[int] = None
    cryptoTradeable: Optional[bool] = None
    hasPrePostMarketData: Optional[bool] = None
    firstTradeDateMilliseconds: Optional[int] = None
    postMarketChangePercent: Optional[float] = None
    postMarketPrice: Optional[float] = None
    postMarketChange: Optional[float] = None
    regularMarketChange: Optional[float] = None
    regularMarketDayRange: Optional[str] = None
    fullExchangeName: Optional[str] = None
    financialCurrency: Optional[str] = None
    averageDailyVolume3Month: Optional[int] = None
    fiftyTwoWeekLowChange: Optional[float] = None
    corporateActions: Optional[List[Any]] = None
    postMarketTime: Optional[int] = None
    regularMarketTime: Optional[int] = None
    exchange: Optional[str] = None
    messageBoardId: Optional[str] = None
    exchangeTimezoneName: Optional[str] = None
    exchangeTimezoneShortName: Optional[str] = None
    gmtOffSetMilliseconds: Optional[int] = None
    market: Optional[str] = None
    esgPopulated: Optional[bool] = None
    regularMarketChangePercent: Optional[float] = None
    regularMarketPrice: Optional[float] = None
    trailingPegRatio: Optional[float] = None


class FundEquityHolding(BaseModel):
    """Schema for individual equity holdings within a fund."""

    fund: Optional[str] = Field(None, alias="index")
    price_to_earnings: Optional[float] = Field(None, alias="Price/Earnings")
    price_to_book: Optional[float] = Field(None, alias="Price/Book")
    price_to_sales: Optional[float] = Field(None, alias="Price/Sales")
    price_to_cashflow: Optional[float] = Field(None, alias="Price/Cashflow")
    median_market_cap: Optional[float] = Field(None, alias="Median Market Cap")
    three_year_earnings_growth: Optional[float] = Field(None, alias="3 Year Earnings Growth")

    model_config = {"arbitrary_types_allowed": True}


class FundHoldings(BaseModel):
    """Schema for fund holdings information."""

    equity_holdings: List[FundEquityHolding]
    total_equity_holdings: Optional[float] = None
    total_fixed_income_holdings: Optional[float] = None
    total_other_holdings: Optional[float] = None
    total_holdings: Optional[float] = None


class FundBondHolding(BaseModel):
    """Schema for individual bond holdings within a fund."""

    fund: Optional[str] = Field(None, alias="index")
    duration: Optional[float] = Field(None, alias="Duration")
    maturity: Optional[float] = Field(None, alias="Maturity")
    credit_quality: Optional[float] = Field(None, alias="Credit Quality")


class FundAssetClassHolding(BaseModel):
    """Schema for individual asset class holdings within a fund."""

    cashPosition: Optional[float] = Field(None, description="Cash Position")
    stockPosition: Optional[float] = Field(None, description="Stock Position")
    bondPosition: Optional[float] = Field(None, description="Bond Position")
    preferredPosition: Optional[float] = Field(None, description="Preferred Position")
    convertiblePosition: Optional[float] = Field(None, description="Convertible Position")
    otherPosition: Optional[float] = Field(None, description="Other Position")


class FundTopHolding(BaseModel):
    """Schema for top holdings within a fund."""

    Symbol: str = Field(..., description="Ticker symbol of the holding.")
    Name: str = Field(..., description="Name of the holding.")
    Holding_Percent: float = Field(
        ..., description="Percentage of the fund's total holdings represented by this holding.", alias="Holding Percent"
    )


class FundSectorWeighting(BaseModel):
    """Schema for sector weightings within a fund."""

    realestate: Optional[float] = Field(None, description="Real Estate")
    customer_ciclical: Optional[float] = Field(None, description="Consumer Cyclical")
    basic_materials: Optional[float] = Field(None, description="Basic Materials")
    consumer_defensive: Optional[float] = Field(None, description="Consumer Defensive")
    utilities: Optional[float] = Field(None, description="Utilities")
    energy: Optional[float] = Field(None, description="Energy")
    communication_services: Optional[float] = Field(None, description="Communication Services")
    financial_services: Optional[float] = Field(None, description="Financial Services")
    industrials: Optional[float] = Field(None, description="Industrials")
    technology: Optional[float] = Field(None, description="Technology")
    healthcare: Optional[float] = Field(None, description="Healthcare")


class FundOperations(BaseModel):
    index: Optional[str] = Field(None, description="Index or fund identifier.")
    annual_report_expense_ratio: Optional[float] = Field(
        None, description="Annual report expense ratio of the fund.", alias="Annual Report Expense Ratio"
    )
    annual_holdings_turnover: Optional[float] = Field(
        None, description="Annual holdings turnover of the fund.", alias="Annual Holdings Turnover"
    )
    total_net_assets: Optional[float] = Field(
        None, description="Total net assets of the fund.", alias="Total Net Assets"
    )


class FundOverview(BaseModel):
    categoryName: Optional[str] = Field(None, description="Category name of the fund.")
    family: Optional[str] = Field(None, description="Fund family.")
    legalType: Optional[str] = Field(None, description="Legal type of the fund.")
