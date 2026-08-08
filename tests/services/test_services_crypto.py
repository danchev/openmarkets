"""Tests for CryptoService.

Verifies that the service layer correctly delegates to the repository
for all cryptocurrency methods.
"""

from datetime import datetime

import pytest

from openmarkets.repositories.crypto import ICryptoRepository
from openmarkets.schemas.crypto import CryptoFastInfo, CryptoHistory
from openmarkets.services.crypto import CryptoService


class CryptoRepositorySpy(ICryptoRepository):
    """Spy implementation of ICryptoRepository for testing."""

    def __init__(self):
        self.calls = {}

    def _record(self, method_name, *args, **kwargs):
        """Record a method call."""
        self.calls[method_name] = self.calls.get(method_name, 0) + 1

    def get_crypto_info(self, ticker, session=None):
        self._record("get_crypto_info", ticker)
        return CryptoFastInfo(
            **{
                "currency": "USD",
                "dayHigh": 50000.0,
                "dayLow": 49000.0,
                "exchange": "CCC",
                "fiftyDayAverage": 48000.0,
                "lastPrice": 49500.0,
                "lastVolume": 1000000,
                "open": 49200.0,
                "previousClose": 49000.0,
                "quoteType": "CRYPTOCURRENCY",
                "regularMarketPreviousClose": 49000.0,
                "tenDayAverageVolume": 1500000,
                "threeMonthAverageVolume": 2000000,
                "timezone": "UTC",
                "twoHundredDayAverage": 45000.0,
                "yearChange": 0.25,
                "yearlyChange": 0.30,
                "yearHigh": 55000.0,
                "yearLow": 35000.0,
                "circulatingSupply": 19000000,
                "fromCurrency": "BTC",
                "lastMarket": "Bitcoin",
                "marketCap": 940500000000,
                "regularMarketDayHigh": 50000.0,
                "regularMarketDayLow": 49000.0,
                "regularMarketOpen": 49200.0,
                "regularMarketVolume": 1000000,
                    "yearHigh": 55000.0,
                    "yearLow": 35000.0,
            }
        )

    def get_crypto_history(self, ticker, period="1y", interval="1d", session=None):
        self._record("get_crypto_history", ticker)
        return [
            CryptoHistory(
                **{
                    "Date": datetime(2024, 1, 1),
                    "Open": 42000.0,
                    "High": 43000.0,
                    "Low": 41500.0,
                    "Close": 42500.0,
                    "Volume": 1000000,
                }
            ),
            CryptoHistory(
                **{
                    "Date": datetime(2024, 1, 2),
                    "Open": 42500.0,
                    "High": 43500.0,
                    "Low": 42000.0,
                    "Close": 43000.0,
                    "Volume": 1200000,
                }
            ),
        ]

    def get_top_cryptocurrencies(self, count=10):
        self._record("get_top_cryptocurrencies", count)
        return [
            CryptoFastInfo(
                **{
                    "currency": "USD",
                    "dayHigh": 50000.0,
                    "dayLow": 49000.0,
                    "exchange": "CCC",
                    "fiftyDayAverage": 48000.0,
                    "lastPrice": 49500.0,
                    "lastVolume": 1000000,
                    "open": 49200.0,
                    "previousClose": 49000.0,
                    "quoteType": "CRYPTOCURRENCY",
                    "regularMarketPreviousClose": 49000.0,
                    "tenDayAverageVolume": 1500000,
                    "threeMonthAverageVolume": 2000000,
                    "timezone": "UTC",
                    "twoHundredDayAverage": 45000.0,
                    "yearChange": 0.25,
                    "yearlyChange": 0.30,
                    "circulatingSupply": 19000000,
                    "fromCurrency": "BTC",
                    "lastMarket": "Bitcoin",
                    "marketCap": 940500000000,
                    "regularMarketDayHigh": 50000.0,
                    "regularMarketDayLow": 49000.0,
                    "regularMarketOpen": 49200.0,
                    "regularMarketVolume": 1000000,
                    "yearHigh": 55000.0,
                    "yearLow": 35000.0,
                }
            ),
            CryptoFastInfo(
                **{
                    "currency": "USD",
                    "dayHigh": 3000.0,
                    "dayLow": 2900.0,
                    "exchange": "CCC",
                    "fiftyDayAverage": 2800.0,
                    "lastPrice": 2950.0,
                    "lastVolume": 500000,
                    "open": 2920.0,
                    "previousClose": 2900.0,
                    "quoteType": "CRYPTOCURRENCY",
                    "regularMarketPreviousClose": 2900.0,
                    "tenDayAverageVolume": 600000,
                    "threeMonthAverageVolume": 700000,
                    "timezone": "UTC",
                    "twoHundredDayAverage": 2500.0,
                    "yearChange": 0.15,
                    "yearlyChange": 0.20,
                    "circulatingSupply": 120000000,
                    "fromCurrency": "ETH",
                    "lastMarket": "Ethereum",
                    "marketCap": 354000000000,
                    "regularMarketDayHigh": 3000.0,
                    "regularMarketDayLow": 2900.0,
                    "regularMarketOpen": 2920.0,
                    "regularMarketVolume": 500000,
                    "yearHigh": 3500.0,
                    "yearLow": 2000.0,
                }
            ),
        ]

    def get_crypto_fear_greed_proxy(self, tickers=None, session=None):
        self._record("get_crypto_fear_greed_proxy", tickers)
        return "Fear"


