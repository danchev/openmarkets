"""Unit tests for YFinanceMarketsRepository."""

from unittest.mock import MagicMock, patch

from openmarkets.repositories.markets import YFinanceMarketsRepository


class TestYFinanceMarketsRepository:
    """Test suite for YFinanceMarketsRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = YFinanceMarketsRepository()
        self.market = "us_market"

    @patch("yfinance.Market")
    def test_get_market_summary(self, mock_market):
        """Test market summary retrieval."""
        summary_data = {
            "^GSPC": {
                "symbol": "^GSPC",
                "shortName": "S&P 500",
                "regularMarketPrice": 4500.0,
                "regularMarketChange": 50.0,
                "regularMarketChangePercent": 1.12,
            }
        }
        mock_instance = MagicMock()
        mock_instance.summary = summary_data
        mock_market.return_value = mock_instance

        result = self.repo.get_market_summary(self.market)

        assert result is not None
        assert hasattr(result, "summary")
        assert "^GSPC" in result.summary

    @patch("yfinance.Market")
    def test_get_market_status(self, mock_market):
        """Test market status retrieval."""
        status_data = {
            "market": "us_market",
            "marketState": "REGULAR",
            "timezone": {"gmtOffset": -18000},
        }
        mock_instance = MagicMock()
        mock_instance.status = status_data
        mock_market.return_value = mock_instance

        result = self.repo.get_market_status(self.market)

        assert result is not None
