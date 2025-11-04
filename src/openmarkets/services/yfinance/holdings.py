import yfinance as yf

from openmarkets.schemas.holdings import (
    InsiderPurchase,
    InsiderRosterHolder,
    StockInstitutionalHoldings,
    StockMajorHolders,
    StockMutualFundHoldings,
)


def get_major_holders_for_ticker(ticker: str) -> StockMajorHolders:
    """
    Fetch stock holdings data for a given ticker and return as StockMajorHolders.
    """
    df = yf.Ticker(ticker).get_major_holders()
    return StockMajorHolders(**df.transpose().reset_index().to_dict(orient="records"))


def get_institutional_holdings_for_ticker(ticker: str) -> list[StockInstitutionalHoldings]:
    """
    Fetch institutional holdings for a given ticker and return as a list of StockInstitutionalHoldings.
    """
    df = yf.Ticker(ticker).get_institutional_holders()
    df.reset_index(inplace=True)
    return [StockInstitutionalHoldings(**row.to_dict()) for _, row in df.iterrows()]


def get_mutual_fund_holdings_for_ticker(ticker: str) -> list[StockMutualFundHoldings]:
    """
    Fetch mutual fund holdings for a given ticker and return as a list of StockMutualFundHoldings.
    """
    df = yf.Ticker(ticker).get_mutualfund_holders()
    df.reset_index(inplace=True)
    return [StockMutualFundHoldings(**row.to_dict()) for _, row in df.iterrows()]


def get_insider_purchases_for_ticker(ticker: str) -> list[InsiderPurchase]:
    """
    Fetch insider purchases for a given ticker and return as a list of InsiderPurchase.
    """
    df = yf.Ticker(ticker).get_insider_purchases()
    df.reset_index(inplace=True)
    return [InsiderPurchase(**row.to_dict()) for _, row in df.iterrows()]


def get_insider_roster_holders_for_ticker(ticker: str) -> list[InsiderRosterHolder]:
    """
    Fetch insider roster holders for a given ticker and return as a list of InsiderRosterHolder.
    """
    df = yf.Ticker(ticker).get_insider_roster_holders()
    df.reset_index(inplace=True)
    return [InsiderRosterHolder(**row.to_dict()) for _, row in df.iterrows()]
