from abc import ABC, abstractmethod

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


class IStockRepository(ABC):
    """Repository interface for stock data access."""

    @abstractmethod
    def fetch_fast_info(self, ticker: str) -> StockFastInfo:
        pass

    @abstractmethod
    def fetch_info(self, ticker: str) -> StockInfo:
        pass

    @abstractmethod
    def fetch_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> list[StockHistory]:
        pass

    @abstractmethod
    def fetch_dividends(self, ticker: str) -> list[StockDividends]:
        pass

    @abstractmethod
    def fetch_financial_summary(self, ticker: str) -> dict:
        pass

    @abstractmethod
    def fetch_risk_metrics(self, ticker: str) -> dict:
        pass

    @abstractmethod
    def fetch_dividend_summary(self, ticker: str) -> dict:
        pass

    @abstractmethod
    def fetch_price_target(self, ticker: str) -> dict:
        pass

    @abstractmethod
    def fetch_financial_summary_v2(self, ticker: str) -> dict:
        pass

    @abstractmethod
    def fetch_quick_technical_indicators(self, ticker: str) -> dict:
        pass

    @abstractmethod
    def fetch_splits(self, ticker: str) -> list[StockSplit]:
        pass

    @abstractmethod
    def fetch_corporate_actions(self, ticker: str) -> list[CorporateActions]:
        pass

    @abstractmethod
    def fetch_news(self, ticker: str) -> list[NewsItem]:
        pass


class YFinanceStockRepository(IStockRepository):
    def fetch_fast_info(self, ticker: str) -> StockFastInfo:
        fast_info = yf.Ticker(ticker).fast_info
        return StockFastInfo(**fast_info)

    def fetch_info(self, ticker: str) -> StockInfo:
        info = yf.Ticker(ticker).info
        return StockInfo(**info)

    def fetch_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> list[StockHistory]:
        df: pd.DataFrame = yf.Ticker(ticker).history(period=period, interval=interval)
        df.reset_index(inplace=True)
        return [StockHistory(**row.to_dict()) for _, row in df.iterrows()]

    def fetch_dividends(self, ticker: str) -> list[StockDividends]:
        dividends = yf.Ticker(ticker).dividends
        return [StockDividends(Date=row[0], Dividends=row[1]) for row in dividends.to_dict().items()]

    def fetch_financial_summary(self, ticker: str) -> dict:
        include_fields: set[str] = {
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

    def fetch_risk_metrics(self, ticker: str) -> dict:
        include_fields: set[str] = {
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

    def fetch_dividend_summary(self, ticker: str) -> dict:
        include_fields: set[str] = {
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

    def fetch_price_target(self, ticker: str) -> dict:
        include_fields: set[str] = {
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

    def fetch_financial_summary_v2(self, ticker: str) -> dict:
        include_fields: set[str] = {
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

    def fetch_quick_technical_indicators(self, ticker: str) -> dict:
        include_fields: set[str] = {
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

    def fetch_splits(self, ticker: str) -> list[StockSplit]:
        splits = yf.Ticker(ticker).splits
        return [
            StockSplit(date=pd.Timestamp(str(index)).to_pydatetime(), stock_splits=value)
            for index, value in splits.items()
        ]

    def fetch_corporate_actions(self, ticker: str) -> list[CorporateActions]:
        actions = yf.Ticker(ticker).actions
        return [CorporateActions(**row.to_dict()) for _, row in actions.reset_index().iterrows()]

    def fetch_news(self, ticker: str) -> list[NewsItem]:
        news = yf.Ticker(ticker).news
        return [NewsItem(**item) for item in news]
