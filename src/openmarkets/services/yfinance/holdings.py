import yfinance as yf

from openmarkets.schemas.holdings import (
    InsiderPurchase,
    InsiderRosterHolder,
    StockInstitutionalHoldings,
    StockMajorHolders,
    StockMutualFundHoldings,
)


def fetch_major_holders(ticker: str) -> list[StockMajorHolders]:
    """
    Fetch stock major holders data for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        StockMajorHolders: Major holders data.
    """
    df = yf.Ticker(ticker).get_major_holders()
    return [StockMajorHolders(**row) for row in df.transpose().reset_index().to_dict(orient="records")]


def fetch_institutional_holdings(ticker: str) -> list[StockInstitutionalHoldings]:
    """
    Fetch institutional holdings for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[StockInstitutionalHoldings]: List of institutional holdings.
    """
    df = yf.Ticker(ticker).get_institutional_holders()
    df.reset_index(inplace=True)
    return [StockInstitutionalHoldings(**row.to_dict()) for _, row in df.iterrows()]


def fetch_mutual_fund_holdings(ticker: str) -> list[StockMutualFundHoldings]:
    """
    Fetch mutual fund holdings for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[StockMutualFundHoldings]: List of mutual fund holdings.
    """
    df = yf.Ticker(ticker).get_mutualfund_holders()
    df.reset_index(inplace=True)
    return [StockMutualFundHoldings(**row.to_dict()) for _, row in df.iterrows()]


def fetch_insider_purchases(ticker: str) -> list[InsiderPurchase]:
    """
    Fetch insider purchases for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[InsiderPurchase]: List of insider purchases.
    """
    df = yf.Ticker(ticker).get_insider_purchases()
    df.reset_index(inplace=True)
    return [InsiderPurchase(**row.to_dict()) for _, row in df.iterrows()]


def fetch_insider_roster_holders(ticker: str) -> list[InsiderRosterHolder]:
    """
    Fetch insider roster holders for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list[InsiderRosterHolder]: List of insider roster holders.
    """
    df = yf.Ticker(ticker).get_insider_roster_holders()
    return [InsiderRosterHolder(**row.to_dict()) for _, row in df.reset_index().iterrows()]
