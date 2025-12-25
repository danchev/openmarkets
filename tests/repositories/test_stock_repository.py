"""
Unit tests for YFinanceStockRepository to improve coverage for src/openmarkets/schemas/stock.py and related repository logic.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from openmarkets.repositories.stock import YFinanceStockRepository
from openmarkets.schemas.stock import (
    CorporateActions,
    NewsItem,
    StockDividends,
    StockFastInfo,
    StockHistory,
    StockInfo,
    StockSplit,
)


@pytest.mark.skipif(YFinanceStockRepository is None, reason="YFinanceStockRepository not available")
class TestYFinanceStockRepository:
    def setup_method(self):
        self.repo = YFinanceStockRepository()
        self.ticker = "AAPL"

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_fast_info(self, mock_ticker):
        mock_ticker.return_value.fast_info = {
            "currency": "USD",
            "dayHigh": 150.0,
            "dayLow": 145.0,
            "exchange": "NASDAQ",
            "fiftyDayAverage": 148.0,
            "lastPrice": 149.0,
            "lastVolume": 1000000,
            "marketCap": 2000000000,
            "open": 146.0,
            "previousClose": 147.0,
            "quoteType": "equity",
            "regularMarketPreviousClose": 147.0,
            "shares": 10000000,
            "tenDayAverageVolume": 900000,
            "threeMonthAverageVolume": 950000,
            "timezone": "EST",
            "twoHundredDayAverage": 140.0,
            "yearChange": 0.1,
            "yearHigh": 155.0,
            "yearLow": 130.0,
        }
        result = self.repo.get_fast_info(self.ticker)
        assert isinstance(result, StockFastInfo)
        assert result.currency == "USD"

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_info(self, mock_ticker):
        mock_ticker.return_value.info = {"currency": "USD", "marketCap": 2000000000}
        result = self.repo.get_info(self.ticker)
        assert isinstance(result, StockInfo)
        assert result.currency == "USD"

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_history(self, mock_ticker):
        df = pd.DataFrame(
            {
                "Date": [datetime(2023, 1, 1)],
                "Open": [100.0],
                "High": [110.0],
                "Low": [90.0],
                "Close": [105.0],
                "Volume": [1000],
                "Dividends": [0.5],
                "Stock Splits": [0],
            }
        )
        mock_ticker.return_value.history.return_value = df
        result = self.repo.get_history(self.ticker)
        assert isinstance(result, list)
        assert isinstance(result[0], StockHistory)

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_dividends(self, mock_ticker):
        # Provide a string date and float dividend to match StockDividends fields
        mock_ticker.return_value.dividends.to_dict.return_value = {"2023-01-01": 0.5}
        result = self.repo.get_dividends(self.ticker)
        assert isinstance(result, list)
        assert isinstance(result[0], StockDividends)

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_splits(self, mock_ticker):
        mock_ticker.return_value.splits.items.return_value = [("2023-01-01", 2)]
        result = self.repo.get_splits(self.ticker)
        assert isinstance(result, list)
        assert isinstance(result[0], StockSplit)

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_news(self, mock_ticker):
        # NewsItem requires 'id' and 'content' fields
        mock_ticker.return_value.news = [
            {"id": "news1", "content": {"title": "News Title", "link": "http://example.com"}}
        ]
        result = self.repo.get_news(self.ticker)
        assert isinstance(result, list)
        assert isinstance(result[0], NewsItem)

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_corporate_actions(self, mock_ticker):
        # CorporateActions requires 'Date' field (datetime or string)
        mock_df = MagicMock()
        mock_df.reset_index.return_value.iterrows.return_value = [
            (0, MagicMock(to_dict=lambda: {"Date": "2023-01-01", "Dividends": 0.5, "Stock Splits": 2.0}))
        ]
        mock_ticker.return_value.actions = mock_df
        result = self.repo.get_corporate_actions(self.ticker)
        assert isinstance(result, list)
        assert isinstance(result[0], CorporateActions)

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_financial_summary(self, mock_ticker):
        mock_ticker.return_value.info = {"totalRevenue": 100, "revenueGrowth": 0.1}
        result = self.repo.get_financial_summary(self.ticker)
        assert isinstance(result, dict)
        assert "totalRevenue" in result

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_risk_metrics(self, mock_ticker):
        mock_ticker.return_value.info = {"auditRisk": 1, "boardRisk": 2}
        result = self.repo.get_risk_metrics(self.ticker)
        assert isinstance(result, dict)
        assert "auditRisk" in result

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_dividend_summary(self, mock_ticker):
        mock_ticker.return_value.info = {"dividendRate": 1.5, "dividendYield": 0.02}
        result = self.repo.get_dividend_summary(self.ticker)
        assert isinstance(result, dict)
        assert "dividendRate" in result

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_price_target(self, mock_ticker):
        mock_ticker.return_value.info = {"targetHighPrice": 200.0, "targetLowPrice": 150.0}
        result = self.repo.get_price_target(self.ticker)
        assert isinstance(result, dict)
        assert "targetHighPrice" in result

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_financial_summary_v2(self, mock_ticker):
        mock_ticker.return_value.info = {"marketCap": 1000000000, "enterpriseValue": 900000000}
        result = self.repo.get_financial_summary_v2(self.ticker)
        assert isinstance(result, dict)
        assert "marketCap" in result

    @patch("openmarkets.repositories.stock.yf.Ticker")
    def test_get_quick_technical_indicators(self, mock_ticker):
        mock_ticker.return_value.info = {"currentPrice": 150.0, "fiftyDayAverage": 148.0}
        result = self.repo.get_quick_technical_indicators(self.ticker)
        assert isinstance(result, dict)
        assert "currentPrice" in result

    def test_get_history_invalid_period(self):
        """Test get_history with invalid period"""
        with pytest.raises(ValueError, match="Invalid period"):
            self.repo.get_history(self.ticker, period="invalid")

    def test_get_history_invalid_interval(self):
        """Test get_history with invalid interval"""
        with pytest.raises(ValueError, match="Invalid interval"):
            self.repo.get_history(self.ticker, interval="invalid")
