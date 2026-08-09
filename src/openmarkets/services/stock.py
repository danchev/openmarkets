"""Service layer for stock data operations.

Provides business logic for retrieving stock information, historical prices,
dividends, financial summaries, risk metrics, technical indicators, splits,
corporate actions, and news. Acts as an intermediary between the MCP tools
layer and repository layer.
"""

from curl_cffi.requests import Session

from openmarkets.core.cache import cached
from openmarkets.core.http import get_session
from openmarkets.core.types import Interval, Period, Ticker, ValuationFrequency
from openmarkets.repositories.stock import StockRepository, YFinanceStockRepository
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
    StockInfo_v2,
    StockSplit,
    ValuationMeasuresEntry,
)
from openmarkets.services.utils import ToolRegistrationMixin, tool


class StockService(ToolRegistrationMixin):
    """
    Service layer for stock-related business logic.
    Provides methods to retrieve stock info, history, dividends, financial summaries, risk metrics, technical indicators, splits, corporate actions, and news for a given ticker.
    """

    def __init__(self, repository: StockRepository | None = None, session: Session | None = None):
        """Initialize the StockService.

        Args:
            repository: Repository instance for data access. Defaults to YFinanceStockRepository.
            session: HTTP session for requests. Defaults to chrome-impersonating Session.
        """
        self.repository = repository or YFinanceStockRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests.

        Falls back to the process-wide shared session so that no session is
        created at import time.
        """
        return self._session if self._session is not None else get_session()

    @tool
    @cached(ttl=300.0)
    def get_fast_info(self, ticker: Ticker) -> StockFastInfo:
        """
        Retrieve fast info for a specific stock ticker.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            StockFastInfo: Fast info data for the given ticker.
        """
        return self.repository.get_fast_info(ticker, session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_info(self, ticker: Ticker, fields: list[str] | None = None) -> StockInfo | dict:
        """
        Retrieve detailed info for a specific stock ticker.

        Args:
            ticker (str): The symbol of the stock.
            fields (list[str], optional): Specific field names to return (e.g. ['marketCap', 'trailingPE']).
                If omitted, returns the complete StockInfo model.

        Returns:
            StockInfo | dict: Detailed info data or pruned dictionary of requested fields.
        """
        info_model = self.repository.get_info(ticker, session=self.session)
        if fields:
            data = info_model.model_dump()
            return {k: data[k] for k in fields if k in data}
        return info_model

    @tool
    @cached(ttl=300.0)
    def get_curated_info(self, ticker: Ticker) -> StockInfo_v2:
        """
        Retrieve curated stock fundamental overview (33 essential metrics).

        Optimized for LLM reasoning to avoid context window bloat.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            StockInfo_v2: Curated stock information.
        """
        return self.repository.get_curated_info(ticker, session=self.session)

    @tool
    def get_history(self, ticker: Ticker, period: Period = "1y", interval: Interval = "1d") -> list[StockHistory]:
        """
        Retrieve historical price data for a stock.

        Args:
            ticker (str): The symbol of the stock.
            period (str, optional): Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max. Defaults to '1y'.
            interval (str, optional): Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo. Defaults to '1d'.

        Returns:
            list[StockHistory]: List of historical data points.
        """
        return self.repository.get_history(ticker, period, interval, session=self.session)

    @tool
    def get_dividends(self, ticker: Ticker) -> list[StockDividends]:
        """
        Retrieve dividend history for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            list[StockDividends]: List of dividend records.
        """
        return self.repository.get_dividends(ticker, session=self.session)

    @tool
    def get_financial_summary(self, ticker: Ticker) -> FinancialSummary:
        """
        Retrieve profitability, liquidity and cash-flow metrics for a stock.

        Covers revenue, margins, cash flow, debt and return ratios. Use
        get_extended_financial_summary instead when valuation or share-count
        metrics are also needed.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            FinancialSummary: Profitability, liquidity and cash-flow metrics.
        """
        return self.repository.get_financial_summary(ticker, session=self.session)

    @tool
    def get_risk_metrics(self, ticker: Ticker) -> RiskMetrics:
        """
        Retrieve risk metrics for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            dict: Risk metrics data.
        """
        return self.repository.get_risk_metrics(ticker, session=self.session)

    @tool
    def get_dividend_summary(self, ticker: Ticker) -> DividendSummary:
        """
        Retrieve a summary of dividend data for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            dict: Dividend summary data.
        """
        return self.repository.get_dividend_summary(ticker, session=self.session)

    @tool
    def get_price_target(self, ticker: Ticker) -> PriceTarget:
        """
        Retrieve price target data for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            dict: Price target data.
        """
        return self.repository.get_price_target(ticker, session=self.session)

    @tool
    def get_extended_financial_summary(self, ticker: Ticker) -> ExtendedFinancialSummary:
        """
        Retrieve the financial summary plus valuation and share-count metrics.

        A superset of get_financial_summary, adding market cap, enterprise
        value, share counts, book value and price-to-book.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            ExtendedFinancialSummary: Financial summary with valuation metrics.
        """
        return self.repository.get_extended_financial_summary(ticker, session=self.session)

    @tool
    def get_quick_technical_indicators(self, ticker: Ticker) -> QuickTechnicalIndicators:
        """
        Retrieve quick technical indicators for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            dict: Technical indicators data.
        """
        return self.repository.get_quick_technical_indicators(ticker, session=self.session)

    @tool
    def get_splits(self, ticker: Ticker) -> list[StockSplit]:
        """
        Retrieve stock split history for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            list[StockSplit]: List of stock split records.
        """
        return self.repository.get_splits(ticker, session=self.session)

    @tool
    def get_corporate_actions(self, ticker: Ticker) -> list[CorporateActions]:
        """
        Retrieve corporate actions for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            list[CorporateActions]: List of corporate action records.
        """
        return self.repository.get_corporate_actions(ticker, session=self.session)

    @tool
    def get_news(self, ticker: Ticker) -> list[NewsItem]:
        """
        Retrieve news items for a stock.

        Args:
            ticker (str): The symbol of the stock.

        Returns:
            list[NewsItem]: List of news items.
        """
        return self.repository.get_news(ticker, session=self.session)

    @tool
    def get_valuation_history(
        self, ticker: Ticker, freq: ValuationFrequency = "quarterly", periods: int | None = 5
    ) -> list[ValuationMeasuresEntry]:
        """
        Retrieve historical valuation ratios (P/E, P/S, P/B, EV/EBITDA, PEG, market cap,
        enterprise value) for a stock, one entry per period.

        Unlike get_financial_summary or get_extended_financial_summary, which are a
        current snapshot, this returns a short history so trend can be seen across
        recent quarters or years.

        Args:
            ticker (str): The symbol of the stock.
            freq (str, optional): Period-column grouping: 'quarterly', 'monthly',
                'yearly' or 'trailing'. Defaults to 'quarterly'.
            periods (int | None, optional): Number of period columns to return, newest
                first. None returns all available history; 0 returns only the current
                value. Defaults to 5.

        Returns:
            list[ValuationMeasuresEntry]: Valuation ratios per period, newest first.
                Empty for instruments valuation measures do not apply to (e.g.
                cryptocurrencies).
        """
        return self.repository.get_valuation_history(ticker, freq, periods, session=self.session)


stock_service = StockService()
