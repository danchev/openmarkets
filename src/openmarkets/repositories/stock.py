"""Repository layer for stock data operations.

Fetches stock information, historical prices, dividends, splits, and other
stock-level data from yfinance.
"""

from typing import Protocol

import pandas as pd
import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.core.types import Interval, Period
from openmarkets.schemas.stock import (
    CorporateActions,
    DividendSummary,
    ExtendedFinancialSummary,
    FinancialSummary,
    NewsItem,
    PriceTarget,
    QuickTechnicalIndicators,
    RiskMetrics,
    StockDividends,
    StockFastInfo,
    StockHistory,
    StockInfo,
    StockSplit,
)


class StockRepository(Protocol):
    """Structural type for stock data access.

    Exists so ``StockService`` can be typed against an interface rather
    than the concrete ``YFinanceStockRepository`` - test doubles satisfy
    this by matching method signatures, with no inheritance and no
    ``@abstractmethod`` bodies to keep in sync. The ``I*Repository`` ABCs
    this replaces had exactly one implementation each and were removed as
    767 lines of unused polymorphism; a Protocol restores the type-checked
    substitutability that removal cost, at a fraction of the size.
    """

    def get_fast_info(self, ticker: str, session: Session | None = None) -> StockFastInfo: ...

    def get_info(self, ticker: str, session: Session | None = None) -> StockInfo: ...

    def get_history(
        self, ticker: str, period: Period = "1y", interval: Interval = "1d", session: Session | None = None
    ) -> list[StockHistory]: ...

    def get_dividends(self, ticker: str, session: Session | None = None) -> list[StockDividends]: ...

    def get_financial_summary(self, ticker: str, session: Session | None = None) -> FinancialSummary: ...

    def get_risk_metrics(self, ticker: str, session: Session | None = None) -> RiskMetrics: ...

    def get_dividend_summary(self, ticker: str, session: Session | None = None) -> DividendSummary: ...

    def get_price_target(self, ticker: str, session: Session | None = None) -> PriceTarget: ...

    def get_extended_financial_summary(
        self, ticker: str, session: Session | None = None
    ) -> ExtendedFinancialSummary: ...

    def get_quick_technical_indicators(
        self, ticker: str, session: Session | None = None
    ) -> QuickTechnicalIndicators: ...

    def get_splits(self, ticker: str, session: Session | None = None) -> list[StockSplit]: ...

    def get_corporate_actions(self, ticker: str, session: Session | None = None) -> list[CorporateActions]: ...

    def get_news(self, ticker: str, session: Session | None = None) -> list[NewsItem]: ...


