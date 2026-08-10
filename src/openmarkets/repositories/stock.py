"""Repository layer for stock data operations.

Fetches stock information, historical prices, dividends, splits, and other
stock-level data from yfinance.
"""

from datetime import datetime, timezone
from typing import Protocol

import pandas as pd
import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.core.exceptions import InvalidSymbolError
from openmarkets.core.types import Interval, Period, ValuationFrequency
from openmarkets.core.wsj import fetch_wsj_timeseries, resolve_wsj_key
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
    WSJBollingerBandPoint,
    WSJBollingerBandsSeries,
    WSJIntradayBar,
    WSJStockHistory,
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

    def get_curated_info(self, ticker: str, session: Session | None = None) -> StockInfo_v2: ...

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

    def get_valuation_measures(
        self,
        ticker: str,
        frequency: ValuationFrequency = "annual",
        periods: int | None = 5,
        session: Session | None = None,
    ) -> list[ValuationMeasuresEntry]: ...


class YFinanceStockRepository:
    """Repository for accessing stock data from yfinance."""

    def get_fast_info(self, ticker: str, session: Session | None = None) -> StockFastInfo:
        """Retrieve fast info for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Fast info data for the stock.

        Raises:
            InvalidSymbolError: If the symbol is not found or invalid.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        fast_info = ticker_obj.fast_info
        if not fast_info:
            raise InvalidSymbolError(f"Symbol '{ticker}' not found or invalid.")
        try:
            return StockFastInfo(**fast_info)
        except Exception as exc:
            raise InvalidSymbolError(f"Symbol '{ticker}' not found or invalid.") from exc

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

    def get_curated_info(self, ticker: str, session: Session | None = None) -> StockInfo_v2:
        """Retrieve curated stock overview (33 key fundamental metrics).

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Curated stock information.

        Raises:
            InvalidSymbolError: If the symbol is not found or invalid.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        info = ticker_obj.info
        if not info:
            raise InvalidSymbolError(f"Symbol '{ticker}' not found or invalid.")
        return StockInfo_v2(**info)

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
        return [StockHistory(**row) for row in df.to_dict(orient="records")]

    def get_dividends(self, ticker: str, session: Session | None = None) -> list[StockDividends]:
        """Retrieve dividend history for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of dividend records.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        dividends = getattr(ticker_obj, "dividends", None)
        if dividends is None or (hasattr(dividends, "empty") and dividends.empty):
            return []
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
        splits = getattr(ticker_obj, "splits", None)
        if splits is None or (hasattr(splits, "empty") and splits.empty):
            return []
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
        actions = getattr(ticker_obj, "actions", None)
        if actions is None or (hasattr(actions, "empty") and actions.empty):
            return []
        reset_actions = actions.reset_index()
        return [CorporateActions(**row) for row in reset_actions.to_dict(orient="records")]

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

    def get_valuation_history(
        self,
        ticker: str,
        freq: ValuationFrequency = "quarterly",
        periods: int | None = 5,
        session: Session | None = None,
    ) -> list[ValuationMeasuresEntry]:
        """Retrieve historical valuation ratios for a stock ticker.

        Args:
            ticker: Stock ticker symbol.
            freq: Period-column grouping: "quarterly", "monthly", "yearly"
                or "trailing".
            periods: Number of period columns to return, newest first.
                None returns all available history; 0 returns only the
                "Current" column.
            session: Optional HTTP session for request handling.

        Returns:
            One entry per period (newest first), each with the 9 valuation
            ratios for that period. Empty for instruments valuation
            measures do not apply to (e.g. cryptocurrencies).
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        measures = ticker_obj.get_valuation_measures(freq=freq, periods=periods)
        if measures.empty:
            return []
        records = measures.T.reset_index().rename(columns={"index": "period"}).to_dict("records")
        return [ValuationMeasuresEntry(**record) for record in records]


