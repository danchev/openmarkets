"""Unit tests for YFinanceHoldingsRepository."""

from unittest.mock import patch

import pandas as pd

from openmarkets.repositories.holdings import YFinanceHoldingsRepository


class TestYFinanceHoldingsRepository:
    """Test suite for YFinanceHoldingsRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = YFinanceHoldingsRepository()
        self.ticker = "AAPL"

    @patch("yfinance.Ticker")
    def test_get_major_holders(self, mock_ticker):
        """Test major holders retrieval."""
        df = pd.DataFrame([[0.5], [0.3]], index=["Value", "Breakdown"], columns=["Inst"])
        mock_ticker.return_value.get_major_holders.return_value = df

        result = self.repo.get_major_holders(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_institutional_holdings(self, mock_ticker):
        """Test institutional holdings retrieval."""
        df = pd.DataFrame(
            {
                "Holder": ["Vanguard", "BlackRock"],
                "Shares": [1000000, 900000],
                "Date Reported": ["2024-01-01", "2024-01-01"],
                "% Out": [0.05, 0.045],
                "Value": [100000000, 90000000],
            }
        )
        mock_ticker.return_value.get_institutional_holders.return_value = df

        result = self.repo.get_institutional_holdings(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_mutual_fund_holdings(self, mock_ticker):
        """Test mutual fund holdings retrieval."""
        df = pd.DataFrame(
            {
                "Holder": ["Fund A", "Fund B"],
                "Shares": [500000, 450000],
                "Date Reported": ["2024-01-01", "2024-01-01"],
                "% Out": [0.025, 0.0225],
                "Value": [50000000, 45000000],
            }
        )
        mock_ticker.return_value.get_mutualfund_holders.return_value = df

        result = self.repo.get_mutual_fund_holdings(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_insider_purchases(self, mock_ticker):
        """Test insider purchases retrieval."""
        df = pd.DataFrame(
            {
                "Insider Purchases Last 6m": ["10"],
                "Shares": [1000],
                "Trans": [5],
                "Value": [100000],
            }
        )
        mock_ticker.return_value.get_insider_purchases.return_value = df

        result = self.repo.get_insider_purchases(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_insider_roster_holders(self, mock_ticker):
        """Test insider roster holders retrieval."""
        df = pd.DataFrame(
            {
                "Name": ["John Doe", "Jane Smith"],
                "Position": ["CEO", "CFO"],
                "Most Recent Transaction": ["Buy", "Sell"],
                "Latest Trans Date": ["2024-01-01", "2024-01-02"],
                "Shares Owned Directly": [10000, 5000],
            }
        )
        mock_ticker.return_value.get_insider_roster_holders.return_value = df

        result = self.repo.get_insider_roster_holders(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0
