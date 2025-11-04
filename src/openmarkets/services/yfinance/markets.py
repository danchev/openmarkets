import yfinance as yf

from openmarkets.schemas.markets import MarketStatus, MarketSummary, MarketType, SummaryEntry


def get_market_summary(market: MarketType) -> MarketSummary:
    """
    Fetch the market summary for a given market type and return as a MarketSummary.
    """
    summary = yf.Market(market).summary
    return MarketSummary(summary={k: SummaryEntry(**v) for k, v in summary.items()})


def get_market_status(market: MarketType) -> MarketStatus:
    """
    Fetch the market status for a given market type and return as a MarketStatus.
    """
    status = yf.Market(market).status
    return MarketStatus(**status)