@pytest.fixture
def spy_repository():
    """Create a spy repository for testing service delegation."""
    return CryptoRepositorySpy()


@pytest.fixture
def service(spy_repository):
    """Create CryptoService with spy repository."""
    return CryptoService(repository=spy_repository)


class TestCryptoServiceDelegatesToRepository:
    """Test that all service methods delegate to the repository."""

    def test_get_crypto_info(self, service, spy_repository):
        """Test that get_crypto_info delegates to repository."""
        result = service.get_crypto_info("BTC")
        assert result.last_price == 49500.0
        assert result.currency == "USD"
        assert spy_repository.calls["get_crypto_info"] == 1

    def test_get_crypto_history(self, service, spy_repository):
        """Test that get_crypto_history delegates to repository."""
        result = service.get_crypto_history("BTC")
        assert len(result) == 2
        assert result[0].close == 42500.0
        assert result[1].close == 43000.0
        assert spy_repository.calls["get_crypto_history"] == 1

    def test_get_crypto_history_with_params(self, service, spy_repository):
        """Test that get_crypto_history delegates with custom parameters."""
        result = service.get_crypto_history("ETH", period="6mo", interval="1wk")
        assert len(result) == 2
        assert spy_repository.calls["get_crypto_history"] == 1

    def test_get_top_cryptocurrencies(self, service, spy_repository):
        """Test that get_top_cryptocurrencies delegates to repository."""
        result = service.get_top_cryptocurrencies(count=5)
        assert len(result) == 2
        assert result[0].last_price == 49500.0
        assert result[1].last_price == 2950.0
        assert spy_repository.calls["get_top_cryptocurrencies"] == 1

    def test_get_crypto_fear_greed_proxy(self, service, spy_repository):
        """Test that get_crypto_fear_greed_proxy delegates to repository."""
        result = service.get_crypto_fear_greed_proxy()
        assert result == "Fear"
        assert spy_repository.calls["get_crypto_fear_greed_proxy"] == 1

    def test_get_crypto_fear_greed_proxy_with_tickers(self, service, spy_repository):
        """Test that get_crypto_fear_greed_proxy delegates with custom tickers."""
        result = service.get_crypto_fear_greed_proxy(tickers=["BTC", "ETH"])
        assert result == "Fear"
        assert spy_repository.calls["get_crypto_fear_greed_proxy"] == 1
