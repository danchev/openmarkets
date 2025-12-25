from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.holdings import (
    InsiderPurchase,
    InsiderRosterHolder,
    StockInstitutionalHoldings,
    StockMajorHolders,
    StockMutualFundHoldings,
)


class IHoldingsRepository(ABC):
    @abstractmethod
    def get_major_holders(self, ticker: str, session: Session | None = None) -> list[StockMajorHolders]:
        pass

    @abstractmethod
    def get_institutional_holdings(
        self, ticker: str, session: Session | None = None
    ) -> list[StockInstitutionalHoldings]:
        pass

    @abstractmethod
    def get_mutual_fund_holdings(self, ticker: str, session: Session | None = None) -> list[StockMutualFundHoldings]:
        pass

    @abstractmethod
    def get_insider_purchases(self, ticker: str, session: Session | None = None) -> list[InsiderPurchase]:
        pass

    @abstractmethod
    def get_insider_roster_holders(self, ticker: str, session: Session | None = None) -> list[InsiderRosterHolder]:
        pass


class YFinanceHoldingsRepository(IHoldingsRepository):
    def get_major_holders(self, ticker: str, session: Session | None = None) -> list[StockMajorHolders]:
        df = yf.Ticker(ticker, session=session).get_major_holders()
        return [StockMajorHolders(**row) for row in df.transpose().reset_index().to_dict(orient="records")]

    def get_institutional_holdings(
        self, ticker: str, session: Session | None = None
    ) -> list[StockInstitutionalHoldings]:
        df = yf.Ticker(ticker, session=session).get_institutional_holders()
        df.reset_index(inplace=True)
        return [StockInstitutionalHoldings(**row.to_dict()) for _, row in df.iterrows()]

    def get_mutual_fund_holdings(self, ticker: str, session: Session | None = None) -> list[StockMutualFundHoldings]:
        df = yf.Ticker(ticker, session=session).get_mutualfund_holders()
        df.reset_index(inplace=True)
        return [StockMutualFundHoldings(**row.to_dict()) for _, row in df.iterrows()]

    def get_insider_purchases(self, ticker: str, session: Session | None = None) -> list[InsiderPurchase]:
        df = yf.Ticker(ticker, session=session).get_insider_purchases()
        df.reset_index(inplace=True)
        return [InsiderPurchase(**row.to_dict()) for _, row in df.iterrows()]

    def get_insider_roster_holders(self, ticker: str, session: Session | None = None) -> list[InsiderRosterHolder]:
        df = yf.Ticker(ticker, session=session).get_insider_roster_holders()
        return [InsiderRosterHolder(**row.to_dict()) for _, row in df.reset_index().iterrows()]
