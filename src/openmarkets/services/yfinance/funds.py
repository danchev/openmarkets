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


def get_fund_info(ticker: str) -> FundInfo:
    """Retrieve general information about a fund for a given ticker."""
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.info
    return FundInfo(**fund_info)


def get_fund_sector_weighting(ticker: str) -> FundSectorWeighting:
    """Fetch sector weighting data for a fund by ticker."""
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    return FundSectorWeighting(**fund_info.sector_weightings)


def get_fund_operations(ticker: str) -> FundOperations:
    """Get operational details of a fund for a given ticker."""
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    return FundOperations(**fund_info.fund_operations)


def get_fund_overview(ticker: str) -> FundOverview:
    """Get a summary overview of a fund for a given ticker."""
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    return FundOverview(**fund_info.fund_overview)


def get_fund_top_holdings(ticker: str) -> list[FundTopHolding]:
    """Fetch the top holdings of a fund for a given ticker."""
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    df = fund_info.top_holdings
    return [FundTopHolding(**row.to_dict()) for _, row in df.reset_index().iterrows()]


def get_fund_bond_holdings(ticker: str) -> list[FundBondHolding]:
    """Retrieve bond holdings of a fund for a given ticker."""
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    df = fund_info.bond_holdings
    return [FundBondHolding(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]


def get_fund_equity_holdings(ticker: str) -> list[FundEquityHolding]:
    """Fetch equity holdings of a fund for a given ticker."""
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    df = fund_info.equity_holdings
    return [FundEquityHolding(**row.to_dict()) for _, row in df.transpose().reset_index().iterrows()]


def get_fund_asset_class_holdings(ticker: str) -> FundAssetClassHolding:
    """Get asset class holdings of a fund for a given ticker."""
    fund_ticker = yf.Ticker(ticker)
    fund_info = fund_ticker.get_funds_data()
    return FundAssetClassHolding(**fund_info.asset_classes)
