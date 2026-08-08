"""Unit tests for YFinanceCryptoRepository."""

import pandas as pd
import pytest

from openmarkets.core.exceptions import APIError
from openmarkets.repositories.crypto import YFinanceCryptoRepository
from openmarkets.schemas.crypto import CryptoFastInfo, CryptoHistory


class TestYFinanceCryptoRepository:
    """Test suite for YFinanceCryptoRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = YFinanceCryptoRepository()

    def test_get_crypto_info_adds_suffix(self, monkeypatch):
        """Test that ticker without -USD suffix gets it added."""

        class T:
            def __init__(self, t, session=None):
                self.fast_info = {
                    "currency": "USD",
                    "dayHigh": 2.0,
                    "dayLow": 1.0,
                    "exchange": "X",
                    "fiftyDayAverage": 1.5,
                    "lastPrice": 2.0,
                    "lastVolume": 100,
                    "open": 1.8,
                    "previousClose": 1.9,
                    "quoteType": "CRYPTOCURRENCY",
                    "regularMarketPreviousClose": 1.9,
                    "tenDayAverageVolume": 50,
                    "threeMonthAverageVolume": 60,
                    "timezone": "UTC",
                    "twoHundredDayAverage": 1.0,
                    "yearChange": 0.1,
                    "yearHigh": 3.0,
                    "yearLow": 0.5,
                }

        monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
        info = self.repo.get_crypto_info("BTC")
        assert isinstance(info, CryptoFastInfo)

    def test_get_crypto_history_validation(self, monkeypatch):
        """Test validation of period and interval parameters."""
        with pytest.raises(ValueError):
            self.repo.get_crypto_history("BTC", period="invalid")
        with pytest.raises(ValueError):
            self.repo.get_crypto_history("BTC", interval="bad")

    def test_get_crypto_history_returns_models(self, monkeypatch):
        """Test that get_crypto_history returns CryptoHistory models."""

        class T:
            def __init__(self, t, session=None):
                self._df = pd.DataFrame(
                    [
                        {
                            "Date": pd.Timestamp("2023-01-01"),
                            "Open": 1.0,
                            "High": 2.0,
                            "Low": 0.5,
                            "Close": 1.5,
                            "Volume": 100,
                        }
                    ]
                ).set_index("Date")

            def history(self, period="1y", interval="1d"):
                return self._df

        monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
        res = self.repo.get_crypto_history("BTC", period="1y", interval="1d")
        assert isinstance(res[0], CryptoHistory)

    def test_get_crypto_fear_greed_proxy(self, monkeypatch):
        """Test crypto fear and greed proxy calculation."""

        class T:
            def __init__(self, t, session=None):
                self._hist = pd.DataFrame(
                    [
                        {"Close": 100},
                        {"Close": 105},
                        {"Close": 115},
                    ]
                )

            def history(self, period="7d"):
                return self._hist

        monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
        out = self.repo.get_crypto_fear_greed_proxy(["BTC-USD"])
        assert out.sentiment_proxy

    def test_get_crypto_fear_greed_proxy_error_handling(self, monkeypatch):
        """Test error handling in fear and greed proxy."""

        class TErr:
            def __init__(self, t, session=None):
                pass

            def history(self, period="7d"):
                raise RuntimeError("oops")

        monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": TErr}))
        with pytest.raises(APIError):
            self.repo.get_crypto_fear_greed_proxy(["BTC-USD"])

    def test_get_crypto_info_already_has_suffix(self, monkeypatch):
        """Test that ticker already ending with -USD is not modified."""

        class T:
            def __init__(self, ticker, session=None):
                self.ticker = ticker
                self.fast_info = {
                    "currency": "USD",
                    "dayHigh": 2.0,
                    "dayLow": 1.0,
                    "exchange": "X",
                    "fiftyDayAverage": 1.5,
                    "lastPrice": 2.0,
                    "lastVolume": 100,
                    "open": 1.8,
                    "previousClose": 1.9,
                    "quoteType": "CRYPTOCURRENCY",
                    "regularMarketPreviousClose": 1.9,
                    "tenDayAverageVolume": 50,
                    "threeMonthAverageVolume": 60,
                    "timezone": "UTC",
                    "twoHundredDayAverage": 1.0,
                    "yearChange": 0.1,
                    "yearHigh": 3.0,
                    "yearLow": 0.5,
                }

        monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
        info = self.repo.get_crypto_info("BTC-USD")
        assert isinstance(info, CryptoFastInfo)

    def test_get_top_cryptocurrencies(self, monkeypatch):
        """Test fetching top cryptocurrencies."""

        class T:
            def __init__(self, ticker, session=None):
                self.fast_info = {
                    "currency": "USD",
                    "dayHigh": 2.0,
                    "dayLow": 1.0,
                    "exchange": "X",
                    "fiftyDayAverage": 1.5,
                    "lastPrice": 2.0,
                    "lastVolume": 100,
                    "open": 1.8,
                    "previousClose": 1.9,
                    "quoteType": "CRYPTOCURRENCY",
                    "regularMarketPreviousClose": 1.9,
                    "tenDayAverageVolume": 50,
                    "threeMonthAverageVolume": 60,
                    "timezone": "UTC",
                    "twoHundredDayAverage": 1.0,
                    "yearChange": 0.1,
                    "yearHigh": 3.0,
                    "yearLow": 0.5,
                }

        monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
        result = self.repo.get_top_cryptocurrencies(count=3)
        assert len(result) == 3
        assert all(isinstance(info, CryptoFastInfo) for info in result)

    def test_fetch_crypto_sentiment_insufficient_history(self, monkeypatch):
        """Test sentiment fetch when history has less than 2 data points."""

        class T:
            def __init__(self, t, session=None):
                # Only 1 day of history
                self._hist = pd.DataFrame([{"Close": 100}])

            def history(self, period="7d"):
                return self._hist

        monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
        # No usable data must be reported as unknown rather than as 0.0,
        # which would be indistinguishable from a genuinely flat market.
        out = self.repo.get_crypto_fear_greed_proxy(["BTC-USD"])
        assert out.average_weekly_change is None
        assert out.sentiment_proxy == "Unknown"

    def test_zero_baseline_price_yields_none_not_nan(self):
        """A zero close price must not produce NaN.

        A delisted or erroneous feed reporting 0.00 previously produced NaN,
        which failed every comparison in _determine_sentiment_label and so
        fell through to "Extreme Fear" - a maximally alarming, wrong signal.
        """
        history = pd.DataFrame({"Close": [0.0, 0.0]})

        assert self.repo._calculate_weekly_change(history) is None
        assert self.repo._calculate_daily_change(history) is None

    def test_unusable_change_does_not_poison_average(self):
        """Entries without a usable change are excluded from the average."""
        average = self.repo._calculate_average_weekly_change(
            [
                {"symbol": "BAD", "weekly_change_percent": None},
                {"symbol": "GOOD", "weekly_change_percent": 8.0},
            ]
        )

        assert average == 8.0
        assert self.repo._determine_sentiment_label(average) == "Greed"

    def test_determine_sentiment_label_unknown_for_missing_data(self):
        """None and NaN must map to Unknown, never to Extreme Fear."""
        assert self.repo._determine_sentiment_label(None) == "Unknown"
        assert self.repo._determine_sentiment_label(float("nan")) == "Unknown"

    def test_determine_sentiment_label_greed(self, monkeypatch):
        """Test sentiment label for Greed (5 < change <= 10)."""

        class T:
            def __init__(self, t, session=None):
                self._hist = pd.DataFrame(
                    [
                        {"Close": 100},
                        {"Close": 102},
                        {"Close": 107},  # 7% increase = Greed
                    ]
                )

            def history(self, period="7d"):
                return self._hist

        monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
        out = self.repo.get_crypto_fear_greed_proxy(["BTC-USD"])
        assert out.sentiment_proxy == "Greed"

    def test_determine_sentiment_label_neutral_positive(self, monkeypatch):
        """Test sentiment label for Neutral-Positive (0 < change <= 5)."""

        class T:
            def __init__(self, t, session=None):
                self._hist = pd.DataFrame(
                    [
                        {"Close": 100},
                        {"Close": 101},
                        {"Close": 103},  # 3% increase = Neutral-Positive
                    ]
                )

            def history(self, period="7d"):
                return self._hist

        monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
        out = self.repo.get_crypto_fear_greed_proxy(["BTC-USD"])
        assert out.sentiment_proxy == "Neutral-Positive"

    def test_determine_sentiment_label_fear(self, monkeypatch):
        """Test sentiment label for Fear (-10 < change <= -5)."""

        class T:
            def __init__(self, t, session=None):
                self._hist = pd.DataFrame(
                    [
                        {"Close": 100},
                        {"Close": 95},
                        {"Close": 93},  # -7% decrease = Fear
                    ]
                )

            def history(self, period="7d"):
                return self._hist

        monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
        out = self.repo.get_crypto_fear_greed_proxy(["BTC-USD"])
        assert out.sentiment_proxy == "Fear"

    def test_determine_sentiment_label_extreme_fear(self, monkeypatch):
        """Test sentiment label for Extreme Fear (change <= -10)."""

        class T:
            def __init__(self, t, session=None):
                self._hist = pd.DataFrame(
                    [
                        {"Close": 100},
                        {"Close": 90},
                        {"Close": 85},  # -15% decrease = Extreme Fear
                    ]
                )

            def history(self, period="7d"):
                return self._hist

        monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
        out = self.repo.get_crypto_fear_greed_proxy(["BTC-USD"])
        assert out.sentiment_proxy == "Extreme Fear"
