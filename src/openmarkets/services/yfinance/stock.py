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


def get_fast_info_for_ticker(ticker: str) -> StockFastInfo:
    """
    Fetch fast stock info for a given ticker and return as StockFastInfo.
    """
    fast_info = yf.Ticker(ticker).fast_info
    return StockFastInfo(**fast_info)


def get_info_for_ticker(ticker: str) -> StockInfo:
    """
    Fetch detailed stock info for a given ticker and return as StockInfo.
    """
    info = yf.Ticker(ticker).info
    return StockInfo(**info)


def get_history_for_ticker(ticker: str, period: str = "1y", interval: str = "1d") -> list[StockHistory]:
    """
    Fetch historical OHLCV data for a given ticker and return as a list of StockHistory.
    """
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    df.reset_index(inplace=True)
    return [StockHistory(**row.to_dict()) for _, row in df.iterrows()]


def get_dividends_for_ticker(ticker: str) -> list[StockDividends]:
    """
    Fetch dividend history for a given ticker and return as a list of StockDividends.
    """
    dividends = yf.Ticker(ticker).dividends
    return [StockDividends(Date=row[0], Dividends=row[1]) for row in dividends.to_dict().items()]


def get_financial_summary_for_ticker(ticker: str) -> dict:
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


def get_risk_metrics_for_ticker(ticker: str) -> dict:
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


def get_dividend_summary_for_ticker(ticker: str) -> dict:
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


def get_price_target_for_ticker(ticker: str) -> dict:
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


def get_financial_summary_for_ticker_v2(ticker: str) -> dict:
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


def get_quick_technical_indicators_for_ticker(ticker: str) -> dict:
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


def get_splits_for_ticker(ticker: str) -> list[StockSplit]:
    """
    Fetch stock split history for a given ticker and return as a list of StockSplit.
    """
    splits = yf.Ticker(ticker).splits
    return [StockSplit(date=pd.Timestamp(index).to_pydatetime(), stock_splits=value) for index, value in splits.items()]


def get_corporate_actions_for_ticker(ticker: str) -> list[CorporateActions]:
    """
    Fetch corporate actions (splits/dividends) history for a given ticker and return as a list of CorporateActions.
    """
    actions = yf.Ticker(ticker).actions
    return [CorporateActions(**row.to_dict()) for _, row in actions.reset_index().iterrows()]


def get_news_for_ticker(ticker: str) -> list[NewsItem]:
    """
    Fetch news items for a given ticker and return as a list of NewsItem.
    """
    news = yf.Ticker(ticker).news
    return [NewsItem(**item) for item in news]
