"""Unit tests for YFinanceTechnicalAnalysisRepository."""

from unittest.mock import patch

import pandas as pd
import pytest

from openmarkets.repositories.technical_analysis import (
    YFinanceTechnicalAnalysisRepository,
)


class TestYFinanceTechnicalAnalysisRepository:
    """Test suite for YFinanceTechnicalAnalysisRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = YFinanceTechnicalAnalysisRepository()
        self.ticker = "AAPL"

    @patch("yfinance.Ticker")
    def test_get_technical_indicators_success(self, mock_ticker):
        """Test successful retrieval of technical indicators."""
        df = pd.DataFrame(
            {
                "Close": [100.0, 101.0, 102.0, 103.0, 104.0] * 50,
                "High": [105.0, 106.0, 107.0, 108.0, 109.0] * 50,
                "Low": [95.0, 96.0, 97.0, 98.0, 99.0] * 50,
                "Volume": [1000000] * 250,
            }
        )
        mock_ticker.return_value.history.return_value = df

        result = self.repo.get_technical_indicators(self.ticker)

        assert isinstance(result, dict)
        assert "current_price" in result
        assert "fifty_two_week_high" in result
        assert "fifty_two_week_low" in result
        assert "average_volume" in result
        assert "sma_20" in result
        assert "sma_50" in result
        assert "sma_200" in result
        assert result["current_price"] == 104.0

    @patch("yfinance.Ticker")
    def test_get_technical_indicators_empty_history(self, mock_ticker):
        """Test ValueError when history is empty."""
        mock_ticker.return_value.history.return_value = pd.DataFrame()

        with pytest.raises(ValueError, match="No historical data available"):
            self.repo.get_technical_indicators(self.ticker)

    @patch("yfinance.Ticker")
    def test_get_technical_indicators_with_insufficient_data_for_sma(self, mock_ticker):
        """Test technical indicators with insufficient data for all SMAs."""
        df = pd.DataFrame(
            {
                "Close": [100.0, 101.0, 102.0, 103.0, 104.0],
                "High": [105.0, 106.0, 107.0, 108.0, 109.0],
                "Low": [95.0, 96.0, 97.0, 98.0, 99.0],
                "Volume": [1000000] * 5,
            }
        )
        mock_ticker.return_value.history.return_value = df

        result = self.repo.get_technical_indicators(self.ticker)

        assert result["sma_20"] is None
        assert result["sma_50"] is None
        assert result["sma_200"] is None

    @patch("yfinance.Ticker")
    def test_get_technical_indicators_with_zero_price_range(self, mock_ticker):
        """Test when 52-week high equals low (zero range)."""
        df = pd.DataFrame(
            {
                "Close": [100.0] * 250,
                "High": [100.0] * 250,
                "Low": [100.0] * 250,
                "Volume": [1000000] * 250,
            }
        )
        mock_ticker.return_value.history.return_value = df

        result = self.repo.get_technical_indicators(self.ticker)

        assert result["price_position_in_52w_range_percent"] is None

    @patch("yfinance.Ticker")
    def test_calculate_sma_insufficient_data(self, mock_ticker):
        """Test SMA calculation with insufficient data."""
        df = pd.DataFrame({"Close": [100.0, 101.0, 102.0]})

        result = self.repo._calculate_sma(df, window=20)

        assert result is None

    @patch("yfinance.Ticker")
    def test_calculate_sma_sufficient_data(self, mock_ticker):
        """Test SMA calculation with sufficient data."""
        df = pd.DataFrame({"Close": list(range(1, 51))})

        result = self.repo._calculate_sma(df, window=20)

        assert result is not None
        assert isinstance(result, (float, int))

    def test_calculate_price_position_zero_range(self):
        """Test price position calculation with zero range."""
        result = self.repo._calculate_price_position(100.0, 100.0, 100.0)

        assert result is None

    def test_calculate_price_position_valid_range(self):
        """Test price position calculation with valid range."""
        result = self.repo._calculate_price_position(150.0, 100.0, 200.0)

        assert result == 50.0

    def test_calculate_price_vs_sma_none(self):
        """Test price vs SMA when SMA is None."""
        result = self.repo._calculate_price_vs_sma(100.0, None)

        assert result is None

    def test_calculate_price_vs_sma_zero(self):
        """Test price vs SMA when SMA is zero."""
        result = self.repo._calculate_price_vs_sma(100.0, 0.0)

        assert result is None

    def test_calculate_price_vs_sma_valid(self):
        """Test price vs SMA with valid values."""
        result = self.repo._calculate_price_vs_sma(110.0, 100.0)

        assert result == 10.0

    @patch("yfinance.Ticker")
    def test_get_volatility_metrics_success(self, mock_ticker):
        """Test successful retrieval of volatility metrics."""
        df = pd.DataFrame({"Close": [100.0, 102.0, 101.0, 105.0, 103.0] * 50})
        mock_ticker.return_value.history.return_value = df

        result = self.repo.get_volatility_metrics(self.ticker)

        assert isinstance(result, dict)
        assert "daily_volatility" in result
        assert "annualized_volatility" in result
        assert "max_daily_gain_percent" in result
        assert "max_daily_loss_percent" in result
        assert "positive_days" in result
        assert "negative_days" in result
        assert "total_trading_days" in result
        assert "positive_days_percentage" in result

    @patch("yfinance.Ticker")
    def test_get_volatility_metrics_empty_history(self, mock_ticker):
        """Test ValueError when history is empty."""
        mock_ticker.return_value.history.return_value = pd.DataFrame()

        with pytest.raises(ValueError, match="No historical data available"):
            self.repo.get_volatility_metrics(self.ticker)

    def test_calculate_annualized_volatility(self):
        """Test annualized volatility calculation."""
        result = self.repo._calculate_annualized_volatility(0.02)

        expected = 0.02 * (252**0.5)
        assert abs(result - expected) < 0.0001

    def test_calculate_positive_days_percentage_zero_days(self):
        """Test positive days percentage with zero total days."""
        result = self.repo._calculate_positive_days_percentage(0, 0)

        assert result == 0.0

    def test_calculate_positive_days_percentage_valid(self):
        """Test positive days percentage with valid values."""
        result = self.repo._calculate_positive_days_percentage(75, 100)

        assert result == 75.0

    @patch("yfinance.Ticker")
    def test_get_support_resistance_levels_success(self, mock_ticker):
        """Test successful retrieval of support and resistance levels."""
        df = pd.DataFrame(
            {
                "Close": [100.0] * 100,
                "High": list(range(90, 190)),
                "Low": list(range(50, 150)),
            }
        )
        mock_ticker.return_value.history.return_value = df

        result = self.repo.get_support_resistance_levels(self.ticker)

        assert isinstance(result, dict)
        assert "current_price" in result
        assert "resistance_levels" in result
        assert "support_levels" in result
        assert "nearest_resistance" in result
        assert "nearest_support" in result
        assert result["current_price"] == 100.0

    @patch("yfinance.Ticker")
    def test_get_support_resistance_levels_empty_history(self, mock_ticker):
        """Test ValueError when history is empty."""
        mock_ticker.return_value.history.return_value = pd.DataFrame()

        with pytest.raises(ValueError, match="No historical data available"):
            self.repo.get_support_resistance_levels(self.ticker)

    def test_extract_resistance_levels(self):
        """Test extraction of resistance levels."""
        highs = pd.Series([100, 110, 120, 130, 140, 150, 160, 170, 180, 190])
        current_price = 125.0

        result = self.repo._extract_resistance_levels(highs, current_price)

        assert isinstance(result, list)
        assert all(level > current_price for level in result)
        assert len(result) <= 5

    def test_extract_support_levels(self):
        """Test extraction of support levels."""
        lows = pd.Series([50, 60, 70, 80, 90, 100, 110, 120, 130, 140])
        current_price = 95.0

        result = self.repo._extract_support_levels(lows, current_price)

        assert isinstance(result, list)
        assert all(level < current_price for level in result)
        assert len(result) <= 5

    def test_get_nearest_resistance_empty_list(self):
        """Test nearest resistance with empty list."""
        result = self.repo._get_nearest_resistance([])

        assert result is None

    def test_get_nearest_resistance_valid_list(self):
        """Test nearest resistance with valid list."""
        result = self.repo._get_nearest_resistance([150.0, 160.0, 170.0])

        assert result == 150.0

    def test_get_nearest_support_empty_list(self):
        """Test nearest support with empty list."""
        result = self.repo._get_nearest_support([])

        assert result is None

    def test_get_nearest_support_valid_list(self):
        """Test nearest support with valid list."""
        result = self.repo._get_nearest_support([90.0, 80.0, 70.0])

        assert result == 90.0

    def test_build_indicators_dict(self):
        """Test building indicators dictionary."""
        result = self.repo._build_indicators_dict(
            current_price=100.0,
            high_52w=120.0,
            low_52w=80.0,
            avg_volume=1000000.0,
            price_position=50.0,
            sma_20=98.0,
            sma_50=97.0,
            sma_200=95.0,
        )

        assert isinstance(result, dict)
        assert result["current_price"] == 100.0
        assert result["fifty_two_week_high"] == 120.0
        assert result["sma_20"] == 98.0

    def test_build_indicators_dict_with_none_values(self):
        """Test building indicators dictionary with None values."""
        result = self.repo._build_indicators_dict(
            current_price=100.0,
            high_52w=120.0,
            low_52w=80.0,
            avg_volume=1000000.0,
            price_position=None,
            sma_20=None,
            sma_50=None,
            sma_200=None,
        )

        assert result["price_position_in_52w_range_percent"] is None
        assert result["sma_20"] is None
        assert result["price_vs_sma_20"] is None

    def test_build_volatility_dict(self):
        """Test building volatility dictionary."""
        result = self.repo._build_volatility_dict(
            daily_volatility=0.02,
            annualized_volatility=0.32,
            max_daily_gain=0.05,
            max_daily_loss=-0.03,
            positive_days=150,
            negative_days=100,
            total_days=250,
        )

        assert isinstance(result, dict)
        assert result["daily_volatility"] == 0.02
        assert result["annualized_volatility"] == 0.32
        assert result["positive_days"] == 150

    def test_build_levels_dict(self):
        """Test building levels dictionary."""
        result = self.repo._build_levels_dict(
            current_price=100.0,
            resistance_levels=[110.0, 120.0, 130.0],
            support_levels=[90.0, 80.0, 70.0],
        )

        assert isinstance(result, dict)
        assert result["current_price"] == 100.0
        assert result["nearest_resistance"] == 110.0
        assert result["nearest_support"] == 90.0

    def test_build_levels_dict_with_empty_levels(self):
        """Test building levels dictionary with empty level lists."""
        result = self.repo._build_levels_dict(
            current_price=100.0,
            resistance_levels=[],
            support_levels=[],
        )

        assert result["nearest_resistance"] is None
        assert result["nearest_support"] is None
