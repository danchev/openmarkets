"""Unit tests for YFinanceFinancialsRepository."""

from unittest.mock import MagicMock, patch

import pandas as pd

from openmarkets.repositories.financials import YFinanceFinancialsRepository


class TestYFinanceFinancialsRepository:
    """Test suite for YFinanceFinancialsRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = YFinanceFinancialsRepository()
        self.ticker = "AAPL"

    @patch("yfinance.Ticker")
    def test_get_balance_sheet(self, mock_ticker):
        """Test balance sheet retrieval."""
        df = pd.DataFrame([[100000], [50000]], index=["TotalAssets", "TotalLiabilities"], columns=["2023-12-31"])
        mock_ticker.return_value.get_balance_sheet.return_value = df

        result = self.repo.get_balance_sheet(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_income_statement(self, mock_ticker):
        """Test income statement retrieval."""
        df = pd.DataFrame([[100000], [20000]], index=["TotalRevenue", "NetIncome"], columns=["2023-12-31"])
        mock_ticker.return_value.get_income_stmt.return_value = df

        result = self.repo.get_income_statement(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_ttm_income_statement(self, mock_ticker):
        """Test TTM income statement retrieval."""
        df = pd.DataFrame(
            [[100000], [20000]], index=["TotalRevenue", "NetIncome"], columns=[pd.Timestamp("2024-01-01")]
        )
        mock_instance = MagicMock()
        mock_instance.ttm_income_stmt = df
        mock_ticker.return_value = mock_instance

        result = self.repo.get_ttm_income_statement(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_ttm_cash_flow_statement(self, mock_ticker):
        """Test TTM cash flow statement retrieval."""
        df = pd.DataFrame(
            [[50000], [30000]], index=["OperatingCashFlow", "FreeCashFlow"], columns=[pd.Timestamp("2024-01-01")]
        )
        mock_instance = MagicMock()
        mock_instance.ttm_cash_flow = df
        mock_ticker.return_value = mock_instance

        result = self.repo.get_ttm_cash_flow_statement(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_financial_calendar(self, mock_ticker):
        """Test financial calendar retrieval."""
        calendar_data = {
            "Earnings Date": ["2024-01-15", "2024-01-16"],
            "Earnings Average": 1.5,
            "Earnings Low": 1.3,
            "Earnings High": 1.7,
        }
        mock_ticker.return_value.get_calendar.return_value = calendar_data

        result = self.repo.get_financial_calendar(self.ticker)

        assert result is not None

    @patch("yfinance.Ticker")
    def test_get_sec_filings(self, mock_ticker):
        """Test SEC filings retrieval."""
        filings_data = [
            {"date": "2024-01-01", "type": "10-K", "title": "Annual Report", "edgarUrl": "http://example.com"}
        ]
        mock_ticker.return_value.get_sec_filings.return_value = filings_data

        result = self.repo.get_sec_filings(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_eps_history(self, mock_ticker):
        """Test EPS history retrieval."""
        df = pd.DataFrame({"EPS Estimate": [1.5, 1.6], "Reported EPS": [1.55, 1.65]})
        mock_ticker.return_value.get_earnings_dates.return_value = df

        result = self.repo.get_eps_history(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_eps_history_none(self, mock_ticker):
        """Test EPS history when data is None."""
        mock_ticker.return_value.get_earnings_dates.return_value = None

        result = self.repo.get_eps_history(self.ticker)

        assert result == []

    @patch("yfinance.Ticker")
    def test_get_curated_financials(self, mock_ticker):
        """Test curated financial summary retrieval."""
        from openmarkets.schemas.financials import CuratedFinancialSummary

        mock_ticker.return_value.info = {
            "symbol": "AAPL",
            "totalRevenue": 380000000000.0,
            "grossProfits": 170000000000.0,
            "ebitda": 130000000000.0,
            "netIncomeToCommon": 100000000000.0,
            "freeCashflow": 105000000000.0,
            "operatingCashflow": 115000000000.0,
            "totalCash": 60000000000.0,
            "totalDebt": 110000000000.0,
            "currentRatio": 0.95,
            "debtToEquity": 145.0,
            "grossMargins": 0.44,
            "operatingMargins": 0.30,
            "profitMargins": 0.26,
            "returnOnEquity": 1.5,
            "returnOnAssets": 0.28,
        }

        result = self.repo.get_curated_financials(self.ticker)
        assert isinstance(result, CuratedFinancialSummary)
        assert result.symbol == "AAPL"
        assert result.total_revenue == 380000000000.0
        assert result.free_cashflow == 105000000000.0

    @patch("yfinance.Ticker")
    def test_zero_operating_income_is_not_replaced_by_ebitda(self, mock_ticker):
        mock_ticker.return_value.info = {"symbol": "ZERO", "operatingIncome": 0.0, "ebitda": 99.0}
        result = self.repo.get_curated_financials("ZERO")
        assert result.operating_income == 0.0
        assert result.ebitda == 99.0

    @patch("yfinance.Ticker")
    def test_none_collection_results_are_empty(self, mock_ticker):
        mock_ticker.return_value.get_balance_sheet.return_value = None
        mock_ticker.return_value.get_sec_filings.return_value = None
        assert self.repo.get_balance_sheet(self.ticker) == []
        assert self.repo.get_sec_filings(self.ticker) == []
