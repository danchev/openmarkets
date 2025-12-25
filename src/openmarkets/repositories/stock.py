from abc import ABC, abstractmethod

import pandas as pd
import yfinance as yf
from curl_cffi.requests import Session

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
    def get_fast_info(self, ticker: str, session: Session | None = None) -> StockFastInfo:
        pass

    @abstractmethod
    def get_info(self, ticker: str, session: Session | None = None) -> StockInfo:
        pass

    @abstractmethod
    def get_history(
        self, ticker: str, period: str = "1y", interval: str = "1d", session: Session | None = None
    ) -> list[StockHistory]:
        pass

    @abstractmethod
    def get_dividends(self, ticker: str, session: Session | None = None) -> list[StockDividends]:
        pass

    @abstractmethod
    def get_financial_summary(self, ticker: str, session: Session | None = None) -> dict:
        pass

    @abstractmethod
    def get_risk_metrics(self, ticker: str, session: Session | None = None) -> dict:
        pass

    @abstractmethod
    def get_dividend_summary(self, ticker: str, session: Session | None = None) -> dict:
        pass

    @abstractmethod
    def get_price_target(self, ticker: str, session: Session | None = None) -> dict:
        pass

    @abstractmethod
    def get_financial_summary_v2(self, ticker: str, session: Session | None = None) -> dict:
        pass

    @abstractmethod
    def get_quick_technical_indicators(self, ticker: str, session: Session | None = None) -> dict:
        pass

    @abstractmethod
    def get_splits(self, ticker: str, session: Session | None = None) -> list[StockSplit]:
        pass

    @abstractmethod
    def get_corporate_actions(self, ticker: str, session: Session | None = None) -> list[CorporateActions]:
        pass

    @abstractmethod
    def get_news(self, ticker: str, session: Session | None = None) -> list[NewsItem]:
        pass


class YFinanceStockRepository(IStockRepository):
    def get_fast_info(self, ticker: str, session: Session | None = None) -> StockFastInfo:
        fast_info = yf.Ticker(ticker, session=session).fast_info
        return StockFastInfo(**fast_info)

    def get_info(self, ticker: str, session: Session | None = None) -> StockInfo:
        info = yf.Ticker(ticker, session=session).info
        return StockInfo(**info)

    def get_history(
        self, ticker: str, period: str = "1y", interval: str = "1d", session: Session | None = None
    ) -> list[StockHistory]:
        if period not in ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"):
            raise ValueError("Invalid period. Must be one of: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.")
        if interval not in ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"):
            raise ValueError(
                "Invalid interval. Must be one of: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo."
            )
        df: pd.DataFrame = yf.Ticker(ticker, session=session).history(period=period, interval=interval)
        df.reset_index(inplace=True)
        return [StockHistory(**row.to_dict()) for _, row in df.iterrows()]

    def get_dividends(self, ticker: str, session: Session | None = None) -> list[StockDividends]:
        dividends = yf.Ticker(ticker, session=session).dividends
        return [StockDividends(Date=row[0], Dividends=row[1]) for row in dividends.to_dict().items()]

    def get_financial_summary(self, ticker: str, session: Session | None = None) -> dict:
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
        data = yf.Ticker(ticker, session=session).info
        return StockInfo(**data).model_dump(include=include_fields)

    def get_risk_metrics(self, ticker: str, session: Session | None = None) -> dict:
        include_fields: set[str] = {
            "auditRisk",
            "boardRisk",
            "compensationRisk",
            "financialRisk",
            "governanceRisk",
            "overallRisk",
            "shareHolderRightsRisk",
        }
        data = yf.Ticker(ticker, session=session).info
        return StockInfo(**data).model_dump(include=include_fields)

    def get_dividend_summary(self, ticker: str, session: Session | None = None) -> dict:
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
        data = yf.Ticker(ticker, session=session).info
        return StockInfo(**data).model_dump(include=include_fields)

    def get_price_target(self, ticker: str, session: Session | None = None) -> dict:
        include_fields: set[str] = {
            "targetHighPrice",
            "targetLowPrice",
            "targetMeanPrice",
            "targetMedianPrice",
            "recommendationMean",
            "recommendationKey",
            "numberOfAnalystOpinions",
        }
        data = yf.Ticker(ticker, session=session).info
        return StockInfo(**data).model_dump(include=include_fields)

    def get_financial_summary_v2(self, ticker: str, session: Session | None = None) -> dict:
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
        data = yf.Ticker(ticker, session=session).info
        return StockInfo(**data).model_dump(include=include_fields)

    def get_quick_technical_indicators(self, ticker: str, session: Session | None = None) -> dict:
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
        data = yf.Ticker(ticker, session=session).info
        return StockInfo(**data).model_dump(include=include_fields)

    def get_splits(self, ticker: str, session: Session | None = None) -> list[StockSplit]:
        splits = yf.Ticker(ticker, session=session).splits
        return [
            StockSplit(date=pd.Timestamp(str(index)).to_pydatetime(), stock_splits=value)
            for index, value in splits.items()
        ]

    def get_corporate_actions(self, ticker: str, session: Session | None = None) -> list[CorporateActions]:
        actions = yf.Ticker(ticker, session=session).actions
        return [CorporateActions(**row.to_dict()) for _, row in actions.reset_index().iterrows()]

    def get_news(self, ticker: str, session: Session | None = None) -> list[NewsItem]:
        news = yf.Ticker(ticker, session=session).news
        return [NewsItem(**item) for item in news]
