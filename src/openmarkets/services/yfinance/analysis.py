import yfinance as yf

from openmarkets.schemas.analysis import (
    AnalystPriceTargets,
    AnalystRecommendation,
    AnalystRecommendationChange,
    EarningsEstimate,
    EPSTrend,
    GrowthEstimates,
    RevenueEstimate,
)


def get_analyst_recommendations_for_ticker(ticker: str) -> list[AnalystRecommendation]:
    """
    Fetch analyst recommendations for a given ticker and return as a list of AnalystRecommendation.
    """
    df = yf.Ticker(ticker).get_recommendations()
    return [AnalystRecommendation(**row.to_dict()) for _, row in df.iterrows()]


def get_upgrades_downgrades_for_ticker(ticker: str) -> list[AnalystRecommendationChange]:
    """
    Fetch upgrades and downgrades for a given ticker and return as a list of AnalystRecommendationChange.
    """
    df = yf.Ticker(ticker).get_upgrades_downgrades()
    df.reset_index(inplace=True)
    return [AnalystRecommendationChange(**row.to_dict()) for _, row in df.iterrows()]


def get_revenue_estimate_for_ticker(ticker: str) -> list[RevenueEstimate]:
    """
    Fetch revenue estimates for a given ticker and return as a list of RevenueEstimate.
    """
    df = yf.Ticker(ticker).get_revenue_estimate()
    df.reset_index(inplace=True)
    return [RevenueEstimate(**row.to_dict()) for _, row in df.iterrows()]


def get_earnings_estimate_for_ticker(ticker: str) -> list[EarningsEstimate]:
    """
    Fetch earnings estimates for a given ticker and return as a list of EarningsEstimate.
    """
    df = yf.Ticker(ticker).get_earnings_estimate()
    df.reset_index(inplace=True)
    return [EarningsEstimate(**row.to_dict()) for _, row in df.iterrows()]


def get_eps_trend_for_ticker(ticker: str) -> list[EPSTrend]:
    """
    Fetch EPS trends for a given ticker and return as a list of EPSTrend.
    """
    df = yf.Ticker(ticker).get_eps_trend()
    df.reset_index(inplace=True)
    return [EPSTrend(**row.to_dict()) for _, row in df.iterrows()]


def get_growth_estimates_for_ticker(ticker: str) -> list[GrowthEstimates]:
    """
    Fetch growth estimates for a given ticker and return as a list of GrowthEstimates.
    """
    df = yf.Ticker(ticker).get_growth_estimates()
    df.reset_index(inplace=True)
    return [GrowthEstimates(**row.to_dict()) for _, row in df.iterrows()]


def get_analyst_price_targets(ticker: str) -> AnalystPriceTargets:
    """
    Get analyst price targets and estimates.

    """
    df = yf.Ticker(ticker).get_analyst_price_targets()
    return AnalystPriceTargets(**df)
