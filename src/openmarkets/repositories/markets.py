"""Repository layer for market data operations.

Provides abstractions and implementations for fetching market summaries,
market status, and related market-level information.
"""

import logging
from datetime import datetime, timezone

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.core.wsj import fetch_wsj_timeseries, resolve_wsj_key
from openmarkets.schemas.markets import (
    GlobalIndexQuote,
    GlobalMarketSnapshot,
    MarketStatus,
    MarketSummary,
    SummaryEntry,
)

logger = logging.getLogger(__name__)


class YFinanceMarketsRepository:
    """Repository for accessing market data from yfinance.

    Infrastructure layer: encapsulates yfinance dependency.
    """

    def get_market_summary(self, market: str, session: Session | None = None) -> MarketSummary:
        """Retrieve market summary data.

        Args:
            market: Market identifier.
            session: Optional HTTP session for request handling.

        Returns:
            Market summary data.
        """
        market_obj = yf.Market(market, session=session)
        summary = market_obj.summary
        return MarketSummary(summary={k: SummaryEntry(**v) for k, v in summary.items()})

    def get_market_status(self, market: str, session: Session | None = None) -> MarketStatus:
        """Retrieve market status information.

        Args:
            market: Market identifier.
            session: Optional HTTP session for request handling.

        Returns:
            Market status data.
        """
        market_obj = yf.Market(market, session=session)
        status = market_obj.status
        return MarketStatus(**status)


class WSJMarketsRepository:
    """Repository for global benchmark equity indices and volatility gauges from WSJ."""

    GLOBAL_INDICES = [
        ("SP500", "US"),
        ("DJIA", "US"),
        ("NASDAQ", "US"),
        ("RUSSELL2000", "US"),
        ("DAX", "Europe"),
        ("FTSE100", "Europe"),
        ("CAC40", "Europe"),
        ("EUROSTOXX50", "Europe"),
        ("NIKKEI225", "Asia"),
        ("HANGSENG", "Asia"),
        ("VIX", "US"),
    ]

    def get_global_indices(self, session: Session | None = None) -> GlobalMarketSnapshot:
        """Retrieve latest snapshot of major global benchmark indices."""
        quotes: list[GlobalIndexQuote] = []
        as_of = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        for symbol, region in self.GLOBAL_INDICES:
            wsj_key, name, _, unit = resolve_wsj_key(symbol)
            try:
                raw = fetch_wsj_timeseries(
                    wsj_key=wsj_key,
                    step="P1D",
                    timeframe="D5",
                    datatypes=["Last"],
                    session=session,
                )
                ticks = raw.get("TimeInfo", {}).get("Ticks", [])
                series = raw.get("Series", [])
                dp = series[0].get("DataPoints", []) if series else []
                for ts, vals in reversed(list(zip(ticks, dp, strict=False))):
                    if vals and vals[0] is not None:
                        dt_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
                        quotes.append(
                            GlobalIndexQuote(
                                symbol=symbol,
                                name=name,
                                region=region,
                                value=round(float(vals[0]), 2),
                                unit=unit,
                                date=dt_str,
                            )
                        )
                        break
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                logger.warning("Unable to retrieve WSJ index %s: %s", symbol, exc)
                continue

        return GlobalMarketSnapshot(as_of=as_of, indices=quotes)

    def get_volatility_vix(self, session: Session | None = None) -> GlobalIndexQuote:
        """Retrieve real-time quote for CBOE Volatility Index (VIX)."""
        wsj_key, name, _, unit = resolve_wsj_key("VIX")
        raw = fetch_wsj_timeseries(
            wsj_key=wsj_key,
            step="P1D",
            timeframe="D5",
            datatypes=["Last"],
            session=session,
        )
        ticks = raw.get("TimeInfo", {}).get("Ticks", [])
        series = raw.get("Series", [])
        dp = series[0].get("DataPoints", []) if series else []
        for ts, vals in reversed(list(zip(ticks, dp, strict=False))):
            if vals and vals[0] is not None:
                dt_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
                return GlobalIndexQuote(
                    symbol="VIX",
                    name=name,
                    region="US",
                    value=round(float(vals[0]), 2),
                    unit=unit,
                    date=dt_str,
                )

        raise ValueError("Could not retrieve VIX index from WSJ")
