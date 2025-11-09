from typing import Any

from pydantic import BaseModel, Field

from .company import CompanyOfficer


class FundInfo(BaseModel):
    """Schema for fund information, typically from yfinance Ticker.info for funds/ETFs."""

    phone: str | None = None
    longBusinessSummary: str | None = None
    companyOfficers: list[CompanyOfficer] | None = None
    executiveTeam: list[Any] | None = None
    maxAge: int | None = None
    priceHint: int | None = None
    previousClose: float | None = None
    open: float | None = None
    dayLow: float | None = None
    dayHigh: float | None = None
    regularMarketPreviousClose: float | None = None
    regularMarketOpen: float | None = None
    regularMarketDayLow: float | None = None
    regularMarketDayHigh: float | None = None
    trailingPE: float | None = None
    volume: int | None = None
    regularMarketVolume: int | None = None
    averageVolume: int | None = None
    averageVolume10days: int | None = None
    averageDailyVolume10Day: int | None = None
    bid: float | None = None
    ask: float | None = None
    bidSize: int | None = None
    askSize: int | None = None
    yield_: float | None = Field(None, alias="yield", description="Fund yield.")
    totalAssets: float | None = None
    fiftyTwoWeekLow: float | None = None
    fiftyTwoWeekHigh: float | None = None
    allTimeHigh: float | None = None
    allTimeLow: float | None = None
    fiftyDayAverage: float | None = None
    twoHundredDayAverage: float | None = None
    trailingAnnualDividendRate: float | None = None
    trailingAnnualDividendYield: float | None = None
    navPrice: float | None = None
    currency: str | None = None
    tradeable: bool | None = None
    category: str | None = None
    ytdReturn: float | None = None
    beta3Year: float | None = None
    fundFamily: str | None = None
    fundInceptionDate: int | None = None
    legalType: str | None = None
    threeYearAverageReturn: float | None = None
    fiveYearAverageReturn: float | None = None
    quoteType: str | None = None
    symbol: str | None = None
    language: str | None = None
    region: str | None = None
    typeDisp: str | None = None
    quoteSourceName: str | None = None
    triggerable: bool | None = None
    customPriceAlertConfidence: str | None = None
    longName: str | None = None
    shortName: str | None = None
    marketState: str | None = None
    fiftyTwoWeekLowChangePercent: float | None = None
    fiftyTwoWeekRange: str | None = None
    fiftyTwoWeekHighChange: float | None = None
    fiftyTwoWeekHighChangePercent: float | None = None
    fiftyTwoWeekChangePercent: float | None = None
    dividendYield: float | None = None
    trailingThreeMonthReturns: float | None = None
    trailingThreeMonthNavReturns: float | None = None
    netAssets: float | None = None
    epsTrailingTwelveMonths: float | None = None
    bookValue: float | None = None
    fiftyDayAverageChange: float | None = None
    fiftyDayAverageChangePercent: float | None = None
    twoHundredDayAverageChange: float | None = None
    twoHundredDayAverageChangePercent: float | None = None
    netExpenseRatio: float | None = None
    priceToBook: float | None = None
    sourceInterval: int | None = None
    exchangeDataDelayedBy: int | None = None
    cryptoTradeable: bool | None = None
    hasPrePostMarketData: bool | None = None
    firstTradeDateMilliseconds: int | None = None
    postMarketChangePercent: float | None = None
    postMarketPrice: float | None = None
    postMarketChange: float | None = None
    regularMarketChange: float | None = None
    regularMarketDayRange: str | None = None
    fullExchangeName: str | None = None
    financialCurrency: str | None = None
    averageDailyVolume3Month: int | None = None
    fiftyTwoWeekLowChange: float | None = None
    corporateActions: list[Any] | None = None
    postMarketTime: int | None = None
    regularMarketTime: int | None = None
    exchange: str | None = None
    messageBoardId: str | None = None
    exchangeTimezoneName: str | None = None
    exchangeTimezoneShortName: str | None = None
    gmtOffSetMilliseconds: int | None = None
    market: str | None = None
    esgPopulated: bool | None = None
    regularMarketChangePercent: float | None = None
    regularMarketPrice: float | None = None
    trailingPegRatio: float | None = None


