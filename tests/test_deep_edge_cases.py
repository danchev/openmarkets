"""Exhaustive deep edge-case validation test suite across all 15 domain services."""

from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
import pytest

from openmarkets.core.exceptions import DataUnavailableError
from openmarkets.repositories.analysis import YFinanceAnalysisRepository
from openmarkets.repositories.crypto import YFinanceCryptoRepository
from openmarkets.repositories.financials import YFinanceFinancialsRepository
from openmarkets.repositories.fixed_income import WSJFixedIncomeRepository
from openmarkets.repositories.funds import YFinanceFundsRepository
from openmarkets.repositories.holdings import YFinanceHoldingsRepository
from openmarkets.repositories.macroeconomics import FREDMacroeconomicsRepository
from openmarkets.repositories.options import YFinanceOptionsRepository
from openmarkets.repositories.sector_industry import YFinanceSectorIndustryRepository
from openmarkets.repositories.stock import WSJStockRepository, YFinanceStockRepository
from openmarkets.repositories.technical_analysis import YFinanceTechnicalAnalysisRepository
from openmarkets.services.forex import ForexService


# ---------------------------------------------------------------------------
# 1. Stock & Equities Edge Cases
# ---------------------------------------------------------------------------
def test_stock_edge_case_empty_corporate_actions():
    repo = YFinanceStockRepository()
    with patch("openmarkets.repositories.stock.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.actions = None
        actions = repo.get_corporate_actions("XYZ")
        assert actions == []


def test_stock_edge_case_empty_dividends_and_splits():
    repo = YFinanceStockRepository()
    with patch("openmarkets.repositories.stock.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.dividends = None
        mock_ticker.return_value.splits = None
        divs = repo.get_dividends("XYZ")
        splits = repo.get_splits("XYZ")
        assert divs == []
        assert splits == []


def test_stock_edge_case_valuation_history_empty_for_crypto():
    repo = YFinanceStockRepository()
    with patch("openmarkets.repositories.stock.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.get_valuation_measures.return_value = pd.DataFrame()
        val = repo.get_valuation_history("BTC-USD")
        assert val == []


def test_stock_wsj_edge_case_zero_ticks_intraday():
    repo = WSJStockRepository()
    with patch("openmarkets.repositories.stock.fetch_wsj_timeseries", return_value={"TimeInfo": {"Ticks": []}}):
        bars = repo.get_stock_history("TSLA", timeframe="1d")
        assert bars.data_points == []


# ---------------------------------------------------------------------------
# 2. Options & Derivatives Edge Cases
# ---------------------------------------------------------------------------
def test_options_edge_case_no_options_chain():
    repo = YFinanceOptionsRepository()
    with patch("openmarkets.repositories.options.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.options = ()
        expirations = repo.get_option_expiration_dates("NO_OPTIONS_TICKER")
        assert expirations == []


# ---------------------------------------------------------------------------
# 3. Financial Statements Edge Cases
# ---------------------------------------------------------------------------
def test_financials_edge_case_missing_sec_filings():
    repo = YFinanceFinancialsRepository()
    with patch("openmarkets.repositories.financials.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.get_sec_filings.return_value = None
        filings = repo.get_sec_filings("FOREIGN_ADR")
        assert filings == []


def test_financials_edge_case_empty_financial_calendar():
    repo = YFinanceFinancialsRepository()
    with patch("openmarkets.repositories.financials.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.get_calendar.return_value = None
        with pytest.raises(DataUnavailableError):
            repo.get_financial_calendar("TICKER")


# ---------------------------------------------------------------------------
# 4. Analyst Estimates Edge Cases
# ---------------------------------------------------------------------------
def test_analysis_edge_case_zero_analyst_coverage():
    repo = YFinanceAnalysisRepository()
    with patch("openmarkets.repositories.analysis.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.upgrades_downgrades = None
        recs = repo.get_recommendation_changes("MICRO_CAP")
        assert recs == []


# ---------------------------------------------------------------------------
# 5. Institutional & Insider Holdings Edge Cases
# ---------------------------------------------------------------------------
def test_holdings_edge_case_empty_insider_purchases():
    repo = YFinanceHoldingsRepository()
    with patch("openmarkets.repositories.holdings.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.get_insider_purchases.return_value = None
        purchases = repo.get_insider_purchases("IPO_COMPANY")
        assert purchases == []


# ---------------------------------------------------------------------------
# 6. Sector & Industry Edge Cases
# ---------------------------------------------------------------------------
def test_sector_industry_edge_case_missing_reports():
    repo = YFinanceSectorIndustryRepository()
    with patch("openmarkets.repositories.sector_industry.yf.Sector") as mock_sec:
        mock_sec.return_value.research_reports = None
        reports = repo.get_sector_research_reports("technology")
        assert reports == []


# ---------------------------------------------------------------------------
# 7. Foreign Exchange Edge Cases
# ---------------------------------------------------------------------------
def test_forex_edge_case_valid_and_inverted():
    svc = ForexService()
    mock_ts = {
        "TimeInfo": {"Ticks": [1616457600000]},
        "Series": [{"DataPoints": [[1.085]]}],
    }
    with patch("openmarkets.repositories.forex.fetch_wsj_timeseries", return_value=mock_ts):
        quote_slash = svc.get_forex_quote("EUR/USD")
        quote_no_slash = svc.get_forex_quote("EURUSD")
        assert quote_slash.pair == "EURUSD"
        assert quote_no_slash.pair == "EURUSD"
        assert quote_slash.rate == 1.085
        assert quote_no_slash.rate == 1.085


# ---------------------------------------------------------------------------
# 8. Cryptocurrency Edge Cases
# ---------------------------------------------------------------------------
def test_crypto_edge_case_unknown_symbol():
    from openmarkets.core.exceptions import InvalidSymbolError

    repo = YFinanceCryptoRepository()
    with patch("openmarkets.repositories.crypto.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.fast_info = {}
        with pytest.raises(InvalidSymbolError):
            repo.get_crypto_info("NON_EXISTENT_COIN_XYZ")


# ---------------------------------------------------------------------------
# 9. Funds & ETFs Edge Cases
# ---------------------------------------------------------------------------
def test_funds_edge_case_pure_equity_has_no_bonds():
    repo = YFinanceFundsRepository()
    with patch("openmarkets.repositories.funds.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.get_funds_data.return_value = SimpleNamespace(bond_holdings=None)
        bonds = repo.get_fund_bond_holdings("SPY")
        assert bonds == []


def test_funds_edge_case_pure_bond_has_no_equities():
    repo = YFinanceFundsRepository()
    with patch("openmarkets.repositories.funds.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.get_funds_data.return_value = SimpleNamespace(equity_holdings=None)
        equities = repo.get_fund_equity_holdings("BND")
        assert equities == []


# ---------------------------------------------------------------------------
# 10. Technical Analysis Edge Cases
# ---------------------------------------------------------------------------
def test_technical_analysis_window_larger_than_data():
    repo = YFinanceTechnicalAnalysisRepository()
    import pandas as pd

    short_df = pd.DataFrame({"Close": [10.0, 11.0, 12.0]})
    sma = repo._calculate_sma(short_df, window=50)
    assert sma is None


def test_technical_analysis_zero_volatility():
    repo = YFinanceTechnicalAnalysisRepository()
    import pandas as pd

    flat_df = pd.DataFrame({"Close": [100.0] * 20})
    with patch("openmarkets.repositories.technical_analysis.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = flat_df
        vol = repo.get_volatility_metrics("STABLE")
        assert vol["daily_volatility"] == 0.0
        assert vol["annualized_volatility"] == 0.0


# ---------------------------------------------------------------------------
# 11. Fixed Income Yield Inversion Edge Cases
# ---------------------------------------------------------------------------
def test_fixed_income_curve_inversion_boundary():
    repo = WSJFixedIncomeRepository()

    # Case: Inverted (10Y < 2Y)
    def mock_fetch(wsj_key, **kwargs):
        val = 4.0 if "2Y" in wsj_key else 3.5
        return {"TimeInfo": {"Ticks": [1616457600000]}, "Series": [{"DataPoints": [[val]]}]}

    with patch("openmarkets.repositories.fixed_income.fetch_wsj_timeseries", side_effect=mock_fetch):
        curve = repo.get_treasury_yield_curve()
        assert curve.is_inverted is True
        assert curve.spread_2y_10y_bps == -50.0

    # Case: Normal (10Y > 2Y)
    def mock_fetch_normal(wsj_key, **kwargs):
        val = 3.5 if "2Y" in wsj_key else 4.2
        return {"TimeInfo": {"Ticks": [1616457600000]}, "Series": [{"DataPoints": [[val]]}]}

    with patch("openmarkets.repositories.fixed_income.fetch_wsj_timeseries", side_effect=mock_fetch_normal):
        curve_normal = repo.get_treasury_yield_curve()
        assert curve_normal.is_inverted is False
        assert curve_normal.spread_2y_10y_bps == 70.0


# ---------------------------------------------------------------------------
# 12. Macroeconomics Edge Cases
# ---------------------------------------------------------------------------
def test_macroeconomics_extreme_limit():
    repo = FREDMacroeconomicsRepository()
    mock_data = [{"date": f"2026-0{i}-01", "value": float(i)} for i in range(1, 6)]
    with patch("openmarkets.repositories.macroeconomics.fetch_fred_timeseries", return_value=mock_data):
        # Limit larger than data returns all data
        series = repo.get_series("CPIAUCSL", limit=1000)
        assert len(series.data_points) == 5

        with pytest.raises(ValueError, match="greater than zero"):
            repo.get_series("CPIAUCSL", limit=0)
