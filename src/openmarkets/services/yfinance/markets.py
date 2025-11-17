from typing import Annotated

import yfinance as yf

from openmarkets.schemas.markets import MarketStatus, MarketSummary, MarketType, SummaryEntry


def fetch_market_summary(market: Annotated[str, MarketType.__members__]) -> MarketSummary:
    """
    Fetch the market summary for a given market type.

    Args:
        market (MarketType): The market type.

    Returns:
        MarketSummary: Market summary data.
    """
    summary = yf.Market(market).summary
    return MarketSummary(summary={k: SummaryEntry(**v) for k, v in summary.items()})


def fetch_market_status(market: Annotated[str, MarketType.__members__]) -> MarketStatus:
    """
    Fetch the market status for a given market type.

    Args:
        market (MarketType): The market type.

    Returns:
        MarketStatus: Market status data.
    """
    status = yf.Market(market).status
    return MarketStatus(**status)
