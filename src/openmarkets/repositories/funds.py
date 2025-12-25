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
    @abstractmethod
    def get_fund_info(self, ticker: str, session: Session | None = None) -> FundInfo:
        pass

    @abstractmethod
    def get_fund_sector_weighting(self, ticker: str, session: Session | None = None) -> FundSectorWeighting | None:
        pass

    @abstractmethod
    def get_fund_operations(self, ticker: str, session: Session | None = None) -> FundOperations | None:
        pass

    @abstractmethod
    def get_fund_overview(self, ticker: str, session: Session | None = None) -> FundOverview | None:
        pass

    @abstractmethod
    def get_fund_top_holdings(self, ticker: str, session: Session | None = None) -> list[FundTopHolding]:
        pass

    @abstractmethod
    def get_fund_bond_holdings(self, ticker: str, session: Session | None = None) -> list[FundBondHolding]:
        pass

    @abstractmethod
    def get_fund_equity_holdings(self, ticker: str, session: Session | None = None) -> list[FundEquityHolding]:
        pass

    @abstractmethod
    def get_fund_asset_class_holdings(
        self, ticker: str, session: Session | None = None
    ) -> FundAssetClassHolding | None:
        pass


class YFinanceFundsRepository(IFundsRepository):
    def get_fund_info(self, ticker: str, session: Session | None = None) -> FundInfo:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.info
        return FundInfo(**fund_info)

    def get_fund_sector_weighting(self, ticker: str, session: Session | None = None) -> FundSectorWeighting | None:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info or not hasattr(fund_info, "sector_weightings"):
            return None
        return FundSectorWeighting(**fund_info.sector_weightings)

    def get_fund_operations(self, ticker: str, session: Session | None = None) -> FundOperations | None:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info or not hasattr(fund_info, "fund_operations"):
            return None
        import numpy as np
        import pandas as pd

        ops = fund_info.fund_operations
        if hasattr(ops, "to_dict"):
            ops = ops.to_dict()

        # Ensure keys are strings and values are native types
        def to_native(val):
            if isinstance(val, pd.Series):
                # If Series has only one value, extract it
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

        ops = {str(k): to_native(v) for k, v in ops.items()}
        return FundOperations(**ops)

    def get_fund_overview(self, ticker: str, session: Session | None = None) -> FundOverview | None:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info or not hasattr(fund_info, "fund_overview"):
            return None
        return FundOverview(**fund_info.fund_overview)

    def get_fund_top_holdings(self, ticker: str, session: Session | None = None) -> list[FundTopHolding]:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info or not hasattr(fund_info, "top_holdings"):
            return []
        df = fund_info.top_holdings
        return [FundTopHolding(**row.to_dict()) for _, row in df.reset_index().iterrows()]

    def get_fund_bond_holdings(self, ticker: str, session: Session | None = None) -> list[FundBondHolding]:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info or not hasattr(fund_info, "bond_holdings"):
            return []
        df = fund_info.bond_holdings
        return [FundBondHolding(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]

    def get_fund_equity_holdings(self, ticker: str, session: Session | None = None) -> list[FundEquityHolding]:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info or not hasattr(fund_info, "equity_holdings"):
            return []
        df = fund_info.equity_holdings
        return [FundEquityHolding(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]

    def get_fund_asset_class_holdings(
        self, ticker: str, session: Session | None = None
    ) -> FundAssetClassHolding | None:
        fund_ticker = yf.Ticker(ticker, session=session)
        fund_info = fund_ticker.get_funds_data()
        if not fund_info or not hasattr(fund_info, "asset_classes"):
            return None
        return FundAssetClassHolding(**fund_info.asset_classes)
