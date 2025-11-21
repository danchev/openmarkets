from abc import ABC, abstractmethod

import yfinance as yf

from openmarkets.schemas.holdings import (
    InsiderPurchase,
    InsiderRosterHolder,
    StockInstitutionalHoldings,
    StockMajorHolders,
    StockMutualFundHoldings,
)


class IHoldingsRepository(ABC):
    @abstractmethod
    def fetch_major_holders(self, ticker: str) -> list[StockMajorHolders]:
        pass

    @abstractmethod
    def fetch_institutional_holdings(self, ticker: str) -> list[StockInstitutionalHoldings]:
        pass

    @abstractmethod
    def fetch_mutual_fund_holdings(self, ticker: str) -> list[StockMutualFundHoldings]:
        pass

    @abstractmethod
    def fetch_insider_purchases(self, ticker: str) -> list[InsiderPurchase]:
        pass

    @abstractmethod
    def fetch_insider_roster_holders(self, ticker: str) -> list[InsiderRosterHolder]:
        pass


class YFinanceHoldingsRepository(IHoldingsRepository):
    def fetch_major_holders(self, ticker: str) -> list[StockMajorHolders]:
        df = yf.Ticker(ticker).get_major_holders()
        return [StockMajorHolders(**row) for row in df.transpose().reset_index().to_dict(orient="records")]

    def fetch_institutional_holdings(self, ticker: str) -> list[StockInstitutionalHoldings]:
        df = yf.Ticker(ticker).get_institutional_holders()
        df.reset_index(inplace=True)
        return [StockInstitutionalHoldings(**row.to_dict()) for _, row in df.iterrows()]

    def fetch_mutual_fund_holdings(self, ticker: str) -> list[StockMutualFundHoldings]:
        df = yf.Ticker(ticker).get_mutualfund_holders()
        df.reset_index(inplace=True)
        return [StockMutualFundHoldings(**row.to_dict()) for _, row in df.iterrows()]

    def fetch_insider_purchases(self, ticker: str) -> list[InsiderPurchase]:
        df = yf.Ticker(ticker).get_insider_purchases()
        df.reset_index(inplace=True)
        return [InsiderPurchase(**row.to_dict()) for _, row in df.iterrows()]

    def fetch_insider_roster_holders(self, ticker: str) -> list[InsiderRosterHolder]:
        df = yf.Ticker(ticker).get_insider_roster_holders()
        return [InsiderRosterHolder(**row.to_dict()) for _, row in df.reset_index().iterrows()]