class YFinanceStockRepository:
    """Repository for accessing stock data from yfinance."""

    def get_fast_info(self, ticker: str, session: Session | None = None) -> StockFastInfo:
        """Retrieve fast info for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Fast info data for the stock.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        fast_info = ticker_obj.fast_info
        return StockFastInfo(**fast_info)

    def get_info(self, ticker: str, session: Session | None = None) -> StockInfo:
        """Retrieve detailed info for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Detailed stock information.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        info = ticker_obj.info
        return StockInfo(**info)

    def get_history(
        self, ticker: str, period: Period = "1y", interval: Interval = "1d", session: Session | None = None
    ) -> list[StockHistory]:
        """Retrieve historical price data for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo).
            session: Optional HTTP session for request handling.

        Returns:
            List of historical data points.

        Raises:
            ValueError: If period or interval is invalid.
        """
        if period not in ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"):
            raise ValueError("Invalid period. Must be one of: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.")
        if interval not in ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"):
            raise ValueError(
                "Invalid interval. Must be one of: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo."
            )
        ticker_obj = yf.Ticker(ticker, session=session)
        df: pd.DataFrame = ticker_obj.history(period=period, interval=interval)
        df.reset_index(inplace=True)
        # Normalize column name: yfinance uses "Datetime" for intraday, "Date" for daily+
        if "Datetime" in df.columns:
            df.rename(columns={"Datetime": "Date"}, inplace=True)
        return [StockHistory(**row.to_dict()) for _, row in df.iterrows()]

    def get_dividends(self, ticker: str, session: Session | None = None) -> list[StockDividends]:
        """Retrieve dividend history for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of dividend records.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        dividends = ticker_obj.dividends
        dividend_dict = dividends.to_dict()
        return [StockDividends(Date=row[0], Dividends=row[1]) for row in dividend_dict.items()]

    def get_financial_summary(self, ticker: str, session: Session | None = None) -> FinancialSummary:
        """Retrieve financial summary metrics for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary containing financial summary metrics.
        """
        include_fields: set[str] = {
            "total_revenue",
            "revenue_growth",
            "gross_profits",
            "gross_margins",
            "operating_margins",
            "profit_margins",
            "operating_cashflow",
            "free_cashflow",
            "total_cash",
            "total_debt",
            "total_cash_per_share",
            "earnings_growth",
            "current_ratio",
            "quick_ratio",
            "return_on_assets",
            "return_on_equity",
            "debt_to_equity",
        }
        ticker_obj = yf.Ticker(ticker, session=session)
        data = ticker_obj.info
        stock_info = StockInfo(**data)
        return FinancialSummary.model_validate(stock_info.model_dump(include=include_fields, by_alias=True))

    def get_risk_metrics(self, ticker: str, session: Session | None = None) -> RiskMetrics:
        """Retrieve risk metrics for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary containing risk metrics.
        """
        include_fields: set[str] = {
            "audit_risk",
            "board_risk",
            "compensation_risk",
            "financial_risk",
            "governance_risk",
            "overall_risk",
            "share_holder_rights_risk",
        }
        ticker_obj = yf.Ticker(ticker, session=session)
        data = ticker_obj.info
        stock_info = StockInfo(**data)
        return RiskMetrics.model_validate(stock_info.model_dump(include=include_fields, by_alias=True))

    def get_dividend_summary(self, ticker: str, session: Session | None = None) -> DividendSummary:
        """Retrieve dividend summary for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary containing dividend metrics.
        """
        include_fields: set[str] = {
            "dividend_rate",
            "dividend_yield",
            "payout_ratio",
            "five_year_avg_dividend_yield",
            "trailing_annual_dividend_rate",
            "trailing_annual_dividend_yield",
            "ex_dividend_date",
            "last_dividend_date",
            "last_dividend_value",
        }
        ticker_obj = yf.Ticker(ticker, session=session)
        data = ticker_obj.info
        stock_info = StockInfo(**data)
        return DividendSummary.model_validate(stock_info.model_dump(include=include_fields, by_alias=True))

    def get_price_target(self, ticker: str, session: Session | None = None) -> PriceTarget:
        """Retrieve analyst price targets for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary containing price target data.
        """
        include_fields: set[str] = {
            "target_high_price",
            "target_low_price",
            "target_mean_price",
            "target_median_price",
            "recommendation_mean",
            "recommendation_key",
            "number_of_analyst_opinions",
        }
        ticker_obj = yf.Ticker(ticker, session=session)
        data = ticker_obj.info
        stock_info = StockInfo(**data)
        return PriceTarget.model_validate(stock_info.model_dump(include=include_fields, by_alias=True))

    def get_extended_financial_summary(self, ticker: str, session: Session | None = None) -> ExtendedFinancialSummary:
        """Retrieve financial summary metrics plus valuation and share counts.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary containing extended financial metrics.
        """
        include_fields: set[str] = {
            "market_cap",
            "enterprise_value",
            "float_shares",
            "shares_outstanding",
            "shares_short",
            "book_value",
            "price_to_book",
            "total_revenue",
            "revenue_growth",
            "gross_profits",
            "gross_margins",
            "operating_margins",
            "profit_margins",
            "operating_cashflow",
            "free_cashflow",
            "total_cash",
            "total_debt",
            "total_cash_per_share",
            "earnings_growth",
            "current_ratio",
            "quick_ratio",
            "return_on_assets",
            "return_on_equity",
            "debt_to_equity",
        }
        ticker_obj = yf.Ticker(ticker, session=session)
        data = ticker_obj.info
        stock_info = StockInfo(**data)
        return ExtendedFinancialSummary.model_validate(stock_info.model_dump(include=include_fields, by_alias=True))

    def get_quick_technical_indicators(self, ticker: str, session: Session | None = None) -> QuickTechnicalIndicators:
        """Retrieve quick technical indicators for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary containing technical indicators.
        """
        include_fields: set[str] = {
            "current_price",
            "fifty_day_average",
            "two_hundred_day_average",
            "fifty_day_average_change",
            "fifty_day_average_change_percent",
            "two_hundred_day_average_change",
            "two_hundred_day_average_change_percent",
            "fifty_two_week_low",
            "fifty_two_week_high",
        }
        ticker_obj = yf.Ticker(ticker, session=session)
        data = ticker_obj.info
        stock_info = StockInfo(**data)
        return QuickTechnicalIndicators.model_validate(stock_info.model_dump(include=include_fields, by_alias=True))

    def get_splits(self, ticker: str, session: Session | None = None) -> list[StockSplit]:
        """Retrieve stock split history for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of stock split records.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        splits = ticker_obj.splits
        return [
            StockSplit(date=pd.Timestamp(str(index)).to_pydatetime(), stock_splits=value)
            for index, value in splits.items()
        ]

    def get_corporate_actions(self, ticker: str, session: Session | None = None) -> list[CorporateActions]:
        """Retrieve corporate actions for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of corporate action records.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        actions = ticker_obj.actions
        reset_actions = actions.reset_index()
        return [CorporateActions(**row.to_dict()) for _, row in reset_actions.iterrows()]

    def get_news(self, ticker: str, session: Session | None = None) -> list[NewsItem]:
        """Retrieve news items for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of news items.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        news = ticker_obj.news
        return [NewsItem(**item) for item in news]
