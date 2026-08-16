"""Repository layer for fund data operations.

Provides abstractions and implementations for fetching fund information,
holdings, sector weightings, and operational data.
"""

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.core.exceptions import DataUnavailableError, ProviderContractError
from openmarkets.core.provider import dataframe_records, require_mapping
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


class YFinanceFundsRepository:
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
        fund_info = require_mapping(fund_ticker.info, f"fund info for {ticker}")
        return FundInfo(**fund_info)

    def get_fund_sector_weighting(self, ticker: str, session: Session | None = None) -> FundSectorWeighting | None:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info:
            return None
        if not hasattr(fund_info, "sector_weightings"):
            return None
        return FundSectorWeighting(**require_mapping(fund_info.sector_weightings, f"sector weights for {ticker}"))

    def get_fund_operations(self, ticker: str, session: Session | None = None) -> FundOperations | None:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info:
            return None
        if not hasattr(fund_info, "fund_operations"):
            return None

        normalized_ops = self._normalize_fund_operations(fund_info.fund_operations, ticker=ticker)
        return FundOperations(**normalized_ops)

    def _normalize_fund_operations(self, ops, ticker: str | None = None) -> dict:
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
            if isinstance(val, np.generic):
                return val.item()
            if isinstance(val, np.ndarray):
                return val.tolist()
            return val

        if isinstance(ops, pd.DataFrame):
            if ops.empty:
                raise DataUnavailableError("Fund operations are empty.")
            selected_column = next(
                (column for column in ops.columns if str(column).upper() == (ticker or "").upper()), None
            )
            if selected_column is None:
                candidates = [column for column in ops.columns if str(column).lower() != "category average"]
                if len(candidates) != 1:
                    raise ProviderContractError("Fund operations do not identify a unique fund column.")
                selected_column = candidates[0]
            normalized = {str(k): to_native(v) for k, v in ops[selected_column].to_dict().items()}
            normalized["index"] = str(selected_column)
            return normalized

        if hasattr(ops, "to_dict"):
            ops = ops.to_dict()
        if not isinstance(ops, dict):
            raise ProviderContractError(f"Fund operations returned {type(ops).__name__}; expected a mapping")

        # yfinance may return the DataFrame's column-oriented nested mapping.
        if ops and all(isinstance(value, dict) for value in ops.values()):
            key = next((k for k in ops if str(k).upper() == (ticker or "").upper()), None)
            candidates = [k for k in ops if str(k).lower() != "category average"]
            key = key if key is not None else (candidates[0] if len(candidates) == 1 else None)
            if key is None:
                raise ProviderContractError("Fund operations do not identify a unique fund column.")
            normalized = {str(k): to_native(v) for k, v in ops[key].items()}
            normalized["index"] = str(key)
            return normalized

        return {str(k): to_native(v) for k, v in ops.items()}

    def get_fund_overview(self, ticker: str, session: Session | None = None) -> FundOverview | None:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info:
            return None
        if not hasattr(fund_info, "fund_overview"):
            return None
        return FundOverview(**require_mapping(fund_info.fund_overview, f"fund overview for {ticker}"))

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
        records = dataframe_records(fund_info.top_holdings, f"top fund holdings for {ticker}")
        return [FundTopHolding(**row) for row in records]

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
        df = getattr(fund_info, "bond_holdings", None)
        if df is None or (hasattr(df, "empty") and df.empty):
            return []
        transposed = df.transpose()
        reset_df = transposed.reset_index()
        return [FundBondHolding(**row) for row in reset_df.to_dict(orient="records")]

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
        df = getattr(fund_info, "equity_holdings", None)
        if df is None or (hasattr(df, "empty") and df.empty):
            return []
        transposed = df.transpose()
        reset_df = transposed.reset_index()
        return [FundEquityHolding(**row) for row in reset_df.to_dict(orient="records")]

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