class FundEquityHolding(BaseModel):
    """Schema for individual equity holdings within a fund."""

    fund: str | None = Field(None, alias="index")
    price_to_earnings: float | None = Field(None, alias="Price/Earnings")
    price_to_book: float | None = Field(None, alias="Price/Book")
    price_to_sales: float | None = Field(None, alias="Price/Sales")
    price_to_cashflow: float | None = Field(None, alias="Price/Cashflow")
    median_market_cap: float | None = Field(None, alias="Median Market Cap")
    three_year_earnings_growth: float | None = Field(None, alias="3 Year Earnings Growth")

    model_config = {"arbitrary_types_allowed": True}


class FundHoldings(BaseModel):
    """Schema for fund holdings information."""

    equity_holdings: list[FundEquityHolding]
    total_equity_holdings: float | None = None
    total_fixed_income_holdings: float | None = None
    total_other_holdings: float | None = None
    total_holdings: float | None = None


class FundBondHolding(BaseModel):
    """Schema for individual bond holdings within a fund."""

    fund: str | None = Field(None, alias="index")
    duration: float | None = Field(None, alias="Duration")
    maturity: float | None = Field(None, alias="Maturity")
    credit_quality: float | None = Field(None, alias="Credit Quality")


class FundAssetClassHolding(BaseModel):
    """Schema for individual asset class holdings within a fund."""

    cashPosition: float | None = Field(None, description="Cash Position")
    stockPosition: float | None = Field(None, description="Stock Position")
    bondPosition: float | None = Field(None, description="Bond Position")
    preferredPosition: float | None = Field(None, description="Preferred Position")
    convertiblePosition: float | None = Field(None, description="Convertible Position")
    otherPosition: float | None = Field(None, description="Other Position")


class FundTopHolding(BaseModel):
    """Schema for top holdings within a fund."""

    Symbol: str = Field(..., description="Ticker symbol of the holding.")
    Name: str = Field(..., description="Name of the holding.")
    Holding_Percent: float = Field(
        ..., description="Percentage of the fund's total holdings represented by this holding.", alias="Holding Percent"
    )


class FundSectorWeighting(BaseModel):
    """Schema for sector weightings within a fund."""

    realestate: float | None = Field(None, description="Real Estate")
    customer_ciclical: float | None = Field(None, description="Consumer Cyclical")
    basic_materials: float | None = Field(None, description="Basic Materials")
    consumer_defensive: float | None = Field(None, description="Consumer Defensive")
    utilities: float | None = Field(None, description="Utilities")
    energy: float | None = Field(None, description="Energy")
    communication_services: float | None = Field(None, description="Communication Services")
    financial_services: float | None = Field(None, description="Financial Services")
    industrials: float | None = Field(None, description="Industrials")
    technology: float | None = Field(None, description="Technology")
    healthcare: float | None = Field(None, description="Healthcare")


class FundOperations(BaseModel):
    index: str | None = Field(None, description="Index or fund identifier.")
    annual_report_expense_ratio: float | None = Field(
        None, description="Annual report expense ratio of the fund.", alias="Annual Report Expense Ratio"
    )
    annual_holdings_turnover: float | None = Field(
        None, description="Annual holdings turnover of the fund.", alias="Annual Holdings Turnover"
    )
    total_net_assets: float | None = Field(None, description="Total net assets of the fund.", alias="Total Net Assets")


class FundOverview(BaseModel):
    categoryName: str | None = Field(None, description="Category name of the fund.")
    family: str | None = Field(None, description="Fund family.")
    legalType: str | None = Field(None, description="Legal type of the fund.")
