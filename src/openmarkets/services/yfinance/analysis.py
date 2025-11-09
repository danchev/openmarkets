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


def fetch_analyst_recommendations(ticker: str) -> list[AnalystRecommendation]:
    """
    Fetch analyst recommendations for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[AnalystRecommendation]: List of analyst recommendations.
    """
    df = yf.Ticker(ticker).get_recommendations()
    return [AnalystRecommendation(**row.to_dict()) for _, row in df.iterrows()]


def fetch_analyst_upgrades_downgrades(ticker: str) -> list[AnalystRecommendationChange]:
    """
    Fetch upgrades and downgrades for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[AnalystRecommendationChange]: List of analyst recommendation changes.
    """
    df = yf.Ticker(ticker).get_upgrades_downgrades()
    df.reset_index(inplace=True)
    return [AnalystRecommendationChange(**row.to_dict()) for _, row in df.iterrows()]


def fetch_revenue_estimates(ticker: str) -> list[RevenueEstimate]:
    """
    Fetch revenue estimates for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[RevenueEstimate]: List of revenue estimates.
    """
    df = yf.Ticker(ticker).get_revenue_estimate()
    df.reset_index(inplace=True)
    return [RevenueEstimate(**row.to_dict()) for _, row in df.iterrows()]


def fetch_earnings_estimates(ticker: str) -> list[EarningsEstimate]:
    """
    Fetch earnings estimates for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[EarningsEstimate]: List of earnings estimates.
    """
    df = yf.Ticker(ticker).get_earnings_estimate()
    df.reset_index(inplace=True)
    return [EarningsEstimate(**row.to_dict()) for _, row in df.iterrows()]


def fetch_eps_trends(ticker: str) -> list[EPSTrend]:
    """
    Fetch EPS trends for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[EPSTrend]: List of EPS trends.
    """
    df = yf.Ticker(ticker).get_eps_trend()
    df.reset_index(inplace=True)
    return [EPSTrend(**row.to_dict()) for _, row in df.iterrows()]


def fetch_growth_estimates(ticker: str) -> list[GrowthEstimates]:
    """
    Fetch growth estimates for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[GrowthEstimates]: List of growth estimates.
    """
    df = yf.Ticker(ticker).get_growth_estimates()
    df.reset_index(inplace=True)
    return [GrowthEstimates(**row.to_dict()) for _, row in df.iterrows()]


def fetch_analyst_price_targets(ticker: str) -> AnalystPriceTargets:
    """
    Get analyst price targets and estimates for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        AnalystPriceTargets: Analyst price targets and related estimates.
    """
    df = yf.Ticker(ticker).get_analyst_price_targets()
    return AnalystPriceTargets(**df)
