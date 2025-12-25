from typing import Any

from pydantic import BaseModel, Field

from .company import CompanyOfficer


class FundInfo(BaseModel):
    """Schema for fund information, typically from yfinance Ticker.info for funds/ETFs."""

    phone: str | None = Field(None, description="Contact phone number.", alias="phone")
    long_business_summary: str | None = Field(
        None, description="Long business summary of the fund.", alias="longBusinessSummary"
    )
    company_officers: list[CompanyOfficer] | None = Field(
        None, description="List of company officers.", alias="companyOfficers"
    )
    executive_team: list[Any] | None = Field(None, description="Executive team members.", alias="executiveTeam")
    max_age: int | None = Field(None, description="Maximum age of the data in seconds.", alias="maxAge")
    price_hint: int | None = Field(None, description="Price hint for formatting.", alias="priceHint")
    previous_close: float | None = Field(None, description="Previous day's closing price.", alias="previousClose")
    open: float | None = Field(None, description="Opening price.", alias="open")
    day_low: float | None = Field(None, description="Day's lowest price.", alias="dayLow")
    day_high: float | None = Field(None, description="Day's highest price.", alias="dayHigh")
    regular_market_previous_close: float | None = Field(
        None, description="Regular market previous close price.", alias="regularMarketPreviousClose"
    )
    regular_market_open: float | None = Field(
        None, description="Regular market opening price.", alias="regularMarketOpen"
    )
    regular_market_day_low: float | None = Field(
        None, description="Regular market day's lowest price.", alias="regularMarketDayLow"
    )
    regular_market_day_high: float | None = Field(
        None, description="Regular market day's highest price.", alias="regularMarketDayHigh"
    )
    trailing_pe: float | None = Field(None, description="Trailing price-to-earnings ratio.", alias="trailingPE")
    volume: int | None = Field(None, description="Trading volume.", alias="volume")
    regular_market_volume: int | None = Field(
        None, description="Regular market trading volume.", alias="regularMarketVolume"
    )
    average_volume: int | None = Field(None, description="Average trading volume.", alias="averageVolume")
    average_volume_10days: int | None = Field(
        None, description="Average trading volume over 10 days.", alias="averageVolume10days"
    )
    average_daily_volume_10_day: int | None = Field(
        None, description="Average daily volume over 10 days.", alias="averageDailyVolume10Day"
    )
    bid: float | None = Field(None, description="Current bid price.", alias="bid")
    ask: float | None = Field(None, description="Current ask price.", alias="ask")
    bid_size: int | None = Field(None, description="Size of current bid.", alias="bidSize")
    ask_size: int | None = Field(None, description="Size of current ask.", alias="askSize")
    yield_: float | None = Field(None, description="Fund yield.", alias="yield")
    total_assets: float | None = Field(None, description="Total assets under management.", alias="totalAssets")
    fifty_two_week_low: float | None = Field(None, description="52-week low price.", alias="fiftyTwoWeekLow")
    fifty_two_week_high: float | None = Field(None, description="52-week high price.", alias="fiftyTwoWeekHigh")
    all_time_high: float | None = Field(None, description="All-time high price.", alias="allTimeHigh")
    all_time_low: float | None = Field(None, description="All-time low price.", alias="allTimeLow")
    fifty_day_average: float | None = Field(None, description="50-day moving average.", alias="fiftyDayAverage")
    two_hundred_day_average: float | None = Field(
        None, description="200-day moving average.", alias="twoHundredDayAverage"
    )
    trailing_annual_dividend_rate: float | None = Field(
        None, description="Trailing annual dividend rate.", alias="trailingAnnualDividendRate"
    )
    trailing_annual_dividend_yield: float | None = Field(
        None, description="Trailing annual dividend yield.", alias="trailingAnnualDividendYield"
    )
    nav_price: float | None = Field(None, description="Net asset value price.", alias="navPrice")
    currency: str | None = Field(None, description="Currency of the fund.", alias="currency")
    tradeable: bool | None = Field(None, description="Whether the fund is tradeable.", alias="tradeable")
    category: str | None = Field(None, description="Fund category.", alias="category")
    ytd_return: float | None = Field(None, description="Year-to-date return.", alias="ytdReturn")
    beta_3_year: float | None = Field(None, description="3-year beta.", alias="beta3Year")
    fund_family: str | None = Field(None, description="Fund family name.", alias="fundFamily")
    fund_inception_date: int | None = Field(
        None, description="Fund inception date as Unix timestamp.", alias="fundInceptionDate"
    )
    legal_type: str | None = Field(None, description="Legal type of the fund.", alias="legalType")
    three_year_average_return: float | None = Field(
        None, description="3-year average return.", alias="threeYearAverageReturn"
    )
    five_year_average_return: float | None = Field(
        None, description="5-year average return.", alias="fiveYearAverageReturn"
    )
    quote_type: str | None = Field(None, description="Type of quote.", alias="quoteType")
    symbol: str | None = Field(None, description="Ticker symbol.", alias="symbol")
    language: str | None = Field(None, description="Language code.", alias="language")
    region: str | None = Field(None, description="Region code.", alias="region")
    type_disp: str | None = Field(None, description="Display type.", alias="typeDisp")
    quote_source_name: str | None = Field(None, description="Quote source name.", alias="quoteSourceName")
    triggerable: bool | None = Field(None, description="Whether price alerts can be triggered.", alias="triggerable")
    custom_price_alert_confidence: str | None = Field(
        None, description="Custom price alert confidence level.", alias="customPriceAlertConfidence"
    )
    long_name: str | None = Field(None, description="Long name of the fund.", alias="longName")
    short_name: str | None = Field(None, description="Short name of the fund.", alias="shortName")
    market_state: str | None = Field(
        None, description="Current market state (e.g., PRE, REGULAR, POST, CLOSED).", alias="marketState"
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
    fifty_two_week_change_percent: float | None = Field(
        None, description="52-week percentage change.", alias="fiftyTwoWeekChangePercent"
    )
    dividend_yield: float | None = Field(None, description="Dividend yield.", alias="dividendYield")
    trailing_three_month_returns: float | None = Field(
        None, description="Trailing 3-month returns.", alias="trailingThreeMonthReturns"
    )
    trailing_three_month_nav_returns: float | None = Field(
        None, description="Trailing 3-month NAV returns.", alias="trailingThreeMonthNavReturns"
    )
    net_assets: float | None = Field(None, description="Net assets of the fund.", alias="netAssets")
    eps_trailing_twelve_months: float | None = Field(
        None, description="Earnings per share over trailing twelve months.", alias="epsTrailingTwelveMonths"
    )
    book_value: float | None = Field(None, description="Book value per share.", alias="bookValue")
    fifty_day_average_change: float | None = Field(
        None, description="Change from 50-day average.", alias="fiftyDayAverageChange"
    )
    fifty_day_average_change_percent: float | None = Field(
        None, description="Percentage change from 50-day average.", alias="fiftyDayAverageChangePercent"
    )
    two_hundred_day_average_change: float | None = Field(
        None, description="Change from 200-day average.", alias="twoHundredDayAverageChange"
    )
    two_hundred_day_average_change_percent: float | None = Field(
        None, description="Percentage change from 200-day average.", alias="twoHundredDayAverageChangePercent"
    )
    net_expense_ratio: float | None = Field(None, description="Net expense ratio.", alias="netExpenseRatio")
    price_to_book: float | None = Field(None, description="Price-to-book ratio.", alias="priceToBook")
    source_interval: int | None = Field(None, description="Source data interval in seconds.", alias="sourceInterval")
    exchange_data_delayed_by: int | None = Field(
        None, description="Exchange data delay in minutes.", alias="exchangeDataDelayedBy"
    )
    crypto_tradeable: bool | None = Field(
        None, description="Whether crypto trading is available.", alias="cryptoTradeable"
    )
    has_pre_post_market_data: bool | None = Field(
        None, description="Whether pre/post-market data is available.", alias="hasPrePostMarketData"
    )
    first_trade_date_milliseconds: int | None = Field(
        None, description="First trade date in milliseconds since epoch.", alias="firstTradeDateMilliseconds"
    )
    post_market_change_percent: float | None = Field(
        None, description="Post-market percentage change.", alias="postMarketChangePercent"
    )
    post_market_price: float | None = Field(None, description="Post-market price.", alias="postMarketPrice")
    post_market_change: float | None = Field(None, description="Post-market price change.", alias="postMarketChange")
    regular_market_change: float | None = Field(
        None, description="Regular market price change.", alias="regularMarketChange"
    )
    regular_market_day_range: str | None = Field(
        None, description="Regular market day price range.", alias="regularMarketDayRange"
    )
    full_exchange_name: str | None = Field(None, description="Full name of the exchange.", alias="fullExchangeName")
    financial_currency: str | None = Field(
        None, description="Currency used for financial statements.", alias="financialCurrency"
    )
    average_daily_volume_3_month: int | None = Field(
        None, description="Average daily volume over 3 months.", alias="averageDailyVolume3Month"
    )
    fifty_two_week_low_change: float | None = Field(
        None, description="Change from 52-week low.", alias="fiftyTwoWeekLowChange"
    )
    corporate_actions: list[Any] | None = Field(
        None, description="List of corporate actions.", alias="corporateActions"
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
    esg_populated: bool | None = Field(None, description="Whether ESG data is populated.", alias="esgPopulated")
    regular_market_change_percent: float | None = Field(
        None, description="Regular market percentage change.", alias="regularMarketChangePercent"
    )
    regular_market_price: float | None = Field(None, description="Regular market price.", alias="regularMarketPrice")
    trailing_peg_ratio: float | None = Field(
        None, description="Trailing price/earnings to growth ratio.", alias="trailingPegRatio"
    )


class FundEquityHolding(BaseModel):
    """Schema for individual equity holdings within a fund."""

    fund: str | None = Field(None, description="Fund identifier.", alias="index")
    price_to_earnings: float | None = Field(
        None, description="Price-to-earnings ratio of holdings.", alias="Price/Earnings"
    )
    price_to_book: float | None = Field(None, description="Price-to-book ratio of holdings.", alias="Price/Book")
    price_to_sales: float | None = Field(None, description="Price-to-sales ratio of holdings.", alias="Price/Sales")
    price_to_cashflow: float | None = Field(
        None, description="Price-to-cashflow ratio of holdings.", alias="Price/Cashflow"
    )
    median_market_cap: float | None = Field(
        None, description="Median market capitalization of holdings.", alias="Median Market Cap"
    )
    three_year_earnings_growth: float | None = Field(
        None, description="3-year earnings growth rate of holdings.", alias="3 Year Earnings Growth"
    )

    model_config = {"arbitrary_types_allowed": True}


class FundHoldings(BaseModel):
    """Schema for fund holdings information."""

    equity_holdings: list[FundEquityHolding] = Field(..., description="List of equity holdings.")
    total_equity_holdings: float | None = Field(
        None, description="Total value of equity holdings.", alias="total_equity_holdings"
    )
    total_fixed_income_holdings: float | None = Field(
        None, description="Total value of fixed income holdings.", alias="total_fixed_income_holdings"
    )
    total_other_holdings: float | None = Field(
        None, description="Total value of other holdings.", alias="total_other_holdings"
    )
    total_holdings: float | None = Field(None, description="Total value of all holdings.", alias="total_holdings")


class FundBondHolding(BaseModel):
    """Schema for individual bond holdings within a fund."""

    fund: str | None = Field(None, description="Fund identifier.", alias="index")
    duration: float | None = Field(None, description="Average duration of bond holdings in years.", alias="Duration")
    maturity: float | None = Field(None, description="Average maturity of bond holdings in years.", alias="Maturity")
    credit_quality: float | None = Field(
        None, description="Credit quality rating of bond holdings.", alias="Credit Quality"
    )


class FundAssetClassHolding(BaseModel):
    """Schema for individual asset class holdings within a fund."""

    cash_position: float | None = Field(None, description="Cash Position", alias="cashPosition")
    stock_position: float | None = Field(None, description="Stock Position", alias="stockPosition")
    bond_position: float | None = Field(None, description="Bond Position", alias="bondPosition")
    preferred_position: float | None = Field(None, description="Preferred Position", alias="preferredPosition")
    convertible_position: float | None = Field(None, description="Convertible Position", alias="convertiblePosition")
    other_position: float | None = Field(None, description="Other Position", alias="otherPosition")


class FundTopHolding(BaseModel):
    """Schema for top holdings within a fund."""

    symbol: str = Field(..., description="Ticker symbol of the holding.", alias="Symbol")
    name: str = Field(..., description="Name of the holding.", alias="Name")
    holding_percent: float = Field(
        ..., description="Percentage of the fund's total holdings represented by this holding.", alias="Holding Percent"
    )


class FundSectorWeighting(BaseModel):
    """Schema for sector weightings within a fund."""

    real_estate: float | None = Field(None, description="Real Estate", alias="realestate")
    consumer_cyclical: float | None = Field(None, description="Consumer Cyclical", alias="customer_ciclical")
    basic_materials: float | None = Field(None, description="Basic Materials", alias="basic_materials")
    consumer_defensive: float | None = Field(None, description="Consumer Defensive", alias="consumer_defensive")
    utilities: float | None = Field(None, description="Utilities", alias="utilities")
    energy: float | None = Field(None, description="Energy", alias="energy")
    communication_services: float | None = Field(
        None, description="Communication Services", alias="communication_services"
    )
    financial_services: float | None = Field(None, description="Financial Services", alias="financial_services")
    industrials: float | None = Field(None, description="Industrials", alias="industrials")
    technology: float | None = Field(None, description="Technology", alias="technology")
    healthcare: float | None = Field(None, description="Healthcare", alias="healthcare")


class FundOperations(BaseModel):
    index: str | None = Field(None, description="Index or fund identifier.", alias="index")
    annual_report_expense_ratio: float | None = Field(
        None, description="Annual report expense ratio of the fund.", alias="Annual Report Expense Ratio"
    )
    annual_holdings_turnover: float | None = Field(
        None, description="Annual holdings turnover of the fund.", alias="Annual Holdings Turnover"
    )
    total_net_assets: float | None = Field(None, description="Total net assets of the fund.", alias="Total Net Assets")


class FundOverview(BaseModel):
    category_name: str | None = Field(None, description="Category name of the fund.", alias="categoryName")
    family: str | None = Field(None, description="Fund family.", alias="family")
    legal_type: str | None = Field(None, description="Legal type of the fund.", alias="legalType")
