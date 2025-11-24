from typing import Annotated

from openmarkets.repositories.stock import IStockRepository, YFinanceStockRepository
from openmarkets.schemas.stock import (
    CorporateActions,
    NewsItem,
    StockDividends,
    StockFastInfo,
    StockHistory,
    StockInfo,
    StockSplit,
)
from openmarkets.services.utils import ToolRegistrationMixin


class StockService(ToolRegistrationMixin):
    """
    Service layer for stock-related business logic.
    Provides methods to retrieve stock info, history, dividends, financial summaries, risk metrics, technical indicators, splits, corporate actions, and news for a given ticker.
    """

    def __init__(self, repository: IStockRepository | None = None):
        """
        Initialize the StockService with a repository dependency.

        Args:
            repository (IStockRepository): The repository instance for data access.
        """
        self.repository = repository or YFinanceStockRepository()

    def get_fast_info(self, ticker: Annotated[str, "The symbol of the security."]) -> StockFastInfo:
        """
        Retrieve fast info for a specific stock ticker.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            StockFastInfo: Fast info data for the given ticker.
        """
        return self.repository.fetch_fast_info(ticker)

    def get_info(self, ticker: Annotated[str, "The symbol of the security."]) -> StockInfo:
        """
        Retrieve detailed info for a specific stock ticker.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            StockInfo: Detailed info data for the given ticker.
        """
        return self.repository.fetch_info(ticker)

    def get_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> list[StockHistory]:
        """
        Retrieve historical price data for a stock.

        Args:
            ticker (str): The symbol of the stock.
            period (str, optional): Time period for history (e.g., '1y', '6mo'). Defaults to '1y'.
            interval (str, optional): Data interval (e.g., '1d', '1h'). Defaults to '1d'.

        Returns:
            list[StockHistory]: List of historical data points.
        """
        return self.repository.fetch_history(ticker, period, interval)

    def get_dividends(self, ticker: Annotated[str, "The symbol of the security."]) -> list[StockDividends]:
        """
        Retrieve dividend history for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            list[StockDividends]: List of dividend records.
        """
        return self.repository.fetch_dividends(ticker)

    def get_financial_summary(self, ticker: Annotated[str, "The symbol of the security."]) -> dict:
        """
        Retrieve a financial summary for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            dict: Financial summary data.
        """
        return self.repository.fetch_financial_summary(ticker)

    def get_risk_metrics(self, ticker: Annotated[str, "The symbol of the security."]) -> dict:
        """
        Retrieve risk metrics for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            dict: Risk metrics data.
        """
        return self.repository.fetch_risk_metrics(ticker)

    def get_dividend_summary(self, ticker: Annotated[str, "The symbol of the security."]) -> dict:
        """
        Retrieve a summary of dividend data for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            dict: Dividend summary data.
        """
        return self.repository.fetch_dividend_summary(ticker)

    def get_price_target(self, ticker: Annotated[str, "The symbol of the security."]) -> dict:
        """
        Retrieve price target data for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            dict: Price target data.
        """
        return self.repository.fetch_price_target(ticker)

    def get_financial_summary_v2(self, ticker: Annotated[str, "The symbol of the security."]) -> dict:
        """
        Retrieve an alternative version of the financial summary for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            dict: Financial summary data (version 2).
        """
        return self.repository.fetch_financial_summary_v2(ticker)

    def get_quick_technical_indicators(self, ticker: Annotated[str, "The symbol of the security."]) -> dict:
        """
        Retrieve quick technical indicators for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            dict: Technical indicators data.
        """
        return self.repository.fetch_quick_technical_indicators(ticker)

    def get_splits(self, ticker: Annotated[str, "The symbol of the security."]) -> list[StockSplit]:
        """
        Retrieve stock split history for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            list[StockSplit]: List of stock split records.
        """
        return self.repository.fetch_splits(ticker)

    def get_corporate_actions(self, ticker: Annotated[str, "The symbol of the security."]) -> list[CorporateActions]:
        """
        Retrieve corporate actions for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            list[CorporateActions]: List of corporate action records.
        """
        return self.repository.fetch_corporate_actions(ticker)

    def get_news(self, ticker: Annotated[str, "The symbol of the security."]) -> list[NewsItem]:
        """
        Retrieve news items for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            list[NewsItem]: List of news items.
        """
        return self.repository.fetch_news(ticker)


stock_service = StockService()
