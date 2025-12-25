"""Unit tests for YFinanceFundsRepository."""

from unittest.mock import MagicMock, patch

import pandas as pd

from openmarkets.repositories.funds import YFinanceFundsRepository


class TestYFinanceFundsRepository:
    """Test suite for YFinanceFundsRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = YFinanceFundsRepository()
        self.ticker = "SPY"

    @patch("yfinance.Ticker")
    def test_get_fund_info(self, mock_ticker):
        """Test fund info retrieval."""
        info_data = {"fundFamily": "Test Family", "category": "Large Blend"}
        mock_ticker.return_value.info = info_data

        result = self.repo.get_fund_info(self.ticker)

        assert result is not None

    @patch("yfinance.Ticker")
    def test_get_fund_sector_weighting(self, mock_ticker):
        """Test fund sector weighting retrieval."""
        mock_fund_data = MagicMock()
        mock_fund_data.sector_weightings = {"technology": 0.3, "healthcare": 0.2}
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_sector_weighting(self.ticker)

        assert result is not None

    @patch("yfinance.Ticker")
    def test_get_fund_sector_weighting_none(self, mock_ticker):
        """Test fund sector weighting when data is None."""
        mock_ticker.return_value.get_funds_data.return_value = None

        result = self.repo.get_fund_sector_weighting(self.ticker)

        assert result is None

    @patch("yfinance.Ticker")
    def test_get_fund_sector_weighting_no_attr(self, mock_ticker):
        """Test fund sector weighting when attribute doesn't exist."""
        mock_fund_data = MagicMock(spec=[])
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_sector_weighting(self.ticker)

        assert result is None

    @patch("yfinance.Ticker")
    def test_get_fund_operations(self, mock_ticker):
        """Test fund operations retrieval."""
        ops_data = {"fundInceptionDate": "2000-01-01", "annualReportExpenseRatio": 0.09}
        mock_fund_data = MagicMock()
        mock_fund_data.fund_operations = ops_data
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_operations(self.ticker)

        assert result is not None

    @patch("yfinance.Ticker")
    def test_get_fund_operations_none(self, mock_ticker):
        """Test fund operations when data is None."""
        mock_ticker.return_value.get_funds_data.return_value = None

        result = self.repo.get_fund_operations(self.ticker)

        assert result is None

    @patch("yfinance.Ticker")
    def test_get_fund_operations_no_attr(self, mock_ticker):
        """Test fund operations when attribute doesn't exist."""
        mock_fund_data = MagicMock(spec=[])
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_operations(self.ticker)

        assert result is None

    @patch("yfinance.Ticker")
    def test_get_fund_overview(self, mock_ticker):
        """Test fund overview retrieval."""
        overview_data = {"ratingOverall": 5, "riskOverall": 3}
        mock_fund_data = MagicMock()
        mock_fund_data.fund_overview = overview_data
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_overview(self.ticker)

        assert result is not None

    @patch("yfinance.Ticker")
    def test_get_fund_overview_none(self, mock_ticker):
        """Test fund overview when data is None."""
        mock_ticker.return_value.get_funds_data.return_value = None

        result = self.repo.get_fund_overview(self.ticker)

        assert result is None

    @patch("yfinance.Ticker")
    def test_get_fund_overview_no_attr(self, mock_ticker):
        """Test fund overview when attribute doesn't exist."""
        mock_fund_data = MagicMock(spec=[])
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_overview(self.ticker)

        assert result is None

    @patch("yfinance.Ticker")
    def test_get_fund_top_holdings(self, mock_ticker):
        """Test fund top holdings retrieval."""
        df = pd.DataFrame(
            {"Symbol": ["AAPL", "MSFT"], "Name": ["Apple Inc", "Microsoft Corp"], "Holding Percent": [0.05, 0.04]}
        )
        mock_fund_data = MagicMock()
        mock_fund_data.top_holdings = df
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_top_holdings(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_fund_top_holdings_none(self, mock_ticker):
        """Test fund top holdings when data is None."""
        mock_ticker.return_value.get_funds_data.return_value = None

        result = self.repo.get_fund_top_holdings(self.ticker)

        assert result == []

    @patch("yfinance.Ticker")
    def test_get_fund_top_holdings_no_attr(self, mock_ticker):
        """Test fund top holdings when attribute doesn't exist."""
        mock_fund_data = MagicMock(spec=[])
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_top_holdings(self.ticker)

        assert result == []

    @patch("yfinance.Ticker")
    def test_get_fund_bond_holdings(self, mock_ticker):
        """Test fund bond holdings retrieval."""
        df = pd.DataFrame([[5.0], [10.0]], index=["duration", "maturity"], columns=["Bonds"])
        mock_fund_data = MagicMock()
        mock_fund_data.bond_holdings = df
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_bond_holdings(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_fund_bond_holdings_none(self, mock_ticker):
        """Test fund bond holdings when data is None."""
        mock_ticker.return_value.get_funds_data.return_value = None

        result = self.repo.get_fund_bond_holdings(self.ticker)

        assert result == []

    @patch("yfinance.Ticker")
    def test_get_fund_bond_holdings_no_attr(self, mock_ticker):
        """Test fund bond holdings when attribute doesn't exist."""
        mock_fund_data = MagicMock(spec=[])
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_bond_holdings(self.ticker)

        assert result == []

    @patch("yfinance.Ticker")
    def test_get_fund_equity_holdings(self, mock_ticker):
        """Test fund equity holdings retrieval."""
        df = pd.DataFrame([[15.0], [2.5]], index=["priceToEarnings", "priceToBook"], columns=["Equity"])
        mock_fund_data = MagicMock()
        mock_fund_data.equity_holdings = df
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_equity_holdings(self.ticker)

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("yfinance.Ticker")
    def test_get_fund_equity_holdings_none(self, mock_ticker):
        """Test fund equity holdings when data is None."""
        mock_ticker.return_value.get_funds_data.return_value = None

        result = self.repo.get_fund_equity_holdings(self.ticker)

        assert result == []

    @patch("yfinance.Ticker")
    def test_get_fund_equity_holdings_no_attr(self, mock_ticker):
        """Test fund equity holdings when attribute doesn't exist."""
        mock_fund_data = MagicMock(spec=[])
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_equity_holdings(self.ticker)

        assert result == []

    @patch("yfinance.Ticker")
    def test_get_fund_asset_class_holdings(self, mock_ticker):
        """Test fund asset class holdings retrieval."""
        asset_classes = {"stock": 0.7, "bond": 0.3}
        mock_fund_data = MagicMock()
        mock_fund_data.asset_classes = asset_classes
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_asset_class_holdings(self.ticker)

        assert result is not None

    @patch("yfinance.Ticker")
    def test_get_fund_asset_class_holdings_none(self, mock_ticker):
        """Test fund asset class holdings when data is None."""
        mock_ticker.return_value.get_funds_data.return_value = None

        result = self.repo.get_fund_asset_class_holdings(self.ticker)

        assert result is None

    @patch("yfinance.Ticker")
    def test_get_fund_asset_class_holdings_no_attr(self, mock_ticker):
        """Test fund asset class holdings when attribute doesn't exist."""
        mock_fund_data = MagicMock(spec=[])
        mock_ticker.return_value.get_funds_data.return_value = mock_fund_data

        result = self.repo.get_fund_asset_class_holdings(self.ticker)

        assert result is None
