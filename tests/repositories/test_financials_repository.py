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
