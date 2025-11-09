import pandas as pd
import yfinance as yf

from openmarkets.schemas.stock import (
    CorporateActions,
    NewsItem,
    StockDividends,
    StockFastInfo,
    StockHistory,
    StockInfo,
    StockSplit,
)


def fetch_fast_info(ticker: str) -> StockFastInfo:
    """
    Fetch fast stock info for a given ticker and return as StockFastInfo.
    """
    fast_info = yf.Ticker(ticker).fast_info
    return StockFastInfo(**fast_info)


def fetch_info(ticker: str) -> StockInfo:
    """
    Fetch detailed stock info for a given ticker and return as StockInfo.
    """
    info = yf.Ticker(ticker).info
    return StockInfo(**info)


def fetch_history(ticker: str, period: str = "1y", interval: str = "1d") -> list[StockHistory]:
    """
    Fetch historical OHLCV data for a given ticker and return as a list of StockHistory.
    """
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    df.reset_index(inplace=True)
    return [StockHistory(**row.to_dict()) for _, row in df.iterrows()]


def fetch_dividends(ticker: str) -> list[StockDividends]:
    """
    Fetch dividend history for a given ticker and return as a list of StockDividends.
    """
    dividends = yf.Ticker(ticker).dividends
    return [StockDividends(Date=row[0], Dividends=row[1]) for row in dividends.to_dict().items()]


def fetch_financial_summary(ticker: str) -> dict:
    """
    Fetch financial summary data for a given ticker and return as a dictionary.
    """
    include_fields = {
        "totalRevenue",
        "revenueGrowth",
        "grossProfits",
        "grossMargins",
        "operatingMargins",
        "profitMargins",
        "operatingCashflow",
        "freeCashflow",
        "totalCash",
        "totalDebt",
        "totalCashPerShare",
        "earningsGrowth",
        "currentRatio",
        "quickRatio",
        "returnOnAssets",
        "returnOnEquity",
        "debtToEquity",
    }
    data = yf.Ticker(ticker).info
    return StockInfo(**data).model_dump(include=include_fields)


def fetch_risk_metrics(ticker: str) -> dict:
    """
    Fetch risk metrics data for a given ticker and return as a dictionary.
    """
    include_fields = {
        "auditRisk",
        "boardRisk",
        "compensationRisk",
        "financialRisk",
        "governanceRisk",
        "overallRisk",
        "shareHolderRightsRisk",
    }
    data = yf.Ticker(ticker).info
    return StockInfo(**data).model_dump(include=include_fields)


def fetch_dividend_summary(ticker: str) -> dict:
    """
    Fetch dividend summary data for a given ticker and return as a dictionary.
    """
    include_fields = {
        "dividendRate",
        "dividendYield",
        "payoutRatio",
        "fiveYearAvgDividendYield",
        "trailingAnnualDividendRate",
        "trailingAnnualDividendYield",
        "exDividendDate",
        "lastDividendDate",
        "lastDividendValue",
    }
    data = yf.Ticker(ticker).info
    return StockInfo(**data).model_dump(include=include_fields)


def fetch_price_target(ticker: str) -> dict:
    """
    Fetch analyst price target data for a given ticker and return as a dictionary.
    """
    include_fields = {
        "targetHighPrice",
        "targetLowPrice",
        "targetMeanPrice",
        "targetMedianPrice",
        "recommendationMean",
        "recommendationKey",
        "numberOfAnalystOpinions",
    }
    data = yf.Ticker(ticker).info
    return StockInfo(**data).model_dump(include=include_fields)


def fetch_financial_summary_v2(ticker: str) -> dict:
    """
    Fetch financial summary data for a given ticker and return as a dictionary.
    """
    include_fields = {
        "marketCap",
        "enterpriseValue",
        "floatShares",
        "sharesOutstanding",
        "sharesShort",
        "bookValue",
        "priceToBook",
        "totalRevenue",
        "revenueGrowth",
        "grossProfits",
        "grossMargins",
        "operatingMargins",
        "profitMargins",
        "operatingCashflow",
        "freeCashflow",
        "totalCash",
        "totalDebt",
        "totalCashPerShare",
        "earningsGrowth",
        "currentRatio",
        "quickRatio",
        "returnOnAssets",
        "returnOnEquity",
        "debtToEquity",
    }
    data = yf.Ticker(ticker).info
    return StockInfo(**data).model_dump(include=include_fields)


def fetch_quick_technical_indicators(ticker: str) -> dict:
    """
    Fetch technical indicators for a given ticker and return as a dictionary.
    """
    include_fields = {
        "currentPrice",
        "fiftyDayAverage",
        "twoHundredDayAverage",
        "fiftyDayAverageChange",
        "fiftyDayAverageChangePercent",
        "twoHundredDayAverageChange",
        "twoHundredDayAverageChangePercent",
        "fiftyTwoWeekLow",
        "fiftyTwoWeekHigh",
    }
    data = yf.Ticker(ticker).info
    return StockInfo(**data).model_dump(include=include_fields)


def fetch_splits(ticker: str) -> list[StockSplit]:
    """
    Fetch stock split history for a given ticker and return as a list of StockSplit.
    """
    splits = yf.Ticker(ticker).splits
    return [
        StockSplit(date=pd.Timestamp(str(index)).to_pydatetime(), stock_splits=value) for index, value in splits.items()
    ]


def fetch_corporate_actions(ticker: str) -> list[CorporateActions]:
    """
    Fetch corporate actions (splits/dividends) history for a given ticker and return as a list of CorporateActions.
    """
    actions = yf.Ticker(ticker).actions
    return [CorporateActions(**row.to_dict()) for _, row in actions.reset_index().iterrows()]


def fetch_news(ticker: str) -> list[NewsItem]:
    """
    Fetch news items for a given ticker and return as a list of NewsItem.
    """
    news = yf.Ticker(ticker).news
    return [NewsItem(**item) for item in news]
