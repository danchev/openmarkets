"""Repository layer for fund data operations.

Provides abstractions and implementations for fetching fund information,
holdings, sector weightings, and operational data.
"""

from abc import ABC, abstractmethod

import yfinance as yf
from curl_cffi.requests import Session

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


class IFundsRepository(ABC):
    """Abstract interface for fund data repositories."""

    @abstractmethod
    def get_fund_info(self, ticker: str, session: Session | None = None) -> FundInfo:
        """Retrieve fund information for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Fund information.
        """
        pass

    @abstractmethod
    def get_fund_sector_weighting(self, ticker: str, session: Session | None = None) -> FundSectorWeighting | None:
        """Retrieve fund sector weighting for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Fund sector weighting or None if unavailable.
        """
        pass

    @abstractmethod
    def get_fund_operations(self, ticker: str, session: Session | None = None) -> FundOperations | None:
        """Retrieve fund operations data for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Fund operations or None if unavailable.
        """
        pass

    @abstractmethod
    def get_fund_overview(self, ticker: str, session: Session | None = None) -> FundOverview | None:
        """Retrieve fund overview for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Fund overview or None if unavailable.
        """
        pass

    @abstractmethod
    def get_fund_top_holdings(self, ticker: str, session: Session | None = None) -> list[FundTopHolding]:
        """Retrieve fund top holdings for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of fund top holdings.
        """
        pass

    @abstractmethod
    def get_fund_bond_holdings(self, ticker: str, session: Session | None = None) -> list[FundBondHolding]:
        """Retrieve fund bond holdings for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of fund bond holdings.
        """
        pass

    @abstractmethod
    def get_fund_equity_holdings(self, ticker: str, session: Session | None = None) -> list[FundEquityHolding]:
        """Retrieve fund equity holdings for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of fund equity holdings.
        """
        pass

    @abstractmethod
    def get_fund_asset_class_holdings(
        self, ticker: str, session: Session | None = None
    ) -> FundAssetClassHolding | None:
        """Retrieve fund asset class holdings for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Fund asset class holdings or None if unavailable.
        """
        pass


class YFinanceFundsRepository(IFundsRepository):
    """Repository for accessing fund data from yfinance."""

    def get_fund_info(self, ticker: str, session: Session | None = None) -> FundInfo:
        """Retrieve fund information for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            Fund information.
        """
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.info
        return FundInfo(**fund_info)

    def get_fund_sector_weighting(self, ticker: str, session: Session | None = None) -> FundSectorWeighting | None:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info:
            return None
        if not hasattr(fund_info, "sector_weightings"):
            return None
        return FundSectorWeighting(**fund_info.sector_weightings)

    def get_fund_operations(self, ticker: str, session: Session | None = None) -> FundOperations | None:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info:
            return None
        if not hasattr(fund_info, "fund_operations"):
            return None

        ops = fund_info.fund_operations
        if hasattr(ops, "to_dict"):
            ops = ops.to_dict()

        normalized_ops = self._normalize_fund_operations(ops)
        return FundOperations(**normalized_ops)

    def _normalize_fund_operations(self, ops: dict) -> dict:
        """Normalize fund operations dictionary to native types.

        Args:
            ops: Raw fund operations dictionary.

        Returns:
            Dictionary with normalized keys and values.
        """
        import numpy as np
        import pandas as pd

        def to_native(val):
            if isinstance(val, pd.Series):
                if len(val) == 1:
                    return to_native(val.iloc[0])
                return val.to_list()
            if hasattr(val, "item"):
                try:
                    return val.item()
                except Exception:
                    pass
            if isinstance(val, (np.generic, np.ndarray)):
                return val.tolist()
            return val

        return {str(k): to_native(v) for k, v in ops.items()}

    def get_fund_overview(self, ticker: str, session: Session | None = None) -> FundOverview | None:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info:
            return None
        if not hasattr(fund_info, "fund_overview"):
            return None
        return FundOverview(**fund_info.fund_overview)

    def get_fund_top_holdings(self, ticker: str, session: Session | None = None) -> list[FundTopHolding]:
        """Retrieve fund top holdings for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of fund top holdings.
        """
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info:
            return []
        if not hasattr(fund_info, "top_holdings"):
            return []
        df = fund_info.top_holdings
        reset_df = df.reset_index()
        return [FundTopHolding(**row.to_dict()) for _, row in reset_df.iterrows()]

    def get_fund_bond_holdings(self, ticker: str, session: Session | None = None) -> list[FundBondHolding]:
        """Retrieve fund bond holdings for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of fund bond holdings.
        """
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info:
            return []
        if not hasattr(fund_info, "bond_holdings"):
            return []
        df = fund_info.bond_holdings
        transposed = df.transpose()
        reset_df = transposed.reset_index()
        return [FundBondHolding(**row.to_dict()) for _, row in reset_df.iterrows()]

    def get_fund_equity_holdings(self, ticker: str, session: Session | None = None) -> list[FundEquityHolding]:
        """Retrieve fund equity holdings for a ticker.

        Args:
            ticker: Fund ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of fund equity holdings.
        """
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info:
            return []
        if not hasattr(fund_info, "equity_holdings"):
            return []
        df = fund_info.equity_holdings
        transposed = df.transpose()
        reset_df = transposed.reset_index()
        return [FundEquityHolding(**row.to_dict()) for _, row in reset_df.iterrows()]

    def get_fund_asset_class_holdings(
        self, ticker: str, session: Session | None = None
    ) -> FundAssetClassHolding | None:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info:
            return None
        if not hasattr(fund_info, "asset_classes"):
            return None
        return FundAssetClassHolding(**fund_info.asset_classes)
