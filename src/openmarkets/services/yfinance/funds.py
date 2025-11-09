import yfinance as yf

from openmarkets.schemas.funds import (
    FundAssetClassHolding,
    FundBondHolding,
    FundEquityHolding,
    FundInfo,
    FundOperations,
    FundOverview,
    FundSectorWeighting,
    FundTopHolding,
)


def fetch_fund_info(ticker: str) -> FundInfo:
    """
    Retrieve general information about a fund for a given ticker.

    Args:
        ticker (str): The fund ticker symbol.

    Returns:
        FundInfo: General fund information.
    """
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.info
    return FundInfo(**fund_info)


def fetch_fund_sector_weighting(ticker: str) -> FundSectorWeighting | None:
    """
    Fetch sector weighting data for a fund by ticker.

    Args:
        ticker (str): The fund ticker symbol.

    Returns:
        FundSectorWeighting | None: Sector weighting data or None if unavailable.
    """
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    if not fund_info or not hasattr(fund_info, "sector_weightings"):
        return None
    return FundSectorWeighting(**fund_info.sector_weightings)


def fetch_fund_operations(ticker: str) -> FundOperations | None:
    """
    Get operational details of a fund for a given ticker.

    Args:
        ticker (str): The fund ticker symbol.

    Returns:
        FundOperations | None: Operational details of the fund or None if unavailable.
    """
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    if not fund_info or not hasattr(fund_info, "fund_operations"):
        return None
    return FundOperations(**fund_info.fund_operations)


def fetch_fund_overview(ticker: str) -> FundOverview | None:
    """
    Get a summary overview of a fund for a given ticker.

    Args:
        ticker (str): The fund ticker symbol.

    Returns:
        FundOverview | None: Summary overview of the fund or None if unavailable.
    """
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    if not fund_info or not hasattr(fund_info, "fund_overview"):
        return None
    return FundOverview(**fund_info.fund_overview)


def fetch_fund_top_holdings(ticker: str) -> list[FundTopHolding]:
    """
    Fetch the top holdings of a fund for a given ticker.

    Args:
        ticker (str): The fund ticker symbol.

    Returns:
        list[FundTopHolding]: List of top fund holdings.
    """
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    if not fund_info or not hasattr(fund_info, "top_holdings"):
        return []
    df = fund_info.top_holdings
    return [FundTopHolding(**row.to_dict()) for _, row in df.reset_index().iterrows()]


def fetch_fund_bond_holdings(ticker: str) -> list[FundBondHolding]:
    """
    Retrieve bond holdings of a fund for a given ticker.

    Args:
        ticker (str): The fund ticker symbol.

    Returns:
        list[FundBondHolding]: List of bond holdings.
    """
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    if not fund_info or not hasattr(fund_info, "bond_holdings"):
        return []
    df = fund_info.bond_holdings
    return [FundBondHolding(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]


def fetch_fund_equity_holdings(ticker: str) -> list[FundEquityHolding]:
    """
    Fetch equity holdings of a fund for a given ticker.

    Args:
        ticker (str): The fund ticker symbol.

    Returns:
        list[FundEquityHolding]: List of equity holdings.
    """
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    if not fund_info or not hasattr(fund_info, "equity_holdings"):
        return []
    df = fund_info.equity_holdings
    return [FundEquityHolding(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]


def fetch_fund_asset_class_holdings(ticker: str) -> FundAssetClassHolding | None:
    """
    Get asset class holdings of a fund for a given ticker.

    Args:
        ticker (str): The fund ticker symbol.

    Returns:
        FundAssetClassHolding | None: Asset class holdings of the fund or None if unavailable.
    """
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    if not fund_info or not hasattr(fund_info, "asset_classes"):
        return None
    return FundAssetClassHolding(**fund_info.asset_classes)