class WSJStockRepository:
    """Stock repository backed by WSJ Michelangelo timeseries API."""

    def get_stock_history(
        self,
        ticker: str,
        timeframe: str = "P1Y",
        step: str = "P1D",
        session: Session | None = None,
    ) -> WSJStockHistory:
        """Fetch historical price timeseries for a stock from WSJ.

        Args:
            ticker: Stock ticker symbol (e.g. 'TSLA', 'AAPL').
            timeframe: Timespan duration (e.g. 'D7', '1mo', 'P1Y', '5y', 'all').
            step: Bar frequency (e.g. 'P1D', 'PT1M', 'PT5M').
            session: Optional HTTP session.

        Returns:
            WSJStockHistory with ordered OHLCV bars.
        """
        wsj_key, name, _, _ = resolve_wsj_key(ticker)
        raw = fetch_wsj_timeseries(
            wsj_key=wsj_key,
            step=step,
            timeframe=timeframe,
            datatypes=["Open", "High", "Low", "Last"],
            session=session,
        )

        ticks = raw.get("TimeInfo", {}).get("Ticks", [])
        series_list = raw.get("Series", [])
        datapoints = series_list[0].get("DataPoints", []) if series_list else []
        volume_points = series_list[1].get("DataPoints", []) if len(series_list) > 1 else []

        bars: list[WSJIntradayBar] = []
        for i, (ts, vals) in enumerate(zip(ticks, datapoints, strict=False)):
            if not vals or all(v is None for v in vals):
                continue
            dt_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            vol = (
                float(volume_points[i][0])
                if i < len(volume_points) and volume_points[i] and volume_points[i][0] is not None
                else None
            )

            if len(vals) >= 4 and vals[3] is not None:
                bars.append(
                    WSJIntradayBar(
                        timestamp=ts,
                        date=dt_str,
                        open=vals[0],
                        high=vals[1],
                        low=vals[2],
                        close=float(vals[3]),
                        volume=vol,
                    )
                )
            elif len(vals) >= 1 and vals[0] is not None:
                bars.append(
                    WSJIntradayBar(
                        timestamp=ts,
                        date=dt_str,
                        open=None,
                        high=None,
                        low=None,
                        close=float(vals[0]),
                        volume=vol,
                    )
                )

        return WSJStockHistory(
            symbol=ticker.upper(),
            name=name,
            data_points=bars,
        )

    def get_bollinger_bands(
        self,
        ticker: str,
        window: int = 20,
        multiplier: float = 2.0,
        timeframe: str = "P1M",
        step: str = "P1D",
        session: Session | None = None,
    ) -> WSJBollingerBandsSeries:
        """Fetch server-side computed Bollinger Bands from WSJ Michelangelo."""
        wsj_key, _, _, _ = resolve_wsj_key(ticker)
        indicators = [
            {
                "Parameters": [
                    {"Name": "Period", "Value": window},
                    {"Name": "Multiplier", "Value": multiplier},
                ],
                "Kind": "BollingerBands",
                "SeriesId": "i_bb",
            }
        ]

        raw = fetch_wsj_timeseries(
            wsj_key=wsj_key,
            step=step,
            timeframe=timeframe,
            datatypes=["Last"],
            indicators=indicators,
            session=session,
        )

        ticks = raw.get("TimeInfo", {}).get("Ticks", [])
        series_list = raw.get("Series", [])
        price_points = series_list[0].get("DataPoints", []) if series_list else []
        bb_points = series_list[1].get("DataPoints", []) if len(series_list) > 1 else []

        points: list[WSJBollingerBandPoint] = []
        for i, (ts, p_val) in enumerate(zip(ticks, price_points, strict=False)):
            if not p_val or p_val[0] is None:
                continue
            dt_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            price = float(p_val[0])
            if i < len(bb_points) and bb_points[i] and len(bb_points[i]) >= 3:
                low_b, mid_b, up_b = float(bb_points[i][0]), float(bb_points[i][1]), float(bb_points[i][2])
                bw = round(((up_b - low_b) / mid_b) * 100, 2) if mid_b else None
                points.append(
                    WSJBollingerBandPoint(
                        timestamp=ts,
                        date=dt_str,
                        price=price,
                        lower_band=round(low_b, 3),
                        middle_band=round(mid_b, 3),
                        upper_band=round(up_b, 3),
                        bandwidth_pct=bw,
                    )
                )

        return WSJBollingerBandsSeries(
            symbol=ticker.upper(),
            window=window,
            multiplier=multiplier,
            data_points=points,
        )
